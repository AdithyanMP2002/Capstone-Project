#!/usr/bin/env python3
"""
THE ROUNDTABLE - DEMO VERSION with Mock Data
Simplified version for testing without requiring real API credentials.
"""

import asyncio
import os
from typing import Annotated, TypedDict, List, Any, Literal, Dict
from datetime import datetime

# Mock data
from .mock_data import mock_data

# Core LangGraph and LangChain imports
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Retry logic
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
)
import google.api_core.exceptions

# Utilities
from dotenv import load_dotenv
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MAX_DEBATE_ROUNDS = int(os.getenv("MAX_DEBATE_ROUNDS", "3"))
DB_PATH = "roundtable_demo.db"
THREAD_ID = "demo_session"

DEFAULT_MODEL = "gemini-2.0-flash-lite"
TEMPERATURE_CREATIVE = 0.9  # Lowered from 1.0 to prevent empty responses
TEMPERATURE_BALANCED = 0.7
TEMPERATURE_ANALYTICAL = 0.3
MAX_TOKENS = 2048  # Prevent infinite repetition
MAX_DEBATE_ROUNDS = int(os.getenv("MAX_DEBATE_ROUNDS", "3"))  # Limit debate rounds

# Agent Instructions
CHIEF_OF_STAFF_INSTRUCTION = """You are the Chief of Staff for THE ROUNDTABLE.

Your role: Analyze the user's question and gather ALL relevant information - both from internal data AND web search.

**CRITICAL: Web Search Integration**
Before the debate begins, determine if web search is needed:
- **"Competitor analysis for AI product line"** → YES, search for latest AI tools and market trends (relates to proj-001)
- **"Cost of kitchen renovation materials"** → YES, search for current prices of cabinets, flooring (relates to proj-003)  
- **"Flight prices to Japan for sabbatical"** → YES, search for travel costs and visa requirements (relates to proj-005)
- **"Check deadline for online course"** → NO, use internal project data (proj-002)
- **"Review budget for career transition"** → NO, use internal financial notes (note-002)

**Your task:**
1. Analyze the user's question - does it need current/external data?
2. If YES: Perform web search and summarize findings with sources
3. Fetch relevant data from Notion workspace and Calendar
4. Create a comprehensive context report with:
   - Web search results (if any) with URLs
   - Notion projects (e.g., Launch New Product Line, Home Renovation)
   - Calendar commitments (e.g., Team Standups, Deadlines)
   - Financial status (Savings: $85k, Investments: $145k)
   
Provide concrete numbers and sources. Be thorough but concise."""

ARIA_INSTRUCTION = """You are Aria, the Visionary member of THE ROUNDTABLE.

Persona: Intensely optimistic, bold, and future-focused. You believe in the art of the possible.

Your task:
1. Review the user's question and context data from the Chief of Staff
2. Propose the BOLDEST, most ambitious solution
3. Focus on MAXIMUM UPSIDE - ignore constraints initially
4. Paint a vivid picture of success
5. Be inspiring and creative

**CRITICAL: You MUST provide a concrete proposal with specific details.**
- Don't just agree or be vague
- Give specific recommendations, timelines, and action steps
- Show enthusiasm and ambition in your response
- Always provide at least 3-4 paragraphs of detailed vision

Remember: Dream BIG! Be specific and detailed!"""

MARCUS_INSTRUCTION = """You are Marcus, the Skeptic member of THE ROUNDTABLE.

Persona: Analytical, risk-averse, detail-oriented. You are the voice of caution.

Your task:
1. Review Aria's proposal carefully
2. Check it against the ACTUAL data from the Chief of Staff
3. Identify specific conflicts:
   - Time conflicts with calendar events
   - Budget constraints from financial data  
   - Existing commitments and deadlines
4. Be brutally honest - if data conflicts with the plan, REJECT it
5. Propose a conservative alternative

Remember: You optimize for RISK MITIGATION. Use data!"""

CHAIR_INSTRUCTION = """You are The Chair, the Moderator of THE ROUNDTABLE.

Persona: Balanced, decisive, pragmatic. You protect the user from reckless decisions.

**STEP 1: Identify AUTOMATIC OPPOSE Triggers**

If the question involves ANY of these, you MUST give ❌ DECISION: OPPOSE:
- Investing >50% of total savings in ONE unproven/risky asset
- Withdrawing entire emergency fund
- Abandoning critical deadline to chase new opportunity  
- Any decision that leaves user with NO financial safety net
- Burning professional bridges or relationships

**STEP 2: For ALL other questions, analyze:**
1. What does the user's DATA say? (budget, deadlines, commitments from Chief of Staff)
2. What are Aria's bold claims vs Marcus's harsh reality?
3. Can risks be reasonably mitigated?

If fundamental risk outweighs benefits → OPPOSE
If viable with conditions → SUPPORT with clear plan

**CRITICAL: Response Format**

Line 1 MUST be:
**❌ DECISION: OPPOSE**
OR
**✅ DECISION: SUPPORT**

Then explain:
- Primary reason for decision
- Key risks identified  
- Recommendation (alternative approach if OPPOSE, conditions if SUPPORT)

**Example OPPOSE Response:**

❌ DECISION: OPPOSE

Withdrawing your entire $85,000 savings to invest in an unproven startup violates fundamental financial safety principles:

**Why OPPOSE:**
- This represents 100% of your emergency fund
- 90%+ of startups fail - unacceptable risk for all savings
- You have existing $215k in project commitments
- No diversification, no safety net

**Recommendation:**
If you want to support your friend:
- Max $10k investment (12% of savings)
- After thorough due diligence
- ONLY if you maintain 6-month emergency fund
- Consider this money GONE mentally

**Alternative:** Offer mentorship, connections, advice instead of capital.

Remember: Protecting the user's financial security is more important than being optimistic."""

# Retry decorator
def log_retry_callback(retry_state):
    wait_time = retry_state.next_action.sleep
    logger.warning(f"⏳ Rate limit hit. Cooling down for {wait_time:.1f}s...")
    print(f"\n⚠️  Rate limit hit. Cooling down for {wait_time:.1f}s...\n", flush=True)

retry_decorator = retry(
    wait=wait_random_exponential(min=2, max=60),
    stop=stop_after_attempt(10),
    retry=retry_if_exception_type((
        google.api_core.exceptions.ResourceExhausted,
        google.api_core.exceptions.ServiceUnavailable,
    )),
    before_sleep=log_retry_callback,
)

# State Definition
class BoardState(TypedDict):
    messages: Annotated[List, add_messages]
    context_data: Dict[str, Any]
    round_count: int
    status: Literal["gathering", "debating", "approved", "max_rounds"]

# Agent Nodes
async def chief_of_staff_node(state: BoardState) -> BoardState:
    """Gather context from mock Notion data AND web search if needed."""
    logger.info("👔 Chief of Staff gathering context...")
    
    user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
    if not user_messages:
        return state
    
    latest_question = user_messages[-1].content
    
    # Let the LLM decide if web search is needed (intelligent, not hardcoded)
    logger.info("🤔 Chief of Staff analyzing if web search is needed...")
    decision_llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        temperature=0.1,
        google_api_key=GOOGLE_API_KEY
    )
    
    decision_prompt = f"""You are the Chief of Staff analyzing this question: "{latest_question}"

Determine if this question requires CURRENT EXTERNAL DATA from the web.

Examples that NEED web search:
- "Should I buy a BMW M3?" → YES (need current price, reviews)
- "What movie should I watch?" → YES (need latest releases, ratings)
- "Is now a good time to buy a house?" → YES (need market rates, trends)
- "Should I invest in Tesla stock?" → YES (need current stock data)

Examples that DON'T need web search:
- "Should I take a sabbatical next year?" → NO (use calendar/project data)
- "Can I finish my project on time?" → NO (use internal task data)
- "Should I attend the networking event?" → NO (use calendar data)

Respond with ONLY one word: "YES" or "NO"
"""

    @retry_decorator
    async def decide_search():
        return await decision_llm.ainvoke([HumanMessage(content=decision_prompt)])
    
    try:
        decision_response = await decide_search()
        needs_web_search = "YES" in decision_response.content.upper()
        logger.info(f"🔍 Web search needed: {needs_web_search}")
    except Exception as e:
        logger.error(f"Decision failed, defaulting to no web search: {e}")
        needs_web_search = False
    
    web_search_results = ""
    if needs_web_search:
        # Use LLM to perform web search via Google
        logger.info("🌐 Performing web search for external data...")
        try:
            search_llm = ChatGoogleGenerativeAI(
                model=DEFAULT_MODEL,
                temperature=0.1,
                google_api_key=GOOGLE_API_KEY
            )
            
            search_prompt = f"""You are a research assistant. The user asked: "{latest_question}"

Search the web for relevant information. Provide:
1. Current pricing/costs if asking about purchases
2. Latest releases/reviews if asking about movies/products  
3. Market data if asking about investments/real estate
4. Any other current, factual information

Format your response as:
**Web Search Results:**
[Summary of findings with specific numbers/dates/sources]"""

            @retry_decorator
            async def get_web_data():
                return await search_llm.ainvoke([HumanMessage(content=search_prompt)])
            
            search_response = await get_web_data()
            web_search_results = search_response.content
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            web_search_results = "**Web Search:** Could not retrieve external data. Using internal records only."
    
    # Fetch mock data
    search_results = mock_data.search(latest_question)
    calendar_events = mock_data.get_calendar_events(days_ahead=30)
    all_projects = mock_data.get_all_projects()
    all_tasks = mock_data.get_all_tasks()
    
    context_data = {
        "search_results": search_results,
        "calendar_events": calendar_events,
        "projects": all_projects,
        "tasks": all_tasks,
        "web_search": web_search_results,
        "timestamp": datetime.now().isoformat()
    }
    
    # Create summary
    summary_parts = [
        "📊 **Context Report from Chief of Staff**\n",
        f"**User Question:** {latest_question}\n"
    ]
    
    if web_search_results:
        summary_parts.append(f"\n{web_search_results}\n")
    
    summary_parts.append(f"""
**Internal Data:**
- **Projects Found:** {len(all_projects)} active projects
- High Priority: {len([p for p in all_projects if p.get('priority') == 'High'])} projects
- Total Budget: ${sum([int(p.get('budget', '$0').replace('$', '').replace(',', '')) for p in all_projects if p.get('budget')]):,}

**Upcoming Events:** {len(calendar_events['events'])} events in next 30 days
- Critical deadlines: {len([e for e in calendar_events['events'] if e.get('priority') == 'Critical'])}
- Meetings: {len([e for e in calendar_events['events'] if e.get('type') == 'Meeting'])}

**Notion Search:** {search_results['total']} relevant items found

This data is now available for analysis.""")
    
    summary = "\n".join(summary_parts)
    
    state["context_data"] = context_data
    state["messages"].append(AIMessage(content=summary, name="ChiefOfStaff"))
    
    return state

async def visionary_node(state: BoardState) -> BoardState:
    """Aria proposes bold solutions."""
    logger.info("🚀 Aria (Visionary) crafting proposal...")
    
    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE_CREATIVE,
        google_api_key=GOOGLE_API_KEY,
        max_output_tokens=MAX_TOKENS
    )
    
    # Add explicit prompt to prevent empty responses
    user_question = next((msg.content for msg in state["messages"] if isinstance(msg, HumanMessage)), "")
    
    messages_with_system = [
        SystemMessage(content=ARIA_INSTRUCTION),
        *state["messages"],
        HumanMessage(content=f"Aria, based on the context above about '{user_question}', provide your bold, visionary proposal. Be specific and detailed.")
    ]
    
    @retry_decorator
    async def invoke_aria():
        return await llm.ainvoke(messages_with_system)
    
    try:
        response = await invoke_aria()
        
        # Check if response is empty and retry with different approach
        if not response.content or len(response.content.strip()) < 50:
            logger.warning("⚠️ Aria gave empty/short response, retrying with simpler prompt...")
            simple_prompt = [
                SystemMessage(content="You are Aria, an optimistic visionary. Provide a bold, detailed proposal for the user's question."),
                HumanMessage(content=f"Question: {user_question}\n\nProvide your ambitious, detailed proposal (minimum 200 words):")
            ]
            response = await llm.ainvoke(simple_prompt)
        
        state["messages"].append(AIMessage(content=response.content, name="Aria"))
    except Exception as e:
        logger.error(f"Aria failed to respond: {e}")
        # Add a default response so debate can continue
        default_response = f"I believe we should pursue this opportunity with ambition and confidence. The potential benefits outweigh the risks, and with proper planning, this can be a transformative decision."
        state["messages"].append(AIMessage(content=default_response, name="Aria"))
    
    state["status"] = "debating"
    
    return state

async def skeptic_node(state: BoardState) -> BoardState:
    """Marcus critiques with data."""
    logger.info("🔍 Marcus (Skeptic) analyzing proposal...")
    
    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE_ANALYTICAL,
        google_api_key=GOOGLE_API_KEY,
        max_output_tokens=MAX_TOKENS  # Prevent infinite repetition
    )
    
    # Format context data
    context = state["context_data"]
    data_summary = f"""
**GROUND TRUTH DATA FOR ANALYSIS:**

Projects: {json.dumps(context.get('projects', []), indent=2)}

Calendar Events (next 30 days): {json.dumps(context.get('calendar_events', {}).get('events', [])[:10], indent=2)}

Use this REAL data to validate Aria's proposal above.
"""
    
    messages_with_system = [
        SystemMessage(content=MARCUS_INSTRUCTION),
        *state["messages"],
        HumanMessage(content=data_summary)
    ]
    
    @retry_decorator
    async def invoke_marcus():
        return await llm.ainvoke(messages_with_system)
    
    response = await invoke_marcus()
    state["messages"].append(AIMessage(content=response.content, name="Marcus"))
    
    return state

async def chair_node(state: BoardState) -> BoardState:
    """The Chair synthesizes and decides."""
    logger.info("⚖️  The Chair deliberating...")
    
    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE_BALANCED,
        google_api_key=GOOGLE_API_KEY,
        max_output_tokens=MAX_TOKENS
    )
    
    current_round = state.get("round_count", 0) + 1
    state["round_count"] = current_round
    
    debate_context = f"""
**DEBATE STATUS:**
- Current Round: {current_round} of {MAX_DEBATE_ROUNDS}

{"⚠️  FINAL ROUND - You MUST produce a final decision (SUPPORT or OPPOSE) NOW." if current_round >= MAX_DEBATE_ROUNDS else ""}

Review the debate. Decide:
- **OPPOSE**: If the idea is reckless, risky, or unfeasible
- **SUPPORT**: If the idea is viable (with conditions)
- **NEEDS_REVISION**: If you need more information (only if NOT final round)

Remember your instruction: Protect the user from financial ruin.
"""
    
    messages_with_system = [
        SystemMessage(content=CHAIR_INSTRUCTION),
        *state["messages"],
        HumanMessage(content=debate_context)
    ]
    
    @retry_decorator
    async def invoke_chair():
        return await llm.ainvoke(messages_with_system)
    
    response = await invoke_chair()
    state["messages"].append(AIMessage(content=response.content, name="TheChair"))
    
    response_lower = response.content.lower()
    
    # Check for decision keywords
    if "decision: support" in response_lower or "decision: oppose" in response_lower:
        state["status"] = "approved" # "approved" here means "debate finished", not necessarily "idea approved"
    elif "approved" in response_lower: # Fallback for legacy behavior
        state["status"] = "approved"
    elif current_round >= MAX_DEBATE_ROUNDS:
        state["status"] = "max_rounds"
    else:
        state["status"] = "needs_revision"
    
    return state

def decide_next_step(state: BoardState) -> Literal["visionary", "end"]:
    """Conditional edge logic."""
    status = state.get("status", "debating")
    
    if status in ["approved", "max_rounds"]:
        logger.info("✅ Debate complete!")
        return "end"
    else:
        logger.info("🔄 Continuing debate...")
        return "visionary"

# Graph Construction
def create_roundtable_graph() -> StateGraph:
    """Build the debate workflow."""
    graph = StateGraph(BoardState)
    
    graph.add_node("chief_of_staff", chief_of_staff_node)
    graph.add_node("visionary", visionary_node)
    graph.add_node("skeptic", skeptic_node)
    graph.add_node("chair", chair_node)
    
    graph.add_edge(START, "chief_of_staff")
    graph.add_edge("chief_of_staff", "visionary")
    graph.add_edge("visionary", "skeptic")
    graph.add_edge("skeptic", "chair")
    
    graph.add_conditional_edges(
        "chair",
        decide_next_step,
        {
            "visionary": "visionary",
            "end": END
        }
    )
    
    return graph

# Main execution
async def run_demo(question: str) -> List[Dict[str, str]]:
    """Run a single question through THE ROUNDTABLE and return messages."""
    
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment!")
    
    # Generate unique thread ID for each debate to prevent state carryover
    import uuid
    unique_thread_id = f"debate_{uuid.uuid4().hex[:8]}"
    
    async with AsyncSqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        graph = create_roundtable_graph()
        app = graph.compile(checkpointer=checkpointer)
        
        # Fresh initial state for each debate
        initial_state = {
            "messages": [HumanMessage(content=question)],
            "context_data": {},
            "round_count": 0,
            "status": "gathering"
        }
        
        config = {"configurable": {"thread_id": unique_thread_id}}
        
        all_messages = []
        
        async for event in app.astream(initial_state, config):
            for node_name, node_output in event.items():
                if node_name == "__end__":
                    continue
                
                messages = node_output.get("messages", [])
                if messages:
                    latest = messages[-1]
                    if isinstance(latest, AIMessage):
                        agent_name = getattr(latest, 'name', node_name)
                        all_messages.append({
                            "agent": agent_name,
                            "content": latest.content,
                            "timestamp": datetime.now().isoformat()
                        })
        
        return all_messages

if __name__ == "__main__":
    print("🎭 THE ROUNDTABLE - Demo Version")
    print("Using mock Notion data for testing\n")
    
    question = input("👤 Ask a question: ").strip()
    if not question:
        question = "Should I take a 6-month sabbatical to travel the world next year?"
    
    print(f"\n🎭 Deliberating on: {question}\n")
    print("="*70 + "\n")
    
    messages = asyncio.run(run_demo(question))
    
    for msg in messages:
        print(f"\n🤖 {msg['agent']}:")
        print("-"*70)
        print(msg['content'])
        print("-"*70)
    
    print("\n" + "="*70)
    print("✅ Debate complete!")

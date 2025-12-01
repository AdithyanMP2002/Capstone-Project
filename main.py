#!/usr/bin/env python3
"""
THE ROUNDTABLE - Local-First Personal Board of Directors
A persistent multi-agent decision support system using Google Gemini, LangGraph, and MCP.

Architecture:
- LLM: Google Gemini (Free Tier with 15 RPM limit)
- Orchestration: LangGraph for cyclic debate workflow
- Tools: Model Context Protocol (MCP) for Notion and Google Calendar
- Persistence: SQLite with hardcoded thread_id for conversation continuity
- Interface: Console-based with streaming responses

Key Design Decisions:
1. Single-file implementation for simplicity and portability
2. Industrial-grade retry logic for Gemini's 15 RPM free tier limit
3. MCP servers spawned as subprocesses via npx (stdio transport)
4. AsyncExitStack for proper lifecycle management of connections
5. Hardcoded thread_id enables true conversation persistence

Author: THE ROUNDTABLE Project
License: MIT
"""

import asyncio
import os
import sys
import signal
from contextlib import AsyncExitStack
from typing import Annotated, TypedDict, Dict, List, Any, Literal
from datetime import datetime

# Core LangGraph and LangChain imports
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

# MCP imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Retry logic for rate limiting
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import google.api_core.exceptions

# Utilities
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
GOOGLE_OAUTH_CREDENTIALS = os.getenv("GOOGLE_OAUTH_CREDENTIALS")
MAX_DEBATE_ROUNDS = int(os.getenv("MAX_DEBATE_ROUNDS", "3"))
DB_PATH = "roundtable.db"
THREAD_ID = "main_session"  # Hardcoded for persistence across runs

# Model configuration
DEFAULT_MODEL = "gemini-2.0-flash-exp"  # Updated model name
TEMPERATURE_CREATIVE = 1.0  # For Aria (Visionary)
TEMPERATURE_BALANCED = 0.7  # For Chair
TEMPERATURE_ANALYTICAL = 0.3  # For Marcus (Skeptic)

# =============================================================================
# AGENT PERSONA DEFINITIONS
# Using "Persona + Task + Context" prompting methodology
# =============================================================================

CHIEF_OF_STAFF_INSTRUCTION = """You are the Chief of Staff for THE ROUNDTABLE.

Your role: You are a meticulous data gatherer. Before the debate begins, you must collect relevant context from the user's Notion workspace and Google Calendar.

Your task:
1. Analyze the user's problem or question
2. Determine what data would be relevant (upcoming events, project notes, goals, etc.)
3. Use the available MCP tools to fetch this data:
   - Use notion_search to find relevant pages/databases
   - Use calendar_list_events to check upcoming commitments
4. Summarize the findings in a structured format

Be thorough but concise. The other agents will rely on your data."""

ARIA_INSTRUCTION = """You are Aria, the Visionary member of THE ROUNDTABLE.

Persona: You are intensely optimistic, bold, and future-focused. You believe in the art of the possible.

Your role: When presented with a problem or decision, you propose the most ambitious, high-upside solution. You think in "Blue Sky" terms.

Your task:
1. Review the user's question and the context provided by the Chief of Staff
2. Propose the boldest possible path forward
3. Ignore constraints like budget or time initially - focus on potential
4. Paint a vivid picture of what success looks like
5. Be creative and inspiring

Remember: You optimize for MAXIMUM UPSIDE. Dream big."""

MARCUS_INSTRUCTION = """You are Marcus, the Skeptic member of THE ROUNDTABLE.

Persona: You are analytical, risk-averse, and detail-oriented. You are the voice of caution.

Your role: Critique proposals using hard data and ground truth.

Your task:
1. Review Aria's proposal carefully
2. Reference the ACTUAL data from the Chief of Staff's report
3. Identify conflicts between the proposal and reality:
   - Does the user have time? (Check calendar data)
   - Does the plan align with existing commitments? (Check Notion data)
   - What are the risks and downsides?
4. If data conflicts with the plan, reject it decisively
5. Propose a more conservative alternative if needed

Remember: You optimize for RISK MITIGATION. Be brutally honest with data."""

CHAIR_INSTRUCTION = """You are The Chair, the Moderator of THE ROUNDTABLE.

Persona: You are balanced, decisive, and diplomatic. Your goal is synthesis and consensus.

Your role: Facilitate the debate and reach a final decision.

Your task:
1. Review Aria's ambitious proposal
2. Review Marcus's critique and concerns
3. Determine if the debate has reached a productive conclusion:
   - If proposals and critiques are converging → APPROVE a synthesized plan
   - If still diverging significantly → Send for REVISION (max 3 rounds)
   - If at max rounds → Force a synthesis anyway
4. When approving, create a clear, actionable "Action Plan" that:
   - Incorporates Aria's vision where realistic
   - Addresses Marcus's concerns with concrete mitigations
   - Provides specific next steps

Remember: Your job is CONSENSUS. Find the balanced path forward."""

# =============================================================================
# RATE LIMIT RETRY DECORATOR
# Critical for Gemini Free Tier (15 RPM limit)
# =============================================================================

def log_retry_callback(retry_state):
    """Callback to log retry attempts with visible user feedback."""
    wait_time = retry_state.next_action.sleep
    logger.warning(f"⏳ Rate limit hit. Cooling down for {wait_time:.1f}s...")
    print(f"\n⚠️  Rate limit hit. Cooling down for {wait_time:.1f}s...\n", flush=True)


# Retry decorator applied to all LLM invocations
# - Exponential backoff: 2s to 60s
# - Max 10 attempts
# - Only retry on 429 (ResourceExhausted) and 503 (ServiceUnavailable)
retry_decorator = retry(
    wait=wait_random_exponential(min=2, max=60),
    stop=stop_after_attempt(10),
    retry=retry_if_exception_type((
        google.api_core.exceptions.ResourceExhausted,  # 429 rate limit
        google.api_core.exceptions.ServiceUnavailable,  # 503 service issues
    )),
    before_sleep=log_retry_callback,
)

# =============================================================================
# STATE DEFINITION
# =============================================================================

class BoardState(TypedDict):
    """State schema for THE ROUNDTABLE debate workflow.
    
    Attributes:
        messages: Conversation history with automatic message aggregation
        context_data: Data fetched from Notion/Calendar by Chief of Staff
        round_count: Current debate round number (for termination condition)
        status: Current workflow status
    """
    messages: Annotated[List, add_messages]
    context_data: Dict[str, Any]
    round_count: int
    status: Literal["gathering", "debating", "approved", "max_rounds"]

# =============================================================================
# MCP CLIENT WRAPPER
# Manages lifecycle of Notion and Google Calendar MCP servers via stdio
# =============================================================================

class MCPClientManager:
    """Manages MCP server connections via stdio transport.
    
    This class spawns and manages MCP servers as Node.js subprocesses:
    - Notion MCP: @notionhq/notion-mcp-server
    - Google Calendar MCP: @cocal/google-calendar-mcp
    
    Uses AsyncExitStack to ensure clean shutdown of all connections.
    """
    
    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.notion_session: ClientSession = None
        self.calendar_session: ClientSession = None
        self.notion_tools = []
        self.calendar_tools = []
    
    async def __aenter__(self):
        """Initialize MCP connections on context entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up MCP connections on context exit."""
        await self.exit_stack.aclose()
    
    async def connect(self):
        """Connect to both MCP servers and initialize tools."""
        logger.info("🔌 Connecting to MCP servers...")
        
        # Connect to Notion MCP
        try:
            notion_params = StdioServerParameters(
                command="npx",
                args=["-y", "@notionhq/notion-mcp-server"],
                env={**os.environ, "NOTION_TOKEN": NOTION_TOKEN} if NOTION_TOKEN else os.environ
            )
            
            notion_stdio = await self.exit_stack.enter_async_context(
                stdio_client(notion_params)
            )
            self.notion_session = await self.exit_stack.enter_async_context(
                ClientSession(notion_stdio[0], notion_stdio[1])
            )
            await self.notion_session.initialize()
            
            # Get available Notion tools
            tools_list = await self.notion_session.list_tools()
            self.notion_tools = [t.name for t in tools_list.tools]
            logger.info(f"✅ Notion MCP connected. Tools: {self.notion_tools}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Notion MCP: {e}")
            self.notion_session = None
        
        # Connect to Google Calendar MCP
        try:
            calendar_params = StdioServerParameters(
                command="npx",
                args=["-y", "@cocal/google-calendar-mcp"],
                env={
                    **os.environ,
                    "GOOGLE_OAUTH_CREDENTIALS": GOOGLE_OAUTH_CREDENTIALS
                } if GOOGLE_OAUTH_CREDENTIALS else os.environ
            )
            
            calendar_stdio = await self.exit_stack.enter_async_context(
                stdio_client(calendar_params)
            )
            self.calendar_session = await self.exit_stack.enter_async_context(
                ClientSession(calendar_stdio[0], calendar_stdio[1])
            )
            await self.calendar_session.initialize()
            
            # Get available Calendar tools
            tools_list = await self.calendar_session.list_tools()
            self.calendar_tools = [t.name for t in tools_list.tools]
            logger.info(f"✅ Calendar MCP connected. Tools: {self.calendar_tools}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Calendar MCP: {e}")
            self.calendar_session = None
    
    async def call_notion_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Call a Notion MCP tool."""
        if not self.notion_session:
            return {"error": "Notion MCP not connected"}
        
        try:
            result = await self.notion_session.call_tool(tool_name, arguments)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error calling Notion tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def call_calendar_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Call a Google Calendar MCP tool."""
        if not self.calendar_session:
            return {"error": "Calendar MCP not connected"}
        
        try:
            result = await self.calendar_session.call_tool(tool_name, arguments)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error calling Calendar tool {tool_name}: {e}")
            return {"error": str(e)}

# =============================================================================
# AGENT NODE IMPLEMENTATIONS
# Each node represents one agent in the debate workflow
# =============================================================================

# Global MCP client (initialized in main)
mcp_client = None

async def chief_of_staff_node(state: BoardState) -> BoardState:
    """Chief of Staff: Gathers context from Notion and Google Calendar.
    
    This node:
    1. Analyzes the user's question
    2. Fetches relevant data from Notion and Calendar via MCP
    3. Adds context to state for other agents to use
    """
    logger.info("👔 Chief of Staff gathering context...")
    
    # Get the latest user message
    user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
    if not user_messages:
        return state
    
    latest_question = user_messages[-1].content
    
    # Initialize context
    context_data = {
        "notion_results": {},
        "calendar_events": {},
        "timestamp": datetime.now().isoformat()
    }
    
    # Fetch Notion data (search for relevant pages)
    if mcp_client and mcp_client.notion_session:
        try:
            # Simple search for now - could be made smarter with LLM analysis
            search_result = await mcp_client.call_notion_tool(
                "notion_search",
                {"query": latest_question[:100]}  # Limit query length
            )
            context_data["notion_results"] = search_result
        except Exception as e:
            logger.error(f"Notion search failed: {e}")
            context_data["notion_results"] = {"error": str(e)}
    
    # Fetch Calendar events (next 7 days)
    if mcp_client and mcp_client.calendar_session:
        try:
            events_result = await mcp_client.call_calendar_tool(
                "list_events",
                {"maxResults": 10}  # Get next 10 events
            )
            context_data["calendar_events"] = events_result
        except Exception as e:
            logger.error(f"Calendar fetch failed: {e}")
            context_data["calendar_events"] = {"error": str(e)}
    
    # Create summary message
    summary = f"""📊 **Context Report from Chief of Staff**

**User Question:** {latest_question}

**Notion Search Results:** {len(context_data.get('notion_results', {}).get('results', []))} pages found
**Calendar Events:** {len(context_data.get('calendar_events', {}).get('items', []))} upcoming events

This data is now available for analysis."""
    
    state["context_data"] = context_data
    state["messages"].append(AIMessage(content=summary, name="ChiefOfStaff"))
    
    return state


async def visionary_node(state: BoardState) -> BoardState:
    """Aria (Visionary): Proposes bold, optimistic solutions.
    
    This node:
    1. Reviews the user's question and context
    2. Generates an ambitious, high-upside proposal
    3. Focuses on potential, not constraints
    """
    logger.info("🚀 Aria (Visionary) crafting proposal...")
    
    # Create LLM with high creativity
    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE_CREATIVE,
        google_api_key=GOOGLE_API_KEY
    )
    
    # Add system instruction
    messages_with_system = [
        SystemMessage(content=ARIA_INSTRUCTION),
        *state["messages"]
    ]
    
    # Invoke with retry decorator
    @retry_decorator
    async def invoke_aria():
        return await llm.ainvoke(messages_with_system)
    
    response = await invoke_aria()
    
    state["messages"].append(AIMessage(content=response.content, name="Aria"))
    state["status"] = "debating"
    
    return state


async def skeptic_node(state: BoardState) -> BoardState:
    """Marcus (Skeptic): Critiques using ground-truth data.
    
    This node:
    1. Reviews Aria's proposal
    2. Checks against real data from context
    3. Identifies risks and conflicts
    4. Proposes conservative alternatives
    """
    logger.info("🔍 Marcus (Skeptic) analyzing proposal...")
    
    # Create LLM with low temperature for analytical thinking
    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE_ANALYTICAL,
        google_api_key=GOOGLE_API_KEY
    )
    
    # Include context data explicitly
    context_summary = f"""
**GROUND TRUTH DATA:**
- Notion Results: {state['context_data'].get('notion_results', {})}
- Calendar Events: {state['context_data'].get('calendar_events', {})}

Use this data to validate the proposal above.
"""
    
    messages_with_system = [
        SystemMessage(content=MARCUS_INSTRUCTION),
        *state["messages"],
        HumanMessage(content=context_summary)
    ]
    
    @retry_decorator
    async def invoke_marcus():
        return await llm.ainvoke(messages_with_system)
    
    response = await invoke_marcus()
    
    state["messages"].append(AIMessage(content=response.content, name="Marcus"))
    
    return state


async def chair_node(state: BoardState) -> BoardState:
    """The Chair: Facilitates debate and reaches consensus.
    
    This node:
    1. Reviews the debate so far
    2. Decides if consensus is reached or revision needed
    3. At max rounds, forces a synthesis
    4. Produces final Action Plan when approving
    """
    logger.info("⚖️  The Chair deliberating...")
    
    # Create LLM with balanced temperature
    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE_BALANCED,
        google_api_key=GOOGLE_API_KEY
    )
    
    # Check round count
    current_round = state.get("round_count", 0) + 1
    state["round_count"] = current_round
    
    # Add context about debate progress
    debate_context = f"""
**DEBATE STATUS:**
- Current Round: {current_round} of {MAX_DEBATE_ROUNDS}
- Round {current_round}/{MAX_DEBATE_ROUNDS}

{"⚠️  FINAL ROUND - You MUST produce a synthesis." if current_round >= MAX_DEBATE_ROUNDS else ""}

Review the debate above. Decide:
- APPROVED: Proposals have converged → Create final Action Plan
- NEEDS_REVISION: Still diverging → Send back to Aria for revision
- MAX_ROUNDS: At limit → Force synthesis now
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
    
    # Simple heuristic: check if Chair says "approved" or we're at max rounds
    response_lower = response.content.lower()
    if "approved" in response_lower or "action plan" in response_lower:
        state["status"] = "approved"
    elif current_round >= MAX_DEBATE_ROUNDS:
        state["status"] = "max_rounds"
    else:
        state["status"] = "needs_revision"
    
    return state


def decide_next_step(state: BoardState) -> Literal["visionary", "end"]:
    """Conditional edge: Decide whether to continue debate or end.
    
    Returns:
        - "visionary": Continue debate (needs revision)
        - "end": Terminate (approved or max rounds)
    """
    status = state.get("status", "debating")
    
    if status == "approved":
        logger.info("✅ Consensus reached!")
        return "end"
    elif status == "max_rounds":
        logger.info("⏱️  Max rounds reached. Forcing synthesis.")
        return "end"
    else:
        logger.info("🔄 Sending back for revision...")
        return "visionary"

# =============================================================================
# LANGGRAPH WORKFLOW CONSTRUCTION
# =============================================================================

def create_roundtable_graph() -> StateGraph:
    """Construct the LangGraph workflow for THE ROUNDTABLE debate.
    
    Flow:
        START → chief_of_staff → visionary → skeptic → chair
                                    ↑                    |
                                    |____(if revision)___|
                                    |
                                    └─→ END (if approved/max rounds)
    
    Returns:
        Compiled StateGraph ready for invocation
    """
    graph = StateGraph(BoardState)
    
    # Add nodes
    graph.add_node("chief_of_staff", chief_of_staff_node)
    graph.add_node("visionary", visionary_node)
    graph.add_node("skeptic", skeptic_node)
    graph.add_node("chair", chair_node)
    
    # Add edges
    graph.add_edge(START, "chief_of_staff")
    graph.add_edge("chief_of_staff", "visionary")
    graph.add_edge("visionary", "skeptic")
    graph.add_edge("skeptic", "chair")
    
    # Conditional edge from chair
    graph.add_conditional_edges(
        "chair",
        decide_next_step,
        {
            "visionary": "visionary",  # Loop back
            "end": END
        }
    )
    
    return graph

# =============================================================================
# MAIN EXECUTION LOOP
# =============================================================================

async def main():
    """Main execution loop with persistent conversation.
    
    Features:
    - Initializes MCP connections
    - Sets up SQLite checkpointer for persistence
    - Uses hardcoded thread_id for conversation continuity
    - Handles graceful shutdown on Ctrl+C
    - Streams agent responses in real-time
    """
    global mcp_client
    
    print("\n" + "="*70)
    print("🎭 THE ROUNDTABLE - Your Personal Board of Directors")
    print("="*70)
    print("\nInitializing...")
    
    # Validate environment
    if not GOOGLE_API_KEY:
        print("❌ ERROR: GOOGLE_API_KEY not found in environment")
        print("Please set it in your .env file")
        sys.exit(1)
    
    if not NOTION_TOKEN:
        print("⚠️  WARNING: NOTION_TOKEN not found. Notion integration will be disabled.")
    
    if not GOOGLE_OAUTH_CREDENTIALS:
        print("⚠️  WARNING: GOOGLE_OAUTH_CREDENTIALS not found. Calendar integration will be disabled.")
        print("Remember to run: npx -y @cocal/google-calendar-mcp auth")
    
    # Initialize MCP connections
    try:
        mcp_client = MCPClientManager()
        await mcp_client.connect()
    except Exception as e:
        logger.error(f"MCP initialization failed: {e}")
        print(f"⚠️  Warning: MCP connections failed. Continuing without tools.\n")
    
    # Set up SQLite checkpointer for persistence
    async with AsyncSqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        # Create graph
        graph = create_roundtable_graph()
        app = graph.compile(checkpointer=checkpointer)
        
        print("\n✅ THE ROUNDTABLE is ready!")
        print(f"💾 Conversation persisted to: {DB_PATH}")
        print(f"🔑 Thread ID: {THREAD_ID}\n")
        
        # Check if we have existing conversation
        try:
            config = {"configurable": {"thread_id": THREAD_ID}}
            state_snapshot = await app.aget_state(config)
            
            if state_snapshot and state_snapshot.values.get("messages"):
                print("📜 Resuming previous conversation...\n")
                print("-" * 70)
                # Show last few messages
                messages = state_snapshot.values["messages"]
                for msg in messages[-4:]:  # Show last 4 messages
                    if isinstance(msg, HumanMessage):
                        print(f"\n👤 You: {msg.content}")
                    elif isinstance(msg, AIMessage):
                        agent_name = getattr(msg, 'name', 'Agent')
                        print(f"\n🤖 {agent_name}: {msg.content}")
                print("\n" + "-" * 70)
        except Exception as e:
            logger.debug(f"No previous conversation found: {e}")
        
        print("\n💡 Ask me anything! (Ctrl+C or type 'exit' to quit)\n")
        
        # Main conversation loop
        try:
            while True:
                # Get user input
                try:
                    user_input = input("\n👤 You: ").strip()
                except EOFError:
                    break
                
                if not user_input or user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                
                # Create initial state with user message
                initial_state = {
                    "messages": [HumanMessage(content=user_input)],
                    "context_data": {},
                    "round_count": 0,
                    "status": "gathering"
                }
                
                # Run the graph with streaming
                config = {"configurable": {"thread_id": THREAD_ID}}
                
                print("\n" + "="*70)
                print("🎭 THE ROUNDTABLE is deliberating...")
                print("="*70 + "\n")
                
                try:
                    async for event in app.astream(initial_state, config):
                        for node_name, node_output in event.items():
                            if node_name == "__end__":
                                continue
                            
                            # Display the latest message from this node
                            messages = node_output.get("messages", [])
                            if messages:
                                latest = messages[-1]
                                if isinstance(latest, AIMessage):
                                    agent_name = getattr(latest, 'name', node_name)
                                    print(f"\n🤖 {agent_name}:")
                                    print("-" * 70)
                                    print(latest.content)
                                    print("-" * 70)
                
                except Exception as e:
                    print(f"\n❌ Error during execution: {e}")
                    logger.error(f"Graph execution error: {e}", exc_info=True)
                
                print("\n" + "="*70)
        
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down gracefully...")
        
        finally:
            # Clean up MCP connections
            if mcp_client:
                await mcp_client.__aexit__(None, None, None)
            
            print("\n💾 Conversation saved!")
            print("✅ Goodbye!\n")

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
        sys.exit(0)

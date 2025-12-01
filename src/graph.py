from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.agents import get_visionary_agent, get_skeptic_agent, get_chair_agent
from src.tools import calendar_list_events, notion_search
import datetime

# State Definition
class BoardState(TypedDict):
    messages: Annotated[list, add_messages]
    context_data: Dict[str, Any]
    round_count: int

# Nodes
async def node_chief_of_staff(state: BoardState):
    """
    Fetches initial context data from MCP tools to ground the debate.
    """
    # Example: Fetch events for the next 7 days
    now = datetime.datetime.now()
    next_week = now + datetime.timedelta(days=7)
    
    # We use the tool functions directly or via a helper if they were just functions, 
    # but here they are LangChain tools. We can invoke them.
    # Note: In a real app, we might want to handle errors gracefully.
    try:
        events = await calendar_list_events.ainvoke({
            "start_time": now.isoformat() + "Z",
            "end_time": next_week.isoformat() + "Z"
        })
    except Exception as e:
        events = f"Error fetching events: {e}"

    # We could also search notion for "Goals" or "Budget"
    try:
        notion_context = await notion_search.ainvoke({"query": "Goals"})
    except Exception as e:
        notion_context = f"Error fetching Notion context: {e}"

    return {
        "context_data": {
            "calendar_events": events,
            "notion_context": notion_context
        },
        "messages": [SystemMessage(content=f"Context Data Loaded:\nCalendar: {events}\nNotion: {notion_context}")]
    }

async def node_visionary(state: BoardState):
    agent = get_visionary_agent()
    # Visionary sees the user problem and potentially the context (or ignores it as per persona)
    # The prompt includes the history, so it sees the context message added by Chief of Staff
    response = await agent.ainvoke(state["messages"])
    return {
        "messages": [AIMessage(content=response.content, name="Visionary")]
    }

async def node_skeptic(state: BoardState):
    agent = get_skeptic_agent()
    # Skeptic sees Visionary's proposal and critiques it
    response = await agent.ainvoke(state["messages"])
    return {
        "messages": [AIMessage(content=response.content, name="Skeptic")]
    }

async def node_chair(state: BoardState):
    agent = get_chair_agent()
    response = await agent.ainvoke(state["messages"])
    
    # Parse decision (simple heuristic or structured output)
    # For now, we assume the Chair says "APPROVED" or "NEEDS_REVISION" in the text
    # or we can ask for structured output.
    # Let's rely on the text content for the conditional edge.
    
    return {
        "messages": [AIMessage(content=response.content, name="Chair")],
        "round_count": state.get("round_count", 0) + 1
    }

# Conditional Logic
def decide_next_step(state: BoardState):
    last_message = state["messages"][-1].content.upper()
    round_count = state.get("round_count", 0)
    
    if round_count >= 3:
        return END
    
    if "APPROVED" in last_message:
        return END
    
    return "visionary"

# Graph Construction
workflow = StateGraph(BoardState)

workflow.add_node("chief_of_staff", node_chief_of_staff)
workflow.add_node("visionary", node_visionary)
workflow.add_node("skeptic", node_skeptic)
workflow.add_node("chair", node_chair)

workflow.set_entry_point("chief_of_staff")

workflow.add_edge("chief_of_staff", "visionary")
workflow.add_edge("visionary", "skeptic")
workflow.add_edge("skeptic", "chair")

workflow.add_conditional_edges(
    "chair",
    decide_next_step,
    {
        END: END,
        "visionary": "visionary"
    }
)

graph = workflow.compile()

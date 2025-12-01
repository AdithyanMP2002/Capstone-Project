import streamlit as st
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from langchain_core.messages import HumanMessage
from src.graph import graph

st.set_page_config(page_title="THE ROUNDTABLE", page_icon="🏛️", layout="wide")

st.title("🏛️ THE ROUNDTABLE")
st.markdown("### A Personal Board of Directors")

# Sidebar for configuration or status
with st.sidebar:
    st.header("Council Members")
    st.markdown("- **Aria (The Visionary)**: Optimistic, Blue Sky Thinking")
    st.markdown("- **Marcus (The Skeptic)**: Risk-Averse, Data-Driven")
    st.markdown("- **The Chair**: Moderator, Decision Maker")
    
    st.divider()
    st.info("System Status: Ready")

# Main Input
user_problem = st.text_area("Present your problem to the Council:", height=100, placeholder="e.g., Should I quit my job to start a bakery?")

if st.button("Convene Council", type="primary"):
    if not user_problem:
        st.warning("Please state your problem first.")
    else:
        st.markdown("---")
        st.subheader("Council Debate")
        
        # Container for chat history
        chat_container = st.container()
        
        async def run_debate():
            initial_state = {
                "messages": [HumanMessage(content=user_problem)],
                "round_count": 0
            }
            
            # Stream the graph execution
            async for event in graph.astream(initial_state):
                for node_name, state_update in event.items():
                    # Check if there are new messages
                    if "messages" in state_update:
                        latest_msg = state_update["messages"][-1]
                        
                        # Determine avatar/role
                        role = "assistant"
                        avatar = "🤖"
                        if node_name == "visionary":
                            avatar = "✨"
                            role = "Visionary"
                        elif node_name == "skeptic":
                            avatar = "🛡️"
                            role = "Skeptic"
                        elif node_name == "chair":
                            avatar = "⚖️"
                            role = "The Chair"
                        elif node_name == "chief_of_staff":
                            avatar = "📋"
                            role = "Chief of Staff"
                        
                        with chat_container:
                            with st.chat_message(name=role, avatar=avatar):
                                st.write(f"**{role}**")
                                st.write(latest_msg.content)
                                
                    # Check for context data update
                    if "context_data" in state_update:
                        with st.expander("Context Data Fetched"):
                            st.json(state_update["context_data"])

        # Run the async function
        asyncio.run(run_debate())
        
        st.success("The Council has spoken.")

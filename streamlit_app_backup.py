"""
Streamlit UI for THE ROUNDTABLE
Beautiful visual interface to watch the AI debate in real-time.
"""

import streamlit as st
import asyncio
from datetime import datetime
import json
from main_demo import run_demo, mock_data
from typing import List, Dict

# Page config
st.set_page_config(
    page_title="THE ROUNDTABLE",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .agent-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chief-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .aria-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    .marcus-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    .chair-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
    }
    .stat-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #6c757d;
    }
    .decision-box {
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        animation: pulse 2s ease-in-out;
    }
    .decision-support {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border: 3px solid #11998e;
    }
    .decision-oppose {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        border: 3px solid #eb3349;
    }
    .decision-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
        margin-bottom: 1rem;
    }
    .decision-subtitle {
        font-size: 1.2rem;
        color: white;
        opacity: 0.9;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🎭 THE ROUNDTABLE")
st.subheader("Your Personal Board of Directors")

# Sidebar with mock data overview
with st.sidebar:
    st.header("📊 Your Data Context")
    
    projects = mock_data.get_all_projects()
    tasks = mock_data.get_all_tasks()
    events = mock_data.get_calendar_events(30)
    
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{len(projects)}</div>
        <div class="stat-label">Active Projects</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{len(tasks)}</div>
        <div class="stat-label">Pending Tasks</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{len(events['events'])}</div>
        <div class="stat-label">Upcoming Events</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    with st.expander("📁 View Projects"):
        for proj in projects:
            st.markdown(f"**{proj['title']}**")
            st.caption(f"Status: {proj['status']} | Priority: {proj['priority']}")
            st.caption(f"Budget: {proj['budget']}")
            st.divider()
    
    with st.expander("📅 View Calendar"):
        for event in events['events'][:10]:
            st.markdown(f"**{event['title']}**")
            st.caption(f"{event['date']} at {event['time']}")
            st.divider()

# Main content
st.markdown("---")

# Example questions
st.subheader("💡 Try These Questions")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Should I take a sabbatical?", use_container_width=True):
        st.session_state.question = "Should I take a 6-month sabbatical to travel the world next year?"

with col2:
    if st.button("Can I start a business?", use_container_width=True):
        st.session_state.question = "Should I quit my job and start my own business in Q1 2026?"

with col3:
    if st.button("BMW M3 Competition?", use_container_width=True):
        st.session_state.question = "I am thinking of buying a BMW M3 Competition by 2026. Should I do it?"

with col4:
    if st.button("Watch a movie?", use_container_width=True):
        st.session_state.question = "I am thinking of watching a movie this weekend. Any recommendations?"

st.markdown("---")

# Question input
question = st.text_area(
    "🎤 Ask THE ROUNDTABLE for advice:",
    value=st.session_state.get("question", ""),
    height=100,
    placeholder="e.g., Should I take a sabbatical next year? Can I afford to start a business?"
)

if st.button("🚀 Start Debate", type="primary", use_container_width=True):
    if not question:
        st.error("Please enter a question!")
    else:
        with st.spinner("🎭 THE ROUNDTABLE is deliberating..."):
            # Run the debate
            messages = asyncio.run(run_demo(question))
            
            st.session_state.messages = messages
            st.session_state.question_asked = question

# Display results if available
if "messages" in st.session_state:
    st.markdown("---")
    
    # Extract final decision from The Chair's message
    final_decision = None
    decision_type = None
    chair_message = None
    
    for msg in st.session_state.messages:
        if msg['agent'] == 'TheChair':
            chair_message = msg['content']
            if "✅ DECISION: SUPPORT" in chair_message or "DECISION: SUPPORT" in chair_message:
                final_decision = "SUPPORT"
                decision_type = "support"
            elif "❌ DECISION: OPPOSE" in chair_message or "DECISION: OPPOSE" in chair_message:
                final_decision = "OPPOSE"
                decision_type = "oppose"
    
    # Display prominent final decision if found
    if final_decision:
        decision_class = "decision-support" if decision_type == "support" else "decision-oppose"
        decision_icon = "✅" if decision_type == "support" else "❌"
        decision_subtitle = "The Roundtable recommends moving forward" if decision_type == "support" else "The Roundtable advises caution"
        
        st.markdown(f"""
        <div class="decision-box {decision_class}">
            <div class="decision-title">{decision_icon} DECISION: {final_decision}</div>
            <div class="decision-subtitle">{decision_subtitle}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Put full transcript in collapsible expander
    with st.expander("📋 View Full Debate Transcript", expanded=False):
        st.caption(f"Question: *{st.session_state.question_asked}*")
        st.markdown("---")
        
        # Display each agent's response
    for msg in st.session_state.messages:
        agent = msg['agent']
        content = msg['content']
        
        # Choose card style based on agent
        if agent == "ChiefOfStaff":
            card_class = "chief-card"
            icon = "👔"
            title = "Chief of Staff"
        elif agent == "Aria":
            card_class = "aria-card"
            icon = "🚀"
            title = "Aria (The Visionary)"
        elif agent == "Marcus":
            card_class = "marcus-card"
            icon = "🔍"
        for msg in st.session_state.messages:
            agent = msg['agent']
            content = msg['content']
            
            # Choose card style based on agent
            if agent == "ChiefOfStaff":
                card_class = "chief-card"
                icon = "👔"
                title = "Chief of Staff"
            elif agent == "Aria":
                card_class = "aria-card"
                icon = "🚀"
                title = "Aria (The Visionary)"
            elif agent == "Marcus":
                card_class = "marcus-card"
                icon = "🔍"
                title = "Marcus (The Skeptic)"
            elif agent == "TheChair":
                card_class = "chair-card"
                icon = "⚖️"
                title = "The Chair"
            else:
                card_class = "agent-card"
                icon = "🤖"
                title = agent
            
            st.markdown(f"""
            <div class="agent-card {card_class}">
                <h3>{icon} {title}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(content)
            st.markdown("---")
        
        # Summary stats inside expander
        st.subheader("📊 Debate Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            rounds = sum(1 for m in st.session_state.messages if m['agent'] == "TheChair")
            st.metric("Debate Rounds", rounds)
        
        with col2:
            total_agents = len(set(m['agent'] for m in st.session_state.messages))
            st.metric("Agents Involved", total_agents)
        
        with col3:
            total_words = sum(len(m['content'].split()) for m in st.session_state.messages)
            st.metric("Total Words", total_words)

# Footer
st.markdown("---")
st.caption("🎭 THE ROUNDTABLE - Powered by Google Gemini, LangGraph & Mock Notion Data")
```

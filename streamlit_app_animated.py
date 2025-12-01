"""
THE ROUNDTABLE - Animated Visualization
Watch agents literally sit around a table and stand up to speak!
"""

import streamlit as st
import asyncio
from datetime import datetime
import json
from main_demo import run_demo, mock_data
from typing import List, Dict
import time

# Page config
st.set_page_config(
    page_title="THE ROUNDTABLE",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with roundtable animation
st.markdown("""
<style>
    /* Roundtable container */
    .roundtable-container {
        position: relative;
        width: 600px;
        height: 600px;
        margin: 2rem auto;
    }
    
    /* The table itself */
    .table-center {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, #8b5cf6 0%, #6d28d9 100%);
        border-radius: 50%;
        box-shadow: 0 0 40px rgba(139, 92, 246, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    /* Agent seats around the table */
    .agent-seat {
        position: absolute;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        cursor: pointer;
        border: 3px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Positioned around circle */
    .seat-top { top: 0; left: 50%; transform: translate(-50%, 0); }
    .seat-right { top: 50%; right: 0; transform: translate(0, -50%); }
    .seat-bottom { bottom: 0; left: 50%; transform: translate(-50%, 0); }
    .seat-left { top: 50%; left: 0; transform: translate(0, -50%); }
    
    /* Agent colors */
    .chief { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .aria { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .marcus { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .chair { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    
    /* Seated state (default) */
    .agent-seat.seated {
        opacity: 0.6;
        transform: scale(1);
    }
    
    /* Standing/Speaking state */
    .agent-seat.standing {
        opacity: 1;
        transform: scale(1.3) !important;
        box-shadow: 0 0 50px currentColor;
        animation: pulse-glow 2s ease-in-out infinite;
        border: 4px solid white;
        z-index: 100;
    }
    
    .seat-top.standing { transform: translate(-50%, -10px) scale(1.3)  !important; }
    .seat-right.standing { transform: translate(10px, -50%) scale(1.3) !important; }
    .seat-bottom.standing { transform: translate(-50%, 10px) scale(1.3) !important; }
    .seat-left.standing { transform: translate(-10px, -50%) scale(1.3) !important; }
    
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 30px currentColor; }
        50% { box-shadow: 0 0 60px currentColor; }
    }
    
    /* Agent icon */
    .agent-icon {
        font-size: 2.5rem;
        margin-bottom: 0.3rem;
    }
    
    .agent-seat.standing .agent-icon {
        font-size: 3.5rem;
        animation: bounce 0.5s ease-out;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .agent-name {
        font-size: 0.7rem;
        font-weight: bold;
        color: white;
        text-align: center;
    }
    
    .agent-seat.standing .agent-name {
        font-size: 0.9rem;
    }
    
    /* Speech bubble */
    .speech-bubble {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        max-width: 600px;
        max-height: 70vh;
        overflow-y: auto;
        z-index: 1000;
        animation: fadeIn 0.3s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
        to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
    }
    
    .speech-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .speech-header-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    
    .close-speech {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: #ef4444;
        color: white;
        border: none;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        cursor: pointer;
        font-size: 1.2rem;
    }
    
    /* Decision box (same as before) */
    .decision-box {
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
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
    
    /* Progress indicator */
    .debate-progress {
        text-align: center;
        padding: 1rem;
        background: #f3f4f6;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .progress-steps {
        display: flex;
        justify-content: space-around;
        margin-top: 1rem;
    }
    
    .progress-step {
        flex: 1;
        padding: 0.5rem;
        margin: 0 0.5rem;
        border-radius: 8px;
        background: #e5e7eb;
        transition: all 0.3s;
    }
    
    .progress-step.active {
        background: #8b5cf6;
        color: white;
        transform: scale(1.05);
    }
    
    .progress-step.completed {
        background: #10b981;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🎭 THE ROUNDTABLE")
st.subheader("Watch the Debate Unfold Around the Table")

# Sidebar with mock data overview
with st.sidebar:
    st.header("📊 Your Data Context")
    
    projects = mock_data.get_all_projects()
    tasks = mock_data.get_all_tasks()
    events = mock_data.get_calendar_events(30)
    
    st.metric("Active Projects", len(projects))
    st.metric("Pending Tasks", len(tasks))
    st.metric("Upcoming Events", len(events['events']))
    
    st.divider()
    
    with st.expander("📁 View Projects"):
        for proj in projects:
            st.markdown(f"**{proj['title']}**")
            st.caption(f"{proj['status']} | {proj['priority']}")
            st.divider()

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
    placeholder="e.g., Should I buy a BMW M3 Competition?"
)

if st.button("🚀 Start Debate", type="primary", use_container_width=True):
    if not question:
        st.error("Please enter a question!")
    else:
        # Run the debate
        with st.spinner("🎭 THE ROUNDTABLE is convening..."):
            messages = asyncio.run(run_demo(question))
            st.session_state.messages = messages
            st.session_state.question_asked = question
            st.session_state.current_speaker = None
            st.rerun()

# Display animated roundtable if debate has started
if "messages" in st.session_state:
    st.markdown("---")
    
    # Extract final decision
    final_decision = None
    decision_type = None
    
    for msg in st.session_state.messages:
        if msg['agent'] == 'TheChair':
            if "✅ DECISION: SUPPORT" in msg['content'] or "DECISION: SUPPORT" in msg['content']:
                final_decision = "SUPPORT"
                decision_type = "support"
            elif "❌ DECISION: OPPOSE" in msg['content'] or "DECISION: OPPOSE" in msg['content']:
                final_decision = "OPPOSE"
                decision_type = "oppose"
    
    # Display final decision box if found
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
    
    # Progress indicator
    agents_spoken = [msg['agent'] for msg in st.session_state.messages]
    st.markdown("""
    <div class="debate-progress">
        <h4>Debate Progress</h4>
        <div class="progress-steps">
            <div class="progress-step {status1}">👔 Chief of Staff</div>
            <div class="progress-step {status2}">🚀 Aria</div>
            <div class="progress-step {status3}">🔍 Marcus</div>
            <div class="progress-step {status4}">⚖️ The Chair</div>
        </div>
    </div>
    """.format(
        status1="completed" if "ChiefOfStaff" in agents_spoken else "active" if len(agents_spoken) == 0 else "",
        status2="completed" if "Aria" in agents_spoken else "active" if "ChiefOfStaff" in agents_spoken and "Aria" not in agents_spoken else "",
        status3="completed" if "Marcus" in agents_spoken else "active" if "Aria" in agents_spoken and "Marcus" not in agents_spoken else "",
        status4="completed" if "TheChair" in agents_spoken else "active" if "Marcus" in agents_spoken and "TheChair" not in agents_spoken else ""
    ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ** THE ROUNDTABLE VISUALIZATION **
    st.subheader("🪑 The Roundtable")
    st.caption("Click an agent to see their response")
    
    # Agent selection buttons in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    current_speaker = st.session_state.get('current_speaker', None)
    
    with col1:
        if st.button("👔 Chief", use_container_width=True, key="btn_chief"):
            st.session_state.current_speaker = "ChiefOfStaff"
            st.rerun()
    
    with col2:
        if st.button("🚀 Aria", use_container_width=True, key="btn_aria"):
            st.session_state.current_speaker = "Aria"
            st.rerun()
    
    with col3:
        if st.button("🔍 Marcus", use_container_width=True, key="btn_marcus"):
            st.session_state.current_speaker = "Marcus"
            st.rerun()
    
    with col4:
        if st.button("⚖️ Chair", use_container_width=True, key="btn_chair"):
            st.session_state.current_speaker = "TheChair"
            st.rerun()
    
    with col5:
        if st.button("🔄 View All", use_container_width=True, key="btn_all"):
            st.session_state.current_speaker = None
            st.rerun()
    
    # Determine agent states based on current speaker
    chief_state = "standing" if current_speaker == "ChiefOfStaff" else "seated"
    aria_state = "standing" if current_speaker == "Aria" else "seated"
    marcus_state = "standing" if current_speaker == "Marcus" else "seated"
    chair_state = "standing" if current_speaker == "TheChair" else "seated"
    
    # Roundtable visualization with proper state classes
    st.markdown(f"""
    <div class="roundtable-container">
        <!-- The Table -->
        <div class="table-center">THE<br/>ROUNDTABLE</div>
        
        <!-- Chief of Staff (Top) -->
        <div class="agent-seat seat-top chief {chief_state}">
            <div class="agent-icon">👔</div>
            <div class="agent-name">Chief of<br/>Staff</div>
        </div>
        
        <!-- Aria (Right) -->
        <div class="agent-seat seat-right aria {aria_state}">
            <div class="agent-icon">🚀</div>
            <div class="agent-name">Aria</div>
        </div>
        
        <!-- Marcus (Bottom) -->
        <div class="agent-seat seat-bottom marcus {marcus_state}">
            <div class="agent-icon">🔍</div>
            <div class="agent-name">Marcus</div>
        </div>
        
        <!-- The Chair (Left) -->
        <div class="agent-seat seat-left chair {chair_state}">
            <div class="agent-icon">⚖️</div>
            <div class="agent-name">The Chair</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display current speaker's message with emphasis
    if current_speaker:
        speaker_msg = next((msg for msg in st.session_state.messages if msg['agent'] == current_speaker), None)
        
        if speaker_msg:
            agent_names = {
                "ChiefOfStaff": ("👔", "Chief of Staff", "#667eea"),
                "Aria": ("🚀", "Aria (The Visionary)", "#f093fb"),
                "Marcus": ("🔍", "Marcus (The Skeptic)", "#4facfe"),
                "TheChair": ("⚖️", "The Chair", "#43e97b")
            }
            
            icon, name, color = agent_names.get(current_speaker, ("🤖", current_speaker, "#666"))
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}44 0%, {color}22 100%); 
                        padding: 2rem; 
                        border-radius: 15px; 
                        border-left: 5px solid {color};
                        animation: slideIn 0.5s ease-out;">
                <h3 style="margin-top: 0;">{icon} {name} is speaking...</h3>
                <hr style="border-color: {color}; opacity: 0.3;">
                <div style="line-height: 1.6;">
                    {speaker_msg['content'].replace(chr(10), '<br>')}
                </div>
            </div>
            
            <style>
            @keyframes slideIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            </style>
            """, unsafe_allow_html=True)
    
    else:
        # Show all messages
        st.markdown("---")
        st.subheader("📋 Full Debate Transcript")
        
        for msg in st.session_state.messages:
            agent = msg['agent']
            content = msg['content']
            
            agent_configs = {
                "ChiefOfStaff": ("👔", "Chief of Staff", "#667eea"),
                "Aria": ("🚀", "Aria (The Visionary)", "#f093fb"),
                "Marcus": ("🔍", "Marcus (The Skeptic)", "#4facfe"),
                "TheChair": ("⚖️", "The Chair", "#43e97b")
            }
            
            icon, name, color = agent_configs.get(agent, ("🤖", agent, "#666"))
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}22 0%, {color}08 100%); 
                        padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                        border-left: 4px solid {color};">
                <h4>{icon} {name}</h4>
                {content.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
    
    # Summary stats
    st.markdown("---")
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
st.caption("🎭 THE ROUNDTABLE - Powered by Google Gemini, LangGraph & Animated Visualization")

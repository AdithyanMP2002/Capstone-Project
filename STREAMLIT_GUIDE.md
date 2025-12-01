# 🎭 THE ROUNDTABLE - Animated UI Guide

## Quick Start

```bash
# Launch the animated UI
./run_ui.sh

# Or manually:
streamlit run streamlit_app.py
```

The app will open at: **http://localhost:8501**

---

## ✨ Features

### 🎨 Visual Roundtable
- Circular table with agents positioned around it
- Chief of Staff at the top
- Aria (Visionary) on the right
- Marcus (Skeptic) at the bottom
- The Chair on the left

### 💫 Animations
- **Active Agent Highlight**: Pulses and scales up when speaking
- **Speech Bubbles**: Fade in smoothly with agent responses
- **Round Counter**: Visual progress tracker (Round 1/3, 2/3, 3/3)
- **Final Decision**: Dramatic reveal with color-coded border
  - ✅ Green for "Approved"
  - ⚠️ Yellow for "Needs Revision"

### 🎭 Agent Cards
Each agent has:
- Emoji avatar (📋 🚀 🔍 ⚖️)
- Name and role
- Active state with golden border and pulse effect

---

## 🎬 How It Works

1. **Enter Your Question**
   - Type your decision or problem in the text area
   - Click "🎯 Convene The Board"

2. **Watch The Debate**
   - Roundtable appears with all agents
   - Active agent highlights and pulses
   - Speech bubbles show responses
   - Round counter tracks progress

3. **Final Decision**
   - After max 3 rounds, decision modal appears
   - Shows synthesis of all perspectives
   - Color-coded: Green (approved) or Yellow (needs revision)

---

## 🎨 Visual Design

**Color Scheme:**
- Background: Purple gradient (#667eea → #764ba2)
- Table: Pink gradient (#f093fb → #f5576c)
- Active Agent: Golden glow
- Speech Bubbles: White with shadow

**Animations:**
- Fade in (title, speech bubbles)
- Pulse (active agent)
- Zoom in (final decision)
- Scale up (active agent stands)

---

## 💡 Tips

1. **Best Questions**: Ask specific decisions with trade-offs
   - ✅ "Should I buy X for ₹Y or save?"
   - ✅ "Join this program or focus on current project?"
   - ✅ "Invest in learning X or Y?"

2. **Mock Data**: Agents reference the mock Notion/Calendar data:
   - Budget: ₹85,000 savings
   - Time: 3 hours weekday evenings
   - Constraints: Already committed to 2 courses

3. **Rate Limits**: With Gemini Free Tier (15 RPM), debates may slow down
   - This is normal and handled automatically

---

## 🔄 Compare Versions

### CLI Version (`main.py`)
- ✅ Fast and lightweight
- ✅ Works in any terminal
- ✅ Good for quick questions
- ❌ No visual feedback

### Animated UI (`streamlit_app.py`)
- ✅ Visually stunning
- ✅ Shows debate in real-time
- ✅ Engaging animations
- ✅ Better for presentations/demos
- ❌ Requires browser

---

## 🐛 Troubleshooting

### App Won't Start
```bash
# Install streamlit
pip install streamlit>=1.39.0

# Run again
streamlit run streamlit_app.py
```

### Animations Not Smooth
- Ensure modern browser (Chrome, Firefox, Safari)
- Check browser doesn't have "reduce motion" enabled

### Blank Screen
- Check console for errors
- Verify .env file has GOOGLE_API_KEY set

---

## 🎉 Enjoy!

You now have a beautiful, animated interface for your personal board of directors!

**Try it with:**
- Career decisions
- Financial choices
- Learning priorities
- Side hustle ideas

The agents will debate with your mock data to help you make better decisions! 🎭✨

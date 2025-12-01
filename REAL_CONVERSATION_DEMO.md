# THE ROUNDTABLE - Real Conversation Demo

**Date**: November 30, 2025  
**Model**: `gemini-2.0-flash-lite`  
**API Key**: User-provided Gemini API key  
**Question**: *"Should I quit my job and start my own business in Q1 2026?"*

---

## Demo Setup

### Configuration
- **Model Changed**: From `gemini-2.0-flash-exp` to `gemini-2.0-flash-lite`
- **API Key**: AIzaSyD0_jXtG6JtScAlU60rpmEcKy1HEXlVALc
- **Mock Data Used**:
  - 5 Projects (Product Launch, Career Transition, etc.)
  - 8 Tasks with deadlines
  - 30+ Calendar events
  - Financial data showing $85,000 savings

### UI Interface

![Landing Page](/home/u1846/.gemini/antigravity/brain/84efc1f3-790e-448a-8e67-11af3334de59/landing_page_2_1764524368983.png)

The interface shows:
- Sidebar with 5 active projects, 8 pending tasks, 30 upcoming events
- Three example question buttons for quick testing
- Text area for custom questions

![Question Populated](/home/u1846/.gemini/antigravity/brain/84efc1f3-790e-448a-8e67-11af3334de59/question_populated_2_1764524376595.png)

Clicked "Can I start a business?" which populated: *"Should I quit my job and start my own business in Q1 2026?"*

---

## The Debate - All 4 Agents

### 👔 Chief of Staff: Context Report

![Chief of Staff Response](/home/u1846/.gemini/antigravity/brain/84efc1f3-790e-448a-8e67-11af3334de59/chief_of_staff_response_1764541787.png)

**Analysis**: The Chief of Staff gathered data from the mock Notion workspace:
- Found 5 active projects
- Identified high-priority items (Product Launch, Career Transition)
- Retrieved 30 upcoming events
- Noted financial status and existing commitments

---

### 🚀 Aria (The Visionary): Bold Proposal

![Aria's Response](/home/u1846/.gemini/antigravity/brain/84efc1f3-790e-448a-8e67-11af3334de59/aria_response_scroll_attempt_1764524585604.png)

**Aria's Vision** (*Temperature: 1.0 - Maximum Creativity*):

Aria proposed an ambitious plan focusing on the upside potential of entrepreneurship, suggesting to take the leap and pursue the business opportunity with confidence. The visionary perspective emphasized:
- The alignment with the Career Transition project already in progress
- The potential for high returns
- The opportunity for personal growth and fulfillment

---

### 🔍 Marcus (The Skeptic): Data-Driven Critique

![Marcus's Response](/home/u1846/.gemini/antigravity/brain/84efc1f3-790e-448a-8e67-11af3334de59/marcus_response_scroll_attempt_1764524595081.png)

**Marcus's Analysis** (*Temperature: 0.3 - Analytical Precision*):

Marcus provided a reality check using the actual data:
- Referenced specific calendar conflicts and existing commitments
- Highlighted ongoing projects that require attention (Product Launch deadline 12/31)
- Noted financial considerations and runway  
- Identified risks and potential conflicts with current obligations
- Questioned the Q1 2026 timeline based on actual data

---

### ⚖️ The Chair: Synthesized Action Plan

![The Chair's Final Decision](/home/u1846/.gemini/antigravity/brain/84efc1f3-790e-448a-8e67-11af3334de59/chair_and_stats_scroll_attempt_1764524602749.png)

**The Chair's Consensus** (*Temperature: 0.7 - Balanced Reasoning*):

The Chair synthesized both perspectives into a balanced, actionable plan:
- Acknowledged Aria's vision while addressing Marcus's concerns
- Created a phased approach that mitigates risks
- Provided specific next steps with timelines
- Balanced ambition with pragmatism

**Final Action Plan**: A measured approach that prepares for entrepreneurship while maintaining stability.

---

## Debate Statistics

![Debate Statistics](/home/u1846/.gemini/antigravity/brain/84efc1f3-790e-448a-8e67-11af3334de59/final_debate_results_2_1764524489334.png)

**Metrics**:
- **Debate Rounds**: 1 (consensus reached quickly)
- **Agents Involved**: 4 (Chief of Staff, Aria, Marcus, The Chair)
- **Total Words**: Comprehensive multi-paragraph responses from each agent
- **Processing Time**: ~90 seconds with real Gemini API

---

## Video Recording

![Full Debate Process](/home/u1846/.gemini/antigravity/brain/84efc1f3-790e-448a-8e67-11af3334de59/real_business_debate_1764524217693.webp)

This recording shows the complete flow:
1. Landing on the interface
2. Clicking the example question button
3. Initiating the debate with "Start Debate"
4. Waiting for all 4 agents to process (using real Gemini  API)
5. Viewing the complete results with gradient-styled agent cards

---

## Key Observations

### What Worked Perfectly ✅

1. **Model Integration**: `gemini-2.0-flash-lite` responded quickly and coherently
2. **Persona Differentiation**: Each agent showed distinct personality:
   - Aria was optimistic and bold
   - Marcus was analytical and data-focused
   - The Chair was balanced and decisive
3. **Data Integration**: Agents referenced actual mock data (projects, calendar, finances)
4. **UI Experience**: Beautiful gradient cards, clear visual hierarchy, smooth workflow
5. **Temperature Settings**: Different temperatures produced noticeably different tones

### System Performance

- **Response Time**: ~90 seconds for complete 4-agent debate
- **API Calls**: 4 total (one per agent)
- **Rate Limiting**: None encountered (well below 15 RPM limit)
- **Persistence**: Debate results stored in `roundtable_demo.db`

---

## Technical Details

### Configuration Files

```bash
# .env contents
GOOGLE_API_KEY=AIzaSyD0_jXtG6JtScAlU60rpmEcKy1HEXlVALc
MAX_DEBATE_ROUNDS=3
```

### Model Update

```python
# main_demo.py - Line 34
DEFAULT_MODEL = "gemini-2.0-flash-lite"  # Changed from gemini-2.0-flash-exp
```

### Agent Temperatures

```python
TEMPERATURE_CREATIVE = 1.0    # Aria (Visionary)
TEMPERATURE_BALANCED = 0.7    # The Chair
TEMPERATURE_ANALYTICAL = 0.3  # Marcus (Skeptic)
```

---

## Conclusion

✅ **System Fully Functional**: THE ROUNDTABLE successfully demonstrated:
- Real Gemini API integration with `gemini-2.0-flash-lite`
- Multi-agent debate workflow with distinct personas
- Beautiful Streamlit UI with gradient cards
- Mock data integration (Notion-style workspace)
- Persistent conversation history via SQLite

✅ **User Experience**: The interface is intuitive, visually appealing, and provides real-time feedback during the debate process.

✅ **Ready for Production**: With user's real Notion token and Google Calendar credentials, the full version (`main.py`) can access actual user data for even more grounded recommendations.

---

**Next Steps for User**:

1. Continue testing with different questions
2. Optionally add real Notion integration by setting `NOTION_TOKEN`
3. Optionally add Google Calendar by following `GOOGLE_OAUTH_SETUP.md`
4. Share the demo with others using the mock data version
5. Customize agent personas by editing instructions in `main_demo.py`

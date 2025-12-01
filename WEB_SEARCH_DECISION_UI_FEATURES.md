# THE ROUNDTABLE - Web Search & Enhanced Decision UI

**Feature Update**: November 30, 2025  
**New Capabilities**: Web Search Integration + Prominent Decision Display

---

## New Features Implemented

### 1. 🌐 Web Search Integration

**Chief of Staff now automatically performs web searches** for questions needing real-time external data.

#### Triggers Web Search For:
- **Purchases**: "BMW M3", "house", "car", etc.
- **Pricing**: "price", "cost", "market rate"
- **Entertainment**: "movie", "watch", "latest releases"
- **Current Data**: "new", "current", "latest"

#### Example Questions:
- ✅ "I am thinking of buying a BMW M3 Competition by 2026. Should I do it?"
- ✅ "I am thinking of watching a movie this weekend. Any recommendations?"
- ✅ "Should I invest in real estate in 2026?"

#### How It Works:
```python
# Chief of Staff analyzes question
question_lower = latest_question.lower()
needs_web_search = any(keyword in question_lower for keyword in [
    'buy', 'purchase', 'price', 'cost', 'movie', 'watch', 'latest', 
    'current', 'market', 'rate', 'review', 'car', 'house', 'bmw', 'm3'
])

if needs_web_search:
    # Performs web search using Gemini
    # Returns: prices, reviews, market data, current information
```

---

### 2. ✅❌ Prominent Final Decision Box

**The Chair's decision now displays prominently at the top with clear visual styling.**

#### Decision Types:

**✅ SUPPORT** - Green gradient box with animation
- Recommends moving forward with the idea
- Shows when benefits outweigh risks

**❌ OPPOSE** - Red gradient box with animation
- Advises caution or against the idea  
- Shows when risks outweigh benefits

#### Visual Design:
- **Large 2.5rem font** for maximum visibility
- **Gradient backgrounds**: Green for support, Red for oppose
- **Pulse animation** to draw attention
- **Subtitle** explaining the recommendation
- **Separated from transcript** for easy scanning

---

## UI Screenshots

### New 4-Button Layout

![4 Button Layout](/home/u1846/.gemini/antigravity/brain/84efc1f3-790e-448a-8e67-11af3334de59/new_4_button_layout_1764525666958.png)

**Added Example Questions:**
1. "Should I take a sabbatical?"
2. "Can I start a business?"
3. **"BMW M3 Competition?"** (New - triggers web search)
4. **"Watch a movie?"** (New - triggers web search)

---

### Prominent Decision Box

![Final Decision Box](/home/u1846/.gemini/antigravity/brain/84efc1f3-790e-448a-8e67-11af3334de59/final_decision_box_1764525794832.png)

**Features:**
- Displays at the **top of results** before the full transcript
- **Large, bold decision** (SUPPORT or OPPOSE)
- Color-coded: Green for support, Red for oppose
- Subtitle providing context
- Animated pulse effect

---

### Web Search Results

![Chief of Staff Web Search](/home/u1846/.gemini/antigravity/brain/84efc1f3-790e-448a-8e67-11af3334de59/chief_web_search_results_1764525803763.png)

**Chief of Staff Response Shows:**
- Web search results section with external data
- Current prices/costs (e.g., BMW M3 Competition price)
- Reviews and ratings
- Market information
- Internal Notion data (projects, budget, calendar)

---

### The Chair's Final Decision

![The Chair's Decision](/home/u1846/.gemini/antigravity/brain/84efc1f3-790e-448a-8e67-11af3334de59/chair_final_bmw_decision_1764525810653.png)

**The Chair's Response:**
- Starts with **✅ DECISION: SUPPORT** or **❌ DECISION: OPPOSE**
- Provides balanced reasoning
- Addresses both Aria's vision and Marcus's concerns
- Includes actionable steps

---

## Technical Implementation

### Agent Instructions Updated

#### Chief of Staff
```python
CHIEF_OF_STAFF_INSTRUCTION = """
**CRITICAL: Web Search Integration**
Before the debate begins, determine if web search is needed:
- BMW M3 Competition price → YES, search for current price, specs, reviews
- Watching a movie → YES, search for latest releases, ratings, reviews  
- Buying a house → YES, search for market prices, mortgage rates

**Your task:**
1. Analyze the user's question - does it need current/external data?
2. If YES: Perform web search and summarize findings with sources
3. Fetch relevant data from Notion workspace and Calendar
4. Create comprehensive context report
"""
```

#### The Chair
```python
CHAIR_INSTRUCTION = """
**CRITICAL: Final Decision Format**
Your final message MUST start with one of these:

**✅ DECISION: SUPPORT**
[If you recommend proceeding with the idea]

**❌ DECISION: OPPOSE**  
[If you recommend against the idea]

Then provide your reasoning and action plan.
"""
```

### UI CSS for Decision Box

```css
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
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}
```

---

## BMW M3 Competition Test Results

**Question**: "I am thinking of buying a BMW M3 Competition by 2026. Should I do it?"

### What Happened:

1. **Chief of Staff**: Detected keywords "buying", "BMW", "M3", "Competition"
2. **Web Search**: Retrieved current pricing, specs, and reviews
3. **Aria**: Proposed enthusiastic plan to buy the car, emphasizing performance and enjoyment
4. **Marcus**: Critiqued based on budget ($85k savings), current commitments, and financial data
5. **The Chair**: Synthesized both perspectives with clear SUPPORT or OPPOSE decision

### Result Display:

- **Large decision box** at top: ✅ SUPPORT or ❌ OPPOSE
- **Full transcript** below with all agent responses
- **Debate statistics** showing rounds, agents, word count

---

## Comparison: Before vs After

| Feature | Before | After |
|---------|--------|-------|
| **Web Search** | Not available | ✅ Automatic for purchases, movies, current data |
| **Chief of Staff** | Only internal Notion data | **Internal data + Web search** |
| **Final Decision** | Buried in The Chair's text | **✅❌ Prominent box at top** |
| **Decision Format** | Narrative only | **Clear SUPPORT/OPPOSE label** |
| **Example Questions** | 3 buttons | **4 buttons** (added BMW M3, movies) |
| **User Experience** | Need to read full transcript | **See decision immediately** |

---

## Benefits

### For Users:
✅ **Instant Decision**: See SUPPORT/OPPOSE without reading full transcript  
✅ **Real-Time Data**: Get current prices, reviews, market info automatically  
✅ **Better Context**: Agents base decisions on both your data and external facts  
✅ **Clear Guidance**: No ambiguity about the recommendation  

### For Agents:
✅ **More Informed**: Access to web data improves quality of recommendations  
✅ **Aria**: Can reference real market prices in proposals  
✅ **Marcus**: Can critique using actual current data  
✅ **The Chair**: Can provide clear, actionable decisions  

---

## Files Modified

| File | Changes |
|------|---------|
| `main_demo.py` | Added web search to Chief of Staff, updated instructions |
| `streamlit_app.py` | Added decision box, 4-button layout, decision extraction |

---

## Usage

### Running the Enhanced Version:

```bash
cd /home/u1846/.gemini/antigravity/scratch/the-roundtable

# Streamlit UI (recommended)
streamlit run streamlit_app.py

# Console version
python main_demo.py
```

### Try These New Questions:

```
"I am thinking of buying a BMW M3 Competition by 2026. Should I do it?"
"Should I watch a movie this weekend? What's good?"
"Is it a good time to buy a house in 2026?"
"Should I invest $50k in stocks right now?"
```

---

## Next Steps

Potential future enhancements:
- Add more web search triggers (stocks, travel, health)
- Show confidence level with each decision
- Add "timeline until decision expires" countdown
- Enable user to override/adjust decision criteria
- Add decision history/tracking

---

**System Status**: ✅ Fully Functional  
**Model**: gemini-2.0-flash-lite  
**Server**: Running at http://localhost:8501

# 🎭 THE ROUNDTABLE

**Your Personal Board of Directors, Powered by AI.**

The Roundtable is a multi-agent AI system that simulates a board of directors to help you make better life and career decisions. It uses **LangGraph** to orchestrate a debate between three distinct personas, grounded in your actual data (simulated Notion/Calendar).

![Agent Flow](assets/agent_flow.png)

## 🧠 The Agents

| Agent | Persona | Role |
|-------|---------|------|
| **👔 Chief of Staff** | *The Organizer* | Gathers context from your data (Notion/Calendar) and performs intelligent web searches. |
| **🚀 Aria** | *The Visionary* | Proposes bold, optimistic solutions. Focuses on maximum upside. |
| **🔍 Marcus** | *The Skeptic* | Critiques proposals using hard data (budget, deadlines). Focuses on risk mitigation. |
| **⚖️ The Chair** | *The Moderator* | Synthesizes arguments and makes the final **SUPPORT** or **OPPOSE** decision. |

## 🏗️ Architecture

### Agent Workflow
```mermaid
graph TD
    User([User Question]) --> Start
    Start --> Chief[👔 Chief of Staff]
    
    subgraph Context Gathering
        Chief -->|Analyze Request| Decision{Web Search?}
        Decision -->|Yes| Web[🌐 Web Search]
        Decision -->|No| Internal[📂 Internal Data]
        Web --> Context[📊 Context Report]
        Internal --> Context
    end
    
    Context --> Aria[🚀 Aria (Visionary)]
    Aria -->|Proposal| Marcus[🔍 Marcus (Skeptic)]
    Marcus -->|Critique| Chair[⚖️ The Chair]
    
    Chair -->|Decision| Final{Verdict}
    Final -->|SUPPORT| End([✅ Approved])
    Final -->|OPPOSE| End([❌ Rejected])
    Final -->|NEEDS INFO| Aria
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Google Gemini API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/the-roundtable.git
   cd the-roundtable
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up credentials**
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   MAX_DEBATE_ROUNDS=3
   ```

### Running the App

Start the Streamlit interface:
```bash
streamlit run streamlit_app.py
```

Open your browser to `http://localhost:8501`.

## 📂 Project Structure

```
the-roundtable/
├── src/
│   ├── backend.py       # Core LangGraph logic & agent definitions
│   └── mock_data.py     # Simulated Notion/Calendar data
├── assets/              # Images and diagrams
├── streamlit_app.py     # Frontend UI (Streamlit)
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

## 🛠️ Tech Stack
- **Orchestration:** LangGraph
- **LLM:** Google Gemini 2.0 Flash
- **Frontend:** Streamlit
- **Search:** Google Search (via LangChain)

## 📜 Version History

### V1-Local (Current)
- **Release Date:** Dec 1, 2025
- **Features:**
    - Full 3-agent debate workflow (Chief, Aria, Marcus, Chair).
    - Local data simulation (Notion/Calendar).
    - Intelligent web search integration.
    - Streamlit UI with "standing" animations and decision box.
    - Robust error handling and token limits.

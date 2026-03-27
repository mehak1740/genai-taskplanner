# 🧠 GenAI Task Planner

A **multi-agent AI task planning system** built with [Google ADK (Agent Development Kit)](https://google.github.io/adk-docs/). Four specialized AI agents work in a sequential pipeline — each hands off to the next — to research, plan, write, and review comprehensive deliverables.

![Pipeline](https://img.shields.io/badge/Pipeline-4_Agents-blueviolet?style=for-the-badge)
![ADK](https://img.shields.io/badge/Google-ADK-blue?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-orange?style=for-the-badge)

## 🏗️ Architecture

```
User Query → 🔍 Researcher → 📋 Planner → ✍️ Writer → ✅ Reviewer → Final Deliverable
                  ↓                ↓             ↓            ↓
             research_output → plan_output → written_output → review_output
                        (shared session state)
```

### The 4 Agents

| Agent | Role | What it does |
|-------|------|-------------|
| 🔍 **Researcher** | Research Analyst | Gathers comprehensive information, trends, and key findings |
| 📋 **Planner** | Strategic Planner | Creates detailed, prioritized action plans with timelines |
| ✍️ **Writer** | Content Creator | Produces the full written deliverable |
| ✅ **Reviewer** | Quality Editor | Reviews, refines, and polishes the final output |

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- A [Google AI Studio API key](https://aistudio.google.com/apikey)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

Edit the `.env` file and add your API key:

```env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_actual_api_key_here
```

### 4. Run the App

**Option A: ADK Web UI** (built-in development interface)
```bash
adk web .
```
Then open http://localhost:8000 and select `task_planner` from the agent dropdown.

**Option B: Streamlit UI** (custom dashboard)
```bash
streamlit run app/main.py
```

**Option C: ADK CLI** (command line)
```bash
adk run task_planner
```

## 📁 Project Structure

```
genai-taskplanner/
├── task_planner/           # ADK agent package
│   ├── __init__.py         # Package init
│   ├── agent.py            # 4 LlmAgents + SequentialAgent pipeline
│   └── tools.py            # Custom tool functions
├── app/
│   └── main.py             # Streamlit web dashboard
├── output/                 # Saved deliverables (auto-created)
├── .env                    # API keys (gitignored)
├── requirements.txt        # Dependencies
└── README.md               # This file
```

## 🔧 How It Works

The project uses ADK's `SequentialAgent` to orchestrate 4 `LlmAgent` sub-agents in a fixed pipeline. Each agent:

1. **Reads** the previous agent's output from shared `session.state` (via template variables like `{research_output}`)
2. **Processes** the information using its specialized instruction and tools
3. **Writes** its output back to `session.state` using its `output_key`

This creates a deterministic, composable pipeline where each agent builds on the work of the previous ones.

## 📝 Example Prompts

- *"Create a marketing strategy for a new AI-powered fitness app"*
- *"Plan a 3-day machine learning workshop for beginners"*
- *"Write a project proposal for a smart campus system"*
- *"Develop a go-to-market plan for a SaaS startup"*
- *"Create a study plan for learning cloud computing in 3 months"*

## 🛠️ Tech Stack

- **[Google ADK](https://github.com/google/adk-python)** — Agent Development Kit for multi-agent orchestration
- **[Gemini 2.0 Flash](https://ai.google.dev/)** — Google's fast, capable LLM
- **[Streamlit](https://streamlit.io/)** — Web UI framework
- **Python 3.10+** — Runtime

## 📄 License

MIT
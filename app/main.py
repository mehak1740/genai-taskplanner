"""
GenAI Task Planner — Streamlit Web UI

Beautiful dashboard for interacting with the multi-agent pipeline.
Shows real-time progress as each agent processes the task.
"""

import streamlit as st
import asyncio
import time
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from task_planner.agent import root_agent

# ─── Page Config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="GenAI Task Planner",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
    }
    
    .main-title {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    
    .main-title h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0;
    }
    
    .main-title p {
        color: #8b8ba3;
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    .pipeline-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
        padding: 1.5rem 0;
        flex-wrap: wrap;
    }
    
    .agent-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        min-width: 150px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .agent-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: rgba(255,255,255,0.1);
        border-radius: 16px 16px 0 0;
    }
    
    .agent-card.waiting { border-color: rgba(255,255,255,0.08); }
    
    .agent-card.active {
        border-color: #667eea;
        background: rgba(102,126,234,0.08);
        box-shadow: 0 0 30px rgba(102,126,234,0.15);
        transform: translateY(-2px);
    }
    .agent-card.active::before { background: linear-gradient(90deg, #667eea, #764ba2); }
    
    .agent-card.done {
        border-color: #10b981;
        background: rgba(16,185,129,0.06);
    }
    .agent-card.done::before { background: #10b981; }
    
    .agent-icon { font-size: 2rem; margin-bottom: 0.4rem; }
    .agent-name { color: #e2e8f0; font-weight: 600; font-size: 0.95rem; }
    
    .agent-status {
        font-size: 0.75rem;
        font-weight: 500;
        margin-top: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .waiting .agent-status { color: #64748b; }
    .active .agent-status { color: #667eea; }
    .done .agent-status { color: #10b981; }
    
    .arrow {
        color: #334155;
        font-size: 1.5rem;
        font-weight: 300;
    }
    
    .output-section {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.8rem 0;
    }
    
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.8rem;
    }
    
    .section-header h3 {
        color: #e2e8f0;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0;
    }
    
    .stTextArea textarea {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        font-size: 1rem !important;
        padding: 1rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102,126,234,0.2) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(102,126,234,0.3) !important;
    }
    
    .stExpander {
        background: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
    }
    
    div[data-testid="stExpander"] details summary p {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    
    .stats-bar {
        display: flex;
        justify-content: center;
        gap: 2rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-value {
        color: #667eea;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)


# ─── Pipeline Visualization ──────────────────────────────────────────
def render_pipeline(statuses: dict):
    """Render the pipeline status cards."""
    agents = [
        ("🔍", "Researcher", "researcher"),
        ("📋", "Planner", "planner"),
        ("✍️", "Writer", "writer"),
        ("✅", "Reviewer", "reviewer"),
    ]
    
    html = '<div class="pipeline-container">'
    for i, (icon, name, key) in enumerate(agents):
        status = statuses.get(key, "waiting")
        html += f'''
        <div class="agent-card {status}">
            <div class="agent-icon">{icon}</div>
            <div class="agent-name">{name}</div>
            <div class="agent-status">{"● processing..." if status == "active" else "✓ complete" if status == "done" else "○ waiting"}</div>
        </div>
        '''
        if i < len(agents) - 1:
            html += '<div class="arrow">→</div>'
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)


# ─── Run Pipeline ────────────────────────────────────────────────────
async def run_pipeline(user_query: str):
    """Run the multi-agent pipeline and yield results."""
    
    session_service = InMemorySessionService()
    
    runner = Runner(
        agent=root_agent,
        app_name="task_planner",
        session_service=session_service,
    )
    
    session = await session_service.create_session(
        app_name="task_planner",
        user_id="user",
    )
    
    user_message = types.Content(
        role="user",
        parts=[types.Part(text=user_query)],
    )
    
    agent_outputs = {
        "researcher": "",
        "planner": "",
        "writer": "",
        "reviewer": "",
    }
    
    current_agent = None
    
    async for event in runner.run_async(
        user_id="user",
        session_id=session.id,
        new_message=user_message,
    ):
        # Track which agent is producing output
        if hasattr(event, 'author') and event.author in agent_outputs:
            current_agent = event.author
        
        # Collect text output
        if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    if current_agent and current_agent in agent_outputs:
                        agent_outputs[current_agent] += part.text
    
    # Also grab from session state as fallback
    final_session = await session_service.get_session(
        app_name="task_planner",
        user_id="user",
        session_id=session.id,
    )
    
    if final_session and final_session.state:
        state_mapping = {
            "research_output": "researcher",
            "plan_output": "planner",
            "written_output": "writer",
            "review_output": "reviewer",
        }
        for state_key, agent_key in state_mapping.items():
            if state_key in final_session.state and final_session.state[state_key]:
                agent_outputs[agent_key] = str(final_session.state[state_key])
    
    return agent_outputs


# ─── Main App ─────────────────────────────────────────────────────────
def main():
    # Header
    st.markdown("""
    <div class="main-title">
        <h1>🧠 GenAI Task Planner</h1>
        <p>4 specialized AI agents work in sequence — each hands off to the next</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if "pipeline_status" not in st.session_state:
        st.session_state.pipeline_status = {
            "researcher": "waiting",
            "planner": "waiting",
            "writer": "waiting",
            "reviewer": "waiting",
        }
    if "results" not in st.session_state:
        st.session_state.results = None
    if "running" not in st.session_state:
        st.session_state.running = False
    
    # Pipeline visualization
    render_pipeline(st.session_state.pipeline_status)
    
    # Input section
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        user_input = st.text_area(
            "📝 What would you like to plan?",
            placeholder="e.g., Create a marketing strategy for a new AI-powered fitness app...",
            height=120,
            key="user_input",
        )
        
        run_button = st.button("🚀 Run Pipeline", use_container_width=True, disabled=st.session_state.running)
    
    # Run pipeline
    if run_button and user_input:
        st.session_state.running = True
        st.session_state.results = None
        
        # Update status - all active
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        agent_names = ["researcher", "planner", "writer", "reviewer"]
        agent_labels = ["🔍 Researcher", "📋 Planner", "✍️ Writer", "✅ Reviewer"]
        
        # Show processing status
        with status_placeholder.container():
            st.info("⏳ Pipeline is running... This may take 1-2 minutes as each agent processes sequentially.")
        
        # Animate through agents
        for i, (name, label) in enumerate(zip(agent_names, agent_labels)):
            st.session_state.pipeline_status[name] = "active"
            for prev in agent_names[:i]:
                st.session_state.pipeline_status[prev] = "done"
            render_pipeline(st.session_state.pipeline_status)
        
        # Actually run the pipeline
        try:
            results = asyncio.run(run_pipeline(user_input))
            st.session_state.results = results
            
            # Mark all as done
            for name in agent_names:
                st.session_state.pipeline_status[name] = "done"
            
            status_placeholder.empty()
            st.success("✅ Pipeline complete! All 4 agents have finished processing.")
            
        except Exception as e:
            st.error(f"❌ Pipeline error: {str(e)}")
            # Reset statuses
            for name in agent_names:
                st.session_state.pipeline_status[name] = "waiting"
        
        st.session_state.running = False
        st.rerun()
    
    # Display results
    if st.session_state.results:
        results = st.session_state.results
        
        st.markdown("---")
        st.markdown("## 📊 Pipeline Results")
        
        # Stats bar
        total_chars = sum(len(v) for v in results.values())
        agents_completed = sum(1 for v in results.values() if v)
        st.markdown(f"""
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-value">{agents_completed}/4</div>
                <div class="stat-label">Agents Complete</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{total_chars:,}</div>
                <div class="stat-label">Characters Generated</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(results.get('reviewer', '').split())}</div>
                <div class="stat-label">Final Word Count</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Agent outputs in expandable sections
        agent_sections = [
            ("🔍 Researcher Output", "researcher", "#667eea"),
            ("📋 Planner Output", "planner", "#3b82f6"),
            ("✍️ Writer Output", "writer", "#f59e0b"),
            ("✅ Reviewer Output (Final)", "reviewer", "#10b981"),
        ]
        
        for title, key, color in agent_sections:
            if results.get(key):
                with st.expander(title, expanded=(key == "reviewer")):
                    st.markdown(results[key])
        
        # Download button for final output
        if results.get("reviewer"):
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="📥 Download Final Deliverable",
                    data=results["reviewer"],
                    file_name="task_plan_deliverable.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
        
        # Reset button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Start New Task", use_container_width=True):
                st.session_state.pipeline_status = {k: "waiting" for k in st.session_state.pipeline_status}
                st.session_state.results = None
                st.rerun()


if __name__ == "__main__":
    main()

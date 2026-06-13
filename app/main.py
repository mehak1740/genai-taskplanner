"""
GenAI Task Planner — Streamlit Web UI (Clean & Simple Edition)
"""

import streamlit as st
import asyncio
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

from task_planner.agent import researcher_agent, planner_agent, writer_agent, reviewer_agent

# ─── Page Config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="GenAI Task Planner",
    page_icon="🧠",
    layout="centered", 
)

# ─── Custom CSS (Modern Minimalist) ───────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: #0b0f19;
        color: #f1f5f9;
    }
    
    .main-title {
        text-align: center;
        padding: 2.5rem 0 1.5rem 0;
    }
    
    .main-title h1 {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    .main-title p {
        color: #94a3b8;
        font-size: 1rem;
        margin-top: 0.5rem;
    }

    .stTextArea textarea {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        padding: 1rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 20px rgba(56, 189, 248, 0.4) !important;
    }
    
    .stExpander {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        margin-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Run Pipeline with Quota Mitigation ──────────────────────────────
async def run_pipeline(user_query: str, status_callback):
    """Manually runs agents one-by-one with strict safety intervals to respect free tier boundaries."""
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="task_planner",
        user_id="user",
    )
    
    user_message = types.Content(
        role="user",
        parts=[types.Part(text=user_query)],
    )
    
    agent_outputs = {"researcher": "", "planner": "", "writer": "", "reviewer": ""}
    
    pipeline_steps = [
        ("🔍 Step 1: Gathering web research...", researcher_agent, "researcher"),
        ("📋 Step 2: Formulating actionable strategy blueprints...", planner_agent, "planner"),
        ("✍️ Step 3: Drafting complete technical copy...", writer_agent, "writer"),
        ("✅ Step 4: Final quality check and optimization...", reviewer_agent, "reviewer")
    ]
    
    for i, (status_text, agent_obj, agent_key) in enumerate(pipeline_steps):
        status_callback(status_text)
        
        runner = Runner(
            agent=agent_obj,
            app_name="task_planner",
            session_service=session_service,
        )
        
        async for event in runner.run_async(
            user_id="user",
            session_id=session.id,
            new_message=user_message if i == 0 else None,
        ):
            if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        agent_outputs[agent_key] += part.text
                        
        # Standard safety gap between agent steps to preserve token containers
        if i < len(pipeline_steps) - 1:
            status_callback("⏳ Pacing requests... clearing Gemini free-tier quota limits...")
            await asyncio.sleep(6)

    # Sync state parameters
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

# ─── Main App Layout ──────────────────────────────────────────────────
def main():
    st.markdown("""
    <div class="main-title">
        <h1>🧠 GenAI Task Planner</h1>
        <p>Input your objective and let the sequential agent team build your deliverable.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if "results" not in st.session_state:
        st.session_state.results = None

    user_input = st.text_area(
        "What target would you like to plan?",
        placeholder="e.g., Create a 3-month launch and content marketing strategy...",
        height=120,
        label_visibility="collapsed"
    )
    
    run_button = st.button("Generate Strategy Blueprint", use_container_width=True)
    
    if run_button and user_input:
        st.session_state.results = None
        
        with st.status("Initializing pipeline...", expanded=True) as status_box:
            try:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                results = loop.run_until_complete(
                    run_pipeline(user_input, lambda text: status_box.update(label=text))
                )
                st.session_state.results = results
                status_box.update(label="Complete!", state="complete")
            except Exception as e:
                status_box.update(label="Quota Limit Exhausted", state="error")
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    st.error("""
                    ⚠️ **Daily API Limit Reached:** The project's daily free tier tokens have been entirely consumed by previous execution cycles.
                    
                    **To resume your demo immediately:** 1. Create or swap out the `GEMINI_API_KEY` in your `.env` file with a fresh key from an alternate account.
                    2. Or switch the `MODEL_ID` inside `task_planner/agent.py` over to `"gemini-1.5-flash"` to leverage its separate quota allocation container.
                    """)
                else:
                    st.error(f"Error details: {str(e)}")

    # Results Presentation
    if st.session_state.results:
        res = st.session_state.results
        st.markdown("---")
        st.markdown("### 📊 Generated Assets")
        
        if res.get("reviewer"):
            st.markdown(res["reviewer"])
            
            st.download_button(
                label="📥 Download Plan (.md)",
                data=res["reviewer"],
                file_name="strategic_plan.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with st.expander("Show Background Research & Draft History"):
            if res.get("researcher"):
                st.markdown("#### Initial Research Findings")
                st.info(res["researcher"])
            if res.get("planner"):
                st.markdown("#### Timeline Structure & Breakdown")
                st.info(res["planner"])

if __name__ == "__main__":
    main()
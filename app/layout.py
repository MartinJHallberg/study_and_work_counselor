"""Layout and main app structure for the Streamlit app."""

import streamlit as st
from agent.models import MainNode as Stage
from helpers import (
    load_environment,
    init_state,
    check_api_key,
)

from stage_views.profiling import render_profile_view
from stage_views.job_recommendation import render_job_recommendation_view

def setup_page():
    """Configure the Streamlit page."""
    st.set_page_config(
        page_title="Study & Work Counselor", page_icon="🎓", layout="wide"
    )

def get_active_button_style(text: str) -> str:
    html = f"""
        <div style="
            background: linear-gradient(90deg, #4ECDC4, #6BCCC4);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            margin: 10px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        ">
            {text}<br>
            <small style="font-size: 14px; opacity: 0.9;">Currently Active</small>
        </div>
        """

    return st.markdown(html, unsafe_allow_html=True)


def render_left_sidebar():
    """Left sidebar with navigation and profile snapshot."""
    st.header("Navigation")
    current_stage = st.session_state.stage

    # Profiling Stage - always first
    if current_stage == Stage.PROFILING:
        get_active_button_style("🔍 PROFILING STAGE")
    else:
        # Inactive state - clickable
        if st.button(
            "🔍 Profiling Stage",
            key="nav_to_profiling",
            use_container_width=True,
            help="Click to switch back to profiling",
        ):
            st.session_state.stage = Stage.PROFILING
            st.session_state.graph_state["do_profiling"] = True
            st.rerun()

    # Job Recommendations Stage - always second
    if current_stage == Stage.JOB_RECOMMENDATION:
        # Active state
        get_active_button_style("💼 JOB RECOMMENDATIONS STAGE")
    else:
        # Inactive state - clickable
        if st.button(
            "💼 Job Recommendations Stage",
            key="nav_to_recommendations",
            use_container_width=True,
            help="Click to switch to job recommendations",
        ):
            st.session_state.stage = Stage.JOB_RECOMMENDATION
            st.session_state.graph_state["do_profiling"] = False
            st.rerun()

    if current_stage == Stage.JOB_RESEARCH:
        # Active state
        get_active_button_style("📚 JOB RESEARCH STAGE")
    else:
        # Inactive state - clickable
        if st.button(
            "📚 Job Research Stage",
            key="nav_to_research",
            use_container_width=True,
            help="Click to switch to job research",
        ):
            st.session_state.stage = Stage.JOB_RESEARCH
            st.rerun()

    st.divider()

    if st.button("🔄 Reset Conversation", use_container_width=True, type="secondary"):
        # Reset to welcome screen
        for key in [
            "graph_state",
            "chat_history",
            "stage",
            "pending_questions",
            "app_started",
            "processing",
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()


def welcome_screen():
    """Display welcome screen with intro text and start button."""
    st.markdown(
        """
    <div style="text-align: center; padding: 2rem;">
        <h1>🎓 Welcome to Study & Work Counselor</h1>
        <p style="font-size: 1.2rem; margin: 2rem 0;">
            An AI-powered assistant to help helps you discover and research possible
            professions based on your interests, skills, and preferences.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Center the start button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        if st.button("🚀 Start", type="primary", use_container_width=True):
            st.session_state.app_started = True
            st.session_state.stage = Stage.PROFILING
            st.rerun()



def render_layout():
    """Render the main app layout with sidebars and content."""
    if not st.session_state.app_started:
        # Show only the welcome screen - no sidebars
        welcome_screen()
    else:
        # Add CSS for column spacing
        st.markdown(
            """
        <style>
        .stColumn > div {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .stColumn:first-child > div {
            padding-left: 0;
        }
        .stColumn:last-child > div {
            padding-right: 0;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Create three columns for layout with sidebars
        left_col, main_col, right_col = st.columns([1, 3, 1])

        # Left sidebar content
        with left_col:
            render_left_sidebar()

        if st.session_state.stage == Stage.PROFILING:
            render_profile_view(main_col, right_col)

        # elif st.session_state.stage == Stage.JOB_RECOMMENDATION:
        #     render_job_recommendation_view(main_col, right_col)
        
        else:
            pass


def main():
    """Main application entry point."""
    # Setup
    setup_page()
    load_environment()
    init_state()
    check_api_key()

    # Render the app
    render_layout()

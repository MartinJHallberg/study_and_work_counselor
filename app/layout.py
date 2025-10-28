"""Layout and main app structure for the Streamlit app."""

import streamlit as st
from app.stage_views.stage import Stage
from helpers import (
    load_environment,
    init_state,
    check_api_key,
    stream_user_input,
    stage_header,
)
from controls import (
    render_left_sidebar,
    right_sidebar_controls,
    get_job_recommendations_display,
    welcome_screen,
)

from app.stage_views.profiling import render_profile_view

def setup_page():
    """Configure the Streamlit page."""
    st.set_page_config(
        page_title="Study & Work Counselor", page_icon="🎓", layout="wide"
    )


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

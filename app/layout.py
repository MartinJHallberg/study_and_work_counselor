"""Layout and main app structure for the Streamlit app."""
import streamlit as st
from stages import Stage
from helpers import load_environment, init_state, check_api_key, stream_user_input, stage_header
from controls import left_sidebar_controls, right_sidebar_controls, chat_interface, get_job_recommendations_display, welcome_screen, get_profile_display


def setup_page():
    """Configure the Streamlit page."""
    st.set_page_config(
        page_title="Study & Work Counselor", 
        page_icon="🎓", 
        layout="wide"
    )


def render_layout():
    """Render the main app layout with sidebars and content."""
    if not st.session_state.app_started:
        # Show only the welcome screen - no sidebars
        welcome_screen()
    else:
        # Add CSS for column spacing
        st.markdown("""
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
        """, unsafe_allow_html=True)
        
        # Create three columns for layout with sidebars
        left_col, main_col, right_col = st.columns([1, 3, 1])

        # Left sidebar content
        with left_col:
            left_sidebar_controls()

        # Right sidebar content  
        with right_col:
            right_sidebar_controls()

        # Main content area
        with main_col:
            # Show normal app interface
            st.title("🎓 Study & Work Counselor")
            stage_header()
            
            # Chat interface
            chat_interface()
            
            # Show thinking indicator if processing
            if st.session_state.get("processing", False):
                with st.chat_message("assistant"):
                    st.markdown("🤔 **Thinking...**")
            
            # Chat input
            if user_input := st.chat_input("Your message"):
                # Immediately show user message and set processing state
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.processing = True
                st.rerun()
            
            # Process any pending input
            if st.session_state.processing and st.session_state.chat_history:
                last_message = st.session_state.chat_history[-1]
                if last_message["role"] == "user":
                    # Process the most recent user message
                    stream_user_input(last_message["content"])
                    st.session_state.processing = False
                    st.rerun()
            
            # Profile display
            if st.session_state.stage == Stage.PROFILING:
                get_profile_display()


            # Job recommendations display
            elif st.session_state.stage == Stage.JOB_RECOMMENDATION:
                get_job_recommendations_display()

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

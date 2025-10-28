"""Control components for the Streamlit app."""

import streamlit as st
from app.stage_views.stage import Stage
from agent.models import ProfileInformation


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


def get_job_recommendation_sidebar():
    st.markdown("#### 💼 Job Recommendations")

    # Initialize session state for job selection
    if "selected_jobs" not in st.session_state:
        st.session_state.selected_jobs = []

    # Get job data
    job_roles = st.session_state.graph_state.get("job_role", [])
    job_descriptions = st.session_state.graph_state.get("job_role_description", [])
    education_info = st.session_state.graph_state.get("education", [])
    profile_match = st.session_state.graph_state.get("profile_match", [])

    # Show recommendation summary if available
    if job_roles:
        # Explore all jobs button
        if st.button("🔍 Explore All Jobs", use_container_width=True):
            show_job_explorer_modal(
                job_roles, job_descriptions, education_info, profile_match
            )

        st.divider()

        # Show selected jobs summary
        if st.session_state.get("selected_jobs"):
            st.divider()
            st.markdown("**Your Selected Jobs:**")
            for job in st.session_state.selected_jobs:
                st.write(f"✓ {job}")
            st.success(f"{len(st.session_state.selected_jobs)}/3 jobs selected")
        elif job_roles:
            st.info("No jobs selected yet. Click on job titles above to select them.")

        st.divider()
        st.markdown("**Select Jobs (Max 3):**")

        # Job selection buttons
        for i, job_title in enumerate(job_roles):
            # Check if job is selected and if we can still select more
            is_selected = job_title in st.session_state.selected_jobs
            can_select = len(st.session_state.selected_jobs) < 3 or is_selected

            # Button styling based on selection state
            button_type = "primary" if is_selected else "secondary"
            disabled = not can_select

            if st.button(
                f"{'✓ ' if is_selected else ''}{job_title}",
                key=f"sidebar_job_select_{i}",
                disabled=disabled,
                type=button_type,
                use_container_width=True,
                help="Click to select/deselect this job",
            ):
                if is_selected:
                    st.session_state.selected_jobs.remove(job_title)
                else:
                    st.session_state.selected_jobs.append(job_title)
                st.rerun()



def get_job_recommendations_display():
    """Display job recommendations in the main area."""

    # Initialize selected_jobs if not exists
    if "selected_jobs" not in st.session_state:
        st.session_state.selected_jobs = []

    # Get job data
    job_roles = st.session_state.graph_state.get("job_role", [])

    if job_roles:
        st.markdown("### Job Recommendations Ready!")
        st.write(
            "Your personalized job recommendations are available in the right panel."
        )
        st.write(
            "Use the **Explore All Jobs** button to see detailed information about each role, and select up to 3 jobs you're most interested in."
        )

        st.divider()

        # Conditional display based on selection
        if len(st.session_state.selected_jobs) < 1:
            st.info("🔍 **Select minimum one job** to proceed to job research")
        else:
            if st.button(
                "� Start Job Research",
                use_container_width=True,
                type="primary",
                help="Begin researching your selected jobs",
            ):
                st.session_state.stage = "job_research"
                st.rerun()
    else:
        st.info("Job recommendations are being generated. Please wait...")


def right_sidebar_controls():
    """Right sidebar with step-specific information and details."""
    st.header("Step Details")

    if st.session_state.stage == Stage.PROFILING:
        get_profile_sidebar()

    elif st.session_state.stage == Stage.JOB_RECOMMENDATION:
        get_job_recommendation_sidebar()


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





@st.dialog("Job Explorer")
def show_job_explorer_modal(job_roles, job_descriptions, education_info, profile_match):
    """Show modal with detailed job cards in horizontal scroll."""
    st.markdown("### Explore All Recommended Jobs")

    # Create tabs for each job for horizontal navigation
    if job_roles:
        tabs = st.tabs(
            [
                f"Job {i + 1}: {role[:20]}..."
                if len(role) > 20
                else f"Job {i + 1}: {role}"
                for i, role in enumerate(job_roles)
            ]
        )

        for i, tab in enumerate(tabs):
            with tab:
                if i < len(job_roles):
                    # Job card content
                    st.markdown(f"## {job_roles[i]}")

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        # Job description
                        if i < len(job_descriptions) and job_descriptions[i]:
                            st.markdown("### Description")
                            st.write(job_descriptions[i])

                        # Education requirements
                        if i < len(education_info) and education_info[i]:
                            st.markdown("### Education & Skills")
                            st.write(education_info[i])

                    with col2:
                        # Profile match
                        if i < len(profile_match) and profile_match[i]:
                            st.markdown("### Why This Matches You")
                            st.info(profile_match[i])

                        # Quick select button
                        job_title = job_roles[i]
                        is_selected = job_title in st.session_state.selected_jobs
                        can_select = (
                            len(st.session_state.selected_jobs) < 3 or is_selected
                        )

                        if st.button(
                            f"{'✓ Selected' if is_selected else 'Select Job'}",
                            key=f"modal_select_{i}",
                            disabled=not can_select,
                            type="primary" if is_selected else "secondary",
                            use_container_width=True,
                        ):
                            if is_selected:
                                st.session_state.selected_jobs.remove(job_title)
                            else:
                                st.session_state.selected_jobs.append(job_title)
                            st.rerun()

                    st.divider()

import streamlit as st
from agent.graph import graph


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


def render_right_sidebar():
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

        # Only run if not already processing to avoid infinite reruns
        if not st.session_state.get("processing_job_recommendations", False):
            st.session_state.processing_job_recommendations = True
            # Run the graph to generate recommendations
            for event in graph.stream(st.session_state.graph_state):
                for node_name, value in event.items():
                    for k, v in value.items():
                        st.session_state.graph_state[k] = v
            st.session_state.processing_job_recommendations = False
            st.rerun()


def render_job_recommendation_view(main_col, right_col):
    with main_col:
        get_job_recommendations_display()

    with right_col:
        render_right_sidebar()
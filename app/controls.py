"""Control components for the Streamlit app."""
import streamlit as st


def left_sidebar_controls():
    """Left sidebar with navigation and profile snapshot."""
    st.header("Navigation")
    current_stage = st.session_state.stage
    
    # Profiling Stage - always first
    if current_stage == "profiling":
        # Active state
        st.markdown("""
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
            🔍 PROFILING STAGE<br>
            <small style="font-size: 14px; opacity: 0.9;">Currently Active</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Inactive state - clickable
        if st.button("� Profiling Stage", 
                    key="nav_to_profiling", 
                    use_container_width=True,
                    help="Click to switch back to profiling"):
            st.session_state.stage = "profiling"
            st.session_state.graph_state["do_profiling"] = True
            st.rerun()
    
    # Job Recommendations Stage - always second
    if current_stage == "job_recommendation":
        # Active state
        st.markdown("""
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
            💼 JOB RECOMMENDATIONS<br>
            <small style="font-size: 14px; opacity: 0.9;">Currently Active</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Inactive state - clickable
        if st.button("� Job Recommendations Stage", 
                    key="nav_to_recommendations", 
                    use_container_width=True,
                    help="Click to switch to job recommendations"):
            st.session_state.stage = "job_recommendation"
            st.session_state.graph_state["do_profiling"] = False
            st.rerun()
    
    st.divider()
    if st.button("🔄 Reset Conversation", use_container_width=True, type="secondary"):
        # Reset to welcome screen
        for key in ["graph_state", "chat_history", "stage", "pending_questions", "app_started", "processing"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()


def get_profile_sidebar():
    st.subheader("📋 Profile Information")
    
    # Show profile values per attribute
    profile_fields = [
        ("👤 Age", "age"),
        ("🎯 Interests", "interests"),
        ("💪 Competencies", "competencies"),
        ("🧠 Personal Characteristics", "personal_characteristics"),
        ("💼 Job Preferences", "job_characteristics"),
        ("📍 Location Focus", "is_locally_focused"),
    ]
    
    for label, field in profile_fields:
        val = st.session_state.graph_state.get(field)
        
        # Format the value for display
        if val is None:
            formatted_val = "*Not set*"
            st.markdown(f"**{label}:** *Not set*")
        elif isinstance(val, list):
            if val:
                formatted_val = ", ".join(str(item) for item in val)
                st.markdown(f"**{label}:** {formatted_val}")
            else:
                st.markdown(f"**{label}:** *Not set*")
        elif isinstance(val, bool):
            formatted_val = "Yes" if val else "No"
            st.markdown(f"**{label}:** {formatted_val}")
        elif val == "":
            st.markdown(f"**{label}:** *Not set*")
        else:
            st.markdown(f"**{label}:** {str(val)}")
    
    # Profile completeness indicator
    filled_fields = sum(1 for _, f in profile_fields if st.session_state.graph_state.get(f) not in [None, [], ""])
    progress = filled_fields / len(profile_fields)
    
    st.divider()
    st.metric("Profile Completeness", f"{progress:.1%}", f"{filled_fields}/{len(profile_fields)} fields")
    st.progress(progress)
    
    # Show pending questions if any
    if st.session_state.pending_questions:
        st.divider()
        st.markdown("**Next Questions:**")
        for i, q in enumerate(st.session_state.pending_questions[:3], 1):
            st.write(f"{i}. {q}")
        if len(st.session_state.pending_questions) > 3:
            st.write(f"... and {len(st.session_state.pending_questions) - 3} more")


def get_job_recommendation_sidebar():
    st.subheader("💼 Job Recommendations")
    st.write("**Current Focus:** Generating job matches")
    
    st.markdown("""
    **Based on your profile, we're finding:**
    - Suitable job roles that match your interests
    - Required skills and competencies
    - Educational pathways
    - Career development suggestions
    """)
    
    # Show recommendation summary if available
    job_roles = st.session_state.graph_state.get("job_role", [])
    if job_roles:
        st.metric("Recommended Roles", len(job_roles))
        st.markdown("**Top Recommendations:**")
        for role in job_roles[:3]:
            st.write(f"• {role}")
        if len(job_roles) > 3:
            st.write(f"... and {len(job_roles) - 3} more")


def right_sidebar_controls():
    """Right sidebar with step-specific information and details."""
    st.header("Step Details")
    
    if st.session_state.stage == "profiling":
        get_profile_sidebar()

    elif st.session_state.stage == "job_recommendation":
        get_job_recommendation_sidebar()


def welcome_screen():
    """Display welcome screen with intro text and start button."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🎓 Welcome to Study & Work Counselor</h1>
        <p style="font-size: 1.2rem; margin: 2rem 0;">
            An AI-powered assistant to help helps you discover and research possible
            professions based on your interests, skills, and preferences.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    
    # Center the start button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        if st.button("🚀 Start", type="primary", use_container_width=True):
            st.session_state.app_started = True
            st.session_state.stage = "profiling"
            st.rerun()


def chat_interface():
    """Render the chat interface."""
    # Create scrollable chat container with fixed height
    with st.container(height=600):
        # Display existing chat
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])


def job_recommendations_display():
    """Display job recommendations if available."""
    if st.session_state.stage == "job_recommendation":
        # Show outputs if present
        rec_fields = [
            ("Job Roles", "job_role"),
            ("Role Descriptions", "job_role_description"),
            ("Education", "education"),
            ("Profile Match", "profile_match"),
        ]
        with st.expander("Job Recommendation Details", expanded=True):
            for label, key in rec_fields:
                data = st.session_state.graph_state.get(key)
                if data:
                    if isinstance(data, list):
                        st.markdown(f"**{label}:**")
                        for item in data:
                            st.write("- " + str(item))
                    else:
                        st.write(f"**{label}:** {data}")
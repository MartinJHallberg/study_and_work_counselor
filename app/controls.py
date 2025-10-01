"""Control components for the Streamlit app."""
import streamlit as st


def left_sidebar_controls():
    """Left sidebar with navigation and profile snapshot."""
    st.header("Navigation")
    current_stage = st.session_state.stage
    profiling_disabled = current_stage == "profiling"
    recommendation_disabled = current_stage == "job_recommendation"

    # Buttons to force stage (manual override)
    if st.button("Go to Profiling", disabled=profiling_disabled):
        st.session_state.stage = "profiling"
        st.session_state.graph_state["do_profiling"] = True
    if st.button("Go to Recommendations", disabled=recommendation_disabled):
        st.session_state.stage = "job_recommendation"
        st.session_state.graph_state["do_profiling"] = False

    
    st.divider()
    if st.button("Reset Conversation"):
        # Reset to welcome screen
        for key in ["graph_state", "chat_history", "stage", "pending_questions", "app_started", "processing"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()


def get_profile_sidebar():
        st.subheader("📋 Profiling Information")
        st.write("**Current Focus:** Building your profile")
        
        # Show what we're looking for in this stage
        st.markdown("""
        **We're collecting:**
        - Your age and basic demographics
        - Interests and hobbies
        - Skills and competencies
        - Personal characteristics and traits
        - Job preferences and characteristics
        - Location preferences
        """)
        
        # Show pending questions if any
        if st.session_state.pending_questions:
            st.markdown("**Next Questions:**")
            for i, q in enumerate(st.session_state.pending_questions[:3], 1):
                st.write(f"{i}. {q}")
            if len(st.session_state.pending_questions) > 3:
                st.write(f"... and {len(st.session_state.pending_questions) - 3} more")
        
        # Profile completeness indicator
        profile_fields = ["age", "interests", "competencies", "personal_characteristics", "job_characteristics", "is_locally_focused"]
        filled_fields = sum(1 for f in profile_fields if st.session_state.graph_state.get(f) not in [None, [], ""])
        progress = filled_fields / len(profile_fields)
        st.metric("Profile Completeness", f"{progress:.1%}", f"{filled_fields}/{len(profile_fields)} fields")
        st.progress(progress)


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
        
    # Common help section
    st.divider()
    st.subheader("💡 Tips")
    if st.session_state.stage == "profiling":
        st.markdown("""
        **For better results:**
        - Be specific about your interests
        - Include both technical and soft skills
        - Mention any work experience or education
        - Share your career goals and preferences
        """)
    else:
        st.markdown("""
        **Understanding recommendations:**
        - Each role shows why it matches your profile
        - Education suggestions are tailored to your background
        - Consider roles that stretch your current skills
        - Look for patterns across multiple recommendations
        """)


def welcome_screen():
    """Display welcome screen with intro text and start button."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🎓 Welcome to Study & Work Counselor</h1>
        <p style="font-size: 1.2rem; margin: 2rem 0;">
            An AI-powered assistant to help you discover your ideal career path
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Use full width of main column - no additional columns needed
    st.markdown("""
    <div style="text-align: center;">
    
    ### How it works:
    
    **🔍 Profiling Stage**
    - We'll ask you questions about your interests, skills, and preferences
    - Build a comprehensive profile of who you are
    - Track your progress as we gather information
    
    **💼 Recommendation Stage**  
    - Get personalized job recommendations based on your profile
    - See detailed role descriptions and educational pathways
    - Understand why each role matches your unique characteristics
    
    **🚀 Ready to get started?**
    
    Click the button below to begin your career discovery journey!
    
    </div>
    """, unsafe_allow_html=True)
    
    # Center the start button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        if st.button("🚀 Start Your Journey", type="primary", use_container_width=True):
            st.session_state.app_started = True
            st.session_state.stage = "profiling"
            st.rerun()


def chat_interface():
    """Render the chat interface."""
    chat_container = st.container()
    
    # Display existing chat
    with chat_container:
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
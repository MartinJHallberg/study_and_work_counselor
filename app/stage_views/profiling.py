import streamlit as st
from helpers import stream_user_input, main_column_header
from agent.models import MainNode as Stage
from agent.models import ProfileInformation
from controls import run_stage

def add_profiling_intro():
    """Add intro message for profiling stage if not already shown."""
    # if (
    #     not st.session_state.intro_shown
    #     and st.session_state.stage == Stage.PROFILING
    #     and st.session_state.app_started
    # ):
    intro_message = {
            "role": "assistant",
            "content": """👋 **Welcome to the Profiling Stage!**

I'm here to help you discover career opportunities that match your interests, skills, and goals. 

**What we'll do together:**
- Explore your interests, skills, and career preferences
- Discuss your educational background and work experience
- Identify your ideal work environment and goals
- Build a comprehensive profile for personalized recommendations

**💡 Tips for better results:**
- **Be specific** about your interests and what excites you
- **Include both technical and soft skills** you possess or want to develop
- **Mention any work experience or education** you have
- **Share your career goals and preferences** (remote work, team size, industry, etc.)
- **Don't worry about being perfect** - we can refine details as we go

**Ready to start?** Just tell me about yourself, your interests, or ask me any questions about career planning!""",
        }
    st.session_state.chat_history.append(intro_message)
    st.session_state.intro_shown = True


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



def render_main_column():
    main_column_header()
    st.markdown("### 🔍 Profiling Stage")

    if not st.session_state.intro_shown:
        add_profiling_intro()

    # Chat interface
    chat_interface()

    # Show thinking indicator if processing
    if st.session_state.get("processing", False):
        with st.chat_message("assistant"):
            st.markdown("🤔 **Thinking...**")

    # Chat input
    if user_input := st.chat_input("Your message"):
        # Immediately show user message and set processing state
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )
        st.session_state.processing = True
        st.rerun()

    # Process any pending input
    if st.session_state.processing and st.session_state.chat_history:

        run_stage(st.session_state.stage, st.session_state.graph_state)
        st.session_state.processing = False
        st.rerun()
        # last_message = st.session_state.chat_history[-1]
        # if last_message["role"] == "user":
        #     # Process the most recent user message
        #     stream_user_input(last_message["content"])
        #     st.session_state.processing = False
        #     st.rerun()

    render_display()

def render_display():
    state = st.session_state.graph_state
    # Determine stage based on 'do_profiling'
    if state.get("do_profiling") is True:
        st.markdown("### 🔍 Profiling Stage")
        st.write(
            "Your profile is being created and the more information you provide, the better job recommendations you will receive. Please answer the questions in the chat to help us understand your interests, skills, and preferences."
        )
        st.write(
            "If you think you've provided enough information, you can click the button below to proceed to job recommendations."
        )

    if state.get("do_profiling") is False:
        st.markdown("### Profile Complete!")

        st.write(
            "You have completed your profile. You can now proceed to get personalized job recommendations based on your interests, skills, and preferences."
        )

    if st.button(
        "Proceed to Job Recommendations", type="primary", use_container_width=True
    ):
        st.session_state.stage = Stage.JOB_RECOMMENDATION
        st.rerun()

def render_right_sidebar():
    st.markdown("#### 📋 Profile Information")

    field_display = {
        "age": "👤 Age",
        "interests": "🎯 Interests",
        "competencies": "💪 Competencies",
        "personal_characteristics": "🧠 Personal Characteristics",
        "job_characteristics": "💼 Job Preferences",
        "is_locally_focused": "📍 Location Focus",
    }

    check_keys = [field for field in field_display.keys() if field not in ProfileInformation.model_fields.keys()]

    if check_keys:
        raise ValueError(f"ProfileInformation model is missing fields: {', '.join(check_keys)}")
    profile_lines = []

    profile_information = st.session_state.graph_state.get("profile_information")

    if profile_information:
        for field, label in field_display.items():
            val = st.session_state.graph_state.get("profile_information").get(field)

            # Format the value for display
            if val is None:
                formatted_val = "*Not set*"
                profile_lines.append(f"**{label}:** *Not set*")
            elif isinstance(val, list):
                if val:
                    formatted_val = ", ".join(str(item) for item in val)
                    profile_lines.append(f"**{label}:** {formatted_val}")
                else:
                    profile_lines.append(f"**{label}:** *Not set*")
            elif isinstance(val, bool):
                formatted_val = "Yes" if val else "No"
                profile_lines.append(f"**{label}:** {formatted_val}")
            elif val == "":
                profile_lines.append(f"**{label}:** *Not set*")
            else:
                profile_lines.append(f"**{label}:** {str(val)}")
        st.markdown("\n\n".join(profile_lines))

        # Profile completeness indicator
        filled_fields = sum(1 for val in profile_information.values() if val)
        progress = filled_fields / len(field_display)

        st.divider()
        st.metric(
            "Profile Completeness",
            f"{progress:.1%}",
            f"{filled_fields}/{len(field_display)} fields",
        )
        st.progress(progress)

        # Show pending questions if any
        if st.session_state.pending_questions:
            st.divider()
            st.markdown("**Next Questions:**")
            for i, q in enumerate(st.session_state.pending_questions[:3], 1):
                st.write(f"{i}. {q}")
            if len(st.session_state.pending_questions) > 3:
                st.write(f"... and {len(st.session_state.pending_questions) - 3} more")


def render_profile_view(main_col, right_col):
    with main_col:
        render_main_column()

    with right_col:
        render_right_sidebar()

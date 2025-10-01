"""Helper functions for the Streamlit app."""

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agent.graph import graph
import os
from dotenv import load_dotenv
from stages import Stage


def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()


def init_state():
    """Initialize session state variables."""
    if "graph_state" not in st.session_state:
        # Minimal overall state
        st.session_state.graph_state = {"messages": [], "do_profiling": True}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "stage" not in st.session_state:
        st.session_state.stage = Stage.PROFILING
    if "pending_questions" not in st.session_state:
        st.session_state.pending_questions = []
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "app_started" not in st.session_state:
        st.session_state.app_started = False
    if "intro_shown" not in st.session_state:
        st.session_state.intro_shown = False


def add_profiling_intro():
    """Add intro message for profiling stage if not already shown."""
    if (
        not st.session_state.intro_shown
        and st.session_state.stage == Stage.PROFILING
        and st.session_state.app_started
    ):
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


def check_api_key():
    """Check if OpenAI API key is available in .env file, fail if not."""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("🚨 OpenAI API Key Not Found")
        st.markdown("""
        **Setup Required:**
        
        1. Create a `.env` file in your project root directory
        2. Add your OpenAI API key to the file:
        ```
        OPENAI_API_KEY=sk-your-actual-key-here
        ```
        3. Restart the Streamlit app
        
        **Note:** Make sure to add `.env` to your `.gitignore` file to keep your API key secure.
        """)
        st.stop()  # Stop execution completely


def stream_user_input(user_input: str):
    """Send user input through the langgraph and update session state."""
    state = st.session_state.graph_state

    # Convert existing dict messages to LangChain message objects for compatibility
    normalized_messages = []
    for m in state.get("messages", []):
        if isinstance(m, (HumanMessage, AIMessage)):
            normalized_messages.append(m)
        else:
            role = m.get("role") if isinstance(m, dict) else None
            content = m.get("content") if isinstance(m, dict) else str(m)
            if role == "user":
                normalized_messages.append(HumanMessage(content=content))
            else:
                normalized_messages.append(AIMessage(content=content))
    state["messages"] = normalized_messages + [HumanMessage(content=user_input)]

    for event in graph.stream(state):
        for node_name, value in event.items():
            # Merge new values into state
            for k, v in value.items():
                if k == "messages" and v:
                    # Append only new messages
                    state.setdefault("messages", []).extend(v)
                else:
                    state[k] = v

            # Track profile questions if produced
            if value.get("profile_questions"):
                st.session_state.pending_questions = value["profile_questions"]

    # Update chat history for display (convert to simple role/content)
    # Preserve any intro messages that aren't in the graph state
    intro_messages = []
    for msg in st.session_state.chat_history:
        if msg.get(
            "role"
        ) == "assistant" and "Welcome to the Profiling Stage" in msg.get("content", ""):
            intro_messages.append(msg)

    # Rebuild chat history from graph state
    new_chat_history = intro_messages.copy()  # Start with preserved intro messages
    for msg in state.get("messages", []):
        if isinstance(msg, HumanMessage):
            new_chat_history.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            new_chat_history.append({"role": "assistant", "content": msg.content})

    # Update session state chat history
    st.session_state.chat_history = new_chat_history
    st.session_state.graph_state = state


def stage_header():
    """Display the current stage header."""
    # Add intro message for profiling stage if needed
    add_profiling_intro()

    if st.session_state.stage == Stage.PROFILING:
        st.markdown("### 🔍 Profiling Stage")
    elif st.session_state.stage == Stage.JOB_RECOMMENDATION:
        st.markdown("### 💼 Job Recommendation Stage")
    elif st.session_state.stage == Stage.JOB_RESEARCH:
        st.markdown("### 🔬 Job Research Stage")

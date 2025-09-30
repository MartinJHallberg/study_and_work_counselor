import streamlit as st
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from agent.graph import graph
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="Study & Work Counselor", page_icon="🎓", layout="wide")

# --- Helper functions ---

def init_state():
    if "graph_state" not in st.session_state:
        # Minimal overall state
        st.session_state.graph_state = {"messages": [], "do_profiling": True}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "stage" not in st.session_state:
        st.session_state.stage = "profiling"  # or 'recommendation'
    if "pending_questions" not in st.session_state:
        st.session_state.pending_questions = []


def check_api_key():
    """Check if OpenAI API key is available in .env file, fail if not."""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("� OpenAI API Key Not Found")
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

            # Determine stage based on 'do_profiling'
            if state.get("do_profiling") is False:
                st.session_state.stage = "job_recommendation"

    # Update chat history for display (convert to simple role/content)
    st.session_state.chat_history = []
    for msg in state.get("messages", []):
        if isinstance(msg, HumanMessage):
            st.session_state.chat_history.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            st.session_state.chat_history.append({"role": "assistant", "content": msg.content})

    st.session_state.graph_state = state


def stage_header():
    if st.session_state.stage == "profiling":
        st.markdown("### Profiling Stage")
        st.write("We're collecting and refining profile details. Answer follow-up questions or provide more info.")
    else:
        st.markdown("### Job Recommendation Stage")
        st.write("Profile complete. Reviewing and generating job recommendations.")


def sidebar_controls():
    with st.sidebar:
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
        st.subheader("Profile Snapshot")
        snapshot_fields = [
            "age",
            "interests",
            "competencies",
            "personal_characteristics",
            "job_characteristics",
            "is_locally_focused",
        ]
        for f in snapshot_fields:
            val = st.session_state.graph_state.get(f)
            if val:
                st.write(f"**{f.replace('_', ' ').title()}**: {val}")

        if st.session_state.pending_questions:
            st.divider()
            st.subheader("Pending Questions")
            for q in st.session_state.pending_questions:
                st.write("- " + q)

        st.divider()
        if st.button("Reset Conversation"):
            for key in ["graph_state", "chat_history", "stage", "pending_questions"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()


# --- App Layout ---
init_state()
check_api_key()  # Must have API key before proceeding
sidebar_controls()
st.title("🎓 Study & Work Counselor")
stage_header()

chat_container = st.container()

# Display existing chat
with chat_container:
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])

# Chat input
if user_input := st.chat_input("Your message"):
    stream_user_input(user_input)
    st.rerun()

# Recommendations summary if available
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

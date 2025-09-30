"""Helper functions for the Streamlit app."""
import streamlit as st
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from agent.graph import graph
import os
from dotenv import load_dotenv


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
        st.session_state.stage = "profiling"  # or 'recommendation'
    if "pending_questions" not in st.session_state:
        st.session_state.pending_questions = []
    if "processing" not in st.session_state:
        st.session_state.processing = False


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

            # Determine stage based on 'do_profiling'
            if state.get("do_profiling") is False:
                st.session_state.stage = "job_recommendation"

    # Update chat history for display (convert to simple role/content)
    # Don't clear existing chat_history since user message was already added
    # Only rebuild if we don't have the current user message
    current_chat_length = len(st.session_state.chat_history)
    
    # Rebuild chat history from graph state
    new_chat_history = []
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
    if st.session_state.stage == "profiling":
        st.markdown("### Profiling Stage")
        st.write("We're collecting and refining profile details. Answer follow-up questions or provide more info.")
    else:
        st.markdown("### Job Recommendation Stage")
        st.write("Profile complete. Reviewing and generating job recommendations.")
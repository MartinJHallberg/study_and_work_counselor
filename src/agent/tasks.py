from agent.state import (
    OverallState,
    ProfilingState,
    JobRecommendationState,
    ResearchState,
)
from agent.models import (
    ProfileInformation,
    ProfileQuestions,
    JobRecommendations,
    ResearchQuery
)
from langchain_openai import ChatOpenAI
from agent.prompts import (
    PROFILE_INFORMATION_PROMPT,
    FOLLOW_UP_QUESTION_PROMPT,
    JOB_RECOMMENDATIONS_PROMPT,
    RESEARCH_QUERY_PROMPT,
)
from langchain_core.messages import AIMessage
from config import NUMBER_OF_JOB_RECOMMENDATIONS


def get_llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)

def get_conversation_history(state: OverallState) -> str:
    messages = state["messages"]

    # Extract and format user messages
    user_messages = []
    for msg in messages:
        if hasattr(msg, "content"):
            if msg.__class__.__name__ == "HumanMessage":
                user_messages.append(f"User: {msg.content}")
            elif msg.__class__.__name__ == "AIMessage":
                user_messages.append(f"Assistant: {msg.content}")
        else:
            # Handle string messages (from initial state)
            user_messages.append(f"User: {str(msg)}")

    return "\n".join(user_messages) if user_messages else "No previous conversation"


def extract_profile_information(state: OverallState) -> ProfilingState:
    # Extract and format user messages
    user_input_text = get_conversation_history(state)
    current_profile_info = state.get("profile_data", None)

    llm = get_llm()  # Get LLM when needed
    structured_llm = llm.with_structured_output(ProfileInformation)
    formatted_prompt = PROFILE_INFORMATION_PROMPT.format(
        user_input=user_input_text,
        current_profile_information=current_profile_info,
    )
    structured_response = structured_llm.invoke(formatted_prompt)

    # Check if profile is complete by verifying no null values
    profile_dict = structured_response.model_dump()
    if any(value is None for value in profile_dict.values()):
        has_null_values = True
        message = "Profile information is incomplete, further questions are needed. Generating questions..."
    else:
        has_null_values = False
        message = "Profile information extracted successfully."

    # Update the structured response with completeness check
    profile_dict["is_profile_complete"] = not has_null_values

    return {
        "messages": [AIMessage(content=message)],
        "profile_data": profile_dict,
    }


def ask_profile_questions(state: ProfilingState) -> OverallState:
    llm = get_llm()  # Get LLM when needed
    structured_llm = llm.with_structured_output(ProfileQuestions)
    current_profile_info = state.get("profile_data", None)

    formatted_prompt = FOLLOW_UP_QUESTION_PROMPT.format(
        current_profile_information=current_profile_info,
    )

    structured_response = structured_llm.invoke(formatted_prompt)

    return {
        "messages": [AIMessage(content=structured_response.message)],
        "profile_questions": structured_response.questions,
    }


def get_job_recommendations(state: OverallState, number_of_recommendations: int=NUMBER_OF_JOB_RECOMMENDATIONS) -> JobRecommendationState:
    llm = get_llm()
    structured_llm = llm.with_structured_output(JobRecommendations)
    current_profile_info = state.get("profile_data", None)

    formatted_prompt = JOB_RECOMMENDATIONS_PROMPT.format(
        number_of_recommendations=number_of_recommendations,
        current_profile_information=current_profile_info,
    )
    structured_response = structured_llm.invoke(formatted_prompt)

    return {
        "messages": [AIMessage(content=structured_response.summary)],
        "job_recommendations_data": structured_response.model_dump(),
    }

def get_research_query(state: OverallState) -> ResearchState:
    llm = get_llm()
    structured_llm = llm.with_structured_output(ResearchQuery)

    formatted_prompt = RESEARCH_QUERY_PROMPT.format(
        job_role=state.get("job_role", []),
        job_role_description=state.get("job_role_description", [])
    )
    structured_response = structured_llm.invoke(formatted_prompt)

    return {
        "messages": [AIMessage(content="I've created a research plan. Let me start investigating...")],
        "research_query": structured_response.research_query,
    }
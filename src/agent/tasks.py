from agent.state import OverallState, ProfilingState
from typing import List

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from agent.prompts import PROFILE_INFORMATION_PROMPT, FOLLOW_UP_QUESTION_PROMPT
from langchain_core.messages import AIMessage


def get_llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


class ProfileStateModel(BaseModel):
    pass

    def get_attribute_with_values(self) -> str:
        """
        Generate a formatted string representation of the profile information
        that can be used as input to a prompt.

        Returns:
            str: A formatted string containing all profile attributes and their values
        """
        lines = []

        for field_name, field_info in self.__class__.model_fields.items():
            value = getattr(self, field_name)

            # Format the field name to be more human-readable
            display_name = field_name.replace("_", " ").title()

            if isinstance(value, list):
                if value:
                    formatted_value = ", ".join(str(item) for item in value)
                else:
                    formatted_value = None
            else:
                formatted_value = str(value)

            lines.append(f"{display_name}: {formatted_value}")

        return "\n".join(lines)

    def get_field_descriptions(self) -> str:
        """
        Generate a simple field name and description list.

        Returns:
            str: A formatted string with field names and descriptions
        """
        lines = []

        for field_name, field_info in self.__class__.model_fields.items():
            lines.append(f'- "{field_name}": {field_info.description}')

        return "\n".join(lines)


class ProfileInformation(ProfileStateModel):
    age: int | None = Field(default=None, description="The age of the user")
    interests: List[str] | None = Field(
        default=None, description="The interests of the user"
    )
    competencies: List[str] | None = Field(
        default=None, description="The competencies of the user"
    )
    personal_characteristics: List[str] | None = Field(
        default=None, description="The personal characteristics of the user"
    )
    is_locally_focused: bool | None = Field(
        default=None, description="Whether the user is focused on local opportunities"
    )
    desired_job_characteristics: List[str] | None = Field(
        default=None, description="The job characteristics the user is looking for"
    )
    is_profile_complete: bool | None = Field(
        description="Whether the profile is complete"
    )


class ProfileQuestions(ProfileStateModel):
    answer: str = Field(
        description="A helpful answer to the user's input based on their profile"
    )
    questions: List[str] | None = Field(
        default=None, description="Follow-up questions to clarify the user's profile"
    )


def get_current_profile_information(state: OverallState) -> ProfileInformation:
    return ProfileInformation(
        age=state.get("age"),  # Default to 0 if not present
        interests=state.get("interests", []),
        competencies=state.get("competencies", []),
        personal_characteristics=state.get("personal_characteristics", []),
        is_locally_focused=state.get("is_locally_focused"),
        job_characteristics=state.get("job_characteristics", []),
        is_profile_complete=state.get("is_profile_complete"),
    )


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
    current_profile_info = get_current_profile_information(state)

    # 1. Get structured output for profile extraction
    llm = get_llm()  # Get LLM when needed
    structured_llm = llm.with_structured_output(ProfileInformation)
    formatted_prompt = PROFILE_INFORMATION_PROMPT.format(
        fields=current_profile_info.get_field_descriptions(),
        user_input=user_input_text,
        current_profile_information=current_profile_info.get_attribute_with_values(),
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
    structured_response.is_profile_complete = not has_null_values

    return {
        "messages": [AIMessage(content=message)],
        "age": structured_response.age,
        "interests": structured_response.interests,
        "competencies": structured_response.competencies,
        "personal_characteristics": structured_response.personal_characteristics,
        "job_characteristics": structured_response.desired_job_characteristics,
        "is_locally_focused": structured_response.is_locally_focused,
        "do_profiling": not structured_response.is_profile_complete,
    }


def ask_profile_questions(state: ProfilingState) -> OverallState:
    llm = get_llm()  # Get LLM when needed
    structured_llm = llm.with_structured_output(ProfileQuestions)
    current_profile_info = get_current_profile_information(state)

    formatted_prompt = FOLLOW_UP_QUESTION_PROMPT.format(
        fields=current_profile_info.get_field_descriptions(),
        current_profile_information=current_profile_info.get_attribute_with_values(),
    )

    structured_response = structured_llm.invoke(formatted_prompt)

    return {
        "messages": [AIMessage(content=structured_response.answer)],
        "profile_questions": structured_response.questions,
    }

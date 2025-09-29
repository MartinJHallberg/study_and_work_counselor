from agent.state import (
    OverallState,
    ProfileState
)
from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

config = RunnableConfig(max_retries=3, retry_delay=2, stop=["\n\n"])


class ProfileInformation(BaseModel):
    age: int = Field(description="The age of the user")
    interests: List[str] = Field(description="The interests of the user")
    competencies: List[str] = Field(description="The competencies of the user")
    personal_characteristics: List[str] = Field(description="The personal characteristics of the user")
    is_locally_focused: bool = Field(description="Whether the user is focused on local opportunities")
    desired_job_characteristics: List[str] = Field(description="The job characteristics the user is looking for")

    def to_prompt_string(self) -> str:
        """
        Generate a formatted string representation of the profile information
        that can be used as input to a prompt.
        
        Returns:
            str: A formatted string containing all profile attributes and their values
        """
        lines = []
        
        for field_name, field_info in self.model_fields.items():
            value = getattr(self, field_name)
            description = field_info.description or field_name.replace('_', ' ').title()
            
            # Format the field name to be more human-readable
            display_name = field_name.replace('_', ' ').title()
            
            # Format the value based on its type
            if isinstance(value, bool):
                formatted_value = "Yes" if value else "No"
            elif isinstance(value, list):
                if value:
                    formatted_value = ", ".join(str(item) for item in value)
                else:
                    formatted_value = "None specified"
            else:
                formatted_value = str(value)
            
            lines.append(f"{display_name}: {formatted_value}")
        
        return "\n".join(lines)


def get_current_profile_information(state: OverallState) -> ProfileInformation:
    return ProfileInformation(
        age=state["age"],
        interests=state["interests"],
        competencies=state["competencies"],
        personal_characteristics=state["personal_characteristics"],
        is_locally_focused=state["is_locally_focused"],
        job_characteristics=state["job_characteristics"]
    )
    


def add_profile_information(state: OverallState) -> ProfileState:
    messages = state["messages"]
    last_messages = state["messages"][-1]

    current_profile_info = get_current_profile_information(state)



if __name__ == "__main__":
    

    profile = ProfileInformation(
        age=30,
        interests=["reading", "traveling"],
        competencies=["Python", "Data Analysis"],
        personal_characteristics=["curious", "adaptable"],
        is_locally_focused=True,
        desired_job_characteristics=["remote work", "flexible hours"]
    )

    a = 10
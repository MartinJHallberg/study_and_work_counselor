from pydantic import BaseModel, Field
from typing import List
from enum import StrEnum


class StateModel(BaseModel):
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


class ProfileInformation(StateModel):
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


class ProfileQuestions(StateModel):
    message: str | None = Field(
        description="A helpful message to summarise what information that is missing from the profile"
    )
    questions: List[str] | None = Field(
        default=None, description="Follow-up questions to clarify the user's profile"
    )

class Job(BaseModel):
    name: str = Field(description="A recommended job role that matches the user's profile")
    description: str = Field(description="A brief description of the recommended job role")

class JobRecommendationData(StateModel):
    job : Job = Field(
        description="A recommended job role that matches the user's profile"
    )

    education: List[str] | None = Field(
        default=None,
        description="A list of educational paths or qualifications beneficial for the recommended job role"
    )
    profile_match: str | None = Field(
        default=None,
        description="A list of profile attributes that make the user a good match for the recommended job role"
    )

class JobRecommendations(StateModel):
    job_recommendations: List[JobRecommendationData] = Field(
        description="A list of job recommendations based on the user's profile"
    )
    summary: str | None = Field(
        description="A summary of the personal profile and how it relates to the recommended job roles"
    )

class ResearchQuery(StateModel):
    research_query: List[str] | None = Field(
        description="A list of research queries based on the job recommendations"
    )


class JobResearchStatus(StrEnum):
    NOT_STARTED = "Not started"
    INITIALIZED = "Initialized"
    RESEARCH_QUERY_GENERATED = "Research query generated"
    RESEARCH_IN_PROGRESS = "Research in progress"
    EVALUATION_IN_PROGRESS = "Evaluation in progress"
    COMPLETED = "completed"

class JobResearchData(StateModel):
    job: Job | None = Field(
        default=None,
        description="The job role being researched"
    )

    research_query: ResearchQuery | None = Field(
        default=None,
        description="A research query based on the job recommendation"
    )

    research_status: JobResearchStatus = Field(
        default=JobResearchStatus.NOT_STARTED,
        description="The status of the research"
    )
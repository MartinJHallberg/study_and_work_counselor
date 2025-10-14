from pydantic import BaseModel, Field
from typing import List
from enum import StrEnum
import uuid


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
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique job identifier")
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
        description="Explanation of why this job matches the user's profile"
    )

class JobRecommendations(StateModel):
    job_recommendations: List[JobRecommendationData] = Field(
        description="A list of job recommendations based on the user's profile"
    )
    summary: str | None = Field(
        description="A summary of the personal profile and how it relates to the recommended job roles"
    )

class ResearchQueries(StateModel):
    queries: List[str] = Field(
        description="A list of research queries based on the job recommendations"
    )


class JobResearchStatus(StrEnum):
    NOT_STARTED = "Not started"
    INITIALIZED = "Initialized"
    RESEARCH_QUERY_GENERATED = "Research query generated"
    RESEARCH_RESULTS_GATHERED = "Research results gathered"
    ANALYSIS_COMPLETED = "Analysis completed"
    COMPLETED = "completed"
    FAILED = "Failed"

class JobResearchData(StateModel):

    query: str | None = Field(
        default=None,
        description="A research query based on the job recommendations"
    )
    results: List[str] | None = Field(
        default=None,
        description="A list of research results obtained from the research query"
    )
    sources: List[str] | None = Field(
        default=None,
        description="A list of sources for the research results"
    )




class JobResearch(StateModel):
    job: Job = Field(
        description="The job role being researched"
    )

    research_data: List[JobResearchData] | None = Field(
        default=None,
        description="A list of research data entries related to the job"
    )

    research_status: JobResearchStatus = Field(
        default=JobResearchStatus.NOT_STARTED,
        description="The status of the research"
    )

    @property
    def job_id(self) -> str:
        return self.job.job_id
from pydantic import BaseModel, Field
from typing import List

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
    answer: str | None = Field(
        description="A helpful answer to the user's input based on their profile"
    )
    questions: List[str] | None = Field(
        default=None, description="Follow-up questions to clarify the user's profile"
    )

class JobRecommendations(StateModel):
    job_role: List[str] | None = Field(
        description="A list of recommended job roles that match the user's profile"
    )
    job_role_description: List[str] | None = Field(
        description="A brief description of each recommended job role"
    )
    education: List[str] | None = Field(
        description="A list of educational paths or qualifications beneficial for each recommended job role"
    )
    profile_match: List[str] = Field(
        description="An explanation of why each job role is a good match for the user's profile"
    )
    summary: str | None = Field(
        description="A summary of the job recommendations provided and the characteristics of the profile"
    )
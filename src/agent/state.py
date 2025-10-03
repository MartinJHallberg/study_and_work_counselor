from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
import operator


class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    profile_data: dict | None  # Store as dict for serialization
    job_recommendations_data: dict | None  # Store as dict for serialization
    research_query_data: dict | None  # Store as dict for serialization


class ProfilingState(TypedDict):
    messages: Annotated[list, add_messages]
    age: int | None
    interests: Annotated[list, operator.add] | None
    competencies: Annotated[list, operator.add] | None
    personal_characteristics: Annotated[list, operator.add] | None
    is_locally_focused: bool | None
    desired_job_characteristics: Annotated[list, operator.add] | None
    do_profiling: bool  # Fixed typo: was "do_priofiling"


class JobRecommendationState(TypedDict):
    messages: Annotated[list, add_messages]
    job_role: list[str] | None
    job_role_description: list[str] | None
    education: list[str] | None
    profile_match: list[str] | None

class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    research_query: list[str] | None
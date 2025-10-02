from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
import operator


class OverallState(TypedDict):
    # Always present from the start
    messages: Annotated[list, add_messages]
    do_profiling: bool

    # Fields that will be populated during profiling - make them optional
    interests: Annotated[list, operator.add] | None
    competencies: Annotated[list, operator.add] | None
    personal_characteristics: Annotated[list, operator.add] | None
    job_characteristics: Annotated[list, operator.add] | None
    profile_questions: Annotated[list, operator.add] | None
    age: int | None
    is_locally_focused: bool | None

    # Fields that will be populated during job recommendation - make them optional
    job_role: list[str] | None
    job_role_description: list[str] | None
    education: list[str] | None
    profile_match: list[str] | None


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
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
import operator

class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    age: int
    interests: Annotated[list, operator.add]
    competencies: Annotated[list, operator.add]
    personal_characteristics: Annotated[list, operator.add]
    is_locally_focused: bool
    job_characteristics: Annotated[list, operator.add]


class ProfileState(TypedDict):
    messages: Annotated[list, add_messages]
    age: int
    interests: Annotated[list, operator.add]
    competencies: Annotated[list, operator.add]
    personal_characteristics: Annotated[list, operator.add]
    is_locally_focused: bool
    desired_job_characteristics: Annotated[list, operator.add]

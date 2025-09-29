from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
import operator

class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    interests: Annotated[list, operator.add]
    competencies: Annotated[list, operator.add]
    personal_characteristics: Annotated[list, operator.add]
    job_characteristics: Annotated[list, operator.add]
    age: int
    is_locally_focused: bool
    profile_questions: Annotated[list, operator.add]
    do_profiling: bool



class ProfilingState(TypedDict):
    messages: Annotated[list, add_messages]
    age: int
    interests: Annotated[list, operator.add]
    competencies: Annotated[list, operator.add]
    personal_characteristics: Annotated[list, operator.add]
    is_locally_focused: bool
    desired_job_characteristics: Annotated[list, operator.add]
    do_priofiling: bool


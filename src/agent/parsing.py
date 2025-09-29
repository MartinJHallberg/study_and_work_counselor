from langgraph.graph import START, END
from agent.tasks import extract_profile_information
from langgraph.graph import StateGraph
from agent.state import OverallState

builder = StateGraph(OverallState)

builder = builder.add_node(
    "extract_profile_information",
    extract_profile_information
)

builder = builder.add_edge(START, "extract_profile_information")
builder = builder.add_edge("extract_profile_information", END)

graph = builder.compile()


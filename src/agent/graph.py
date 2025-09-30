from langgraph.graph import START, END
from agent.tasks import (
    extract_profile_information,
    ask_profile_questions,
    get_job_recommendations,
)
from langgraph.graph import StateGraph
from agent.state import OverallState

builder = StateGraph(OverallState)

builder.add_node("extract_profile_information", extract_profile_information)
builder.add_node("ask_profile_questions", ask_profile_questions)
builder.add_node("get_job_recommendations", get_job_recommendations)

builder.add_edge(START, "extract_profile_information")
builder.add_conditional_edges(
    "extract_profile_information",
    lambda state: state.get("do_profiling", True),
    {True: "ask_profile_questions", False: "get_job_recommendations"},
)

builder.add_edge("get_job_recommendations", END)

graph = builder.compile()

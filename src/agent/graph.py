from langgraph.graph import START, END
from agent.tasks import (
    extract_profile_information,
    ask_profile_questions,
    get_job_recommendations,
    start_job_research,
    get_research_query,
    conduct_research,
    analyze_research,
)
from langgraph.graph import StateGraph
from agent.state import OverallState
from models import Stage
from langgraph.checkpoint.base import BaseCheckpointSaver


def next_stage(state):
    stage = state["stage"]
    return {
        Stage.PROFILING: Stage.ASK_PROFILE if state.get("missing_fields") else Stage.RECOMMEND,
        Stage.ASK_PROFILE: Stage.RECOMMEND,
        Stage.RECOMMEND: Stage.RESEARCH,
        Stage.RESEARCH: END,
    }.get(stage, END)


def continue_research(state: OverallState) -> bool:
    return state.get("research_queue") is not None and len(state["research_queue"]) > 0


# Get research subgraph
def create_research_graph(checkpointer: BaseCheckpointSaver = None) -> StateGraph:
    research_builder = StateGraph(OverallState)

    research_builder.add_node("start_job_research", start_job_research)
    research_builder.add_node("get_research_query", get_research_query)
    research_builder.add_node("conduct_research", conduct_research)
    research_builder.add_node("analyze_research", analyze_research)

    # Define the research flow
    research_builder.add_edge(START, "start_job_research")
    research_builder.add_edge("start_job_research", "get_research_query")
    research_builder.add_edge("get_research_query", "conduct_research")
    research_builder.add_edge("conduct_research", "analyze_research")
    research_builder.add_conditional_edges(
        "analyze_research",
        continue_research,
        {True: "start_job_research", False: END},
    )

    if checkpointer:
        return research_builder.compile(checkpointer=checkpointer)
    else:
        return research_builder.compile()
    
def get_profiling_graph():
    builder = StateGraph(OverallState)

    # Create nodes
    builder.add_node("extract_profile_information", extract_profile_information)
    builder.add_node("ask_profile_questions", ask_profile_questions)
    builder.add_node("get_job_recommendations", get_job_recommendations)

    # Define the profiling flow
    builder.add_edge(START, "extract_profile_information")
    builder.add_conditional_edges(
        "extract_profile_information",
        lambda state: state.get("is_profile_complete", False),
        {False: "ask_profile_questions", True: END},
    )

    return builder.compile()

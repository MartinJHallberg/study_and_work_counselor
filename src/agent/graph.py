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

from langgraph.graph import StateGraph
from agent.state import OverallState
from langgraph.checkpoint.base import BaseCheckpointSaver


# Get research subgraph
def create_research_graph(checkpointer: BaseCheckpointSaver=None) -> StateGraph:
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
    research_builder.add_edge("analyze_research", END)

    if checkpointer:
        return research_builder.compile(checkpointer=checkpointer)
    else:
        return research_builder.compile()


def create_main_graph(checkpointer: BaseCheckpointSaver = None):
    """Create the main application graph."""
    builder = StateGraph(OverallState)

    # Create nodes
    builder.add_node("extract_profile_information", extract_profile_information)
    builder.add_node("ask_profile_questions", ask_profile_questions)
    builder.add_node("get_job_recommendations", get_job_recommendations)

    # Add research subgraph
    research_subgraph = create_research_graph(checkpointer=checkpointer)
    builder.add_node("research_workflow", research_subgraph)

    # Define the overall flow
    builder.add_edge(START, "extract_profile_information")
    builder.add_conditional_edges(
        "extract_profile_information",
        lambda state: state.get("do_profiling", True),
        {True: "ask_profile_questions", False: "get_job_recommendations"},
    )

    builder.add_edge("get_job_recommendations", "research_workflow")
    builder.add_edge("research_workflow", END)

    if checkpointer:
        return builder.compile(checkpointer=checkpointer)
    else:
        return builder.compile()


# Default graph for production (no checkpointer)
graph = create_main_graph()

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
from agent.models import MainNode, SubNode
from langgraph.checkpoint.base import BaseCheckpointSaver


def continue_research(state: OverallState) -> bool:
    return state.get("research_queue") is not None and len(state["research_queue"]) > 0


def create_profiling_graph():
    builder = StateGraph(OverallState)

    # Create nodes
    builder.add_node(SubNode.EXTRACT_PROFILE_INFORMATION, extract_profile_information)
    builder.add_node(SubNode.ASK_PROFILE_QUESTIONS, ask_profile_questions)

    # Define the profiling flow
    builder.add_edge(START, SubNode.EXTRACT_PROFILE_INFORMATION)
    builder.add_edge(
        SubNode.EXTRACT_PROFILE_INFORMATION, SubNode.ASK_PROFILE_QUESTIONS
    )

    return builder.compile()

# Get research subgraph
def create_research_graph(checkpointer: BaseCheckpointSaver = None) -> StateGraph:
    research_builder = StateGraph(OverallState)

    research_builder.add_node(SubNode.START_JOB_RESEARCH, start_job_research)
    research_builder.add_node(SubNode.GET_RESEARCH_QUERY, get_research_query)
    research_builder.add_node(SubNode.CONDUCT_RESEARCH, conduct_research)
    research_builder.add_node(SubNode.ANALYZE_RESEARCH, analyze_research)

    # Define the research flow
    research_builder.add_edge(START, SubNode.START_JOB_RESEARCH)
    research_builder.add_edge(SubNode.START_JOB_RESEARCH, SubNode.GET_RESEARCH_QUERY)
    research_builder.add_edge(SubNode.GET_RESEARCH_QUERY, SubNode.CONDUCT_RESEARCH)
    research_builder.add_edge(SubNode.CONDUCT_RESEARCH, SubNode.ANALYZE_RESEARCH)
    research_builder.add_conditional_edges(
        SubNode.ANALYZE_RESEARCH,
        continue_research,
        {True: SubNode.START_JOB_RESEARCH, False: END},
    )

    if checkpointer:
        return research_builder.compile(checkpointer=checkpointer)
    else:
        return research_builder.compile()
    


def create_main_graph(checkpointer: BaseCheckpointSaver = None):
    """Create the main application graph."""
    builder = StateGraph(OverallState)

    # Create nodes
    builder.add_node(MainNode.PROFILING, create_profiling_graph())
    builder.add_node(MainNode.JOB_RECOMMENDATION, get_job_recommendations)
    builder.add_node(MainNode.JOB_RESEARCH, create_research_graph(checkpointer=checkpointer))

    # Define the overall flow
    builder.add_edge(START, MainNode.PROFILING)
    builder.add_edge(MainNode.PROFILING, MainNode.JOB_RECOMMENDATION)
    builder.add_edge(MainNode.JOB_RECOMMENDATION, MainNode.JOB_RESEARCH)
    builder.add_edge(MainNode.JOB_RESEARCH, END)

    if checkpointer:
        return builder.compile(checkpointer=checkpointer)
    else:
        return builder.compile()
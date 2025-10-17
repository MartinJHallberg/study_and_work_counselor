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
from config import config
from langchain_core.runnables import RunnableConfig

builder = StateGraph(OverallState)

from langgraph.graph import StateGraph
from agent.state import OverallState

# Create nodes
builder.add_node("extract_profile_information", extract_profile_information)
builder.add_node("ask_profile_questions", ask_profile_questions)
builder.add_node("get_job_recommendations", get_job_recommendations)


# Get research subgraph
def create_research_graph(config: RunnableConfig = config.to_runnable_config) -> StateGraph:
    research_builder = StateGraph(OverallState)

    research_builder.add_node("start_job_research", start_job_research)
    research_builder.add_node("get_research_query",
                              lambda state: get_research_query(
                                  state,
                                  config
                                  )
                                )
    research_builder.add_node("conduct_research",
                              lambda state: conduct_research(
                                  state,
                                  config
                                  )
                              )

    research_builder.add_node("analyze_research", analyze_research)

    # Define the research flow
    research_builder.add_edge(START, "start_job_research")
    research_builder.add_edge("start_job_research", "get_research_query")
    research_builder.add_edge("get_research_query", "conduct_research")
    research_builder.add_edge("conduct_research", "analyze_research")
    research_builder.add_edge("analyze_research", END)

    return research_builder.compile()


builder.add_node("research_workflow", create_research_graph())


# Define the overall flow
builder.add_edge(START, "extract_profile_information")
builder.add_conditional_edges(
    "extract_profile_information",
    lambda state: state.get("do_profiling", True),
    {True: "ask_profile_questions", False: "get_job_recommendations"},
)

builder.add_edge("get_job_recommendations", "research_workflow")
builder.add_edge("research_workflow", END)

graph = builder.compile()

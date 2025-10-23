from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from config import config as app_config
from langchain_core.runnables import RunnableConfig


@tool
def web_search(
    query: str,
    config: RunnableConfig,
) -> str:
    """Uses Tavily's official search API."""

    # Extract configuration values with fallback to defaults
    max_results = config["configurable"].get(
        "max_research_results", app_config.max_research_results
    )
    search_depth = config["configurable"].get(
        "research_depth", app_config.research_depth
    )
    include_raw_content = config["configurable"].get(
        "research_include_raw_content", app_config.research_include_raw_content
    )

    # Initialize search with configuration
    search = TavilySearch(
        max_results=max_results,
        search_depth=search_depth,
        include_raw_content=include_raw_content,
    )

    return search.run(query)

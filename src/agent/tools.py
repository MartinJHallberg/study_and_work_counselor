from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from typing import List
from config import config


@tool
def web_search(
    query: str,
    max_results: int = config.tavily_max_search_results,
    search_depth: str = config.tavily_search_depth,
    include_raw_content: bool = config.tavily_include_raw_content,
    ) -> str:
    """Uses Tavily's official search API."""
    search = TavilySearch(
        max_results=max_results,
        search_depth=search_depth,
        include_raw_content=include_raw_content
    )
    return search.run(query)
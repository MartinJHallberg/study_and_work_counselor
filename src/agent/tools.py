from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from typing import List
#from src.config import config


@tool
def web_search(
    query: str,
    max_results: int,
    search_depth: str,
    include_raw_content: bool,
    ) -> str:
    """Uses Tavily's official search API."""
    search = TavilySearch(
        max_results=max_results,
        search_depth=search_depth,
        include_raw_content=include_raw_content
    )
    return search.run(query)
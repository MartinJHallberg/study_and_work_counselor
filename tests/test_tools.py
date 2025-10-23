from agent.tools import (
    web_search,
)


def test_simple_web_search(research_config_for_testing):
    query = "Python programming"
    result = web_search.invoke({"query": query}, config=research_config_for_testing)

    expected = research_config_for_testing["configurable"]["max_research_results"]

    assert len(result["results"]) == expected

from agent.tools import(
    web_search,
)

def test_simple_web_search():
    query = "Python programming"
    result = web_search(
        query,
        max_results=2,
        search_depth="shallow",
        include_raw_content=False)

    assert len(result["results"]) == 2
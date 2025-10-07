from agent.tools import(
    web_search,
)

def test_web_search():
    query = "Python programming"
    result = web_search(query)

    assert len(result) > 0
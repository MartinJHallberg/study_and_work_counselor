from agent.graph import create_research_graph
from agent.state import OverallState



def test_research_workflow(software_developer, test_research_config):
    state = OverallState(
        job_recommendations=[software_developer.model_dump()],
        research_queue=[software_developer.job_id],
    )

    number_of_queries = test_research_config["number_of_queries"]
    max_search_results = test_research_config["max_search_results"]

    research_graph = create_research_graph(
        number_of_queries=number_of_queries
    )

    # Stream the execution to get intermediate results
    results = {}
    for step in research_graph.stream(state):
        results.update(step)

        # Test intermediate states
        if "start_job_research" in step:
            assert (
                step["start_job_research"]["current_job_research"]["job"]["job_id"]
                == software_developer.job_id
            )
            assert step["start_job_research"]["research_queue"] == []

        if "get_research_query" in step:
            assert step["get_research_query"]["current_job_research"]["research_data"][0] is not None

        if "conduct_research" in step:
            job_research = step["conduct_research"]["current_job_research"]
            assert len(job_research["research_data"][0]["results"]) > 0

        if "analyze_research" in step:
            job_research = step["analyze_research"]["current_job_research"]
            assert job_research["research_status"] == "ANALYZED"

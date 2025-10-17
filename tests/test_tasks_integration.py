from agent.graph import create_research_graph
from agent.state import OverallState
from agent.models import JobResearchStatus


def test_research_workflow(software_developer, research_config_for_testing):
    state = OverallState(
        job_recommendations=[software_developer.model_dump()],
        research_queue=[software_developer.job_id],
    )


    research_graph = create_research_graph(
        config=research_config_for_testing
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
            assert step["get_research_query"]["current_job_research"]["research_status"] == JobResearchStatus.RESEARCH_QUERY_GENERATED

        if "conduct_research" in step:
            job_research = step["conduct_research"]["current_job_research"]
            assert job_research["research_status"] == JobResearchStatus.RESEARCH_RESULTS_GATHERED
            assert len(job_research["research_data"][0]["results"]) > 0

        if "analyze_research" in step:
            # Check that the research analysis is completed and correct
            completed_job = step["analyze_research"]["completed_job_research"][0]
            assert completed_job["research_status"] == JobResearchStatus.COMPLETED
            assert completed_job["research_analysis"] is not None
            assert completed_job["job"]["job_id"] == software_developer.job_id

            # Check that the current job research is cleared
            assert step["analyze_research"]["current_job_research"] is None

            # Check that the research queue is empty
            assert step["analyze_research"]["research_queue"] == []

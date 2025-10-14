from agent.models import (
    Job,
    JobResearchStatus,
    JobResearch,
    JobResearchData
)
from agent.tasks import (
    get_job_recommendations,
    extract_profile_information,
    ask_profile_questions,
    get_research_query,
    start_job_research,
    conduct_research
)
from langgraph.graph import StateGraph
from agent.state import OverallState, ProfilingState
import pytest

MINIMAL_PROFILE_MESSAGE = "I like math, I am social and interested in arts."



@pytest.mark.llm_call
def test_extract_profile_information_with_minimal_input():
    state = OverallState(
        messages=[{"role": "user", "content": MINIMAL_PROFILE_MESSAGE}]
    )

    result = extract_profile_information(state)

    assert result["profile_information"]["interests"] is not None
    assert result["profile_information"]["personal_characteristics"] is not None

@pytest.mark.llm_call
def test_extract_profile_information_with_previous_data():

    interests = ["technology", "innovation"]
    state = OverallState(
        messages=[{"role": "user", "content": MINIMAL_PROFILE_MESSAGE}],
        profile_data={
            "age": 18,
            "interests": interests,
            "competencies": ["Math", "History", "Arts"],
            "personal_characteristics": ["analytical", "creative"],
            "is_locally_focused": False,
            "desired_job_characteristics": [
                "small business",
                "creative",
                "innovative",
                "not stressful",
            ],
            "is_profile_complete": False,
        },
    )

    result = extract_profile_information(state)

    assert len(result["profile_information"]["interests"]) > len(interests) # Ensure interests are updated
    assert result["profile_information"]["personal_characteristics"] is not None
    assert result["profile_information"]["age"] == 18  # Ensure age remains unchanged

@pytest.mark.llm_call
def test_ask_profile_questions_with_minimal_input():
    state = OverallState(
        messages=[{"role": "user", "content": MINIMAL_PROFILE_MESSAGE}],
    )

    result = ask_profile_questions(state)

    assert result["messages"] is not None
    assert isinstance(result["profile_questions"], list)
    assert result["profile_questions"], "Questions should not be None"


@pytest.mark.llm_call
def test_get_job_recommendations_with_complete_profile():
    state = OverallState(
        messages=[{"role": "user", "content": MINIMAL_PROFILE_MESSAGE}],
        profile_data={
            "age": 18,
            "interests": ["technology", "innovation"],
            "competencies": ["Math", "History", "Arts"],
            "personal_characteristics": ["analytical", "creative"],
            "desired_job_characteristics": [
                "small business",
                "creative",
                "innovative",
                "not stressful",
            ],
            "is_locally_focused": False,
        },
    )

    result = get_job_recommendations(state, number_of_recommendations=3)

    assert result["messages"] is not None

    for job in result["job_recommendations_data"]:
        for attr_name in job.__dict__:
            attr_value = getattr(job, attr_name)
            assert attr_value is not None, f"Attribute '{attr_name}' should not be None"


@pytest.mark.llm_call
def test_research_query():

    job = Job(
        name="Software Developer",
        description="A Software Developer writes and maintains code for software applications.",
    )

    state = OverallState(
        job_recommendations_data=job.model_dump()
    )

    result = get_research_query(state)

    assert result["research_query"] is not None
    assert isinstance(result["research_query"], list)


@pytest.fixture
def software_developer():
    return Job(
        name="software developer",
        description="A Software Developer writes and maintains code for software applications.",
    )

@pytest.fixture
def data_scientist():
    return Job(
        name="data scientist",
        description="A Data Scientist analyzes and interprets complex data to help companies make decisions.",
    )

@pytest.fixture
def product_manager():
    return Job(
        name="product manager",
        description="A Product Manager oversees the development and delivery of products, ensuring they meet customer needs and business goals.",
    )



@pytest.mark.llm_call
def test_start_job_research(
    software_developer,
    data_scientist,
    product_manager,
):

    jobs = [
        software_developer,
        data_scientist,
        product_manager,
    ]

    jobs = [job.model_dump() for job in jobs]

    selected_jobs = ["software developer", "data scientist"]

    selected_jobs_with_id = {job["name"]: job["job_id"] for job in jobs if job["name"] in selected_jobs}

    selected_job_ids = list(selected_jobs_with_id.values())

    state = OverallState(
        job_recommendations_data=jobs,
        research_queue=selected_job_ids,
    )

    result = start_job_research(state)

    # Update state with research results
    assert result["job_research_data"][0]["job"]["name"] == "software developer"
    assert result["job_research_data"][0]["research_status"] == JobResearchStatus.INITIALIZED

    state.update(result)
    assert isinstance(state["job_research_data"], list)
    assert len(state["job_research_data"]) == 1 # check that one job is in research
    assert state["job_research_data"][0]["job"]["name"] == "software developer"
    assert state["job_research_data"][0]["research_status"] == JobResearchStatus.INITIALIZED
    assert state["current_research_job_id"] == selected_jobs_with_id["software developer"]
    assert state["research_queue"] == [selected_jobs_with_id["data scientist"]]

@pytest.mark.llm_call
def test_conduct_research(
    software_developer,
):
    
    job_research_data = JobResearchData(
        query="What are the main responsibilities of a Software Developer?",
    )
    job_research = JobResearch(
        job=software_developer,
        research_data=[job_research_data],
        research_status=JobResearchStatus.RESEARCH_QUERY_GENERATED
    ).model_dump()

    state = OverallState(
        job_research=[job_research],
        current_research_job_id=software_developer.job_id,
    )

    result = conduct_research(state)

    job_research_result = result["job_research"]

    assert job_research_result["research_status"] == JobResearchStatus.RESEARCH_RESULTS_GATHERED
    assert len(job_research_result["research_data"][0]["results"]) > 0
    assert len(job_research_result["research_data"][0]["sources"]) > 0
    assert job_research_result["research_data"][0]["query"] == "What are the main responsibilities of a Software Developer?"
    assert result["messages"] is not None
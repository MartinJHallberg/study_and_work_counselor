from agent.models import (
    JobResearchStatus,
    JobResearch,
    JobResearchData,
    ProfileInformation,
)
from agent.tasks import (
    get_job_recommendations,
    extract_profile_information,
    ask_profile_questions,
    get_research_query,
    start_job_research,
    conduct_research,
    analyze_research,
)
from agent.state import OverallState
import pytest
from langchain_core.runnables import RunnableConfig

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

    profile_information = ProfileInformation(
        age=18,
        interests=interests,
        competencies=["Math", "History", "Arts"],
        personal_characteristics=["analytical", "creative"],
        is_locally_focused=False,
        desired_job_characteristics=[
            "small business",
            "creative",
            "innovative",
            "not stressful",
        ],
        is_profile_complete=False,
    )

    state = OverallState(
        messages=[{"role": "user", "content": MINIMAL_PROFILE_MESSAGE}],
        profile_information=profile_information.model_dump(),
    )

    result = extract_profile_information(state)

    assert result["profile_information"]["interests"] is not None
    assert result["profile_information"]["personal_characteristics"] is not None


@pytest.mark.llm_call
def test_extract_profile_information_with_previous_data():
    interests = ["technology", "innovation"]

    profile_information = ProfileInformation(
        age=18,
        interests=interests,
        competencies=["Math", "History", "Arts"],
        personal_characteristics=["analytical", "creative"],
        is_locally_focused=False,
        desired_job_characteristics=[
            "small business",
            "creative",
            "innovative",
            "not stressful",
        ],
        is_profile_complete=False,
    )

    state = OverallState(
        messages=[{"role": "user", "content": MINIMAL_PROFILE_MESSAGE}],
        profile_information=profile_information.model_dump(),
    )

    result = extract_profile_information(state)

    assert result["profile_information"]["interests"] is not None
    assert result["profile_information"]["personal_characteristics"] is not None


@pytest.mark.llm_call
def test_extract_profile_information_with_previous_data():
    interests = ["technology", "innovation"]

    profile_information = ProfileInformation(
        age=18,
        interests=interests,
        competencies=["Math", "History", "Arts"],
        personal_characteristics=["analytical", "creative"],
        is_locally_focused=False,
        desired_job_characteristics=[
            "small business",
            "creative",
            "innovative",
            "not stressful",
        ],
        is_profile_complete=False,
    )

    state = OverallState(
        messages=[{"role": "user", "content": MINIMAL_PROFILE_MESSAGE}],
        profile_information=profile_information.model_dump(),
    )

    result = extract_profile_information(state)

    assert len(result["profile_information"]["interests"]) > len(
        interests
    )  # Ensure interests are updated
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

    selected_jobs_with_id = {
        job["name"]: job["job_id"] for job in jobs if job["name"] in selected_jobs
    }

    selected_job_ids = list(selected_jobs_with_id.values())

    state = OverallState(
        job_recommendations=jobs,
        research_queue=selected_job_ids,
    )

    result = start_job_research(state)

    # Update state with research results
    assert result["current_job_research"]["job"]["name"] == "software developer"
    assert (
        result["current_job_research"]["research_status"]
        == JobResearchStatus.INITIALIZED
    )
    assert (
        result["current_job_research"]["job"]["job_id"]
        == selected_jobs_with_id["software developer"]
    )

    state.update(result)
    assert isinstance(state["current_job_research"], dict)
    assert state["current_job_research"]["job"]["name"] == "software developer"
    assert (
        state["current_job_research"]["research_status"]
        == JobResearchStatus.INITIALIZED
    )
    assert (
        state["current_job_research"]["job"]["job_id"]
        == selected_jobs_with_id["software developer"]
    )
    assert state["research_queue"] == [selected_jobs_with_id["data scientist"]]




@pytest.mark.llm_call
def test_research_query(
    software_developer,
    research_config_for_testing
    ):
    job_research = JobResearch(
        job=software_developer,
        research_data=[],
        research_status=JobResearchStatus.INITIALIZED,
    )

    state = OverallState(current_job_research=job_research.model_dump())

    result = get_research_query(state, run_config=research_config_for_testing)

    assert (
        result["current_job_research"]["research_status"]
        == JobResearchStatus.RESEARCH_QUERY_GENERATED
    )
    assert isinstance(result["current_job_research"]["research_data"], list)
    queries = [
        data["query"] for data in result["current_job_research"]["research_data"]
    ]
    assert all(isinstance(query, str) and query for query in queries)
    assert len(queries) == research_config_for_testing["configurable"]["number_of_research_queries"]


@pytest.mark.llm_call
def test_conduct_research(
    software_developer,
):
    job_research_data = [
        JobResearchData(
            query="What are the main responsibilities of a Software Developer?",
        ),
        JobResearchData(
            query="What skills are essential for a Software Developer?",
        ),
    ]
    job_research = JobResearch(
        job=software_developer,
        research_data=job_research_data,
        research_status=JobResearchStatus.RESEARCH_QUERY_GENERATED,
    ).model_dump()

    state = OverallState(
        current_job_research=job_research,
    )

    result = conduct_research(state)

    job_research_result = result["current_job_research"]

    assert (
        job_research_result["research_status"]
        == JobResearchStatus.RESEARCH_RESULTS_GATHERED
    )
    assert len(job_research_result["research_data"][0]["results"]) > 0
    assert len(job_research_result["research_data"][0]["sources"]) > 0
    assert result["messages"] is not None


@pytest.mark.llm_call
def test_analyze_research(
    software_developer,
):
    job_research_data = [
        JobResearchData(
            query="What are the main responsibilities of a Software Developer?",
            results=[
                "Designing, coding, and testing software applications.",
                "Collaborating with cross-functional teams to define project requirements.",
                "Debugging and resolving software issues.",
            ],
            sources=[
                "https://www.example.com/software-developer-responsibilities",
                "https://www.example.com/what-does-a-software-developer-do",
            ],
        ),
        JobResearchData(
            query="What skills are essential for a Software Developer?",
            results=[
                "Proficiency in programming languages such as Java, Python, or C#.",
                "Strong problem-solving and analytical skills.",
                "Experience with version control systems like Git.",
            ],
            sources=[
                "https://www.example.com/software-developer-skills",
                "https://www.example.com/essential-skills-for-developers",
            ],
        ),
    ]
    job_research = JobResearch(
        job=software_developer,
        research_data=job_research_data,
        research_status=JobResearchStatus.RESEARCH_RESULTS_GATHERED,
    ).model_dump()

    state = OverallState(current_job_research=job_research)

    result = analyze_research(state)

    job_research_result = result["completed_job_research"][0]

    assert job_research_result["research_status"] == JobResearchStatus.COMPLETED
    assert isinstance(job_research_result["research_analysis"], str)
    assert result["messages"] is not None

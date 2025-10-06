from agent.models import Job, JobRecommendationData
from agent.tasks import (
    get_job_recommendations,
    extract_profile_information,
    ask_profile_questions,
    get_research_query,
    start_job_research
)
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

@pytest.mark.llm_call
def test_start_job_research():

    job = [
        {"job_role": "software developer",
            "job_role_description": "A Software Developer writes and maintains code for software applications.",
        },
        {"job_role": "data scientist",
            "job_role_description": "A Data Scientist analyzes and interprets complex data to help companies make decisions.",
        },
        {"job_role": "product manager",
            "job_role_description": "A Product Manager oversees the development and delivery of products, ensuring they meet customer needs and business goals.",
        }
    ]

    selected_jobs = ["software developer", "data scientist"]

    state = OverallState(
        job_recommendations_data=job,
        selected_jobs=selected_jobs
    )

    result = start_job_research(state)

    # Update state with research results
    assert result["job_research_data"]["job_recommendation"]["job_role"] == "software developer"
    assert result["job_research_data"]["job_recommendation"]["research_status"] == "INITIALIZED"

    state.update(result)
    assert state["job_research_data"]["job_recommendation"]["job_role"] == "software developer"
    assert state["job_research_data"]["job_recommendation"]["research_status"] == "INITIALIZED"

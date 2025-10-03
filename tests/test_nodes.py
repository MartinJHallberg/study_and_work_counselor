from agent.tasks import (
    get_job_recommendations,
    extract_profile_information,
    ask_profile_questions,
    get_research_query
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

    assert result["profile_data"]["interests"] is not None
    assert result["profile_data"]["personal_characteristics"] is not None

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

    assert len(result["profile_data"]["interests"]) > len(interests) # Ensure interests are updated
    assert result["profile_data"]["personal_characteristics"] is not None
    assert result["profile_data"]["age"] == 18  # Ensure age remains unchanged

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

    for key, val in result["job_recommendations_data"].items():
        if isinstance(val, list):
            assert val, f"Value for key '{key}' should not be an empty list"
            assert len(val) == 3
        else:
            assert val is not None, f"Value for key '{key}' should not be None"


@pytest.mark.llm_call
def test_research_query():
    state = OverallState(
        job_role=["Software Developer"],
        job_role_description=[
            "A Software Developer writes and maintains code for software applications.",
        ],
    )

    result = get_research_query(state)

    assert result["research_query"] is not None
    assert isinstance(result["research_query"], list)



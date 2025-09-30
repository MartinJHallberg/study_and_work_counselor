from agent.tasks import (
    get_job_recommendations,
    extract_profile_information,
    ask_profile_questions,
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

    assert result["interests"] is not None
    assert result["personal_characteristics"] is not None


@pytest.mark.llm_call
def test_ask_profile_questions_with_minimal_input():
    state = ProfilingState(
        messages=[{"role": "user", "content": MINIMAL_PROFILE_MESSAGE}],
    )

    result = ask_profile_questions(state)

    assert result["messages"] is not None
    assert isinstance(result["profile_questions"], list)
    assert result["profile_questions"], "Questions should not be None"


@pytest.mark.llm_call
def test_get_job_recommendations_with_complete_profile():
    state = ProfilingState(
        age=18,
        interests=["technology", "innovation"],
        competencies=["Math", "History", "Arts"],
        personal_characteristics=["analytical", "creative"],
        is_locally_focused=False,
        desired_job_characteristics=[
            "small business",
            "creative",
            "innovative",
            "not stressful",
        ],
        is_profile_complete=True,
    )

    result = get_job_recommendations(state)

    for key, value in result.items():
        if isinstance(value, list):
            assert value, f"Value for key '{key}' should not be an empty list"
        else:
            assert value is not None, f"Value for key '{key}' should not be None"

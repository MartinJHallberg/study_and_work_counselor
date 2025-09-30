from agent.tasks import (
    get_job_recommendations
)
from agent.state import (
    ProfilingState
)


def test_get_job_recommendations_with_complete_profile():
    state = ProfilingState(
        age=18,
        interests=["technology", "innovation"],
        competencies=["Math", "History", "Arts"],
        personal_characteristics=["analytical", "creative"],
        is_locally_focused=False,
        desired_job_characteristics=["small business", "creative", "innovative",  "not stressful"],
        is_profile_complete=True,
    )

    result = get_job_recommendations(state)

    for key, value in result.items():
        if isinstance(value, list):
            assert value, f"Value for key '{key}' should not be an empty list"
        else:
            assert value is not None, f"Value for key '{key}' should not be None"
from agent.tasks import ProfileInformation





def test_to_prompt_string():
    profile = ProfileInformation(
        age=25,
        interests=["programming", "music", "hiking"],
        competencies=["Python", "JavaScript", "SQL"],
        personal_characteristics=["analytical", "creative"],
        is_locally_focused=False,
        desired_job_characteristics=["remote work", "good work-life balance"]
    )
    
    prompt_string = profile.get_attribute_with_values()
    
    # Test that all expected fields are present
    assert "Age: 25" in prompt_string
    assert "Interests: programming, music, hiking" in prompt_string
    assert "Competencies: Python, JavaScript, SQL" in prompt_string 
    assert "Personal Characteristics: analytical, creative" in prompt_string
    assert "Is Locally Focused: No" in prompt_string
    assert "Desired Job Characteristics: remote work, good work-life balance" in prompt_string



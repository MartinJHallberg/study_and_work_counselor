import pytest
from agent.models import Job


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

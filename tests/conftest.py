import pytest
from agent.models import Job
from langchain_core.runnables import RunnableConfig


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

@pytest.fixture
def research_config_for_testing():
    """Test configuration with reduced queries for faster tests."""
    return RunnableConfig(
                configurable={
                    "max_search_results": 1,
                    "search_depth": "basic",
                    "include_raw_content": False,
                    "number_of_research_queries": 2,
                }
            )
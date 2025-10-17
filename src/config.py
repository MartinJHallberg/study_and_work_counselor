from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig

load_dotenv()


class Config(BaseSettings):
    """Application configuration using Pydantic BaseSettings."""

    openai_api_key: str = Field(..., env="OPENAI_API_KEY", description="OpenAI API key")
    tavily_api_key: str = Field(..., env="TAVILY_API_KEY", description="Tavily API key")
    number_of_job_recommendations: int = Field(
        10, description="Number of job recommendations to return"
    )
    number_of_research_queries: int = Field(
        5, description="Number of research queries to generate per job role"
    )
    tavily_max_search_results: int = Field(
        2, description="Maximum number of search results from Tavily"
    )
    tavily_search_depth: str = Field(
        "advanced", description="Depth of the search (e.g., shallow, deep)"
    )
    tavily_include_raw_content: bool = Field(
        True, description="Whether to include raw content in search results"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    def to_runnable_config(self) -> RunnableConfig:
        """Convert to RunnableConfig for LangChain usage."""
        return RunnableConfig(
            configurable={
                "number_of_job_recommendations": self.number_of_job_recommendations,
                "number_of_research_queries": self.number_of_research_queries,
                "max_search_results": self.tavily_max_search_results,
                "search_depth": self.tavily_search_depth,
                "include_raw_content": self.tavily_include_raw_content,
            }
        )


# Create a global config instance
config = Config()

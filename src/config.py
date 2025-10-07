import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    """Application configuration using Pydantic BaseSettings."""
    
    openai_api_key: str = Field(..., env="OPENAI_API_KEY", description="OpenAI API key")
    tavily_api_key: str = Field(..., env="TAVILY_API_KEY", description="Tavily API key")
    number_of_job_recommendations: int = Field(10, description="Number of job recommendations to return")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


# Create a global config instance
config = Config()
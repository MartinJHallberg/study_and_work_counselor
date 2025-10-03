import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

NUMBER_OF_JOB_RECOMMENDATIONS = 10
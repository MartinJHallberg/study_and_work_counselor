from agent.state import (
    OverallState,
    ProfilingState,
    JobRecommendationState,
)
from agent.models import (
    Job,
    ProfileInformation,
    ProfileQuestions,
    JobRecommendationData,
    JobRecommendations,
    ResearchQueries,
    JobResearchData,
    JobResearch,
    JobResearchStatus,
)
from agent.tools import (
    web_search,
)
from langchain_openai import ChatOpenAI
from agent.prompts import (
    PROFILE_INFORMATION_PROMPT,
    FOLLOW_UP_QUESTION_PROMPT,
    JOB_RECOMMENDATIONS_PROMPT,
    RESEARCH_QUERY_PROMPT,
    RESEARCH_PROMPT,
)
from langchain_core.messages import AIMessage
from config import config


def get_llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


def get_conversation_history(state: OverallState) -> str:
    messages = state["messages"]

    # Extract and format user messages
    user_messages = []
    for msg in messages:
        if hasattr(msg, "content"):
            if msg.__class__.__name__ == "HumanMessage":
                user_messages.append(f"User: {msg.content}")
            elif msg.__class__.__name__ == "AIMessage":
                user_messages.append(f"Assistant: {msg.content}")
        else:
            # Handle string messages (from initial state)
            user_messages.append(f"User: {str(msg)}")

    return "\n".join(user_messages) if user_messages else "No previous conversation"


def extract_profile_information(state: OverallState) -> ProfilingState:
    # Extract and format user messages
    user_input_text = get_conversation_history(state)
    current_profile_info = state.get("profile_information", None)

    llm = get_llm()  # Get LLM when needed
    structured_llm = llm.with_structured_output(ProfileInformation)
    formatted_prompt = PROFILE_INFORMATION_PROMPT.format(
        user_input=user_input_text,
        current_profile_information=current_profile_info,
    )
    structured_response = structured_llm.invoke(formatted_prompt)

    # Check if profile is complete by verifying no null values
    profile_dict = structured_response.model_dump()
    if any(value is None for value in profile_dict.values()):
        has_null_values = True
        message = "Profile information is incomplete, further questions are needed. Generating questions..."
    else:
        has_null_values = False
        message = "Profile information extracted successfully."

    # Update the structured response with completeness check
    profile_dict["is_profile_complete"] = not has_null_values

    return {
        "messages": [AIMessage(content=message)],
        "profile_information": profile_dict,
    }


def ask_profile_questions(state: ProfilingState) -> OverallState:
    llm = get_llm()  # Get LLM when needed
    structured_llm = llm.with_structured_output(ProfileQuestions)
    current_profile_info = state.get("profile_information", None)

    formatted_prompt = FOLLOW_UP_QUESTION_PROMPT.format(
        current_profile_information=current_profile_info,
    )

    structured_response = structured_llm.invoke(formatted_prompt)

    return {
        "messages": [AIMessage(content=structured_response.message)],
        "profile_questions": structured_response.questions,
    }


def get_job_recommendations(
    state: OverallState, number_of_recommendations=config.number_of_job_recommendations
) -> JobRecommendationState:
    llm = get_llm()
    structured_llm = llm.with_structured_output(JobRecommendations)
    current_profile_info = state.get("profile_information", None)

    formatted_prompt = JOB_RECOMMENDATIONS_PROMPT.format(
        number_of_recommendations=number_of_recommendations,
        current_profile_information=current_profile_info,
    )
    structured_response = structured_llm.invoke(formatted_prompt)

    job_recommendations_list = [
        JobRecommendationData(**job)
        for job in structured_response.model_dump().get("job_recommendations", [])
    ]

    return {
        "messages": [AIMessage(content=structured_response.summary)],
        "job_recommendations_data": job_recommendations_list,
    }


def start_job_research(state: OverallState) -> OverallState:
    """Initialize job research for next job in queue."""
    queue = state.get("research_queue", [])

    if not queue:
        return {
            "messages": [AIMessage(content="No jobs selected for research.")],
        }

    job_id = queue[0]
    job_recommendations = state["job_recommendations"]
    job_data = None

    for job_rec in job_recommendations:
        if job_rec["job_id"] == job_id:
            job_data = job_rec
            break

    if not job_data:
        return {
            "messages": [AIMessage(content=f"Job with ID {job_id} not found.")],
        }

    # Create initial job research with empty research_data list
    job_research = JobResearch(
        job=Job(**job_data),
        research_data=[],  # Initialize empty list for research entries
        research_status=JobResearchStatus.INITIALIZED,
    )

    return {
        "messages": [AIMessage(content=f"Starting research on {job_data['name']}")],
        "current_job_research": job_research.model_dump(),
        "research_queue": queue[1:],
    }


def get_research_query(
        state: OverallState,
        number_of_queries: int = config.number_of_research_queries
    ) -> OverallState:
    """Generate research queries and create JobResearchData entries."""
    current_job = state["current_job_research"]

    if not current_job:
        return {
            "messages": [AIMessage(content="No current job research found.")],
        }

    llm = get_llm()
    structured_llm = llm.with_structured_output(ResearchQueries)

    formatted_prompt = RESEARCH_QUERY_PROMPT.format(
        number_of_queries=number_of_queries,
        job=current_job["job"]["name"],
        description=current_job["job"]["description"]
    )
    structured_response = structured_llm.invoke(formatted_prompt)

    # Create JobResearchData entries for each query
    research_data_entries = []
    for query in structured_response.queries:
        research_data_entries.append(
            JobResearchData(
                query=query,
                results=None,  # Will be filled in conduct_research
                sources=None,  # Will be filled in conduct_research
            ).model_dump()
        )

    # Update the current job research
    updated_research = JobResearch(**current_job)
    updated_research.research_data = research_data_entries
    updated_research.research_status = JobResearchStatus.RESEARCH_QUERY_GENERATED

    return {
        "messages": [
            AIMessage(content="Research queries generated. Starting research...")
        ],
        "current_job_research": updated_research.model_dump(),
    }


def conduct_research(state: OverallState) -> OverallState:
    """Conduct research for each query in the current job research."""
    current_research = state.get("current_job_research")

    if not current_research or not current_research.get("research_data"):
        return {
            "messages": [AIMessage(content="No research queries found.")],
        }

    llm = get_llm()
    tools = [web_search]
    llm_with_tools = llm.bind_tools(tools)

    updated_entries = []

    # Process each research data entry
    for entry_data in current_research["research_data"]:
        research_query = entry_data["query"]
        formatted_prompt = RESEARCH_PROMPT.format(research_query=research_query)
        response = llm_with_tools.invoke(formatted_prompt)

        research_results = []
        sources = []

        # Check if response has tool_calls
        tool_calls = getattr(response, "tool_calls", None)
        if tool_calls:
            for tool_call in tool_calls:
                if tool_call["name"] == "web_search":
                    result = web_search.invoke(tool_call["args"])
                    for item in result["results"]:
                        research_results.append(f"{item['title']}: {item['content']}")
                        sources.append(item["url"])

        # Update the entry with results
        updated_entry = JobResearchData(
            query=research_query, results=research_results, sources=sources
        )
        updated_entries.append(updated_entry.model_dump())

    # Update the job research
    updated_research = JobResearch(**current_research)
    updated_research.research_data = updated_entries
    updated_research.research_status = JobResearchStatus.RESEARCH_RESULTS_GATHERED

    return {
        "messages": [AIMessage(content="Research completed for all queries.")],
        "current_job_research": updated_research.model_dump(),
    }


def analyze_research(state: OverallState) -> OverallState:
    """Analyze the research results and complete the job research."""
    current_research = state.get("current_job_research")

    if not current_research or not current_research.get("research_data"):
        return {
            "messages": [AIMessage(content="No research data found for analysis.")],
        }

    llm = get_llm()

    # Combine all query results for analysis
    combined_results = []
    for entry in current_research["research_data"]:
        if entry.get("results"):
            query_summary = (
                f"Query: {entry['query']}\nResults: {'; '.join(entry['results'])}"
            )
            if entry.get("sources"):
                query_summary += f"\nSources: {'; '.join(entry['sources'])}"
            combined_results.append(query_summary)

    combined_text = "\n\n".join(combined_results)

    analysis_prompt = (
        "Based on the following research results, provide a concise analysis summarizing key insights:\n"
        f"{combined_text}"
    )

    response = llm.invoke(analysis_prompt)

    # Update and complete the research
    updated_research = JobResearch(**current_research)
    updated_research.research_analysis = response.content
    updated_research.research_status = JobResearchStatus.COMPLETED

    return {
        "messages": [AIMessage(content="Research analysis completed.")],
        "completed_job_research": [updated_research.model_dump()],
        "current_job_research": None,  # Clear current research
    }

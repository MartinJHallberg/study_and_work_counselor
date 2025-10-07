from agent.state import (
    OverallState,
    ProfilingState,
    JobRecommendationState,
    ResearchState,
)
from agent.models import (
    ProfileInformation,
    ProfileQuestions,
    JobRecommendationData,
    JobRecommendations,
    ResearchQuery,
    JobResearchData,
    JobResearchStatus,
)
from agent.tools import(
    web_search,
)
from langchain_openai import ChatOpenAI
from agent.prompts import (
    PROFILE_INFORMATION_PROMPT,
    FOLLOW_UP_QUESTION_PROMPT,
    JOB_RECOMMENDATIONS_PROMPT,
    RESEARCH_QUERY_PROMPT,
    RESEARCH_PROMPT
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
    current_profile_info = state["profile_data"]

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


def get_job_recommendations(state: OverallState, number_of_recommendations = config.number_of_job_recommendations) -> JobRecommendationState:
    llm = get_llm()
    structured_llm = llm.with_structured_output(JobRecommendations)
    current_profile_info = state.get("profile_information", None)

    formatted_prompt = JOB_RECOMMENDATIONS_PROMPT.format(
        number_of_recommendations=number_of_recommendations,
        current_profile_information=current_profile_info,
    )
    structured_response = structured_llm.invoke(formatted_prompt)

    job_recommendations_list = [JobRecommendationData(**job) for job in structured_response.model_dump().get("job_recommendations", [])]

    return {
        "messages": [AIMessage(content=structured_response.summary)],
        "job_recommendations_data": job_recommendations_list,
    }

def get_research_query(state: OverallState) -> OverallState:
    llm = get_llm()
    structured_llm = llm.with_structured_output(ResearchQuery)

    formatted_prompt = RESEARCH_QUERY_PROMPT.format(
        job=state.get("job_recommendations_data").get("name"),
        description=state.get("job_recommendations_data").get("description")
    )
    structured_response = structured_llm.invoke(formatted_prompt)

    return {
        "messages": [AIMessage(content="I've created a research plan. Let me start investigating...")],
        "research_query": structured_response.research_query,
    }


def start_job_research(state: OverallState) -> OverallState:
    """Initialize job research for selected jobs."""
    selected_jobs = state.get("selected_jobs", [])
    
    if not selected_jobs:
        return {
            "messages": [AIMessage(content="No jobs selected for research. Please select jobs first.")],
        }
    
    # Initialize research results dictionary
    jobs_in_research = [job_res["job"]["name"] for job_res in state["job_research_data"]] if state.get("job_research_data") else []

    candidate_job = [job for job in selected_jobs if job not in jobs_in_research]

    job = candidate_job[0]

    job_data = [job_ for job_ in state.get("job_recommendations_data") if job_["name"] == job][0]

    job_research_data = JobResearchData(
        job=job_data,
        research_status=JobResearchStatus.INITIALIZED
    )
    
    return {
        "messages": [AIMessage(content=f"Starting research on {len(selected_jobs)} selected jobs. Beginning with: {job}")],
        "job_research_data": [job_research_data.model_dump()],
    }

def research_job(state: OverallState) -> OverallState:
    """Conduct research on the job using the research query."""
    if not state["job_research_data"]:
        return {
            "messages": [AIMessage(content="No job research initialized. Please start job research first.")],
        }
    
    job_research = state["job_research_data"][0]  # Assuming single job research at a time
    if job_research["research_status"] == JobResearchStatus.COMPLETED:
        return {
            "messages": [AIMessage(content=f"Research on {job_research['job']['name']} is already completed.")],
        }
    
    llm = get_llm()
    structured_llm = llm.with_structured_output(JobResearchData)

    formatted_prompt = RESEARCH_QUERY_PROMPT.format(
        job=job_research["job"]["name"],
        description=job_research["job"]["description"]
    )
    structured_response = structured_llm.invoke(formatted_prompt)

    # Update research status
    job_research["research_query"] = structured_response.research_query
    job_research["research_status"] = JobResearchStatus.RESEARCH_QUERY_GENERATED

    return {
        "messages": [AIMessage(content=f"Research queries generated for {job_research['job']['name']}.")],
        "job_research_data": [job_research],
    }

def conduct_research(state: OverallState) -> OverallState:
    """Conducting research based on the research query."""
    if not state["job_research_data"]:
        return {
            "messages": [AIMessage(content="No job research initialized. Please start job research first.")],
        }
    
    job_research = state["job_research_data"][0]  # Assuming single job research at a time
    if job_research["research_status"] != JobResearchStatus.RESEARCH_QUERY_GENERATED:
        return {
            "messages": [AIMessage(content=f"Research on {job_research['job']['name']} is not ready to be conducted. Please generate research queries first.")],
        }
    
    llm = get_llm()

    tools = [web_search]

    llm_with_tools = llm.bind_tools(tools)

    research_query = state["job_research_data"][0]["research_query"]

    formatted_prompt = RESEARCH_PROMPT.format(
        research_query=research_query
    )

    response = llm_with_tools.invoke(formatted_prompt)

    # Process tool calls if any
    research_results = []
    sources = []
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            # Execute the tool and collect results
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            if tool_name == 'web_search':
                result = web_search.invoke(tool_args)
                research_results.append(result)
                sources.append(f"Web search: {tool_args.get('query', '')}")

    
from agent.graph import create_research_graph
from agent.state import OverallState
from agent.models import JobResearchStatus
from enum import Enum
from typing import Set, Dict, Any


class ResearchWorkflowState(Enum):
    INITIAL = "initial"
    JOB_RESEARCH_STARTED = "job_research_started"
    QUERIES_GENERATED = "queries_generated"
    RESEARCH_COMPLETED = "research_completed"
    ANALYSIS_COMPLETED = "analysis_completed"


class WorkflowStateMachine:
    def __init__(self):
        self.current_state = ResearchWorkflowState.INITIAL
        self.valid_transitions = {
            ResearchWorkflowState.INITIAL: {ResearchWorkflowState.JOB_RESEARCH_STARTED},
            ResearchWorkflowState.JOB_RESEARCH_STARTED: {ResearchWorkflowState.QUERIES_GENERATED},
            ResearchWorkflowState.QUERIES_GENERATED: {ResearchWorkflowState.RESEARCH_COMPLETED},
            ResearchWorkflowState.RESEARCH_COMPLETED: {ResearchWorkflowState.ANALYSIS_COMPLETED},
            ResearchWorkflowState.ANALYSIS_COMPLETED: set()  # Final state
        }
    
    def transition(self, new_state: ResearchWorkflowState):
        """Validate and perform state transition."""
        if new_state not in self.valid_transitions[self.current_state]:
            raise ValueError(f"Invalid transition from {self.current_state} to {new_state}")
        self.current_state = new_state
    
    def get_expected_state_properties(self) -> Dict[str, Any]:
        """Get expected properties for current state."""
        state_properties = {
            ResearchWorkflowState.INITIAL: {
                "should_have_research_queue": True,
                "should_have_current_research": False,
            },
            ResearchWorkflowState.JOB_RESEARCH_STARTED: {
                "should_have_current_research": True,
                "research_status": JobResearchStatus.INITIALIZED,
            },
            ResearchWorkflowState.QUERIES_GENERATED: {
                "research_status": JobResearchStatus.RESEARCH_QUERY_GENERATED,
                "should_have_research_data": True,
            },
            ResearchWorkflowState.RESEARCH_COMPLETED: {
                "research_status": JobResearchStatus.RESEARCH_RESULTS_GATHERED,
                "should_have_results": True,
            },
            ResearchWorkflowState.ANALYSIS_COMPLETED: {
                "should_have_completed_research": True,
                "should_have_current_research": False,
            }
        }
        return state_properties[self.current_state]


def test_research_workflow_state_machine(software_developer, research_config_for_testing):
    """Test workflow using state machine validation."""
    state = OverallState(
        job_recommendations=[software_developer.model_dump()],
        research_queue=[software_developer.job_id],
    )

    research_graph = create_research_graph()
    state_machine = WorkflowStateMachine()
    
    step_to_state_map = {
        "start_job_research": ResearchWorkflowState.JOB_RESEARCH_STARTED,
        "get_research_query": ResearchWorkflowState.QUERIES_GENERATED,
        "conduct_research": ResearchWorkflowState.RESEARCH_COMPLETED,
        "analyze_research": ResearchWorkflowState.ANALYSIS_COMPLETED,
    }

    for step in research_graph.stream(state, config=research_config_for_testing):
        step_name = list(step.keys())[0]
        step_state = step[step_name]
        
        # Transition state machine
        expected_workflow_state = step_to_state_map[step_name]
        state_machine.transition(expected_workflow_state)
        
        # Validate state properties
        expected_properties = state_machine.get_expected_state_properties()
        _validate_state_properties(step_state, expected_properties)


def _validate_state_properties(state: Dict[str, Any], expected_properties: Dict[str, Any]):
    """Validate state matches expected properties."""
    for property_name, expected_value in expected_properties.items():
        if property_name == "should_have_research_queue":
            has_queue = len(state.get("research_queue", [])) > 0
            assert has_queue == expected_value
            
        elif property_name == "should_have_current_research":
            has_current = state.get("current_job_research") is not None
            assert has_current == expected_value
            
        elif property_name == "research_status":
            current_research = state.get("current_job_research")
            if current_research:
                assert current_research["research_status"] == expected_value
                
        # Add more property validations as needed


def test_research_workflow_state_updates(software_developer, research_config_for_testing):
    """Test that state updates work correctly (reducer functions)."""
    initial_state = OverallState(
        job_recommendations=[software_developer.model_dump()],
        research_queue=[software_developer.job_id],
        messages=[],
        current_job_research=None,
        completed_job_research=[],
    )

    research_graph = create_research_graph()
    
    # Track state changes
    previous_state = initial_state.copy()
    step_count = 0
    total_messages = 0
    
    for step in research_graph.stream(initial_state, config=research_config_for_testing):
        step_name = list(step.keys())[0]
        current_state = step[step_name]
        step_count += 1
        
        print(f"Step {step_count}: {step_name}")  # For debugging
        
        # Test state update behavior for each specific step
        if step_name == "start_job_research":
            _validate_start_job_research_updates(previous_state, current_state, software_developer)
            
        elif step_name == "get_research_query":
            _validate_get_research_query_updates(previous_state, current_state, research_config_for_testing)
            
        elif step_name == "conduct_research":
            _validate_conduct_research_updates(previous_state, current_state)
            
        elif step_name == "analyze_research":
            _validate_analyze_research_updates(previous_state, current_state)
        
        # Test general state update principles
        _validate_general_state_updates(previous_state, current_state, step_name)
        
        # Test message accumulation
        if "messages" in current_state:
            new_messages = len(current_state["messages"])
            assert new_messages >= total_messages, f"Messages decreased in {step_name}"
            total_messages = new_messages
        
        # Update for next iteration
        previous_state = current_state.copy()
    
    # Final state validation
    assert step_count == 4, "Should have exactly 4 steps"
    assert total_messages >= 4, "Should have accumulated messages from all steps"


def _validate_start_job_research_updates(previous_state: Dict, current_state: Dict, expected_job):
    """Validate state changes in start_job_research step."""
    # Research queue should decrease by 1
    prev_queue_len = len(previous_state.get("research_queue", []))
    curr_queue_len = len(current_state.get("research_queue", []))
    assert curr_queue_len == prev_queue_len - 1, "Research queue should decrease by 1"
    
    # current_job_research should be created (was None, now exists)
    assert previous_state.get("current_job_research") is None, "Should start with no current research"
    assert current_state.get("current_job_research") is not None, "Should create current research"
    
    # Job data should match
    current_research = current_state["current_job_research"]
    assert current_research["job"]["job_id"] == expected_job.job_id, "Job ID should match"
    
    # Should preserve other fields
    assert current_state.get("job_recommendations") == previous_state.get("job_recommendations"), \
        "job_recommendations should be preserved"
    assert current_state.get("completed_job_research") == previous_state.get("completed_job_research"), \
        "completed_job_research should be preserved"


def _validate_get_research_query_updates(previous_state: Dict, current_state: Dict, config):
    """Validate state changes in get_research_query step."""
    # current_job_research should be updated, not replaced
    prev_research = previous_state.get("current_job_research")
    curr_research = current_state.get("current_job_research")
    
    assert prev_research is not None, "Previous state should have current_job_research"
    assert curr_research is not None, "Current state should have current_job_research"
    
    # Job data should be preserved
    assert curr_research["job"] == prev_research["job"], "Job data should be preserved"
    
    # Research data should be added
    assert prev_research.get("research_data") is None, "Previous should have no research_data"
    assert curr_research.get("research_data") is not None, "Current should have research_data"
    
    # Number of queries should match config
    expected_queries = config.configurable.get("number_of_research_queries", 5)
    assert len(curr_research["research_data"]) == expected_queries, \
        f"Should have {expected_queries} research queries"
    
    # Research status should be updated
    assert curr_research["research_status"] == JobResearchStatus.RESEARCH_QUERY_GENERATED
    
    # Other fields should be preserved
    assert current_state.get("research_queue") == previous_state.get("research_queue"), \
        "research_queue should be preserved"


def _validate_conduct_research_updates(previous_state: Dict, current_state: Dict):
    """Validate state changes in conduct_research step."""
    prev_research = previous_state.get("current_job_research")
    curr_research = current_state.get("current_job_research")
    
    # Research queries should be preserved but enhanced with results
    prev_data = prev_research["research_data"]
    curr_data = curr_research["research_data"]
    
    assert len(curr_data) == len(prev_data), "Number of research entries should be preserved"
    
    for i, (prev_entry, curr_entry) in enumerate(zip(prev_data, curr_data)):
        # Query should be preserved
        assert curr_entry["query"] == prev_entry["query"], f"Query {i} should be preserved"
        
        # Results should be added
        assert prev_entry.get("results") is None, f"Previous entry {i} should have no results"
        assert curr_entry.get("results") is not None, f"Current entry {i} should have results"
        assert len(curr_entry["results"]) > 0, f"Entry {i} should have non-empty results"
        
        # Sources should be added
        assert prev_entry.get("sources") is None, f"Previous entry {i} should have no sources"
        assert curr_entry.get("sources") is not None, f"Current entry {i} should have sources"
    
    # Status should be updated
    assert curr_research["research_status"] == JobResearchStatus.RESEARCH_RESULTS_GATHERED


def _validate_analyze_research_updates(previous_state: Dict, current_state: Dict):
    """Validate state changes in analyze_research step."""
    # current_job_research should be moved to completed_job_research
    prev_current = previous_state.get("current_job_research")
    curr_current = current_state.get("current_job_research")
    
    assert prev_current is not None, "Previous state should have current_job_research"
    assert curr_current is None, "Current state should have no current_job_research"
    
    # completed_job_research should be updated
    prev_completed = previous_state.get("completed_job_research", [])
    curr_completed = current_state.get("completed_job_research", [])
    
    assert len(curr_completed) == len(prev_completed) + 1, "Should add one completed research"
    
    # The completed research should have analysis
    completed_research = curr_completed[-1]  # Last item
    assert completed_research["research_status"] == JobResearchStatus.COMPLETED
    assert completed_research.get("research_analysis") is not None, "Should have analysis"
    
    # Job data should be preserved through the whole process
    assert completed_research["job"] == prev_current["job"], "Job data should be preserved"


def _validate_general_state_updates(previous_state: Dict, current_state: Dict, step_name: str):
    """Validate general state update principles."""
    # Messages should only accumulate (never decrease)
    prev_messages = len(previous_state.get("messages", []))
    curr_messages = len(current_state.get("messages", []))
    assert curr_messages >= prev_messages, f"Messages should not decrease in {step_name}"
    
    # Validate no unexpected fields are lost
    core_fields = ["job_recommendations", "research_queue", "messages", "current_job_research", "completed_job_research"]
    
    for field in core_fields:
        if field in previous_state:
            assert field in current_state, f"Field '{field}' should not be lost in {step_name}"
    
    # State should never be empty
    assert len(current_state) > 0, f"State should not be empty after {step_name}"


def test_research_workflow_field_lifecycle(software_developer, research_config_for_testing):
    """Test the complete lifecycle of specific state fields."""
    initial_state = OverallState(
        job_recommendations=[software_developer.model_dump()],
        research_queue=[software_developer.job_id],
        messages=[],
        current_job_research=None,
        completed_job_research=[],
    )

    research_graph = create_research_graph()
    
    # Track field values throughout workflow
    field_tracker = {
        "research_queue_length": [1],  # Initial length
        "current_job_research_exists": [False],  # Initial state
        "completed_research_count": [0],  # Initial count
        "message_count": [0],  # Initial count
    }
    
    for step in research_graph.stream(initial_state, config=research_config_for_testing):
        step_name = list(step.keys())[0]
        current_state = step[step_name]
        
        # Track field values
        field_tracker["research_queue_length"].append(len(current_state.get("research_queue", [])))
        field_tracker["current_job_research_exists"].append(current_state.get("current_job_research") is not None)
        field_tracker["completed_research_count"].append(len(current_state.get("completed_job_research", [])))
        field_tracker["message_count"].append(len(current_state.get("messages", [])))
    
    # Validate field lifecycle patterns
    queue_lengths = field_tracker["research_queue_length"]
    assert queue_lengths == [1, 0, 0, 0, 0], "Queue should: start=1, after_start=0, stay=0"
    
    current_exists = field_tracker["current_job_research_exists"]
    assert current_exists == [False, True, True, True, False], \
        "Current research should: start=False, exist through middle steps, end=False"
    
    completed_counts = field_tracker["completed_research_count"]
    assert completed_counts == [0, 0, 0, 0, 1], \
        "Completed count should: start=0, stay=0 until end, final=1"
    
    message_counts = field_tracker["message_count"]
    assert all(message_counts[i] <= message_counts[i+1] for i in range(len(message_counts)-1)), \
        "Message count should only increase or stay same"

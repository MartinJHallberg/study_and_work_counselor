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

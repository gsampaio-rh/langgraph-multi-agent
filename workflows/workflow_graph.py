from langgraph.graph import StateGraph, START, END
from agents.planner.planner_agent import PlannerAgent
from agents.pm.pm_agent import PMAgent
from agents.architect.architect_agent import ArchitectAgent
from agents.engineer.engineer_agent import EngineerAgent
from agents.engineer.jr_engineer_agent import JrEngineerAgent
from agents.reviewer.reviewer_agent import ReviewerAgent
from state.agent_state import get_last_entry_from_state
from config.app_config import app_config
from utils.helpers import get_current_utc_datetime
from termcolor import colored
from utils import task_utils

# Define state data structure (assuming you have AgentGraphState defined in one of the agent modules)
from agents.base_agent import AgentGraphState

def planner_node_function(state: AgentGraphState):
    PlannerAgent(
        state=state,
        role="planner",
        model_config=app_config.model_config,
    ).invoke(
        user_request=state["user_request"],
        )

def pm_node_function(state: AgentGraphState):
    PMAgent(
        state=state,
        role="manager",
        model_config=app_config.model_config,
    ).invoke(
        user_request=state["user_request"],
    )


def architect_node_function(state: AgentGraphState):
    ArchitectAgent(
        state=state,
        role="architect",
        model_config=app_config.model_config,
    ).invoke(
        user_request=state["user_request"],
    )


def ocp_engineer_node_function(state: AgentGraphState):
    EngineerAgent(
        state=state,
        role="ocp_engineer",
        model_config=app_config.model_config,
    ).invoke(
        user_request=state["user_request"],
    )


def vsphere_engineer_node_function(state: AgentGraphState):
    EngineerAgent(
        state=state,
        role="vsphere_engineer",
        model_config=app_config.model_config,
    ).invoke(
        user_request=state["user_request"],
    )


def jr_engineer_node_function(state: AgentGraphState):
    JrEngineerAgent(
        state=state,
        role="ocp_engineer",
        model_config=app_config.model_config,
    ).invoke(
        user_request=state["user_request"],
    )


def reviewer_node_function(state: AgentGraphState):
    ReviewerAgent(
        state=state,
        role="reviewer",
        model_config=app_config.model_config,
    ).invoke(
        user_request=state["user_request"],
        agent_update=get_last_entry_from_state(state, "ocp_engineer_response"),
    )


def should_continue(state):
    """
    Determines the next step in the workflow based on the agent's output.

    Parameters:
    data (dict): The data containing the agent's state.

    Returns:
    str: The next node to execute ('continue' for tool execution, 'end' to finish).
    """
    # Check if the tools_response contains a final answer or indication to stop

    tasks_list = task_utils.get_tasks_list(state)

    # Collect agents with pending tasks that have no open dependencies
    pending_agents = []

    for task in tasks_list:
        # Check if task is not completed and has no open dependencies
        if task["status"] != "completed":
            # Check dependencies
            dependencies_completed = all(
                dep_task["status"] == "completed"
                for dep_task in tasks_list
                if dep_task["task_id"] in task["dependencies"]
            )
            # Only add the agent if all dependencies are completed
            if dependencies_completed:
                pending_agents.append(task["agent"])

    if pending_agents:
        print(
            colored(
                f"[{get_current_utc_datetime()}] Not all tasks are marked as 'completed'.\n"
                f"These agents {pending_agents} have tasks.\n",
                "red",
            )
        )
        return pending_agents
    else:
        print(
            colored(
                f"[{get_current_utc_datetime()}] All tasks are marked as 'completed'.",
                "green",
            )
        )
        return END


def create_graph() -> StateGraph:
    """
    Create the state graph by defining nodes and edges.
    
    Returns:
    - StateGraph: The compiled state graph ready for execution.
    """
    graph = StateGraph(AgentGraphState)

    agents = ["ocp_engineer", "vsphere_engineer", END]

    # Add nodes
    graph.add_node("planner", planner_node_function)
    graph.add_node("manager", pm_node_function)
    graph.add_node("ocp_engineer", jr_engineer_node_function)
    graph.add_node("vsphere_engineer", vsphere_engineer_node_function)
    graph.add_node("reviewer", reviewer_node_function)

    # Define the flow of the graph
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "manager")
    graph.add_conditional_edges("manager", should_continue, agents)
    # graph.add_edge("manager", END)

    graph.add_edge("ocp_engineer", "reviewer")
    graph.add_edge("vsphere_engineer", "reviewer")
    graph.add_edge("reviewer", "manager")

    return graph

def compile_workflow(graph: StateGraph):
    """
    Compile the workflow graph into an executable workflow.
    
    Parameters:
    - graph (StateGraph): The graph to be compiled.

    Returns:
    - The compiled workflow.
    """
    workflow = graph.compile()
    return workflow

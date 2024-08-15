from langgraph.graph import StateGraph, START, END
from agents.planner.planner_agent import PlannerAgent
from agents.pm.pm_agent import PMAgent
from agents.reviewer.reviewer_agent import ReviewerAgent
from agents.researcher.researcher_agent import ResearcherAgent
from state.agent_state import get_last_entry_from_state
from config.config import app_config
from custom_tools import tools_description
from utils.helpers import get_current_utc_datetime
from termcolor import colored
from utils import task_utils

# Define state data structure (assuming you have AgentGraphState defined in one of the agent modules)
from agents.base_agent import AgentGraphState

# Render the tools description
tools_description = tools_description

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

def reseacher_node_function(state: AgentGraphState):
    ResearcherAgent(
        state=state,
        role="researcher",
        model_config=app_config.model_config,
    ).invoke(
        user_request=state["user_request"]
    )


def reviewer_node_function(state: AgentGraphState):
    ReviewerAgent(
        state=state,
        role="reviewer",
        model_config=app_config.model_config,
    ).invoke(
        user_request=state["user_request"],
        agent_update=get_last_entry_from_state(state, "researcher_response"),
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

    # Check if all tasks have the status "done"
    all_done = all(task["status"] == "done" for task in tasks_list)

    if all_done:
        print(
            colored(
                f"[{get_current_utc_datetime()}] All tasks are marked as 'done'.", "green"
            )
        )
        return False
    else:
        print(
            colored(
                f"[{get_current_utc_datetime()}] Not all tasks are marked as 'done'.\n",
                "red",
            )
        )
        return True


def create_graph() -> StateGraph:
    """
    Create the state graph by defining nodes and edges.
    
    Returns:
    - StateGraph: The compiled state graph ready for execution.
    """
    graph = StateGraph(AgentGraphState)

    # Add nodes
    graph.add_node("planner_node", planner_node_function)
    graph.add_node("pm_node", pm_node_function)
    # graph.add_node("tools_node", tools_node_function)
    graph.add_node("reviewer_node", reviewer_node_function)
    graph.add_node("researcher_node", reseacher_node_function)

    # Define the flow of the graph
    graph.add_edge(START, "planner_node")
    graph.add_edge("planner_node", "pm_node")
    graph.add_conditional_edges(
        "pm_node", should_continue, {True: "researcher_node", False: END}
    )
    # graph.add_edge("pm_node", "tools_node")
    graph.add_edge("researcher_node", "reviewer_node")
    graph.add_edge("reviewer_node", "pm_node")

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

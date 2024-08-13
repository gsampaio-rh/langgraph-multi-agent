from langgraph.graph import StateGraph, START, END
from agents.planner.planner_agent import PlannerAgent
from agents.pm.pm_agent import PMAgent
from agents.tools.tools_agent import ToolsAgent
from agents.reviewer.reviewer_agent import ReviewerAgent
from state.agent_state import get_last_entry_from_state
from config.config import app_config
from custom_tools import custom_tools
from langchain.tools.render import render_text_description_and_args

# Define state data structure (assuming you have AgentGraphState defined in one of the agent modules)
from agents.base_agent import AgentGraphState

# Render the tools description
tools_description = (
    render_text_description_and_args(custom_tools).replace("{", "{{").replace("}", "}}")
)

def planner_node_function(state: AgentGraphState):
    PlannerAgent(
        state=state,
        role="planner_node",
        model_config=app_config.model_config,
    ).invoke(
        user_request=state["user_request"], 
        tools_description=tools_description,
        )

def pm_node_function(state: AgentGraphState):
    PMAgent(
        state=state,
        role="pm_node",
        model_config=app_config.model_config,
    ).invoke(
        request=state["user_request"],
        tools_description=tools_description,
    )

def tools_node_function(state: AgentGraphState):
    ToolsAgent(
        state=state,
        role="tools_node",
        model_config=app_config.model_config,
    ).invoke(
        user_request=state["user_request"],
        tools_description=tools_description,
    )

def reviewer_node_function(state: AgentGraphState):
    ReviewerAgent(
        state=state,
        role="reviewer_node",
        model_config=app_config.model_config,
    ).invoke(
        user_request=state["user_request"],
        agent_update=get_last_entry_from_state(state, "tools_response"),
    )

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
    graph.add_node("tools_node", tools_node_function)
    graph.add_node("reviewer_node", reviewer_node_function)

    # Define the flow of the graph
    graph.add_edge(START, "planner_node")
    graph.add_edge("planner_node", "pm_node")
    graph.add_edge("pm_node", "tools_node")
    graph.add_edge("tools_node", "reviewer_node")
    graph.add_edge("reviewer_node", END)

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

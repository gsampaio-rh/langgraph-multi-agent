from typing import TypedDict, Annotated, List, Any
from langchain_core.messages.human import HumanMessage
from langgraph.graph.message import add_messages

# Define the state object for the agent graph
class AgentGraphState(TypedDict):
    user_request: str
    start_chain: Annotated[list, add_messages]
    planner_response: Annotated[list, add_messages]
    manager_response: Annotated[list, add_messages]
    researcher_response: Annotated[list, add_messages]
    reviewer_response: Annotated[list, add_messages]
    end_chain: Annotated[list, add_messages]


def get_agent_graph_state(state: AgentGraphState, state_key: str) -> Any:
    """
    Retrieve a specific part of the agent graph state.

    Parameters:
    - state (AgentGraphState): The current state of the agent graph.
    - state_key (str): The key to retrieve from the state.

    Returns:
    - Any: The value associated with the state_key, or None if the key doesn't exist.
    """
    return state.get(state_key, None)


def get_all_entries_from_state(state: AgentGraphState, state_key: str) -> List[Any]:
    """
    Retrieve all entries from a list in the graph state.

    Parameters:
    - state (AgentGraphState): The current state of the agent graph.
    - state_key (str): The key to retrieve all entries from the state.

    Returns:
    - List[Any]: A list of entries, or an empty list if the key doesn't exist.
    """
    return state.get(state_key, []) if state_key in state else []


def get_first_entry_from_state(state: AgentGraphState, state_key: str) -> Any:
    """
    Retrieve the first entry from a list in the graph state.

    Parameters:
    - state (AgentGraphState): The current state of the agent graph.
    - state_key (str): The key to retrieve the first entry from the state.

    Returns:
    - Any: The first entry in the list, or None if the list is empty or the key doesn't exist.
    """
    entries = state.get(state_key, [])
    if isinstance(entries, list) and entries:
        return entries[0]
    return None


def get_last_entry_from_state(state: AgentGraphState, state_key: str) -> Any:
    """
    Retrieve the last entry from a list in the graph state.

    Parameters:
    - state (AgentGraphState): The current state of the agent graph.
    - state_key (str): The key to retrieve the last entry from the state.

    Returns:
    - Any: The last entry in the list, or None if the list is empty or the key doesn't exist.
    """
    entries = state.get(state_key, [])
    if isinstance(entries, list) and entries:
        return entries[-1]
    return None

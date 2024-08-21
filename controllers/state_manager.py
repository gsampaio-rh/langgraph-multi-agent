from typing import Any
from state.agent_state import AgentGraphState
from utils.log_utils import log_message

class StateManager:

    def __init__(self, state: AgentGraphState, agent_role: str):
        """
        Initialize the StateManager with the given state.

        Parameters:
        - state (AgentGraphState): The agent's state object.
        """
        self.state = state
        self.agent_role = agent_role

    def update_state(self, key: str, value: Any):
        """
        Update the agent's state with a new value for a given key.

        Parameters:
        - key (str): The key in the state to update.
        - value (Any): The value to append to the state's list for this key.
        """
        try:
            # Log attempt to update state
            self.log_event("info", f"🫥 Attempting to update state for key: '{key}'")

            # Ensure state is a dictionary
            if not isinstance(self.state, dict):
                raise TypeError(
                    f"😭 State should be a dictionary, but got {type(self.state).__name__}"
                )

            # Update state with the new value
            if key not in self.state:
                self.log_event(
                    "info",
                    f"😭 Key '{key}' not found, initializing with an empty list.",
                )
                self.state[key] = []

            self.state[key].append(value)
            self.log_event("info", f"😃 Successfully updated state for key '{key}'.")

        except TypeError as te:
            # Log type error
            self.log_event("error", f"😭 TypeError occurred: {str(te)}")
        except Exception as e:
            # Log any other exceptions and raise
            self.log_event(
                "error", f"😭 An error occurred while updating state: {str(e)}"
            )
            raise

    def get_state(self) -> Any:
        """
        Retrieve the value from the state for the given key.

        Parameters:
        - key (str): The key to retrieve from the state.

        Returns:
        - Any: The value associated with the key in the state, or None if the key doesn't exist.
        """
        return self.state

    def get_state_by_key(self, key: str) -> Any:
        """
        Retrieve the value from the state for the given key.

        Parameters:
        - key (str): The key to retrieve from the state.

        Returns:
        - Any: The value associated with the key in the state, or None if the key doesn't exist.
        """
        return self.state.get(key, None)

    def reset_state_key(self, key: str):
        """
        Reset the state value for a specific key.

        Parameters:
        - key (str): The key to reset in the state.
        """
        if key in self.state:
            self.state[key] = []
            self.log_event("info", f"🔄 State for key '{key}' has been reset.")

    def log_event(self, event_type: str, message: str):
        """
        Log state-related events.

        Parameters:
        - event_type (str): The type of log event (info, error, etc.).
        - message (str): The message to log.
        """
        log_message(self.agent_role, message_type=event_type, custom_message=message)

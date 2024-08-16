from typing import Any, Dict
from state.agent_state import AgentGraphState
from utils.log_utils import log_start, log_info, log_error, log_finished
from services.model_service import ModelService


class Agent:
    def __init__(self, state: AgentGraphState, role: str, model_config: dict):
        self.state = state
        self.role = role
        self.model_service = ModelService(model_config)

    def update_state(self, key: str, value: Any):
        """
        Update the agent's state with a new value for a given key.

        Parameters:
        - key (str): The key in the state to update.
        - value (Any): The value to append to the state's list for this key.

        Logs the process and handles errors with detailed exception handling.
        """
        try:
            self.log_event(
                "info",
                f"🫥 Attempting to update state for key: '{key}'",
            )
            # self.log_event("info", f"🫥 Attempting to update state for key: {key} with value: {value}")

            # Check if self.state is a dictionary
            if not isinstance(self.state, dict):
                raise TypeError(f"😭 State should be a dictionary, but got {type(self.state).__name__}")

            # Update the state
            if key not in self.state:
                self.log_event(
                    "info",
                    f"😭 Key '{key}' not found, initializing with an empty list.",
                )
                self.state[key] = []

            # Append the new value
            self.state[key].append(value)
            self.log_event("info", f"😃 Successfully updated state for key '{key}'.")

        except TypeError as te:
            # Log error if state is not a dictionary
            self.log_event("error", f"😭 TypeError occurred: {str(te)}")

        except Exception as e:
            # Catch any other exceptions and log them
            self.log_event(
                "error", f"😭 An error occurred while updating state: {str(e)}"
            )
            raise  # Re-raise the exception for further handling if necessary

    def log_event(self, event_type: str, message: str = None):
        if event_type == "start":
            log_start(self.role, message)
        elif event_type == "finished":
            log_finished(self.role, message)
        elif event_type == "info":
            log_info(self.role, message)
        elif event_type == "error":
            log_error(self.role, message)
        else:
            log_info(self.role, message)  # Fallback to info

    def invoke_model(self, sys_prompt: str, user_prompt: str):
        """
        Use the ModelService to prepare the payload, invoke the model, and process the response.
        """
        # Prepare the payload using the ModelService
        payload = self.model_service.prepare_payload(sys_prompt, user_prompt)

        # Invoke the model and get the response
        response_json = self.model_service.invoke_model(payload, self.role)

        response_human_message, response_content = (
            self.model_service.process_model_response(response_json, self.role)
        )

        self.update_state(f"{self.role}_response", response_content)

        # Process the response
        return response_human_message, response_content

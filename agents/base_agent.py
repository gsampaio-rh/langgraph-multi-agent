import json
import jsonschema
from jsonschema import validate
from typing import Any
from state.agent_state import AgentGraphState
from services.model_service import ModelService
from utils.log_utils import log_message
from tools.tool_registry import (
    get_tool_descriptions_by_category,
    get_tool_names_by_category,
)
from controllers.task_manager import TaskManager
from controllers.tool_manager import ToolManager

class Agent:
    def __init__(self, state: AgentGraphState, role: str, model_config: dict):
        self.state = state
        self.role = role
        self.task_manager = TaskManager(role)
        self.tool_manager = ToolManager()
        self.model_service = ModelService(model_config)
        self.tool_names, self.tool_descriptions = self._get_agent_tools()

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
        """
        Logs an event based on the event type. Falls back to 'info' if the event_type is unknown.
        """
        log_message(self.role, message_type=event_type, custom_message=message)

    def _get_agent_tools(self):
        """
        Get the tool names and descriptions available to the agent based on their role.
        """
        if self.role == "ocp_engineer":
            tool_names = get_tool_names_by_category("openshift")
            tool_descriptions = get_tool_descriptions_by_category("openshift")
        elif self.role == "vsphere_engineer":
            tool_names = get_tool_names_by_category("vsphere_lifecycle")
            tool_descriptions = get_tool_descriptions_by_category("vsphere_lifecycle")
        else:
            tool_names = []
            tool_descriptions = []

        return tool_names, tool_descriptions

    def invoke_model(self, sys_prompt: str, user_prompt: str, update_state:bool = True):
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

        if update_state:
            self.update_state(f"{self.role}_response", response_content)

        # Process the response
        return response_human_message, response_content

    def validate_model_output(self, response: dict, schema: dict):
        """
        Validate the planner's output against the predefined schema.

        Parameters:
        - response (dict): The JSON response from the planner agent.
        - schema (dict): The schema to validate the response against.

        Returns:
        - tuple: (bool, str) where the first value indicates success (True/False),
        and the second value contains a message (validation passed/failed with reason).
        """
        try:
            # Parse the JSON response object
            json_response_object = json.loads(response)

            # Perform schema validation
            validate(instance=json_response_object, schema=schema)
            self.log_event(
                "info", f"📑 🟢 Model response for {self.role} validation passed."
            )
            return True, json_response_object, f"{self.role} output validation passed."

        except jsonschema.exceptions.ValidationError as e:

            # Extract detailed error information
            error_field = list(e.path)  # This gives the path to the invalid field
            error_message = e.message  # The specific validation error message
            schema_error = list(e.schema_path)  # Path to the relevant part of the schema

            # Log the detailed error message
            self.log_event(
                "error",
                f"🚨 Model response for {self.role} output validation failed.\n"
                f"Field: {'.'.join(map(str, error_field)) if error_field else 'N/A'}\n"
                f"Error: {error_message}\n"
                f"Schema Error Path: {'.'.join(map(str, schema_error)) if schema_error else 'N/A'}",
            )

            # Return failure with detailed error information
            return False, None, f"{self.role} output validation failed. Field: {'.'.join(map(str, error_field)) if error_field else 'N/A'}, Error: {error_message}"

import json
import requests
from termcolor import colored
from state.agent_state import AgentGraphState
from langchain_core.messages.human import HumanMessage
from typing import Any, Dict
from utils.log_utils import (
    log,
    log_info,
    log_start,
    log_error,
    log_finished,
)

class Agent:
    def __init__(self, state: AgentGraphState, role: str, model_config: dict):
        """
        Initialize the Agent with the given state, role, and model configuration.

        Parameters:
        - state (AgentGraphState): The state object that the agent will use.
        - role (str): The role of the agent (e.g., planner, pm, tools, reviewer).
        - model_config (dict): The configuration dictionary for the language model.
        """
        self.state = state
        self.role = role
        self.model_endpoint = model_config.model_endpoint  # Directly access attributes
        self.model_name = model_config.model_name  # Directly access attributes
        self.temperature = model_config.temperature  # Directly access attributes
        self.headers = model_config.headers  # Directly access attributes
        self.stop = model_config.stop  # Directly access attributes

    def update_state(self, key: str, value: Any):
        """
        Update the agent's state with a new value for a given key.

        Parameters:
        - key (str): The key in the state to update.
        - value (Any): The value to append to the state's list for this key.
        """
        if key not in self.state:
            self.state[key] = (
                []
            )  # Initialize the key with an empty list if it doesn't exist
        self.state[key].append(value)

    def log_event(self, event_type: str, message: str = None):
        """
        Centralized logging method to handle different types of log events.
        """
        event_mapping = {
            "start": log_start,
            "finished": log_finished,
            "info": log_info,
            "error": log_error,
        }
        log_func = event_mapping.get(event_type, log)
        log_func(self.role, message)

    def _log_user_prompt(self, usr_prompt: str) -> None:
        """
        Logs the user prompt in a pretty-printed format for better readability.
        """
        try:
            usr_prompt_dict = json.loads(usr_prompt)
            pretty_usr_prompt = json.dumps(usr_prompt_dict, indent=4)
            self.log_event("processing", "User Prompt:")
            self.log_event("processing", pretty_usr_prompt)
        except json.JSONDecodeError as e:
            self.log_event("error", f"Invalid JSON string provided: {str(e)}")
            self.log_event("processing", f"User Prompt -> {usr_prompt}")

    def prepare_payload(self, sys_prompt: str, prompt: str) -> Dict[str, Any]:
        """
        Prepare the payload for the model API request.

        Parameters:
        - sys_prompt (str): The system prompt.
        - prompt (str): The user prompt.

        Returns:
        - dict: The payload for the API request.
        """
        return {
            "model": self.model_name,
            "format": "json",
            "prompt": prompt,
            "system": sys_prompt,
            "stream": False,
            "temperature": self.temperature,
        }

    def invoke_model(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the model API with the given payload and return the response.

        Parameters:
        - payload (dict): The payload to send to the model API.

        Returns:
        - dict: The JSON response from the model.
        """
        self.log_event("info", "🦙 Invoking LLAMA...")
        try:
            response = requests.post(
                self.model_endpoint, headers=self.headers, data=json.dumps(payload)
            )
            response.raise_for_status()  # Raises an error for HTTP errors
            self.log_event("info", "🦙 🤝 LLAMA Answered...")

            # Check if the response content is not empty or malformed
            if response.content.strip():  # Ensure content is not empty
                try:
                    return response.json()  # Attempt to parse JSON
                except json.JSONDecodeError as e:
                    # Log error and return fallback error message
                    self.log_event("error", f"🦙 JSON Decode Error: {str(e)}")
                    return {"error": "Invalid JSON response", "content": response.text}
            else:
                # Handle empty response content
                self.log_event("error", "🦙 Empty response from LLAMA")
                return {"error": "Empty response from model"}

        except requests.RequestException as e:
            self.log_event("error", f"🦙 Something happened... {str(e)}")
            return {"error": str(e)}

    def process_model_response(
        self, response_json: Dict[str, Any]
    ) -> (HumanMessage, Dict[str, Any]):
        """
        Process the model's response and return the parsed content.

        Parameters:
        - response_json (dict): The JSON response from the model.

        Returns:
        - HumanMessage: The formatted response as a HumanMessage.
        - dict: The parsed response content.
        """
        response_content = json.loads(response_json.get("response", "{}"))
        response_formatted = HumanMessage(content=json.dumps(response_content))

        # Pretty-print the JSON content
        pretty_content = json.dumps(response_content, indent=4)
        self.update_state(f"{self.role}_response", response_formatted)
        self.log_event("info", message=pretty_content)

        return response_formatted, pretty_content

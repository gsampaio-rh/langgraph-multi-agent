import json
import requests
from termcolor import colored
from datetime import datetime
from state.agent_state import AgentGraphState
from langchain_core.messages.human import HumanMessage
from typing import Any, Dict
from utils.log_utils import (
    log,
    log_start,
    log_processing,
    log_response,
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

    def log(self, message: str, level: str = "INFO"):
        """
        Log a message using the centralized logging utility.
        """
        log(self.role, message, level)

    def log_start(self, message: str = None):
        """
        Log the default or custom start message for this agent.
        """
        log_start(self.role, message)

    def log_processing(self, message: str = None):
        """
        Log the default or custom processing message for this agent.
        """
        log_processing(self.role, message)

    def log_finished(self, message: str = None):
        """
        Log the default or custom finished message for this agent.
        """
        log_finished(self.role, message)

    def log_response(self, response: str = None):
        log_response(self.role, response)

    def log_error(self, message: str = None):
        log_error(self.role, message)

    def update_state(self, key: str, value: Any):
        """
        Update the agent's state with a new value for a given key.

        Parameters:
        - key (str): The key in the state to update.
        - value (Any): The value to append to the state's list for this key.
        """
        if key in self.state:
            self.state[key].append(value)
        else:
            print(
                colored(
                    f"Warning: Attempting to update a non-existing state key '{key}'.",
                    "red",
                )
            )

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
        try:
            response = requests.post(
                self.model_endpoint, headers=self.headers, data=json.dumps(payload)
            )
            response.raise_for_status()  # Raises an error for HTTP errors
            return response.json()
        except requests.RequestException as e:
            print(f"Error in invoking model! {str(e)}")
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
        return HumanMessage(content=json.dumps(response_content)), response_content

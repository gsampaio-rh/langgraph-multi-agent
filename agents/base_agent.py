import json
import requests
from typing import Any, Dict
from state.agent_state import AgentGraphState
from langchain_core.messages.human import HumanMessage
from tenacity import retry, stop_after_attempt, wait_exponential
from utils.log_utils import log_start, log_info, log_error, log_finished

class Agent:
    def __init__(self, state: AgentGraphState, role: str, model_config: dict):
        self.state = state
        self.role = role
        self.model_endpoint = model_config.model_endpoint  # Directly access attributes
        self.model_name = model_config.model_name  # Directly access attributes
        self.temperature = model_config.temperature  # Directly access attributes
        self.headers = model_config.headers  # Directly access attributes
        self.stop = model_config.stop  # Directly access attributes

    def update_state(self, key: str, value: Any):
        if key not in self.state:
            self.state[key] = []
        self.state[key].append(value)

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

    def prepare_payload(self, sys_prompt: str, prompt: str) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "format": "json",
            "prompt": prompt,
            "system": sys_prompt,
            "stream": False,
            "temperature": self.temperature,
        }

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def invoke_model(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.log_event("info", "🦙 Invoking model...")
        try:
            response = requests.post(
                self.model_endpoint,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=10,
            )
            response.raise_for_status()
            self.log_event("info", "🦙 🤝 Model response received.")

            if response.content.strip():
                try:
                    return response.json()
                except json.JSONDecodeError as e:
                    self.log_event("error", f"🦙 JSON Decode Error: {str(e)}")
                    return {"error": "Invalid JSON response", "content": response.text}
            else:
                self.log_event("error", "🦙 Empty response from model")
                return {"error": "Empty response from model"}

        except requests.RequestException as e:
            self.log_event("error", f"Request Error: {str(e)}")
            raise  # Retry will kick in here

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

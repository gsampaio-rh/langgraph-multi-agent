import json
import requests
from typing import Dict, Any
from utils.log_utils import log_message
from langchain_core.messages.human import HumanMessage
from tenacity import retry, stop_after_attempt, wait_exponential

class ModelService:
    def __init__(self, model_config: dict):
        """
        Initialize the ModelService with the given configuration.

        Parameters:
        - model_config (dict): The configuration dictionary for the model.
        """
        self.model_endpoint = model_config.model_endpoint  # Directly access attributes
        self.model_name = model_config.model_name  # Directly access attributes
        self.temperature = model_config.temperature  # Directly access attributes
        self.top_p = model_config.top_p  # Directly access attributes
        self.top_k = model_config.top_k  # Directly access attributes
        self.repetition_penalty = (
            model_config.repetition_penalty
        )  # Directly access attributes
        self.headers = model_config.headers  # Directly access attributes
        self.stop = model_config.stop  # Directly access attributes

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
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repetition_penalty": self.repetition_penalty,
        }

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def invoke_model(self, payload: Dict[str, Any], agent_role: str) -> Dict[str, Any]:
        """
        Invoke the model API with retries and return the response.

        Parameters:
        - payload (dict): The payload to send to the model API.
        - agent_role (str): The role of the agent for logging purposes.

        Returns:
        - dict: The JSON response from the model.
        """
        log_message(
            agent_role, message_type="info", custom_message="🦙 Invoking model..."
        )
        try:
            response = requests.post(
                self.model_endpoint,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30,
            )
            response.raise_for_status()
            log_message(
                agent_role,
                message_type="info",
                custom_message=f"🦙 🤝 Model response received - RESPONSE_CODE {response}.",
            )
            # print(response.content.strip())

            if response.content.strip():
                try:
                    return response.json()
                except json.JSONDecodeError as e:
                    log_message(
                        self.role,
                        message_type="error",
                        custom_message=f"🦙 JSON Decode Error: {str(e)}"
                    )
                    return {"error": "Invalid JSON response", "content": response.text}
            else:
                log_message(
                    agent_role,
                    message_type="error",
                    custom_message=f"🦙 Empty response from mode",
                )
                return {"error": "Empty response from model"}

        except requests.RequestException as e:
            log_message(
                agent_role,
                message_type="error",
                custom_message=f"Request Error: {str(e)}",
            )
            raise  # Retry will kick in here

    def process_model_response(
        self, response_json: Dict[str, Any], agent_role: str
    ) -> (HumanMessage, str):
        """
        Process the model's response and return the parsed content.

        Parameters:
        - response_json (dict): The JSON response from the model.
        - agent_role (str): The role of the agent for logging purposes.

        Returns:
        - HumanMessage: The formatted response as a HumanMessage.
        - str: The pretty-printed response content.
        """
        try:
            response_content = json.loads(response_json.get("response", "{}"))
            response_formatted = HumanMessage(content=json.dumps(response_content))

            # Pretty-print the JSON content for better readability
            pretty_content = json.dumps(response_content, indent=4)
            log_message(
                agent_role,
                message_type="info",
                custom_message=pretty_content,
            )
            return response_formatted, pretty_content
        except json.JSONDecodeError as e:
            log_message(
                agent_role,
                message_type="error",
                custom_message=f"Error processing model response: {str(e)}",
            )
            return HumanMessage(content="Error processing response"), ""

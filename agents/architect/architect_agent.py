from agents.base_agent import Agent
from utils import task_utils
from prompts.prompt_builder import PromptBuilder
from schemas.architect_schema import architect_output_schema
from typing import Any, Dict
import json

class ArchitectAgent(Agent):

    def _get_pending_task(self) -> dict:
        """Retrieve the first pending task for the architect."""
        try:
            return task_utils.get_first_pending_task(self.state, self.role)
        except ValueError as e:
            # Handle the case where no pending tasks are found
            self.log_event("error", f"No pending tasks found: {str(e)}")
            return None  # or some default task structure, depending on your needs

    def invoke(self, user_request: str) -> Dict[str, Any]:
        self.log_event("start", "")

        pending_task = self._get_pending_task()
        if pending_task is None:
            self.log_event("error", "No pending task available for processing.")
            return self.state  # Early exit or return some default state

        task = json.dumps(pending_task, indent=4)
        self.log_event(
            "info",
            f"I have a pending task: {task}",
        )
        sys_prompt = PromptBuilder.build_architect_prompt(user_request)

        usr_prompt = f"The PM Agent has assigned you the following task: {task}. Please configure the VMs for migration, ensuring network and storage mappings are correctly set, and validate readiness for migration."

        while True:
            self.log_event("info", "⏳ Processing the request...")

            # Invoke the model and process the response
            response_human_message, response_content = self.invoke_model(
                sys_prompt, usr_prompt
            )

            # Validate the model output
            is_valid, validation_message = self.validate_model_output(
                response_content, architect_output_schema
            )

            if is_valid:
                self.log_event("finished", "")
                return self.state
            else:
                # Log the invalid output and provide feedback
                self.log_event(
                    "error", f"❌ Invalid output received: {validation_message}"
                )
                feedback_value = f"Invalid response: {validation_message}. Please correct and try again."

                sys_prompt = PromptBuilder.build_architect_prompt(user_request)
                # Update the prompt with feedback
                sys_prompt = PromptBuilder.build_planner_prompt(
                    user_request, feedback_value
                )

                # Retry the request with feedback
                self.log_event(
                    "info", f"Retrying the request with feedback: {feedback_value}"
                )

from agents.base_agent import Agent
from utils import task_utils
from prompts.prompt_builder import PromptBuilder
from typing import Any, Dict

class ArchitectAgent(Agent):

    def _get_pending_task(self) -> dict:
        """Retrieve the first pending task for the architect."""
        try:
            return task_utils.get_first_pending_task(self.state, "architect")
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

        sys_prompt = PromptBuilder.build_architect_prompt(user_request)

        usr_prompt = pending_task

        self.log_event("info", "⏳ Processing the request...")

        # Invoke the model and process the response
        response_human_message, response_content = self.invoke_model(
            sys_prompt, usr_prompt
        )

        self.log_event("finished", "")

        return self.state

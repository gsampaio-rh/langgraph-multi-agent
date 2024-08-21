from agents.base_agent import Agent
from state.agent_state import (
    get_first_entry_from_state,
    get_all_entries_from_state,
)
from schemas.pm_schema import pm_output_schema
from utils import task_utils
from typing import Any, Dict
from builders.prompt_builder import PromptBuilder

class PMAgent(Agent):

    def construct_user_prompt(self, user_request: str, tasks_list: Any) -> str:
        if not tasks_list or tasks_list == "":
            self.log_event("info", "📝 Task list is empty. Starting from scratch...")
            return f"The task list is currently empty. This is the user_request: {user_request}. Please create an initial task plan based on the original project requirements."

        self.log_event("info", f"Now I have the last task list: {tasks_list}.")
        all_reviewer_responses = get_all_entries_from_state(
            self.state, "reviewer_response"
        )

        if not all_reviewer_responses or all_reviewer_responses == "":
            self.log_event(
                "info",
                "🟡 Not all tasks are completed but the reviewer didn't send any response yet.",
            )
            return "Some tasks remain incomplete, but no feedback has been provided by the reviewer. No updates are required at this time."

        self.log_event(
            "info", f"Now I have the reviewer responses: {all_reviewer_responses}."
        )
        return f"The reviewer has provided feedback on the tasks. Please update the task list accordingly with the following details: {all_reviewer_responses}"

    def invoke(self, user_request: str,) -> Dict:
        """
        Invoke the PM agent by processing the agent request and generating a response.

        Parameters:
        - user_request (str): The user request that the agent should process.

        Returns:
        - dict: The updated state after the PM agent's invocation.
        """
        self.log_event("start")

        original_plan = get_first_entry_from_state(self.state, "planner_response")
        if not original_plan:
            error_message = (
                "Original plan not found. Cannot proceed without the initial plan."
            )
            self.log_event("error", error_message)
            return {"error": error_message}

        # self.log_event(
        #     "info",
        #     message=f"Now I have the plan {original_plan.content}.",
        # )

        tasks_list = task_utils.get_tasks_list(self.state)

        usr_prompt = self.construct_user_prompt(user_request, tasks_list)
        self.log_event("info", usr_prompt)
        sys_prompt = PromptBuilder.build_pm_prompt(original_plan, tasks_list)

        while True:
            self.log_event("info", "⏳ Processing the request...")

            # Invoke the model and process the response
            response_human_message, response_content = self.invoke_model(
                sys_prompt, usr_prompt
            )

            # Validate the model output
            is_valid, json_response, validation_message = self.validate_model_output(
                response_content, pm_output_schema
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

                # Update the prompt with feedback
                sys_prompt = PromptBuilder.build_pm_prompt(
                    original_plan, tasks_list, feedback_value
                )

                # Retry the request with feedback
                self.log_event(
                    "info", f"Retrying the request with feedback: {feedback_value}"
                )

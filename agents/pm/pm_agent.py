from agents.base_agent import Agent
from state.agent_state import (
    get_first_entry_from_state,
    get_all_entries_from_state, 
    get_last_entry_from_state,
)
from typing import Any, Dict
from prompts.prompt_builder import PromptBuilder

class PMAgent(Agent):

    def get_task_list(self) -> Any:
        return get_last_entry_from_state(self.state, "manager_response")

    def construct_user_prompt(self, user_request: str, task_list: Any) -> str:
        if not task_list or task_list == "":
            self.log_event("info", "📝 Task list is empty. Starting from scratch...")
            return f"The task list is currently empty. This is the user_request: {user_request}. Please create an initial task plan based on the original project requirements."

        self.log_event("info", f"Now I have the last task list: {task_list.content}.")
        all_reviewer_responses = get_all_entries_from_state(
            self.state, "reviewer_response"
        )

        if not all_reviewer_responses or all_reviewer_responses == "":
            self.log_event(
                "info",
                "🟡 Not all tasks are done but the reviewer didn't send any response yet.",
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

        task_list = self.get_task_list()

        usr_prompt = self.construct_user_prompt(user_request, task_list)
        sys_prompt = PromptBuilder.build_pm_prompt(original_plan, task_list)
        payload = self.prepare_payload(sys_prompt, usr_prompt)

        while True:
            self.log_event("info","⏳ Processing the request..." )
            # Invoke the model and process the response
            response_json = self.invoke_model(payload)
            if "error" in response_json:
                return response_json

            response_formatted, response_content = self.process_model_response(
                response_json
            )

            self.update_state("manager_response", response_formatted)
            self.log_event("info", message=response_content)
            self.log_event("finished", )
            return self.state

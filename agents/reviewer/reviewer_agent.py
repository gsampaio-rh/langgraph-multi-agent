from agents.base_agent import Agent
from utils import task_utils
from typing import Dict, Any
from builders.prompt_builder import PromptBuilder
from state.agent_state import get_last_entry_from_state
from schemas.reviewer_schema import task_completion_schema

class ReviewerAgent(Agent):

    def get_agent_last_update_and_original_task(self, task):
        agent_name = task["agent"]

        # Get the last update from the agent
        agent_last_update = get_last_entry_from_state(
            self.state, 
            f"{agent_name}_response"
        )
        if not agent_last_update:
            self.log_event(
                "warning",
                f"No updates found for agent {agent_name}. Skipping task.",
            )

        self.log_event(
            "info", f"Now I have the last {agent_name} list: {agent_last_update}."
        )

        task_id = agent_last_update.get("task_id")
        if not task_id or task_id != task["task_id"]:
            self.log_event(
                "warning",
                f"Task ID mismatch for agent {agent_name}. Skipping task.",
            )

        self.log_event(
            "info", f"Now I have the task id: {task_id}."
        )

        # Fetch the task directly by its ID
        original_task = task_utils.get_task_by_id(self.state, task_id)

        self.log_event("info", f"Now I have the original task: {original_task}.")

        # Process the agent's update (e.g., evaluate or validate)
        self.log_event(
            "info",
            f"Reviewing task {original_task['task_name']} from agent {agent_name}.",
        )
        return agent_last_update, original_task

    def invoke(self, user_request: str, agent_update: str) -> Dict[str, Any]:
        """
        Invoke the Reviewer Agent to review pending tasks and process agent updates.

        Parameters:
        - user_request (str): The user request that the agent should process.
        - agent_update (str): The update provided by another agent that the Reviewer should evaluate.

        Returns:
        - dict: The updated state after the Reviewer Agent's invocation.
        """

        self.log_event("start", f" the user_request: {user_request}")

        try:
            # Get the list of tasks
            tasks_list = task_utils.get_tasks_list(self.state)

            # Iterate over each pending task
            for task in tasks_list:
                if task["status"] == "pending":

                    agent_last_update, original_task = (
                        self.get_agent_last_update_and_original_task(task)
                    )

                    # Build the system prompt using the PromptBuilder
                    sys_prompt = PromptBuilder.build_reviewer_prompt(original_task)

                    # Prepare the agent's prompt
                    usr_prompt = f"Agent Update: {agent_last_update}"

                    while True:
                        self.log_event("info", "⏳ Processing the request...")
                        # Invoke the model and process the response

                        response_human_message, response_content = self.invoke_model(
                            sys_prompt, usr_prompt
                        )

                        # Validate the model output
                        is_valid, json_response, validation_message = (
                            self.validate_model_output(
                                response_content, task_completion_schema
                            )
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
                            sys_prompt = PromptBuilder.build_reviewer_prompt(
                                original_task, feedback_value
                            )

                            # Retry the request with feedback
                            self.log_event(
                                "info", f"Retrying the request with feedback: {feedback_value}"
                            )

        except Exception as e:
            error_message = f"❌ Error occurred: {str(e)}"
            self.log_event("error", error_message)
            return {"error": error_message}

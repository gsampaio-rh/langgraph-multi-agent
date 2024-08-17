from agents.base_agent import Agent
from utils import task_utils
from utils import tools_utils
from prompts.prompt_builder import PromptBuilder
from schemas.architect_schema import architect_output_schema
from schemas.task_schema import execute_step_output_schema
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
            return None

    def _get_next_pending_step(self, task_plan: list) -> dict:
        """Retrieve the next pending step in the task plan."""
        for step in task_plan:
            if step['status'] == 'pending':
                return step
        return None

    def _update_step_status(self, task_plan: list, step_name: str, new_status: str):
        """Update the status of a specific step in the task plan."""
        for step in task_plan:
            if step['step_name'] == step_name:
                step['status'] = new_status
                break

    def _generate_task_plan(self, user_request: str, pending_task: dict) -> list:
        """
        Generates a valid task plan using the model. Loops until a valid plan is returned.
        """
        task = json.dumps(pending_task, indent=4)
        self.log_event("info", f"I have a pending task: {task}")

        while True:

            # Build the prompts for the plan generation phase
            sys_prompt = PromptBuilder.build_architect_plan_prompt(user_request)
            usr_prompt = f"The PM Agent has assigned you the following task: {task}. Please generate a plan."

            # Invoke the model for plan generation
            self.log_event("info", "⏳ Generating the task plan...")
            plan_response_message, plan_response_content = self.invoke_model(
                sys_prompt, usr_prompt
            )

            # Validate the plan response
            is_valid, json_response, validation_message = self.validate_model_output(
                plan_response_content, architect_output_schema
            )

            if is_valid:
                self.log_event("info", "✅ Valid task plan generated.")
                return json_response.get("task_plan", [])

            # Log feedback and retry
            self.log_event("error", f"❌ Invalid task plan: {validation_message}")
            feedback_value = f"Invalid response: {validation_message}. Please correct and try again."
            sys_prompt = PromptBuilder.build_architect_plan_prompt(user_request, feedback_value)
            self.log_event("info", f"Retrying task plan generation with feedback: {feedback_value}")

    def _execute_task_plan(self, user_request: str, task_plan: list) -> None:
        """
        Executes the task plan step-by-step by invoking the corresponding tools.
        """
        # Initialize the scratchpad
        scratchpad = []

        while True:

            next_step = self._get_next_pending_step(task_plan)
            if next_step is None:
                self.log_event("info", "All steps have been completed.")
                self.log_event("finished", "Task completed successfully.")
                return scratchpad

            # Retrieve details for the next step
            step_name = next_step["step_name"]
            tool_needed = next_step["tool_needed"]
            description = next_step["description"]

            self.log_event("info", f"Processing step: {step_name}")
            sys_prompt = PromptBuilder.build_architect_execute_prompt(
                task_plan,
                tool_needed,
                tools_utils.get_vsphere_tool_description(tool_needed),
            )
            usr_prompt = f"Task Step: {step_name} - {description}. Use the {tool_needed} tool to complete this step."

            # Invoke the model for the current step
            self.log_event("info", "⏳ Invoking the model for the current step...")
            response_human_message, response_content = self.invoke_model(
                sys_prompt, usr_prompt
            )

            # Validate the model's response for the current step
            is_valid, json_response, validation_message = self.validate_model_output(
                response_content, execute_step_output_schema
            )

            if is_valid:
                self.log_event("info", f"Step '{step_name}' completed successfully.")
                self._update_step_status(task_plan, step_name, "done")
                scratchpad.append(
                    {
                        "step_name": step_name,
                        "tool_used": tool_needed,
                        "result": response_content,
                        "status": "done"
                    }
                )
            else:
                self.log_event("error", f"❌ Invalid output for step '{step_name}': {validation_message}")
                feedback_value = f"Invalid response: {validation_message}. Please correct and try again."
                scratchpad.append(
                    {
                        "step_name": step_name,
                        "tool_used": tool_needed,
                        "result": response_content,
                        "status": "retry",
                    }
                )

                sys_prompt = PromptBuilder.build_architect_execute_prompt(
                    task_plan,
                    tool_needed,
                    tools_utils.get_vsphere_tool_description(tool_needed),
                    scratchpad=scratchpad,
                )
                self.log_event("info", f"Retrying step '{step_name}' with feedback: {feedback_value}")

    def invoke(self, user_request: str) -> Dict[str, Any]:
        """
        Main invoke method that handles plan generation and task execution.
        """
        self.log_event("start", "Invoking the Architect Agent.")

        # Step 1: Retrieve the pending task from the state
        pending_task = self._get_pending_task()
        if pending_task is None:
            self.log_event("error", "No pending task available for processing.")
            return self.state  # Early exit if no pending task is found

        # Step 2: Generate a valid task plan by invoking the model
        task_plan = self._generate_task_plan(user_request, pending_task)

        # Step 3: If no valid task plan is received, exit early
        if not task_plan:
            self.log_event("error", "No valid task plan generated.")
            return self.state

        # Step 4: Execute the task plan step by step
        self._execute_task_plan(user_request, task_plan)

        return self.state

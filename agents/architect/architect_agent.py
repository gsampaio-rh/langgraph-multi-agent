from agents.base_agent import Agent
from utils import task_utils
from utils import tools_utils
from prompts.prompt_builder import PromptBuilder
from schemas.architect_schema import architect_output_schema
from schemas.task_schema import execute_step_output_schema
from typing import Any, Dict
import json
from custom_tools.tool_invoker import invoke_tool
from custom_tools.tool_registry import get_tool_by_name

class ArchitectAgent(Agent):

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
        """Iterates over the task plan and processes each step."""
        scratchpad = []

        for step in task_plan:
            # Process each step until its status is "done"
            if step["status"] == "pending":
                self._process_step(user_request, step, task_plan, scratchpad)

        self.log_event("info", "All steps have been completed.")
        self.log_event("finished", "Task completed successfully.")

    def _process_step(self, user_request: str, step: dict, task_plan: list, scratchpad: list):
        """Processes a single step by reasoning on actions and invoking the model iteratively until the model reports the task is done."""
        step_name = step["step_name"]
        tool_needed = step["tool_needed"]
        description = step["description"]

        while step["status"] != "done":
            self.log_event("info", f"Processing step: {step_name}")

            # Build prompts for this step
            sys_prompt = PromptBuilder.build_architect_execute_prompt(
                task_plan,
                tool_needed,
                tools_utils.get_vsphere_tool_description(tool_needed)
            )
            usr_prompt = f"Task Step: {step_name} - {description}. Use the {tool_needed} tool to complete this step."

            # Invoke the model to reason through this step
            self.log_event("info", "⏳ Invoking the model for the current step...")
            response_human_message, response_content = self.invoke_model(sys_prompt, usr_prompt)

            # Validate the model's output for this step
            is_valid, json_response, validation_message = self.validate_model_output(
                response_content, execute_step_output_schema
            )

            if is_valid:
                # Check the model's output for the status of the step
                step_status = json_response.get("status", "pending")

                if step_status == "done":
                    # If the model indicates that the task is done, mark the step as done
                    self.log_event("info", f"Step '{step_name}' completed successfully.")
                    step["status"] = "done"
                    scratchpad.append({"step_name": step_name, "result": json_response, "status": "done"})
                else:
                    # Otherwise, continue reasoning and retry
                    # If the task is not done, check for suggested tool and input
                    suggested_tool = json_response.get("tool")
                    suggested_tool_input = json_response.get("tool_input")

                    if suggested_tool and suggested_tool_input:
                        self.log_event("info", f"Model suggested tool '{suggested_tool}' with input '{suggested_tool_input}' for step '{step_name}'.")

                        # Get the tool from the registry
                        tool = get_tool_by_name(suggested_tool)
                        if tool:
                            try:
                                # Invoke the tool using the provided input
                                tool_result = invoke_tool(tool, **suggested_tool_input)
                                self.log_event("info", f"Tool '{suggested_tool}' executed successfully for step '{step_name}'.")

                                # Update the scratchpad with the tool's result
                                scratchpad.append({
                                    "step_name": step_name,
                                    "suggested_tool": suggested_tool,
                                    "tool_input": suggested_tool_input,
                                    "tool_result": tool_result,
                                    "status": "in_progress"
                                })

                            except Exception as e:
                                # Handle tool execution failure
                                self.log_event("error", f"Tool execution failed for step '{step_name}': {str(e)}")
                                scratchpad.append({
                                    "step_name": step_name,
                                    "suggested_tool": suggested_tool,
                                    "tool_input": suggested_tool_input,
                                    "result": str(e),
                                    "status": "retry"
                                })
                                self._update_step_status(task_plan, step_name, "pending")
                    else:
                        self.log_event("info", f"Step '{step_name}' is still in progress. Waiting for completion.")
                        scratchpad.append({"step_name": step_name, "result": json_response, "status": "in_progress"})

            else:
                # Handle invalid model output by providing feedback and retrying
                self.log_event("error", f"❌ Invalid output for step '{step_name}': {validation_message}")
                feedback_value = f"Invalid response: {validation_message}. Please correct and try again."
                scratchpad.append({"step_name": step_name, "result": response_content, "status": "retry"})

                sys_prompt = PromptBuilder.build_architect_execute_prompt(
                    task_plan,
                    tool_needed,
                    tools_utils.get_vsphere_tool_description(tool_needed),
                    scratchpad=scratchpad,
                )
                self.log_event("info", f"Retrying step '{step_name}' with feedback: {feedback_value}")

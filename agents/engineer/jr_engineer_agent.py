from agents.base_agent import Agent
from builders.prompt_builder import PromptBuilder
from utils import task_utils
from typing import Any, Dict, List
from schemas.engineer_schema import (
    engineer_output_schema,
    engineer_reflection_output_schema,
)
import json


class JrEngineerAgent(Agent):

    def invoke(self, user_request: str) -> Dict[str, Any]:
        """Main invoke method to handle plan generation and task execution."""
        self.log_event("start", "")

        # Retrieve all pending tasks from TaskManager
        self.task_manager.tasks = task_utils.get_pending_tasks(self.state, self.role)

        if not self.task_manager.has_pending_tasks():
            self.log_event("info", "✅ All tasks are completed.")
            return self.state

        # Process each pending task one by one
        while self.task_manager.has_pending_tasks():
            for task in self.task_manager.tasks:
                task_id = task.get("task_id", "N/A")
                task_name = task.get("task_name", "Unnamed Task")

                self.log_event(
                    "info",
                    f"\n\n### 📝 Working on Task ID: {task_id} - {task_name}\n\n",
                )
                self.process_task(task)

        return self.state

    def process_task(self, task: Dict[str, Any]):
        """Process a single task by going through the think, act, and reflect phases."""
        task_id = task.get("task_id", "N/A")
        task_name = task.get("task_name", "Unnamed Task")

        # Log the start of task processing
        self.log_event("info", f"### 📝 Starting Task ID: {task_id} - {task_name}")
        scratchpad = []

        # Keep track of whether reflection succeeds
        iteration_count = 0
        max_iterations = 5  # Ensure we don't loop indefinitely

        while iteration_count < max_iterations:
            iteration_count += 1
            self.log_event("info", f"🔄 Iteration {iteration_count} for Task ID: {task_id}")

            # Step 1: Think phase
            self.log_event("info", f"🔍 [THINK] Initiating the Think phase for Task ID: {task_id}")
            think_response, think_human_message = self.think_phase(task, scratchpad)

            scratchpad.append(think_human_message)

            # Step 2: Act phase
            self.log_event("info", f"🛠️ [ACT] Initiating the Act phase for Task ID: {task_id}")
            success, act_usr_prompt = self.act_phase(think_response)

            if not success:
                scratchpad.append(f"[ACT] Action failed in Act phase. Please reflect on next stes for task {task_name}.")

            # Step 3: Reflect phase
            self.log_event("info", f"💭 [REFLECT] Initiating the Reflect phase for Task ID: {task_id}")
            reflect_response, reflect_human_message = self.reflect_phase(
                task, scratchpad, act_usr_prompt
            )

            scratchpad.append(reflect_human_message)

            # Step 4: Process Reflection
            reflection_success = self._process_reflection_result(task, reflect_response)

            if reflection_success:
                self.log_event("info", "Final answer generated.")
                act_dict = json.loads(act_usr_prompt)
                reflect_output = {
                    "task_id": task.get("task_id"),
                    "final_thought": reflect_response.get("final_thought"),
                    "action": think_response.get("action"),
                    "action_result": act_dict.get("action_result"),
                    "action_final_status": act_dict.get("tool_result_success"),
                }
                self.update_state(f"{self.role}_response", reflect_output)
                self.log_event("info", f"✅ Task ID: {task_id} - {task_name} completed successfully after {iteration_count} iterations.")
                break  # Break the loop when reflection succeeds
            else:
                self.log_event("warning", f"Task ID: {task_id} - {task_name} not completed yet. Continuing to next iteration.")

        # Log the completion of the task process
        self.log_event("info", f"✅ Task ID: {task_id} - {task_name} processed successfully.")

    def _build_system_prompt(
        self, pending_task: dict, scratchpad: list, is_reflecting: bool = False
    ) -> str:
        """
        Build the system prompt for thinking or reflecting, based on task details and scratchpad history.
        """
        if is_reflecting:
            return PromptBuilder.build_engineer_reflect_prompt(
                task=pending_task.get("task_name"),
                task_description=pending_task.get("task_description"),
                acceptance_criteria=pending_task.get("acceptance_criteria"),
                scratchpad=scratchpad,
            )
        else:
            return PromptBuilder.build_engineer_prompt(
                task=pending_task.get("task_name"),
                task_description=pending_task.get("task_description"),
                acceptance_criteria=pending_task.get("acceptance_criteria"),
                tool_names=self.tool_names,
                tool_descriptions=self.tool_descriptions,
                scratchpad=scratchpad,
            )

    def think_phase(self, task: dict, scratchpad: list) -> Dict[str, Any]:
        """
        Execute the thinking phase by invoking the model to generate the plan.
        """
        sys_prompt = self._build_system_prompt(task, scratchpad, is_reflecting=False)
        usr_prompt = f"Solve this task: {task.get('task_name')}"

        response_human_message, response_content = self.invoke_model(
            sys_prompt, usr_prompt
        )
        is_valid, think_response, validation_message = self.validate_model_output(
            response_content, engineer_output_schema
        )

        if is_valid:
            return think_response, response_human_message
        else:
            self.log_event(
                "error",
                f"❌ Invalid output received during thinking: {validation_message}",
            )
            return f"❌ Invalid output received during thinking: {validation_message}", None

    def act_phase(self, think_response: Dict[str, Any]) -> (bool, str):
        """Execute the action phase using the specified tool and return the usr_prompt for reflection."""
        tool = think_response.get("action")
        tool_input = think_response.get("action_input")

        # Invoke the tool
        result = self.tool_manager.invoke_tool(tool, tool_input)

        if result.get("success"):
            tool_result = result["result"]
            self.log_event("info", f"🪛 Tool '{tool}' executed successfully.")
            self.log_event("info", json.dumps(tool_result, indent=4))

            # Return usr_prompt in the specified format
            usr_prompt = json.dumps(
                {
                    "action": tool,
                    "action_result": str(tool_result),
                    "tool_result_success": True,
                },
                indent=4,
            )
            return True, usr_prompt
        else:
            tool_result = f"{result['error']}: {result['details']}"
            self.log_event("error", json.dumps(result, indent=4))

            # Return usr_prompt with tool failure information
            usr_prompt = json.dumps(
                {
                    "action": tool,
                    "action_result": str(tool_result),
                    "tool_result_success": False,
                },
                indent=4,
            )
            return False, usr_prompt

    def reflect_phase(self, task: Dict[str, Any], scratchpad: List[str], usr_prompt: str):
        """Execute the reflection phase based on the tool's result."""
        sys_prompt = self._build_system_prompt(task, scratchpad, is_reflecting=True)

        # Log the reflection
        self.log_event("info", usr_prompt)

        # Invoke the model for reflection
        response_human_message, response_content = self.invoke_model(sys_prompt, usr_prompt)

        # Validate the reflection response
        is_valid, reflection_response, validation_message = self.validate_model_output(response_content, engineer_reflection_output_schema)

        if is_valid:
            self.log_event("info", "Reflection completed successfully.")
            self.log_event("info", json.dumps(reflection_response, indent=4))
            return reflection_response, response_human_message
        else:
            self.log_event(
                "error",
                f"❌ Invalid output received during reflecting: {validation_message}",
            )
            return f"❌ Invalid output received during reflecting: {validation_message}", None

    def _process_reflection_result(
        self, task: dict, reflection_result: Dict[str, Any]
    ) -> bool:
        """
        Process the result of the reflection to determine if the task is complete or requires further steps.
        """
        if reflection_result:
            if "final_answer" in reflection_result:
                self.task_manager.update_task_status(task.get("task_id"), "completed")
                self.log_event(
                    "info", f"✅ Task '{task.get('task_name')}' completed successfully."
                )
                return True
            else:
                self.task_manager.update_task_status(task.get("task_id"), "failed")
                self.log_event(
                    "warning",
                    f"Task '{task.get('task_name')}' not yet completed. Further action required.",
                )
                return False
        else:
            self.log_event(
                "error",
                "❌ Reflection result is invalid, unable to process task completion.",
            )
            return False

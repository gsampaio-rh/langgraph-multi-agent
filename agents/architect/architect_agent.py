from agents.base_agent import Agent
from utils import task_utils
from prompts.prompt_builder import PromptBuilder
from typing import Any, Dict
import json
from custom_tools.tool_invoker import invoke_tool
from custom_tools.tool_registry import get_tool_by_name

class ArchitectAgent(Agent):

    def invoke(self, user_request: str) -> Dict[str, Any]:
        """Main invoke method to handle plan generation and task execution."""
        self.log_event("start", "")
        pending_task = self._get_pending_task()

        if not pending_task:
            self.log_event("error", "No pending task available.")
            return self.state

        # Continuously reason and act on the task until a final answer is reached.
        self._reason_and_act(user_request, pending_task)

        return self.state

    def _get_pending_task(self) -> dict:
        """Retrieve the first pending task for the architect."""
        try:
            return task_utils.get_first_pending_task(self.state, self.role)
        except ValueError as e:
            # Handle the case where no pending tasks are found
            self.log_event("error", f"No pending tasks found: {str(e)}")
            return None

    def _thinking(self, sys_prompt: str, usr_prompt: str) -> dict:
        """
        Generate a task plan using the model and return the parsed response.
        """
        self.log_event("info", "💭 Thinking...")
        response_message, response_content = self.invoke_model(sys_prompt, usr_prompt)

        try:
            return json.loads(response_content), response_message
        except json.JSONDecodeError as e:
            self.log_event("error", f"Failed to decode JSON response: {e}")
            return None

    def _reason_and_act(self, user_request: str, pending_task: dict) -> None:
        """
        Iteratively reason and act until a valid task plan with a final answer is generated.
        """
        usr_prompt = f"Solve this task: {pending_task.get('task_name')}"
        scratchpad = []
        sys_prompt = PromptBuilder.build_react_prompt(
            task=pending_task.get("task_name"),
            task_description=pending_task.get("task_description"),
            acceptance_criteria=pending_task.get("acceptance_criteria"),
        )

        previous_response = None  # To track repeated outputs
        iteration_limit = 3  # Set a limit for the number of times to allow repeated responses

        while True:
            # print(usr_prompt)
            # print(sys_prompt)
            think_response, think_message = self._thinking(sys_prompt, usr_prompt)

            if not think_response:
                continue  # Retry on invalid plan

            scratchpad.append(str(think_message))

            # Detect repeated reasoning responses
            if think_response == previous_response:
                iteration_limit -= 1
                self.log_event(
                    "warning",
                    f"Repeated output detected. Remaining attempts: {iteration_limit}",
                )

                if iteration_limit <= 0:
                    self.log_event(
                        "error",
                        "Reasoning stuck in a loop. Forcing a retry or an alternative approach.",
                    )
                    usr_prompt = "You keep repeating the same reasoning. Please act now or provide more specific details."
                    iteration_limit = 3  # Reset the limit for the next cycle
                else:
                    continue  # Retry the reasoning

            if suggested_tool and tool_input:
                success = self._execute_tool(suggested_tool, tool_input)
                usr_prompt = {"action": suggested_tool, "success": success}

            if final_answer := think_response.get("final_answer"):
                self.log_event("info", "Final answer generated.")
                return final_answer

            suggested_tool = think_response.get("action")
            tool_input = think_response.get("action_input")

            # Update system prompt with the scratchpad history
            sys_prompt = PromptBuilder.build_react_prompt(
                task=pending_task.get("task_name"),
                task_description=pending_task.get("task_description"),
                acceptance_criteria=pending_task.get("acceptance_criteria"),
                scratchpad=scratchpad,
            )

    def _execute_tool(self, tool_name: str, tool_input: dict) -> bool:
        """
        Execute the suggested tool and return whether it was successful.
        """
        self.log_event("info", f"Executing tool '{tool_name}' with input {tool_input}.")

        tool = get_tool_by_name(tool_name)
        if not tool:
            self.log_event("error", f"Tool '{tool_name}' not found.")
            return False

        try:
            invoke_tool(tool, **tool_input)
            self.log_event("info", f"Tool '{tool_name}' executed successfully.")
            return True
        except Exception as e:
            self.log_event("error", f"Tool execution failed: {e}")
            return False

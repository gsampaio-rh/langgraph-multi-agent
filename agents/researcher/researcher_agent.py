from typing import Any, Dict
from agents.base_agent import Agent
from utils import task_utils, tool_handler
from custom_tools.tool_invoker import ToolInvoker 
from custom_tools import (
    custom_tools,
)
from prompts.prompt_builder import PromptBuilder
import json

# Initialize the ToolInvoker outside the class
tool_invoker = ToolInvoker(custom_tools)

class ResearcherAgent(Agent):

    def _log_user_prompt(self, usr_prompt: str) -> None:
        """
        Logs the user prompt in a pretty-printed format for better readability.
        """
        try:
            usr_prompt_dict = json.loads(usr_prompt)
            pretty_usr_prompt = json.dumps(usr_prompt_dict, indent=4)
            self.log_event("processing", "User Prompt:")
            self.log_event("processing", pretty_usr_prompt)
        except json.JSONDecodeError as e:
            self.log_event("error", f"Invalid JSON string provided: {str(e)}")
            self.log_event("processing", f"User Prompt -> {usr_prompt}")

    def _get_pending_task(self) -> dict:
        """Retrieve the first pending task for the researcher."""
        return task_utils.get_first_pending_task(self.state, "researcher")

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the researcher agent."""
        return PromptBuilder.build_researcher_prompt()

    def _handle_invocation_error(self, error: ValueError) -> Dict[str, Any]:
        """Handle errors during the invocation."""
        error_message = f"Error during invocation: {str(error)}"
        self.log_event("error", error_message)
        self.update_state("researcher_response", error_message)
        return {"error": error_message}

    def _process_tool_action(self, response_content: Dict[str, Any], pending_task: dict, state_key: str) -> tuple:
        """Process tool actions and return the tool result and usage status."""
        try:
            tool_result, used_tool = tool_handler.process_tool_action(response_content, pending_task, state_key, self)
            return tool_result, used_tool
        except Exception as e:
            self.log_event("error", f"Error during tool invocation: {str(e)}")
            return {"error": str(e)}, False

    def _update_user_prompt(self, tool_result: Any) -> str:
        """Update the user prompt based on the tool result."""
        return json.dumps({"observation": str(tool_result)})

    def _update_system_prompt(self, scratchpad: str) -> str:
        """Update the system prompt with the scratchpad."""
        return PromptBuilder.build_researcher_prompt(scratchpad=scratchpad)

    def update_scratchpad(
        self, response_content: Dict[str, Any], usr_prompt: str, scratchpad: str
    ) -> str:
        """
        Update the scratchpad with the user prompt and the model's response.
        """

        scratchpad_dict = {
            "user": usr_prompt,
            "response": response_content,
        }
        # Convert to a valid JSON string
        scratchpad_json = json.dumps(scratchpad_dict)

        # If you need to append this to an existing scratchpad string
        scratchpad += scratchpad_json
        return scratchpad

    def is_final_step(self, response_content: Dict[str, Any], used_tool: bool) -> bool:
        """
        Determine if the loop has reached its final step based on the response content, tool usage,
        and the absence of meaningful 'action' and 'action_input' (which can be None, null, or empty).
        """
        response_dict = json.loads(response_content)

        # Check for final elements and absence of action-related elements
        has_final_elements = (
            "observation" in response_dict or "final_answer" in response_dict
        )
        lacks_action_elements = not response_dict.get(
            "action"
        ) and not response_dict.get("action_input")

        return used_tool and has_final_elements and lacks_action_elements

    def create_researcher_user_prompt(self, task: dict) -> Dict[str, Any]:
        """
        Create a dictionary for the user prompt based on the task information.
        """
        usr_prompt_dict = {
            "task_id": task["task_id"],
            "task_description": task["task_description"],
            "acceptance_criteria": task["acceptance_criteria"],
            "tools_to_use": task["tools_to_use"],
            "tools_not_to_use": task.get("tools_not_to_use", "None"),
        }

        return json.dumps(usr_prompt_dict)

    def invoke(self, user_request: str) -> Dict[str, Any]:
        self.log_event("start", "")

        try:

            pending_task = self._get_pending_task()

            sys_prompt = self._build_system_prompt()

            usr_prompt = self.create_researcher_user_prompt(pending_task)

            response_content, used_tool, tool_result = self.process_react_tools_loop(sys_prompt, usr_prompt, pending_task)

            return self.finalize_response(
                pending_task, response_content, used_tool, tool_result
            )

        except ValueError as e:
            return self._handle_invocation_error(e)

    def process_react_tools_loop(
        self, 
        sys_prompt: str, 
        usr_prompt: str, 
        pending_task: dict, 
        state_key: str = "researcher_response",
        max_loops: int = 15
    ) -> Dict[str, Any]:
        """
        Process the request in a loop, invoking tools and updating the state.
        """
        loop_count = 0
        used_tool = False
        scratchpad = ""
        tool_result = None

        while loop_count < max_loops:
            loop_count += 1

            # Log the user prompt at the start of each loop iteration
            self._log_user_prompt(usr_prompt)

            response_human_message, response_content = self.invoke_model(sys_prompt, usr_prompt)

            # Update the scratchpad with the new information
            scratchpad = self.update_scratchpad(response_content, usr_prompt, scratchpad)

            # Check if we've reached the final step
            if self.is_final_step(response_content, used_tool):
                return response_content, used_tool, tool_result

            tool_result, used_tool = self._process_tool_action(
                response_content, pending_task, state_key
            )

            # Update the user prompt for the next loop iteration based on the tool result
            if tool_result:
                usr_prompt = self._update_user_prompt(tool_result)

            # Update the system prompt with the latest scratchpad before next loop
            sys_prompt = self._update_system_prompt(scratchpad)

        self.log_event("info", f"Loop limit of {max_loops} reached. Returning the current state.")
        return response_content, used_tool, tool_result

    def finalize_response(
        self,
        pending_task: dict,
        response_content: Dict[str, Any],
        used_tool: bool,
        tool_result: Any
    ) -> Dict[str, Any]:
        """
        Finalize the response by processing the final thought and answer.
        This method ensures that the final response is logged, the state is updated, and the process ends cleanly.
        """
        # Ensure the response content is properly formatted
        if isinstance(response_content, str):
            try:
                response_content = json.loads(response_content)
            except json.JSONDecodeError as e:
                self.log_event("error", f"Invalid JSON in response: {str(e)}")
                return {"error": f"Invalid JSON in response: {str(e)}"}

        # Convert tool_result to string format for logging
        tool_result_str = str(tool_result) if tool_result else "No tool result"

        # Log final responses
        # self.log_event("info", message=f"Final Response: {response_content}")
        # self.log_event("info", message=f"Tool Result: {tool_result_str}")

        # Prepare the final response dictionary for state update
        final_response = {
            "task_id": pending_task["task_id"],
            "used_tool": used_tool,
            "tool_result": tool_result_str,
            "final_response": response_content,
        }

        # Update the state with the final response
        final_response_json = json.dumps(final_response)
        self.update_state("researcher_response", final_response_json)

        # Log final state update
        self.log_event("info", message=f"Finalized state: {final_response_json}")
        self.log_event("finished")

        return self.state

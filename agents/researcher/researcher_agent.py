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

    def invoke(self, user_request: str) -> Dict[str, Any]:
        self.log_event("start", "")

        try:
            pending_task = task_utils.get_first_pending_task(self.state, "researcher")

            sys_prompt = PromptBuilder.build_researcher_prompt()

            usr_prompt_dict = {
                "task_id": pending_task["task_id"],
                "task_description": pending_task["task_description"],
                "acceptance_criteria": pending_task["acceptance_criteria"],
                "tools_to_use": pending_task["tools_to_use"],
                "tools_not_to_use": pending_task.get("tools_not_to_use", "None"),
            }

            usr_prompt = json.dumps(usr_prompt_dict)

            response_content, used_tool, tool_result = self.process_react_tools_loop(sys_prompt, usr_prompt, pending_task)
            return self.finalize_response(
                pending_task, response_content, used_tool, tool_result
            )

        except ValueError as e:
            error_message = f"Error during invocation: {str(e)}"
            self.log_event("error", error_message)
            self.update_state("researcher_response", error_message)
            return {"error": str(e)}

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

            # Prepare the payload and invoke the model
            try:
                payload = self.prepare_payload(sys_prompt, usr_prompt)
                response_json = self.invoke_model(payload)

                if "error" in response_json:
                    self.log_event("error", f"Model error encountered: {response_json}")
                    return response_json

                # Process and log the model's response
                response_formatted, response_content = self.process_model_response(response_json)

            except Exception as e:
                self.log_event("error", f"Unexpected error during model invocation: {str(e)}")
                return {"error": str(e)}

            # Update the scratchpad with the new information
            scratchpad = self.update_scratchpad(response_content, usr_prompt, scratchpad)

            # Check if we've reached the final step
            if self.is_final_step(response_content, used_tool):
                return response_content, used_tool, tool_result

            # Centralized tool handling: Invoke tools if needed
            try:
                tool_result, used_tool = tool_handler.process_tool_action(response_content, pending_task, state_key, self)
            except Exception as e:
                self.log_event("error", f"Error during tool invocation: {str(e)}")
                return {"error": f"Error during tool invocation: {str(e)}"}

            # Update the user prompt for the next loop iteration based on the tool result
            if tool_result:
                usr_prompt = json.dumps({"observation": str(tool_result)})

            # Update the system prompt with the latest scratchpad before next loop
            sys_prompt = PromptBuilder.build_researcher_prompt(scratchpad=scratchpad)

        self.log_event("info", f"Loop limit of {max_loops} reached. Returning the current state.")
        return response_content, used_tool, tool_result

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
        Determine if the loop has reached its final step based on the response content and tool usage.
        """
        return used_tool and (
            "observation" in response_content or "final_answer" in response_content
        )

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

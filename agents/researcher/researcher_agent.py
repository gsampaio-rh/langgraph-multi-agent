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

            return self.process_request_loop(sys_prompt, usr_prompt, pending_task)

        except ValueError as e:
            error_message = f"Error during invocation: {str(e)}"
            self.log_event("error", error_message)
            self.update_state("researcher_response", error_message)
            return {"error": str(e)}

    def process_request_loop(
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

            try:
                usr_prompt_dict = json.loads(usr_prompt)
                pretty_usr_prompt = json.dumps(usr_prompt_dict, indent=4)
                self.log_event("processing", "User Prompt:")
                self.log_event("processing", pretty_usr_prompt)
            except json.JSONDecodeError as e:
                self.log_event("error", f"Invalid JSON string provided: {str(e)}")
                self.log_event("processing", f"User Prompt -> {usr_prompt}")

            # Prepare the payload and invoke the model
            payload = self.prepare_payload(sys_prompt, usr_prompt)
            response_json = self.invoke_model(payload)

            if "error" in response_json:
                self.log_event("error", f"{response_json}")
                return response_json

            response_content = self.handle_response(response_json, pending_task, scratchpad)

            if self.is_final_step(response_content, used_tool):
                return self.finalize_response(pending_task, response_content, used_tool, tool_result)

            # Use the tool_handler to process actions and tool invocation
            tool_result, used_tool = tool_handler.process_tool_action(response_content, pending_task, state_key, self)

            if tool_result:
                # Log the result and continue processing
                usr_prompt_dict = {
                    "observation": str(tool_result),
                }
                usr_prompt = json.dumps(usr_prompt_dict)

            sys_prompt = PromptBuilder.build_researcher_prompt(scratchpad=scratchpad)

        self.log_event("info", f"Loop limit of {max_loops} reached. Returning the current state.")
        return self.finalize_response(pending_task, response_content, scratchpad, used_tool)

    def handle_response(
        self, response_json: Dict[str, Any], pending_task: dict, scratchpad: str
    ) -> Dict[str, Any]:
        """
        Process the model's response, update the state, and return the content.
        """
        response_formatted, response_content = self.process_model_response(response_json)

        scratchpad_dict = {
            "user": pending_task["task_description"],
            "response": response_content,
        }
        # Convert to a valid JSON string
        scratchpad_json = json.dumps(scratchpad_dict)

        # If you need to append this to an existing scratchpad string
        scratchpad += scratchpad_json
        return response_content

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
        tool_result,
    ) -> Dict[str, Any]:
        """
        Finalize the response by processing the final thought and answer.
        """

        if isinstance(response_content, str):
            try:
                response_content = json.loads(response_content)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON string for action: {response_content}. Error: {str(e)}"
                )

        last_response = response_content
        tool_result = str(tool_result)

        self.log_event("info", message=f"Last Response: {last_response}")
        self.log_event("info", message=f"Tool Result: {tool_result}")

        answer_dict = {
            "task_id": pending_task["task_id"],
            "used_tool": used_tool,
            "tool_result": tool_result,
            "last_response_from_agent": last_response,
        }
        answer_json = json.dumps(answer_dict)
        self.update_state(f"researcher_response", answer_json)
        self.log_event("info", message=answer_json)
        self.log_event("finished")
        return self.state

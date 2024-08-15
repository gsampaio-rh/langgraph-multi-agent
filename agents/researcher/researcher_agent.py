from typing import Any, Dict
from agents.base_agent import Agent
from utils import task_utils
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
            pending_tasks = task_utils.get_pending_tasks(self.state, "researcher")
            # Get the first pending task
            if not pending_tasks:
                raise ValueError("No pending tasks found for the researcher.")

            first_task = pending_tasks[0]  # Access the first task

            validated_task = task_utils.validate_task(first_task)

            sys_prompt = PromptBuilder.build_researcher_prompt()

            usr_prompt_dict = {
                "task_id": validated_task["task_id"],
                "task_description": validated_task["task_description"],
                "acceptance_criteria": validated_task["acceptance_criteria"],
                "tools_to_use": validated_task["tools_to_use"],
                "tools_not_to_use": validated_task.get("tools_not_to_use", "None"),
            }

            usr_prompt = json.dumps(usr_prompt_dict)

            return self.process_request_loop(sys_prompt, usr_prompt, validated_task)

        except ValueError as e:
            error_message = f"Error during invocation: {str(e)}"
            self.log_event("error", error_message)
            self.update_state("researcher_response", error_message)
            return {"error": str(e)}

    def process_request_loop(
        self, sys_prompt: str, usr_prompt: str, validated_task: dict
    ) -> Dict[str, Any]:
        """
        Process the request in a loop, invoking tools and updating the state.
        """
        loop_count = 0
        max_loops = 15
        used_tool = False
        scratchpad = ""

        while loop_count < max_loops:
            loop_count += 1
            self.log_event("processing", f"User Prompt -> {usr_prompt}")

            # Prepare the payload and invoke the model
            payload = self.prepare_payload(sys_prompt, usr_prompt)
            response_json = self.invoke_model(payload)

            # Handle any errors in the response
            if "error" in response_json:
                self.log_event("error", f"{response_json}")
                return response_json

            # Process the model's response and update the state
            response_content = self.handle_response(
                response_json, validated_task, scratchpad
            )

            # Check if we've reached the final step
            if self.is_final_step(response_content, used_tool):
                return self.finalize_response(
                    validated_task, response_content, used_tool, tool_result
                )

            # Invoke the tool if needed and update the user prompt
            tool_result = tool_invoker.find_and_invoke_tool(
                response_content,
            )
            if tool_result is not None:
                used_tool = True
                self.update_state(
                    f"researcher_response",
                    {"task_id": validated_task["task_id"], "tool_result": tool_result},
                )

                usr_prompt_dict = {
                    "observation": str(tool_result),
                }
                print(usr_prompt_dict)
                usr_prompt = json.dumps(usr_prompt_dict)

            # Update the system prompt with the latest scratchpad
            sys_prompt = PromptBuilder.build_researcher_prompt(scratchpad=scratchpad)

        self.log_event(
            "info", f"Loop limit of {max_loops} reached. Returning the current state."
        )
        return self.finalize_response(
            validated_task, response_content, scratchpad, used_tool
        )

    def handle_response(
        self, response_json: Dict[str, Any], validated_task: dict, scratchpad: str
    ) -> Dict[str, Any]:
        """
        Process the model's response, update the state, and return the content.
        """
        response_formatted, response_content = self.process_model_response(response_json)
        self.update_state(f"researcher_response", response_content)
        self.log_event("info", message=response_content)

        scratchpad += f"User Prompt: {validated_task['task_description']}\nResponse: {response_content}\n"
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
        validated_task: dict,
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
            "task_id": validated_task["task_id"],
            "used_tool": used_tool,
            "tool_result": tool_result,
            "last_response_from_agent": last_response,
        }
        answer_json = json.dumps(answer_dict)
        self.update_state(f"researcher_response", answer_json)
        self.log_event("info", message=answer_json)
        self.log_event("finished")
        return self.state

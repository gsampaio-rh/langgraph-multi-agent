import json
from agents.base_agent import Agent
from prompts.prompt_builder import PromptBuilder
from custom_tools.tool_invoker import invoke_tool
from custom_tools.tool_registry import get_tool_by_name


class ReactAgent(Agent):

    def invoke_model_react(self, sys_prompt: str, user_prompt: str):
        """
        Use the ModelService to prepare the payload, invoke the model, and process the response.
        """
        # Prepare the payload using the ModelService
        payload = self.model_service.prepare_payload(sys_prompt, user_prompt)

        # Invoke the model and get the response
        response_json = self.model_service.invoke_model(payload, self.role)

        response_human_message, response_content = (
            self.model_service.process_model_response(response_json, self.role)
        )

        # self.update_state(f"{self.role}_response", response_content)

        # Process the response
        return response_human_message, response_content

    def _thinking(self, sys_prompt: str, usr_prompt: str) -> dict:
        """
        Generate a task plan using the model and return the parsed response.
        """
        self.log_event("info", "💭 Thinking...")
        response_message, response_content = self.invoke_model_react(
            sys_prompt, usr_prompt
        )

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
        iteration_limit = (
            3  # Set a limit for the number of times to allow repeated responses
        )

        success = False
        while True:
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

            if final_answer := think_response.get("final_answer"):

                # Ensure that if there's an action, the tool must be used and result must be valid
                if not success:
                    self.log_event("error", "Final answer attempted but tool was not executed. Rejecting final answer.")
                    usr_prompt = "Final answer attempted but tool was not executed. Rejecting final answer."
                    continue

                final_thought = think_response.get("thought")
                self.log_event("info", "Final answer generated.")
                reason_and_act_output = {
                    "task_id": pending_task.get("task_id"),
                    "suggested_tool": suggested_tool,
                    "action_result": str(tool_result),
                    "final_thought": final_thought,
                }
                print(reason_and_act_output)
                return reason_and_act_output

            suggested_tool = think_response.get("action")
            tool_input = think_response.get("action_input")

            if suggested_tool:
                success, tool_result = self._execute_tool(suggested_tool, tool_input)
                usr_prompt_dict = {
                    "action": suggested_tool, 
                    "action_result": str(tool_result), 
                    "success": success
                }
                usr_prompt = json.dumps(usr_prompt_dict, indent=4)
                print(usr_prompt)

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
        self.log_event("info", f"🔧 Executing tool '{tool_name}' with input {tool_input}.")

        tool = get_tool_by_name(tool_name)
        if not tool:
            error_message = f"❌ Tool '{tool_name}' not found."
            self.log_event("error", error_message)
            return False, error_message

        try:
            tool_result = invoke_tool(tool, **tool_input)
            self.log_event("info", f"🪛 \n '{tool_result}' \n")
            self.log_event("info", f"🪛 Tool '{tool_name}' executed successfully.")
            return True, tool_result
        except Exception as e:
            error_message = f"❌ Tool execution failed: {e}"
            self.log_event("error", error_message)
            return False, error_message

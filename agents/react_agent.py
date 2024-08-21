import json
from agents.base_agent import Agent
from builders.prompt_builder import PromptBuilder

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

    def _handle_repeated_response(
        self,
        think_response: dict,
        previous_response: dict,
        iteration_limit: int,
        pending_task: dict,
    ):
        """
        Handle repeated responses during the reasoning loop.
        """
        if think_response == previous_response:
            iteration_limit -= 1
            self.log_event("warning", f"❌ Repeated output detected. Remaining attempts: {iteration_limit}")

            if iteration_limit <= 0:
                self.log_event("error", "❌ Reasoning stuck in a loop. Forcing a retry or an alternative approach.")
                return {
                    "retry": True,
                    "reset_iteration_limit": True,
                    "new_prompt": f"You keep repeating the same reasoning. Your task is to {pending_task.get('task_name')}. Please act now or provide more specific details."
                }
        return {
            "retry": False,
            "reset_iteration_limit": False,
            "new_prompt": None
        }

    def _handle_tool_result(self, tool_name: str, result: dict) -> (str, bool):
        """
        Handle the tool execution result and log accordingly.
        """
        if result.get("success"):
            tool_result = result["result"]
            self.log_event("info", f"🪛 Tool '{tool_name}' executed successfully.")
            self.log_event("info", json.dumps(tool_result, indent=4))
            return tool_result, True
        else:
            tool_result = f"{result['error']}: {result['details']}"
            self.log_event("error", json.dumps(result, indent=4))
            return tool_result, False

    def _reason_and_act(self, task_checklist: str, pending_task: dict) -> None:
        """
        Iteratively reason and act until a valid task plan with a final answer is generated.
        """
        self.log_event(
            "info",
            f"💬 I am the {self.role} agent and I have access to these tools: {self.tool_names}",
        )
        usr_prompt = f"Solve this task: {pending_task.get('task_name')}"
        scratchpad = []
        sys_prompt = PromptBuilder.build_react_prompt(
            task=pending_task.get("task_name"),
            task_description=pending_task.get("task_description"),
            acceptance_criteria=pending_task.get("acceptance_criteria"),
            tool_names=self.tool_names,
            tool_descriptions=self.tool_descriptions,
        )

        previous_response = None  # To track repeated outputs
        iteration_limit = (
            3  # Set a limit for the number of times to allow repeated responses
        )

        success = False

        while True:
            self.log_event(
                "info",
                f"🗣️ User Prompt: {usr_prompt}",
            )
            think_response, think_message = self._thinking(sys_prompt, usr_prompt)

            if not think_response:
                continue  # Retry on invalid plan

            scratchpad.append(str(think_message))

            # Handle repeated responses
            response_handling = self._handle_repeated_response(
                think_response, previous_response, iteration_limit, pending_task
            )
            if response_handling["retry"]:
                usr_prompt = response_handling["new_prompt"]
                if response_handling["reset_iteration_limit"]:
                    iteration_limit = 3
                    scratchpad = []
                    sys_prompt = PromptBuilder.build_react_prompt(
                        task=pending_task.get("task_name"),
                        task_description=pending_task.get("task_description"),
                        acceptance_criteria=pending_task.get("acceptance_criteria"),
                        tool_names=self.tool_names,
                        tool_descriptions=self.tool_descriptions,
                    )
                continue

            # Update previous_response after comparison
            previous_response = think_response

            suggested_tool = think_response.get("action")
            tool_input = think_response.get("action_input")
            action_result = think_response.get("action_result")

            if final_answer := think_response.get("final_answer"):
                # Check if tool was not executed successfully and any of the fields exist (not None or empty)
                if not success and any([suggested_tool, tool_input, action_result]):
                    self.log_event("error", "❌ Final answer attempted but tool was not executed yet. Rejecting final answer.")
                    usr_prompt = "Final answer attempted but tool was not executed yet. You need to use the tool in order to generate a result. Rejecting final answer."
                    continue  # Reject final answer and continue with the loop

                final_thought = think_response.get("thought")
                self.log_event("info", "Final answer generated.")
                reason_and_act_output = {
                    "task_id": pending_task.get("task_id"),
                    "suggested_tool": suggested_tool,
                    "action_result": str(tool_result),
                    "final_thought": final_thought,
                }
                self.log_event("info", reason_and_act_output)
                return reason_and_act_output

            # Execute the suggested tool
            if suggested_tool:
                result = self.tool_manager.invoke_tool(suggested_tool, tool_input)
                tool_result, success = self._handle_tool_result(suggested_tool, result)
                usr_prompt = json.dumps(
                    {
                        "action": suggested_tool,
                        "action_result": str(tool_result),
                        "success": success,
                    },
                    indent=4,
                )
                self.log_event("info", usr_prompt)

            # Update system prompt with the scratchpad history
            sys_prompt = PromptBuilder.build_react_prompt(
                task=pending_task.get("task_name"),
                task_description=pending_task.get("task_description"),
                acceptance_criteria=pending_task.get("acceptance_criteria"),
                tool_names=self.tool_names,
                tool_descriptions=self.tool_descriptions,
                scratchpad=scratchpad,
            )

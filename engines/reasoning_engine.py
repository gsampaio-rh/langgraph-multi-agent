# engines/reasoning_engine.py

from controllers.scratchpad_manager import ScratchpadManager
from tools.tool_registry import get_tool_by_name, get_tool_names_by_category, get_tool_descriptions_by_category
from builders.prompt_builder import PromptBuilder

class ReasoningEngine:
    def __init__(self, agent_role: str):
        self.agent_role = agent_role
        self.scratchpad_manager = ScratchpadManager()
        self.tool_names, self.tool_descriptions = self._get_agent_tools()

    

    def reason_and_act(self, task_name: str, task_description: str, acceptance_criteria: str, pending_task: dict):
        """
        Iteratively reason and act until a valid task plan with a final answer is generated.
        """
        success = False
        previous_response = None
        iteration_limit = 3  # Limit iterations to prevent loops
        usr_prompt = f"Solve this task: {pending_task.get('task_name')}"

        sys_prompt = PromptBuilder.build_react_prompt(
            task=task_name,
            task_description=task_description,
            acceptance_criteria=acceptance_criteria,
            tool_names=self.tool_names,
            tool_descriptions=self.tool_descriptions,
        )

        while True:
            # Invoke thinking process and get the response
            think_response, think_message = self._thinking(sys_prompt, usr_prompt)
            if not think_response:
                continue

            self.scratchpad_manager.add_thought(str(think_message))

            # Handle repeated responses
            if think_response == previous_response:
                iteration_limit -= 1
                if iteration_limit <= 0:
                    usr_prompt = f"You keep repeating the same reasoning. Please act now or provide more specific details. Your task is {pending_task.get('task_name')}."
                    self.scratchpad_manager.reset_scratchpad()
                    sys_prompt = PromptBuilder.build_react_prompt(
                        task=task_name,
                        task_description=task_description,
                        acceptance_criteria=acceptance_criteria,
                        tool_names=self.tool_names,
                        tool_descriptions=self.tool_descriptions,
                    )
                    iteration_limit = 3  # Reset limit for next loop
                continue

            previous_response = think_response

            # Check for final answer or suggested tool
            if think_response.get("final_answer"):
                if not success:
                    usr_prompt = "Final answer attempted but no tool was executed."
                    continue
                return think_response

            # Execute suggested tool
            suggested_tool = think_response.get("action")
            tool_input = think_response.get("action_input")
            if suggested_tool:
                success, tool_result = self._execute_tool(suggested_tool, tool_input)
                usr_prompt = f"Action: {suggested_tool}, Result: {tool_result}, Success: {success}"
                sys_prompt = PromptBuilder.build_react_prompt(
                    task=task_name,
                    task_description=task_description,
                    acceptance_criteria=acceptance_criteria,
                    tool_names=self.tool_names,
                    tool_descriptions=self.tool_descriptions,
                    scratchpad=self.scratchpad_manager.get_scratchpad(),
                )

    def _thinking(self, sys_prompt: str, usr_prompt: str):
        """
        Call the actual model service to simulate thinking based on prompts and return response.
        """
        # Prepare the payload using the ModelService
        payload = self.model_service.prepare_payload(sys_prompt, usr_prompt)

        # Invoke the model and get the response
        response_json = self.model_service.invoke_model(payload, self.agent_role)

        # Process the model's response
        response_human_message, response_content = (
            self.model_service.process_model_response(response_json, self.agent_role)
        )

        try:
            return json.loads(response_content), response_human_message
        except json.JSONDecodeError as e:
            # Handle JSON decoding errors here if needed
            return None, f"Error decoding JSON response: {e}"

    def _execute_tool(self, tool_name: str, tool_input: dict):
        """
        Execute a tool by name with given inputs.
        """
        tool = get_tool_by_name(tool_name)
        if tool:
            return True, "Tool result here."
        return False, "Tool execution failed."

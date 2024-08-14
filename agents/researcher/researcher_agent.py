import json
from state.agent_state import (
    get_last_entry_from_state,
    get_all_entries_from_state, 
)
from agents.base_agent import Agent
from typing import Dict, Any
from custom_tools import custom_tools, tools_names
from utils.helpers import get_current_utc_datetime

researcher_system_prompt_template = """
You are an AI Researcher Agent responsible for solving tasks by reasoning through the steps, selecting the most appropriate tools, and providing the corresponding arguments. Your task is to reflect on each result to guide your next steps and ensure that the task is completed efficiently and accurately. You may need to break down the task into subtasks and use different tools to complete each subtask. All your outputs should maintain a consistent JSON structure.

## Tools
You have access to the following tools:
{tools_description}

### Use the following format:
- **task**: The task you must complete.
- **thought**: Reflect on what needs to be done.
- **action**: Choose the action to take from the available tools [{tools_names}]
- **action_input**: Use a valid JSON format for the action input (e.g., `{{"input": "example input"}}`). Ensure that the inputs are precise and match the expected format.
- **observation**: Record the result of the action.
... (This Thought/Action/Action Input/Observation sequence can repeat N times as needed)
- **thought**: I now know the final answer!
- **answer**: Once all necessary actions are completed, or if you determine no further tools are needed, provide the final answer. Ensure that the final output meets the task's acceptance criteria and is presented in the required format.

### Output Format:
Your response must follow this JSON format:

- **For Thought only**:
{{
    "thought": "[your reasoning or thought process here]"
}}

- **For Thought with Action**:
{{
    "thought": "[your reasoning or thought process here]",
    "action": "[the tool you decide to use]",
    "action_input": {{"[argument name]": "[argument value]", ...}}
}}

- **For Thought when you have the final answer**:
{{
    "thought": "I now know the final answer!"
}}

- **For Final Answer**:
{{
    "answer": "[the final answer, if no further tools are needed]"
}}

### Example:

**Task**: "What is 20+(2*4)? Calculate step by step."

**Output Sequence**:

1. **Thought**:
{{
    "thought": "I need to calculate the multiplication first before adding."
}}

2. **Thought with Action**:
{{
    "thought": "I need to multiply 2 by 4.",
    "action": "multiply",
    "action_input": {{"a": 2, "b": 4}}
}}

3. **Thought**:
{{
    "thought": "Based on the observation, I now need to add 20 to the result."
}}

4. **Thought with Action**:
{{
    "thought": "I need to add 20 to the result.",
    "action": "add",
    "action_input": {{"a": 20, "b": 8}}
}}

5. **Final Thought**:
{{
    "thought": "I know the final answer."
}}

6. **Final Answer**:
{{
    "answer": "28"
}}

### Error Avoidance:
- **Type Validation**: Before using a tool, double-check that the values provided match the expected types (e.g., ensure that a string is provided where `str` is expected).
- **JSON Format**: Ensure your JSON output is correctly structured, clean, and includes only the necessary details.

### Important Considerations
- Start with the initial user input.
- Clearly distinguish between thoughts, actions, and observations.
- Avoid repeating the same thoughts or actions if they do not lead to progress.
- If you find that you are making the same observations without new insights, consider changing your approach or concluding the task.
- Provide the final answer only when all necessary actions have been completed.

## Current date and time:
{datetime}

## Current Conversation
Below is the current conversation consisting of interleaving human and assistant messages.
{agent_scratchpad}
"""

class ResearcherAgent(Agent):

    def find_and_invoke_tool(
        self, action: Dict[str, Any], custom_tools: list, tools_description: str
    ) -> Any:
        """
        Find and invoke the specified tool based on the action.

        Parameters:
        - action (dict): The action that specifies the tool to be invoked.
        - custom_tools (list): The list of available custom tools.
        - tools_description (str): The description of the available tools.

        Returns:
        - Any: The result of invoking the tool, or None if the tool is not found or an error occurs.
        """
        function_name = action.get("action")
        if not function_name:
            return None

        arguments = action.get("action_input", {})
        if function_name not in tools_description:
            self.log_error(f"TOOL NOT FOUND: '{function_name}'")
            return None

        tool = next((t for t in custom_tools if t.name == function_name), None)
        if tool:
            try:
                self.log_tool_invocation(function_name, arguments)
                return tool.invoke(arguments)
            except Exception as e:
                return self.handle_tool_invocation_error(function_name, e)
        else:
            self.log_error(f"Tool '{function_name}' not found in custom tools.")
        return None

    def log_tool_invocation(self, function_name: str, arguments: dict):
        """Log tool invocation details."""
        self.log_response(f"🔵 Using Tool: {function_name}.")
        self.log_response(f"🔵 Arguments: {arguments}.")

    def handle_tool_invocation_error(
        self, function_name: str, error: Exception
    ) -> dict:
        """Handle errors during tool invocation."""
        error_message = f"Error invoking tool '{function_name}': {str(error)}"
        self.log_error(error_message)
        return {"error": error_message}

    def validate_task(self, task: dict) -> dict:
        """
        Validate that the task contains all required fields.

        Parameters:
        - task (dict): The task to be validated.

        Returns:
        - dict: The validated fields, or raises ValueError if validation fails.
        """
        required_fields = {
            "task_id": task.get("task_id"),
            "task_description": task.get("task_description"),
            "acceptance_criteria": task.get("acceptance_criteria"),
            "tools_to_use": task.get("tools_to_use"),
        }

        missing_fields = [
            field for field, value in required_fields.items() if not value
        ]
        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            self.log_error(
                f"Error: Missing required fields: {missing_fields_str}. Please ensure all required fields are provided."
            )
            raise ValueError(f"Missing required fields: {missing_fields_str}")

        return required_fields

    def fetch_task(self) -> dict:
        """Fetch the current task for the Researcher agent."""
        manager_response = get_last_entry_from_state(self.state, "manager_response")
        if not manager_response:
            self.log_error("NO TASK FOR RESEARCHER FOUND.")
            raise ValueError("No RESEARCHER task found.")

        data = json.loads(manager_response.content)
        for task_item in data.get("tasks", []):
            if (
                task_item.get("agent") == "researcher"
                and task_item.get("status") != "done"
            ):
                return task_item

        self.log_error("NO TASK FOR RESEARCHER FOUND.")
        raise ValueError("No RESEARCHER task found.")

    def check_feedback(self, task_id: str) -> str:
        """Check for feedback related to the identified task."""
        researcher_states = get_all_entries_from_state(self.state, "Researcher_state")
        self.log_response(f"Looking for feedback on {researcher_states}")

        for researcher_state in researcher_states:
            researcher_data = json.loads(researcher_state.content)
            if researcher_data.get("task_id") == task_id:
                feedback = researcher_data.get("feedback", "")
                if feedback:
                    self.log_response(f"Feedback found for task {task_id}: {feedback}")
                else:
                    self.log_response(f"No feedback provided for task {task_id}.")
                return feedback
        return ""

    def format_sys_prompt(
        self,
        task_description: dict,
        tools_description: str,
        feedback: str,
        scratchpad: str,
    ) -> str:
        """Format the system prompt using the provided task and context."""
        return researcher_system_prompt_template.format(
            task_description=task_description,
            tools_names=tools_names,
            tools_description=tools_description,
            agent_scratchpad=scratchpad,
            # feedback=feedback,
            datetime=get_current_utc_datetime(),
        )

    def format_usr_prompt(self, task: dict) -> str:
        """Format the user prompt using the provided task details."""
        return (
            f"Task {task['task_id']}: {task['task_description']}. "
            f"Criteria: {task['acceptance_criteria']}. "
            f"Use the following tools: {task['tools_to_use']}. "
            f"Do not use: {task.get('tools_not_to_use', 'None')}."
        )

    def invoke(
        self,
        user_request: str,
        tools_description: str,
    ) -> dict:
        """Invoke the Researcher Agent by processing the user request and generating a response."""
        self.log_start()

        try:
            task = self.fetch_task()
            validated_task = self.validate_task(task)
            feedback = self.check_feedback(validated_task["task_id"])

            self.update_state(
                "researcher_response",
                f"I am starting to work on {validated_task['task_id']} at {get_current_utc_datetime()}.",
            )

            # Initialize scratchpad
            scratchpad = ""

            sys_prompt = self.format_sys_prompt(
                task["task_description"], tools_description, feedback, scratchpad
            )
            usr_prompt = self.format_usr_prompt(validated_task)

            loop_count = 0
            max_loops = 15

            while loop_count < max_loops:
                loop_count += 1
                self.log_processing(f"User Prompt -> {usr_prompt}")

                payload = self.prepare_payload(sys_prompt, usr_prompt)
                response_json = self.invoke_model(payload)

                if "error" in response_json:
                    self.log_error(f"{response_json}")
                    return response_json

                response_formatted, response_content = self.process_model_response(
                    response_json
                )

                # Update the scratchpad with the latest user prompt and response content
                scratchpad += f"User Prompt: {usr_prompt}\nResponse: {response_content}\n"

                self.update_state(f"researcher_response", response_content)
                self.log_response(response=response_content)

                tool_result = self.find_and_invoke_tool(
                    response_content, custom_tools, tools_description
                )

                if tool_result is not None:
                    tool_result_with_id = {
                        "task_id": validated_task["task_id"],
                        "tool_result": tool_result,
                    }
                    self.log_response(response=tool_result_with_id)
                    self.update_state(f"researcher_response", tool_result_with_id)
                    usr_prompt = f"Observation: {tool_result}"

                if "answer" in response_content:
                    final_answer = response_content["answer"]
                    self.update_state(f"researcher_response", final_answer)
                    self.log_response(response=final_answer)
                    self.log_finished()
                    return self.state

                # Update sys_prompt with the latest scratchpad
                sys_prompt = self.format_sys_prompt(task, tools_description, feedback, scratchpad)

            self.log_response(
                f"Loop limit of {max_loops} reached. Returning the current state."
            )
            self.log_finished()
            return self.state

        except ValueError as e:
            self.log_error(f"Error during invocation: {str(e)}")
            return {"error": str(e)}

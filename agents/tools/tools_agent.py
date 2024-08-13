import json
from termcolor import colored
from agents.base_agent import Agent
from state.agent_state import get_agent_graph_state
from typing import Dict, Any
from utils.helpers import get_current_utc_datetime
from tools import tools

# Template for guiding the tools agent response
tools_sys_prompt_template = """
You are a Tools Agent responsible for selecting the most appropriate tool and providing its corresponding arguments based on the task assigned to you. Your output must be concise, accurate, and follow the specified format.

## Current date and time:
{datetime}

## Task:
{task}

## Available Tools:
{tools_description}

**Important**:
1. Carefully analyze the task to determine which tool is best suited for it.
2. Specify the tool's name exactly as listed in the available tools.
3. Include all necessary arguments for the selected tool.
4. If the task requires optional arguments to improve the tool's performance, include them as well.
5. Ensure the output is in the correct JSON format.

Your response must take the following JSON format:

{{
    "function": "name_of_tool",
    "arguments": {{
        "argument_name": "argument_value",
        ...
    }}
}}

**Examples**:

**Correct Tool Selection Example**:
- Task: "Summarize the provided text."
- Reponse:
    {{
        "function": "text_summarizer",
        "arguments": {{
            "text": "This is the text to be summarized.",
            "max_length": 100
        }}
    }}
    

**Incorrect Tool Selection Example**:
- Task: "Summarize the provided text."
- Selected Tool: "summarizer_tool"
- Reponse:
    {{
        "function": "summarizer_tool",
        "arguments": {{
            "input_text": "Summarize this.",
            "length": 100
        }}
    }}

Remember:
- Always use the exact tool names and argument structures as provided.
- The JSON output should be clean and only include necessary details.
- Double-check the alignment between the task and the chosen tool.
"""

class ToolsAgent(Agent):

    def extract_tools_task(self, content: str) -> Dict[str, Any]:
        """
        Extract the task assigned to the Tools Agent from the given content.

        Parameters:
        - content (str): The JSON content containing tasks.

        Returns:
        - dict: The task assigned to the Tools Agent or None if not found.
        """
        data = json.loads(content)
        for task in data["tasks"]:
            if task["agent"] == "tools":
                return task
        return None

    def find_and_invoke_tool(
        self, action: Dict[str, Any], tools: list, tools_description: str
    ) -> Any:
        """
        Find and invoke the specified tool based on the action.

        Parameters:
        - action (dict): The action that specifies the tool to be invoked.
        - tools (list): The list of available tools.
        - tools_description (str): The description of the available tools.

        Returns:
        - Any: The result of invoking the tool, or None if the tool is not found.
        """
        if action.get("function", False):
            function_name = action.get("function")
            arguments = action.get("arguments", {})

            if function_name in tools_description:
                for tool in tools:
                    if tool.name == function_name:
                        print(
                            colored(
                                f"Tools Agent - Using Tool 🪛: {function_name}",
                                "magenta",
                            )
                        )
                        print(
                            colored(
                                f"Tools Agent - Arguments 🪛: {arguments}",
                                "magenta",
                            )
                        )
                        tool_result = tool(arguments)
                        print(
                            colored(
                                f"Tools Agent - Result  🪛: {tool_result}", "magenta"
                            )
                        )

                        return tool_result
            else:
                print(
                    colored(f"Tools Agent  - TOOL NOT FOUND 🪛: {function_name}", "red")
                )
        return None

    def invoke(
        self,
        user_request: str,
        tools_description: str,
    ) -> dict:
        """
        Invoke the Tools Agent by processing the user request and generating a response.

        Parameters:
        - user_request (str): The user request that the agent should process.
        - prompt (str): The base prompt template.
        - tools_description (str): The description of the available tools.

        Returns:
        - dict: The updated state after the Tools Agent's invocation.
        """
        feedback = ""
        manager_response = get_agent_graph_state(self.state, "manager_response")
        task = (
            self.extract_tools_task(manager_response[0].content)
            if manager_response
            else None
        )

        if task is None:
            return {"error": "No tools task found."}

        task_id = task["task_id"]

        # Format the task prompt
        sys_prompt = tools_sys_prompt_template.format(
            task=task,
            tools_description=tools_description,
            datetime=get_current_utc_datetime(),
        )
        
        payload = self.prepare_payload(sys_prompt, user_request)

        while True:
            # Invoke the model and process the response
            response_json = self.invoke_model(payload)
            if "error" in response_json:
                return response_json

            response_formatted, response_content = self.process_model_response(
                response_json
            )

            response_with_id = {"task_id": task_id, "response": response_formatted}

            # Update the state with the new response
            self.update_state(f"tools_response", response_with_id)
            print(colored(f"Tools Agent 🪛: {response_with_id}", "green"))

            # Attempt to find and invoke a tool
            tool_result = self.find_and_invoke_tool(
                response_content, tools, tools_description
            )

            # If a tool is used, update the state and return
            if tool_result is not None:
                tool_result_with_id = {"task_id": task_id, "tool_result": tool_result}
                print(colored(f"Tools Agent 🪛: {tool_result_with_id}", "green"))
                self.update_state(f"tools_response", tool_result_with_id)
                return self.state

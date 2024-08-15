# custom_tools/tool_invoker.py
import json
from typing import Any, Dict

class ToolInvoker:
    def __init__(self, custom_tools: list):
        self.custom_tools = custom_tools

    def find_and_invoke_tool(
        self, action: Dict[str, Any],
    ) -> Any:

        if isinstance(action, str):
            try:
                action = json.loads(action)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON string for action: {action}. Error: {str(e)}"
                )

        # Ensure the action is a dictionary after conversion
        if not isinstance(action, dict):
            raise TypeError(
                f"Expected action to be a dict, but got {type(action).__name__}"
            )

        function_name = action.get("action")
        if not function_name:
            return None

        tool = next((t for t in self.custom_tools if t.name == function_name), None)
        if tool:
            try:
                return tool.invoke(action.get("action_input", {}))
            except Exception as e:
                raise RuntimeError(f"Error invoking tool '{function_name}': {str(e)}")
        return None

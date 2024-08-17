# custom_tools/tool_invoker.py
import json
from typing import Any, Dict

class ToolInvoker:
    def __init__(self, custom_tools: list):
        self.custom_tools = custom_tools

    def find_and_invoke_tool(
        self,
        action: Dict[str, Any],
    ) -> Any:

        if isinstance(action, str):
            try:
                action = json.loads(action)
            except json.JSONDecodeError as e:
                return {
                    "error": "Invalid JSON",
                    "details": f"Invalid JSON string for action: {action}. Error: {str(e)}",
                }

        function_name = action.get("action")
        if not function_name:
            return {
                "error": "Missing action",
                "details": "No action specified in the input.",
            }

        tool = next((t for t in self.custom_tools if t.name == function_name), None)
        if tool:
            try:
                return tool.invoke(action.get("action_input", {}))
            except Exception as e:
                # Returning the error in a structured format instead of raising it
                return {
                    "error": "Tool Invocation Error",
                    "details": f"Error invoking tool '{function_name}': {str(e)}",
                }
        return {
            "error": "Tool Not Found",
            "details": f"Tool '{function_name}' not found in available tools.",
        }

from typing import Any, Dict


def invoke_tool(tool: Any, **tool_input: Dict[str, Any]) -> Any:
    """
    Invokes the given tool with the provided input parameters.

    :param tool: The tool object to be executed. It must have an `execute()` method.
    :param tool_input: Dictionary containing the input parameters required by the tool.
    :return: The result of the tool execution.
    :raises Exception: If the tool execution fails or the tool does not have an execute method.
    """
    try:
        # Ensure that the tool has an 'execute' method
        if hasattr(tool, "execute") and callable(tool.execute):
            # Invoke the tool with the provided inputs
            result = tool.execute(**tool_input)
            return result
        else:
            raise AttributeError(
                f"The tool '{tool.__class__.__name__}' does not have an 'execute' method."
            )

    except Exception as e:
        # If tool execution fails, raise an exception with the error message
        raise Exception(f"Tool execution failed: {str(e)}") from e

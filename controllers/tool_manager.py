import json
from typing import Any, Dict, List
from tools.tool_registry import (
    get_tool_by_name,
)


class ToolManager:
    def __init__(self):
        """
        Initialize the ToolManager with a list of available tools.

        Parameters:
        - tools (List[Any]): A list of custom tools that have an `invoke()` method.
        """
        # self.tools = tools

    def find_tool(self, tool_name: str) -> Any:
        """
        Find a tool by its name in the available tools list.

        Parameters:
        - tool_name (str): The name of the tool to find.

        Returns:
        - Any: The tool object if found, otherwise None.
        """
        tool = get_tool_by_name(tool_name)
        return tool

    def invoke_tool(
        self, tool_name: str, tool_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Find and invoke a tool by its name, passing the provided input.

        Parameters:
        - tool_name (str): The name of the tool to invoke.
        - tool_input (Dict[str, Any]): The input parameters to pass to the tool's `invoke()` method.

        Returns:
        - Dict[str, Any]: The result of the tool invocation or an error message.
        """
        if tool_input is None:
            tool_input = {}

        # Find the tool by name
        tool = self.find_tool(tool_name)
        if not tool:
            return {
                "error": "Tool Not Found",
                "details": f"Tool '{tool_name}' not found in available tools.",
            }

        # Ensure the tool has an `invoke()` method
        if not hasattr(tool, "invoke") or not callable(tool.invoke):
            return {
                "error": "Invalid Tool",
                "details": f"Tool '{tool_name}' does not have a callable 'invoke()' method.",
            }

        try:
            # Invoke the tool with the provided input
            result = tool.invoke(tool_input)
            return {"success": True, "result": result}
        except Exception as e:
            return {
                "error": "Tool Invocation Error",
                "details": f"Error invoking tool '{tool_name}': {str(e)}",
            }

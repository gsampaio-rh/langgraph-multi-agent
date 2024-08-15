# tool_handler.py
from typing import Any, Dict
from custom_tools.tool_invoker import ToolInvoker
from custom_tools import custom_tools

tool_invoker = ToolInvoker(custom_tools)


def process_tool_action(
    response_content: dict, task: dict, state_key: str, agent
) -> (Any, bool):
    """
    Processes the tool invocation based on the action found in the response content.

    Args:
        response_content (dict): The content returned by the agent's model.
        task (dict): The task being processed.
        state_key (str): The key to update the state with.
        agent: The agent instance to handle state updates and logging.

    Returns:
        tuple: A tuple containing the tool result and a flag indicating if a tool was used (bool).
    """
    used_tool = False
    tool_result = None

    if "action" in response_content:
        tool_result = tool_invoker.find_and_invoke_tool(response_content)
        if tool_result is not None:
            used_tool = True
            agent.update_state(
                f"{state_key}",
                {
                    "task_id": task["task_id"],
                    "tool_result": tool_result,
                },
            )
            agent.log_event("info", f"Tool result: {tool_result}")
        else:
            agent.log_event("info", "Tool invocation failed or no result.")
    else:
        agent.log_event("info", "No action found in the response content.")

    return tool_result, used_tool

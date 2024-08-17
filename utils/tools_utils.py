# utils/tools_utils.py

from custom_tools import (
    custom_tools,
    tools_description,
    vsphere_tools,
    vsphere_tool_descriptions,
)

def render_tools_description_and_args(tools: list) -> list:
    tools_list = []
    for tool in tools:
        # Access the attributes of StructuredTool directly
        tools_list.append(
            {
                "name": tool.name,
                "description": (
                    tool.description
                    if tool.description
                    else "No description available."
                ),
            }
        )
    return tools_list

def format_tools_description(tools_description: str):
    tools_list = []
    try:
        for tool_line in tools_description.splitlines():
            tool_line = tool_line.strip()
            if tool_line and tool_line != "Available Tools:":
                tool_name, *tool_info = tool_line.split(" - ", 1)
                tools_list.append(
                    {
                        "name": tool_name.strip(),
                        "description": (
                            tool_info[0].strip()
                            if tool_info
                            else "No description available."
                        ),
                    }
                )
    except Exception as e:
        raise ValueError(f"Error formatting tools: {str(e)}")

    return tools_list

def get_tool_description(tool_name: str) -> str:
    """
    Retrieves the description of a specific tool by its name from the tools list.
    
    Parameters:
    - tools_list (list): A list of dictionaries containing tool names and descriptions.
    - tool_name (str): The name of the tool whose description is required.
    
    Returns:
    - str: The description of the specified tool or an error message if not found.
    """
    # Iterate over the list of tools to find the matching tool name
    for tool in render_tools_description_and_args(custom_tools):
        if tool['name'] == tool_name:
            return tool['description']

    # If the tool is not found, return an error message
    return f"Tool '{tool_name}' description not found."

def get_vsphere_tool_description(vsphere_tool_name: str) -> str:
    """
    Retrieves the description of a specific tool by its name from the tools list.
    
    Parameters:
    - tools_list (list): A list of dictionaries containing tool names and descriptions.
    - tool_name (str): The name of the tool whose description is required.
    
    Returns:
    - str: The description of the specified tool or an error message if not found.
    """
    # Iterate over the list of tools to find the matching tool name
    for tool in render_tools_description_and_args(vsphere_tools):
        if tool['name'] == vsphere_tool_name:
            return tool['description']

    # If the tool is not found, return an error message
    return f"Tool '{vsphere_tool_name}' description not found."

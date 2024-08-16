# utils/tools_utils.py

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

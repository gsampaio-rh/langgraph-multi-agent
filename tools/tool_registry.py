from langchain.tools.render import render_text_description_and_args
from termcolor import colored
from typing import List
from tools.openshift.openshift_tools import openshift_tools
from tools.vsphere.vm_lifecycle_manager import vm_lifecycle_manager_tools
from utils.helpers import loading_animation
import time

# Registry to hold all discovered tools
tool_registry = {}

# Define a mapping of categories to their respective tool lists
CATEGORY_TOOLS_MAPPING = {
    "openshift": openshift_tools,
    "vsphere_lifecycle": vm_lifecycle_manager_tools,
}

def generate_tool_descriptions(tools):
    """
    Generate tool descriptions using render_text_description_and_args.
    The descriptions are processed and any curly braces are escaped.

    Args:
        tools (list): List of tool objects.

    Returns:
        str: Formatted tool descriptions.
    """
    return render_text_description_and_args(tools).replace("{", "{{").replace("}", "}}")


def register_tools(category_name, tools_list):
    """
    Register tools from the given list, including their generated descriptions,
    and print them immediately.

    Args:
        category_name (str): The category name (e.g., 'vSphere', 'OpenShift').
        tools_list (list): List of tool functions to register.
    """
    print(colored(f"\n🔧 {category_name} Tools:\n", "blue", attrs=["bold"]))
    loading_animation()

    # Register the tools in the registry by their name and description
    for tool in tools_list:
        description = generate_tool_descriptions([tool])
        tool_registry[tool.name] = {"function": tool, "description": description}
        print(colored(f"🔧 {tool.name}:", "yellow", attrs=["bold"]))
        print(colored(f"  {description}\n", "white"))
        time.sleep(0.5)

    print(
        colored(
            f"\n✅ {category_name} tools successfully registered.\n",
            "green",
            attrs=["bold"],
        )
    )


def load_tools():
    """
    Load and display tools from different categories (General, vSphere, OpenShift),
    including their descriptions.
    """
    # Register and display tools for vSphere Lifecycle Manager
    register_tools("vSphere Lifecycle Manager", vm_lifecycle_manager_tools)

    # Register and display tools for OpenShift
    register_tools("OpenShift", openshift_tools)


def get_tool_by_name(tool_name):
    """
    Retrieve a tool function by its name from the tool registry.
    """
    tool_entry = tool_registry.get(tool_name, None)
    if tool_entry:
        return tool_entry["function"]  # Return only the function
    return None


def get_tool_descriptions(tool_name):
    """
    Retrieve a tool function by its name from the tool registry.
    """
    tool_entry = tool_registry.get(tool_name, None)
    if tool_entry:
        return tool_entry["description"]  # Return only the function
    return None


def get_tool_descriptions_by_category(category_name: str):
    """
    Generate and return tool descriptions for the given category using generate_tool_descriptions.

    Args:
        category_name (str): The category name (e.g., 'OpenShift', 'vSphere Lifecycle Manager').

    Returns:
        str: Formatted tool descriptions for the specified category.
    """
    # Get the list of tools based on the category name
    tools_list = CATEGORY_TOOLS_MAPPING.get(category_name)

    if not tools_list:
        return f"No tools found for category: {category_name}"

    # Generate descriptions for the tools in this category
    descriptions = generate_formatted_tool_descriptions(tools_list)

    return descriptions


def generate_formatted_tool_descriptions(tools):
    """
    Generate formatted tool descriptions for readability.
    """
    formatted_descriptions = ""

    for tool in tools:
        # Tool name and description
        description = generate_tool_descriptions([tool])
        formatted_descriptions += f"- **{tool.name}**\n\n"
        formatted_descriptions += f"    {tool.description}\n\n"

        # Arguments section
        formatted_descriptions += "    **Arguments**:\n"
        formatted_descriptions += f"    {str(tool.args)}\n\n"

        # formatted_descriptions += "\n"

        # # Returns section
        # # formatted_descriptions += f"    **Returns**:\n    - `{tool['returns']}`\n"
        formatted_descriptions += "\n"

    return formatted_descriptions

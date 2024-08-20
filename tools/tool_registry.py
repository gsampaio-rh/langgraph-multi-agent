from langchain.tools.render import render_text_description_and_args
from termcolor import colored
from typing import List
from tools.openshift.openshift_tools import openshift_tools
from tools.vsphere.vm_lifecycle_manager import vm_lifecycle_manager_tools
from utils.helpers import loading_animation
import time

# Registry to hold all discovered tools
tool_registry = {}

# Tool categories and corresponding modules
TOOL_CATEGORIES = {
    "vsphere": "tools.vsphere.vm_lifecycle_manager",
    "openshift": "tools.openshift.openshift_tools",
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

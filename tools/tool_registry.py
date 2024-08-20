from tools import (
    custom_tools,
    tools_description,
    vsphere_tools, 
    vsphere_tool_descriptions,
    openshift_tools,
    openshift_tool_descriptions
)
from termcolor import colored
from utils.helpers import loading_animation
from utils.tools_utils import format_tools_description
import time

# Registry to hold all discovered tools
tool_registry = {}

# Explicitly register tools by category
def register_tools():
    """
    Register tools from various modules manually. Organized by category.
    """
    print(colored("\n🧰 REGISTERING TOOLS...", "cyan", attrs=["bold"]))

    # General Tools
    general_tools = custom_tools

    # Register tools in the registry by name
    for tool in general_tools:
        tool_registry[tool.name] = tool
    for tool in vsphere_tools:
        tool_registry[tool.name] = tool
    for tool in openshift_tools:
        tool_registry[tool.name] = tool

    print(colored("\n🔧 General Tools:\n", "blue", attrs=["bold"]))
    loading_animation()
    tools_list = format_tools_description(tools_description)
    for tool in tools_list:
        print(colored(f"🔧 {tool['name']}:", "yellow", attrs=["bold"]))
        print(colored(f"  {tool['description']}\n", "white"))
        time.sleep(0.5)

    print(colored("\n🔧 vSphere Tools:\n", "blue", attrs=["bold"]))
    loading_animation()
    tools_list = format_tools_description(vsphere_tool_descriptions)
    for tool in tools_list:
        print(colored(f"🔧 {tool['name']}:", "yellow", attrs=["bold"]))
        print(colored(f"  {tool['description']}\n", "white"))
        time.sleep(0.5)

    print(colored("\n🔧 OpenShift Tools:\n", "blue", attrs=["bold"]))
    loading_animation()
    tools_list = format_tools_description(openshift_tool_descriptions)
    for tool in tools_list:
        print(colored(f"🔧 {tool['name']}:", "yellow", attrs=["bold"]))
        print(colored(f"  {tool['description']}\n", "white"))
        time.sleep(0.5)

    print(colored("\n✅ All tools successfully registered.", "green", attrs=["bold"]))

    # Log the registration process
    print(colored("\n🧰 TOOL REGISTRATION COMPLETED:", "cyan", attrs=["bold"]))

def get_tool_by_name(tool_name):
    """
    Retrieve a tool by its name from the tool registry.
    """
    return tool_registry.get(tool_name, None)

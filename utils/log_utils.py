# log_utils.py
from termcolor import colored
from config.config import app_config
from utils.helpers import get_current_utc_datetime
import datetime
import time
import sys

# Default messages
DEFAULT_START_MESSAGE = "🤔 Started processing..."
DEFAULT_INFO_MESSAGE = "ℹ️ Info..."
DEFAULT_FINISHED_MESSAGE = "✅ Finished processing.\n"
DEFAULT_RESPONSE_MESSAGE = "🟢 RESPONSE:"
DEFAULT_ERROR_MESSAGE = "❌ ERROR:"

def log(agent_role: str, message: str, level: str = "INFO"):
    """
    Log a message with a timestamp for a specific agent.

    Parameters:
    - agent_role (str): The role of the agent in the app_config.agent_config.agent_display_config.
    - message (str): The message to log.
    - level (str): The log level (INFO, WARNING, ERROR, SUCCESS).
    """
    current_time = get_current_utc_datetime()
    agent_info = app_config.agent_config.agent_display_config.get(agent_role, {})
    agent_name = agent_info.get("name", "Unknown Agent")
    color = agent_info.get("color", "white")

    print(colored(f"[{current_time}][{agent_name}] {message}", color))


def log_start(agent_role: str, message: str = None):
    """
    Log the default start message for a specific agent.

    Parameters:
    - agent_role (str): The role of the agent.
    - message (str): An optional custom start message.
    """
    start_message = f"{DEFAULT_START_MESSAGE} {message}" or DEFAULT_START_MESSAGE
    log(agent_role, start_message)


def log_info(agent_role: str, message: str = None):
    """
    Log the default processing message for a specific agent.

    Parameters:
    - agent_role (str): The role of the agent.
    - message (str): An optional custom processing message.
    """
    info_message = message or DEFAULT_INFO_MESSAGE
    log(agent_role, info_message)


def log_error(agent_role: str, message: str = None):
    """
    Log the default finished message for a specific agent.

    Parameters:
    - agent_role (str): The role of the agent.
    - message (str): An optional custom finished message.
    """
    error_message = f"{DEFAULT_ERROR_MESSAGE} {message}" or DEFAULT_ERROR_MESSAGE
    log(agent_role, error_message)


def log_finished(agent_role: str, message: str = None):
    """
    Log the default finished message for a specific agent.

    Parameters:
    - agent_role (str): The role of the agent.
    - message (str): An optional custom finished message.
    """
    finished_message = message or DEFAULT_FINISHED_MESSAGE
    log(agent_role, finished_message)


def format_agents_description(agent_description: str):
    agents_list = []
    for line in agent_description.splitlines():
        if line.strip().startswith("- **"):
            # Extracting and structuring the agent info
            agent_info = line.strip().split(":")
            agent_name = agent_info[0].replace("- **", "").replace("**", "").strip()
            agent_desc = agent_info[1].strip()
            agents_list.append((agent_name, agent_desc))
    return agents_list


def format_tools_description(tools_description: str):
    tools_list = []
    for tool_line in tools_description.split("\n"):
        tool_line = tool_line.strip()
        if tool_line and tool_line != "Available Tools:":
            tool_name, *tool_info = tool_line.split(" - ", 1)
            tool_name = tool_name.strip()
            tool_info = (
                tool_info[0].strip() if tool_info else "No description available."
            )
            tools_list.append((tool_name, tool_info))
    return tools_list

def log_startup(agents_description: str, tools_description: str):
    # Print the application startup header
    print(
        colored(
            "===============================================", "green", attrs=["bold"]
        )
    )
    print(
        colored(
            "WELCOME TO THE MULTI-AGENT SYSTEM", "green", attrs=["bold"]
        )
    )
    print(colored(f"Startup Time: {datetime.datetime.now()}", "green"))
    print(
        colored(
            "===============================================", "green", attrs=["bold"]
        )
    )

    # Section: Available Agents
    print(colored("\n🛠️  LOADING AGENTS...", "cyan", attrs=["bold"]))
    loading_animation()  # Simulate loading animation

    agents_list = format_agents_description(agents_description)
    for agent_name, agent_desc in agents_list:
        print(colored(f"🔹 {agent_name}:", "yellow", attrs=["bold"]))
        print(colored(f"  {agent_desc}", "white"))
        time.sleep(0.5)  # Add delay between loading each agent

    # Section: Available Tools
    print(colored("\n🧰 LOADING TOOLS...", "cyan", attrs=["bold"]))
    loading_animation()  # Simulate loading animation

    tools_list = format_tools_description(tools_description)
    for tool_name, tool_info in tools_list:
        print(colored(f"🔧 {tool_name}:", "yellow", attrs=["bold"]))
        print(colored(f"  {tool_info}\n", "white"))
        time.sleep(0.5)  # Add delay between loading each tool

    # Section: Starting Workflow
    print(colored("\n🚀 INITIALIZING WORKFLOW...", "green", attrs=["bold"]))
    print(
        colored(
            "===============================================", "green", attrs=["bold"]
        )
    )

def loading_animation():
    """A simple loading animation (rotating bar)."""
    for _ in range(3):  # Loop the animation for a few seconds
        for frame in r"-\|/":
            sys.stdout.write("\r" + frame)
            sys.stdout.flush()
            time.sleep(0.2)

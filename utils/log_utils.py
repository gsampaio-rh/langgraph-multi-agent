# log_utils.py
import logging
from termcolor import colored
from config.config import app_config
import datetime
import time
import sys

# Custom logging levels with colors
LOG_COLORS = {
    logging.INFO: "green",
    logging.WARNING: "yellow",
    logging.ERROR: "red",
    logging.DEBUG: "blue",
}

# Default messages
DEFAULT_START_MESSAGE = "🤔 Started processing..."
DEFAULT_INFO_MESSAGE = "ℹ️ Info..."
DEFAULT_FINISHED_MESSAGE = "✅ Finished processing.\n"
DEFAULT_RESPONSE_MESSAGE = "🟢 RESPONSE:"
DEFAULT_ERROR_MESSAGE = "❌ ERROR:"

class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored log output based on log level."""

    def __init__(self, agent_role):
        super().__init__("%(asctime)s - [%(name)s] %(levelname)s: %(message)s")
        self.agent_role = agent_role

    def format(self, record):
        log_message = super().format(record)
        # Get the color for the specific agent from the config
        agent_info = app_config.agent_config.agent_display_config.get(
            self.agent_role, {}
        )
        agent_color = agent_info.get("color", "white")
        return colored(log_message, agent_color)


def configure_logger(agent_role: str):
    """Configure a logger for each agent based on their role."""
    logger = logging.getLogger(agent_role)
    logger.setLevel(logging.DEBUG)  # Set level to debug for all loggers

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create formatter with color based on the agent's role and add it to the handler
    formatter = ColoredFormatter(agent_role)
    ch.setFormatter(formatter)

    # Add handler to logger if not already added
    if not logger.hasHandlers():
        logger.addHandler(ch)

    return logger


def log(agent_role: str, message: str, level: str = "INFO"):
    """
    Log a message with a timestamp for a specific agent using the centralized logger.
    The log color is based on the agent's role.
    """
    logger = configure_logger(agent_role)

    log_func = getattr(logger, level.lower(), logger.info)  # Default to info level
    log_func(message)


def log_start(agent_role: str, message: str = None):
    """
    Log the default start message for a specific agent.
    """
    start_message = (
        f"{DEFAULT_START_MESSAGE} {message}" if message else DEFAULT_START_MESSAGE
    )
    log(agent_role, start_message, level="INFO")


def log_info(agent_role: str, message: str = None):
    """
    Log an info message for a specific agent.
    """
    info_message = message or DEFAULT_INFO_MESSAGE
    log(agent_role, info_message, level="INFO")


def log_error(agent_role: str, message: str = None):
    """
    Log an error message for a specific agent.
    """
    error_message = (
        f"{DEFAULT_ERROR_MESSAGE} {message}" if message else DEFAULT_ERROR_MESSAGE
    )
    log(agent_role, error_message, level="ERROR")


def log_finished(agent_role: str, message: str = None):
    """
    Log the default finished message for a specific agent.
    """
    finished_message = message or DEFAULT_FINISHED_MESSAGE
    log(agent_role, finished_message, level="INFO")


def format_agents_description(agent_description: str):
    agents_list = []
    current_agent = None
    current_responsibilities = []

    for line in agent_description.splitlines():
        line = line.strip()

        # Check if the line starts with the agent's role
        if line.startswith("#### **") and "Agent**" in line:
            if current_agent:
                # Append the last agent to the list before moving to the next
                agents_list.append(
                    {
                        "name": current_agent,
                        "role": current_role,
                        "responsibilities": current_responsibilities,
                    }
                )
            # Extract the agent name
            current_agent = line.replace("#### **", "").replace("**", "").strip()
            current_responsibilities = []  # Reset responsibilities for the new agent

        elif line.startswith("- **Role**:"):
            # Extract the role description
            current_role = line.replace("- **Role**:", "").strip()

        elif line.startswith("- **Responsibilities**:"):
            # Start capturing responsibilities
            continue

        elif line.startswith("- "):
            # Add each responsibility to the list
            current_responsibilities.append(line.replace("- ", "").strip())

    # Add the last agent to the list
    if current_agent:
        agents_list.append(
            {
                "name": current_agent,
                "role": current_role,
                "responsibilities": current_responsibilities,
            }
        )

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

    agents_list = format_agents_description(app_config.get_agents_description())
    # print(agents_list)
    # Check the structure of the agents_list for debugging
    if not isinstance(agents_list, list):
        print("Error: agents_list is not a list. It's:", type(agents_list))
        print(agents_list)  # Output the content for debugging
    else:
        for agent in agents_list:
            if not isinstance(agent, dict):
                print("Error: agent is not a dictionary. It's:", type(agent))
                print(agent)  # Output the content for debugging
                continue

            # Print the agent's name in yellow, bold
            print(colored(f"🔹 {agent['name']}:", "yellow", attrs=["bold"]))

            # Print the agent's role in white
            print(colored(f"  Role: {agent['role']}", "white"))

            # Print the agent's responsibilities, each on a new line
            print(colored(f"  Responsibilities:", "white", attrs=["bold"]))
            for responsibility in agent["responsibilities"]:
                print(colored(f"    - {responsibility}", "white"))

            time.sleep(0.5)  # Add delay between loading each agent
            print()  # Print a blank line for better readability

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

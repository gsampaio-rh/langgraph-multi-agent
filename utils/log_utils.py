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

DEFAULT_MESSAGES = {
    "start": "🤔 Started processing...",
    "info": "ℹ️ Info...",
    "finished": "✅ Finished processing.\n",
    "response": "🟢 RESPONSE:",
    "error": "❌ ERROR:",
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored log output based on log level."""

    def __init__(self, agent_role):
        super().__init__("%(asctime)s - [%(name)s] %(levelname)s: %(message)s")
        self.agent_role = agent_role

    def format(self, record):
        log_message = super().format(record)
        agent_info = app_config.agent_config.agent_display_config.get(
            self.agent_role, {}
        )
        agent_color = agent_info.get("color", "white")
        return colored(log_message, agent_color)


def configure_logger(agent_role: str):
    """Configure a logger for each agent based on their role."""
    logger = logging.getLogger(agent_role)

    # Configure the logger only once
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # Set the formatter based on the agent's role
        formatter = ColoredFormatter(agent_role)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger


def log(agent_role: str, message: str, level: str = "INFO"):
    """Log a message with a timestamp for a specific agent using the centralized logger."""
    logger = configure_logger(agent_role)
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message)


# Unified logging function for different message types
def log_message(
    agent_role: str, message_type: str = "info", custom_message: str = None
):
    """
    Unified logging function for different message types using if statements.
    If no custom message is provided, the default message for that type is used.
    """
    # Select the message based on the message_type
    if message_type == "start":
        message = custom_message or DEFAULT_MESSAGES["start"]
    elif message_type == "info":
        message = custom_message or DEFAULT_MESSAGES["info"]
    elif message_type == "error":
        message = custom_message or DEFAULT_MESSAGES["error"]
    elif message_type == "finished":
        message = custom_message or DEFAULT_MESSAGES["finished"]
    else:
        message = custom_message or "ℹ️ Info..."  # Default to info if unknown type

    # Log the message at the appropriate level
    log(agent_role, message, level=message_type.upper())


def format_agents_description(agent_description: str):
    agents_list = []
    current_agent = None
    current_responsibilities = []

    try:
        for line in agent_description.splitlines():
            line = line.strip()

            if line.startswith("#### **") and "Agent**" in line:
                if current_agent:
                    agents_list.append(
                        {
                            "name": current_agent,
                            "role": current_role,
                            "responsibilities": current_responsibilities,
                        }
                    )
                current_agent = line.replace("#### **", "").replace("**", "").strip()
                current_responsibilities = []

            elif line.startswith("- **Role**:"):
                current_role = line.replace("- **Role**:", "").strip()

            elif line.startswith("- **Responsibilities**:"):
                continue

            elif line.startswith("- "):
                current_responsibilities.append(line.replace("- ", "").strip())

        if current_agent:
            agents_list.append(
                {
                    "name": current_agent,
                    "role": current_role,
                    "responsibilities": current_responsibilities,
                }
            )
    except Exception as e:
        log("system", f"Error formatting agents: {str(e)}", level="ERROR")

    return agents_list


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
        log("system", f"Error formatting tools: {str(e)}", level="ERROR")

    return tools_list


def log_startup(agents_description: str, tools_description: str):
    print(
        colored(
            "===============================================", "green", attrs=["bold"]
        )
    )
    print(colored("WELCOME TO THE MULTI-AGENT SYSTEM", "green", attrs=["bold"]))
    print(colored(f"Startup Time: {datetime.datetime.now()}", "green"))
    print(
        colored(
            "===============================================", "green", attrs=["bold"]
        )
    )

    print(colored("\n🛠️  LOADING AGENTS...", "cyan", attrs=["bold"]))
    loading_animation()

    agents_list = format_agents_description(agents_description)
    if isinstance(agents_list, list):
        for agent in agents_list:
            print(colored(f"🔹 {agent['name']}:", "yellow", attrs=["bold"]))
            print(colored(f"  Role: {agent['role']}", "white"))
            print(colored(f"  Responsibilities:", "white", attrs=["bold"]))
            for responsibility in agent["responsibilities"]:
                print(colored(f"    - {responsibility}", "white"))
            time.sleep(0.5)
            print()
    else:
        log("system", "Error: agents_list is not correctly formatted.", level="ERROR")

    print(colored("\n🧰 LOADING TOOLS...", "cyan", attrs=["bold"]))
    loading_animation()

    tools_list = format_tools_description(tools_description)
    for tool in tools_list:
        print(colored(f"🔧 {tool['name']}:", "yellow", attrs=["bold"]))
        print(colored(f"  {tool['description']}\n", "white"))
        time.sleep(0.5)

    print(colored("\n🚀 INITIALIZING WORKFLOW...", "green", attrs=["bold"]))
    print(
        colored(
            "===============================================", "green", attrs=["bold"]
        )
    )


def loading_animation(cycles=3, duration=0.2):
    """A simple loading animation (rotating bar)."""
    for _ in range(cycles):
        for frame in r"-\|/":
            sys.stdout.write("\r" + frame)
            sys.stdout.flush()
            time.sleep(duration)

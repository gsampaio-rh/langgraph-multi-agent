import logging
from termcolor import colored
from config.app_config import app_config
import datetime

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
        agent_info = app_config.agents_config.agent_display_config.get(
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


def log_startup():
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

    print(colored("\n🚀 INITIALIZING WORKFLOW...", "green", attrs=["bold"]))
    print(
        colored(
            "===============================================", "green", attrs=["bold"]
        )
    )

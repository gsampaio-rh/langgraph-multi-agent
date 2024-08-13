# log_utils.py
from termcolor import colored
from config.config import app_config
from utils.helpers import get_current_utc_datetime

# Default messages
DEFAULT_START_MESSAGE = "🤔 Started processing..."
DEFAULT_PROCESSING_MESSAGE = "⏳ Processing the request..."
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


def log_processing(agent_role: str, message: str = None):
    """
    Log the default processing message for a specific agent.

    Parameters:
    - agent_role (str): The role of the agent.
    - message (str): An optional custom processing message.
    """
    processing_message = message or DEFAULT_PROCESSING_MESSAGE
    log(agent_role, processing_message)


def log_response(agent_role: str, response: str = None):
    """
    Log the default finished message for a specific agent.

    Parameters:
    - agent_role (str): The role of the agent.
    - message (str): An optional custom finished message.
    """
    reponse_message = (
        f"{DEFAULT_RESPONSE_MESSAGE} {response}" or DEFAULT_RESPONSE_MESSAGE
    )
    log(agent_role, reponse_message)


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

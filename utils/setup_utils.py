import configparser
import os
import logging
import os
from config.app_config import app_config
from tools import tools_description, vsphere_tool_descriptions
from utils.log_utils import log_startup
from tools.tool_registry import register_tools
from controllers.agents_manager import AgentsManager
from controllers.prompts_manager import PromptManager

def load_config():
    # Load the configuration from .env.conf
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), ".env.conf")

    if not config.read(config_path):
        logging.error(f"Failed to read config file at {config_path}")
    else:
        logging.info("Config file read successfully")
        return config

def startup(): 

    agents_manager = AgentsManager()
    agents_manager.display_agents()


    # log_startup(app_config.get_agents_description(), vsphere_tool_descriptions)

    register_tools()
    # load_config()

    # print("Startup sequence completed successfully")

import configparser
import os
import logging
import os
from config.config import app_config
from custom_tools import tools_description, vsphere_tool_descriptions
from utils.log_utils import log_startup

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

    # load_config()

    log_startup(app_config.get_agents_description(), vsphere_tool_descriptions)

    # print("Startup sequence completed successfully")

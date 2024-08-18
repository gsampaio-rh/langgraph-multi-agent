from dataclasses import dataclass
import configparser
import os
from contextlib import contextmanager
from typing import Optional
import logging
from utils.vsphere_utils import connect_to_vsphere, disconnect_from_vsphere

# Load the configuration from .env.conf
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), ".env.conf")

# Check if the config file is being read correctly
if not config.read(config_path):
    print(f"Failed to read config file at {config_path}")
else:
    print("Config file read successfully")


@dataclass
class VsphereConfig:
    """
    Configuration for vSphere connections.
    """

    host: str = config.get("vsphere", "host")
    user: str = config.get("vsphere", "user")
    pwd: str = config.get("vsphere", "pwd")


class VsphereManager:
    def __init__(self, vsphere_config: VsphereConfig):
        self.vsphere_config = vsphere_config
        self.si = None  # Holds the vSphere connection session

    def connect(self) -> Optional[str]:
        """
        Connect to vCenter and store the connection session.

        Returns:
            Optional[str]: None if successful, or an error message if the connection failed.
        """
        try:
            # Pass the config parameters to the connect_to_vsphere function
            self.si, msg = connect_to_vsphere(
                host=self.vsphere_config.host,
                user=self.vsphere_config.user,
                pwd=self.vsphere_config.pwd,
            )

            if self.si:
                logging.info("Successfully connected to vCenter.")
            return msg  # Return the connection message (success or failure)

        except Exception as e:
            logging.error(f"Failed to connect to vCenter: {str(e)}")
            return str(e)

    def disconnect(self):
        """
        Disconnect from vCenter if a session exists.
        """
        if self.si:
            try:
                msg = disconnect_from_vsphere(self.si)
                logging.info(msg)
            except Exception as e:
                logging.error(f"Failed to disconnect from vCenter: {str(e)}")
            finally:
                self.si = None
        else:
            logging.info("No connection to disconnect.")

    @contextmanager
    def connection(self):
        """
        Context manager to ensure that vCenter connection is established and safely disconnected.
        """
        error = self.connect()
        try:
            if not self.si:
                raise ConnectionError(f"Failed to connect to vCenter: {error}")
            yield self.si
        finally:
            self.disconnect()

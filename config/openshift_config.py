from dataclasses import dataclass
import os


@dataclass
class OpenshiftConfig:
    """
    Configuration for OpenShift connections.
    """

    api_url: str = os.getenv("OPENSHIFT_API_URL", "api_url")
    console_url: str = os.getenv("OPENSHIFT_CONSOLE_URL", "console_url")
    token: str = os.getenv("OPENSHIFT_TOKEN", "token")
    inventory_route: str = os.getenv("OPENSHIFT_INVENTORY_ROUTE", "inventory_route")

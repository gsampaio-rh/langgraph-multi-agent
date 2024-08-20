from dataclasses import dataclass, field
from typing import Any, Dict
from .model_config import ModelConfig
from .agents_config import AgentsConfig
from .logging_config import LoggingConfig
from .vsphere_config import VsphereConfig
from .openshift_config import OpenshiftConfig
import json


@dataclass
class AppConfig:
    model_config: ModelConfig = field(default_factory=ModelConfig)
    agents_config: AgentsConfig = field(default_factory=AgentsConfig)
    logging_config: LoggingConfig = field(default_factory=LoggingConfig)
    vsphere_config: VsphereConfig = field(default_factory=VsphereConfig)
    openshift_config: OpenshiftConfig = field(default_factory=OpenshiftConfig)

    def update_from_dict(self, config_dict: Dict[str, Any]):
        """
        Update the AppConfig object with values from a dictionary.
        """
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
            elif key == "model_config":
                self.model_config = ModelConfig(**value)
            elif key == "agents_config":
                self.agents_config = AgentsConfig(**value)
            elif key == "logging_config":
                self.logging_config = LoggingConfig(**value)
            elif key == "vsphere_config":
                self.vsphere_config = VsphereConfig(**value)
            elif key == "openshift_config":
                self.openshift_config = OpenshiftConfig(**value)


def load_config_from_file(file_path: str) -> AppConfig:
    """
    Load the configuration from a JSON file and return an AppConfig instance.
    """
    with open(file_path, "r") as f:
        config_data = json.load(f)

    app_config = AppConfig()
    app_config.update_from_dict(config_data)
    return app_config


# Initialize a default global config object
app_config = AppConfig()

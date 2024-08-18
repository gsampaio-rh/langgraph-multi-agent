from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from config.agents_description import AGENTS_DESCRIPTION
import os
import os
import json

@dataclass
class ModelConfig:
    model_endpoint: str = os.getenv(
        "MODEL_ENDPOINT", "http://localhost:11434/api/generate"
    )
    model_name: str = os.getenv("MODEL_NAME", "llama3:instruct")
    temperature: float = float(os.getenv("MODEL_TEMPERATURE", 0.0))
    top_p: float = float(os.getenv("MODEL_TOP_P", 1.0))
    top_k: int = int(os.getenv("MODEL_TOP_K", 0))
    repetition_penalty: float = float(os.getenv("MODEL_REPEATITION_PENALTY", 1.0))
    headers: Dict[str, str] = field(
        default_factory=lambda: {"Content-Type": "application/json"}
    )
    stop: Optional[str] = os.getenv("MODEL_STOP", None)


@dataclass
class AgentConfig:
    roles: List[str] = field(
        default_factory=lambda: ["planner", "pm", "researcher", "reviewer", "architect"]
    )
    max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", 10))
    recursion_limit: int = int(os.getenv("AGENT_RECURSION_LIMIT", 10))
    agent_display_config: Dict[str, Dict[str, str]] = field(
        default_factory=lambda: {
            "planner": {"name": "Planner Agent 👩🏿‍💻", "color": "cyan"},
            "manager": {"name": "Manager Agent 👩‍💼", "color": "yellow"},
            "researcher": {
                "name": "Researcher Agent 🧑‍🔬",
                "color": "light_magenta",
            },
            "reviewer": {"name": "Reviewer Agent 🔎", "color": "light_blue"},
            "architect": {"name": "Architect Agent 📐", "color": "light_yellow"},
        }
    )

@dataclass
class LoggingConfig:
    verbose: bool = bool(int(os.getenv("LOGGING_VERBOSE", "1")))


@dataclass
class VsphereConfig:
    """
    Configuration for vSphere connections.
    """

    host: str = os.getenv("VSPHERE_HOST", "host")
    user: str = os.getenv("VSPHERE_USER", "user")
    pwd: str = os.getenv("VSPHERE_PWD", "pwd")
    # config.get("vsphere", "host")
    # user: str = config.get("vsphere", "user")
    # pwd: str = config.get("vsphere", "pwd")


@dataclass
class AppConfig:
    model_config: ModelConfig = field(default_factory=ModelConfig)
    agent_config: AgentConfig = field(default_factory=AgentConfig)
    logging_config: LoggingConfig = field(default_factory=LoggingConfig)
    vsphereConfig: VsphereConfig = field(default_factory=VsphereConfig)
    def update_from_dict(self, config_dict: Dict[str, Any]):
        """
        Update the AppConfig object with values from a dictionary.
        """
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
            elif key == "model_config":
                self.model_config = ModelConfig(**value)
            elif key == "agent_config":
                self.agent_config = AgentConfig(**value)
            elif key == "logging_config":
                self.logging_config = LoggingConfig(**value)
            elif key == "vsphereConfig":
                self.vsphereConfig = VsphereConfig(**value)

    def get_agents_description(self) -> str:
        """
        Return a formatted string with agent descriptions.
        """
        return AGENTS_DESCRIPTION


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

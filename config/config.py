from dataclasses import dataclass, field
from typing import Optional, List, Dict
import json


@dataclass
class ModelConfig:
    model_endpoint: str = "http://localhost:11434/api/generate"
    model_name: str = "llama3:instruct"
    temperature: float = 0.0
    headers: Dict[str, str] = field(
        default_factory=lambda: {"Content-Type": "application/json"}
    )
    stop: Optional[str] = None


@dataclass
class AgentConfig:
    roles: List[str] = field(
        default_factory=lambda: ["planner", "pm", "tools", "reviewer"]
    )
    max_iterations: int = 10
    recursion_limit: int = 10
    agent_display_config: Dict[str, Dict[str, str]] = field(
        default_factory=lambda: {
            "planner_node": {"name": "Planner Agent 👩🏿‍💻", "color": "cyan"},
            "pm_node": {"name": "Manager Agent 👩‍💼", "color": "yellow"},
            "tools_node": {"name": "Tools Agent 🪛", "color": "magenta"},
            "reviewer_node": {"name": "Reviewer Agent 🔎", "color": "green"},
        }
    )


@dataclass
class AppConfig:
    model_config: ModelConfig = field(default_factory=ModelConfig)
    agent_config: AgentConfig = field(default_factory=AgentConfig)
    verbose: bool = True

    def update_from_dict(self, config_dict: Dict[str, any]):
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

# Example usage of loading from a file (optional)
# If you have a config file, you can load it like this:
# app_config = load_config_from_file('path_to_config.json')

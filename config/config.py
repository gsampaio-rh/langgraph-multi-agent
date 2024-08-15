from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from custom_tools import tools_names
import os
import json


@dataclass
class ModelConfig:
    model_endpoint: str = os.getenv(
        "MODEL_ENDPOINT", "http://localhost:11434/api/generate"
    )
    model_name: str = os.getenv("MODEL_NAME", "llama3:instruct")
    temperature: float = float(os.getenv("MODEL_TEMPERATURE", 0.0))
    headers: Dict[str, str] = field(
        default_factory=lambda: {"Content-Type": "application/json"}
    )
    stop: Optional[str] = os.getenv("MODEL_STOP", None)


@dataclass
class AgentConfig:
    roles: List[str] = field(
        default_factory=lambda: ["planner", "pm", "tools", "reviewer"]
    )
    max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", 10))
    recursion_limit: int = int(os.getenv("AGENT_RECURSION_LIMIT", 10))
    agent_display_config: Dict[str, Dict[str, str]] = field(
        default_factory=lambda: {
            "planner_node": {"name": "Planner Agent 👩🏿‍💻", "color": "cyan"},
            "pm_node": {"name": "Manager Agent 👩‍💼", "color": "yellow"},
            "researcher_node": {
                "name": "Researcher Agent 🧑‍🔬",
                "color": "light_magenta",
            },
            "reviewer_node": {"name": "Reviewer Agent 🔎", "color": "light_blue"},
        }
    )


@dataclass
class LoggingConfig:
    verbose: bool = bool(int(os.getenv("LOGGING_VERBOSE", "1")))


@dataclass
class AppConfig:
    model_config: ModelConfig = field(default_factory=ModelConfig)
    agent_config: AgentConfig = field(default_factory=AgentConfig)
    logging_config: LoggingConfig = field(default_factory=LoggingConfig)

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

    def get_agents_description(self) -> str:
        """
        Return a formatted string with agent descriptions.
        """
        return f"""
            - **Project Planner:** Creates and manages the overall project plan.
            - **Project Manager:** Manages task execution, monitors progress, and ensures deadlines are met.
            - **Researcher:** Gathers detailed information as required. The researcher has access to these tools: {tools_names}
            - **Reviewer:** Reviews work completed by agents, providing feedback.
        """


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

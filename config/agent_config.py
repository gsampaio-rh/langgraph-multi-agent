from dataclasses import dataclass, field
from typing import List, Dict
import os


@dataclass
class AgentConfig:
    roles: List[str] = field(
        default_factory=lambda: [
            "planner",
            "pm",
            "researcher",
            "vsphere_engineer",
            "ocp_engineer",
            "architect",
        ]
    )
    max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", 10))
    recursion_limit: int = int(os.getenv("AGENT_RECURSION_LIMIT", 10))
    agent_display_config: Dict[str, Dict[str, str]] = field(
        default_factory=lambda: {
            "planner": {"name": "Planner Agent 👩🏿‍💻", "color": "cyan"},
            "manager": {"name": "Manager Agent 👩‍💼", "color": "yellow"},
            "researcher": {"name": "Researcher Agent 🧑‍🔬", "color": "light_magenta"},
            "vsphere_engineer": {
                "name": "vSphere Engineer 👷‍♀️",
                "color": "light_yellow",
            },
            "ocp_engineer": {"name": "OCP Engineer 🧑‍💻", "color": "light_red"},
            "architect": {"name": "Architect Agent 📐", "color": "light_yellow"},
        }
    )

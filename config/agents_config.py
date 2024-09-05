from dataclasses import dataclass, field
from typing import List, Dict, Any
import os
import yaml


@dataclass
class AgentsConfig:
    roles: List[str] = field(
        default_factory=lambda: [
            "planner",
            "pm",
            "vsphere_engineer",
            "ocp_engineer",
            "reviewer",
        ]
    )
    max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", 10))
    recursion_limit: int = int(os.getenv("AGENT_RECURSION_LIMIT", 10))
    agent_display_config: Dict[str, Dict[str, str]] = field(
        default_factory=lambda: {
            "planner": {"name": "Planner Agent 👩🏿‍💻", "color": "cyan"},
            "manager": {"name": "Manager Agent 👩‍💼", "color": "yellow"},
            "vsphere_engineer": {
                "name": "vSphere Engineer 👷‍♀️",
                "color": "light_yellow",
            },
            "ocp_engineer": {"name": "OCP Engineer 🧑‍💻", "color": "light_red"},
            "reviewer": {"name": "Reviewer Agent 🤓", "color": "light_green"},
        }
    )
    description_file: str = "agents.yaml"  # Path to the agents description file
    agents_description: Dict[str, Any] = field(init=False)  # Initialized during load

    def __post_init__(self):
        """
        Called automatically after the dataclass is initialized. It loads and processes
        the agent descriptions by replacing placeholders.
        """
        self.agents_description = self.load_and_replace_placeholders()

    def load_agent_descriptions(self) -> Dict[str, Any]:
        """
        Load the agent descriptions from the YAML file.
        """
        try:
            with open(self.description_file, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Description file '{self.description_file}' not found."
            )

    def replace_placeholders(
        self, agent_data: Dict[str, Any], variables: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Replace placeholders in the agent data with actual values from the variables dictionary.
        """
        for agent in agent_data.get("agents", []):
            # Replace placeholders in responsibilities
            agent["responsibilities"] = [
                responsibility.format(**variables)
                for responsibility in agent.get("responsibilities", [])
            ]

            # Replace placeholders in tools section if it exists and is a list of strings
            if "tools" in agent and isinstance(agent["tools"], list):
                agent["tools"] = [
                    f"    - **Tools**:\n      - {tool.format(**variables)}"
                    for tool in agent["tools"]
                ]

        return agent_data

    def load_and_replace_placeholders(self) -> Dict[str, Any]:
        """
        Load agent descriptions and replace any placeholders with actual values.
        """
        # Load agent descriptions from the YAML file
        agent_data = self.load_agent_descriptions()

        # Define the placeholder replacement values
        vsphere_tool_names = "list_vms, retrieve_vm_details, ensure_vms_not_running"
        openshift_tool_names = (
            "ensure_openshift_project_access, ensure_openshift_providers_ready, "
            "create_migration_plan_tool, start_migration_tool"
        )

        # Variables to replace placeholders
        variables = {
            "vsphere_tool_names": vsphere_tool_names,
            "openshift_tool_names": openshift_tool_names,
        }

        # Replace the placeholders in the agent data
        return self.replace_placeholders(agent_data, variables)

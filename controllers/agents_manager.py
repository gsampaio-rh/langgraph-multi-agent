import yaml
import os
from typing import Dict, Any, List
from termcolor import colored
from utils.helpers import loading_animation
import time


class AgentsManager:
    def __init__(self):
        self.description_file = os.path.join(
            os.path.dirname(__file__), "agents.yaml"
        )
        self.agent_descriptions = self.load_and_replace_placeholders()

    def load_agent_descriptions(self) -> Dict[str, Any]:
        """
        Load the agent descriptions from the YAML file located in the same directory.
        """
        print(colored("\n🛠️  LOADING AGENTS...", "cyan", attrs=["bold"]))
        loading_animation()

        with open(self.description_file, "r") as file:
            return yaml.safe_load(file)

    def replace_placeholders(self, agent_data: Dict[str, Any], variables: Dict[str, str]) -> Dict[str, Any]:
        """
        Replace placeholders in the agent data with actual values from the variables dictionary.
        """

        for agent in agent_data['agents']:

            # Replace placeholders in responsibilities
            agent['responsibilities'] = [
                responsibility.format(**variables) for responsibility in agent.get('responsibilities', [])
            ]

            # Replace placeholders in tools section if it exists and is a list of strings
            if "tools" in agent and isinstance(agent["tools"], list):
                # Properly format the tools section
                agent["tools"] = [
                    f"    - **Tools**:\n      - {tool.format(**variables)}"
                    for tool in agent["tools"]
                ]

        return agent_data

    def load_and_replace_placeholders(self) -> Dict[str, Any]:
        """
        Load agent descriptions and replace any placeholders with actual values.
        """
        agent_data = self.load_agent_descriptions()

        # VSPHERE
        vsphere_tool_names = "list_vms, retrieve_vm_details, ensure_vms_not_running"
        # OPENSHIFT
        openshift_tool_names = "ensure_openshift_project_access, ensure_openshift_providers_ready, create_migration_plan_tool, start_migration_tool"

        # Variables to replace placeholders
        variables = {
            "vsphere_tool_names": vsphere_tool_names,
            "openshift_tool_names": openshift_tool_names,
        }

        # Replace the placeholders in the agent data
        return self.replace_placeholders(agent_data, variables)

    def format_agents_description(self) -> List[Dict[str, Any]]:
        """
        Formats the agent descriptions for output.
        """
        agents_list = self.agent_descriptions.get("agents", [])
        if isinstance(agents_list, list):
            return agents_list
        else:
            raise ValueError("Error: agents_list is not correctly formatted.")

    def display_agents(self):
        """
        Displays the formatted agent descriptions, including tools if available.
        """
        try:
            agents_list = self.format_agents_description()
            for agent in agents_list:
                print(colored(f"🔹 {agent['name']}:", "yellow", attrs=["bold"]))
                print(colored(f"  Role: {agent['role']}", "white"))
                print(colored(f"  Responsibilities:", "white", attrs=["bold"]))
                for responsibility in agent.get('responsibilities', []):
                    print(colored(f"    - {responsibility}", "white"))

                # Display the tools section only if it exists
                if 'tools' in agent:
                    for tool in agent['tools']:
                        print(colored(f"{tool}", "white"))

                time.sleep(0.5)  # Simulate a delay in the loading process
                print()
        except ValueError as e:
            print(colored(str(e), "red"))

    def get_agent_description(self, agent_name: str) -> Dict[str, Any]:
        """
        Get the description for a specific agent by name.
        """
        for agent in self.agent_descriptions["agents"]:
            if agent["name"].lower() == agent_name.lower():
                return agent
        raise ValueError(f"Agent '{agent_name}' not found in descriptions.")

    def get_agent_descriptions(self) -> List[Dict[str, Any]]:
        """
        Return the list of agent descriptions loaded from the YAML file.
        """
        agents_list = self.agent_descriptions.get("agents", [])
        if isinstance(agents_list, list):
            return agents_list
        else:
            raise ValueError("Error: agents_list is not correctly formatted.")

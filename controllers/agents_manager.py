import time
import os
from typing import Dict, Any, List
from termcolor import colored
from config.app_config import app_config
from utils.helpers import loading_animation


class AgentsManager:
    def __init__(self):
        self.agent_descriptions = app_config.agents_config.agents_description

    def format_agent_descriptions(self) -> List[Dict[str, Any]]:
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
        print(colored("\n🛠️  LOADING AGENTS...", "cyan", attrs=["bold"]))
        loading_animation()
        try:
            agents_list = self.format_agent_descriptions()
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

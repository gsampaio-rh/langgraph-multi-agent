# Multi-Agent Virtual Machine Migration System

## Overview

The Multi-Agent Virtual Machine Migration System automates the migration of virtual machines (VMs) from VMware to OpenShift using specialized agents. Each agent is designed to handle a specific part of the migration process, and the Project Manager (PM) Agent oversees the entire workflow, ensuring all tasks are completed in an efficient and coordinated manner.

This system is designed to streamline the migration process, breaking down complex tasks into manageable steps that are handled by intelligent agents, ensuring accuracy, reliability, and extensibility.

## Technologies Used

This system leverages the following technologies:

1. **Large Language Models (LLMs)**:
   - Agents are powered by LLMs, which allow them to understand natural language, reason through tasks, and generate outputs based on complex inputs.

2. **LangChain**:
   - A framework used to manage interactions between the agents, ensuring that they work together smoothly.

3. **LangGraph**:
   - A tool used to visualize and structure the relationships between agents, tasks, and workflows.

## Key Features

- **Automated VM Migration**: Manages the full lifecycle of VM migration from planning to execution and cleanup.
- **Multi-Agent Architecture**: Specialized agents handle specific tasks, allowing for parallel execution and improved efficiency.
- **Validation and Error Handling**: Automated feedback loops ensure tasks are validated, and issues are retried or reported.
- **Customizable Workflows**: The migration process is fully customizable to meet the specific needs of your environment.

## Project Structure

```bash
.
├── agents                 # Contains specialized agents for different tasks
│   ├── architect           # Architect agent
│   ├── engineer            # Engineer agent
│   ├── planner             # Planner agent
│   ├── pm                  # Project Manager agent
│   ├── reviewer            # Reviewer agent
│   ├── networking          # Networking agent
│   └── cleanup             # Cleanup agent
├── builders                # Builders for prompts and plans
├── config                  # Configuration files
├── controllers             # Orchestrates interactions between agents
├── data                    # Data files, including migration steps and configurations
├── prompts                 # Prompt templates for agents
├── schemas                 # JSON schemas for validating agent outputs
├── services                # External services for API calls and tool integrations
├── state                   # Manages the state of agents and tasks
├── tools                   # Custom tools and utilities for specific tasks
├── utils                   # Utility scripts for logging, helpers, etc.
├── workflows               # Manages the flow of tasks between agents
├── main.py                 # Entry point for the application
└── requirements.txt        # Python dependencies
```

### Key Components

- **agents/**: Contains the code for each specialized agent involved in the migration process.
- **config/**: Holds configuration files and agent descriptions.
- **custom_tools/**: Implements custom tools and utilities to aid in specific migration tasks.
- **data/**: Markdown files that define the tutorial and steps for the migration plan.
- **prompts/**: Contains the system prompts for various agents.
- **services/**: Handles interaction with external models, including API calls and response processing.
- **state/**: Manages agent states and interactions.
- **utils/**: General utilities for logging, task management, and helpers.
- **workflows/**: Orchestrates workflows and agent interactions.

## Agents

The system leverages a set of intelligent agents, each with clearly defined roles:

- **Planner Agent**: Creates the Migration Plan Document (MPD) detailing key steps, target VMs, and source/target providers.
- **PM Agent**: Oversees task distribution, execution, and ensures agent coordination throughout the migration process.
- **vSphere Engineer Agent**: Prepares VMs in the vSphere environment and configures the source provider for migration.
- **OpenShift Engineer Agent**: Configures the OpenShift environment and initiates the migration of VMs from vSphere to OpenShift.
- **Reviewer Agent**: Validates the success of the VM migration and ensures applications function correctly post-migration.
- **Networking Agent**: Ensures proper networking configuration for the migrated VMs, including routes, services, and load balancers.
- **Cleanup Agent**: Cleans up unnecessary resources post-migration and ensures a clean environment.

## Agent Workflow Example

Here is a typical flow of tasks in the system:

1. **Planner Agent**:
   - Receives the input and tutorial.
   - Generates the Migration Plan Document (MPD), detailing key steps, VMs, and source/target providers.
   - Passes the MPD to the PM Agent for task distribution.

2. **PM Agent**:
   - Breaks down the Migration Plan into discrete tasks.
   - Assigns tasks to the appropriate agents (e.g., vSphere Engineer, OpenShift Engineer).
   - Oversees execution, ensuring all agents are working in coordination.

3. **vSphere Engineer Agent**:
   - Prepares the VMs in the vSphere environment, ensuring they are powered off and ready for migration.
   - Configures the source provider for the migration and verifies that the VMs are properly allocated.

4. **OpenShift Engineer Agent**:
   - Configures the OpenShift environment, ensuring namespaces are ready.
   - Prepares the target environment and initiates the migration of VMs from vSphere to OpenShift.
   - Coordinates with the Networking Agent to configure OpenShift routes, services, and load balancers.

5. **Reviewer Agent**:
   - Verifies the successful migration of the VMs to OpenShift.
   - Ensures the applications are functioning as expected and that all resources are correctly allocated.

6. **PM Agent**:
   - Receives feedback from the Reviewer Agent.
   - Updates the task list and plans further actions if needed.
   - Ensures all tasks are completed, closes out the process, and provides final updates.

## How to Run the Project

1. **Install Dependencies**:

    Ensure you have Python installed and run:

    ```bash
    pip install -r requirements.txt
    ```

2. **Run the Main Script:**

    To start the system, simply run:

    ```bash
    python main.py
    ```

3. **Configuration:**

    You can adjust the project’s behavior by modifying the config/config.py file. This file controls how agents operate, the tools they use, and the workflow settings.

## Contributing

Contributions are welcome! If you have suggestions, improvements, or new ideas, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments

Special thanks to the developers and community behind LangChain and the LLM models.
All contributors and users who provided feedback and improvements.

## Contact

For any questions or comments, please reach out via <gsampaio@redhat.com>

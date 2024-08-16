# Multi-Agent Virtual Machine Migration System

## Overview

The Multi-Agent Virtual Machine Migration System is designed to manage and automate the migration of virtual machines (VMs) from VMware to OpenShift using a set of specialized agents. Each agent has a distinct role within the migration process, and the project manager (PM) oversees the execution of the migration tasks.

This system utilizes intelligent agents to handle various aspects of the migration, such as planning, configuration, execution, validation, and cleanup. The agents communicate with each other and the central project manager to ensure a smooth and efficient migration process.

## Features

- **Automated VM Migration**: Handles the entire VM migration lifecycle, from planning to cleanup.
- **Task-Based Execution**: Breaks down complex migration tasks into smaller, actionable steps.
- **Multi-Agent Architecture**: Specialized agents handle specific tasks, improving efficiency and accuracy.
- **Validation and Feedback Loops**: Continuous validation of tasks and automated retries on failure.
- **Customizable Migration Plan**: Tailor the migration steps to meet specific project requirements.

## Overview

The **Multi-Agent Task Management System** is built to simulate a collaborative work environment where different agents, powered by AI, work together to complete various tasks. These agents have distinct roles, ranging from project planning to research and review.

The system is designed to streamline task management by distributing responsibilities across specialized agents. Each agent communicates with others to ensure tasks are completed accurately and efficiently.

## Technologies Used

This system leverages the following technologies:

1. **Large Language Models (LLMs)**:
   - Agents are powered by LLMs, which allow them to understand natural language, reason through tasks, and generate outputs based on complex inputs.

2. **LangChain**:
   - A framework used to manage interactions between the agents, ensuring that they work together smoothly.

3. **LangGraph**:
   - A tool used to visualize and structure the relationships between agents, tasks, and workflows.

## Key Concepts

1. **Agents**: Agents are autonomous entities responsible for specific roles in the system. Each agent has specialized skills that allow them to perform tasks such as planning, researching, and reviewing.
2. **Tasks**: Tasks are the individual units of work that agents handle. Each task has a description, criteria for completion, and a status indicating its progress.
3. **Workflow**: The workflow represents the overall flow of tasks, from their creation to completion, managed by different agents working together.
4. **State**: The state holds information about the tasks and agents, ensuring that agents can track progress and share data effectively.

## Agents

The system consists of the following agents, each with clearly defined roles and responsibilities:

- **Planner Agent**: Creates the Migration Plan Document (MPD) based on the provided tutorial and instructions.
- **Architect Agent**: Handles VM identification, network, and storage mapping configuration using the Migration Toolkit for Virtualization (MTV).
- **Engineer Agent**: Executes the migration plan and monitors the migration process.
- **Reviewer Agent**: Validates the success of the migration, ensuring VMs and applications are functioning correctly.
- **Networking Agent**: Ensures proper networking configuration for migrated VMs and verifies application accessibility.
- **Cleanup Agent**: Cleans up unnecessary resources post-migration and ensures a clean environment.
- **PM (Project Manager) Agent**: Manages task breakdowns, oversees execution, and facilitates communication between agents.

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

## Agent Workflow Example

Here is a typical flow of tasks:

1. **Planner Agent**: Generates the Migration Plan Document (MPD).
2. **PM Agent**: Breaks down the MPD into tasks and assigns them to the appropriate agents.
3. **Architect Agent**: Configures the migration settings (e.g., providers, networks).
4. **Engineer Agent**: Executes the migration plan using the Migration Toolkit for Virtualization (MTV).
5. **Reviewer Agent**: Validates the successful migration of the VMs.
6. **Networking Agent**: Ensures that the network configurations are correct.
7. **Cleanup Agent**: Cleans up the environment post-migration.

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

### Acknowledgments

Special thanks to the developers and community behind LangChain and the LLM models.
All contributors and users who provided feedback and improvements.

## Contact

For any questions or comments, please reach out via <gsampaio@redhat.com>
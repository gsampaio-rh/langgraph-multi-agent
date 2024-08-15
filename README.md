# Multi-Agent Task Management System

Welcome to the **Multi-Agent Task Management System**! This project involves multiple AI agents that collaborate to complete complex tasks. The system helps in managing workflows where different agents handle various aspects of a project, such as planning, task execution, and review.

## Table of Contents

- [Multi-Agent Task Management System](#multi-agent-task-management-system)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Technologies Used](#technologies-used)
  - [Key Concepts](#key-concepts)
  - [Modules](#modules)
    - [1. Agents](#1-agents)
    - [2. Workflows](#2-workflows)
    - [3. Custom Tools](#3-custom-tools)
    - [4. Utils](#4-utils)
    - [5. Config](#5-config)
  - [How to Run the Project](#how-to-run-the-project)
  - [Contributing](#contributing)
  - [License](#license)
    - [Acknowledgments](#acknowledgments)
  - [Contact](#contact)

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

## Modules

### 1. Agents

This module contains the different agents involved in the task management system. Each agent has a specific role:

- **Planner Agent**: Creates project plans based on user input.
- **PM (Project Manager) Agent**: Manages the breakdown of tasks and oversees the execution.
- **Researcher Agent**: Executes tasks by gathering information and performing actions based on detailed plans.
- **Reviewer Agent**: Reviews the outputs of tasks to ensure they meet the acceptance criteria.

### 2. Workflows

This module handles the workflow and the logic of how tasks flow between agents. It compiles the workflow graph, ensures that agents communicate effectively, and tracks the status of each task.

### 3. Custom Tools

This module includes custom tools that agents can use to perform their tasks. These tools include:

- **DuckDuckGo Search**: Allows agents to search the web for information.
- **Wikipedia**: Allows agents to query Wikipedia for detailed information on various topics.
- **Arxiv**: Lets agents query Arxiv for scientific articles.
- **Website Crawler**: Allows agents to crawl web pages and extract content.

### 4. Utils

Utility functions for logging, handling state, and managing other general-purpose code.

### 5. Config

Handles the configuration of the system, including model settings and agent behaviors. The configuration is done via the `AppConfig`, which allows you to customize the project’s behavior by modifying the configuration values.

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
# Multi-Agent Task Management System

This repository contains a multi-agent task management system where agents collaborate to complete complex tasks. Each agent has a specific role and interacts with others to ensure the project is completed efficiently and accurately.

## Table of Contents

- [Overview](#overview)
- [Agents](#agents)
- [Usage](#usage)
- [Functions](#functions)
- [Installation](#installation)
- [License](#license)

## Overview

The system is designed to manage a workflow where different agents handle various aspects of a project, such as planning, task execution, and review. The agents communicate with each other to ensure that tasks are completed according to the defined criteria and within the scope of the project.

## Technology Stack

This system leverages the following technologies:

- **LLM (Large Language Models):** The agents utilize advanced LLMs to process natural language inputs, generate responses, and perform complex reasoning tasks.
- **LangChain:** The framework used to build and manage the interactions between agents, enabling them to work together efficiently in a coordinated manner.
- **LangGraph:** A tool that helps structure and visualize the relationships and interactions between agents, tasks, and workflows, ensuring that the system operates smoothly.

## Agents

### 1. Planner Agent

- Role: Creates a comprehensive Project Requirements Document (PRD) based on user inputs.
- Outputs: User requests, objectives, deliverables, scope, requirements, constraints, and limitations.

### 2. Project Manager (PM) Agent

- Role: Manages the execution of the project plan, breaking down tasks and updating them based on feedback.
- Outputs: A detailed task list in JSON format, including task descriptions, statuses, dependencies, and tools to use or avoid.

### 3. Researcher Agent

- Role: Executes tasks by following detailed plans, using specified tools, and adhering to acceptance criteria.
- Outputs: Results of actions taken, observations, and final answers.

### 4. Reviewer Agent

- Role: Reviews the outputs of tasks completed by other agents, ensuring they meet the acceptance criteria and providing feedback.
- Outputs: Task status updates, feedback, and suggestions for improvement.
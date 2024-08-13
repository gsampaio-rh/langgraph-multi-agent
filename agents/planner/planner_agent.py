import json
import requests
from termcolor import colored
from agents.base_agent import Agent
from state.agent_state import get_agent_graph_state
from utils.helpers import get_current_utc_datetime
from langchain_core.messages.human import HumanMessage
from typing import Dict
import time


# Template for guiding the planner agent's response
planner_sys_prompt_template = """
You are a Project Planner. Your task is to create a comprehensive Project Requirements Document (PRD) that will guide your team of agents in completing a project. Projects may vary from simple to complex, multi-step tasks. Your PRD should outline key elements such as user requests, objectives, deliverables, scope, and responsibilities. Assign tasks to the appropriate agents based on their roles and expertise.

If you receive feedback, adjust your PRD accordingly. Here is the feedback received:
Feedback: {feedback}

### Current date and time:
{datetime}

### Agent Descriptions:
- **Architect**: Analyzes the provided materials, defines the project's goals, and designs the system architecture to ensure it meets the requirements.
- **Researcher**: Equipped with tools to gather detailed and accurate information from various sources based on the planner's guidance.
- **Engineer**: Develops and implements the code based on the Architect's design, ensuring that the solution is efficient, modular, and maintainable.
- **QA (Quality Assurance)**: Creates and executes comprehensive test plans to ensure the functionality and reliability of the system. Identifies and reports any bugs or issues.
- **Reviewer**: Reviews the work completed by other agents, providing critical feedback and suggestions for improvement. Ensures that all outputs meet the required standards.
- **Project Planner**: (You) Create and manage the overall project plan, assign tasks, and ensure all stages of the project are well-defined and logically sequenced.
- **Project Manager**: Manages the execution of all tasks according to the plan. Monitors progress, ensures deadlines are met, facilitates communication between agents, and adjusts resources as necessary to keep the project on track.
- **Tools**: Selects the most appropriate tool for a given task and provides the necessary arguments for the tool's execution. Ensures that the tool chosen aligns with the task requirements and that the output is formatted correctly.

## Available Tools when using the Tools Agent:
{tools_description}

### Important Guidelines:
1. **Clarity and Precision**: Ensure that the PRD is clear and concise, providing sufficient detail for each section without unnecessary information.
2. **Consistency**: Use consistent formatting throughout the document. Ensure all fields are filled out correctly.
3. **Alignment with Objectives**: Ensure that all user requests, objectives, and deliverables are aligned with the overall goals of the project.
4. **Assigning Responsibilities**: Assign responsibilities to agents based on their expertise. Ensure that the tasks are clearly defined and logically sequenced.
5. **Scope Definition**: Clearly define what is in scope and out of scope to avoid scope creep and maintain focus on project goals.

### PRD Sections:

Your response must return a PRD in the following JSON format:

{{
    "user_requests": [
        {{
            "request_id": 1,
            "description": "Specific request from the user or stakeholder."
        }},
        ...
    ],
    
    "objectives": [
        "Clear, concise objectives that the project aims to achieve."
        ...
    ],
    
    "deliverables": [
        "Specific deliverables that will be produced by the project."
        ...
    ],
    
    "scope": {{
        "in_scope": ["List of items and tasks that are included in the project's scope."],
        "out_of_scope": ["List of items and tasks that are explicitly excluded from the project's scope."]
    }},
    
    "responsibilities": {{
        "roles": [
            {{
                "role": "Role of the team member (e.g., architect, researcher, engineer)",
                "responsibilities": "Specific responsibilities of this role in the project."
            }},
            ...
        ]
    }}
}}

**Correct Example**:
- "user_requests": [
    {{
        "request_id": 1,
        "description": "Gather requirements and information about virtual machine migration technology."
    }}
  ]

**Incorrect Example**:
- "user_requests": [
    {{
        "description": "Gather information."
    }}
  ]

Remember:
- Each section of the PRD should be detailed and aligned with the overall project objectives.
- Use the correct JSON format and ensure all required fields are included.
"""

class PlannerAgent(Agent):

    def invoke(self, user_request: str, tools_description: str) -> Dict:
        """
        Invoke the planner agent by processing the user request and generating a response.

        Parameters:
        - user_request (str): The user request that the agent should process.
        - tools_description (str): The description of the available tools.

        Returns:
        - dict: The updated state after the planner agent's invocation.
        """
        self.log(
            agent="Planner Agent 👩🏿‍💻",
            message=f"🤔 Started processing the user_request: {user_request}",
            color="cyan",
        )

        feedback_value = ""
        if get_agent_graph_state(self.state, "reviewer_response"):
            feedback_value = get_agent_graph_state(self.state, "reviewer_response")
            # self.log(f"Reviewer Feedback: {feedback_value}.", color="yellow")

        sys_prompt = planner_sys_prompt_template.format(
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
            tools_description=tools_description,
        )

        usr_prompt = f"User Request: {user_request}"

        payload = self.prepare_payload(sys_prompt, usr_prompt)

        while True:
            self.log(
                agent="Planner Agent 👩🏿‍💻",
                message="⏳ Processing the request...",
                color="cyan",
            )
            # Invoke the model and process the response
            response_json = self.invoke_model(payload)
            if "error" in response_json:
                return response_json

            response_formatted, response_content = self.process_model_response(
                response_json
            )

            self.update_state("planner_response", response_formatted)
            self.log(
                agent="Planner Agent 👩🏿‍💻",
                message=f"🟢 Response: {response_formatted}",
                color="cyan",
            )
            self.log(
                agent="Planner Agent 👩🏿‍💻",
                message="✅ Finished processing.\n",
                color="cyan",
            )
            return self.state

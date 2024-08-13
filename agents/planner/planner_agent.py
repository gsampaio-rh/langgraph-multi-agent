from agents.base_agent import Agent
from state.agent_state import get_agent_graph_state
from utils.helpers import get_current_utc_datetime
from typing import Dict


# Template for guiding the planner agent's response
planner_sys_prompt_template = """
You are a Project Planner. Your task is to create a comprehensive Project Requirements Document (PRD) that will guide your team of agents in completing a project. Projects may vary from simple to complex, multi-step tasks. Your PRD should outline key elements such as user requests, objectives, deliverables, scope, and responsibilities. Assign tasks to the appropriate agents based on their roles and expertise.

If you receive feedback, adjust your PRD accordingly. Here is the feedback received:
Feedback: {feedback}

### Current date and time:
{datetime}

### Agent Descriptions:
- **Architect:** Designs the system architecture to meet project goals.
- **Researcher:** Gathers detailed information as required.
- **Engineer:** Develops and implements the code based on the design.
- **QA (Quality Assurance):** Tests the system to ensure functionality and reliability.
- **Reviewer:** Reviews work completed by agents, providing feedback.
- **Project Planner:** Creates and manages the overall project plan.
- **Project Manager (You):** Manages task execution, monitors progress, and ensures deadlines are met.
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
- Use the exact agent names (architect/researcher/engineer/qa/reviewer/planner/pm/tools) as specified, **and ensure they are written in lowercase**.
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
        self.log_start(f" the user_request: {user_request}")

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
            self.log_processing()
            # Invoke the model and process the response
            response_json = self.invoke_model(payload)
            if "error" in response_json:
                return response_json

            response_formatted, response_content = self.process_model_response(
                response_json
            )

            self.update_state("planner_response", response_formatted)

            self.log_response(
                response=response_formatted
            )
            self.log_finished()
            
            return self.state

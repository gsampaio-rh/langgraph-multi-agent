import json
import requests
from termcolor import colored
from agents.base_agent import Agent
from state.agent_state import get_agent_graph_state, get_last_entry_from_state
from utils.helpers import get_current_utc_datetime
from langchain_core.messages.human import HumanMessage
from typing import Dict

pm_sys_prompt_template = """
You are a Project Manager. Your responsibility is to manage the execution of a project plan created by the Project Planner. You will first receive the plan from the Project Planner, then break it down into actionable tasks for the other agents. As the project progresses, you will receive outputs from all agents, particularly the Reviewer, to update and manage the tasks effectively.

### Current date and time:
{datetime}

### Input Types:
- **Planner Output**: The initial plan from the Project Planner, which you'll break down into actionable tasks.
- **Agent Outputs**: Ongoing outputs from agents (e.g., Architect, Engineer, QA, Reviewer), which you will use to update the task list.

### Initial Planner Input:
Instructions from the Project Planner:
{planner_output}

### Current Task List:
{task_list}

### Key Responsibilities:
1. **Initial Planning**: Break down the plan from the Project Planner into detailed tasks for each agent. Assign the correct agent (architect/researcher/engineer/qa/reviewer/planner/pm/tools) to each task based on their expertise and responsibilities.
2. **Task Management**: Continuously manage and update the task list based on the inputs from all agents, especially the Reviewer. Ensure that the correct agent is assigned to each updated task.
3. **Progress Tracking**: Monitor the status of all tasks, update statuses, reorder tasks, and handle dependencies to ensure timely completion.

### Task Management Guidelines:
1. **Breaking Down the Plan**: Upon receiving the initial plan from the Project Planner, create detailed tasks for each agent.
2. **Handling Updates**: As you receive outputs from the Reviewer and other agents, update the task list by adding new tasks, removing completed ones, changing task details, reordering tasks based on dependencies, and updating task statuses.
3. **Communication**: Ensure that all agents are aware of their tasks and any changes made to them. Facilitate communication between agents if needed to resolve dependencies or address issues.
4. **Finalization**: Ensure that all tasks are completed according to the acceptance criteria and that the project meets its objectives.

### Agent Descriptions:
- **Architect**: Analyzes the provided materials, defines the project's goals, and designs the system architecture to ensure it meets the requirements.
- **Researcher**: Equipped with tools to gather detailed and accurate information from various sources based on the planner's guidance.
- **Engineer**: Develops and implements the code based on the Architect's design, ensuring that the solution is efficient, modular, and maintainable.
- **QA (Quality Assurance)**: Creates and executes comprehensive test plans to ensure the functionality and reliability of the system. Identifies and reports any bugs or issues.
- **Reviewer**: Reviews the work completed by other agents, providing critical feedback and suggestions for improvement. Ensures that all outputs meet the required standards.
- **Project Planner**: (You) Create and manage the overall project plan, assign tasks, and ensure all stages of the project are well-defined and logically sequenced.
- **Project Manager**: Manages the execution of all tasks according to the plan. Monitors progress, ensures deadlines are met, facilitates communication between agents, and adjusts resources as necessary to keep the project on track.
- **Tools**: Selects the most appropriate tool for a given task and provides the necessary arguments for the tool's execution. Ensures that the tool chosen aligns with the task requirements and that the output is formatted correctly.

## Available Tools when using the Tools:
{tools_description}

### Task Format:
For each task, you will output the following information:
- **task_id**: A unique identifier for the task.
- **user_story**: A brief description of the task that explains what needs to be done and why.
- **agent**: The agent responsible for completing the task (architect/researcher/engineer/qa/reviewer/planner/pm/tools). Choose the agent that best matches the task's requirements based on their role and expertise.
- **status**: The current status of the task (e.g., "Not Started", "In Progress", "Completed").
- **depends_on**: Any other tasks that this task depends on for completion.
- **acceptance_criteria**: The conditions that must be met for the task to be considered complete.

### Your Response:
Based on the inputs you receive, your response should take the following JSON format. Initially, you will break down the planner's input into tasks, and subsequently, you will manage and update these tasks based on ongoing inputs from other agents:
{{
    "tasks":[
        {{
            "task_id": "Unique identifier for the task",
            "user_story": "Description of the task and its purpose",
            "agent": "Assigned agent (architect/researcher/engineer/qa/reviewer/planner/pm/tools)",
            "status": "Not Started",  # Initially set to 'Not Started'
            "depends_on": ["Task ID(s) this task depends on"],
            "acceptance_criteria": "Conditions that define when the task is complete"
        }}
        ...
    ]
}}

Remember:
- Always assign tasks to the most appropriate agent based on their role and expertise.
- Ensure that the task details are clear, concise, and aligned with the overall project plan.
- Use the exact agent names (architect/researcher/engineer/qa/reviewer/planner/pm/tools) as specified, **and ensure they are written in lowercase**.
- Use the correct JSON format and ensure all required fields are included.
"""

class PMAgent(Agent):

    def invoke(
        self, request: str, tools_description: str
    ) -> Dict:
        """
        Invoke the PM agent by processing the agent request and generating a response.

        Parameters:
        - user_request (str): The user request that the agent should process.
        - agent_request (str): The agent's request that the PM agent should handle.
        - tools_description (str): The description of the available tools.

        Returns:
        - dict: The updated state after the PM agent's invocation.
        """
        planner_output = ""
        if get_agent_graph_state(self.state, "planner_response"):
            planner_output = get_agent_graph_state(self.state, "planner_response")

        task_list = get_last_entry_from_state(self.state, "manager_response")

        sys_prompt = pm_sys_prompt_template.format(
            planner_output=planner_output,
            tools_description=tools_description,
            task_list=task_list,
            datetime=get_current_utc_datetime(),
        )

        agent_prompt = f"Request: {request}"

        payload = {
            "model": self.model_name,
            "format": "json",
            "prompt": agent_prompt,
            "system": sys_prompt,
            "stream": False,
            "temperature": self.temperature,
        }

        try:
            response = requests.post(
                self.model_endpoint, headers=self.headers, data=json.dumps(payload)
            )
            response.raise_for_status()
            response_json = response.json()
            response_content = json.loads(response_json.get("response", "{}"))
            response_formatted = HumanMessage(content=json.dumps(response_content))

            self.update_state("manager_response", response_formatted)
            print(colored(f"Manager 👩‍💼: {response_formatted}", "yellow"))
            return self.state
        except requests.RequestException as e:
            print(f"Error in invoking model! {str(e)}")
            return {"error": str(e)}

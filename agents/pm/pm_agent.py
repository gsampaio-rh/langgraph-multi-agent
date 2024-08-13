from agents.base_agent import Agent
from state.agent_state import (
    get_first_entry_from_state,
    get_all_entries_from_state, 
    get_last_entry_from_state,
)
from utils.helpers import get_current_utc_datetime
from typing import Dict
import json

pm_sys_prompt_template = """
You are a Project Manager. Your role is to manage the execution of a project plan created by the Project Planner. You are responsible for breaking down the initial plan into actionable tasks, managing task updates, tracking progress, and ensuring effective communication between agents.

### Current Date and Time:
{datetime}

### Inputs:
1. **Planner:** The initial plan from the Project Planner, which you'll break down into actionable tasks.
2. **Reviewer:** Ongoing feedback from the reviewer on a task, which you will use to update the task list.

## User Request
{user_request}

### The original overall plan instructions from the Project Planner:
{original_plan}

### Current Task List:
{task_list}

### Key Responsibilities:
1. **Task Breakdown:** Upon receiving the initial plan from the Project Planner, create detailed tasks for each agent.
2. **Task Management:** Continuously update and manage the task list based on inputs from agents, particularly the Reviewer. Reorder tasks, handle dependencies, and update statuses as needed.
3. **Communication:** Ensure all agents are informed of their tasks and any changes. Facilitate communication between agents to resolve dependencies or address issues.

### Agent Descriptions:
- **Architect:** Designs the system architecture to meet project goals.
- **Researcher:** Gathers detailed information as required.
- **Engineer:** Develops and implements the code based on the design.
- **QA (Quality Assurance):** Tests the system to ensure functionality and reliability.
- **Reviewer:** Reviews work completed by agents, providing feedback.
- **Project Planner:** Creates and manages the overall project plan.
- **Project Manager (You):** Manages task execution, monitors progress, and ensures deadlines are met.
- **Tools**: Selects the most appropriate tool for a given task and provides the necessary arguments for the tool's execution. Ensures that the tool chosen aligns with the task requirements and that the output is formatted correctly.

## Available Tools when using the Tools:
{tools_description}

### Task Format:
For each task, output the following information:
- **task_id:** A unique identifier for the task.
- **user_story:** A brief description explaining what needs to be done and why.
- **agent:** The agent responsible for the task (architect/researcher/engineer/qa/reviewer/planner/pm/tools).
- **status:** The current status of the task ("to_do", "in_progress", "incomplete", "done").
- **depends_on:** Any other tasks this task depends on.
- **acceptance_criteria:** Conditions that must be met for the task to be considered complete.

### Your Response:
Based on the inputs, respond in the following JSON format:
{{
    "tasks": [
        {{
            "task_id": "Unique identifier for the task",
            "user_story": "Description of the task and its purpose",
            "agent": "Assigned agent (architect/researcher/engineer/qa/reviewer/planner/pm/tools)",
            "status": "to_do",  # Initially set to 'to_do'
            "depends_on": ["Task ID(s) this task depends on"],
            "acceptance_criteria": "Conditions that define when the task is complete"
        }}
        ...
    ]
}}

Remember:
- Assign tasks to the most appropriate agent based on their role.
- Ensure task details are clear, concise, and aligned with the project plan.
- Use the exact agent names (architect/researcher/engineer/qa/reviewer/planner/pm/tools) as specified, **and ensure they are written in lowercase**.
- Only use the following statuses: "to_do", "in_progress", "incomplete", "done".
- Use the correct JSON format and ensure all required fields are included.
"""

class PMAgent(Agent):

    def invoke(self, user_request: str, tools_description: str) -> Dict:
        """
        Invoke the PM agent by processing the agent request and generating a response.

        Parameters:
        - user_request (str): The user request that the agent should process.
        - tools_description (str): The description of the available tools.

        Returns:
        - dict: The updated state after the PM agent's invocation.
        """
        self.log_start()

        original_plan = get_first_entry_from_state(self.state, "planner_response")
        if not original_plan:
            error_message = (
                "Original plan not found. Cannot proceed without the initial plan."
            )
            self.log_error(error_message)
            return {"error": error_message}

        self.log_response(
            response=f"Now I have the plan {original_plan.content}.",
        )

        task_list = get_last_entry_from_state(self.state, "manager_response")

        if not task_list or task_list == "":
            self.log_response(
                response="📝 Task list is empty. Starting from scratch...",
            )
            usr_prompt = "The task list is empty. You need to create a plan."
        else:
            self.log_response(
                response=f"Now I have the last task list: {task_list.content}.",
            )

            # task_list_dict = json.loads(task_list.content)
            # incomplete_tasks = [
            #     task for task in task_list_dict["tasks"] if task["status"] != "done"
            # ]

            all_reviewer_responses = get_all_entries_from_state(
                self.state, "reviewer_response"
            )

            if not all_reviewer_responses or all_reviewer_responses == "":
                self.log_response(
                    response="🟡 Not all tasks are done but the reviewer didn't send any response yet.",
                )
                usr_prompt = "Not all tasks are done but the reviewer didn't send any response yet. I don't need to update anything."
            else:
                self.log_response(
                    response=f"Now I have the reviewer responses: {all_reviewer_responses}.",
                )
                usr_prompt = f"The reviewer sent a list of updates to the tasks: {all_reviewer_responses}" 

        sys_prompt = pm_sys_prompt_template.format(
            original_plan=original_plan.content,
            user_request=user_request,
            tools_description=tools_description,
            task_list=task_list,
            datetime=get_current_utc_datetime(),
        )

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

            self.update_state("manager_response", response_formatted)
            self.log_response(response=response_formatted)
            self.log_finished()
            return self.state

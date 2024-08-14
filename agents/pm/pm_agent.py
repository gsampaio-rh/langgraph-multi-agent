from agents.base_agent import Agent
from state.agent_state import (
    get_first_entry_from_state,
    get_all_entries_from_state, 
    get_last_entry_from_state,
)
from utils.helpers import get_current_utc_datetime
from config.config import app_config
from typing import Dict

pm_sys_prompt_template = """
You are a Project Manager. Your role is to manage the execution of a project plan created by the Project Planner. You are responsible for breaking down the initial plan into actionable tasks, managing task updates, tracking progress, and ensuring effective communication between agents. Each task must include a detailed and precise plan to ensure it can be executed without confusion or unnecessary iterations.

### Current Date and Time:
{datetime}

### Key Responsibilities:
1. **Task Breakdown:** Upon receiving the initial plan, you will create detailed tasks for each agent. Each task should include a clear and specific plan, outlining exactly what needs to be done, the tools to be used, and any constraints.
2. **Task Management:** Continuously update and manage the task list based on inputs from the agents, particularly feedback from the Reviewer. This includes reordering tasks, handling dependencies, and updating statuses as needed.
3. **Communication:** Ensure all agents are informed of their tasks and any changes. Facilitate communication between agents to resolve dependencies or address issues that arise during task execution.

### Task Structure:
Each task should include the following fields:

- **task_id:** A unique identifier for the task.
- **task_description:** A detailed and specific description of what needs to be done.
- **agent:** The agent responsible for the task (architect/researcher/engineer/qa/reviewer/planner/pm).
- **status:** The current status of the task, which must be one of the following: "to_do", "in_progress", "incomplete", "done".
- **depends_on:** Any other tasks this task depends on. List task IDs.
- **acceptance_criteria:** Clear and specific conditions that must be met for the task to be considered complete.
- **tools_to_use:** List of specific tools that should be used to complete the task.
- **tools_not_to_use:** List of specific tools that should not be used.

### Your Response:
Based on the inputs, respond in the following JSON format:
{{
    "tasks": [
        {{
            "task_id": "Unique identifier for the task",
            "task_description": "Detailed and specific description of the task",
            "agent": "Assigned agent (architect/researcher/engineer/qa/reviewer/planner/pm)",
            "status": "to_do",  # Initially set to 'to_do'
            "depends_on": ["Task ID(s) this task depends on"],
            "acceptance_criteria": "Conditions that define when the task is complete",
            "tools_to_use": ["List of specific tools to use"],
            "tools_not_to_use": ["List of specific tools not to use"]
        }}
        ...
    ]
}}

### Original Plan:
{original_plan}

### Current Task List:
{task_list}

### Agents Description:
{agents_description}

Remember:
- Assign tasks to the most appropriate agent based on their role.
- Ensure task details are clear, concise, and aligned with the project plan.
- Use the exact agent names (architect/researcher/engineer/qa/reviewer/planner/pm) as specified, **and ensure they are written in lowercase**.
- Only use the following statuses: "to_do", "in_progress", "incomplete", "done".
- Use the correct JSON format and ensure all required fields are included.
"""

class PMAgent(Agent):

    def invoke(self, user_request: str,) -> Dict:
        """
        Invoke the PM agent by processing the agent request and generating a response.

        Parameters:
        - user_request (str): The user request that the agent should process.
        - tools_description (str): The description of the available tools.

        Returns:
        - dict: The updated state after the PM agent's invocation.
        """
        self.log_event("start", )

        original_plan = get_first_entry_from_state(self.state, "planner_response")
        if not original_plan:
            error_message = (
                "Original plan not found. Cannot proceed without the initial plan."
            )
            self.log_event("error", error_message)
            return {"error": error_message}

        self.log_event("response", 
            message=f"Now I have the plan {original_plan.content}.",
        )

        task_list = get_last_entry_from_state(self.state, "manager_response")

        if not task_list or task_list == "":
            self.log_event("response", 
                message="📝 Task list is empty. Starting from scratch...",
            )
            usr_prompt = f"The task list is currently empty. This is the user_request: {user_request}. Please create an initial task plan based on the original project requirements."
        else:
            self.log_event("response", 
                message=f"Now I have the last task list: {task_list.content}.",
            )

            # task_list_dict = json.loads(task_list.content)
            # incomplete_tasks = [
            #     task for task in task_list_dict["tasks"] if task["status"] != "done"
            # ]

            all_reviewer_responses = get_all_entries_from_state(
                self.state, "reviewer_response"
            )

            if not all_reviewer_responses or all_reviewer_responses == "":
                self.log_event("response", 
                    message="🟡 Not all tasks are done but the reviewer didn't send any response yet.",
                )
                usr_prompt = "Some tasks remain incomplete, but no feedback has been provided by the reviewer. No updates are required at this time."
            else:
                self.log_event("response", 
                    message=f"Now I have the reviewer responses: {all_reviewer_responses}.",
                )
                usr_prompt = f"The reviewer has provided feedback on the tasks. Please update the task list accordingly with the following details: {all_reviewer_responses}"

        sys_prompt = pm_sys_prompt_template.format(
            original_plan=original_plan.content,
            agents_description=app_config.get_agents_description(),
            task_list=task_list,
            datetime=get_current_utc_datetime(),
        )

        payload = self.prepare_payload(sys_prompt, usr_prompt)

        while True:
            self.log_event("processing", )
            # Invoke the model and process the response
            response_json = self.invoke_model(payload)
            if "error" in response_json:
                return response_json

            response_formatted, response_content = self.process_model_response(
                response_json
            )

            self.update_state("manager_response", response_formatted)
            self.log_event("response", message=response_formatted)
            self.log_event("finished", )
            return self.state

from agents.base_agent import Agent
from state.agent_state import get_first_entry_from_state, get_last_entry_from_state
from utils.helpers import get_current_utc_datetime
from typing import Dict

pm_sys_prompt_template = """
You are a Project Manager. Your role is to manage the execution of a project plan created by the Project Planner. You are responsible for breaking down the initial plan into actionable tasks, managing task updates, tracking progress, and ensuring effective communication between agents.

### Current Date and Time:
{datetime}

### Inputs:
1. **Planner:** The initial plan from the Project Planner, which you'll break down into actionable tasks.
2. **Reviewer:** Ongoing feedback from the reviewer on a task, which you will use to update the task list.

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
- **status:** The current status of the task (e.g., "to_do", "in_progress", "done").
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
        self.log(
            agent="Manager Agent 👩‍💼",
            message=f"🤔 Started processing request {request}",
            color="yellow",
        )

        original_plan = get_first_entry_from_state(self.state, "planner_response")
        if not original_plan:
            error_message = (
                "❌ Original plan not found. Cannot proceed without the initial plan."
            )
            self.log(
                agent="Manager Agent 👩‍💼",
                message=error_message,
                color="red",
            )
            return {"error": error_message}

        self.log(
            agent="Manager Agent 👩‍💼",
            message=f"🟢 Now I have the plan {original_plan.content}.",
            color="yellow",
        )

        task_list = get_last_entry_from_state(self.state, "manager_response")

        if not task_list or task_list == "":
            task_message = "📝 Task list is empty. Starting from scratch..."
        else:
            task_message = f"🟢 Now I have the last task list: {task_list}."

        self.log(
            agent="Manager Agent 👩‍💼",
            message=task_message,
            color="yellow",
        )

        sys_prompt = pm_sys_prompt_template.format(
            original_plan=original_plan.content,
            tools_description=tools_description,
            task_list=task_list,
            datetime=get_current_utc_datetime(),
        )

        agent_prompt = f"Request: {request}"

        payload = self.prepare_payload(sys_prompt, agent_prompt)

        while True:
            self.log(
                agent="Manager Agent 👩‍💼",
                message="⏳ Processing the request...",
                color="yellow",
            )
            # Invoke the model and process the response
            response_json = self.invoke_model(payload)
            if "error" in response_json:
                return response_json

            response_formatted, response_content = self.process_model_response(
                response_json
            )

            self.update_state("manager_response", response_formatted)
            self.log(
                agent="Manager Agent 👩‍💼",
                message=f"🟢 Response: {response_formatted}",
                color="yellow",
            )
            self.log(
                agent="Manager Agent 👩‍💼",
                message="✅ Finished processing.\n",
                color="yellow",
            )
            return self.state

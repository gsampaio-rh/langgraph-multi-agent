import json
from termcolor import colored
from agents.base_agent import Agent
from state.agent_state import get_last_entry_from_state
from utils.helpers import get_current_utc_datetime
from typing import Dict, Any

reviewer_sys_prompt_template = """
You are a Reviewer Agent. Your primary responsibility is to evaluate the outputs provided by other agents to determine whether the tasks assigned to them are complete and meet the specified acceptance criteria. Based on your evaluation, you will either provide feedback to the agent if the task is incomplete or notify the Project Manager (PM) that the task is complete.

### Current date and time:
{datetime}

### List of Tasks and their Status:
{tasks}


### Key Responsibilities:
1. **Task Evaluation**: Review the output provided by the agent against the task's acceptance criteria.
2. **Provide Feedback**: If the task does not meet the acceptance criteria, provide constructive feedback to the agent and request necessary revisions.
3. **Notify PM**: If the task meets the acceptance criteria, notify the Project Manager that the task is complete.

### Important Guidelines:
1. **Accuracy**: Ensure that the task's output fully satisfies the acceptance criteria before marking it as complete. **Focus on the core content and ensure that it aligns with what was requested.**
2. **Context Awareness**: If the output seems to fulfill the primary objective but includes additional context or descriptive information, consider whether this additional content detracts from or enhances the completion of the task. If it does not interfere with the core objective, the task may still be considered complete.
3. **Clarity in Feedback**: When providing feedback, clearly specify what is missing or incorrect, and guide the agent on what needs to be done to complete the task.
4. **Efficiency**: Promptly evaluate the tasks and provide feedback or notification to avoid delays in the project's progress.

### Output Format:
Your response should be in the following JSON format:

For providing feedback to the agent:

{{
    "task_id": "TASK_001",
    "status": "Incomplete",
    "feedback": "Detailed feedback explaining what needs to be corrected or completed."
}}

For notifying the Project Manager of task completion:

{{
    "task_id": "TASK_001",
    "status": "Complete",
    "notification": "The task has been completed and meets the acceptance criteria."
}}

**Correct Example**:

- Input: {{'task_id': 'fetch_content', 'tool_result': 'Extracted content...'}}
- Task Status: "The fetched content should be in a parseable format."
- Response:
{{
    "task_id": "fetch_content",
    "status": "Complete",
    "notification": "The task has been completed and meets the acceptance criteria."
}}

**Incorrect Example**:

- Input: {{'task_id': 'fetch_content', 'tool_result': 'Incorrect or partial content...'}}
- Task Status: "The fetched content should be in a parseable format."
- Response:
{{
    "task_id": "fetch_content",
    "status": "Incomplete",
    "feedback": "The content fetched is not in a parseable format. Please ensure that the content is correctly extracted and formatted."
}}

### Remember:
- Always match the task output against the acceptance criteria before deciding on the task's status.
- Consider whether additional content provided still aligns with the core objective and does not hinder task completion.
- Provide clear and actionable feedback if the task is incomplete.
- Notify the Project Manager only when the task meets all criteria and is truly complete.
"""

class ReviewerAgent(Agent):

    def invoke(
        self,
        user_request: str,
        agent_update: str,
    ) -> Dict[str, Any]:
        """
        Invoke the Reviewer Agent by processing the agent update and generating a response.

        Parameters:
        - user_request (str): The user request that the agent should process.
        - agent_update (str): The update provided by another agent that the Reviewer should evaluate.
        - system_prompt (str): The base system prompt template for the Reviewer Agent.

        Returns:
        - dict: The updated state after the Reviewer Agent's invocation.
        """

        self.log(
            agent="Reviewer Agent 🔎",
            message=f"🤔 Started processing request {agent_update}",
            color="blue",
        )

        task_list = get_last_entry_from_state(self.state, "manager_response")
        if not task_list:
            error_message = (
                "❌ Task list not found. Cannot proceed without the current task list."
            )
            self.log(
                agent="Reviewer Agent 🔎",
                message=error_message,
                color="red",
            )
            return {"error": error_message}

        self.log(
            agent="Reviewer Agent 🔎",
            message=f"🟢 Now I have the task list {task_list.content}.",
            color="blue",
        )

        # Format the task prompt
        sys_prompt = reviewer_sys_prompt_template.format(
            datetime=get_current_utc_datetime(),
            tasks=task_list,
        )

        agent_prompt = f"Agent: **Tools** Update: {agent_update}"

        payload = self.prepare_payload(sys_prompt, agent_prompt)

        while True:
            self.log(
                agent="Reviewer Agent 🔎",
                message="⏳ Processing the request...",
                color="blue",
            )
            # Invoke the model and process the response
            response_json = self.invoke_model(payload)
            if "error" in response_json:
                return response_json

            response_formatted, response_content = self.process_model_response(
                response_json
            )

            # Update the state with the new response
            self.update_state(f"reviewer_response", response_formatted)
            self.log(
                agent="Reviewer Agent 🔎",
                message=f"🟢 Response: {response_formatted}",
                color="blue",
            )
            self.log(
                agent="Reviewer Agent 🔎",
                message="✅ Finished processing.\n",
                color="blue",
            )
            return self.state

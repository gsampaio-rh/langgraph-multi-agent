from agents.base_agent import Agent
from state.agent_state import get_last_entry_from_state
from utils.helpers import get_current_utc_datetime
from typing import Dict, Any
import json

reviewer_sys_prompt_template = """
You are a Reviewer Agent. Your primary responsibility is to evaluate the outputs provided by other agents to ensure that tasks are completed and meet the specified acceptance criteria. You will receive the original task description and the agent's output. Based on your evaluation, you will either provide constructive feedback if the task is incomplete or notify the Project Manager (PM) when the task is complete.

### Current Date and Time:
{datetime}

### Original Task Description:
{original_task}

### Key Responsibilities:
1. **Evaluate Task Output**: Assess the agent's output against the original task description to determine if the task is complete and meets the acceptance criteria.
2. **Provide Constructive Feedback**: If the task does not meet the criteria, provide specific and actionable feedback to the agent, highlighting what needs to be corrected or improved.
3. **Notify Project Manager**: Once the task meets the acceptance criteria, notify the PM that the task is complete.

### Evaluation Guidelines:
1. **Strict Adherence to Criteria**: Ensure that the output fully satisfies the acceptance criteria defined in the original task description before marking a task as complete.
2. **Contextual Awareness**: Consider whether additional information included in the output enhances or detracts from the task's objectives. If it adds value without compromising the primary goal, the task may still be marked as complete.
3. **Clear and Actionable Feedback**: When a task is incomplete, clearly state what is missing or incorrect, and guide the agent on what is required for completion.
4. **Timely Responses**: Quickly evaluate tasks and provide feedback or notifications to avoid project delays.

### Response Format:
Your response should be in JSON format:

- **For Providing Feedback**:

{{
    "task_id": "TASK_001",
    "status": "incomplete",
    "feedback": "Specific feedback explaining what needs to be corrected or completed."
}}

For notifying the Project Manager of task completion:

{{
    "task_id": "TASK_001",
    "status": "done",
    "notification": "The task has been completed and meets the acceptance criteria."
}}

**Correct Example**:

- Input: 
{{ 
    "task_id": "crawl-example-com", 
    "final_thought": "The webpage has been crawled and I have observed the content.", 
    "tool_result": "Document(metadata={{'source': 'https://example.com/', 'title': 'Example Domain', 'language': 'No language found.'}}, page_content='...')"
}}
- Task Status: "The content has been extracted as per the requirements."
- Response:
{{
    "task_id": "fetch_content",
    "status": "done",
    "notification": "The task has been completed and meets the acceptance criteria."
}}

**Incorrect Example**:

- Input: 
{{
    "task_id": "crawl-example-com", 
    "final_thought": "The webpage has been crawled and I have observed the content.", 
    "tool_result": "Document(metadata={{'source': 'https://example.com/', 'title': 'Example Domain', 'language': 'No language found.'}}, page_content='...')"
}}
- Task Status: "The content extraction is incomplete or incorrect."
- Response:
{{
    "task_id": "fetch_content",
    "status": "incomplete",
    "feedback": "The content fetched is not in a parseable format. Please ensure that the content is correctly extracted and formatted."
}}

### Remember:
- Always match the task output against the acceptance criteria before deciding on the task's status.
- Consider whether additional content provided still aligns with the core objective and does not hinder task completion.
- Provide clear and actionable feedback if the task is incomplete.
- Notify the Project Manager only when the task meets all criteria and is truly complete.
- Only use the following statuses: "to_do", "in_progress", "incomplete", "done".
- Use the correct JSON format and ensure all required fields are included.
"""

class ReviewerAgent(Agent):

    def list_task(self, agent_update):
        # Attempt to convert agent_update from a string to a dictionary
        try:
            agent_update_dict = json.loads(agent_update)
        except (TypeError, json.JSONDecodeError) as e:
            error_message = f"❌ Failed to parse agent_update. Error: {str(e)}"
            self.log_event("error", error_message)
            return {"error": error_message}

        task_list = get_last_entry_from_state(self.state, "manager_response")

        # Check if the task list is found
        if not task_list:
            error_message = "❌ Task list not found. Cannot proceed without the current task list."
            self.log_event("error", error_message)
            return {"error": error_message}

        self.log_event("info", 
            message=f"Now I have the last task list: {task_list.content}.",
        )

        try:
            task_list_dict = json.loads(task_list.content)
        except (TypeError, json.JSONDecodeError) as e:
            error_message = f"❌ Failed to parse task_list. Error: {str(e)}"
            self.log_event("error", error_message)
            return {"error": error_message}

        # Extract the task_id from the converted dictionary
        task_id = agent_update_dict.get("task_id")

        # Search for the task in the task_list
        matching_task = None
        for task in task_list_dict.get("tasks", []):
            if task.get("task_id") == task_id:
                matching_task = task
                break

        # Handle the result
        if matching_task:
            self.log_event("info", f"Task found: {matching_task}")
            return {"task": matching_task}
        else:
            error_message = f"❌ Task with ID '{task_id}' not found in the task list."
            self.log_event("error", error_message)
            return {"error": error_message}

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
        self.log_event("start", agent_update)

        task = self.list_task(agent_update)
        # task_list = get_last_entry_from_state(self.state, "manager_response")
        # if not task_list:
        #     error_message = (
        #         "❌ Task list not found. Cannot proceed without the current task list."
        #     )
        #     self.log_event("error", error_message)
        #     return {"error": error_message}

        # self.log_event("info", 
        #     message=f"Now I have the last task list: {task_list.content}.",
        # )

        # Format the task prompt
        sys_prompt = reviewer_sys_prompt_template.format(
            datetime=get_current_utc_datetime(),
            original_task=task,
        )

        agent_prompt = f"Agent Update: {agent_update}"

        # usr_prompt = (
        #     f"Review Task {task_id}: {task_description}. "
        #     f"Criteria: {acceptance_criteria}. "
        #     f"Tools Used: {tools_to_use}. "
        #     f"Tools Not Used: {tools_not_to_use}. "
        #     f"Plan Followed: {detailed_plan}. "
        #     f"Provide feedback on whether the task meets the criteria, and update the task status as 'done' or 'incomplete'. If 'incomplete', explain what needs to be corrected or improved."
        # )

        payload = self.prepare_payload(sys_prompt, agent_prompt)

        while True:
            self.log_event("info","⏳ Processing the request..." )
            # Invoke the model and process the response
            response_json = self.invoke_model(payload)
            if "error" in response_json:
                return response_json

            response_formatted, response_content = self.process_model_response(
                response_json
            )

            # Update the state with the new response
            self.update_state(f"reviewer_response", response_formatted)
            self.log_event("info", message=response_formatted)
            self.log_event("finished", )
            return self.state

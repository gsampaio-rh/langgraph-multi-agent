from agents.base_agent import Agent
from utils import task_utils
from builders.prompt_builder import PromptBuilder
from typing import Dict, Any
import json


class ReviewerAgent(Agent):

    def invoke(self, user_request: str, agent_update: str) -> Dict[str, Any]:
        """
        Invoke the Reviewer Agent by processing the agent update and generating a response.

        Parameters:
        - user_request (str): The user request that the agent should process.
        - agent_update (str): The update provided by another agent that the Reviewer should evaluate.

        Returns:
        - dict: The updated state after the Reviewer Agent's invocation.
        """
        self.log_event("start", agent_update)

        try:
            # Convert agent_update to dictionary to extract task_id
            agent_update_dict = json.loads(agent_update)
            task_id = agent_update_dict.get("task_id")

            if not task_id:
                raise ValueError("No task_id found in the agent update.")

            # Fetch the task directly by its ID
            task = task_utils.get_task_by_id(self.state, task_id)

        except (ValueError, json.JSONDecodeError) as e:
            error_message = f"❌ Error retrieving task: {str(e)}"
            self.log_event("error", error_message)
            return {"error": error_message}

        # Build the system prompt using the PromptBuilder
        sys_prompt = PromptBuilder.build_reviewer_prompt(task)

        # Prepare the agent's prompt
        usr_prompt = f"Agent Update: {agent_update}"

        while True:
            self.log_event("info", "⏳ Processing the request...")
            # Invoke the model and process the response

            response_human_message, response_content = self.invoke_model(
                sys_prompt, usr_prompt
            )

            self.log_event("finished", "")
            return self.state

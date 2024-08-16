from agents.base_agent import Agent
from state.agent_state import get_agent_graph_state
from prompts.prompt_builder import PromptBuilder
from typing import Dict

class PlannerAgent(Agent):

    def invoke(self, user_request: str) -> Dict:
        """
        Invoke the planner agent by processing the user request and generating a response.

        Parameters:
        - user_request (str): The user request that the agent should process.

        Returns:
        - dict: The updated state after the planner agent's invocation.
        """
        self.log_event("start", f" the user_request: {user_request}")

        feedback_value = ""
        if get_agent_graph_state(self.state, "reviewer_response"):
            feedback_value = get_agent_graph_state(self.state, "reviewer_response")
            # self.log(f"Reviewer Feedback: {feedback_value}.", color="yellow")

        sys_prompt = PromptBuilder.build_planner_prompt(user_request, feedback_value)
        usr_prompt = f"User Request: {user_request}"

        self.log_event("info","⏳ Processing the request..." )

        # Invoke the model and process the response
        response_human_message, response_content = self.invoke_model(sys_prompt, usr_prompt)
        if "error" in response_content:
            return response_content
        

        self.log_event("finished", "")

        return self.state

from agents.base_agent import Agent
from state.agent_state import get_agent_graph_state
from typing import Dict
from prompts.prompt_builder import PromptBuilder

class PlannerAgent(Agent):

    def invoke(self, user_request: str) -> Dict:
        """
        Invoke the planner agent by processing the user request and generating a response.

        Parameters:
        - user_request (str): The user request that the agent should process.

        Returns:
        - dict: The updated state after the planner agent's invocation.
        """
        self.log_start(f" the user_request: {user_request}")

        feedback_value = ""
        if get_agent_graph_state(self.state, "reviewer_response"):
            feedback_value = get_agent_graph_state(self.state, "reviewer_response")
            # self.log(f"Reviewer Feedback: {feedback_value}.", color="yellow")

        sys_prompt = PromptBuilder.build_planner_prompt(user_request, feedback_value)
        usr_prompt = f"User Request: {user_request}"
        payload = self.prepare_payload(sys_prompt, usr_prompt)

        self.log_processing()

        # Invoke the model and process the response
        response_json = self.invoke_model(payload)
        response_formatted, response_content = self.process_model_response(
            response_json
        )

        self.update_state("planner_response", response_formatted)
        self.log_response(response=response_formatted)
        self.log_finished()

        return self.state

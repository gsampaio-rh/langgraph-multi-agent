from agents.base_agent import Agent
from state.agent_state import get_agent_graph_state
from prompts.prompt_builder import PromptBuilder
from schemas.planner_schema import planner_output_schema
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

        sys_prompt = PromptBuilder.build_planner_prompt(user_request, feedback_value)
        usr_prompt = f"User Request: {user_request}"

        while True:
            self.log_event("info", "⏳ Processing the request...")

            # Invoke the model and process the response
            response_human_message, response_content = self.invoke_model(
                sys_prompt, usr_prompt
            )

            # Validate the model output
            is_valid, validation_message = self.validate_model_output(
                response_content, planner_output_schema
            )

            if is_valid:
                self.log_event("finished", "")
                return self.state
            else:
                # Log the invalid output and provide feedback
                self.log_event(
                    "error", f"❌ Invalid output received: {validation_message}"
                )
                feedback_value = f"Invalid response: {validation_message}. Please correct and try again."

                # Update the prompt with feedback
                sys_prompt = PromptBuilder.build_planner_prompt(
                    user_request, feedback_value
                )

                # Retry the request with feedback
                self.log_event(
                    "info", f"Retrying the request with feedback: {feedback_value}"
                )

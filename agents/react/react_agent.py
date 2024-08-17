from agents.base_agent import Agent
from state.agent_state import get_agent_graph_state
from prompts.prompt_builder import PromptBuilder
from typing import Dict 

class ReactAgent(Agent):
    def invoke(self, user_request: str) -> Dict:
        """
        Invoke the React agent by processing the user request and executing a series of actions.
        
        Parameters:
        - user_request (str): The user input that the agent should process.

        Returns:
        - dict: The updated state after completing the task.
        """
        self.log_event("start", f"User request received: {user_request}")

        # Step 1: Initialize feedback and system prompt
        feedback_value = ""
        if get_agent_graph_state(self.state, "reviewer_response"):
            feedback_value = get_agent_graph_state(self.state, "reviewer_response")

        sys_prompt = PromptBuilder.build_react_prompt(user_request, feedback_value)
        usr_prompt = f"User Request: {user_request}"
        while True:
            self.log_event("info", "⏳ Processing the request...")

            # Step 2: Invoke the model with the system and user prompt
            response_human_message, response_content = self.invoke_model(
                sys_prompt, usr_prompt
            )

            # Step 3: Process the response from the model
            try:
                action_result = self.process_react_output(response_content)

                # Step 4: Check if the task is completed
                if action_result.get("final_answer"):
                    self.log_event("finished", f"✅ Task completed: {action_result['final_answer']}")
                    return self.state

                # Step 5: Continue with the next thought, action, and observation
                thought = action_result.get("thought")
                action = action_result.get("action")
                action_input = action_result.get("action_input")

                self.log_event("info", f"🤔 Thought: {thought}")
                self.log_event("info", f"🔧 Action: {action}")
                self.log_event("info", f"🔢 Action Input: {action_input}")

                # Update the prompt for the next iteration
                sys_prompt = PromptBuilder.build_react_prompt(thought, feedback_value)
                usr_prompt = f"Action: {action}, Input: {action_input}"
            
            # Step 6: Handle any errors during processing
            except ValueError as e:
                self.log_event("error", f"❌ Error: {str(e)}")
                feedback_value = f"Error: {str(e)}. Please correct and try again."
                sys_prompt = PromptBuilder.build_react_prompt(user_request, feedback_value)
                self.log_event("info", f"Retrying with feedback: {feedback_value}")

    def process_react_output(self, response_content: Dict) -> Dict:
        """
        Process the output of the model and extract the next steps (thought, action, action input).
        
        Parameters:
        - response_content (dict): The content of the model's response.

        Returns:
        - dict: The next thought, action, and action input.
        
        Raises:
        - ValueError: If the model's response is incomplete or invalid.
        """
        # Ensure the response contains the required keys
        if not all(key in response_content for key in ("thought", "action", "action_input")):
            raise ValueError("Incomplete response from the model. Missing 'thought', 'action', or 'action_input'.")

        # Extract thought, action, and action input
        thought = response_content["thought"]
        action = response_content["action"]
        action_input = response_content["action_input"]

        return {
            "thought": thought,
            "action": action,
            "action_input": action_input,
        }

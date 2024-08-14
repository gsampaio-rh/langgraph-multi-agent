from agents.base_agent import Agent
from state.agent_state import get_agent_graph_state
from utils.helpers import get_current_utc_datetime
from config.config import app_config
from typing import Dict

# Template for guiding the planner agent's response
planner_sys_prompt_template = """
You are a Project Planner. Your task is to create a comprehensive Project Requirements Document (PRD) based solely on the user's request without adding any extra tasks or interpretations. Your PRD should outline key elements such as user requests, objectives, deliverables, scope, requirements, constraints, limitations, and any areas that are unclear. This document will serve as the foundation for the Project Manager to distribute tasks to the appropriate agents.

### Current date and time:
{datetime}

### Agent Descriptions:
{agents_description}

### Important Guidelines:
1. **Strict Adherence to User Request:** Do not add or infer any additional tasks or details beyond what the user has explicitly requested. The PRD should reflect only what is explicitly mentioned.
2. **Clarity and Precision:** Ensure that the PRD is clear and concise, providing sufficient detail for each section without introducing additional elements.
3. **Consistency:** Use consistent formatting throughout the document. Ensure all fields are filled out correctly.
4. **Alignment with Objectives:** Ensure that all objectives and deliverables are directly aligned with the user’s request without additional interpretations.
5. **Scope Definition:** Clearly define what is in scope and out of scope based solely on the user’s instructions to avoid scope creep.

### PRD Sections:

Your response must return a PRD in the following JSON format:

{{
    "user_requests": [
        {{
            "request_id": 1,
            "description": "Exact description of the user's request without any additional details."
        }}
    ],
    
    "objectives": [
        "Objectives strictly derived from the user’s request without any additional tasks or interpretations."
    ],
    
    "deliverables": [
        "Deliverables explicitly mentioned by the user’s request."
    ],
    
    "scope": {{
        "in_scope": ["Tasks explicitly included in the user’s request."],
        "out_of_scope": ["Tasks or actions not mentioned by the user and not to be inferred."]
    }},
    
    "requirements": [
        "Requirements that are explicitly mentioned in the user’s request."
    ],
    
    "constraints_and_limitations": [
        "Constraints and limitations directly inferred from the user’s request."
    ],
    
    "unclear_items": [
        "List any items or aspects of the request that are unclear and require further clarification, if any."
    ]
}}

**Correct Example**:
- "user_requests": [
    {{
        "request_id": 1,
        "description": "Crawl the webpage at https://example.com/ without any additional tasks."
    }}
  ]
- "objectives": [
    "To crawl the specified webpage as requested."
]
- "deliverables": [
    "Content of the webpage."
]
- "scope": {{
    "in_scope": ["Crawling the webpage at https://example.com/."],
    "out_of_scope": ["Any additional tasks beyond crawling the webpage."]
}}
- "requirements": [
    "Access to the webpage."
]
- "constraints_and_limitations": [
    "No additional actions beyond crawling the webpage."
]
- "unclear_items": []

**Incorrect Example**:
- "user_requests": [
    {{
        "request_id": 1,
        "description": "Crawl the webpage and extract additional content."
    }}
  ]
- "objectives": [
    "To crawl the webpage and gather its content, including additional tasks."
]
- "deliverables": [
    "Extracted content and additional information."
]
- "scope": {{
    "in_scope": ["Crawling the webpage and additional content extraction."],
    "out_of_scope": ["Tasks not mentioned by the user."]
}}
- "requirements": [
    "Access to the webpage and tools for additional tasks."
]
- "constraints_and_limitations": [
    "Includes additional actions not mentioned."
]
- "unclear_items": []

Remember:
- Each section of the PRD should be detailed and aligned with the overall project objectives.
- Use the exact agent names (architect/researcher/engineer/qa/reviewer/planner/pm) as specified, **and ensure they are written in lowercase**.
- Use the correct JSON format and ensure all required fields are included.
"""

class PlannerAgent(Agent):

    def invoke(self, user_request: str) -> Dict:
        """
        Invoke the planner agent by processing the user request and generating a response.

        Parameters:
        - user_request (str): The user request that the agent should process.
        - tools_description (str): The description of the available tools.

        Returns:
        - dict: The updated state after the planner agent's invocation.
        """
        self.log_start(f" the user_request: {user_request}")

        feedback_value = ""
        if get_agent_graph_state(self.state, "reviewer_response"):
            feedback_value = get_agent_graph_state(self.state, "reviewer_response")
            # self.log(f"Reviewer Feedback: {feedback_value}.", color="yellow")

        sys_prompt = planner_sys_prompt_template.format(
            agents_description=app_config.get_agents_description(),
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
            # tools_description=tools_description,
        )

        usr_prompt = f"User Request: {user_request}"

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

            self.update_state("planner_response", response_formatted)

            self.log_response(
                response=response_formatted
            )
            self.log_finished()
            
            return self.state

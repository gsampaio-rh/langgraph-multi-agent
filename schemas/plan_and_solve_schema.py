# plan_and_solve_schema.py

plan_and_solve_output_schema = {
    "type": "object",
    "properties": {
        "thought": {
            "type": "string",
            "description": "The current thought or reasoning step at any point in the process."
        },
        "action": {
            "type": "string",
            "description": "The action taken based on the thought.",
        },
        "action_input": {
            "type": "object",
            "description": "The input parameters for the action.",
            "additionalProperties": True
        },
        "final_thought": {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "The final thought concluding the task."
                },
                "final_answer": {
                    "type": ["string", "number"],
                    "description": "The final answer derived from completing the task."
                }
            },
            "required": ["thought", "final_answer"],
            "description": "The concluding thought and final answer of the task."
        }
    },
    "required": ["thought",],
    "additionalProperties": False
}

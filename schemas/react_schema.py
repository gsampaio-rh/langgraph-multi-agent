react_output_schema = {
    "type": "object",
    "properties": {
        "thought": {
            "type": "string",
            "description": "The current thought or reasoning step at any point in the process.",
        },
        "action": {
            "type": "string",
            "description": "The action taken based on the thought.",
        },
        "action_input": {
            "type": "object",
            "description": "The input parameters for the action, with dynamic properties allowed.",
            "additionalProperties": {
                "type": ["string", "number", "array", "object"],
                "description": "Input parameter for the action, which can be of multiple types.",
            },
        },
        "observation": {
            "type": ["string", "object", "array"],
            "description": "The result of the action taken, which could be a simple string or a more complex object/array.",
        },
        "final_thought": {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "The final thought concluding the task.",
                },
                "final_answer": {
                    "type": ["string", "number", "boolean", "array", "object"],
                    "description": "The final answer derived from completing the task, which can be of multiple data types.",
                },
            },
            "required": ["thought", "final_answer"],
            "description": "The concluding thought and final answer of the task.",
        },
    },
    "required": ["thought"],
    "additionalProperties": False,
}

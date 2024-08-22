# engineer_output_schema.py

engineer_output_schema = {
    "type": "object",
    "properties": {
        "thought": {
            "type": "string",
            "description": "A description of the engineer's thought process, including why the tool is necessary to proceed.",
        },
        "action": {
            "type": "string",
            "description": "The name of the tool the engineer intends to use.",
        },
        "action_input": {
            "type": "object",
            "description": "A valid JSON object containing the input parameters for the tool.",
            "additionalProperties": True,  # Allows flexibility for different tools
        },
    },
    "required": ["thought", "action", "action_input"],
}

engineer_reflection_output_schema = {
    "type": "object",
    "oneOf": [
        {
            "title": "Successful Task Completion",
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "The thought process reflecting on the successful execution of the tool and confirming that no further actions are required.",
                },
                "final_answer": {
                    "type": "string",
                    "description": "The confirmation that the task has been completed successfully.",
                },
            },
            "required": ["thought", "final_answer"],
        },
        {
            "title": "Additional Steps Required",
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "The thought process reflecting on the successful execution of the tool but identifying the need for additional steps.",
                },
                "next_steps": {
                    "type": "string",
                    "description": "A description of the next steps required to complete the task.",
                },
            },
            "required": ["thought", "next_steps"],
        },
        {
            "title": "Tool Failure",
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "The thought process reflecting on the failed tool execution and identifying what went wrong.",
                },
                "action_correction": {
                    "type": "string",
                    "description": "A description of what needs to be adjusted or corrected before retrying.",
                },
            },
            "required": ["thought", "action_correction"],
        },
    ],
}

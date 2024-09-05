# architect_schema.py

architect_output_schema = {
    "type": "object",
    "properties": {
        "task_id": {
            "type": "string",
            "description": "A unique identifier for the task.",
        },
        "task_name": {
            "type": "string",
            "description": "The name of the task.",
        },
        "task_plan": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step_name": {
                        "type": "string",
                        "description": "The name of the specific step.",
                    },
                    "description": {
                        "type": "string",
                        "description": "A detailed description of the step.",
                    },
                    "tool_needed": {
                        "type": "string",
                        "description": "The name of the tool required for the step, or 'None' if no tool is needed.",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "The current status of the step.",
                    },
                },
                "required": ["step_name", "description", "tool_needed", "status"],
            },
            "description": "An array of steps that comprise the task plan.",
            "minItems": 1,
        },
    },
    "required": ["task_id", "task_name", "task_plan"],
}

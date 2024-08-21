reason_and_act_output_schema = {
    "type": "object",
    "properties": {
        "task_id": {
            "type": "string",
            "description": "The ID of the task being worked on.",
        },
        "suggested_tool": {
            "type": ["string", "null"],
            "description": "The name of the tool that was suggested or used.",
        },
        "action_result": {
            "type": "string",
            "description": "The result of the action performed by the tool, represented as a string.",
        },
        "final_thought": {
            "type": "string",
            "description": "The final thought concluding the task.",
        },
    },
    "required": ["task_id", "final_thought"],
    "additionalProperties": False,
}

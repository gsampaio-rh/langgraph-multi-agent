task_completion_schema = {
    "type": "object",
    "properties": {
        "task_id": {
            "type": "string",
            "description": "The unique identifier of the task.",
        },
        "status": {
            "type": "string",
            "enum": ["completed", "pending", "in_progress"],
            "description": "The current status of the task. It must be one of 'completed', 'pending', or 'in_progress'.",
        },
        "notification": {
            "type": "string",
            "description": "A message describing the current status or notification related to the task.",
        },
    },
    "required": ["task_id", "status", "notification"],
    "additionalProperties": False,
}

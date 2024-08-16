# pm_schema.py

pm_output_schema = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Unique identifier for the task.",
                    },
                    "task_name": {
                        "type": "string",
                        "description": "A descriptive name for the task.",
                    },
                    "task_description": {
                        "type": "string",
                        "description": "A detailed and specific description of what needs to be done.",
                    },
                    "agent": {
                        "type": "string",
                        "enum": [
                            "architect",
                            "engineer",
                            "reviewer",
                            "networking",
                            "cleanup",
                            "pm",
                        ],
                        "description": "The agent responsible for the task.",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["to_do", "in_progress", "incomplete", "done"],
                        "description": "The current status of the task.",
                    },
                    "depends_on": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "List of task IDs that this task depends on.",
                        },
                        "description": "Any other tasks this task depends on.",
                    },
                    "acceptance_criteria": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Clear and specific conditions that must be met for the task to be considered complete.",
                        },
                        "description": "List of acceptance criteria for the task.",
                    },
                    "tools_to_use": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "List of specific tools that should be used to complete the task.",
                        },
                        "description": "List of tools to use for this task.",
                    },
                    "tools_not_to_use": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "List of specific tools that should not be used to complete the task.",
                        },
                        "description": "List of tools not to use for this task.",
                    },
                },
                "required": [
                    "task_id",
                    "task_name",
                    "task_description",
                    "agent",
                    "status",
                    "depends_on",
                    "acceptance_criteria",
                    "tools_to_use",
                    "tools_not_to_use",
                ],
            },
        }
    },
    "required": ["tasks"],
}

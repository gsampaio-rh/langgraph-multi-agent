pm_output_schema = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",  # Unique identifier for the task.
                    },
                    "name": {
                        "type": "string",  # Short name of the task (e.g., "Validate VMware Access").
                    },
                    "description": {
                        "type": "string",  # Detailed description of the task to be executed.
                    },
                    "agent": {
                        "type": "string",
                        "enum": [
                            "architect",
                            "engineer",
                            "networking",
                            "reviewer",
                            "cleanup",
                        ],  # Agent responsible for executing the task (e.g., "Architect Agent").
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "pending",
                            "in-progress",
                            "completed",
                            "failed",
                        ],  # Current status of the task.
                    },
                    "dependencies": {
                        "type": "array",
                        "items": {
                            "type": "string",  # Task IDs that must be completed before this task can start.
                        },
                        "default": [],  # Default is an empty array if there are no dependencies.
                    },
                    "acceptance_criteria": {
                        "type": "string",  # Criteria that must be met to consider the task successfully completed.
                    },
                },
                "required": [
                    "id",
                    "name",
                    "description",
                    "agent",
                    "status",
                    "acceptance_criteria",
                ],  # Dependencies are optional.
            },
        }
    },
    "required": ["tasks"],
}

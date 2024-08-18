planner_output_schema = {
    "type": "object",
    "properties": {
        "source_provider": {
            "type": "string",
            "enum": ["VMware", "Hyper-V", "KVM", "Other"],
        },
        "target_provider": {
            "type": "string",
            "enum": ["OpenShift", "AWS", "Azure", "GCP", "Other"],
        },
        "stages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "stage_name": {"type": "string"},
                    "goal": {"type": "string"},
                    "input_data": {
                        "type": "object",
                        "additionalProperties": {
                            "type": ["null", "string", "array"],
                            "items": {"type": "string"},
                        },
                    },
                    "task_breakdown": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                    },
                    "expected_results": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                    },
                },
                "required": [
                    "stage_name",
                    "goal",
                    "input_data",
                    "task_breakdown",
                    "expected_results",
                ],
            },
            "minItems": 1,
        },
        "variables": {
            "type": "object",
            "additionalProperties": {
                "type": ["null", "string", "array"],
                "items": {"type": "string"},
            },
        },
    },
    "required": ["source_provider", "target_provider", "stages", "variables"],
}

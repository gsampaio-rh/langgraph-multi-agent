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
                    "completion_criteria": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                    },
                    "provided_inputs": {
                        "type": "object",
                        "additionalProperties": {
                            "type": ["null", "string", "array"],
                            "items": {"type": "string"},
                        },
                    },
                    "execution_plan": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                    },
                },
                "required": [
                    "stage_name",
                    "goal",
                    "completion_criteria",
                    "provided_inputs",
                    "execution_plan",
                ],
            },
            "minItems": 1,
        },
    },
    "required": ["source_provider", "target_provider", "stages"],
}

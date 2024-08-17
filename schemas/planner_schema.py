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
                    "pre_requisites": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "available"],
                                },
                                "value": {
                                    "type": ["null", "string", "array"],
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["status", "value"],
                        },
                    },
                    "steps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                    },
                    "validations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                    },
                },
                "required": ["stage_name", "pre_requisites", "steps", "validations"],
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

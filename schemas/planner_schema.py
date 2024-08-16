planner_output_schema = {
    "type": "string",
    "properties": {
        "source_provider": {"type": "string", "enum": ["VMware", "Hyper-V", "KVM"]},
        "target_provider": {
            "type": "string",
            "enum": ["OpenShift", "AWS", "Azure", "GCP"],
        },
        "vms_to_migrate": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "vm_name": {"type": "string"},
                    "os": {"type": "string", "enum": ["Linux", "Windows"]},
                    "source_network": {"type": "string"},
                    "target_network": {"type": "string"},
                    "source_storage": {"type": "string"},
                    "target_storage": {"type": "string"},
                },
                "required": [
                    "vm_name",
                    "os",
                    "source_network",
                    "target_network",
                    "source_storage",
                    "target_storage",
                ],
            },
            "minItems": 1,
        },
        "steps": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "network_mappings": {
            "type": "object",
            "properties": {
                "source_network": {"type": "string"},
                "target_network": {"type": "string"},
            },
            "required": ["source_network", "target_network"],
        },
        "storage_mappings": {
            "type": "object",
            "properties": {
                "source_storage": {"type": "string"},
                "target_storage": {"type": "string"},
            },
            "required": ["source_storage", "target_storage"],
        },
        "validations": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    },
    "required": [
        "source_provider",
        "target_provider",
        "vms_to_migrate",
        "steps",
        "network_mappings",
        "storage_mappings",
        "validations",
    ],
}

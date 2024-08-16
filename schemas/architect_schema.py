#architect_schema.py

architect_output_schema = {
    "type": "object",
    "properties": {
        "vm_configurations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "vm_name": {"type": "string"},
                    "os": {"type": "string", "enum": ["Linux", "Windows"]},
                    "vm_id": {"type": "string"},
                    "network": {
                        "type": "object",
                        "properties": {
                            "source_network": {"type": "string"},
                            "target_network": {"type": "string"},
                        },
                        "required": ["source_network", "target_network"]
                    },
                    "storage": {
                        "type": "object",
                        "properties": {
                            "source_storage": {"type": "string"},
                            "target_storage": {"type": "string"},
                            "disk_mappings": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "disk_id": {"type": "string"},
                                        "source_size": {"type": "string"},
                                        "target_size": {"type": "string"}
                                    },
                                    "required": ["disk_id", "source_size", "target_size"]
                                },
                                "minItems": 1
                            }
                        },
                        "required": ["source_storage", "target_storage", "disk_mappings"]
                    }
                },
                "required": ["vm_name", "os", "vm_id", "network", "storage"]
            },
            "minItems": 1
        },
        "mtv_config": {
            "type": "object",
            "properties": {
                "source_provider": {"type": "string", "enum": ["VMware", "Hyper-V", "KVM"]},
                "target_provider": {"type": "string", "enum": ["OpenShift", "AWS", "Azure", "GCP"]},
                "migration_tool": {"type": "string"},
                "provider_configurations": {
                    "type": "object",
                    "properties": {
                        "vmware": {
                            "type": "object",
                            "properties": {
                                "endpoint": {"type": "string"},
                                "credentials": {
                                    "type": "object",
                                    "properties": {
                                        "username": {"type": "string"},
                                        "password": {"type": "string"}
                                    },
                                    "required": ["username", "password"]
                                }
                            },
                            "required": ["endpoint", "credentials"]
                        },
                        "openshift": {
                            "type": "object",
                            "properties": {
                                "cluster_url": {"type": "string"},
                                "credentials": {
                                    "type": "object",
                                    "properties": {
                                        "username": {"type": "string"},
                                        "token": {"type": "string"}
                                    },
                                    "required": ["username", "token"]
                                }
                            },
                            "required": ["cluster_url", "credentials"]
                        }
                    },
                    "required": ["vmware", "openshift"]
                }
            },
            "required": ["source_provider", "target_provider", "migration_tool", "provider_configurations"]
        },
        "validation_checks": {
            "type": "object",
            "properties": {
                "network_validation": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "criteria": {"type": "string"}
                    },
                    "required": ["status", "criteria"]
                },
                "storage_validation": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "criteria": {"type": "string"}
                    },
                    "required": ["status", "criteria"]
                },
                "vm_compatibility_check": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "criteria": {"type": "string"}
                    },
                    "required": ["status", "criteria"]
                }
            },
            "required": ["network_validation", "storage_validation", "vm_compatibility_check"]
        }
    },
    "required": ["vm_configurations", "mtv_config", "validation_checks"]
}

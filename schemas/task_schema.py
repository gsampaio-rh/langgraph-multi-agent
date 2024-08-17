execute_step_output_schema = {
    "type": "object",
    "properties": {
        "step_name": {"type": "string"},  # Name of the step being executed
        "status": {"type": "string", "enum": ["done", "failed"]},  # Status of the step (done or failed)
        "result": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},  # Indicates if the step was successful"details": {"type": "string"},  # Additional details or output from the step"output": {"type": ["string", "object"]}  # The output of the executed step (can be string or object)
            },
            "required": ["success"]
        }
    },
    "required": ["step_name", "status"]
}

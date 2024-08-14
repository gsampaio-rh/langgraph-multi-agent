# utils/task_utils.py

from state.agent_state import get_last_entry_from_state
import json


def fetch_pending_task(
    state, agent_role: str, task_state_entry: str = "manager_response"
) -> dict:
    """Fetch the current task for the Researcher agent."""
    manager_response = get_last_entry_from_state(state, task_state_entry)
    if not manager_response:
        raise ValueError(f"No {agent_role} task found.")

    data = json.loads(manager_response.content)
    for task_item in data.get("tasks", []):
        if task_item.get("agent") == agent_role and task_item.get("status") != "done":
            return task_item
    raise ValueError(f"No {agent_role} task found.")


def validate_task(task: dict) -> dict:
    """Validate that the task contains all required fields."""
    required_fields = {
        "task_id": task.get("task_id"),
        "task_description": task.get("task_description"),
        "acceptance_criteria": task.get("acceptance_criteria"),
        "tools_to_use": task.get("tools_to_use"),
    }
    missing_fields = [field for field, value in required_fields.items() if not value]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    return required_fields

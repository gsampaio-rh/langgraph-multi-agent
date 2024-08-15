# utils/task_utils.py

import json
from state.agent_state import get_last_entry_from_state


def get_tasks_list(state, task_state_key: str = "manager_response") -> list:
    """
    Retrieve the list of valid tasks from the state.

    Parameters:
    - state: The state object that contains task data.
    - task_state_key: The state key to the state object that contains task data.

    Returns:
    - list: A list of valid tasks from the state (non-empty and contains 'status').

    Raises:
    - ValueError: If the task list is not found or cannot be parsed.
    """
    task_list = get_last_entry_from_state(state, task_state_key)

    # Return an empty list if no tasks are found
    if not task_list:
        return []

    try:
        task_list_dict = json.loads(task_list.content)
        tasks = task_list_dict.get("tasks", [])

        # Filter out invalid tasks (empty tasks or tasks without a 'status' key)
        valid_tasks = [
            task
            for task in tasks
            if isinstance(task, dict) and task and "status" in task
        ]

        return valid_tasks

    except (TypeError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to parse task list. Error: {str(e)}")


def get_task_by_id(state, task_id: str) -> dict:
    """
    Retrieve a specific task by its ID from the state.

    Parameters:
    - state: The state object that contains task data.
    - task_id (str): The ID of the task to retrieve.

    Returns:
    - dict: The task with the specified ID.

    Raises:
    - ValueError: If the task with the given ID is not found.
    """
    task_list = get_tasks_list(state)

    for task in task_list:
        if task.get("task_id") == task_id:
            return task

    raise ValueError(f"Task with ID '{task_id}' not found in the task list.")


def get_pending_tasks(state, agent_role: str = None) -> list:
    """
    Fetch pending tasks for a specific agent role, or all pending tasks if no role is provided.

    Parameters:
    - state: The state object that contains task data.
    - agent_role (str, optional): The role of the agent whose tasks should be fetched.
      If None, returns all pending tasks.

    Returns:
    - list: A list of pending tasks matching the agent role, or all pending tasks if no role is specified.

    Raises:
    - ValueError: If no pending tasks are found for the given role.
    """
    task_list = get_tasks_list(
        state
    )  # Assume this function fetches the full task list from the state

    pending_tasks = []
    for task in task_list:
        # Check if the task is pending (not 'done')
        if task.get("status") != "done":
            # If an agent_role is specified, filter by role; otherwise, add all pending tasks
            if agent_role is None or task.get("agent") == agent_role:
                pending_tasks.append(task)

    if not pending_tasks:
        raise ValueError(
            f"No pending tasks found{' for agent ' + agent_role if agent_role else ''}."
        )

    return pending_tasks


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

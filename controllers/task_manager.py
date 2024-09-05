from utils.log_utils import log_message
from utils.helpers import get_status_symbol

class TaskManager:

    def __init__(self, agent_role: str):
        self.agent_role = agent_role
        self.tasks = []

    def log_event(self, event_type: str, message: str = None):
        """
        Logs an event based on the event type.
        """
        log_message(self.agent_role, message_type=event_type, custom_message=message)

    def add_task(self, task_id: str, task_name: str):
        """
        Add a new task to the task list.

        Parameters:
        - task_id (str): The unique ID of the task.
        - task_name (str): The name of the task.
        """
        task = {"task_id": task_id, "task_name": task_name, "status": "pending"}
        self.tasks.append(task)

    def update_task_status(self, task_id: str, new_status: str):
        """
        Update the status of a task and log the event.

        Parameters:
        - task_id (str): The ID of the task to update.
        - new_status (str): The new status of the task (e.g., 'completed', 'failed', 'in_progress').
        """
        task_found = False

        for task in self.tasks:
            if task["task_id"] == task_id:
                task["status"] = new_status
                task_found = True
                # Log the task update
                self.log_event(
                    "info",
                    f"🔄 Task '{task['task_name']}' status updated to '{new_status}'.",
                )
                break

        if not task_found:
            self.log_event(
                "error", f"❌ Task with ID '{task_id}' not found in the task list."
            )

        # Additional logging for completed or failed tasks
        if new_status == "completed":
            self.log_event("info", f"✅ Task '{task_id}' completed successfully.")
        elif new_status == "failed":
            self.log_event("error", f"⚠️ Task '{task_id}' failed.")

    def get_pending_tasks(self):
        """
        Retrieve a list of tasks that are still pending.

        Returns:
        - list: A list of pending tasks.
        """
        return [task for task in self.tasks if task["status"] == "pending"]

    def has_pending_tasks(self) -> bool:
        """Check if there are any pending tasks."""
        for task in self.tasks:
            if task.get("status") != "completed":
                return True
        return False

    def get_task_by_id(self, task_id: str):
        """
        Retrieve a task by its ID.

        Parameters:
        - task_id (str): The unique ID of the task.

        Returns:
        - dict: The task object if found, otherwise None.
        """
        for task in self.tasks:
            if task["task_id"] == task_id:
                return task
        return None

    def log_task_checklist(self):
        """
        Logs the tasks in a checklist format, displaying their status with corresponding symbols.
        """
        task_messages = []

        # Get all pending tasks from TaskManager
        pending_tasks = self.get_pending_tasks()

        if pending_tasks:
            self.log_event("info", f"🔢 Number of pending tasks: {len(pending_tasks)}")

            for task in pending_tasks:
                task_id = task.get("task_id", "N/A")
                task_name = task.get("task_name", "Unnamed Task")
                task_status = task.get("status", "NO_STATUS")

                # Map statuses to checklist symbols
                status_symbol = get_status_symbol(task_status)

                # Create the checklist message for the task
                task_message = f"{status_symbol} Task ID: {task_id}, Task Name: {task_name}, Status: {task_status}"
                self.log_event("info", task_message)
                task_messages.append(task_message)

        return task_messages

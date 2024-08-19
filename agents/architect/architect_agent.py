from agents.react_agent import ReactAgent
from utils import task_utils
from typing import Any, Dict


class ArchitectAgent(ReactAgent):
    
    def get_status_symbol(self, task_status):
        """
        Returns the corresponding symbol for the given task status.

        Args:
            task_status (str): The status of the task.

        Returns:
            str: The symbol representing the task status.
        """
        status_mapping = {
            "completed": "✅",
            "pending": "⏳",
            "failed": "❌",
        }
        return status_mapping.get(task_status, "❔")

    def log_task_checklist(self):
        """
        Logs the tasks in a checklist format, displaying their status with corresponding symbols.
        """
        if self.has_pending_tasks():
            # Log the total number of tasks
            self.log_event("info", f"🔢 Number of pending tasks: {len(self.tasks)}")

            # Iterate through tasks and log them in a checklist format
            for task in self.tasks:
                task_id = task.get("task_id", "N/A")
                task_name = task.get("task_name", "Unnamed Task")
                task_status = task.get("status", "NO_STATUS")

                # Map statuses to checklist symbols
                status_symbol = self.get_status_symbol(task_status)

                # Log the task as a checklist item
                self.log_event(
                    "info", f"{status_symbol} Task ID: {task_id}, Task Name: {task_name}"
                )
            
    def has_pending_tasks(self) -> bool:
        """Check if there are any pending tasks."""
        for task in self.tasks:
            if task.get("status") != "completed":
                return True
        return False

    def invoke(self, user_request: str) -> Dict[str, Any]:
        """Main invoke method to handle plan generation and task execution."""
        self.log_event("start", "")

        # Retrieve all pending tasks
        self.tasks = task_utils.get_pending_tasks(self.state, self.role)

        if not self.tasks:
            # If no more pending tasks, break the loop
            self.log_event("info", "✅ All tasks are completed.")

        while self.has_pending_tasks():
            
            # Print the total number of tasks
            # self.log_event("info", f"🔢 Number of pending tasks: {len(self.tasks)}")
            self.log_task_checklist()

            # Process each pending task one by one
            for task in self.tasks:
                task_id = task.get("task_id", "N/A")
                task_name = task.get("task_name", "Unnamed Task")

                self.log_event(
                    "info",
                    f"\n\n### 📝 Working on Task ID: {task_id} - {task_name}\n\n",
                )
                # Reason and act on the pending task
                result = self._reason_and_act(user_request, task)

                # Check if the task was completed successfully
                if result:
                    # Update the task status to 'completed'
                    self.update_task_status(task["task_id"], "completed")
                    self.update_state(f"{self.role}_response", result)
                else:
                    # Handle task failure, potentially reattempt or mark as failed
                    self.update_task_status(task["task_id"], "failed")
                    self.log_event(
                        "error",
                        f"❌ Task {task_name} failed. Reason: {result.get('reason', 'Unknown error')}",
                    )
                    break  # Optional: break if a task fails, or continue to next task

        # Return the final state after all tasks are completed or failed
        return self.state

from agents.react_agent import ReactAgent
from utils import task_utils
from typing import Any, Dict


class ArchitectAgent(ReactAgent):

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
            # print(self.tasks)
            # Print the total number of tasks
            self.log_event("info", f"🔢 Number of pending tasks: {len(self.tasks)}")

            # Process each pending task one by one
            for task in self.tasks:
                task_id = task.get("task_id", "N/A")
                task_name = task.get("task_name", "Unnamed Task")
                self.log_event("info", f"📋 Task ID: {task_id}, Task Name: {task_name}")

                self.log_event(
                    "info",
                    f"\n\n### 📝 Working on Task ID: {task_id} - {task_name}",
                )
                # Reason and act on the pending task
                result = self._reason_and_act(user_request, task)

                # Check if the task was completed successfully
                if result:
                    # Update the task status to 'completed'
                    self.update_task_status(task["task_id"], "completed")
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

from agents.react_agent import ReactAgent
from utils import task_utils
from typing import Any, Dict


class ArchitectAgent(ReactAgent):

    def invoke(self, user_request: str) -> Dict[str, Any]:
        """Main invoke method to handle plan generation and task execution."""
        self.log_event("start", "")

        while True:
            # Retrieve all pending tasks
            self.tasks = task_utils.get_pending_tasks(self.state, self.role)

            if not self.tasks:
                # If no more pending tasks, break the loop
                self.log_event("info", "✅ All tasks are completed.")
                break

            # Print the total number of tasks
            self.log_event("info", f"🔢 Number of pending tasks: {len(self.tasks)}")

            # Print details of each task (name and ID)
            for task in self.tasks:
                task_id = task.get("task_id", "N/A")
                task_name = task.get("task_name", "Unnamed Task")
                self.log_event("info", f"📋 Task ID: {task_id}, Task Name: {task_name}")

            # Process each pending task one by one
            for task in self.tasks:
                self.log_event(
                    "info",
                    f"\n\n### 📝 Working on Task ID: {task['task_id']} - {task['task_name']}",
                )
                # Reason and act on the pending task
                result = self._reason_and_act(user_request, task)

                # Check if the task was completed successfully
                if result:
                    # Update the task status to 'completed'
                    self.update_task_status(task["task_id"], "completed")
                    self.log_event(
                        "info", f" Task {task['task_name']} completed successfully."
                    )
                else:
                    # Handle task failure, potentially reattempt or mark as failed
                    self.update_task_status(task["task_id"], "failed")
                    self.log_event(
                        "error",
                        f"❌ Task {task['task_name']} failed. Reason: {result.get('reason', 'Unknown error')}",
                    )
                    break  # Optional: break if a task fails, or continue to next task

        # Return the final state after all tasks are completed or failed
        return self.state

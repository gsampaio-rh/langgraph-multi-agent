from agents.react_agent import ReactAgent
from utils import task_utils
from typing import Any, Dict

class EngineerAgent(ReactAgent):

    def invoke(self, user_request: str) -> Dict[str, Any]:
        """Main invoke method to handle plan generation and task execution."""
        self.log_event("start", "")

        # Retrieve all pending tasks from TaskManager
        self.task_manager.tasks = task_utils.get_pending_tasks(self.state, self.role)

        if not self.task_manager.has_pending_tasks():
            self.log_event("info", "✅ All tasks are completed.")
            return self.state

        while self.task_manager.has_pending_tasks():
            # Log and display the task checklist
            task_checklist = self.task_manager.log_task_checklist()

            # Process each pending task one by one
            for task in self.task_manager.tasks:
                task_id = task.get("task_id", "N/A")
                task_name = task.get("task_name", "Unnamed Task")

                self.log_event(
                    "info",
                    f"\n\n### 📝 Working on Task ID: {task_id} - {task_name}\n\n",
                )
                # Reason and act on the pending task
                result = self._reason_and_act(task_checklist, task)

                # Check if the task was completed successfully
                if result:
                    # Update the task status to 'completed' via TaskManager
                    self.task_manager.update_task_status(task["task_id"], "completed")
                    self.state_manager.update_state(f"{self.role}_response", result)
                else:
                    # Handle task failure, potentially reattempt or mark as failed
                    self.task_manager.update_task_status(task["task_id"], "failed")
                    self.log_event(
                        "error",
                        f"❌ Task {task_name} failed. Reason: {result.get('reason', 'Unknown error')}",
                    )
                    break  # Optional: break if a task fails, or continue to the next task

        # Return the final state after all tasks are completed or failed
        return self.state

from agents.react_agent import ReactAgent
from utils import task_utils
from typing import Any, Dict

class ArchitectAgent(ReactAgent):

    def invoke(self, user_request: str) -> Dict[str, Any]:
        """Main invoke method to handle plan generation and task execution."""
        self.log_event("start", "")
        pending_task = self._get_pending_task()

        if not pending_task:
            self.log_event("error", "No pending task available.")
            return self.state

        # Continuously reason and act on the task until a final answer is reached.
        self._reason_and_act(user_request, pending_task)

        return self.state

    def _get_pending_task(self) -> dict:
        """Retrieve the first pending task for the architect."""
        try:
            return task_utils.get_first_pending_task(self.state, self.role)
        except ValueError as e:
            # Handle the case where no pending tasks are found
            self.log_event("error", f"No pending tasks found: {str(e)}")
            return None

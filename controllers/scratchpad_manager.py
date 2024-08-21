# controllers/scratchpad_manager.py

class ScratchpadManager:
    def __init__(self):
        self.scratchpad = []

    def add_thought(self, thought: str):
        """
        Add a new thought to the scratchpad.
        """
        self.scratchpad.append(thought)

    def get_scratchpad(self) -> str:
        """
        Retrieve the entire scratchpad as a single formatted string.
        """
        return "\n".join(self.scratchpad)

    def reset_scratchpad(self):
        """
        Reset the scratchpad by clearing all stored thoughts.
        """
        self.scratchpad.clear()

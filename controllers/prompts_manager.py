# controllers/prompts_manager.py
from builders.prompt_builder import PromptBuilder


class PromptManager:
    def __init__(self, agent_descriptions: str):
        self.agent_descriptions = agent_descriptions
        self.prompts = {}

    def load_prompts(self):
        """
        Load and build all necessary prompts at startup.
        This method pre-builds the prompts and stores them for later access.
        """
        print("🛠️  Loading prompts...")

        # Pre-build and cache common prompts
        self.prompts["planner"] = PromptBuilder.build_planner_prompt(
            self.agent_descriptions
        )
        self.prompts["pm"] = PromptBuilder.build_pm_prompt(self.agent_descriptions)
        self.prompts["react"] = PromptBuilder.build_react_prompt()
        self.prompts["researcher"] = PromptBuilder.build_researcher_prompt()
        self.prompts["reviewer"] = PromptBuilder.build_reviewer_prompt()

        print("✅ Prompts loaded successfully.")

    def get_prompt(self, prompt_name: str) -> str:
        """
        Returns a pre-built prompt by name. Raises an exception if the prompt does not exist.
        """
        if prompt_name in self.prompts:
            return self.prompts[prompt_name]
        else:
            raise ValueError(
                f"Prompt '{prompt_name}' not found. Make sure it was loaded properly."
            )

    def build_dynamic_prompt(self, prompt_type: str, **kwargs) -> str:
        """
        Build a dynamic prompt based on the type and provided parameters.
        Delegates to PromptBuilder.
        """
        if prompt_type == "planner":
            return PromptBuilder.build_planner_prompt(self.agent_descriptions, **kwargs)
        elif prompt_type == "pm":
            return PromptBuilder.build_pm_prompt(self.agent_descriptions, **kwargs)
        elif prompt_type == "react":
            return PromptBuilder.build_react_prompt(**kwargs)
        elif prompt_type == "researcher":
            return PromptBuilder.build_researcher_prompt(**kwargs)
        elif prompt_type == "reviewer":
            return PromptBuilder.build_reviewer_prompt(**kwargs)
        else:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

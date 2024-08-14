# prompts/prompt_builder.py
from utils.helpers import get_current_utc_datetime
from config.config import app_config
from prompts.planner_prompt import DEFAULT_SYS_PLANNER_PROMPT

class PromptBuilder:
    @staticmethod
    def build_planner_prompt(user_request: str, feedback_value: str) -> str:
        return DEFAULT_SYS_PLANNER_PROMPT.format(
            agents_description=app_config.get_agents_description(),
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
        )

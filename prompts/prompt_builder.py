# prompts/prompt_builder.py
from utils.helpers import get_current_utc_datetime
from config.config import app_config
from custom_tools import tools_description, tools_names
from prompts.planner_prompt import DEFAULT_SYS_PLANNER_PROMPT
from prompts.pm_prompt import DEFAULT_SYS_PM_PROMPT
from prompts.researcher_prompt import DEFAULT_SYS_RESEACHER_PROMPT

class PromptBuilder:
    @staticmethod
    def build_planner_prompt(user_request: str, feedback_value: str) -> str:
        return DEFAULT_SYS_PLANNER_PROMPT.format(
            agents_description=app_config.get_agents_description(),
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
        )

    @staticmethod
    def build_pm_prompt(
        original_plan: str,
        task_list: str,
        agents_description: str = app_config.get_agents_description(),
    ) -> str:
        return DEFAULT_SYS_PM_PROMPT.format(
            original_plan=original_plan,
            task_list=task_list,
            agents_description=agents_description,
            datetime=get_current_utc_datetime(),
        )

    @staticmethod
    def build_researcher_prompt(
        scratchpad: str = "",
        tools_description: str = tools_description,
        tools_names: str = tools_names,
    ) -> str:
        return DEFAULT_SYS_RESEACHER_PROMPT.format(
            tools_description=tools_description,
            tools_names=tools_names,
            agent_scratchpad=scratchpad,
            datetime=get_current_utc_datetime(),
        )

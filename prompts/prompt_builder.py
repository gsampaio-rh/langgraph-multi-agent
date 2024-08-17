# prompts/prompt_builder.py
from utils.helpers import get_current_utc_datetime
from config.config import app_config
from custom_tools import (
    tool_names,
    tools_description,
    vsphere_tool_names,
    vsphere_tool_descriptions,
)
from prompts.planner_prompt import DEFAULT_SYS_PLANNER_PROMPT
from prompts.pm_prompt import DEFAULT_SYS_PM_PROMPT
from prompts.researcher_prompt import DEFAULT_SYS_RESEARCHER_PROMPT
from prompts.reviewer_prompt import DEFAULT_SYS_REVIEWER_PROMPT
from prompts.architect_prompt import PLAN_AND_EXECUTE_SYS_PROMPT
from prompts.react_agent_prompt import DEFAULT_SYS_REACT_AGENT_PROMPT

class PromptBuilder:
    @staticmethod
    def build_planner_prompt(user_request: str, feedback_value: str = "") -> str:
        return DEFAULT_SYS_PLANNER_PROMPT.format(
            agents_description=app_config.get_agents_description(),
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
        )

    @staticmethod
    def build_pm_prompt(
        original_plan: str,
        task_list: str,
        feedback_value: str = "",
        agents_description: str = app_config.get_agents_description(),
    ) -> str:
        return DEFAULT_SYS_PM_PROMPT.format(
            original_plan=original_plan,
            task_list=task_list,
            agents_description=agents_description,
            vsphere_tool_names=vsphere_tool_names,
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
        )

    @staticmethod
    def build_architect_prompt(
        original_plan: str,
        feedback_value: str = "",
    ) -> str:
        return PLAN_AND_EXECUTE_SYS_PROMPT.format(
            original_plan=original_plan,
            vsphere_tool_names=vsphere_tool_names,
            vsphere_tool_descriptions=vsphere_tool_descriptions,
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
        )

    @staticmethod
    def build_react_prompt(
        original_plan: str,
        scratchpad: str = "",
        tools_description: str = vsphere_tool_descriptions,
        tool_names: str = vsphere_tool_names,
    ) -> str:
        return DEFAULT_SYS_REACT_AGENT_PROMPT.format(
            original_plan=original_plan,
            tools_description=tools_description,
            tool_names=tool_names,
            agent_scratchpad=scratchpad,
            datetime=get_current_utc_datetime(),
        )

    @staticmethod
    def build_researcher_prompt(
        scratchpad: str = "",
        tools_description: str = tools_description,
        tool_names: str = tool_names,
    ) -> str:
        return DEFAULT_SYS_RESEARCHER_PROMPT.format(
            tools_description=tools_description,
            tool_names=tool_names,
            agent_scratchpad=scratchpad,
            datetime=get_current_utc_datetime(),
        )

    @staticmethod
    def build_reviewer_prompt(
        task: dict
    ) -> str:
        return DEFAULT_SYS_REVIEWER_PROMPT.format(
            original_task=task,
            datetime=get_current_utc_datetime(),
        )

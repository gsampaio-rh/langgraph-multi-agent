# prompts/prompt_builder.py
from utils.helpers import get_current_utc_datetime
from config.app_config import app_config
from tools import (
    vsphere_tool_names,
    openshift_tool_names,
)
from tools.tool_registry import (
    get_tool_descriptions_by_category,
    get_tool_names_by_category,
)
from prompts.planner_prompt import DEFAULT_SYS_PLANNER_PROMPT
from prompts.pm_prompt import DEFAULT_SYS_PM_PROMPT
from prompts.architect_prompt import DEFAULT_SYS_ARCHITECT_REACT_PROMPT
from prompts.reviewer_prompt import DEFAULT_SYS_REVIEWER_PROMPT
from prompts.react_agent_prompt import DEFAULT_SYS_REACT_AGENT_PROMPT
from prompts.engineer_prompt import DEFAULT_SYS_ENGINEER_PROMPT, DEFAULT_SYS_ENGINEER_REFLECT_PROMPT

class PromptBuilder:
    openshift_tool_names = get_tool_names_by_category("openshift")
    openshift_tool_descriptions = get_tool_descriptions_by_category("openshift")

    vsphere_tool_names = get_tool_names_by_category("vsphere_lifecycle")
    vsphere_tool_descriptions = get_tool_descriptions_by_category("vsphere_lifecycle")

    @staticmethod
    def build_planner_prompt(
        user_request: str, 
        feedback_value: str = "",
        agents_description: str = app_config.agents_config.agents_description,
    ) -> str:
        return DEFAULT_SYS_PLANNER_PROMPT.format(
            agents_description=agents_description,
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
        )

    @staticmethod
    def build_pm_prompt(
        original_tasks_list: str,
        feedback_value: str = "",
        agents_description: str = app_config.agents_config.agents_description,
    ) -> str:
        return DEFAULT_SYS_PM_PROMPT.format(
            original_tasks_list=original_tasks_list,
            agents_description=agents_description,
            vsphere_tool_names=vsphere_tool_names,
            openshift_tool_names=openshift_tool_names,
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
        )

    @staticmethod
    def build_architect_prompt(
        task: str,
        task_description: str,
        acceptance_criteria: str,
        vsphere_tool_names: str = vsphere_tool_names,
        vsphere_tool_descriptions: str = vsphere_tool_descriptions,
        scratchpad: str = "",
        feedback_value: str = "",
    ) -> str:
        return DEFAULT_SYS_ARCHITECT_REACT_PROMPT.format(
            task=task,
            task_description=task_description,
            acceptance_criteria=acceptance_criteria,
            vsphere_tool_names=vsphere_tool_names,
            vsphere_tool_descriptions=vsphere_tool_descriptions,
            agent_scratchpad=scratchpad,
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
        )

    @staticmethod
    def build_react_prompt(
        task: str,
        task_description: str,
        acceptance_criteria: str,
        tool_names: str = vsphere_tool_names,
        tool_descriptions: str = vsphere_tool_descriptions,
        scratchpad: str = "",
        feedback_value: str = "",
    ) -> str:
        return DEFAULT_SYS_REACT_AGENT_PROMPT.format(
            task=task,
            task_description=task_description,
            acceptance_criteria=acceptance_criteria,
            tool_names=tool_names,
            tool_descriptions=tool_descriptions,
            agent_scratchpad=scratchpad,
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
        )

    @staticmethod
    def build_engineer_prompt(
        task: str,
        task_description: str,
        acceptance_criteria: str,
        tool_names: str = vsphere_tool_names,
        tool_descriptions: str = vsphere_tool_descriptions,
        scratchpad: str = "",
    ) -> str:
        return DEFAULT_SYS_ENGINEER_PROMPT.format(
            task=task,
            task_description=task_description,
            acceptance_criteria=acceptance_criteria,
            tool_names=tool_names,
            tool_descriptions=tool_descriptions,
            agent_scratchpad=scratchpad,
            datetime=get_current_utc_datetime(),
        )

    @staticmethod
    def build_engineer_reflect_prompt(
        task: str,
        task_description: str,
        acceptance_criteria: str,
        scratchpad: str = "",
    ) -> str:
        return DEFAULT_SYS_ENGINEER_REFLECT_PROMPT.format(
            task=task,
            task_description=task_description,
            acceptance_criteria=acceptance_criteria,
            agent_scratchpad=scratchpad,
            datetime=get_current_utc_datetime(),
        )

    @staticmethod
    def build_reviewer_prompt(
        original_task: dict,
        feedback_value: str = "",
    ) -> str:
        return DEFAULT_SYS_REVIEWER_PROMPT.format(
            original_task=original_task,
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
        )

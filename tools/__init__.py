from langchain.tools.render import render_text_description_and_args
from tools.general.website_crawl import website_crawl, extract_content
from tools.general.duck_search import duckSearch
from tools.general.wiki_query import wiki
from tools.general.arxiv_query import arxiv
from tools.vsphere.vm_lifecycle_manager import (
    list_vms,
    retrieve_vm_details,
    ensure_vms_not_running,
)

from tools.openshift.openshift_tools import (
    ensure_openshift_project_access,
    ensure_openshift_providers_ready,
    create_migration_plan_tool,
    start_migration_tool
)

# Expose all tools in a list for easier import
custom_tools = [duckSearch, wiki, arxiv, website_crawl, extract_content]

# Create a list of tool names
tool_names = [tool.name for tool in custom_tools]

# Generate the tools description (already in your code)
tools_description = (
    render_text_description_and_args(custom_tools)
    .replace("{", "{{")
    .replace("}", "}}")
)

# VSPHERE
vsphere_tools = [
    list_vms,
    retrieve_vm_details,
    ensure_vms_not_running
]

# Create a list of tool names
vsphere_tool_names = [tool.name for tool in vsphere_tools]

# Create a list of tool descriptions
vsphere_tool_descriptions = (
    render_text_description_and_args(vsphere_tools)
    .replace("{", "{{")
    .replace("}", "}}")
)

# OPENSHIFT

openshift_tools = [
    ensure_openshift_project_access,
    ensure_openshift_providers_ready,
    create_migration_plan_tool,
    start_migration_tool
]

# Create a list of tool names
openshift_tool_names = [tool.name for tool in openshift_tools]

# Create a list of tool descriptions
openshift_tool_descriptions = (
    render_text_description_and_args(openshift_tools)
    .replace("{", "{{")
    .replace("}", "}}")
)

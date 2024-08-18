from langchain.tools.render import render_text_description_and_args
from custom_tools.website_crawl import website_crawl, extract_content
from custom_tools.duck_search import duckSearch
from custom_tools.wiki_query import wiki
from custom_tools.arxiv_query import arxiv
from custom_tools.vsphere.network_configuration_manager import (
    network_configuration_manager,
)
from custom_tools.vsphere.storage_configuration_manager import (
    storage_configuration_manager,
)
from custom_tools.vsphere.vm_lifecycle_manager import (
    vm_lifecycle_manager,
)


# Expose all tools in a list for easier import
custom_tools = [duckSearch, wiki, arxiv, website_crawl, extract_content]

# Create a list of tool names
tool_names = [tool.name for tool in custom_tools]

# Generate the tools description (already in your code)
tools_description = (
    render_text_description_and_args(custom_tools).replace("{", "{{").replace("}", "}}")
)

vsphere_tools = [
    vm_lifecycle_manager,
    network_configuration_manager,
    storage_configuration_manager,
]

# Create a list of tool names
vsphere_tool_names = [tool.name for tool in vsphere_tools]

vsphere_tool_descriptions = (
    render_text_description_and_args(vsphere_tools)
    .replace("{", "{{")
    .replace("}", "}}")
)

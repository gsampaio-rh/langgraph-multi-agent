# tool_registry.py

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

# Register tools by name and module
tool_registry = {
    "website_crawl": website_crawl,
    "extract_content": extract_content,
    "duck_search": duckSearch,
    "wiki": wiki,
    "arxiv": arxiv,
    "vm_lifecycle_manager": vm_lifecycle_manager,
    "network_configuration_manager": network_configuration_manager,
    "storage_configuration_manager": storage_configuration_manager,
}


def get_tool_by_name(tool_name):
    return tool_registry.get(tool_name, None)

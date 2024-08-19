# tool_registry.py

from custom_tools.general.website_crawl import website_crawl, extract_content
from custom_tools.general.duck_search import duckSearch
from custom_tools.general.wiki_query import wiki
from custom_tools.general.arxiv_query import arxiv
from custom_tools.vsphere.vm_lifecycle_manager import (
    list_vms,
    retrieve_vm_details,
    ensure_vms_not_running
)
from custom_tools.openshift.openshift_tools import ensure_openshift_project_access

# Register tools by name and module
tool_registry = {
    "website_crawl": website_crawl,
    "extract_content": extract_content,
    "duck_search": duckSearch,
    "wiki": wiki,
    "arxiv": arxiv,
    "list_vms": list_vms,
    "retrieve_vm_details": retrieve_vm_details,
    "ensure_vms_not_running": ensure_vms_not_running,
    "ensure_openshift_project_access": ensure_openshift_project_access,
}


def get_tool_by_name(tool_name):
    return tool_registry.get(tool_name, None)

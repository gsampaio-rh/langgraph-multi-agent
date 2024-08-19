from langchain.tools import tool
from config.config import app_config
from utils.vsphere_utils import (
    get_all_vms,
    connect_to_vsphere,
    disconnect_from_vsphere,
    get_all_vm_details,
)

@tool(parse_docstring=True)
def list_vms():
    """
    A wrapper around a vSphere utility for listing all available virtual machines (VMs). Useful for retrieving a list of VMs from the connected vSphere environment. Input: None. Returns: A list of VM names or an error message if the operation fails.
    
    Input: 
        None
    Returns: 
        A list of VM names or an error message if the operation fails.
    """
    si = None
    try:
        # Connect to vSphere
        si, content = connect_to_vsphere(
            host=app_config.vsphereConfig.host,
            user=app_config.vsphereConfig.user,
            pwd=app_config.vsphereConfig.pwd,
        )

        vms = get_all_vms(si, content)
        return vms

    except Exception as e:
        return f"Failed to list vms. {str(e)}"

    finally:
        if si:
            disconnect_from_vsphere(si)


@tool(parse_docstring=True)
def retrieve_vm_details():
    """
    A wrapper around a vSphere utility for extracting detailed information about virtual machines (VMs). Useful for retrieving VM operating systems, resource allocations, and network configurations. Input: None. Returns: A list of dictionaries containing VM details or an error message if the operation fails.
    
    Input: 
        None
    Returns: 
        A list of dictionaries containing VM details or an error message if the operation fails.
    """
    si = None
    try:
        # Connect to vSphere
        si, content = connect_to_vsphere(
            host=app_config.vsphereConfig.host,
            user=app_config.vsphereConfig.user,
            pwd=app_config.vsphereConfig.pwd,
        )

        # Get details of all VMs
        vm_details = get_all_vm_details(content)
        return vm_details

    except Exception as e:
        return f"Failed to retrieve VM details. {str(e)}"

    finally:
        if si:
            disconnect_from_vsphere(si)

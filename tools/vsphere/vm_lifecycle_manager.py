from langchain.tools import tool
from typing import Union, List, Dict
from config.app_config import app_config
from utils.vsphere_utils import (
    get_all_vms,
    connect_to_vsphere,
    disconnect_from_vsphere,
    get_vm_details,
    get_vm_by_name,
    verify_vms_not_running,
)

@tool(parse_docstring=True)
def list_vms() -> Union[List[str], str]:
    """
    A wrapper around a vSphere utility for listing all available virtual machines (VMs). Useful for retrieving a list of VMs from the connected vSphere environment.

    Returns:
        vms: A list of VM names or an error message if the operation fails.
    """
    si = None
    try:
        # Connect to vSphere
        si, content = connect_to_vsphere(
            host=app_config.vsphereConfig.host,
            user=app_config.vsphereConfig.user,
            pwd=app_config.vsphereConfig.pwd,
        )

        vms, vm_names = get_all_vms(si, content)
        return vm_names

    except Exception as e:
        return f"Failed to list vms. {str(e)}"

    finally:
        if si:
            disconnect_from_vsphere(si)


@tool(parse_docstring=True)
def retrieve_vm_details(vm_name: str) -> Union[Dict[str, Union[str, int, list]], str]:
    """
    A wrapper around a vSphere utility for extracting detailed information about a specific virtual machine (VM). Useful for retrieving the VM's operating system, resource allocations, and network configurations based on the provided VM name.

    Args:
        vm_name: The name of the virtual machine to retrieve details for.

    Returns:
        vm_details: A dictionary containing VM details or an error message if the operation fails or the VM is not found.
    """
    si = None
    try:
        # Connect to vSphere
        si, content = connect_to_vsphere(
            host=app_config.vsphereConfig.host,
            user=app_config.vsphereConfig.user,
            pwd=app_config.vsphereConfig.pwd,
        )

        # Find the VM by name
        vm = get_vm_by_name(content, vm_name)

        if not vm:
            return f"VM '{vm_name}' not found."

        # Get detailed information about the found VM
        vm_details = get_vm_details(vm)
        return vm_details

    except Exception as e:
        return f"Failed to retrieve details for VM '{vm_name}': {str(e)}"

    finally:
        if si:
            disconnect_from_vsphere(si)


@tool(parse_docstring=True)
def ensure_vms_not_running(vm_names: List[str]) -> Union[bool, str]:
    """
    A wrapper around a vSphere utility for ensuring that multiple virtual machines (VMs) are not running if 'warm' migration is not supported.
    If warm migration is not supported, the VMs will be powered off if they are running.

    Args:
        vm_names: A list of virtual machine names to check.

    Returns:
        bool: True if the operation was successful.
        str: An error message if the operation fails.
    """
    si = None
    try:
        # Connect to vSphere
        si, content = connect_to_vsphere(
            host=app_config.vsphereConfig.host,
            user=app_config.vsphereConfig.user,
            pwd=app_config.vsphereConfig.pwd,
        )

        # Use the utility function to ensure VMs are not running
        verify_vms_not_running(vm_names, si, content)

        # If the operation succeeds, return True
        return True

    except Exception as e:
        # If an error occurs, return a detailed error message
        return f"Failed to ensure VMs are not running: {str(e)}"

    finally:
        if si:
            disconnect_from_vsphere(si)

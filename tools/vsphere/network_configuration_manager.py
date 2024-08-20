from langchain.tools import tool
from utils.vsphere_utils import (
    get_vm_network_details,
    change_vm_network,
    connect_to_vsphere,
    disconnect_from_vsphere,
)


@tool(parse_docstring=True)
def network_configuration_manager(vm_name: str, action: str, new_network: str = None
) -> str:
    """
    Manages network configuration for a specific VM, including retrieving and updating network details.

    Args:
        vm_name: The name of the VM to perform the network action on.
        action: The network action to perform (e.g., 'get_network', 'change_network').
        new_network: The new network to assign to the VM when 'change_network' action is used.

    Returns:
        str: A success message for the performed network action.
    """

    si = None

    try:
        # Connect to vSphere
        si = connect_to_vsphere(host, user, pwd)

        # Perform the requested network action
        if action == "get_network":
            return get_vm_network_details(si, vm_name)
        elif action == "change_network":
            if not new_network:
                raise ValueError(
                    "new_network must be provided for 'change_network' action."
                )
            return change_vm_network(si, vm_name, new_network)
        else:
            raise ValueError(f"Unsupported action: {action}")

    except Exception as e:
        return f"Failed to execute {action} on VM '{vm_name}': {str(e)}"

    finally:
        if si:
            disconnect_from_vsphere(si)

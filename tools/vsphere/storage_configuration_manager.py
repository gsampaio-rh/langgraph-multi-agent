from langchain.tools import tool
from utils.vsphere_utils import (
    get_vm_storage_details,
    change_vm_storage,
    list_datastores,
    connect_to_vsphere,
    disconnect_from_vsphere,
)


@tool(parse_docstring=True)
def storage_configuration_manager(vm_name: str, action: str, new_datastore: str = None
) -> str:
    """
    Manages storage configuration for a specific VM, including retrieving and updating storage details.

    Args:
        vm_name: The name of the VM to perform the storage action on.
        action: The storage action to perform (e.g., 'get_storage', 'change_storage', 'list_datastores').
        new_datastore: The new datastore to assign to the VM when 'change_storage' action is used.

    Returns:
        str: A success message for the performed storage action or an error message in case of failure.
    """

    si = None
    try:
        # Connect to vSphere
        si = connect_to_vsphere()

        # Perform the requested storage action
        if action == "get_storage":
            return get_vm_storage_details(si, vm_name)
        elif action == "change_storage":
            if not new_datastore:
                raise ValueError(
                    "new_datastore must be provided for 'change_storage' action."
                )
            return change_vm_storage(si, vm_name, new_datastore)
        elif action == "list_datastores":
            return list_datastores(si)
        else:
            raise ValueError(f"Unsupported action: {action}")

    except Exception as e:
        return f"Failed to execute {action} on VM '{vm_name}': {str(e)}"

    finally:
        if si:
            disconnect_from_vsphere(si)

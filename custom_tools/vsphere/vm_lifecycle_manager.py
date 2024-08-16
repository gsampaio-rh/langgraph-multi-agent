from langchain.tools import tool
from utils.vsphere_utils import (
    power_off_vm,
    power_on_vm,
    create_vm_snapshot,
    delete_vm_snapshot,
    revert_vm_to_snapshot,
    migrate_vm,
    validate_vm_compatibility,
    connect_to_vsphere,
    disconnect_from_vsphere,
)


@tool(parse_docstring=True)
def vm_lifecycle_manager(
    vm_name: str,
    action: str,
    snapshot_name: str = None,
    target_host: str = None,
) -> str:
    """
    Manages VM lifecycle operations such as powering on/off, snapshot creation, migration, and more.

    Args:
        vm_name: The name of the VM to perform the action on.
        action: The lifecycle action to perform (e.g., 'power_on', 'power_off', 'snapshot', 'migrate', 'delete_snapshot', 'revert_snapshot', 'validate').
        snapshot_name: The name of the snapshot for snapshot-related actions (create, delete, revert).
        target_host: The target host for VM migration.

    Returns:
        str: A success message for the performed action, or an error message in case of failure.
    """
    si = None
    try:
        # Connect to vSphere
        si = connect_to_vsphere()

        # Perform the requested action
        if action == "power_on":
            return power_on_vm(si, vm_name)
        elif action == "power_off":
            return power_off_vm(si, vm_name)
        elif action == "snapshot":
            if not snapshot_name:
                raise ValueError(
                    "snapshot_name must be provided for 'snapshot' action."
                )
            return create_vm_snapshot(si, vm_name, snapshot_name)
        elif action == "migrate":
            if not target_host:
                raise ValueError("target_host must be provided for 'migrate' action.")
            return migrate_vm(si, vm_name, target_host)
        elif action == "delete_snapshot":
            if not snapshot_name:
                raise ValueError(
                    "snapshot_name must be provided for 'delete_snapshot' action."
                )
            return delete_vm_snapshot(si, vm_name, snapshot_name)
        elif action == "revert_snapshot":
            if not snapshot_name:
                raise ValueError(
                    "snapshot_name must be provided for 'revert_snapshot' action."
                )
            return revert_vm_to_snapshot(si, vm_name, snapshot_name)
        elif action == "validate":
            return validate_vm_compatibility(si, vm_name)
        else:
            raise ValueError(f"Unsupported action: {action}")

    except Exception as e:
        return f"Failed to execute {action} on VM '{vm_name}': {str(e)}"

    finally:
        if si:
            disconnect_from_vsphere(si)

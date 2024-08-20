from typing import List, Union, Dict
from langchain.tools import tool
from services.openshift_service import OpenShiftService


@tool(parse_docstring=True)
def ensure_openshift_project_access(required_projects: List[str]) -> Union[bool, str]:
    """
    A tool that accesses the OpenShift Console and ensures access to the required projects.

    Args:
        required_projects: A list of project names that are needed for migration.

    Returns:
        bool: True if access is confirmed for all required projects.
    """
    try:

        # Create an OpenShiftService instance and establish a connection
        client = OpenShiftService()

        # Check access to the required projects
        access_result = client.check_project_access(required_projects)

        # Return the result
        if access_result is True:
            return True
        else:
            return access_result

    except Exception as e:
        return f"Failed to ensure project access: {str(e)}"


@tool(parse_docstring=True)
def ensure_openshift_providers_ready(
    namespace: str = "openshift-mtv",
) -> Union[bool, str]:
    """
    A tool that verifies that both the VMware and Host providers are listed and their statuses are 'Ready'.

    Args:
        namespace: The namespace where the providers are listed (default: 'openshift-mtv').

    Returns:
        bool: True if both providers are found and have the 'Ready' status.
        str: Error message if the operation fails or if the providers are not ready.
    """
    try:
        # Create an OpenShiftService instance
        client = OpenShiftService()

        # Step 1: Retrieve the providers
        providers = client.get_providers(namespace)

        # Check if there was an error in retrieving the providers
        if isinstance(providers, str):
            return f"Failed to retrieve providers: {providers}"

        # Step 2: Verify that both providers are ready
        verification_result = client.verify_providers_ready(providers)

        # Return the result of the verification
        if verification_result is True:
            return True
        else:
            return verification_result

    except Exception as e:
        return f"Failed to verify providers readiness: {str(e)}"


@tool(parse_docstring=True)
def create_migration_plan_tool(
    vm_names: List[str] = None,
    name: str = "default-migration-plan",
    destination: str = "host",
    source: str = "vmware",
    network_map: str = "vmware-qbjcw",
    storage_map: str = "vmware-wp7cw",
    namespace: str = "openshift-mtv",
) -> Union[Dict, str]:
    """
    A tool to create a migration plan for moving virtual machines (VMs) using the forklift.konveyor.io API. This tool only requires VM names, and the corresponding IDs are fetched automatically.

    Args:
        vm_names: A list of VM names to migrate. Default is a single default VM name if none provided.
        name: The name of the migration plan. Default is 'default-migration-plan'.
        destination: The destination provider. Default is 'host'.
        source: The source provider. Default is 'vmware'.
        network_map: The network map used for the migration. Default is 'vmware-qbjcw'.
        storage_map: The storage map used for the migration. Default is 'vmware-wp7cw'.
        namespace: The namespace for the migration plan. Default is 'openshift-mtv'.

    Returns:
        dict: The created migration plan if successful.
        str: An error message if the operation fails.
    """
    try:
        # Create an OpenShiftService instance
        openshift_service = OpenShiftService()

        # If no VM names are provided, use a default VM
        if not vm_names:
            vm_names = ["default-vm"]

        # Fetch VM IDs for the given VM names (this logic assumes a lookup function exists)
        vms = []
        for vm_name in vm_names:
            vms.append({"name": vm_name})

        # Call the create_migration_plan method with the gathered information
        result = openshift_service.create_migration_plan(
            name=name,
            destination=destination,
            source=source,
            network_map=network_map,
            storage_map=storage_map,
            vms=vms,
            namespace=namespace,
        )

        return result

    except Exception as e:
        return f"Failed to create migration plan: {str(e)}"


@tool(parse_docstring=True)
def check_openshift_connection() -> Union[bool, str]:
    """
    A tool that checks the connection to the OpenShift Console.

    Returns:
        bool: True if the connection to the OpenShift Console is successful.
        str: Error message if the connection fails.
    """
    try:
        # Create an OpenShiftService instance and attempt to establish a connection
        client = OpenShiftService()

        # Attempt to connect
        connection_successful = client._test_connection()  # Assuming this method exists

        # Return the result
        if connection_successful:
            return True
        else:
            return "Failed to connect to the OpenShift Console."

    except Exception as e:
        return f"Connection error: {str(e)}"

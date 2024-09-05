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
    vm_names: List[str],
    name: str,
    source: str = "vmware",
) -> Union[Dict, str]:
    """
    A tool to create a migration plan for moving virtual machines (VMs) using the forklift.konveyor.io API. This tool only requires VM names, and the corresponding IDs are fetched automatically.

    Args:
        vm_names: A list of VM names to migrate. This arg is mandatory.
        name: The name of the migration plan. This arg is mandatory.
        source: The source provider. Default is 'vmware'.

    Returns:
        dict: The created migration plan if successful.
        str: An error message if the operation fails.
    """
    try:
        # Create an OpenShiftService instance
        openshift_service = OpenShiftService()
        print("\n1/5 Connected to Openshift...\n")

        # Automatically lookup the provider UUID based on the source provider name
        vmware_provider_uuid = openshift_service.lookup_provider_uuid_by_name(
            provider_name="vmware", 
            provider_type="vsphere"
        )
        if isinstance(vmware_provider_uuid, str) and "Error" in vmware_provider_uuid:
            return vmware_provider_uuid  # Return the error if we encountered one

        if vmware_provider_uuid is None:
            return f"Provider '{source}' not found."
        print(f"\n2/5 Now I have the provider {vmware_provider_uuid}...\n")

        # If no VM names are provided, use a default VM
        if vm_names is None:
            return f"Failed to create migration plan: No VM was provided!"

        # Fetch VM IDs for the given VM names
        vms = []
        for vm_name in vm_names:
            vm_id = openshift_service.lookup_vm_id_by_name(
                vmware_provider_uuid, vm_name
            )

            # Assuming error messages are distinct, e.g., returned as dicts or special error codes
            if isinstance(vm_id, dict) and 'error' in vm_id:
                return vm_id['error']  # This handles the error case

            # Check if VM was found
            if vm_id:
                vms.append({"id": vm_id, "name": vm_name})
            else:
                return f"VM '{vm_name}' not found."

        print(f"\n3/5 Now I have all the VM Names and all the VM IDs {vms}...\n")

        network_map, n_uid, network_map_name = openshift_service.create_network_map()
        storage_map, s_uid, storage_map_name = openshift_service.create_storage_map()

        print(f"\n4/5 Now I have the Storage and Network maps {vms}...\n")

        # Call the create_migration_plan method with the gathered information
        result = openshift_service.create_migration_plan(
            network_map_uid=n_uid,
            network_map_name=network_map_name,
            storage_map_uid=s_uid,
            storage_map_name=storage_map_name,
            name=name,
            source=source,
            vms=vms,
        )

        print(f"\n5/5 Migration plan RESPONSE - {result}...\n")
        return result

    except Exception as e:
        return f"Failed to create migration plan: {str(e)}"


@tool(parse_docstring=True)
def start_migration_tool(
    plan_name: str, namespace: str = "openshift-mtv"
) -> Union[Dict, str]:
    """
    A tool to start a migration for a given migration plan by its name.

    Args:
        plan_name: The name of the migration plan. The value should consist of lower case alphanumeric characters, '-' or '.', and must start and end with an alphanumeric character (e.g. 'example.com', regex used for validation is '[a-z0-9]([-a-z0-9]*[a-z0-9])?(\\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*').
        namespace: The namespace where the migration plan is located. Default is 'openshift-mtv'.


    Returns:
        dict: The migration start response if successful.
        str: An error message if the operation fails.
    """
    try:
        # Create an OpenShiftService instance
        openshift_service = OpenShiftService()
        print("\n1/4 Connected to Openshift...\n")

        # Retrieve the full migration plan object by its name
        migration_plan = openshift_service.get_migration_plan_by_name(
            plan_name=plan_name, namespace=namespace
        )

        if isinstance(migration_plan, str) and "Error" in migration_plan:
            return migration_plan  # Return the error if we encountered one

        if migration_plan is None:
            return f"Migration plan '{plan_name}' not found."

        # Retrieve the UID of the migration plan
        plan_uid = migration_plan["metadata"]["uid"]
        print(f"\n2/4 Retrieved migration plan UID: {plan_uid}...\n")

        # Check the status conditions to verify if the plan is ready
        ready_status = False
        conditions = migration_plan.get("status", {}).get("conditions", [])
        for condition in conditions:
            if condition.get("type") == "Ready" and condition.get("status") == "True":
                ready_status = True
                break

        if not ready_status:
            return f"Migration plan '{plan_name}' is not ready."

        print(f"\n3/4 Migration plan is ready. Starting migration...\n")

        # Start the migration using the retrieved plan UID
        result = openshift_service.start_migration(
            plan_name=plan_name, plan_uid=plan_uid, namespace=namespace
        )

        print(f"\n4/4 Migration started: {result}...\n")
        return result

    except Exception as e:
        return f"Failed to start migration: {str(e)}"


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

openshift_tools = [
    # ensure_openshift_project_access,
    # ensure_openshift_providers_ready,
    create_migration_plan_tool,
    start_migration_tool,
]

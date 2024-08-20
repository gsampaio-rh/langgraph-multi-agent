from kubernetes import client
from kubernetes.client.rest import ApiException
from typing import List, Dict, Union
from config.config import app_config


class OpenShiftService:
    """
    This service class handles interactions with the OpenShift (Kubernetes-based) API,
    including retrieving namespaces (projects), checking access, retrieving providers,
    and verifying their readiness.
    """

    def __init__(
        self,
        api_url: str = app_config.openshiftConfig.api_url,
        token: str = app_config.openshiftConfig.token,
    ):
        """
        Initializes the OpenShiftService with API URL and token,
        and sets up the connection to the OpenShift cluster.

        Args:
            api_url (str): The API URL of the OpenShift cluster.
            token (str): The Bearer token to authenticate with the OpenShift API.
        """
        try:
            # Set up the Kubernetes API client configuration
            configuration = client.Configuration()
            configuration.host = api_url
            configuration.verify_ssl = False  # Disable SSL verification if needed
            configuration.api_key = {"authorization": f"Bearer {token}"}

            # Use the custom configuration
            client.Configuration.set_default(configuration)

            # Create the CoreV1Api and CustomObjectsApi instances for interacting with resources
            self.core_v1_api = client.CoreV1Api()
            self.custom_objects_api = client.CustomObjectsApi()

            # Test connection by fetching namespaces
            self._test_connection()

        except Exception as e:
            raise Exception(f"Failed to initialize OpenShiftService: {str(e)}")

    def _test_connection(self):
        """
        Tests the connection by attempting to retrieve namespaces (projects).
        """
        try:
            self.core_v1_api.list_namespace()
        except ApiException as e:
            raise Exception(f"Failed to connect to OpenShift API: {str(e)}")

    def get_projects(self) -> Union[List[str], str]:
        """
        Retrieves a list of namespaces (projects) available to the logged-in user on OpenShift.

        Returns:
            List[str]: A list of namespace names if successful.
            str: An error message if the operation fails.
        """
        try:
            namespaces = self.core_v1_api.list_namespace()
            project_list = [ns.metadata.name for ns in namespaces.items]
            return project_list
        except ApiException as e:
            return f"Failed to retrieve namespaces: {str(e)}"

    def check_project_access(self, required_projects: List[str]) -> Union[bool, str]:
        """
        Ensures the user has access to the required namespaces.

        Args:
            required_projects (List[str]): A list of namespace names that are needed for migration.

        Returns:
            bool: True if access is confirmed for all required namespaces.
            str: An error message if the operation fails or access is not available.
        """
        try:
            available_projects = self.get_projects()

            if isinstance(available_projects, str):
                # If the function returned an error message, propagate it
                return available_projects

            missing_projects = [
                proj for proj in required_projects if proj not in available_projects
            ]

            if not missing_projects:
                return True
            else:
                return f"Missing access to the following projects: {', '.join(missing_projects)}"

        except ApiException as e:
            return f"Failed to check project access: {str(e)}"

    def get_providers(self, namespace: str = "openshift-mtv") -> Union[List[dict], str]:
        """
        Retrieves the list of Provider resources in the specified namespace.

        Args:
            namespace (str): The namespace where the providers are listed (default: 'openshift-mtv').

        Returns:
            List[dict]: A list of Provider resources if successful.
            str: An error message if the operation fails.
        """
        try:
            providers = self.custom_objects_api.list_namespaced_custom_object(
                group="forklift.konveyor.io",
                version="v1beta1",
                namespace=namespace,
                plural="providers",
            )
            return providers["items"]
        except ApiException as e:
            return f"Failed to retrieve providers: {str(e)}"

    def verify_providers_ready(self, providers: List[dict]) -> Union[bool, str]:
        """
        Verifies that both the VMware and Host providers are listed and their statuses are 'Ready'.

        Args:
            providers (List[dict]): The list of Provider objects retrieved from the OpenShift cluster.

        Returns:
            bool: True if both providers are found and have the 'Ready' status.
            str: An error message if the providers are not ready or not found.
        """
        # Initialize status flags
        vmware_ready = False
        host_ready = False

        # Check each provider for 'vmware' and 'host' and verify 'Ready' status
        for provider in providers:
            provider_name = provider["metadata"]["name"]
            if provider_name in ["vmware", "host"]:
                conditions = provider["status"].get("conditions", [])
                for condition in conditions:
                    if condition["type"] == "Ready" and condition["status"] == "True":
                        if provider_name == "vmware":
                            vmware_ready = True
                        elif provider_name == "host":
                            host_ready = True

        # Verify both providers are ready
        if vmware_ready and host_ready:
            return True
        else:
            missing_providers = []
            if not vmware_ready:
                missing_providers.append("vmware")
            if not host_ready:
                missing_providers.append("host")
            return (
                f"The following providers are not ready: {', '.join(missing_providers)}"
            )

    def create_migration_plan(
        self,
        name: str = "default-migration-plan",
        destination: str = "host",
        source: str = "vmware",
        network_map: str = "vmware-qbjcw",
        storage_map: str = "vmware-wp7cw",
        vms: List[Dict[str, str]] = None,
        namespace: str = "openshift-mtv",
    ) -> Union[Dict, str]:
        """
        Creates a migration plan using the forklift.konveyor.io API.

        Args:
            name (str): The name of the migration plan. Default is 'default-migration-plan'.
            destination (str): The destination provider. Default is 'host'.
            source (str): The source provider. Default is 'vmware'.
            network_map (str): The network map used for the migration. Default is 'vmware-qbjcw'.
            storage_map (str): The storage map used for the migration. Default is 'vmware-wp7cw.
            vms (List[Dict[str, str]]): A list of VMs to migrate, each VM represented as a dictionary with 'id' and 'name'. Default is None.
            namespace (str): The namespace for the migration plan. Default is 'openshift-mtv'.

        Returns:
            dict: The created migration plan if successful.
            str: An error message if the operation fails.
        """
        if vms is None:
            vms = [{"id": "vm-12345", "name": "default-vm"}]  # Default VM if none provided

        try:
            # Prepare the body of the migration plan
            body = {
                "apiVersion": "forklift.konveyor.io/v1beta1",
                "kind": "Plan",
                "metadata": {
                    "name": name,
                    "namespace": namespace
                },
                "spec": {
                    "map": {
                        "network": {
                            "apiVersion": "forklift.konveyor.io/v1beta1",
                            "kind": "NetworkMap",
                            "name": network_map,
                            "namespace": namespace
                        },
                        "storage": {
                            "apiVersion": "forklift.konveyor.io/v1beta1",
                            "kind": "StorageMap",
                            "name": storage_map,
                            "namespace": namespace
                        }
                    },
                    "provider": {
                        "destination": {
                            "apiVersion": "forklift.konveyor.io/v1beta1",
                            "kind": "Provider",
                            "name": destination,
                            "namespace": namespace
                        },
                        "source": {
                            "apiVersion": "forklift.konveyor.io/v1beta1",
                            "kind": "Provider",
                            "name": source,
                            "namespace": namespace
                        }
                    },
                    "targetNamespace": namespace,
                    "vms": vms
                }
            }

            # Create the migration plan using the Kubernetes custom object API
            api_instance = client.CustomObjectsApi()
            created_plan = api_instance.create_namespaced_custom_object(
                group="forklift.konveyor.io",
                version="v1beta1",
                namespace=namespace,
                plural="plans",
                body=body
            )

            return created_plan

        except ApiException as e:
            return f"Failed to create migration plan: {str(e)}"

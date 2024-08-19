from kubernetes import client
from kubernetes.client.rest import ApiException
from typing import Union, List
from config.config import app_config

class OpenShiftService:
    """
    This service class handles interactions with the OpenShift (Kubernetes-based) API,
    including retrieving namespaces (projects) and checking access to required projects.
    It also manages its own connection to the OpenShift API.
    """

    def __init__(
        self, api_url: str = app_config.openshiftConfig.api_url, token: str = app_config.openshiftConfig.token
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

            # Create the CoreV1Api instance for interacting with core Kubernetes/OpenShift resources
            self.core_v1_api = client.CoreV1Api()

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

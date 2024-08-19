from typing import List, Union
from langchain.tools import tool
from services.openshift_service import OpenShiftService
import os


@tool(parse_docstring=True)
def ensure_openshift_project_access(required_projects: List[str]) -> Union[bool, str]:
    """
    A tool that accesses the OpenShift Console and ensures access to the required projects.

    Args:
        required_projects (List[str]): A list of project names that are needed for migration.

    Returns:
        bool: True if access is confirmed for all required projects.
        str: An error message if the operation fails or access is not available.
    """
    try:
        # Retrieve API URL and token from environment variables
        api_url = os.getenv("OPENSHIFT_API_URL")
        token = os.getenv("OPENSHIFT_TOKEN")

        if not api_url or not token:
            return (
                "API URL or token is missing. Ensure they are set in the environment."
            )

        # Create an OpenShiftService instance and establish a connection
        client = OpenShiftService(api_url, token)

        # Check access to the required projects
        access_result = client.check_project_access(required_projects)

        # Return the result
        if access_result is True:
            return True
        else:
            return access_result

    except Exception as e:
        return f"Failed to ensure project access: {str(e)}"

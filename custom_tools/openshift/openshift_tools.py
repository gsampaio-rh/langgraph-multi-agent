from typing import List, Union
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

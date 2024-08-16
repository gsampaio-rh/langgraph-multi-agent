from langchain.tools import tool
from utils.vsphere_utils import (
    connect_to_vsphere,
    disconnect_from_vsphere,
)

@tool(parse_docstring=True)
def vsphere_connect_tool(host: str, user: str, pwd: str) -> str:
    """
    Connects to the vSphere environment and returns a success message.

    Args:
        host: The IP address or URL of the vCenter server.
        user: The username for the vCenter server.
        pwd: The password for the vCenter server.

    Returns:
        str: A message indicating successful connection or an error message.
    """
    try:
        si = connect_to_vsphere(host, user, pwd)
        return f"Successfully connected to vCenter at {host}.", si
    except Exception as e:
        return f"Failed to connect to vCenter: {str(e)}"


@tool(parse_docstring=True)
def vsphere_disconnect_tool(si) -> str:
    """
    Disconnects from the vSphere environment.

    Returns:
        str: A message indicating successful disconnection or an error message.
    """
    
    try:
        disconnect_from_vsphere(si)
        return "Successfully disconnected from vCenter."
    except Exception as e:
        return f"Failed to disconnect from vCenter: {str(e)}"

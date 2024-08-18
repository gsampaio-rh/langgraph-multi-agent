from langchain.tools import tool
from utils.vsphere_utils import (
    connect_to_vsphere,
    disconnect_from_vsphere,
)

@tool(parse_docstring=True)
def vsphere_connect_tool() -> str:
    """
    Connects to the vSphere environment and returns a success message.

    Returns:
        str: A message indicating successful connection or an error message.
    """
    try:
        si = connect_to_vsphere()
        return f"Successfully connected to vCenter.", si
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

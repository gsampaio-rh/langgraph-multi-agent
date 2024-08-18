from langchain.tools import tool
from config.config import app_config


@tool(parse_docstring=True)
def vsphere_connect_tool() -> str:
    """
    Connects to the vSphere environment and returns a success message.

    Returns:
        str: A message indicating successful connection or an error message.
    """
    try:
        with app_config.vsphere_manager.connection() as si:
            return f"Successfully connected to vCenter.", si
    except Exception as e:
        return f"Failed to connect to vCenter: {str(e)}"


@tool(parse_docstring=True)
def vsphere_disconnect_tool() -> str:
    """
    Disconnects from the vSphere environment.

    Returns:
        str: A message indicating successful disconnection or an error message.
    """
    try:
        app_config.vsphere_manager.disconnect()
        return "Successfully disconnected from vCenter."
    except Exception as e:
        return f"Failed to disconnect from vCenter: {str(e)}"

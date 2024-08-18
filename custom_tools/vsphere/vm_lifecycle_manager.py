from langchain.tools import tool
from config.config import app_config
from utils.vsphere_utils import (
    get_all_vms,
    connect_to_vsphere,
    disconnect_from_vsphere,
)

@tool(parse_docstring=True)
def list_vms():
    """
    Retrieves and lists all the virtual machines (VMs) available in the connected vSphere environment.

    This function establishes a connection to the vSphere environment, retrieves a list of all VMs present, and disconnects from the vSphere environment upon completion. The VMs are retrieved using the established vSphere connection, and any errors during the process are handled and returned as part of the output.

    Returns:
        str: A success message listing all the virtual machines if the operation is successful, or an error message if the operation fails.

    """
    si = None
    try:
        # Connect to vSphere
        si, content = connect_to_vsphere(
            host=app_config.vsphereConfig.host,
            user=app_config.vsphereConfig.user,
            pwd=app_config.vsphereConfig.pwd,
        )

        vms = get_all_vms(si, content)
        return vms

    except Exception as e:
        return f"Failed to list vms. {str(e)}"

    finally:
        if si:
            disconnect_from_vsphere(si)

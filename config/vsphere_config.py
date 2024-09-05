from dataclasses import dataclass
import os


@dataclass
class VsphereConfig:
    """
    Configuration for vSphere connections.
    """

    host: str = os.getenv("VSPHERE_HOST", "host")
    user: str = os.getenv("VSPHERE_USER", "user")
    pwd: str = os.getenv("VSPHERE_PWD", "pwd")

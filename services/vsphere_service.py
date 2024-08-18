from pyVim.connect import SmartConnect, Disconnect
from config.config import VsphereConfig
import ssl

class VsphereService:
    def __init__(self, vsphereConfig: VsphereConfig):
        self.host = vsphereConfig.host
        self.user = vsphereConfig.user
        self.pwd = vsphereConfig.pwd
        self.service_instance = None

    def connect(self):
        # Disable SSL certificate verification for simplicity
        context = ssl._create_unverified_context()
        try:
            # Establish connection to vSphere
            self.service_instance = SmartConnect(
                host=self.host, user=self.user, pwd=self.pwd, sslContext=context
            )
            print("Connected to vSphere")
        except Exception as e:
            print(f"Failed to connect to vSphere: {e}")
            self.service_instance = None

    def disconnect(self):
        if self.service_instance:
            Disconnect(self.service_instance)
            print("Disconnected from vSphere")

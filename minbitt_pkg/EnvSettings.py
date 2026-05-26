from minbitt_pkg.DisplayInterface import DisplayInterface
from minbitt_pkg.iFacialMocap import ConnectionInterface
from minbitt_pkg.DisplayInterface import AnimationInterface

class EnvSettings:
    def __init__(self, proj_env: str, display: DisplayInterface, connection: ConnectionInterface, animation: AnimationInterface):
        self.proj_env = proj_env
        self.display = display
        self.connection = connection
        self.animation = animation

from minbitt_pkg.DisplayInterface import DisplayInterface
from minbitt_pkg.iFacialMocap import ConnectionInterface

#TODO: maybe move into DisplayInterface
class EnvSettings:
    def __init__(self, proj_env: str, display: DisplayInterface, connection: ConnectionInterface):
        self.proj_env = proj_env
        self.display = display
        self.connection = connection

from minbitt_pkg.DisplayInterface import PINK
from minbitt_pkg.EnvSettings import EnvSettings
from minbitt_pkg.face_display import main
from resources.pygame_code.PygameDisplay import PygameDisplay
from resources.pygame_code.WifiConnection import WifiConnection

FPS = 60
WIDTH = 64
HEIGHT = 32
COLOR_KEY = PINK
settings = EnvSettings("/home/agmui/cs/minbitt_head/",
                       PygameDisplay(WIDTH, HEIGHT, COLOR_KEY, FPS),
                       WifiConnection("192.168.1.60"))
main(settings)

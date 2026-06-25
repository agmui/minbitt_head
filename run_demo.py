import os

from minbitt_pkg.DisplayInterface import PINK
from minbitt_pkg.EnvSettings import EnvSettings
from minbitt_pkg.face_display import main
from resources.pygame_code.PygameDisplay import PygameDisplay
from resources.pygame_code.PygameConnection import PygameConnection
from minbitt_pkg.MinBittAnimation import MinBittAnimation

FPS = 60
WIDTH = 64 # TODO: check different width height values
HEIGHT = 32
COLOR_KEY = PINK
proj_env = os.getcwd()+"/"#TODO: test

display = PygameDisplay(WIDTH, HEIGHT, COLOR_KEY, FPS)

minbitt_animation = MinBittAnimation(display, proj_env)

settings = EnvSettings(proj_env, display, PygameConnection("192.168.1.60"), minbitt_animation)

main(settings)

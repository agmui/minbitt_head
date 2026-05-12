from minbitt_pkg.DisplayInterface import PINK
from minbitt_pkg.EnvSettings import EnvSettings
from minbitt_pkg.LedDisplay import LedDisplay
from minbitt_pkg.LedDisplayRaw import LedDisplayRaw
from minbitt_pkg.face_display import main
from minbitt_pkg.iFacialMocap import CircuitPythonConnection

start_msg = """
=============================
=== starting minbitt head ===
=============================
"""
print(start_msg)

FPS = 60
WIDTH = 64
HEIGHT = 32
COLOR_KEY = PINK
proj_env = "/"
font_path = proj_env + "minbitt_pkg/" + "tom-thumb.pcf"  # https://robey.lag.net/2010/01/23/tiny-monospace-font.html
d = LedDisplayRaw(WIDTH, HEIGHT, COLOR_KEY, font_path, FPS)
settings = EnvSettings(proj_env, d, CircuitPythonConnection(d))

main(settings)

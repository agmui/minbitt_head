from minbitt_pkg.DisplayInterface import PINK
from minbitt_pkg.EnvSettings import EnvSettings
from minbitt_pkg.LedDisplay import LedDisplay
from minbitt_pkg.LedDisplayRaw import LedDisplayRaw
from minbitt_pkg.face_display import main
from minbitt_pkg.CircuitPythonConnection import CircuitPythonConnection
from micropython import const

start_msg = """
=============================
=== starting minbitt head ===
=============================
"""
print(start_msg)

FPS = const(60)
WIDTH = const(64)
HEIGHT = const(32)
COLOR_KEY = PINK
proj_env = const("/")
font_path = proj_env + "minbitt_pkg/" + "tom-thumb.pcf"  # https://robey.lag.net/2010/01/23/tiny-monospace-font.html
# display = LedDisplayRaw(WIDTH, HEIGHT, COLOR_KEY, font_path, FPS)
display = LedDisplay(WIDTH, HEIGHT, COLOR_KEY, font_path, FPS)
settings = EnvSettings(proj_env, display, CircuitPythonConnection(display))

main(settings)


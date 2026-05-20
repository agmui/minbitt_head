import board
import rgbmatrix  # For talking to matrices specifically
import displayio
from micropython import const

from minbitt_pkg.DisplayInterface import PINK
from minbitt_pkg.EnvSettings import EnvSettings
from minbitt_pkg.LedDisplay import LedDisplay
from minbitt_pkg.LedDisplayRaw import LedDisplayRaw
from minbitt_pkg.face_display import main
from minbitt_pkg.CircuitPythonConnection import CircuitPythonConnection

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

# release olf display
displayio.release_displays()
# Setup rgbmatrix display
matrix = rgbmatrix.RGBMatrix(
    width=WIDTH,  # Change width & height if you have an LED matrix with different dimensions
    height=HEIGHT,
    bit_depth=2,
    rgb_pins=[  # Preserve GP4 & GP5 for standard STEMMA-QT
        board.GP2,  # R1
        board.GP3,  # G1
        board.GP6,  # B1
        board.GP7,  # R2
        board.GP8,  # G2
        board.GP9  # B2
    ],
    addr_pins=[
        board.GP10,  # A
        board.GP16,  # B
        board.GP18,  # C
        board.GP20  # D
    ],
    clock_pin=board.GP11,
    latch_pin=board.GP12,
    output_enable_pin=board.GP13,
    tile=1,
    serpentine=False,
    doublebuffer=True,
)

# display = LedDisplayRaw(matrix, COLOR_KEY, font_path, FPS)
display = LedDisplay(matrix, COLOR_KEY, font_path, FPS)
settings = EnvSettings(proj_env, display, CircuitPythonConnection(display))

main(settings)


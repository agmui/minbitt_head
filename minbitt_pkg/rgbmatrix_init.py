import board
import displayio
import rgbmatrix  # For talking to HUB75 led matrices specifically

def rgbmatrix_init(WIDTH, HEIGHT):
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
    return matrix

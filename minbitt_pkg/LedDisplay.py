import time
import board
import displayio  # Main display library
import framebufferio  # For showing things on the display
import rgbmatrix  # For talking to matrices specifically
import adafruit_imageload
import bitmaptools
from adafruit_display_text import bitmap_label
from adafruit_bitmap_font import bitmap_font
import gifio

from minbitt_pkg.DisplayInterface import *


class LedDisplay(DisplayInterface):
    def __init__(self, WIDTH, HEIGHT, COLOR_KEY, font_path, FPS=60, palett_size=50):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.COLOR_KEY = COLOR_KEY
        self.FPS = FPS

        self.old_time = time.monotonic()
        self.font = bitmap_font.load_font(font_path)

        self.palette_size = palett_size  # TODO: idk make sure this is never reached by doing reallocs when reaching limit
        if __debug__:
            self.avg = [0 for _ in range(20)]
            self.i = 0

    def __enter__(self):
        # release olf display
        displayio.release_displays()
        # Setup rgbmatrix display (change pins to match your wiring)
        matrix = rgbmatrix.RGBMatrix(
            width=self.WIDTH,  # Change width & height if you have an LED matrix with different dimensions
            height=self.HEIGHT,
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

        # Create a display
        self.led_display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)
        group = displayio.Group()
        self.background_bitmap = displayio.Bitmap(self.WIDTH, self.HEIGHT, self.palette_size)
        self.palette = displayio.Palette(self.palette_size)
        self.cc = displayio.ColorConverter()
        self.palette[0] = self.COLOR_KEY
        self.palette.make_transparent(0)
        self.inverse_palette = {self.COLOR_KEY: 0, }

        self.background_tile_grid = displayio.TileGrid(self.background_bitmap, pixel_shader=self.palette)
        group.append(self.background_tile_grid)
        self.led_display.root_group = group

        return self

    def get_width(self) -> int:
        return self.WIDTH

    def get_height(self) -> int:
        return self.HEIGHT

    def load_image(self, image_path, flipped=False):
        # TODO: idk try loading gifs cuz adafruit_imageload supports gifs

        bitmap, img_palette = adafruit_imageload.load(image_path, bitmap=displayio.Bitmap, palette=displayio.Palette)
        print(image_path, img_palette)

        if flipped:
            tmp_bitmap = displayio.Bitmap(bitmap.width, bitmap.height, len(self.palette))
            for x in range(bitmap.width):
                for y in range(bitmap.height):
                    tmp_bitmap[bitmap.width - x - 1, y] = bitmap[x, y]
            bitmap = tmp_bitmap

        if type(img_palette) == displayio.ColorConverter:
            r = self.COLOR_KEY[0]
            g = self.COLOR_KEY[1]
            b = self.COLOR_KEY[2]
            img_palette.make_transparent(r << 16 | g << 8 | b)
            # TODO: use bitmaptools.replace_color()
            # also use dithering to avoid going over palette 50 color limit
        elif type(img_palette) == displayio.Palette:
            tmp_bitmap = displayio.Bitmap(bitmap.width, bitmap.height, len(self.palette))
            translate = {}
            for i, c in enumerate(img_palette):
                if c not in self.inverse_palette:
                    index = len(self.inverse_palette)
                    self.palette[index] = c
                    self.inverse_palette[c] = index
                    translate[i] = index
                else:
                    translate[i] = self.inverse_palette[c]
            for x in range(tmp_bitmap.width):
                for y in range(tmp_bitmap.height):
                    tmp_bitmap[x, y] = translate[bitmap[x, y]]
            bitmap = tmp_bitmap

            self.background_tile_grid = displayio.TileGrid(self.background_bitmap,
                                                           pixel_shader=self.palette)  # TODO: Check if this has to be here
        # print()

        # for x in range(bitmap.width):
        #     for y in range(bitmap.height):
        #         print(f"{bitmap[x,y]:04x} ", end = "")
        #     print()

        # image = adafruit_imageload.load(image_path, bitmap=displayio.Bitmap, img_palette=displayio.Palette)

        # img_group = displayio.Group()
        # tile_grid = displayio.TileGrid(bitmap, pixel_shader=img_palette)
        # img_group.append(tile_grid)
        # self.led_display.root_group.append(img_group)
        # img_group.hidden = True
        # return img_group

        return const(bitmap)  # TODO: idk test performance


    def load_gif(self, gif_path: str) -> tuple[gifio.OnDiskGif, displayio.TileGrid]:
        odg = gifio.OnDiskGif(gif_path)
        print(gif_path, odg.palette, odg.frame_count)
        odg.next_frame()
        face = displayio.TileGrid(
            odg.bitmap,
            pixel_shader=displayio.ColorConverter(
                input_colorspace=displayio.Colorspace.RGB565_SWAPPED
            ),
        )
        self.led_display.root_group.append(face)
        face.hidden = True
        return odg, face

    # TODO: better name
    def read_input(self) -> HeadInput:
        return HeadInput(True, FaceExpression.NA)

    def draw_line(self, color: color_t, start_pos: Point, end_pos: Point, width: int = 1):
        if color not in self.inverse_palette:
            palette_index = len(self.inverse_palette)
            self.palette[palette_index] = color
            self.inverse_palette[color] = palette_index
            # TODO: check if this needs to be called
            # self.background_tile_grid = displayio.TileGrid(self.background_bitmap, pixel_shader=self.palette)
        # bresenham(self.pixel_buff, color, start_pos.trunc(), end_pos.trunc(), width)
        bitmaptools.draw_line(self.background_bitmap, int(start_pos.x), int(start_pos.y), int(end_pos.x),
                              int(end_pos.y), self.inverse_palette[color])

    def draw_circle(self, color: color_t, pos: Point, radius: int, fill: bool = False):
        if color not in self.inverse_palette:
            palette_index = len(self.inverse_palette)
            self.palette[palette_index] = color
            self.inverse_palette[color] = palette_index
        bitmaptools.draw_circle(self.background_bitmap, int(pos.x), int(pos.y), radius, self.inverse_palette[color])

    def blit(self, image, pos: Point):
        # tg.hidden = False
        # tg.x = int(pos.x)
        # tg.y = int(pos.y)
        # image[1] += 1
        # print(pos.x)
        # bitmaptools.blit(self.background_bitmap, image, clamp(int(pos.x), 0, 64), int(pos.y),
        #                  skip_source_index=self.color_key_conv, skip_dest_index=self.color_key_conv)
        bitmaptools.blit(self.background_bitmap, image, clamp(int(pos.x), 0, 64), int(pos.y), skip_source_index=0)

    def draw_text(self, output_str: str, pos: Point, color):
        if color not in self.inverse_palette:
            palette_index = len(self.inverse_palette)
            self.palette[palette_index] = color
            self.inverse_palette[color] = palette_index
        text_area = bitmap_label.Label(self.font, text=output_str).bitmap

        # this is a hack
        tmp_bitmap = displayio.Bitmap(text_area.width, text_area.height, 3)
        bitmaptools.blit(tmp_bitmap, text_area, 0, 0)
        bitmaptools.replace_color(tmp_bitmap, 1, self.inverse_palette[color])

        bitmaptools.blit(self.background_bitmap, tmp_bitmap, int(pos.x), int(pos.y), skip_source_index=0)


    def draw_gif(self, gif: tuple[gifio.OnDiskGif, displayio.TileGrid], pos: Point):
        odg, face = gif
        face.hidden = False
        face.x = int(pos.x)
        face.y = int(pos.y)
        odg.next_frame()

    def update(self, face_data: BlendshapeData = None):
        # memoryview(self.led_display.framebuffer)[1] = 0xFFFF
        new_time = time.monotonic()
        dt = new_time - self.old_time
        self.old_time = new_time
        if __debug__:
            fps = f"FPS: {1 / dt}"
            # print(fps)

            self.avg[self.i] = 1 / dt
            print(sum(self.avg) / 20)
            self.i += 1
            self.i %= 20

        # for x in range(self.background_bitmap.width):
        #     for y in range(self.background_bitmap.height):
        #         print(self.background_bitmap[x,y], end='')
        #     print()
        #
        # print()
        # print()
        # print()
        # met_deadline = self.led_display.refresh(target_frames_per_second=self.FPS)
        # print(behind_fps)
        self.led_display.refresh()
        # time.sleep(max(0.0417 - dt, 0))
        # time.sleep(max(0.03333 - dt, 0))

        # self.led_display.framebuffer.refresh()

        # for g in self.led_display.root_group:
        #     # for sub_g in g:
        #     g.hidden = True
        #     # g[1] = 0
        # self.background_tile_grid.hidden = False

        self.background_bitmap.fill(0)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: add free code to all obj
        pass

import time
import board
import displayio  # Main display library
import framebufferio  # For showing things on the display
import rgbmatrix  # For talking to matrices specifically
import adafruit_imageload
import bitmaptools
from adafruit_display_text import bitmap_label
from adafruit_bitmap_font import bitmap_font

from minbitt_pkg.DisplayInterface import *


class LedDisplay(DisplayInterface):
    def __init__(self, WIDTH, HEIGHT, COLOR_KEY, font_path, FPS=60):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.COLOR_KEY = COLOR_KEY
        self.FPS = FPS

        self.old_time = time.monotonic()
        self.font = bitmap_font.load_font(font_path)

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
        palette_size = 50  # TODO: idk make sure this is never reached or something
        self.background_bitmap = displayio.Bitmap(self.WIDTH, self.HEIGHT, palette_size)  # 65535)
        self.palette = displayio.Palette(palette_size)
        self.cc = displayio.ColorConverter()
        # self.cc.make_transparent(self.color_key_conv)
        self.palette[0] = self.COLOR_KEY  # TODO: you can use tuple for palette color init
        self.palette[1] = self.cc.convert(0x5FCDE4)  # FIXME: needs to be removed
        self.palette.make_transparent(0)
        self.inverse_palette = {
            self.COLOR_KEY: 0,
            self.palette[1]: 1
        }

        self.background_tile_grid = displayio.TileGrid(self.background_bitmap, pixel_shader=self.palette)
        group.append(self.background_tile_grid)
        self.led_display.root_group = group

        return self

    def get_width(self) -> int:
        return self.WIDTH

    def get_height(self) -> int:
        return self.HEIGHT

    def load_image(self, image_path, flipped=False):
        # TODO: use flipped field
        # TODO: use adafruit_imageload.load https://learn.adafruit.com/circuitpython-display-support-using-displayio/display-a-bitmap
        # TODO: idk try loading gifs cuz adafruit_imageload supports gifs
        # assert flipped == False and "flipped NYI"

        bitmap, img_palette = adafruit_imageload.load(image_path, bitmap=displayio.Bitmap, palette=displayio.Palette)
        # img = displayio.OnDiskBitmap(image_path)
        # bitmap = img
        # img_palette = img.pixel_shader

        print(image_path, img_palette)
        # TODO: maybe its worth trying to turn all images into RGB565 and not need to manage a palette
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
                # c = self.cc.convert(c)
                # print(c in self.inverse_palette, c, self.inverse_palette)
                # for j, p in enumerate(self.palette):
                #     print(j ,'->', f'{p:06x}')
                if c not in self.inverse_palette:
                    # print("adding color")
                    index = len(self.inverse_palette)
                    self.palette[index] = c
                    self.inverse_palette[c] = index
                    # print("translate:",i, index)
                    translate[i] = index
                else:
                    translate[i] = self.inverse_palette[c]
            for x in range(tmp_bitmap.width):
                for y in range(tmp_bitmap.height):
                    tmp_bitmap[x, y] = translate[bitmap[x, y]]
            # print("tmp_bitmap", tmp_bitmap[1,1], self.palette[tmp_bitmap[1,1]])
            bitmap = tmp_bitmap

            self.background_tile_grid = displayio.TileGrid(self.background_bitmap, pixel_shader=self.palette)#TODO: Check if this has to be here
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

        return bitmap

    # TODO: better name
    def read_input(self) -> HeadInput:
        return HeadInput(True, FaceExpression.NA)

    def draw_line(self, color: color_t, start_pos: Point, end_pos: Point, width: int = 1):
        # bresenham(self.pixel_buff, color, start_pos.trunc(), end_pos.trunc(), width)
        # r = color[0]
        # g = color[1]
        # b = color[2]
        # val = self.cc.convert(r << 16 | g << 8 | b)
        bitmaptools.draw_line(self.background_bitmap, int(start_pos.x), int(start_pos.y), int(end_pos.x),
                              int(end_pos.y), 1)  # val)

    def draw_circle(self, color: color_t, pos: Point, radius: int, fill: bool = False):
        # r = color[0]
        # g = color[1]
        # b = color[2]
        # val = self.cc.convert(r << 16 | g << 8 | b)
        bitmaptools.draw_circle(self.background_bitmap, int(pos.x), int(pos.y), radius, 1)  # val)#FIXME:

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
        text_area = bitmap_label.Label(self.font, text=output_str, color=0x5FCDE4, #FIXME:
                                       color_palette=self.palette)  # TODO: add background color
        bitmaptools.blit(self.background_bitmap, text_area.bitmap, int(pos.x), int(pos.y), skip_source_index=0)

    def update(self, face_data: BlendshapeData = None):
        # memoryview(self.led_display.framebuffer)[1] = 0xFFFF
        new_time = time.monotonic()
        dt = new_time - self.old_time
        self.old_time = new_time
        fps = f"FPS: {1 / dt}"
        print(fps)

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
        # TODO: idk run gc

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: add free code to all obj
        pass

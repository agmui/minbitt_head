import time
import displayio  # Main display library
import framebufferio  # For showing things on the display
import adafruit_imageload
import bitmaptools
import rgbmatrix
from adafruit_display_text import bitmap_label
from adafruit_bitmap_font import bitmap_font
import gifio

from minbitt_pkg.DisplayInterface import *


def rgb24_to_rgb16(color: int):
    r5 = color >> 19
    g6 = (color >> 10) & 0x3f
    b5 = (color >> 3) & 0x1f
    return r5 << 11 | g6 << 5 | b5


class LedDisplayRaw(DisplayInterface):
    def __init__(self, matrix: rgbmatrix.RGBMatrix, COLOR_KEY, font_path, FPS=60):
        self.matrix = matrix
        self.WIDTH = matrix.width
        self.HEIGHT = matrix.height
        self.cc = displayio.ColorConverter()
        self.COLOR_KEY = self.cc.convert(COLOR_KEY)
        self.FPS = FPS

        self.old_time = time.monotonic()
        self.font = bitmap_font.load_font(font_path)

        if __debug__:
            self.avg = [0 for _ in range(20)]
            self.i = 0

    def __enter__(self):
        # Create a display
        self.led_display = framebufferio.FramebufferDisplay(self.matrix, auto_refresh=False)
        group = displayio.Group()
        self.background_bitmap = displayio.Bitmap(self.WIDTH, self.HEIGHT, 0xFFFF)  # RGB565

        # NOTE: because we did not do make_transparent for the pixel_shader we can draw self.COLOR_KEY for non blit
        # (i.e. lines and circles) because blit skips over self.COLOR_KEY
        self.background_tile_grid = displayio.TileGrid(self.background_bitmap,
                                                       pixel_shader=displayio.ColorConverter(
                                                           input_colorspace=displayio.Colorspace.RGB565))
        group.append(self.background_tile_grid)
        self.led_display.root_group = group

        return self

    def get_width(self) -> int:
        return self.WIDTH

    def get_height(self) -> int:
        return self.HEIGHT

    def load_image(self, image_path, flipped=False):
        bitmap, img_palette = adafruit_imageload.load(image_path, bitmap=displayio.Bitmap, palette=displayio.Palette)
        print(image_path, img_palette)

        if flipped:
            for x in range(bitmap.width//2):
                for y in range(bitmap.height):
                    bitmap[bitmap.width-x-1,y], bitmap[x,y] = bitmap[x,y], bitmap[bitmap.width-x-1,y]

        tmp_bitmap = displayio.Bitmap(bitmap.width, bitmap.height, 0xFFFF)
        if type(img_palette) == displayio.ColorConverter:
            for x in range(bitmap.width):
                for y in range(bitmap.height):
                    tmp_bitmap[x, y] = img_palette.convert(bitmap[x, y])
        elif type(img_palette) == displayio.Palette:
            for x in range(bitmap.width):
                for y in range(bitmap.height):
                    tmp_bitmap[x, y] = self.cc.convert(img_palette[bitmap[x, y]])

        # bitmap.deinit()
        return const(tmp_bitmap) #TODO: idk test performance

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

    def read_input(self) -> HeadInput:
        return HeadInput(True, FaceExpression.NA)

    def draw_line(self, color: color_t, start_pos: Point, end_pos: Point, width: int = 1):
        """
        Note:
            draw_line is not affected by key color
        """
        # bitmaptools.draw_line(self.background_bitmap, int(start_pos.x), int(start_pos.y), int(end_pos.x),
        #                       int(end_pos.y), color)
        bitmaptools.draw_line(self.background_bitmap, int(start_pos.x), int(start_pos.y), int(end_pos.x),
                              int(end_pos.y),
                              # self.cc.convert(color))
                              rgb24_to_rgb16(color))

    def draw_circle(self, color: color_t, pos: Point, radius: int, fill: bool = False):#TODO: fill argument
        bitmaptools.draw_circle(self.background_bitmap, int(pos.x), int(pos.y), radius,
                                # self.cc.convert(color))
                                rgb24_to_rgb16(color))

    def blit(self, image, pos: Point):
        bitmaptools.blit(self.background_bitmap, image, clamp(int(pos.x), 0, 64), int(pos.y),
                         skip_source_index=self.COLOR_KEY)

    def draw_text(self, output_str: str, pos: Point, color):
        text_area = bitmap_label.Label(self.font, text=output_str).bitmap
        color_rgb565 = self.cc.convert(color)

        # this is a hack
        tmp_bitmap = displayio.Bitmap(text_area.width, text_area.height,
                                      color_rgb565)  # Note: using setting color depth to be the color value may break
        bitmaptools.blit(tmp_bitmap, text_area, 0, 0)
        bitmaptools.replace_color(tmp_bitmap, 1, color_rgb565)

        bitmaptools.blit(self.background_bitmap, tmp_bitmap, int(pos.x), int(pos.y),
                         skip_source_index=0)

    def draw_gif(self, gif: tuple[gifio.OnDiskGif, displayio.TileGrid], pos: Point):
        odg, face = gif
        odg.bitmap.fill(0)
        face.hidden = False
        face.x = int(pos.x)
        face.y = int(pos.y)
        odg.next_frame()

    def free_gif(self, odg: gifio.OnDiskGif):
        # where RAM is limited and the first GIF took most of the RAM.
        odg.deinit()
        odg = None
        # gc.collect()

    def update(self, face_data: BlendshapeData = None):
        new_time = time.monotonic()
        dt = new_time - self.old_time
        self.old_time = new_time
        if __debug__:
            fps = f"FPS: {1 / dt:4.4f} | avg FPS:"
            # print(fps)

            self.avg[self.i] = 1 / dt
            print(fps,sum(self.avg) / 20)
            self.i += 1
            self.i %= 20

        # met_deadline = self.led_display.refresh(target_frames_per_second=self.FPS)
        self.led_display.refresh()

        self.background_bitmap.fill(0)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.background_bitmap.deinit()
        self.led_display.framebuffer.deinit()
        # release olf display
        displayio.release_displays()

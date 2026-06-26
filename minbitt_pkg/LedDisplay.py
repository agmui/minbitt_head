import time
import audiocore
import digitalio
import displayio  # Main display library
import framebufferio  # For showing things on the display
import adafruit_imageload
import bitmaptools
import rgbmatrix
from adafruit_display_text import bitmap_label
from adafruit_bitmap_font import bitmap_font
import gifio
import board # for i2c
import busio # for i2c
import audiobusio
import audiomp3
import neopixel_write
import ulab

from minbitt_pkg.DisplayInterface import *




class LedDisplay(DisplayInterface):
    def __init__(self, matrix: rgbmatrix.RGBMatrix, COLOR_KEY: color_t, font_path: str, FPS=60, use_controller: bool = False, speaker: audiobusio.I2SOut | None = None):
        self.matrix = matrix
        self.WIDTH = matrix.width
        self.HEIGHT = matrix.height
        self.cc = displayio.ColorConverter()
        self.COLOR_KEY = self.cc.convert(COLOR_KEY)
        self.FPS = FPS
        self.desired_dt = const(1 / self.FPS)

        self.old_time = time.monotonic()
        self.font = bitmap_font.load_font(font_path)

        self.use_controller = use_controller
        if self.use_controller:
            self.uart = busio.UART(board.TX, board.A0, baudrate=115200, parity=busio.UART.Parity.EVEN, stop=2, receiver_buffer_size=1)
        self.prev_controller_input = ControllerInput(True, FaceExpression.NA)

        self.speaker = speaker

        # led
        self.led_timer = 0
        self.led = digitalio.DigitalInOut(board.LED)
        self.led.direction = digitalio.Direction.OUTPUT
        self.neopixel = digitalio.DigitalInOut(board.NEOPIXEL)
        self.neopixel.direction = digitalio.Direction.OUTPUT

        if __debug__:
            self.avg = [0 for _ in range(20)]
            self.i = 0

        # === Create a display ===
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

    def __enter__(self):
        # Note: nothing is here because we need LedDisplay to be init before any animation or Connection Interface
        # it is just here so LedDisplay can be properly contex managed
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.background_bitmap.deinit()
        self.led_display.framebuffer.deinit()
        # release olf display
        displayio.release_displays()

        if self.use_controller:
            self.uart.deinit()
        if self.speaker:
            self.speaker.deinit()

    def get_width(self) -> int:
        return self.WIDTH

    def get_height(self) -> int:
        return self.HEIGHT

    def get_FPS(self) -> int:
        return self.FPS

    def draw_line(self, color: color_t, start_pos: Point, end_pos: Point, width: int = 1):
        """
        Note:
            draw_line is not affected by key color
        """
        # using rgb24_to_rgb16 instead of self.cc so we can draw lines with COLOR_KEY
        bitmaptools.draw_line(self.background_bitmap, int(start_pos.x), int(start_pos.y), int(end_pos.x),
                              int(end_pos.y), rgb24_to_rgb16(color))

    def draw_circle(self, color: color_t, pos: Point, radius: int):
        """
        Note:
            draw_circle is not affected by key color
        """
        # using rgb24_to_rgb16 instead of self.cc so we can draw lines with COLOR_KEY
        bitmaptools.draw_circle(self.background_bitmap, int(pos.x), int(pos.y), max(radius, 0), rgb24_to_rgb16(color))

    def load_image(self, image_path, flipped=False):
        bitmap, img_palette = adafruit_imageload.load(image_path, bitmap=displayio.Bitmap, palette=displayio.Palette)
        debug_log(image_path, img_palette)

        if flipped:
            for x in range(bitmap.width // 2):
                for y in range(bitmap.height):
                    bitmap[bitmap.width - x - 1, y], bitmap[x, y] = bitmap[x, y], bitmap[bitmap.width - x - 1, y]

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
        return tmp_bitmap

    def blit(self, image, pos: Point):
        bitmaptools.blit(self.background_bitmap, image, clamp(int(pos.x), 0, 64), int(pos.y),
                         skip_source_index=self.COLOR_KEY)

    # decide if there should be a pre render function
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

    def load_gif(self, gif_path: str) -> tuple[gifio.OnDiskGif, displayio.TileGrid]:
        odg = gifio.OnDiskGif(gif_path)
        debug_log(gif_path, odg.palette, odg.frame_count)
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

    def draw_gif(self, gif: tuple[gifio.OnDiskGif, displayio.TileGrid], pos: Point = Point(0, 0)):
        odg, face = gif
        odg.bitmap.fill(0)
        face.hidden = False
        face.x = int(pos.x)
        face.y = int(pos.y)
        odg.next_frame()

    def free_gif(self, odg: gifio.OnDiskGif):
        for f in self.led_display.root_group:
            if f.bitmap == odg.bitmap:
                self.led_display.root_group.remove(f)
        odg.deinit()
        odg = None
        # gc.collect()

    def load_audio(self, file_path: str):
        # TODO: maybe write check to make sure audio file is within spec?
        file_ending = file_path[-3:]
        if file_ending == "wav":
            wav = audiocore.WaveFile(file_path)
            debug_log(f'{file_path}: samplerate {wav.sample_rate}, bits per sample {wav.bits_per_sample}')
            return wav
        elif file_ending == "mp3":
            mp3 = audiomp3.MP3Decoder(file_path)
            debug_log(f'{file_path}: samplerate {mp3.sample_rate} bits per sample {mp3.bits_per_sample}')
            return mp3
        else:
            raise Exception(f"unsupported filetype: {file_ending}")

    def play_audio(self, audio: audiocore.WaveFile | audiomp3.MP3Decoder):
        if not self.speaker.playing:
            self.speaker.play(audio, loop=False)

    def read_input(self) -> ControllerInput:
        if self.use_controller:
            raw_data = self.uart.read(self.uart.in_waiting)
            if raw_data == b'' or raw_data is None:
                return self.prev_controller_input
            data = raw_data[0]
            if data == 0:
                if self.speaker.playing:
                    self.speaker.pause()
                    self.speaker.stop()
                self.prev_controller_input = ControllerInput(True, FaceExpression.NA)
            elif data == 1:
                self.prev_controller_input = ControllerInput(True, FaceExpression.QUESTION)
            elif data == 2:
                self.prev_controller_input = ControllerInput(True, FaceExpression.LOCK_IN)
            elif data == 4:
                self.prev_controller_input = ControllerInput(True, FaceExpression.HUG_EYES)
            elif data == 8:
                self.prev_controller_input = ControllerInput(True, FaceExpression.POG)
            elif data == 16:
                self.prev_controller_input = ControllerInput(True, FaceExpression.SPIN)
            return self.prev_controller_input
        return ControllerInput(True, FaceExpression.NA)

    def status_led(self, color: color_t):
        c = color.to_bytes(3, 'big')
        neopixel_write.neopixel_write(self.neopixel, bytearray([c[1] >> 3, c[0] >> 3, c[2] >> 3]))
        self.led.value = color == GREEN

    def frame_buffer(self):
        return ulab.numpy.frombuffer(self.background_bitmap, dtype=ulab.numpy.uint16)

    def dirty(self, arr, x1: int = 0, y1: int = 0, x2: int = -1, y2: int = -1):
        self.background_bitmap.dirty(x1, y1, x2, y2)

    def update(self, face_data: BlendshapeData = None):
        self.led_display.refresh()
        # met_deadline = self.led_display.refresh(target_frames_per_second=self.FPS)
        self.background_bitmap.fill(0)

        for i in range(1, len(self.led_display.root_group)):  # clearing gifs
            if not self.led_display.root_group[i].hidden:
                self.led_display.root_group[i].hidden = True

        self.led_timer += 1
        self.led_timer %= 20
        if self.led_timer == 0:
            self.led.value = not self.led.value

        frame_render_dt = time.monotonic() - self.old_time
        if self.desired_dt > frame_render_dt:
            time.sleep(self.desired_dt - frame_render_dt)

        post_sleep = time.monotonic()
        dt = post_sleep - self.old_time
        if __debug__:
            fps = f"FPS: {1 / dt:4.4f} | avg FPS:"
            self.avg[self.i] = 1 / dt
            # debug_log(fps, sum(self.avg) / 20)
            self.i += 1
            self.i %= 20
        self.old_time = post_sleep
        return dt

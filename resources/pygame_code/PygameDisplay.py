from minbitt_pkg.DisplayInterface import *
from pygame import *
import pygame.event


class PygameDisplay(DisplayInterface):
    def __init__(self, WIDTH, HEIGHT, COLOR_KEY, FPS=60, scale=10, DEBUG_TEXT_WIDTH=575, DEBUG_TEXT_HEIGHT=600):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.COLOR_KEY: color_t = COLOR_KEY

        self.FPS = FPS
        self.scale = scale
        self.DEBUG_TEXT_WIDTH = DEBUG_TEXT_WIDTH
        self.DEBUG_TEXT_HEIGHT = DEBUG_TEXT_HEIGHT
        self.SCREEN_OFFSET = 599
        self.head: Surface = surface.Surface((WIDTH * self.scale, HEIGHT * self.scale))

        self.mock_matrix = surface.Surface((WIDTH, HEIGHT))
        self._bitdepth_conversion_buf = surface.Surface((self.WIDTH, self.HEIGHT), depth=16)

        self.hole_mask = Surface((self.WIDTH * self.scale, self.HEIGHT * self.scale))
        self.hole_mask.fill(BLACK)
        pixel_size = 4
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                draw.circle(self.hole_mask, (255, 255, 255, 100), (x * self.scale + pixel_size, y * self.scale + pixel_size), pixel_size)
        # == init display ==
        init()
        self.screen = display.set_mode(
            (self.WIDTH * self.scale + self.DEBUG_TEXT_WIDTH, self.HEIGHT * self.scale + self.DEBUG_TEXT_HEIGHT),
            DOUBLEBUF)
        self.clock = time.Clock()
        self.font = font.SysFont("Arial", 14, bold=True)
        self.FONT_HEIGHT = 5
        self.led_matrix_font = font.Font("minbitt_pkg/assets/tom-thumb.pcf", self.FONT_HEIGHT)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        quit()

    def get_width(self) -> int:
        return self.WIDTH

    def get_height(self) -> int:
        return self.HEIGHT

    def draw_line(self, color: color_t, start_pos: Point, end_pos: Point, width: int = 1):
        draw.line(self.head, color, tuple(start_pos * self.scale), tuple(end_pos * self.scale), width * self.scale)
        # bresenham(self.pixel_buff, color, start_pos.trunc(), end_pos.trunc(), width)
        draw.line(self.mock_matrix, color, start_pos.trunc(), end_pos.trunc(), width)

    def draw_circle(self, color: color_t, center: Point, radius: int):
        """
        Bresenham's circle algorithm: https://funloop.org/post/2021-03-15-bresenham-circle-drawing-algorithm.html
        :param color:
        :param center:
        :param radius:
        :param fill:
        :return:
        """
        # assert pos.x - radius >= 0 and pos.y - radius >= 0

        draw.circle(self.head, color, tuple(center * self.scale), (radius + 0.3) * self.scale, 3)

        # draw.circle(self.buff, color, tuple(center), (radius + 0.3), 1)

        def draw_pixel(y: int, x: int):  # TODO: idk optimize for out of bound draw
            if self.WIDTH <= x or x < 0 or self.HEIGHT <= y or y < 0:
                return
            self.mock_matrix.set_at((x, y), color)

        pos = center.trunc()  # TODO: idk call properly
        if radius == 0:
            draw_pixel(pos[1], pos[0])
            return

        # x^2 + y^2 = r^2
        x = 0
        y = -radius
        F_M = 1 - radius
        d_e = 3
        d_ne = -(radius << 1) + 5

        def mirror_points(x: int, y: int):
            if False:  # fill:#TODO
                bresenham(self.pixel_buff, color, (pos[0] - x, y), (pos[1] + x + 1, y), 1)
                bresenham(self.pixel_buff, color, (pos[0] - x, -y), (pos[1] + x + 1, -y), 1)
                bresenham(self.pixel_buff, color, (pos[0] - y + 1, x), (pos[1] + y, x), 1)
                bresenham(self.pixel_buff, color, (pos[0] - y + 1, -x), (pos[1] + y, -x), 1)
            else:
                draw_pixel(pos[1] + y, pos[0] + x)
                draw_pixel(pos[1] + y, pos[0] - x)
                draw_pixel(pos[1] - y, pos[0] + x)
                draw_pixel(pos[1] - y, pos[0] - x)
                draw_pixel(pos[1] + x, pos[0] + y)
                draw_pixel(pos[1] - x, pos[0] + y)
                draw_pixel(pos[1] + x, pos[0] - y)
                draw_pixel(pos[1] - x, pos[0] - y)

        mirror_points(x, y)  # TODO: extra draws can be optimized out
        while x < -y:
            if F_M <= 0:
                F_M += d_e
            else:
                F_M += d_ne
                d_ne += 2
                y += 1
            d_e += 2
            d_ne += 2
            x += 1
            mirror_points(x, y)

    def load_image(self, image_path: str, flipped=False) -> Surface:
        img = image.load(image_path)
        if flipped:
            img = transform.flip(img, True, False)
        img.set_colorkey(Color(self.COLOR_KEY << 8 | 255))
        return img

    def blit(self, image: Surface, pos: Point):
        self.head.blit(transform.scale_by(image, self.scale), tuple(pos * self.scale))

        self.mock_matrix.blit(image, pos.trunc())

    def draw_text(self, output_str: str, pos: Point, color: color_t):
        """
        supports newlines in string
        """

        for i, s in enumerate(output_str.split('\n')):
            offset = (0, i * (self.FONT_HEIGHT + 2))
            rendered_text = self.led_matrix_font.render(s, 0, color << 8)
            self.mock_matrix.blit(rendered_text, (pos + offset).trunc())

            output_str_t = transform.scale_by(self.font.render(s, 0, color << 8), 4)
            self.head.blit(output_str_t, ((pos + offset) * self.scale).trunc())

    def load_gif(self, gif_path: str):
        return pygame.image.load(gif_path).convert_alpha()

    def draw_gif(self, gif, pos: Point):
        self.head.blit(transform.scale_by(gif, self.scale), tuple(pos * self.scale))
        self.mock_matrix.blit(gif, pos.trunc())

    def load_audio(self, audio_file: str):
        return mixer.Sound(audio_file)

    def play_audio(self, audio):
        if not mixer.get_busy():
            audio.play()

    def read_input(self) -> HeadInput:
        for event in pygame.event.get():
            if event.type == QUIT or (
                    event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_q)):
                return HeadInput(False, FaceExpression.NA)
        if pygame.key.get_pressed()[K_a]:
            return HeadInput(True, FaceExpression.QUESTION)
        elif pygame.key.get_pressed()[K_s]:
            return HeadInput(True, FaceExpression.LOCK_IN)
        elif pygame.key.get_pressed()[K_d]:
            return HeadInput(True, FaceExpression.HUG_EYES)
        elif pygame.key.get_pressed()[K_f]:
            return HeadInput(True, FaceExpression.POG)
        elif pygame.key.get_pressed()[K_g]:
            return HeadInput(True, FaceExpression.FIRE)
        elif pygame.key.get_pressed()[K_z]:
            return HeadInput(True, FaceExpression.SPIN)
        if mixer.get_busy():
            mixer.stop()
        return HeadInput(True, FaceExpression.NA)

    def status_led(self, color: color_t):
        draw.circle(self.screen, color, (1,1), 5)

    def update(self, face_data: BlendshapeData = BlendshapeData()):
        self.screen.fill(GREY)

        flipped_img = transform.flip(self.head, True, False)
        rot_img = transform.rotate(flipped_img, face_data.head.az)
        self.screen.blit(rot_img, (face_data.head.x * 1000 + 100, -face_data.head.y * 1000 + 100))
        self.head.fill(BLACK)


        self._bitdepth_conversion_buf.blit(self.mock_matrix, (0, 0))
        self.screen.blit(transform.scale_by(self._bitdepth_conversion_buf, self.scale), (0, self.SCREEN_OFFSET))
        self.screen.blit(self.hole_mask, (0, self.SCREEN_OFFSET), special_flags=BLEND_RGBA_MULT)
        self.mock_matrix.fill(BLACK)
        self._bitdepth_conversion_buf.fill(BLACK)

        # print Blendshape values
        offset = self.WIDTH * self.scale + 100
        for i, e in enumerate(BlendshapeData.attr_list()):  # this is jank
            output_str = e + ": " + str(getattr(face_data, e))
            output_str_t = self.font.render(output_str, 1, WHITE << 8 | 255)  # 255 is for alpha
            self.screen.blit(output_str_t, (4 + offset, i * 16))

        # display fps
        fps = "Minbitt Head preview - FPS: " + str(int(self.clock.get_fps()))
        display.set_caption(fps)
        # fps_t = font.render(fps, 1, RED)
        # screen.blit(fps_t, (0, 0))
        display.flip()
        self.clock.tick(self.FPS)

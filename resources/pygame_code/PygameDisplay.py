from minbitt_pkg.DisplayInterface import *
from pygame import *
import pygame.event


class PygameDisplay(DisplayInterface):
    def __init__(self, WIDTH, HEIGHT, COLOR_KEY, FPS=60, scale=10, DEBUG_TEXT_WIDTH=575, DEBUG_TEXT_HEIGHT=600):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.COLOR_KEY: color_t = COLOR_KEY
        self.pixel_buff = [[BLACK for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.FPS = FPS
        self.scale = scale
        self.DEBUG_TEXT_WIDTH = DEBUG_TEXT_WIDTH
        self.DEBUG_TEXT_HEIGHT = DEBUG_TEXT_HEIGHT
        self.SCREEN_OFFSET = 599
        # self.head: Surface = surface.Surface((WIDTH,HEIGHT))
        self.head: Surface = surface.Surface((WIDTH * self.scale, HEIGHT * self.scale))

    def __enter__(self):
        init()
        self.screen = display.set_mode(
            (self.WIDTH * self.scale + self.DEBUG_TEXT_WIDTH, self.HEIGHT * self.scale + self.DEBUG_TEXT_HEIGHT))
        self.clock = time.Clock()
        self.font = font.SysFont("Arial", 14, bold=True)
        # self.font = font.SysFont("Calibri", 15, bold=True)
        return self

    def get_width(self) -> int:
        return self.WIDTH

    def get_height(self) -> int:
        return self.HEIGHT

    def load_image(self, image_path: str, flipped=False) -> Surface:
        img = image.load(image_path)
        if flipped:
            img = transform.flip(img, True, False)
        img.set_colorkey(Color(self.COLOR_KEY << 8 | 255))
        return img

    def load_gif(self, gif_path: str):
        return pygame.image.load(gif_path).convert_alpha()

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
        return HeadInput(True, FaceExpression.FIRE)#NA)

    def draw_line(self, color: color_t, start_pos: Point, end_pos: Point, width: int = 1):
        draw.line(self.head, color, tuple(start_pos * self.scale), tuple(end_pos * self.scale), width * self.scale)
        bresenham(self.pixel_buff, color, start_pos.trunc(), end_pos.trunc(), width)

    def draw_circle(self, color: color_t, center: Point, radius: int, fill: bool = False):
        """
        Bresenham's circle algorithm: https://funloop.org/post/2021-03-15-bresenham-circle-drawing-algorithm.html
        :param color:
        :param center:
        :param radius:
        :param fill:
        :return:
        """
        # assert pos.x - radius >= 0 and pos.y - radius >= 0

        draw.circle(self.head, color, tuple(center * self.scale), (radius + 0.3) * self.scale, not fill)

        def draw_pixel(y: int, x: int):  # TODO: idk optimize for out of bound draw
            if self.WIDTH <= x or x < 0 or self.HEIGHT <= y or y < 0:
                return
            self.pixel_buff[y][x] = color

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
            if fill:
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
                # self.pixel_buff[pos.y + y][pos.x + x] = color
                # self.pixel_buff[pos.y + y][pos.x - x] = color
                # self.pixel_buff[pos.y - y][pos.x + x] = color
                # self.pixel_buff[pos.y - y][pos.x - x] = color
                # self.pixel_buff[pos.y + x][pos.x + y] = color
                # self.pixel_buff[pos.y - x][pos.x + y] = color
                # self.pixel_buff[pos.y + x][pos.x - y] = color
                # self.pixel_buff[pos.y - x][pos.x - y] = color

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

    def blit(self, image: Surface, pos: Point):
        self.head.blit(transform.scale_by(image, self.scale), tuple(pos * self.scale))
        # TODO: idk decide out of pixel_buff bounds asserts

        cord = pos.trunc()
        for y in range(image.get_height()):
            for x in range(image.get_width()):
                c = image.get_at((x, y))
                if int(c) >> 8 == self.COLOR_KEY:
                    continue
                if self.WIDTH <= x or x < 0 or self.HEIGHT <= y or y < 0:  # TODO: can be optimized out if needed
                    continue
                self.pixel_buff[y + cord[1]][x + cord[0]] = c

    def draw_text(self, output_str: str, pos: Point, color: color_t):
        # output_str_t = transform.scale_by(self.font.render(output_str, 0, color), self.scale)  # FIXME:
        output_str_t = transform.scale_by(self.font.render(output_str, 0, color << 8 | 255), 4)
        self.head.blit(output_str_t, (pos * self.scale).trunc())
        for x in range(output_str_t.get_width() // self.scale):
            for y in range(output_str_t.get_height() // self.scale):
                sample_cord = (x * self.scale + 5, y * self.scale + 5)
                self.pixel_buff[y + pos.y][x + pos.x] = output_str_t.get_at(sample_cord)[:3]

    def draw_gif(self, gif, pos: Point):
        self.head.blit(transform.scale_by(gif, self.scale), tuple(pos * self.scale))

    def update(self, face_data: BlendshapeData = BlendshapeData()):
        self.screen.fill(GREY)

        # flipped_img = transform.flip(transform.scale_by(self.head,self.scale), True, False)
        flipped_img = transform.flip(self.head, True, False)
        rot_img = transform.rotate(flipped_img, face_data.head.az)
        self.screen.blit(rot_img, (face_data.head.x * 1000 + 100, -face_data.head.y * 1000 + 100))

        # TODO: idk figure out proper refresh (idk maybe have 2 cp of each sprite)
        self.head.fill(BLACK)

        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                pixel_color = self.pixel_buff[y][x]
                draw.rect(self.screen, pixel_color,
                          Rect(x * self.scale + 1, y * self.scale + 1 + self.SCREEN_OFFSET,
                               self.scale - 2, self.scale - 2))

        # print Blendshape values
        offset = self.WIDTH * self.scale + 100
        for i, e in enumerate(sorted(face_data.__dict__)):
            output_str = e + ": " + str(face_data.__dict__[e])
            output_str_t = self.font.render(output_str, 1, WHITE << 8 | 255)  # TODO: idk kinda jank
            self.screen.blit(output_str_t, (4 + offset, i * 16))

        # display fps
        fps = "FPS: " + str(int(self.clock.get_fps()))
        display.set_caption(fps)
        # fps_t = font.render(fps, 1, RED)
        # screen.blit(fps_t, (0, 0))
        display.flip()
        self.clock.tick(self.FPS)

        # TODO: find better spot to put this
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                self.pixel_buff[y][x] = BLACK

    def __exit__(self, exc_type, exc_val, exc_tb):
        quit()

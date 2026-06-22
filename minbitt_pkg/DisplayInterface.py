from math import isnan, sqrt, exp
from minbitt_pkg.BlendshapeData import BlendshapeData
from micropython import const

color_t = int

RED = const(0xff0000)  # (255, 0, 0))
GREEN = const(0x00ff00)  # (0, 255, 0))
BLUE = const(0x0000ff)  # (0, 0, 255))
YELLOW = const(0xffff00)  # (255, 255, 0))
MINBITT_BLUE = const(0x5FCDE4)  # (0x5F, 0xCD, 0xE4)
MINBITT_LIGHTBLUE = const(0x88EBFF)
BLACK = const(0)  # (0, 0, 0)
WHITE = const(0xFFFFFF)  # (255, 255, 255)
GREY = const(0x6e6e6e)  # (110, 110, 110)
PINK = const(0xFF00FF)  # (255, 0, 255)


class Point:
    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    def __add__(self, other: "Point | tuple[float, float]") -> "Point":
        return Point(self.x + other[0], self.y + other[1])

    def __sub__(self, other: "Point"):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float):
        return Point(other * self.x, other * self.y)

    def __getitem__(self, item) -> float:
        return self.x if item == 0 else self.y

    def __iter__(self):
        yield self.x
        yield self.y

    def trunc(self) -> tuple[int, int]:
        return int(self.x), int(self.y)


class FaceExpression:  # (Enum):
    NA = const(0)
    QUESTION = const(1)
    NOTE = const(2)
    LOCK_IN = const(3)
    HUG_EYES = const(4)
    POG = const(5)
    FIRE = const(6)
    SPIN = const(7)


class HeadInput:
    def __init__(self, running: bool, face_expr: FaceExpression):
        self.running: bool = running
        self.face_expr: FaceExpression = face_expr


class DisplayInterface:

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_width(self) -> int:
        pass

    def get_height(self) -> int:
        pass

    def draw_line(self, color: color_t, start_pos: Point, end_pos: Point, width: int = 1):
        pass

    def draw_circle(self, color: color_t, pos: Point, radius: int):
        pass

    def load_image(self, image_path, flipped=False):  # -> GenericImage:
        pass

    def blit(self, image, pos: Point):
        pass

    def draw_text(self, output_str: str, pos: Point, color: color_t):
        pass

    def load_gif(self, gif_path: str):
        pass

    def draw_gif(self, gif, pos: Point):
        pass

    def load_audio(self, audio_file: str):
        pass

    def play_audio(self, audio):
        pass

    def read_input(self) -> HeadInput:
        pass

    def status_led(self, color: color_t):
        pass

    def frame_buffer(self):# TODO: decide
        pass

    def update(self, face_data: BlendshapeData = None):
        pass


class AnimationInterface:
    def animate_face(self, face_data: BlendshapeData, head_input: HeadInput) -> None:
        pass

def bresenham(pixel_buff, color: color_t, start_pos: tuple[int, int], end_pos: tuple[int, int], width: int = 1):
    """
    uses Bresenham's line algorithm
    :param pixel_buff:
    :param color:
    :param start_pos:
    :param end_pos:
    :param width:
    :return:
    """

    x0, y0 = start_pos
    x1, y1 = end_pos

    swap = abs(x1 - x0) <= abs(y1 - y0)
    if swap:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0

    dir = -1 if dy < 0 else 1
    dy *= dir

    double_dy = 2 * dy
    double_dx = 2 * dx
    slope_error_new = double_dy - dx
    y = y0
    for x in range(x0, x1):
        if swap:  # can be optimized out
            if 0 > y or y >= len(pixel_buff[0]) or 0 > x or x >= len(
                    pixel_buff):  # can be optimized out if needed
                continue
            pixel_buff[x][y] = color
        else:
            if 0 > y or y >= len(pixel_buff) or 0 > x or x >= len(
                    pixel_buff[0]):  # can be optimized out if needed
                continue
            pixel_buff[y][x] = color

        if slope_error_new >= 0:
            y += dir
            slope_error_new -= double_dx
        slope_error_new += double_dy


def clamp(n, min, max):
    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n


def sigmoid(x: float) -> float:
    return 1 / (1 + exp(-x))


def lerp(v0: float | Point, v1: float | Point, t: float | Point) -> float | Point:
    return v0 * (1 - t) + v1 * t


def _quadratic_solve(a, b, c) -> tuple[float, float]:
    root_a = float('nan')
    root_b = float('nan')
    # straight line case
    if a == 0:
        if b != 0:
            root_a = -c / b
    else:
        discriminant = b * b - 4 * a * c
        if discriminant >= 0:
            s = sqrt(discriminant)
            root_a = (-b + s) / (2 * a)
            root_b = (-b - s) / (2 * a)
    return root_a, root_b


class QuadraticBezierCurve:
    """
    2D Bezier Curve
    """

    def __init__(self, p0: Point, p1: Point, p2: Point):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2

        self.lines = [((0.0, 0.0), (0.0, 0.0)) for _ in
                      range(320)]  # FIXME: idk max HEIGHT needs to be input here or something
        # TODO: idk find better solution of needing to dynamically update self.lines size
        # self.lines = [((0.0, 0.0), (0.0, 0.0)) for _ in range(self.get_rect().height)]

    # def draw(self, surface: Surface, resolution=20):
    #     display.draw_circle(RED, Point(int(self.p0[0]),int(self.p0[1])), 1, True)
    #     display.draw_circle(BLUE, Point(int(self.p1[0]),int(self.p1[1])), 1, True)
    #     display.draw_circle(BLUE, Point(int(self.p2[0]),int(self.p2[1])), 1, True)
    #     draw.rect(surface, RED, self.get_rect())
    #     points = [self.get_point(i / resolution) for i in range(resolution)] + [self.p2]
    #     draw.lines(surface, GREEN, False, points, 2)

    def fill(self, display: DisplayInterface, color: tuple[int, int, int]):
        """
        fills the inside part of the Bézier curve with one color

        :param display:
        :param color:
        :return:
        """
        # display.draw_circle(RED, Point(int(self.p0[0]),int(self.p0[1])), 1, True)
        # display.draw_circle(BLUE, Point(int(self.p1[0]),int(self.p1[1])), 1, True)
        # display.draw_circle(BLUE, Point(int(self.p2[0]),int(self.p2[1])), 1, True)
        r = self.get_rect()
        for y in range(r[1], r[1] + r[3]):
            i = y - r[1]
            # Note: if you need to optimize more horizontal_ray_intersection calls get_point which calculates
            # both x and y, but we only use x.
            intersect0, intersect1 = self.horizontal_line_intersection(y)
            if intersect0 is not None and intersect1 is not None:
                self.lines[i] = (intersect0, intersect1)
            elif intersect0 is None and intersect1 is None:
                # cuz of floating point error the bounding box is not tight
                # and line might miss the top of the Bézier curve
                self.lines[i] = ((0.0, 0.0), (0.0, 0.0))
            else:
                # calculate diagonal line (y = mx+b) between p0 and p2
                dx = (self.p2[0] - self.p0[0])
                if dx == 0:
                    self.lines[i] = ((0, y), intersect0 if intersect0 is not None else intersect1)
                    continue
                m = (self.p2[1] - self.p0[1]) / dx + 0.0001  # FIXME: this +0.0001 prevents m=0 and div by 0
                b = self.p0[1] - m * self.p0[0]
                diag_x = (y - b) / m  # FIXME prevent div by 0
                if intersect0 is not None:
                    self.lines[i] = (intersect0, (diag_x, y))
                elif intersect1 is not None:
                    self.lines[i] = ((diag_x, y), intersect1)

        for i in range(r[3]):  # Note r.height is less than len(self.lines)
            l = self.lines[i]
            # draw.line(surface, color, l[0], l[1])
            display.draw_line(color, Point(round(l[0][0]), round(l[0][1])), Point(round(l[1][0]), round(l[1][1])))

    def get_point(self, t: float) -> tuple[float, float] | None:
        """
        Note: this will truncate the result and will return None if t is outside the range 0 to 1

        :param t: float
        :return: 2D coordinate
        """
        if 0 <= t <= 1:
            ans = ((self.p0[0] - 2 * self.p1[0] + self.p2[0]) * t * t + 2 * (self.p1[0] - self.p0[0]) * t + self.p0[0],
                   (self.p0[1] - 2 * self.p1[1] + self.p2[1]) * t * t + 2 * (self.p1[1] - self.p0[1]) * t + self.p0[1])
            return ans
        # return self.p0 if t < 0 else self.p2
        return None

    def get_rect(self) -> tuple[int, int, int, int]:
        """
        analytically solves for the Bézier curve's of bounding box
        :return: pygame.Rect
        """
        m_x = (self.p0[0] - 2 * self.p1[0] + self.p2[0])
        m_y = (self.p0[1] - 2 * self.p1[1] + self.p2[1])
        t0 = clamp((self.p0[0] - self.p1[0]) / m_x, 0, 1) if m_x != 0 else 0
        t1 = clamp((self.p0[1] - self.p1[1]) / m_y, 0, 1) if m_y != 0 else 0
        p_x = self.get_point(t0)
        p_y = self.get_point(t1)
        x = min(self.p0[0], self.p2[0], p_x[0], p_y[0])
        y = min(self.p0[1], self.p2[1], p_x[1], p_y[1])
        width = max(self.p0[0], self.p2[0], p_x[0], p_y[0]) - x
        height = max(self.p0[1], self.p2[1], p_x[1], p_y[1]) - y
        return int(x), int(y), int(width), int(height)

    def horizontal_line_intersection(self, line: float) -> tuple[tuple[float, float], tuple[float, float]]:
        """
        gets the points that intersect with the horizontal line

        :param line: float
        :return: two tuples, if the line misses then it returns None
        """
        a = self.p0[1] - 2 * self.p1[1] + self.p2[1]
        b = 2 * (self.p1[1] - self.p0[1])
        c = self.p0[1]
        t0, t1 = _quadratic_solve(a, b, c - line)

        return self.get_point(t0) if not isnan(t0) else None, self.get_point(t1) if not isnan(t1) else None

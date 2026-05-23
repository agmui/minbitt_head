from minbitt_pkg.EnvSettings import EnvSettings
from minbitt_pkg.iFacialMocap import *
# from minbitt_pkg.BlueToothConnection import BlueToothConnection
from minbitt_pkg.BlendshapeData import BlendshapeData
from minbitt_pkg.DisplayInterface import *
from minbitt_pkg.MinBittAnimation import MinBittAnimation
from minbitt_pkg.SansAnimation import SansAnimation


class AnimationTest(AnimationInterface):
    def __init__(self, display: DisplayInterface, proj_env: str):
        self.display = display
        sprite_dir = "minbitt_pkg/"  # TODO: add const to all paths
        self.L_eye = display.load_image(proj_env + sprite_dir + "sprites/eye/eye1.bmp")
        self.left_eye_xy = Point(0, 8)
        self.sus_eye = display.load_image(proj_env + sprite_dir + "sprites/sus_squint.bmp") # non palette bmp

        self.mouth = display.load_image(proj_env + sprite_dir + "sprites/mouth_pixelated_w.bmp")
        self.mouth_xy = Point(26, 12)

        self.left_eyebrow_start = Point(5, 5)
        self.left_eyebrow_end = Point(15, 7)
        self.right_eye_xy = Point(40, 20)

        self.mouth_pos = Point(25, -5)

        self.p0_frame1 = self.mouth_pos + (8, 13)
        self.p1_frame1 = self.mouth_pos + (10, 15)
        self.p2_frame1 = self.mouth_pos + (12, 13)
        self.p0_frame2 = self.mouth_pos + (0, 13)
        self.p1_frame2 = self.mouth_pos + (8, 30)
        self.p2_frame2 = self.mouth_pos + (20, 13)
        self.spline = QuadraticBezierCurve(self.p0_frame2, self.p1_frame2, self.p2_frame2)
        self.fire_gif = self.display.load_gif(proj_env + sprite_dir + "sprites/fire.gif")


    def animate_face(self, face_data: BlendshapeData, head_input: HeadInput) -> None:
        self.left_eye_xy.x += 1
        self.left_eye_xy.x %= 10
        self.display.blit(self.L_eye, self.left_eye_xy + (40, 0))
        self.display.blit(self.sus_eye, self.left_eye_xy + (40, 5))

        self.display.blit(self.mouth, self.mouth_xy)
        self.display.draw_line(MINBITT_BLUE, self.left_eyebrow_start, self.left_eyebrow_end, 1)
        self.display.draw_line(MINBITT_BLUE, self.left_eyebrow_start + (0, 0), self.left_eyebrow_end + (0, 0), 1)
        self.display.draw_line(MINBITT_BLUE, self.left_eyebrow_start + (0, 5), self.left_eyebrow_end + (0, 5), 1)
        self.display.draw_line(MINBITT_BLUE, self.left_eyebrow_start + (0, 10), self.left_eyebrow_end + (0, 10), 1)
        self.display.draw_line(MINBITT_BLUE, self.left_eyebrow_start + (0, 15), self.left_eyebrow_end + (0, 15), 1)
        self.display.draw_line(MINBITT_BLUE, self.left_eyebrow_start + (0, 20), self.left_eyebrow_end + (0, 20), 1)
        self.display.draw_circle(MINBITT_BLUE, self.right_eye_xy, 3, True)

        if self.left_eye_xy.x % 5 == 0:
            if self.spline.p1.y % 2 == 0:
                self.spline.p0.x += 1
                self.spline.p0.x %= 10
                self.spline.p0.x += 12
            self.spline.p1.y += 1
            self.spline.p1.y %= 25
        self.spline.fill(self.display, MINBITT_BLUE)

        self.display.blit(self.mouth, self.mouth_xy + (10, -10))
        # self.display.draw_gif(self.fire_gif, Point(0, 0)) #uncomment to show gif


def main(env_settings: EnvSettings):
    sample_data_dir = "minbitt_pkg/sample_data/"
    proj_env = env_settings.proj_env
    d = env_settings.display
    HEIGHT = d.get_height()
    WIDTH = d.get_width()

    # Note: display must be inited first
    with d as display, env_settings.connection as connection:
    # with d as display, MockConnection(proj_env + sample_data_dir + "data.txt") as connection:
    # with d as display, CachedConnection(proj_env+sample_data_dir+"data.txt") as connection:
    # with d as display, DebugFaceConnection(proj_env+sample_data_dir+"data.txt", display) as connection:
    # with d as display, BlueToothConnection() as connection:

        # minbitt_animation: AnimationInterface = AnimationTest(display, proj_env)
        # minbitt_animation: AnimationInterface = MinBittAnimation(display, proj_env)
        minbitt_animation: AnimationInterface = SansAnimation(display, proj_env)
        no_wifi_img = display.load_image(proj_env + "minbitt_pkg/" + "sprites/no_wifi.bmp")
        loading = 0
        running = True
        while running:
            try:
                while running:
                    head_input = display.read_input()
                    running = head_input.running
                    face_data = connection.get_data()
                    # face_data = connection.get_data()
                    # print(msg.decode('utf-8'))

                    minbitt_animation.animate_face(face_data, head_input)
                    display.update(face_data)

            except (TimeoutError, OSError):
                # TODO: maybe have cute tv glitch effect(burst.png burst2.png) here instead of no wifi logo
                # or put cute tv glitch effect on first turn on of head
                display.blit(no_wifi_img, Point(0, 0))
                if loading >= 10:
                    display.draw_line(MINBITT_BLUE, Point(4, HEIGHT // 2), Point(5, HEIGHT // 2))
                if loading >= 20:
                    display.draw_line(MINBITT_BLUE, Point(8, HEIGHT // 2), Point(9, HEIGHT // 2))
                if loading >= 30:
                    display.draw_line(MINBITT_BLUE, Point(12, HEIGHT // 2), Point(13, HEIGHT // 2))
                loading += 1
                loading %= 40
                print("waiting for frames")
                display.update()
    # TODO: handel Network is unreachable if ip cant be found

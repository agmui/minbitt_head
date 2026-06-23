from minbitt_pkg.DisplayInterface import *

class AnimationTest(AnimationInterface):
    def __init__(self, display: DisplayInterface, proj_env: str):
        self.display = display
        sprite_dir = "minbitt_pkg/"
        self.L_eye = display.load_image(proj_env + sprite_dir + "assets/eye/eye1.bmp")
        self.left_eye_xy = Point(0, 8)
        self.R_eye = display.load_image(proj_env + sprite_dir + "assets/eye/eye1.bmp", True)

        self.mouth = display.load_image(proj_env + sprite_dir + "assets/mouth_pixelated_w.bmp")
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
        self.fire_gif = self.display.load_gif(proj_env + sprite_dir + "assets/fire.gif")


    def animate_face(self, face_data: BlendshapeData, head_input: HeadInput) -> None:
        self.left_eye_xy.x += 1
        self.left_eye_xy.x %= 10
        self.display.blit(self.L_eye, self.left_eye_xy + (40, 0))
        self.display.blit(self.R_eye, self.left_eye_xy + (40, 5))

        self.display.blit(self.mouth, self.mouth_xy)
        self.display.draw_line(MINBITT_BLUE, self.left_eyebrow_start, self.left_eyebrow_end, 1)
        self.display.draw_line(MINBITT_BLUE, self.left_eyebrow_start + (0, 0), self.left_eyebrow_end + (0, 0), 1)
        self.display.draw_line(MINBITT_BLUE, self.left_eyebrow_start + (0, 5), self.left_eyebrow_end + (0, 5), 1)
        self.display.draw_line(MINBITT_BLUE, self.left_eyebrow_start + (0, 10), self.left_eyebrow_end + (0, 10), 1)
        self.display.draw_line(MINBITT_BLUE, self.left_eyebrow_start + (0, 15), self.left_eyebrow_end + (0, 15), 1)
        self.display.draw_line(MINBITT_BLUE, self.left_eyebrow_start + (0, 20), self.left_eyebrow_end + (0, 20), 1)
        self.display.draw_circle(MINBITT_BLUE, self.right_eye_xy, 3)

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


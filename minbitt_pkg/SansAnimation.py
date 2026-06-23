from minbitt_pkg.BlendshapeData import BlendshapeData
from minbitt_pkg.DisplayInterface import *
from minbitt_pkg.DisplayInterface import AnimationInterface


class SansAnimation(AnimationInterface):
    def __init__(self, display: DisplayInterface, proj_env: str):

        self.display = display
        sprite_dir = "minbitt_pkg/assets/sans_heads/"

        head_width = 32
        head_height = 30
        self.center_point = Point(32 - head_width / 2, 1)
        self.left_eye_pos = Point(24,14)
        self.right_eye_pos = Point(38,14)

        self.sans_basic = display.load_image(proj_env + sprite_dir + "sans_basic.bmp")
        self.sans_blue = display.load_image(proj_env + sprite_dir + "sans_blue.bmp")
        self.sans_eyes_closed = display.load_image(proj_env + sprite_dir + "sans_eyes_closed.bmp")
        self.sans_eyes_wide = display.load_image(proj_env + sprite_dir + "sans_eyes_wide.bmp")
        self.sans_wink_L = display.load_image(proj_env + sprite_dir + "sans_wink.bmp")
        self.sans_wink_R = display.load_image(proj_env + sprite_dir + "sans_wink.bmp", flipped=True)
        self.sans_yellow = display.load_image(proj_env + sprite_dir + "sans_yellow.bmp")
        self.sans_happy = display.load_image(proj_env + sprite_dir + "sans_happy.bmp")

    def animate_face(self, face_data: BlendshapeData, head_input: HeadInput) -> None:
        if face_data.eyeBlink_L > 60 and face_data.eyeBlink_R > 60:
            self.display.blit(self.sans_eyes_closed, self.center_point)
        elif face_data.eyeBlink_L > 60:
            self.display.blit(self.sans_wink_L, self.center_point)
        elif face_data.eyeBlink_R > 60:
            self.display.blit(self.sans_wink_R, self.center_point)
        elif face_data.eyeWide_L > 65 and face_data.eyeWide_R > 65:
            self.display.blit(self.sans_eyes_wide, self.center_point)
        elif face_data.cheekSquint_L > 50 and face_data.cheekSquint_R:
            self.display.blit(self.sans_happy, self.center_point)
        elif face_data.browDown_L > 70 and face_data.browDown_R > 70:
            self.display.blit(self.sans_blue, self.center_point)
            return
        else:
            self.display.blit(self.sans_basic, self.center_point)

        # == eyes ==
        left_eye_xy = self.left_eye_pos + (-face_data.leftEye.y * 0.15, face_data.leftEye.p * 0.08)
        self.display.draw_circle(WHITE, left_eye_xy, 0)
        if not(face_data.eyeWide_L > 45 and face_data.eyeWide_R > 45):
            self.display.draw_circle(WHITE, left_eye_xy+(1,0), 0)
            self.display.draw_circle(WHITE, left_eye_xy+(0,1), 0)
            self.display.draw_circle(WHITE, left_eye_xy+(1,1), 0)

        right_eye_xy = self.right_eye_pos + (-face_data.leftEye.y * 0.15, face_data.leftEye.p * 0.08)
        self.display.draw_circle(WHITE, right_eye_xy, 0)
        if not(face_data.eyeWide_L > 45 and face_data.eyeWide_R > 45):
            self.display.draw_circle(WHITE, right_eye_xy+(1,0), 0)
            self.display.draw_circle(WHITE, right_eye_xy+(0,1), 0)
            self.display.draw_circle(WHITE, right_eye_xy+(1,1), 0)


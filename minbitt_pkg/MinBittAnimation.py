from minbitt_pkg.BlendshapeData import BlendshapeData
from minbitt_pkg.DisplayInterface import *
from minbitt_pkg.DisplayInterface import AnimationInterface


class MinBittAnimation(AnimationInterface):
    def __init__(self, display: DisplayInterface, proj_env: str):
        self.display = display
        self.WIDTH = self.display.get_width()
        self.HEIGHT = self.display.get_height()

        # == loading sprites ==
        # eyes
        eye_sprites = [
            "assets/eye/eye1.bmp",
            "assets/eye/eye2.bmp",
            "assets/eye/eye3.bmp",
            "assets/eye/eye4.bmp",
        ]
        project_dir = "minbitt_pkg/"
        self.L_eye = [display.load_image(proj_env + project_dir + i) for i in eye_sprites]
        self.R_eye = [display.load_image(proj_env + project_dir + i, True) for i in eye_sprites]
        self.L_X3_eye = display.load_image(proj_env + project_dir + "assets/eye/X3_eye.bmp")
        self.R_X3_eye = display.load_image(proj_env + project_dir + "assets/eye/X3_eye.bmp", True)
        # self.sus_squint = display.load_image(proj_env+sprite_dir+"sprites/eye/sus_squint.bmp")
        # TODO: make sus_squint with bezier curves/generalize with wide eye animation

        # mouth
        self.mouth_top = display.load_image(proj_env + project_dir + "assets/mouth_pixelated_w.bmp")
        mouth_sprites = [
            "assets/mouth/mouth1.bmp",
            "assets/mouth/mouth2.bmp",
            "assets/mouth/mouth3.bmp",
            "assets/mouth/mouth4.bmp",
        ]
        self.mouth_top_small = display.load_image(proj_env + project_dir + mouth_sprites[0])
        self.blush = display.load_image(proj_env + project_dir + "assets/blush.bmp")

        audio_files = [
            "assets/faaah_16kHz_128k.mp3"
            # "faaah.mp3",
            # "rick_roll.mp3",
        ]
        self.sound_clips = [display.load_audio(proj_env + project_dir + i) for i in audio_files]

        # expressions
        self.question_expr = display.load_image(proj_env + project_dir + "assets/expressions/question_expr.bmp")
        self.pog_expr = display.load_image(proj_env + project_dir + "assets/expressions/pog.bmp")
        # add keyframes system

        eye_spacing = 40
        self.L_eyebrow_pos = Point(5, 6)
        self.R_eyebrow_pos = Point(5 + eye_spacing, 6)
        self.brow_tune = 0.1  # TODO: add sliders in pygame
        self.brow_down_tune = 0.05

        self.left_eye_pos = Point(5, 8)
        self.right_eye_pos = Point(5 + eye_spacing, 8)
        self.eye_tune_x = 0.2
        self.eye_tune_y = 0.2

        self.X3_thresh = 60
        self.eyeWide_thresh = 45
        self.eyeWide_thresh_upper = 70
        self.min_r = 4
        self.max_r = 11
        self.mouth_pos = Point(22, 10)
        self.mouth_tune = 0.8  # 0.5
        self.mouth_close_tune = 1
        self.mouth_xy_tune = 1
        self.mouth_talk_thresh = 4.3

        self.p0_frame1 = self.mouth_pos + (8, 13)
        self.p1_frame1 = self.mouth_pos + (10, 15)
        self.p2_frame1 = self.mouth_pos + (12, 13)
        self.p0_frame2 = self.mouth_pos + (0, 13)
        self.p1_frame2 = self.mouth_pos + (8, 30)
        self.p2_frame2 = self.mouth_pos + (20, 13)
        self.spline = QuadraticBezierCurve(self.p0_frame1, self.p1_frame1, self.p2_frame1)

        self.tv_glitch_line = 0
        self.tv_glitch_animation = False
        self.prev_input = FaceExpression.NA
        self.fire_gif = self.display.load_gif(proj_env + project_dir + "assets/fire.gif")
        self.spinbitt_gif = self.display.load_gif(proj_env + project_dir + "assets/spinbitt.gif")

    def animate_face(self, face_data: BlendshapeData, head_input: HeadInput) -> None:
        # edge led lighting
        self.display.draw_line(PINK,Point(0,0), Point(0,self.HEIGHT))# TODO: idk make these cycle rainbow or something
        self.display.draw_line(PINK,Point(self.WIDTH-1,0), Point(self.WIDTH-1,self.HEIGHT-1))

        if self.prev_input != head_input.face_expr:
            self.prev_input = head_input.face_expr
            self.tv_glitch_animation = True
        if self.tv_glitch_animation:
            if self.tv_glitch_line < self.HEIGHT:
                self.display.draw_line(MINBITT_BLUE, Point(0, self.tv_glitch_line), Point(self.WIDTH, self.tv_glitch_line))
                self.tv_glitch_line += 7
                return
            else:
                self.tv_glitch_line = 0
                self.tv_glitch_animation = False

        # == face expressions ==
        if head_input.face_expr == FaceExpression.QUESTION:
            self.display.blit(self.question_expr, Point(0, 0))
            return
        elif head_input.face_expr == FaceExpression.LOCK_IN:
            self.display.draw_text("LOCK IN", Point(5, self.HEIGHT // 2 - 4), MINBITT_BLUE)
            return
        elif head_input.face_expr == FaceExpression.POG:
            self.display.play_audio(self.sound_clips[0]) #TODO: fix audio start point bug by preloading the audio during tv_glitch_animation
            self.display.blit(self.pog_expr, Point(0, 0))
            return
        elif head_input.face_expr == FaceExpression.FIRE:
            self.display.draw_gif(self.fire_gif, Point(10, 0))
            return
        elif head_input.face_expr == FaceExpression.SPIN:
            self.display.draw_gif(self.spinbitt_gif, Point(0,0))
            return

        # ==================================================================================
        # == left eyebrow ==
        left_eyebrow_start = self.L_eyebrow_pos + (0.0, -self.brow_tune * face_data.browOuterUp_L)
        left_eyebrow_end = self.L_eyebrow_pos + (
            10, -self.brow_tune * face_data.browInnerUp + self.brow_down_tune * face_data.browDown_L)
        # TODO: check if this looks good
        if face_data.cheekSquint_L <= self.X3_thresh:  # X3 face animation
            self.display.draw_line(MINBITT_BLUE, left_eyebrow_start, left_eyebrow_end, 1)

        # == right eyebrow ==
        right_eyebrow_start = self.R_eyebrow_pos + (
            0, - self.brow_tune * face_data.browInnerUp + self.brow_down_tune * face_data.browDown_R)
        right_eyebrow_end = self.R_eyebrow_pos + (10, - self.brow_tune * face_data.browOuterUp_R)
        # TODO: check if this looks good
        if face_data.cheekSquint_R <= self.X3_thresh:  # X3 face animation
            self.display.draw_line(MINBITT_BLUE, right_eyebrow_start, right_eyebrow_end, 1)

        # == left eye ==
        left_eye_xy = self.left_eye_pos + (
            -face_data.leftEye.y * self.eye_tune_x, face_data.leftEye.p * self.eye_tune_y)
        eye_index = face_data.eyeBlink_L * 5 // 100
        eye_index = eye_index if eye_index < 4 else 3

        if face_data.eyeWide_L < self.eyeWide_thresh:  # wide eyes animation
            if face_data.cheekSquint_L > self.X3_thresh:  # X3 face animation
                self.display.blit(self.L_X3_eye, left_eye_xy)
            else:
                if head_input.face_expr == FaceExpression.HUG_EYES and eye_index == 0:  # TODO: idk decide if u like
                    self.display.draw_line(MINBITT_LIGHTBLUE, left_eye_xy + Point(0, -30), left_eye_xy + Point(0, 30))
                    self.display.draw_line(MINBITT_LIGHTBLUE, left_eye_xy + Point(-30, 2), left_eye_xy + Point(30, 2))
                # self.display.blit(self.sus_squint, left_eye_xy + (-3, -1))
                self.display.blit(self.L_eye[eye_index],
                                  left_eye_xy + (-3, -1))  # TODO: check math on offset of X3 face
        else:
            r = int(lerp(self.min_r, self.max_r, (face_data.eyeWide_L - self.eyeWide_thresh) / (
                    self.eyeWide_thresh_upper - self.eyeWide_thresh)))
            self.display.draw_circle(MINBITT_BLUE, left_eye_xy + (3, 3), r)
            self.display.draw_circle(MINBITT_BLUE, left_eye_xy + (3, 3), 0)

        # == right eye ==
        right_eye_xy = self.right_eye_pos + (
            -face_data.rightEye.y * self.eye_tune_x, face_data.rightEye.p * self.eye_tune_y)
        eye_index = face_data.eyeBlink_R * 5 // 100
        eye_index = eye_index if eye_index < 4 else 3
        if face_data.eyeWide_R < self.eyeWide_thresh:
            if face_data.cheekSquint_R > self.X3_thresh:  # X3 face animation
                self.display.blit(self.R_X3_eye, right_eye_xy + (0, -1))
            else:
                # self.display.blit(self.sus_squint, right_eye_xy + (-3, -1))
                self.display.blit(self.R_eye[eye_index], right_eye_xy)
        else:
            r = int(lerp(self.min_r, self.max_r, (face_data.eyeWide_R - self.eyeWide_thresh) / (
                    self.eyeWide_thresh_upper - self.eyeWide_thresh)))
            self.display.draw_circle(MINBITT_BLUE, right_eye_xy + (3, 3), r)
            self.display.draw_circle(MINBITT_BLUE, right_eye_xy + (3, 3), 0)

        # == mouth ==
        final_mouth_pos = self.mouth_pos  # move mouth down if eyeWide animation
        eyeWide = max(face_data.eyeWide_L, face_data.eyeWide_R)
        if eyeWide > self.eyeWide_thresh:
            t = (eyeWide - 45) / (70 - 45)
            final_mouth_pos = lerp(self.mouth_pos, self.mouth_pos + (0, 4), t)
        mouth_dx = final_mouth_pos.x - self.mouth_pos.x
        # print(mouth_dx)
        mouth_form = ((face_data.mouth_form + 100) / 200.0) * self.mouth_tune
        new_p0 = lerp(self.p0_frame1.x, self.p0_frame2.x, mouth_form - eyeWide * 0.005)
        new_p2 = lerp(self.p2_frame1.x, self.p2_frame2.x, mouth_form - eyeWide * 0.005)  # TODO: tune
        self.spline.p0 = Point(new_p0,
                               self.spline.p0.y)  # TODO: if needed make update() func in Point class avoiding reassign
        self.spline.p2 = Point(new_p2, self.spline.p2.y)  # TODO: sub mouth_dx

        mouth_open = self.mouth_close_tune * face_data.mouth_open / 10.0  # div by 10 to "keyframe" the important mouth speach range
        scale = sigmoid(0.7 * mouth_open - 2)
        new_p1 = lerp(self.p1_frame1.y, self.p1_frame2.y, scale)
        # bot of mouth LR
        new_p1_x = self.p1_frame1.x - self.mouth_xy_tune * (face_data.mouthLowerDown_L - face_data.mouthLowerDown_R)
        self.spline.p1 = Point(new_p1_x, new_p1)

        if abs(self.spline.p0.y - self.spline.p1.y) > self.mouth_talk_thresh:
            self.display.draw_line(MINBITT_BLUE, final_mouth_pos + (8, 12), final_mouth_pos + (12, 12))
            self.spline.fill(self.display, MINBITT_BLUE)

        # top of mouth
        if eyeWide > self.eyeWide_thresh:
            self.display.blit(self.mouth_top_small, final_mouth_pos + (7, 7))
        else:
            self.display.blit(self.mouth_top, final_mouth_pos)

        # == blush ==
        self.display.blit(self.blush, final_mouth_pos + (33, 8))
        self.display.blit(self.blush, final_mouth_pos + (-19, 8))


    """
    TODO: maybe to prevent this have an abstract class extend Animation Interface that has already written the deinit
    func, then also have it write load_img, load_gif ... and store all ref internally. Then it can free all that itself
    """
    # def deinit(self): # TODO: free all assets
    #     self.display.free_gif(self.spinbitt_gif)
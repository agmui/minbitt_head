from minbitt_pkg.BlendshapeData import BlendshapeData
from minbitt_pkg.DisplayInterface import *
from minbitt_pkg.DisplayInterface import AnimationInterface
from minbitt_pkg.iFacialMocap import ConnectionInterface


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
        self.left_eye_pos = Point((self.WIDTH-eye_spacing)//2-3, 7)
        self.right_eye_pos = Point(self.left_eye_pos.x + eye_spacing, 7)
        self.eye_tune_x = 0.2
        self.eye_tune_y = 0.2

        self.L_eyebrow_pos = Point(self.left_eye_pos.x-2, 4)
        self.R_eyebrow_pos = Point(self.L_eyebrow_pos.x + eye_spacing-1, 4)
        self.brow_tune = 0.1
        self.brow_down_tune = 0.05

        self.X3_thresh = 60
        self.eyeWide_thresh = 70
        self.eyeWide_thresh_upper = 80
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
        self.spinbitt_gif = self.display.load_gif(proj_env + project_dir + "assets/spinbitt.gif")

        self.rainbow_edge = list(map(rgb24_to_rgb16, [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, VIOLET, PINK]))
        self.rot = 0
        self.reset_led = False

    def animate_face(self, dt: float, face_data: BlendshapeData, controller_input: ControllerInput,
                     connection: ConnectionInterface) -> None:
        # edge rgb lighting
        frame_buff = self.display.frame_buffer()
        l = len(self.rainbow_edge)
        for i in range(self.HEIGHT):
            c = self.rainbow_edge[(i - self.rot) % l]
            j = i * self.WIDTH
            # frame_buff[j] = c
            # frame_buff[j+self.WIDTH-1] = c
        self.rot += round(dt * 60)
        self.rot %= len(self.rainbow_edge)
        self.display.dirty(frame_buff)

        if self.prev_input != controller_input.face_expr:
            self.prev_input = controller_input.face_expr
            self.tv_glitch_animation = True
        if self.tv_glitch_animation:
            if self.tv_glitch_line < self.HEIGHT:
                self.display.draw_line(MINBITT_BLUE, Point(0, self.tv_glitch_line),
                                       Point(self.WIDTH, self.tv_glitch_line))
                self.tv_glitch_line += 7
                return
            else:
                self.tv_glitch_line = 0
                self.tv_glitch_animation = False

        # == face expressions ==
        if controller_input.face_expr == FaceExpression.QUESTION:
            self.display.blit(self.question_expr, Point(0, 0))
            return
        elif controller_input.face_expr == FaceExpression.LOCK_IN:
            self.display.draw_text("LOCK IN", Point(5, self.HEIGHT // 2 - 4), MINBITT_BLUE)
            return
        elif controller_input.face_expr == FaceExpression.POG:
            self.display.play_audio(self.sound_clips[
                                        0])  # TODO: fix audio start point bug by preloading the audio during tv_glitch_animation
            self.display.blit(self.pog_expr, Point(0, 0))
            return
        elif controller_input.face_expr == FaceExpression.LOOK_FORWARD:
            connection.send_data("iFacialMocap_lookForward".encode('utf-8'))
            return
        elif controller_input.face_expr == FaceExpression.SPIN:
            self.display.draw_gif(self.spinbitt_gif, Point(0, 0))
            return

        # ==================================================================================


        # == left eye ==
        left_eye_xy = self.left_eye_pos + (
            -face_data.leftEye.y * self.eye_tune_x, face_data.leftEye.p * self.eye_tune_y)
        eye_index = face_data.eyeBlink_L * 5 // 100
        eye_index = eye_index if eye_index < 4 else 3
        left_eye_wide_r = 0
        if face_data.eyeWide_L < self.eyeWide_thresh:  # wide eyes animation
            if face_data.cheekSquint_L > self.X3_thresh:  # X3 face animation
                self.display.blit(self.L_X3_eye, left_eye_xy)
            else:
                if controller_input.face_expr == FaceExpression.HUG_EYES and eye_index == 0:
                    self.display.draw_line(MINBITT_LIGHTBLUE, left_eye_xy + Point(3, -2), left_eye_xy + Point(3, 7))
                    self.display.draw_line(MINBITT_LIGHTBLUE, left_eye_xy + Point(-1, 2), left_eye_xy + Point(7, 2))
                self.display.blit(self.L_eye[eye_index], left_eye_xy)
        else:
            left_eye_wide_r = int(lerp(self.min_r, self.max_r, (face_data.eyeWide_L - self.eyeWide_thresh) / (
                    self.eyeWide_thresh_upper - self.eyeWide_thresh)))
            self.display.draw_circle(MINBITT_BLUE, left_eye_xy + (3, 3), left_eye_wide_r)
            self.display.draw_circle(MINBITT_BLUE, left_eye_xy + (3, 3), 0)

        # == right eye ==
        right_eye_xy = self.right_eye_pos + (
            -face_data.rightEye.y * self.eye_tune_x, face_data.rightEye.p * self.eye_tune_y)
        eye_index = face_data.eyeBlink_R * 5 // 100
        eye_index = eye_index if eye_index < 4 else 3
        right_eye_wide_r = 0
        if face_data.eyeWide_R < self.eyeWide_thresh:
            if face_data.cheekSquint_R > self.X3_thresh:  # X3 face animation
                self.display.blit(self.R_X3_eye, right_eye_xy)
            else:
                if controller_input.face_expr == FaceExpression.HUG_EYES and eye_index == 0:
                    self.display.draw_line(MINBITT_LIGHTBLUE, right_eye_xy + Point(2, -2), right_eye_xy + Point(2, 7))
                    self.display.draw_line(MINBITT_LIGHTBLUE, right_eye_xy + Point(-2, 2), right_eye_xy + Point(6, 2))
                self.display.blit(self.R_eye[eye_index], right_eye_xy)
        else:
            right_eye_wide_r = int(lerp(self.min_r, self.max_r, (face_data.eyeWide_R - self.eyeWide_thresh) / (
                    self.eyeWide_thresh_upper - self.eyeWide_thresh)))
            self.display.draw_circle(MINBITT_BLUE, right_eye_xy + (3, 3), right_eye_wide_r)
            self.display.draw_circle(MINBITT_BLUE, right_eye_xy + (3, 3), 0)

        # == left eyebrow ==
        left_eyebrow_follow_eye_offset = ((left_eye_xy-self.left_eye_pos) * 0.5) + (0, - left_eye_wide_r // 2)
        left_eyebrow_start = (self.L_eyebrow_pos + (0.0, -self.brow_tune * face_data.browOuterUp_L)
                              + left_eyebrow_follow_eye_offset)
        left_eyebrow_end = (self.L_eyebrow_pos
                            + (10, -self.brow_tune * face_data.browInnerUp + self.brow_down_tune * face_data.browDown_L)
                            + left_eyebrow_follow_eye_offset)
        if face_data.cheekSquint_L <= self.X3_thresh:  # X3 face animation
            self.display.draw_line(MINBITT_BLUE, left_eyebrow_start, left_eyebrow_end, 1)

        # == right eyebrow ==
        # print(left_eye_xy.x, left_eye_xy.y, right_eye_xy.x, right_eye_xy.y)
        right_eyebrow_follow_eye_offset = ((right_eye_xy-self.right_eye_pos) * 0.5) + (0, - right_eye_wide_r // 2)
        right_eyebrow_start = (self.R_eyebrow_pos
                               + (
                                   0,
                                   -self.brow_tune * face_data.browInnerUp + self.brow_down_tune * face_data.browDown_R)
                               + right_eyebrow_follow_eye_offset)
        right_eyebrow_end = (self.R_eyebrow_pos + (10, - self.brow_tune * face_data.browOuterUp_R)
                             + right_eyebrow_follow_eye_offset)
        if face_data.cheekSquint_R <= self.X3_thresh:  # X3 face animation
            self.display.draw_line(MINBITT_BLUE, right_eyebrow_start, right_eyebrow_end, 1)

        # == mouth ==
        final_mouth_pos = self.mouth_pos  # move mouth down if eyeWide animation
        eyeWide = max(face_data.eyeWide_L, face_data.eyeWide_R)
        mouth_dy = 0
        if eyeWide > self.eyeWide_thresh:
            t = (eyeWide - 45) / (70 - 45)
            final_mouth_pos = lerp(self.mouth_pos, self.mouth_pos + (0, 4), t)
            mouth_dy = final_mouth_pos.y - self.mouth_pos.y - 1
        mouth_form = ((face_data.mouth_form + 100) / 200.0) * self.mouth_tune
        # min is to account of the case when eyeWide
        new_p0_x = lerp(self.p0_frame1.x, self.p0_frame2.x, mouth_form - eyeWide * min(0.008, mouth_dy))
        new_p2_x = lerp(self.p2_frame1.x, self.p2_frame2.x, mouth_form - eyeWide * min(0.008, mouth_dy))
        new_p0_y = self.p0_frame1.y + mouth_dy
        new_p2_y = self.p2_frame1.y + mouth_dy
        self.spline.p0 = Point(new_p0_x, new_p0_y)
        self.spline.p2 = Point(new_p2_x, new_p2_y)

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

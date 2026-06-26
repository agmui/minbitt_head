import traceback

from minbitt_pkg.EnvSettings import EnvSettings
from minbitt_pkg.iFacialMocap import *
# from minbitt_pkg.BlueToothConnection import BlueToothConnection
from minbitt_pkg.BlendshapeData import BlendshapeData
from minbitt_pkg.DisplayInterface import *
from minbitt_pkg.MinBittAnimation import MinBittAnimation


def main(env_settings: EnvSettings):
    sample_data_dir = "minbitt_pkg/sample_data/"
    proj_env = env_settings.proj_env
    d = env_settings.display
    minbitt_animation = env_settings.animation
    HEIGHT = d.get_height()
    WIDTH = d.get_width()

    try:
        # Note: display must be inited first
        with d as display, env_settings.connection as connection:
        # with d as display, MockConnection(proj_env + sample_data_dir + "data.txt") as connection:
        # with d as display, CachedConnection(proj_env+sample_data_dir+"data.txt") as connection:
        # with d as display, DebugFaceConnection(proj_env+sample_data_dir+"data.txt", display) as connection:
        # with d as display, BlueToothConnection() as connection:

            no_wifi_img = display.load_image(proj_env + "minbitt_pkg/" + "assets/no_wifi.bmp")
            loading = 0
            reset_led_to_green = True
            running = True
            dt = 0.0
            while running:
                try:
                    while running:
                        head_input = display.read_input()
                        running = head_input.running
                        face_data = connection.get_data()

                        if face_data.trackingStatus == 0: # check if phone can see face
                            display.status_led(ORANGE)
                        elif reset_led_to_green:
                            display.status_led(GREEN)
                        reset_led_to_green = face_data.trackingStatus == 0

                        minbitt_animation.animate_face(dt, face_data, head_input, connection)
                        dt = display.update(face_data)

                except (TimeoutError, OSError) as e:
                    # TODO: maybe have cute tv glitch effect(burst.png burst2.png) here instead of no wifi logo
                    # or put cute tv glitch effect on first turn on of head
                    display.status_led(YELLOW)
                    reset_led_to_green = True
                    display.blit(no_wifi_img, Point(0, 0))
                    if loading >= 10:
                        display.draw_line(MINBITT_BLUE, Point(4, HEIGHT // 2), Point(5, HEIGHT // 2))
                    if loading >= 20:
                        display.draw_line(MINBITT_BLUE, Point(8, HEIGHT // 2), Point(9, HEIGHT // 2))
                    if loading >= 30:
                        display.draw_line(MINBITT_BLUE, Point(12, HEIGHT // 2), Point(13, HEIGHT // 2))
                    loading += 1
                    loading %= 40
                    debug_log("waiting for frames")
                    display.update()
        # TODO: handel Network is unreachable if ip cant be found
    except Exception as e:
        print("\n======= exception occurred ========\n")
        traceback.print_exception(e)
        display.status_led(RED)

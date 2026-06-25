from ipaddress import IPv4Address
import time
from socketpool import *
import wifi

from minbitt_pkg.iFacialMocap import ConnectionInterface
from minbitt_pkg.decode_iFacialMocap import *
from minbitt_pkg.DisplayInterface import *
from minbitt_pkg.BlendshapeData import BlendshapeData

class CircuitPythonConnection(ConnectionInterface):
    def __init__(self, display: DisplayInterface, port=49983):
        # set access point credentials
        self.ap_ssid = "myAP"  # TODO: pull from file system just in case you forget
        self.ap_password = "esp32wifipass"
        self.port = port
        # self.buf = bytearray(1024)#TODO: idk do testing
        # https://stackoverflow.com/questions/19671145/how-can-i-quickly-set-a-python-bytearray-to-0
        self.display = display
        self.face_data = BlendshapeData()

    def __enter__(self):


        """
        TODO: debug faces:
        1. init face (minbitt head v1)
        2. started ap (list ap) with loading circle saying "waiting for connections
        3. if connection found list ip
        4. send init string and wait for response
        5. if no response after a while go back to 4
        6. if there is a response continue
        """

        text_pos = Point(0, 0)

        self.display.draw_text("Minbitt head\nv1.0", text_pos + (2, 1), MINBITT_BLUE)
        self.display.update()
        time.sleep(0.2)

        debug_log("starting ap")
        wifi.radio.start_ap(ssid=self.ap_ssid, password=self.ap_password, max_connections=1)

        # print ssid
        debug_log("ssid:",self.ap_ssid)

        echo_time = None
        self.phone_ip = IPv4Address("0.0.0.0")
        while echo_time is None:
            self.display.status_led(BLUE)
            debug_log("scanning")
            wifi.radio.start_scanning_networks()
            wifi.radio.stop_scanning_networks()
            for i in range(10):
                self.display.draw_text(f"connect to: {self.ap_ssid}", text_pos + (2, 0), MINBITT_BLUE)
                self.display.draw_text("waiting", text_pos + (2, 8), MINBITT_BLUE)
                if i >= 2:
                    self.display.draw_circle(MINBITT_BLUE, text_pos + (30, 13), 1)
                if i >= 5:
                    self.display.draw_circle(MINBITT_BLUE, text_pos + (35, 13), 1)
                if i >= 8:
                    self.display.draw_circle(MINBITT_BLUE, text_pos + (40, 13), 1)
                self.display.update()
                if len(wifi.radio.stations_ap) > 0:
                    debug_log(wifi.radio.stations_ap)#TODO: can randomly get index out of range error?
                    if wifi.radio.stations_ap[0].ipv4_address is not None:
                        break
                time.sleep(0.4)
                self.display.status_led(BLUE if i % 2 else BLACK) # flash blue and black while waiting for connection
            else:
                debug_log("starting over")
                continue
            debug_log(wifi.radio.stations_ap)
            self.phone_ip = wifi.radio.stations_ap[0].ipv4_address  # TODO: idk check is None sometimes can happen if too fast
            debug_log("ping", self.phone_ip)
            echo_time = wifi.radio.ping(self.phone_ip, timeout=1)  # to test connection after finding phone ip addr
            debug_log("echo_time", echo_time)

        self.display.status_led(MINBITT_LIGHTBLUE)
        debug_log("creating socket pool")
        pool = SocketPool(wifi.radio)

        debug_log("creating UDP socket")
        self.udpClntSock = pool.socket(SocketPool.AF_INET, SocketPool.SOCK_DGRAM)

        debug_log("creating UDP client")
        self.server = pool.socket(SocketPool.AF_INET, SocketPool.SOCK_DGRAM)
        self.server.bind(("", 49983))
        self.server.settimeout(0.5)

        data = "iFacialMocap_sahuasouryya9218sauhuiayeta91555dy3719"
        data = data.encode('utf-8')
        response = None
        while response is None:
            self.display.draw_text(f"Hotspot: {self.ap_ssid}", text_pos + (2, 0), MINBITT_BLUE)
            self.display.draw_text(f"found\n{self.phone_ip}", text_pos + (2, 8), MINBITT_BLUE)
            self.display.draw_text("open iFacialMocap", text_pos + (2, 23), MINBITT_BLUE)
            self.display.update()

            debug_log("sending", data)
            self.udpClntSock.sendto(data, (str(self.phone_ip), self.port))
            buf = bytearray(1024)
            try:
                response = self.server.recvfrom_into(buf)
            except OSError:
                # TODO: handel case if phone disconnects from ap by checking ping?
                debug_log("retrying")

        return self

    def send_data(self, data: str) -> int:
        """
        send commands to iFaciallMocap:

            `reset_face("iFacialMocap_lookForward")`
        """
        debug_log("sending", data)
        return self.udpClntSock.sendto(data, (str(self.phone_ip), self.port))

    def get_data(self):
        buf = bytearray(1024)
        # clears the most recent msg and waits for next to get most uptodate data
        # msg_size, address = self.server.recvfrom_into(bytearray(1024))
        msg_size, address = self.server.recvfrom_into(buf)  # Note can also throw OSError: [Errno 116] ETIMEDOUT
        # TODO: check if preallocating buf bytearray and zeroing out back half garbage with msg_size is faster
        # decode_iFacialMocap(buf, self.face_data)
        decode_iFacialMocap_fast(buf, self.face_data)
        return self.face_data

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.udpClntSock.close()
        self.server.close()
        wifi.radio.stop_ap()
        # TODO: free other objs


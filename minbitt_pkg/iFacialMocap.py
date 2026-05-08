import ipaddress
from ipaddress import IPv4Address

from minbitt_pkg.DisplayInterface import *
from minbitt_pkg.BlendshapeData import BlendshapeData, decode_msg
import time

if __debug__:
    from socketpool import *
    import wifi
else:
    from socket import *


class ConnectionInterface:
    def __enter__(self):
        pass

    def get_data(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


"""
class WifiConnection(ConnectionInterface):
    def __init__(self, ip: str, port=49983):
        self.server: socket
        self.DstIP: str = ip
        self.DstPort: int = port

    def __enter__(self):
        DstAddr = (self.DstIP, self.DstPort)
        udpClntSock = socket(AF_INET, SOCK_DGRAM)

        data = "iFacialMocap_sahuasouryya9218sauhuiayeta91555dy3719"
        data = data.encode('utf-8')
        udpClntSock.sendto(data, DstAddr)
        # udpClntSock.close() #TODO: idk test

        self.server = socket(AF_INET, SOCK_DGRAM)
        self.server.bind(("", 49983))
        self.server.settimeout(0.05)
        return self

    def get_data(self):
        messages, address = self.server.recvfrom(8192)
        return messages

    def __exit__(self, exc_type, exc_value, traceback):
        # self.server.close() # TODO: idk test
        pass
"""


class CircuitPythonConnection:
    def __init__(self, display: DisplayInterface, port=49983):
        # set access point credentials
        self.ap_ssid = "myAP"  # TODO: pull from file system just in case you forget
        self.ap_password = "esp32wifipass"
        self.port = port
        # self.buf = bytearray(1024)#TODO: idk do testing
        # https://stackoverflow.com/questions/19671145/how-can-i-quickly-set-a-python-bytearray-to-0
        self.display = display

    def __enter__(self):
        """
        debug faces:
        1. init face (minbitt head v1)
        2. started ap (list ap) with loading circle saying "waiting for connections
        3. if connection found list ip
        4. send init string and wait for response
        5. if no response after a while go back to 4
        6. if there is a response continue
        """

        text_pos = Point(0, 0)
        self.display.draw_text("Minbitt head\nv1.0", text_pos + (0, 1), MINBITT_BLUE)
        self.display.update(BlendshapeData())

        print("starting ap")
        wifi.radio.start_ap(ssid=self.ap_ssid, password=self.ap_password, max_connections=1)

        # print access point settings
        print(f"Access point created with SSID: {self.ap_ssid}, password: {self.ap_password}")
        # print IP address
        print("My IP address is", wifi.radio.ipv4_address_ap)

        # print("press any key to continue")
        # a = input()
        # print("starting")
        # print("sleeping 1...")
        # time.sleep(1)
        echo_time = None
        i = 0
        phone_ip: ipaddress.IPv4Address = IPv4Address("0.0.0.0")
        while echo_time is None:
            # TODO: idk flash led or something while waiting
            print("scanning")
            wifi.radio.start_scanning_networks()
            wifi.radio.stop_scanning_networks()
            for i in range(10):
                self.display.draw_text(f"ip:{wifi.radio.ipv4_address_ap}", text_pos + (0, 0), MINBITT_BLUE)
                self.display.draw_text("waiting", text_pos + (0, 8), MINBITT_BLUE)
                if i >= 2:
                    self.display.draw_circle(MINBITT_BLUE, text_pos + (30, 13), 1)
                if i >= 5:
                    self.display.draw_circle(MINBITT_BLUE, text_pos + (35, 13), 1)
                if i >= 8:
                    self.display.draw_circle(MINBITT_BLUE, text_pos + (40, 13), 1)
                self.display.update(BlendshapeData())
                if len(wifi.radio.stations_ap) > 0:
                    if wifi.radio.stations_ap[0].ipv4_address is not None:
                        break
                time.sleep(0.5)
            else:
                print("starting over")
                continue
            print(wifi.radio.stations_ap)
            phone_ip = wifi.radio.stations_ap[0].ipv4_address# TODO: idk check is None sometimes can happen if too fast
            print("ping", phone_ip)
            echo_time = wifi.radio.ping(phone_ip,
                                        timeout=1)  # to test connection after finding phone ip addr
            print("echo_time", echo_time)

        print("creating socket pool")
        pool = SocketPool(wifi.radio)

        print("creating UDP socket")
        udpClntSock = pool.socket(SocketPool.AF_INET, SocketPool.SOCK_DGRAM)

        print("creating UDP client")
        self.server = pool.socket(SocketPool.AF_INET, SocketPool.SOCK_DGRAM)
        self.server.bind(("", 49983))
        self.server.settimeout(5)

        data = "iFacialMocap_sahuasouryya9218sauhuiayeta91555dy3719"
        data = data.encode('utf-8')
        response = None
        while response is None:
            self.display.draw_text(f"ip:{wifi.radio.ipv4_address_ap}", text_pos + (0, 0), MINBITT_BLUE)
            self.display.draw_text(f"found\n{phone_ip}", text_pos + (0, 8), MINBITT_BLUE)
            self.display.draw_text("open iFacialMocap", text_pos + (0, 23), MINBITT_BLUE)
            self.display.update(BlendshapeData())

            print("sending", data)
            udpClntSock.sendto(data, (str(phone_ip), self.port))
            buf = bytearray(1024)
            try:
                response = self.server.recvfrom_into(buf)
            except OSError:
                # TODO: handel case if phone disconnects from ap by checking ping?
                print("retrying")

        return self

    def get_data(self):
        buf = bytearray(1024)
        # clears the most recent msg and waits for next to get most uptodate data
        # msg_size, address = self.server.recvfrom_into(bytearray(1024))
        msg_size, address = self.server.recvfrom_into(buf) # Note can also throw OSError: [Errno 116] ETIMEDOUT
        # TODO: check if preallocating buf bytearray and zeroing out back half garbage with msg_size is faster

        return buf

    def __exit__(self, exc_type, exc_val, exc_tb):
        wifi.radio.stop_ap()
        # TODO: free other objs


class DebugFaceConnection(ConnectionInterface):
    def __init__(self, file: str, display: DisplayInterface):
        self.f = open(file, "rb")
        self.display = display

    def __enter__(self):
        text_pos = Point(0, 0)
        for i in range(350):
            if i < 100:
                self.display.draw_text("Minbitt head\nv1.0", text_pos + (0, 1), MINBITT_BLUE)
                # TODO: idk add cute face splash/animation + sound?
            if 150 < i:
                self.display.draw_text("ip:192.168.1.4", text_pos + (0, 0), MINBITT_BLUE)
                if i < 250:
                    self.display.draw_text("waiting", text_pos + (0, 8), MINBITT_BLUE)
                    if i % 50 >= 12:
                        self.display.draw_circle(MINBITT_BLUE, text_pos + (30, 13), 1)
                    if i % 50 >= 25:
                        self.display.draw_circle(MINBITT_BLUE, text_pos + (35, 13), 1)
                    if i % 50 >= 36:
                        self.display.draw_circle(MINBITT_BLUE, text_pos + (40, 13), 1)
            if 250 < i:
                self.display.draw_text("found\n192.168.1.16", text_pos + (0, 8), MINBITT_BLUE)
            if 260 < i:
                self.display.draw_text("open iFacialMocap", text_pos + (0, 23), MINBITT_BLUE)
                # self.display.draw_text("run iFacialMocap", text_pos + (0, 23), MINBITT_BLUE)

            self.display.update(BlendshapeData())
            if not self.display.read_input().running:
                exit(0)
        return self

    def get_data(self):
        msg = self.f.readline()[:-1]
        if msg == b'':
            self.f.seek(0)
            return self.f.readline()[:-1]
        else:
            return msg

    def __exit__(self, exc_type, exc_value, traceback):
        self.f.close()


class MockConnection(ConnectionInterface):
    def __init__(self, file: str):
        self.f = open(file, "rb")

    def __enter__(self):
        return self

    def get_data(self):
        msg = self.f.readline()[:-1]
        if msg == b'':
            self.f.seek(0)
            return self.f.readline()[:-1]
        else:
            return msg

    def __exit__(self, exc_type, exc_value, traceback):
        self.f.close()


class CachedConnection(ConnectionInterface):
    def __init__(self, file: str, limit=100):
        with open(file, "rb") as f:
            self.index = 0
            self.len = 0
            self.arr = []
            for l in f:
                b = BlendshapeData()
                decode_msg(l, b)
                self.arr.append(b)
                self.len += 1
                if self.len >= limit:
                    break

    def __enter__(self):
        return self

    def get_data(self):
        self.index += 1
        self.index %= self.len
        return self.arr[self.index]

    def __exit__(self, exc_type, exc_value, traceback):
        pass


# if __name__ == "__main__":
#     con = MockConnection()
#     con.init()
#     while True:
#         try:
#             msg = con.get_data()
#             print(msg.decode('utf-8'))
#         except:
#             pass
#     con.de_init()

if __name__ == "__main__":
    con = WifiConnection()
    con.init()
    while True:
        try:
            msg = con.get_data()
            print(msg.decode('utf-8'))
        except:
            pass
    con.de_init()

# recording to file
# with open("data_raw.txt", "wb") as f:
#     for i in range(60*5):
#         messages, address = server.recvfrom(8192)
#         f.write(messages)
#         f.write(b'\n')

# reading from file
# with open("data_raw.txt", "rb") as f:
#     for l in f:
#         message = l[:-1]
#         print(message.decode('utf-8'))

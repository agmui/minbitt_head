from socket import *

from minbitt_pkg.iFacialMocap import ConnectionInterface, decode_iFacialMocap
from minbitt_pkg.BlendshapeData import BlendshapeData

class PygameConnection(ConnectionInterface):
    def __init__(self, ip: str, port=49983):
        self.server: socket
        self.DstIP: str = ip
        self.DstPort: int = port
        self.face_data = BlendshapeData()

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
        decode_iFacialMocap(messages, self.face_data)
        return self.face_data

    def __exit__(self, exc_type, exc_value, traceback):
        # self.server.close() # TODO: idk test
        pass

if __name__ == "__main__":
    with PygameConnection("192.168.12.23") as connection:#, open("data_raw.txt", "wb") as f:
        while True:
            try:
                msg = connection.get_data()
                print(msg)
                # f.write(msg+b'\n') # recording to file
            except:
                print("waiting for msg")


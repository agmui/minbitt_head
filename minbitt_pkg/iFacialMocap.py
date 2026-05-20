from minbitt_pkg.DisplayInterface import *
from minbitt_pkg.decode_iFacialMocap import *


class ConnectionInterface:
    def __enter__(self):
        pass

    def get_data(self) -> BlendshapeData:
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class DebugFaceConnection(ConnectionInterface):
    def __init__(self, file: str, display: DisplayInterface):
        self.f = open(file, "rb")
        self.display = display
        self.face_data = BlendshapeData()

    def __enter__(self):
        text_pos = Point(0, 0)
        for i in range(310):
            if i < 100:
                self.display.draw_text("Minbitt head\nv1.0", text_pos + (0, 1), MINBITT_BLUE)
                # TODO: idk add cute face splash/animation + sound?
            if 150 < i:
                if i < 250:
                    self.display.draw_text("connect to myAP", text_pos + (0, 0), MINBITT_BLUE)
                    self.display.draw_text("waiting", text_pos + (0, 8), MINBITT_BLUE)
                    if i % 50 >= 12:
                        self.display.draw_circle(MINBITT_BLUE, text_pos + (30, 13), 1)
                    if i % 50 >= 25:
                        self.display.draw_circle(MINBITT_BLUE, text_pos + (35, 13), 1)
                    if i % 50 >= 36:
                        self.display.draw_circle(MINBITT_BLUE, text_pos + (40, 13), 1)
            if 250 < i:
                self.display.draw_text("connect to myAP", text_pos + (0, 0), MINBITT_BLUE)
                self.display.draw_text("found\n192.168.1.16", text_pos + (0, 8), MINBITT_BLUE)
            if 260 < i:
                self.display.draw_text("open iFacialMocap", text_pos + (0, 23), MINBITT_BLUE)
                # self.display.draw_text("run iFacialMocap", text_pos + (0, 23), MINBITT_BLUE)

            self.display.update()
            if not self.display.read_input().running:
                exit(0)
        return self

    def get_data(self):
        msg = self.f.readline()[:-1]
        if msg == b'':
            self.f.seek(0)
            msg = self.f.readline()[:-1]
        decode_iFacialMocap(msg, self.face_data)
        return self.face_data

    def __exit__(self, exc_type, exc_value, traceback):
        self.f.close()


class MockConnection(ConnectionInterface):
    def __init__(self, file: str):
        self.f = open(file, "rb")
        self.face_data = BlendshapeData()

    def __enter__(self):
        return self

    def get_data(self):
        msg = self.f.readline()[:-1]
        if msg == b'':
            self.f.seek(0)
            msg = self.f.readline()[:-1]
        # decode_iFacialMocap(msg, self.face_data)
        decode_iFacialMocap_fast(msg, self.face_data)
        return self.face_data

    def __exit__(self, exc_type, exc_value, traceback):
        self.f.close()


class CachedConnection(ConnectionInterface):
    def __init__(self, file: str, limit=100):
        with open(file, "rb") as f:
            self.index = 0
            self.arr = []
            for l in f:
                b = BlendshapeData()
                decode_iFacialMocap(l, b)
                self.arr.append(b)
                if len(self.arr) >= limit:
                    break

    def __enter__(self):
        return self

    def get_data(self):
        self.index += 1
        self.index %= len(self.arr)
        return self.arr[self.index]

    def __exit__(self, exc_type, exc_value, traceback):
        pass


if __name__ == "__main__":
    with MockConnection("sample_data/data.txt") as connection:
        while True:
            try:
                msg = connection.get_data()
                print(msg)
            except:
                print("waiting for msg")


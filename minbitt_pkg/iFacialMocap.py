from minbitt_pkg.DisplayInterface import *
from minbitt_pkg.BlendshapeData import BlendshapeData, HeadData, EyeData


class ConnectionInterface:
    def __enter__(self):
        pass

    def get_data(self) -> BlendshapeData:
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def decode_iFacialMocap(msg: bytearray, face_data: BlendshapeData):
    """
    msg = b"trackingStatus-1|mouthLowerDown_L-0|mouthFunnel-0|eyeSquint_L-2|jawLeft-0|eyeBlink_L-0|mouthPucker-3|mouthFrown_L-1|browDown_R-0|mouthSmile_L-0|eyeLookIn_R-0|mouthRight-0|browInnerUp-2|eyeLookDown_L-25|mouthSmile_R-0|tongueOut-0|mouthPress_L-2|mouthUpperUp_L-0|jawRight-0|mouthStretch_L-1|mouthDimple_R-1|mouthDimple_L-1|cheekPuff-0|eyeLookIn_L-25|eyeLookOut_L-0|eyeWide_R-4|eyeLookDown_R-25|eyeLookUp_R-0|mouthRollLower-1|browDown_L-0|eyeWide_L-4|mouthStretch_R-1|browOuterUp_L-0|noseSneer_L-3|mouthLowerDown_R-0|eyeSquint_R-2|mouthPress_R-2|jawOpen-0|mouthClose-0|eyeBlink_R-0|cheekSquint_L-1|noseSneer_R-3|jawForward-0|mouthRollUpper-0|eyeLookOut_R-13|mouthUpperUp_R-0|eyeLookUp_L-0|mouthShrugUpper-4|mouthLeft-0|mouthFrown_R-3|mouthShrugLower-5|cheekSquint_R-1|browOuterUp_R-1|hapihapi-0|=head#-16.512114,4.3503346,0.26299524,0.032684557,-0.08100321,-0.39741653|rightEye#8.96733,-4.780719,-0.74686855|leftEye#8.807489,-9.080697,-1.4018708|"
    bd = BlendshapeData()
    decode_msg(bytearray(msg),bd)
    print(bd)
    """
    msg = msg.decode('utf-8')
    norm, head_eye_data = msg.split('=')

    arr = norm.split('|')[:-1]
    head_eye_data = head_eye_data.split('|')[:-1]

    for e in arr:
        trait, val = e.split('-')
        setattr(face_data, trait, int(val))

    for e in head_eye_data:
        trait, val = e.split('#')
        if trait == "head":
            setattr(face_data, trait, HeadData(*map(float, val.split(','))))
        else:
            setattr(face_data, trait, EyeData(*map(float, val.split(','))))


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
        decode_iFacialMocap(msg, self.face_data)
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


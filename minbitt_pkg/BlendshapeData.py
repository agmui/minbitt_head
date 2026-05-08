class EyeData:
    """
    Euler angles X, Euler angles Y, Euler angles Z
    """

    def __init__(self, p: float, y: float, r: float):
        self.r: float = r
        self.p: float = p
        self.y: float = y

    def __repr__(self):
        return f"{self.r: .5f}, {self.p: .5f}, {self.y: .5f}"


class HeadData:
    """
    Euler angles X (degree), Euler angles Y, Euler angles Z, Position values X, Position values Y, Position values Z
    """

    def __init__(self, ax: float, ay: float, az: float, x: float, y: float, z: float):
        self.ax: float = ax
        self.ay: float = ay
        self.az: float = az
        self.x: float = x
        self.y: float = y
        self.z: float = z

    def __repr__(self):
        return f"{self.ax:.5f}, {self.ay:.5f}, {self.az:.5f} {self.x: .5f}, {self.y: .5f}, {self.z: .5f}"


# descriptions of blendshapes: https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation
class BlendshapeData:
    """
    Class to hold iFacialMocap output data

    trackingStatus - 1 |
    mouthLowerDown_L - 0 |
    mouthFunnel - 0 |
    eyeSquint_L - 2 |
    jawLeft - 0 |
    eyeBlink_L - 0 |
    mouthPucker - 3 |
    mouthFrown_L - 1 |
    browDown_R - 0 |
    mouthSmile_L - 0 |
    eyeLookIn_R - 0 |
    mouthRight - 0 |
    browInnerUp - 2 |
    eyeLookDown_L - 25 |
    mouthSmile_R - 0 |
    tongueOut - 0 |
    mouthPress_L - 2 |
    mouthUpperUp_L - 0 |
    jawRight - 0 |
    mouthStretch_L - 1 |
    mouthDimple_R - 1 |
    mouthDimple_L - 1 |
    cheekPuff - 0 |
    eyeLookIn_L - 25 |
    eyeLookOut_L - 0 |
    eyeWide_R - 4 |
    eyeLookDown_R - 25 |
    eyeLookUp_R - 0 |
    mouthRollLower - 1 |
    browDown_L - 0 |
    eyeWide_L - 4 |
    mouthStretch_R - 1 |
    browOuterUp_L - 0 |
    noseSneer_L - 3 |
    mouthLowerDown_R - 0 |
    eyeSquint_R - 2 |
    mouthPress_R - 2 |
    jawOpen - 0 |
    mouthClose - 0 |
    eyeBlink_R - 0 |
    cheekSquint_L - 1 |
    noseSneer_R - 3 |
    jawForward - 0 |
    mouthRollUpper - 0 |
    eyeLookOut_R - 13 |
    mouthUpperUp_R - 0 |
    eyeLookUp_L - 0 |
    mouthShrugUpper - 4 |
    mouthLeft - 0 |
    mouthFrown_R - 3 |
    mouthShrugLower - 5 |
    cheekSquint_R - 1 |
    browOuterUp_R - 1 |
    hapihapi - 0 |

    :param
        head:
            Left handed coordinate system
            Angle - related
            data is sent in degrees, not radians.
            Euler angles X (degree), Euler angles Y, Euler angles Z, Position values X, Position values Y, Position values Z
        rightEye:
            Left handed coordinate system
            Euler angles X, Euler angles Y, Euler angles Z
        leftEye:
            Left handed coordinate system
            Euler angles X, Euler angles Y, Euler angles Z
    """

    def __init__(self):
        self.trackingStatus: bool = False
        self.mouthLowerDown_L: int = 0
        self.mouthFunnel: int = 0
        self.eyeSquint_L: int = 0
        self.jawLeft: int = 0
        self.eyeBlink_L: int = 0
        self.mouthPucker: int = 0
        self.mouthFrown_L: int = 0
        self.browDown_R: int = 0
        self.mouthSmile_L: int = 0
        self.eyeLookIn_R: int = 0
        self.mouthRight: int = 0
        self.browInnerUp: int = 0
        self.eyeLookDown_L: int = 0
        self.mouthSmile_R: int = 0
        self.tongueOut: int = 0
        self.mouthPress_L: int = 0
        self.mouthUpperUp_L: int = 0
        self.jawRight: int = 0
        self.mouthStretch_L: int = 0
        self.mouthDimple_R: int = 0
        self.mouthDimple_L: int = 0
        self.cheekPuff: int = 0
        self.eyeLookIn_L: int = 0
        self.eyeLookOut_L: int = 0
        self.eyeWide_R: int = 0
        self.eyeLookDown_R: int = 0
        self.eyeLookUp_R: int = 0
        self.mouthRollLower: int = 0
        self.browDown_L: int = 0
        self.eyeWide_L: int = 0
        self.mouthStretch_R: int = 0
        self.browOuterUp_L: int = 0
        self.noseSneer_L: int = 0
        self.mouthLowerDown_R: int = 0
        self.eyeSquint_R: int = 0
        self.mouthPress_R: int = 0
        self.jawOpen: int = 0
        self.mouthClose: int = 0
        self.eyeBlink_R: int = 0
        self.cheekSquint_L: int = 0
        self.noseSneer_R: int = 0
        self.jawForward: int = 0
        self.mouthRollUpper: int = 0
        self.eyeLookOut_R: int = 0
        self.mouthUpperUp_R: int = 0
        self.eyeLookUp_L: int = 0
        self.mouthShrugUpper: int = 0
        self.mouthLeft: int = 0
        self.mouthFrown_R: int = 0
        self.mouthShrugLower: int = 0
        self.cheekSquint_R: int = 0
        self.browOuterUp_R: int = 0
        self.hapihapi: int = 0
        self.head: HeadData = HeadData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.rightEye: EyeData = EyeData(0.0, 0.0, 0.0)
        self.leftEye: EyeData = EyeData(0.0, 0.0, 0.0)

    def __repr__(self):
        return str(self.__dict__)

    def mouth_open(self) -> float:
        """
        calculates mouth_open from 0 to 100
        :return:
        """
        # res = abs(self.jawOpen - self.mouthClose)#, 0)
        return (self.mouthLowerDown_R + self.mouthLowerDown_R + self.mouthUpperUp_R + self.mouthUpperUp_L) / 4

    def mouth_form(self) -> float:
        """
        gets range of smile to frown range from 100 to -100
        ((mouthSmile_L + mouthSmile_R) - (mouthFrown_L + mouthFrown_R)) / 2
        :return: float
        """
        return ((self.mouthSmile_L + self.mouthSmile_R) - (self.mouthFrown_L + self.mouthFrown_R)) / 2.0


def decode_msg(msg: bytearray, face_data: BlendshapeData):
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



if __name__ == "__main__":
    msg = b"trackingStatus-1|mouthLowerDown_L-0|mouthFunnel-0|eyeSquint_L-2|jawLeft-0|eyeBlink_L-0|mouthPucker-3|mouthFrown_L-1|browDown_R-0|mouthSmile_L-0|eyeLookIn_R-0|mouthRight-0|browInnerUp-2|eyeLookDown_L-25|mouthSmile_R-0|tongueOut-0|mouthPress_L-2|mouthUpperUp_L-0|jawRight-0|mouthStretch_L-1|mouthDimple_R-1|mouthDimple_L-1|cheekPuff-0|eyeLookIn_L-25|eyeLookOut_L-0|eyeWide_R-4|eyeLookDown_R-25|eyeLookUp_R-0|mouthRollLower-1|browDown_L-0|eyeWide_L-4|mouthStretch_R-1|browOuterUp_L-0|noseSneer_L-3|mouthLowerDown_R-0|eyeSquint_R-2|mouthPress_R-2|jawOpen-0|mouthClose-0|eyeBlink_R-0|cheekSquint_L-1|noseSneer_R-3|jawForward-0|mouthRollUpper-0|eyeLookOut_R-13|mouthUpperUp_R-0|eyeLookUp_L-0|mouthShrugUpper-4|mouthLeft-0|mouthFrown_R-3|mouthShrugLower-5|cheekSquint_R-1|browOuterUp_R-1|hapihapi-0|=head#-16.512114,4.3503346,0.26299524,0.032684557,-0.08100321,-0.39741653|rightEye#8.96733,-4.780719,-0.74686855|leftEye#8.807489,-9.080697,-1.4018708|"
    bd = BlendshapeData()
    decode_msg(bytearray(msg),bd)
    print(bd)

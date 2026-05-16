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


class BlendshapeData:
    """
    Class to hold iFacialMocap output data
    descriptions of blendshapes: https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation
    all values go from 0 - 100 except for Head and Eye Data

    trackingStatus
    mouthLowerDown_L
    mouthFunnel
    eyeSquint_L
    jawLeft
    eyeBlink_L
    mouthPucker
    mouthFrown_L
    browDown_R
    mouthSmile_L
    eyeLookIn_R
    mouthRight
    browInnerUp
    eyeLookDown_L
    mouthSmile_R
    tongueOut
    mouthPress_L
    mouthUpperUp_L
    jawRight
    mouthStretch_L
    mouthDimple_R
    mouthDimple_L
    cheekPuff
    eyeLookIn_L
    eyeLookOut_L
    eyeWide_R
    eyeLookDown_R
    eyeLookUp_R
    mouthRollLower
    browDown_L
    eyeWide_L
    mouthStretch_R
    browOuterUp_L
    noseSneer_L
    mouthLowerDown_R
    eyeSquint_R
    mouthPress_R
    jawOpen
    mouthClose
    eyeBlink_R
    cheekSquint_L
    noseSneer_R
    jawForward
    mouthRollUpper
    eyeLookOut_R
    mouthUpperUp_R
    eyeLookUp_L
    mouthShrugUpper
    mouthLeft
    mouthFrown_R
    mouthShrugLower
    cheekSquint_R
    browOuterUp_R
    hapihapi

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



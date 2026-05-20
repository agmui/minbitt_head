import array

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
    def __init__(self):
        self.arr = array.array('b', [0 for _ in range(54)])
        # self.arr = array.array('i',[0 for _ in range(54)])
        # self.arr = [0 for _ in range(54)]
        self.head: HeadData = HeadData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.rightEye: EyeData = EyeData(0.0, 0.0, 0.0)
        self.leftEye: EyeData = EyeData(0.0, 0.0, 0.0)

    @staticmethod
    def attr_list() -> list:
        # return list(filter(lambda x: x[0] != "_", dir(self)))[1:]
        return ['browDown_L', 'browDown_R', 'browInnerUp', 'browOuterUp_L', 'browOuterUp_R', 'cheekPuff', 'cheekSquint_L',
         'cheekSquint_R', 'eyeBlink_L', 'eyeBlink_R', 'eyeLookDown_L', 'eyeLookDown_R', 'eyeLookIn_L', 'eyeLookIn_R',
         'eyeLookOut_L', 'eyeLookOut_R', 'eyeLookUp_L', 'eyeLookUp_R', 'eyeSquint_L', 'eyeSquint_R', 'eyeWide_L',
         'eyeWide_R', 'hapihapi', 'jawForward', 'jawLeft', 'jawOpen', 'jawRight', 'mouthClose', 'mouthDimple_L',
         'mouthDimple_R', 'mouthFrown_L', 'mouthFrown_R', 'mouthFunnel', 'mouthLeft', 'mouthLowerDown_L',
         'mouthLowerDown_R', 'mouthPress_L', 'mouthPress_R', 'mouthPucker', 'mouthRight', 'mouthRollLower',
         'mouthRollUpper', 'mouthShrugLower', 'mouthShrugUpper', 'mouthSmile_L', 'mouthSmile_R', 'mouthStretch_L',
         'mouthStretch_R', 'mouthUpperUp_L', 'mouthUpperUp_R', 'noseSneer_L', 'noseSneer_R', 'tongueOut',
         'trackingStatus']

    def __repr__(self):
        return str(dict(zip(BlendshapeData.attr_list(), list(self.arr)))) + str(self.__dict__)

    @property
    def mouth_open(self) -> float:
        """
        calculates mouth_open from 0 to 100
        :return:
        """
        # res = abs(self.jawOpen - self.mouthClose)#, 0)
        return (self.mouthLowerDown_R + self.mouthLowerDown_R + self.mouthUpperUp_R + self.mouthUpperUp_L) / 4

    @property
    def mouth_form(self) -> float:
        """
        gets range of smile to frown range from 100 to -100
        ((mouthSmile_L + mouthSmile_R) - (mouthFrown_L + mouthFrown_R)) / 2
        :return: float
        """
        return ((self.mouthSmile_L + self.mouthSmile_R) - (self.mouthFrown_L + self.mouthFrown_R)) / 2.0

    @property
    def browDown_L(self) -> int: return self.arr[0]
    @property
    def browDown_R(self) -> int: return self.arr[1]
    @property
    def browInnerUp(self) -> int: return self.arr[2]
    @property
    def browOuterUp_L(self) -> int: return self.arr[3]
    @property
    def browOuterUp_R(self) -> int: return self.arr[4]
    @property
    def cheekPuff(self) -> int: return self.arr[5]
    @property
    def cheekSquint_L(self) -> int: return self.arr[6]
    @property
    def cheekSquint_R(self) -> int: return self.arr[7]
    @property
    def eyeBlink_L(self) -> int: return self.arr[8]
    @property
    def eyeBlink_R(self) -> int: return self.arr[9]
    @property
    def eyeLookDown_L(self) -> int: return self.arr[10]
    @property
    def eyeLookDown_R(self) -> int: return self.arr[11]
    @property
    def eyeLookIn_L(self) -> int: return self.arr[12]
    @property
    def eyeLookIn_R(self) -> int: return self.arr[13]
    @property
    def eyeLookOut_L(self) -> int: return self.arr[14]
    @property
    def eyeLookOut_R(self) -> int: return self.arr[15]
    @property
    def eyeLookUp_L(self) -> int: return self.arr[16]
    @property
    def eyeLookUp_R(self) -> int: return self.arr[17]
    @property
    def eyeSquint_L(self) -> int: return self.arr[18]
    @property
    def eyeSquint_R(self) -> int: return self.arr[19]
    @property
    def eyeWide_L(self) -> int: return self.arr[20]
    @property
    def eyeWide_R(self) -> int: return self.arr[21]
    @property
    def hapihapi(self) -> int: return self.arr[22]
    @property
    def jawForward(self) -> int: return self.arr[23]
    @property
    def jawLeft(self) -> int: return self.arr[24]
    @property
    def jawOpen(self) -> int: return self.arr[25]
    @property
    def jawRight(self) -> int: return self.arr[26]
    @property
    def mouthClose(self) -> int: return self.arr[27]
    @property
    def mouthDimple_L(self) -> int: return self.arr[28]
    @property
    def mouthDimple_R(self) -> int: return self.arr[29]
    @property
    def mouthFrown_L(self) -> int: return self.arr[30]
    @property
    def mouthFrown_R(self) -> int: return self.arr[31]
    @property
    def mouthFunnel(self) -> int: return self.arr[32]
    @property
    def mouthLeft(self) -> int: return self.arr[33]
    @property
    def mouthLowerDown_L(self) -> int: return self.arr[34]
    @property
    def mouthLowerDown_R(self) -> int: return self.arr[35]
    @property
    def mouthPress_L(self) -> int: return self.arr[36]
    @property
    def mouthPress_R(self) -> int: return self.arr[37]
    @property
    def mouthPucker(self) -> int: return self.arr[38]
    @property
    def mouthRight(self) -> int: return self.arr[39]
    @property
    def mouthRollLower(self) -> int: return self.arr[40]
    @property
    def mouthRollUpper(self) -> int: return self.arr[41]
    @property
    def mouthShrugLower(self) -> int: return self.arr[42]
    @property
    def mouthShrugUpper(self) -> int: return self.arr[43]
    @property
    def mouthSmile_L(self) -> int: return self.arr[44]
    @property
    def mouthSmile_R(self) -> int: return self.arr[45]
    @property
    def mouthStretch_L(self) -> int: return self.arr[46]
    @property
    def mouthStretch_R(self) -> int: return self.arr[47]
    @property
    def mouthUpperUp_L(self) -> int: return self.arr[48]
    @property
    def mouthUpperUp_R(self) -> int: return self.arr[49]
    @property
    def noseSneer_L(self) -> int: return self.arr[50]
    @property
    def noseSneer_R(self) -> int: return self.arr[51]
    @property
    def tongueOut(self) -> int: return self.arr[52]
    @property
    def trackingStatus(self) -> bool: return self.arr[53]

#
# class BlendshapeData:
#     """
#     Class to hold iFacialMocap output data
#     descriptions of blendshapes: https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation
#     all values go from 0 - 100 except for Head and Eye Data
#
#     trackingStatus
#     mouthLowerDown_L
#     mouthFunnel
#     eyeSquint_L
#     jawLeft
#     eyeBlink_L
#     mouthPucker
#     mouthFrown_L
#     browDown_R
#     mouthSmile_L
#     eyeLookIn_R
#     mouthRight
#     browInnerUp
#     eyeLookDown_L
#     mouthSmile_R
#     tongueOut
#     mouthPress_L
#     mouthUpperUp_L
#     jawRight
#     mouthStretch_L
#     mouthDimple_R
#     mouthDimple_L
#     cheekPuff
#     eyeLookIn_L
#     eyeLookOut_L
#     eyeWide_R
#     eyeLookDown_R
#     eyeLookUp_R
#     mouthRollLower
#     browDown_L
#     eyeWide_L
#     mouthStretch_R
#     browOuterUp_L
#     noseSneer_L
#     mouthLowerDown_R
#     eyeSquint_R
#     mouthPress_R
#     jawOpen
#     mouthClose
#     eyeBlink_R
#     cheekSquint_L
#     noseSneer_R
#     jawForward
#     mouthRollUpper
#     eyeLookOut_R
#     mouthUpperUp_R
#     eyeLookUp_L
#     mouthShrugUpper
#     mouthLeft
#     mouthFrown_R
#     mouthShrugLower
#     cheekSquint_R
#     browOuterUp_R
#     hapihapi
#
#     :param
#         head:
#             Left handed coordinate system
#             Angle - related
#             data is sent in degrees, not radians.
#             Euler angles X (degree), Euler angles Y, Euler angles Z, Position values X, Position values Y, Position values Z
#         rightEye:
#             Left handed coordinate system
#             Euler angles X, Euler angles Y, Euler angles Z
#         leftEye:
#             Left handed coordinate system
#             Euler angles X, Euler angles Y, Euler angles Z
#     """
#
#     def __init__(self):
#         self.trackingStatus: bool = False
#         self.mouthLowerDown_L: int = 0
#         self.mouthFunnel: int = 0
#         self.eyeSquint_L: int = 0
#         self.jawLeft: int = 0
#         self.eyeBlink_L: int = 0
#         self.mouthPucker: int = 0
#         self.mouthFrown_L: int = 0
#         self.browDown_R: int = 0
#         self.mouthSmile_L: int = 0
#         self.eyeLookIn_R: int = 0
#         self.mouthRight: int = 0
#         self.browInnerUp: int = 0
#         self.eyeLookDown_L: int = 0
#         self.mouthSmile_R: int = 0
#         self.tongueOut: int = 0
#         self.mouthPress_L: int = 0
#         self.mouthUpperUp_L: int = 0
#         self.jawRight: int = 0
#         self.mouthStretch_L: int = 0
#         self.mouthDimple_R: int = 0
#         self.mouthDimple_L: int = 0
#         self.cheekPuff: int = 0
#         self.eyeLookIn_L: int = 0
#         self.eyeLookOut_L: int = 0
#         self.eyeWide_R: int = 0
#         self.eyeLookDown_R: int = 0
#         self.eyeLookUp_R: int = 0
#         self.mouthRollLower: int = 0
#         self.browDown_L: int = 0
#         self.eyeWide_L: int = 0
#         self.mouthStretch_R: int = 0
#         self.browOuterUp_L: int = 0
#         self.noseSneer_L: int = 0
#         self.mouthLowerDown_R: int = 0
#         self.eyeSquint_R: int = 0
#         self.mouthPress_R: int = 0
#         self.jawOpen: int = 0
#         self.mouthClose: int = 0
#         self.eyeBlink_R: int = 0
#         self.cheekSquint_L: int = 0
#         self.noseSneer_R: int = 0
#         self.jawForward: int = 0
#         self.mouthRollUpper: int = 0
#         self.eyeLookOut_R: int = 0
#         self.mouthUpperUp_R: int = 0
#         self.eyeLookUp_L: int = 0
#         self.mouthShrugUpper: int = 0
#         self.mouthLeft: int = 0
#         self.mouthFrown_R: int = 0
#         self.mouthShrugLower: int = 0
#         self.cheekSquint_R: int = 0
#         self.browOuterUp_R: int = 0
#         self.hapihapi: int = 0
#         self.head: HeadData = HeadData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
#         self.rightEye: EyeData = EyeData(0.0, 0.0, 0.0)
#         self.leftEye: EyeData = EyeData(0.0, 0.0, 0.0)
#
#     def __repr__(self):
#         return str(self.__dict__)
#
#     def mouth_open(self) -> float:
#         """
#         calculates mouth_open from 0 to 100
#         :return:
#         """
#         # res = abs(self.jawOpen - self.mouthClose)#, 0)
#         return (self.mouthLowerDown_R + self.mouthLowerDown_R + self.mouthUpperUp_R + self.mouthUpperUp_L) / 4
#
#     def mouth_form(self) -> float:
#         """
#         gets range of smile to frown range from 100 to -100
#         ((mouthSmile_L + mouthSmile_R) - (mouthFrown_L + mouthFrown_R)) / 2
#         :return: float
#         """
#         return ((self.mouthSmile_L + self.mouthSmile_R) - (self.mouthFrown_L + self.mouthFrown_R)) / 2.0
#

# def asdftest():
#     t = Test()
#     b = BlendshapeData()
#     b.jawOpen = 1
#     print(t.x)
#     print(b.jawOpen)
#     print("asdf")
#
#
# if __name__ == "__main__":
#     from dis import dis
#
#     print(dis(asdftest))

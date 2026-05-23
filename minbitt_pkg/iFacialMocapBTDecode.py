import json
import struct
import zlib
from micropython import const

from minbitt_pkg.BlendshapeData import BlendshapeData


def set_blendshape(blendshape: BlendshapeData, arr):
        blendshape.trackingStatus = arr[0]
        blendshape.mouthLowerDown_L = arr[1]
        blendshape.mouthFunnel = arr[2]
        blendshape.eyeSquint_L = arr[3]
        blendshape.jawLeft = arr[4]
        blendshape.eyeBlink_L = arr[5]
        blendshape.mouthPucker = arr[6]
        blendshape.mouthFrown_L = arr[7]
        blendshape.browDown_R = arr[8]
        blendshape.mouthSmile_L = arr[9]
        blendshape.eyeLookIn_R = arr[10]
        blendshape.mouthRight = arr[11]
        blendshape.browInnerUp = arr[12]
        blendshape.eyeLookDown_L = arr[13]
        blendshape.mouthSmile_R = arr[14]
        blendshape.tongueOut = arr[15]
        blendshape.mouthPress_L = arr[16]
        blendshape.mouthUpperUp_L = arr[17]
        blendshape.jawRight = arr[18]
        blendshape.mouthStretch_L = arr[19]
        blendshape.mouthDimple_R = arr[20]
        blendshape.mouthDimple_L = arr[21]
        blendshape.cheekPuff = arr[22]
        blendshape.eyeLookIn_L = arr[23]
        blendshape.eyeLookOut_L = arr[24]
        blendshape.eyeWide_R = arr[25]
        blendshape.eyeLookDown_R = arr[26]
        blendshape.eyeLookUp_R = arr[27]
        blendshape.mouthRollLower = arr[28]
        blendshape.browDown_L = arr[29]
        blendshape.eyeWide_L = arr[30]
        blendshape.mouthStretch_R = arr[31]
        blendshape.browOuterUp_L = arr[32]
        blendshape.noseSneer_L = arr[33]
        blendshape.mouthLowerDown_R = arr[34]
        blendshape.eyeSquint_R = arr[35]
        blendshape.mouthPress_R = arr[36]
        blendshape.jawOpen = arr[37]
        blendshape.mouthClose = arr[38]
        blendshape.eyeBlink_R = arr[39]
        blendshape.cheekSquint_L = arr[40]
        blendshape.noseSneer_R = arr[41]
        blendshape.jawForward = arr[42]
        blendshape.mouthRollUpper = arr[43]
        blendshape.eyeLookOut_R = arr[44]
        blendshape.mouthUpperUp_R = arr[45]
        blendshape.eyeLookUp_L = arr[46]
        blendshape.mouthShrugUpper = arr[47]
        blendshape.mouthLeft = arr[48]
        blendshape.mouthFrown_R = arr[49]
        blendshape.mouthShrugLower = arr[50]
        blendshape.cheekSquint_R = arr[51]
        blendshape.browOuterUp_R = arr[52]
        blendshape.hapihapi = arr[53]

class iFacialMocapBTDecode:
    def __init__(self):
        self.bluetooth_received_data = bytearray()
        self.encode_data_size = None
        self.decompress_json_data = {}
        self.trait_order = const([
            "trackingStatus", "mouthLowerDown_L", "mouthFunnel", "eyeSquint_L", "jawLeft", "eyeBlink_L", "mouthPucker",
            "mouthFrown_L", "browDown_R", "mouthSmile_L", "eyeLookIn_R", "mouthRight", "browInnerUp", "eyeLookDown_L",
            "mouthSmile_R", "tongueOut", "mouthPress_L", "mouthUpperUp_L", "jawRight", "mouthStretch_L",
            "mouthDimple_R",
            "mouthDimple_L", "cheekPuff", "eyeLookIn_L", "eyeLookOut_L", "eyeWide_R", "eyeLookDown_R", "eyeLookUp_R",
            "mouthRollLower", "browDown_L", "eyeWide_L", "mouthStretch_R", "browOuterUp_L", "noseSneer_L",
            "mouthLowerDown_R",
            "eyeSquint_R", "mouthPress_R", "jawOpen", "mouthClose", "eyeBlink_R", "cheekSquint_L", "noseSneer_R",
            "jawForward",
            "mouthRollUpper", "eyeLookOut_R", "mouthUpperUp_R", "eyeLookUp_L", "mouthShrugUpper", "mouthLeft",
            "mouthFrown_R",
            "mouthShrugLower", "cheekSquint_R", "browOuterUp_R", "hapihapi"
        ])
        self.blendshape_arr = [0 for _ in self.trait_order]
        self.blendshape_obj: BlendshapeData = BlendshapeData()

    def decode_blendshapes_data(self, data: bytes, index: int) -> int:
        blend_shapes = self.decompress_json_data["blendShapes"]
        blend_shape_count = len(blend_shapes)

        for i in range(blend_shape_count):
            if index >= len(data):
                break
            encoded_value = data[index]
            index += 1
            if encoded_value != 255:
                value = encoded_value - 100
                value = max(0, value)
            else:
                value = 0
            self.blendshape_arr[blend_shapes[i]] = value
            set_blendshape(self.blendshape_obj,self.blendshape_arr)
        return index

    def decode_bones_data_0x02(self, data: bytes, index: int) -> int:
        bones_list = self.decompress_json_data["bones"]
        bone_values = [0 for _ in range(12)]
        bone_values_index = 0

        for bone_info in bones_list:
            if len(bone_info) != 2:# TODO: idk decided to optimize with struct.unpack("iiiiii...
                continue

            bone_name, count = bone_info[0], bone_info[1]

            for i in range(count):
                if index + 1 >= len(data):
                    break

                high_byte = data[index]
                low_byte = data[index + 1]
                index += 2

                uint16 = (high_byte << 8) | low_byte
                int16 = struct.unpack('>h', struct.pack('>H', uint16))[0]#TODO: optimize

                if bone_name == "head" and i >= 3:
                    value = int16 / 10000.0
                else:
                    value = int16 / 10.0
                bone_values[bone_values_index] = value
                bone_values_index += 1

            # bone_values_str = ','.join(bone_values)
            # decoded.append(f"{bone_name}#{bone_values_str}")

        assert len(bone_values) == 12
        self.blendshape_obj.head.ax = bone_values[0]
        self.blendshape_obj.head.ay = bone_values[1]
        self.blendshape_obj.head.az = bone_values[2]
        self.blendshape_obj.head.x = bone_values[3]
        self.blendshape_obj.head.y = bone_values[4]
        self.blendshape_obj.head.z = bone_values[5]
        self.blendshape_obj.rightEye.r = bone_values[6]
        self.blendshape_obj.rightEye.p = bone_values[7]
        self.blendshape_obj.rightEye.y = bone_values[8]
        self.blendshape_obj.leftEye.r = bone_values[9]
        self.blendshape_obj.leftEye.p = bone_values[10]
        self.blendshape_obj.leftEye.y = bone_values[11]
        return index

    def decode_bones_data_0x03(self, data: bytes, index: int) -> int:
        raise NotImplementedError
        bones_list = self.decompress_json_data.get("bones", [])

        decoded = []
        for bone_info in bones_list:
            if len(bone_info) != 2:
                continue

            bone_name, count = bone_info[0], bone_info[1]

            bone_values = []
            for _ in range(count):
                if index + 7 >= len(data):
                    break
                chunk = data[index:index + 8]
                index += 8
                int64_val = struct.unpack('>q', chunk)[0]
                value = int64_val / 10_000_000.0
                bone_values.append(str(value))

            bone_values_str = ','.join(bone_values)
            decoded.append(f"{bone_name}#{bone_values_str}")

        decoded_str = '|'.join(decoded) + '|'
        return index

    def values_decode_data(self, data: bytes, data_size):
        index = 0
        data = data[3: 3 + data_size]

        while index < len(data):
            identifier = data[index]
            index += 1
            if identifier == 0x01:
                print("blendshapes")
                index = self.decode_blendshapes_data(data, index)
            elif identifier == 0x02:
                # print("bones2")
                index = self.decode_bones_data_0x02(data, index)
                pass
            elif identifier == 0x03:
                print("bones3")
                index = self.decode_bones_data_0x03(data, index)
                pass
            else:
                print("err")
                return

    def decompress_zlib(self, compressed_data: bytes) -> str:
        # try:
        decompressed_bytes = zlib.decompress(compressed_data)

        decompressed_text = decompressed_bytes.decode('utf-8')

        return decompressed_text
        # except Exception as e:
        #     print("err",e)
        #     return None

    def decode_msg(self, data: bytearray):
        print("decode_msg", len(data))
        self.bluetooth_received_data.extend(data)
        # try: #TODO: idk decide whether or not to add back latter
        if not self.bluetooth_received_data:
            print("bluetooth_received_data is empty")
            return
        head = self.bluetooth_received_data[0]
        if head == 0x00:
            print("head == 0x00")
            if len(self.bluetooth_received_data) > 3:
                if self.encode_data_size is None:
                    self.encode_data_size = struct.unpack(">H", self.bluetooth_received_data[1:3])[0]
                if len(self.bluetooth_received_data) >= 3 + self.encode_data_size:
                    print("json data frame msg")
                    print("encoded_data_size", self.encode_data_size)
                    comp = self.bluetooth_received_data[3: 3 + self.encode_data_size]
                    decoded = self.decompress_zlib(comp)
                    if decoded is not None:
                        self.decompress_json_data = json.loads(decoded)
                        # remap
                        blendShapes = self.decompress_json_data['blendShapes']
                        for i in range(len(blendShapes)):
                            blendShapes[i] = self.trait_order.index(blendShapes[i])
                    self.bluetooth_received_data = bytearray()
                    self.encode_data_size = None
        elif head == 0x01:
            print("found 0x01 head")
            if len(self.bluetooth_received_data) > 3:
                if self.encode_data_size is None:
                    self.encode_data_size = struct.unpack(">H", self.bluetooth_received_data[1:3])[0]
                if len(self.bluetooth_received_data) >= 3 + self.encode_data_size:
                    print("encoded_data_size", self.encode_data_size)
                    self.values_decode_data(self.bluetooth_received_data, self.encode_data_size)
                    self.bluetooth_received_data = bytearray()
                    self.encode_data_size = None
        else:
            print("err: not valid msg header, maybe only received half a msg")
            self.bluetooth_received_data = bytearray()
            self.encode_data_size = None
        # except Exception as e:
        #     bluetooth_received_data = bytearray()
        #     encode_data_size = None
        #     print("error", e)

        print("help4")

if __name__ == "__main__":
    msg1 = b'\x00\x01Jx\x9cU\x93Mk\xc30\x0c\x86\xff\x8b\xcf\xbd\rv\xd8q\xeb\n\x81BKB\xe9\xa1\x94\x91&j\xec\xc5\xb53\xc5&\x94\xb1\xff>\x7f\xc6\xf6!\xa0G\xefk[\x96\x9c_r\xe3 \xfa\x86\xb6\x13\xcc\xe4\xedBn(\x97\xad\\\xc4\xd7\x9el\x12\xd4\x01*!\x00OS\xa0\x83V\x96Vkd\xeb\xee(\xc0x\xd4\xf7{\x8c\x9b\x1f\xcd\x84r\xde\x9c\xad\x17\x9e\xf0\xce\x99\x18\x9d\xb8BP\xf6R\x8ekA9gzU\xa8U\xa1\x99\xa2r\xd1b\xa6\x86\xea\x13\x05-\xab6Q\xd0\xce\xac\x87\xa8\xb8\xd8\xe6M\x03\x99\xfdL\xf8\xdd.;\x89K\x8b\xbd\x87=\xdc\x95\x8f\x0e\x13\x08\x1f\xd5l\xa06\xf9\x90Z\xd1\x0f.g\x88\xb0e\x8f\x89\xfb\xfds\xae#\xef06#\xc3\xa4j3!\x1e)\x9c\xecc\xb9\x00n\x8b\xb5)\xb5\xae?"\xccsrxL\xaa\xeeF\xc0H\xc5\x1dj\xc9\xb9\xdb/O\x9c\xa6)%\x1a\x8az(,.Sz\x1e,\xbf\xbb\xc7\xf5\xf8F!\xa8\x8efzH\xac\x0e\xb7Y\x98i\x91\xb0\x0ea\xba\xdc\x08\x00tr"\xab))\x06\r\xe6q\xd8\x18\xdbndbhT\xab\xf4L\xae\xe6qK\xe1\xfe\x8e\x0b\xa1\xd0\x9a\xa9\xbe^7\x17\xc2Ms?\x9ffn/\x96\xd06#\xe0\xf5\xef\x1fg\xfc*V'
    msg2 = b'\x01\x00P\x01\x82\x82gddflidddd\xa0dd\x96ggpp{|dedeeeeeddedffjjgdgdpmhdkkffwwde\x02\xff~\xff\xdc\x005\xff\xc4\xff\xe3\xfd\xf8\xff\xf8\xff.\x00\x03\xff\xf8\xffP\x00\x02\x01\x00P\x01\x84\x83gddfljdddd\x9fdd\x96iipp{{dedeeeeeddedffjjgdgdqmhdkkffwxde\x02\xff~\xff\xdb\x005\xff\xc3\xff\xe2\xfd\xfc\xff\xf4\xff/\x00\x04\xff\xf4\xffQ\x00\x03\x01\x00P\x01\x84\x84gddfljd'
    # data = b"\x00\x01\x4a\x78\x9c\x55\x93\x4d\x6b\xc3\x30\x0c\x86\xff\x8b\xcf\xbd\x0d\x76\xd8\x71\xeb\x0a\x81\x42\x4b\x42\xe9\xa1\x94\x91\x26\x6a\xec\xc5\xb5\x33\xc5\x26\x94\xb1\xff\x3e\x7f\xc6\xf6\x21\xa0\x47\xef\x6b\x5b\x96\x9c\x5f\x72\xe3\x20\xfa\x86\xb6\x13\xcc\xe4\xed\x42\x6e\x28\x97\xad\x5c\xc4\xd7\x9e\x6c\x12\xd4\x01\x2a\x21\x00\x4f\x53\xa0\x83\x56\x96\x56\x6b\x64\xeb\xee\x28\xc0\x78\xd4\xf7\x7b\x8c\x9b\x1f\xcd\x84\x72\xde\x9c\xad\x17\x9e\xf0\xce\x99\x18\x9d\xb8\x42\x50\xf6\x52\x8e\x6b\x41\x39\x67\x7a\x55\xa8\x55\xa1\x99\xa2\x72\xd1\x62\xa6\x86\xea\x13\x05\x2d\xab\x36\x51\xd0\xce\xac\x87\xa8\xb8\xd8\xe6\x4d\x03\x99\xfd\x4c\xf8\xdd\x2e\x3b\x89\x4b\x8b\xbd\x87\x3d\xdc\x95\x8f\x0e\x13\x08\x1f\xd5\x6c\xa0\x36\xf9\x90\x5a\xd1\x0f\x2e\x67\x88\xb0\x65\x8f\x89\xfb\xfd\x73\xae\x23\xef\x30\x36\x23\xc3\xa4\x6a\x33\x21\x1e\x29\x9c\xec\x63\xb9\x00\x6e\x8b\xb5\x29\xb5\xae\x3f\x22\xcc\x73\x72\x78\x4c\xaa\xee\x46\xc0\x48\xc5\x1d\x6a\xc9\xb9\xdb\x2f\x4f\x9c\xa6\x29\x25\x1a\x8a\x7a\x28\x2c\x2e\x53\x7a\x1e\x2c\xbf\xbb\xc7\xf5\xf8\x46\x21\xa8\x8e\x66\x7a\x48\xac\x0e\xb7\x59\x98\x69\x91\xb0\x0e\x61\xba\xdc\x08\x00\x74\x72\x22\xab\x29\x29\x06\x0d\xe6\x71\xd8\x18\xdb\x6e\x64\x62\x68\x54\xab\xf4\x4c\xae\xe6\x71\x4b\xe1\xfe\x8e\x0b\xa1\xd0\x9a\xa9\xbe\x5e\x37\x17\xc2\x4d\x73\x3f\x9f\x66\x6e\x2f\x96\xd0\x36\x23\xe0\xf5\xef\x1f\x67\xfc\x2a\x56"
    iface_bt = iFacialMocapBTDecode()
    iface_bt.decode_msg(msg1)
    iface_bt.decode_msg(msg2)
    print(iface_bt.blendshape_obj)

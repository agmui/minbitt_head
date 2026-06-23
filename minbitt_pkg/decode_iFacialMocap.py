from minbitt_pkg.BlendshapeData import BlendshapeData, HeadData, EyeData


def decode_iFacialMocap(msg: bytearray, face_data: BlendshapeData):
    """
    msg = b"trackingStatus-1|mouthLowerDown_ ... |leftEye#8.807489,-9.080697,-1.4018708|"
    bd = BlendshapeData()
    decode_msg(bytearray(msg),bd)
    print(bd)
    """
    msg = msg.decode('utf-8')
    norm, head_eye_data = msg.split('=')

    arr = norm.split('|')[:-1]
    head_eye_data = head_eye_data.split('|')[:-1]
    attr_list = face_data.attr_list()

    for e in arr:
        trait, val = e.split('-')
        # setattr(face_data, trait, int(val))
        face_data.arr[attr_list.index(trait)] = int(val)

    for e in head_eye_data:
        trait, val = e.split('#')
        if trait == "head":
            setattr(face_data, trait, HeadData(*map(float, val.split(','))))
        else:
            setattr(face_data, trait, EyeData(*map(float, val.split(','))))

#TODO: see if can optimize into 2 separate function (init & decode) & have ConnectionInterface class hold _cached_profile
_cached_profile = {}
def decode_iFacialMocap_fast(msg: bytearray, face_data: BlendshapeData):
    blendshape_data, bones_data = msg.rsplit(b'=', 1)
    blendshape_data = blendshape_data.replace(b'-', b'|').split(b'|')[:-1]
    bones_data = bones_data.replace(b'#', b'|').replace(b',', b'|').split(b'|')[:-1]

    """
    def faster_hash(s) -> int:
        p1 = const(97)
        p2 = const(9409)  # 97 * 97
        p3 = const(912673)  # 97 * 97 * 97
        m = const(512)
        hash_value = (s[0] - 96) ^ (s[5] - 96) * p1 ^ (s[-4] - 96) * p2 ^ (s[-1] - 96) * p3
        return hash_value % m // 2
    # aaaa = [faster_hash(arr[i]) for i in range(0, len(arr), 2)]
    for i in range(0, len(arr), 2):
        # trait = aaaa[i//2]#arr[i]
        trait = arr[i]
        val = arr[i+1]
        # setattr(face_data, str(trait,'ascii'), int(val))
        res_arr[faster_hash(trait)] = int(val)
        # res_arr[res_arr[i//2]] = int(val)
    """

    key_trait = bytes(blendshape_data[2])#TODO: idk fix bytearray/bytes problem
    if key_trait in _cached_profile:  # TODO: write test to compare between a setattr and check if its the same
        remap_arr = _cached_profile[key_trait]
        res_arr = face_data.arr
        for i in range(1, 108, 2):
            # trait = arr[i]
            val = blendshape_data[i]
            res_arr[remap_arr[i // 2]] = int(val)
    else:
        remap_arr = [0 for _ in range(54)]
        for i in range(0, len(blendshape_data), 2):
            trait = str(blendshape_data[i], 'ascii')
            val = blendshape_data[i + 1]
            # setattr(face_data, trait, int(val))
            remap_arr[i // 2] = BlendshapeData.attr_list().index(trait)
            face_data.arr[remap_arr[i // 2]] = int(val)
        _cached_profile[key_trait] = remap_arr
        print("new map", _cached_profile.keys())

    face_data.head.ax = float(bones_data[1])
    face_data.head.ay = float(bones_data[2])
    face_data.head.az = float(bones_data[3])
    face_data.head.x = float(bones_data[4])
    face_data.head.y = float(bones_data[5])
    face_data.head.z = float(bones_data[6])
    face_data.rightEye.p = float(bones_data[8])
    face_data.rightEye.y = float(bones_data[9])
    face_data.rightEye.r = float(bones_data[10])
    face_data.leftEye.p = float(bones_data[12])
    face_data.leftEye.y = float(bones_data[13])
    face_data.leftEye.r = float(bones_data[14])


if __name__ == "__main__":
    msg = b"trackingStatus-1|mouthLowerDown_L-0|mouthFunnel-0|eyeSquint_L-2|jawLeft-0|eyeBlink_L-0|mouthPucker-3|mouthFrown_L-1|browDown_R-0|mouthSmile_L-0|eyeLookIn_R-0|mouthRight-0|browInnerUp-2|eyeLookDown_L-25|mouthSmile_R-0|tongueOut-0|mouthPress_L-2|mouthUpperUp_L-0|jawRight-0|mouthStretch_L-1|mouthDimple_R-1|mouthDimple_L-1|cheekPuff-0|eyeLookIn_L-25|eyeLookOut_L-0|eyeWide_R-4|eyeLookDown_R-25|eyeLookUp_R-0|mouthRollLower-1|browDown_L-0|eyeWide_L-4|mouthStretch_R-1|browOuterUp_L-0|noseSneer_L-3|mouthLowerDown_R-0|eyeSquint_R-2|mouthPress_R-2|jawOpen-0|mouthClose-0|eyeBlink_R-0|cheekSquint_L-1|noseSneer_R-3|jawForward-0|mouthRollUpper-0|eyeLookOut_R-13|mouthUpperUp_R-0|eyeLookUp_L-0|mouthShrugUpper-4|mouthLeft-0|mouthFrown_R-3|mouthShrugLower-5|cheekSquint_R-1|browOuterUp_R-1|hapihapi-0|=head#-16.512114,4.3503346,0.26299524,0.032684557,-0.08100321,-0.39741653|rightEye#8.96733,-4.780719,-0.74686855|leftEye#8.807489,-9.080697,-1.4018708|"
    bd = BlendshapeData()
    bd2 = BlendshapeData()
    decode_iFacialMocap(bytearray(msg), bd)
    decode_iFacialMocap_fast(bytearray(msg), bd2)
    print(bd)
    print(bd2)
    assert str(bd) == str(bd2)

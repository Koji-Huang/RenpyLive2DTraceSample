"""renpy

init python:
"""
import socket
import struct
import threading


udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(('127.0.0.1', 11573))

nPoints = 68
packetFrameSize = 8 + 4 + 2 * 4 + 2 * 4 + 1 + 4 + 3 * 4 + 3 * 4 + 4 * 4 + 4 * 68 + 4 * 2 * 68 + 4 * 3 * 70 + 4 * 14

FaceTraceData = dict()


def read_double(i, d):
    return struct.unpack('d', d[i:i+8])[0], i+8

def read_int32(i, d):
    return struct.unpack('i', d[i:i+4])[0], i+4

def read_float(i, d):
    return struct.unpack('f', d[i:i+4])[0], i+4

def read_Quaternion(i, d):
    return (
        struct.unpack('f', d[i:i+4])[0], 
        struct.unpack('f', d[i+4:i+8])[0], 
        struct.unpack('f', d[i+8:i+12])[0], 
        struct.unpack('f', d[i+12:i+16])[0]
        ), i+16

def read_vec3(i, d):
    return (
        struct.unpack('f', d[i:i+4])[0], 
        struct.unpack('f', d[i+4:i+8])[0], 
        struct.unpack('f', d[i+8:i+12])[0]
        ), i+12

def read_vec2(i, d):
    return (
        struct.unpack('f', d[i:i+4])[0], 
        struct.unpack('f', d[i+4:i+8])[0]
        ), i+8


# OpenSeeFace/Unity/OpenSee.cs -> public void readFromPacket
def osf_update_socket():
    while True:
        data, addr = udp_socket.recvfrom(1024*2)

        index = 0

        time, index = read_double(index, data)
        id, index = read_int32(index, data)
        cameraResolution, index = read_vec2(index, data)
        rightEyeOpen, index = read_float(index, data)
        leftEyeOpen, index = read_float(index, data)

        get_3DPoints = data[index]
        index += 1

        fit3DError, index = read_float(index, data)
        rawQuaternion, index = read_Quaternion(index, data)
        Quaternion = (-rawQuaternion[0], rawQuaternion[1], -rawQuaternion[2], rawQuaternion[3])

        rotation, index = read_vec3(index, data)

        rotation = (360 - (rotation[0] + 200), rotation[1], (rotation[2] - 90))
        
        x, index = read_float(index, data)
        y, index = read_float(index, data)
        z, index = read_float(index, data)
        translation = (-y, x, -z)

        confidence = list()
        for i in range(nPoints):
            o, index = read_float(index, data)
            confidence.append(o)

        points = list()
        for i in range(nPoints):
            o, index = read_vec2(index, data)
            points.append(o)

        points3D = list()
        for i in range(nPoints + 2):
            o, index = read_vec3(index, data)
            points3D.append(o)

        features = dict()
        features['EyeLeft'], index = read_float(index, data)
        features['EyeRight'], index = read_float(index, data)
        features['EyebrowSteepnessLeft'], index = read_float(index, data)
        features['EyebrowUpDownLeft'], index = read_float(index, data)
        features['EyebrowQuirkLeft'], index = read_float(index, data)
        features['EyebrowSteepnessRight'], index = read_float(index, data)
        features['EyebrowUpDownRight'], index = read_float(index, data)
        features['EyebrowQuirkRight'], index = read_float(index, data)
        features['MouthCornerUpDownLeft'], index = read_float(index, data)
        features['MouthCornerInOutLeft'], index = read_float(index, data)
        features['MouthCornerUpDownRight'], index = read_float(index, data)
        features['MouthCornerInOutRight'], index = read_float(index, data)
        features['MouthOpen'], index = read_float(index, data)
        features['MouthWide'], index = read_float(index, data)

    
        FaceTraceData['time'] = time
        FaceTraceData['id'] = id
        FaceTraceData['cameraResolution'] = cameraResolution
        FaceTraceData['rightEyeOpen'] = rightEyeOpen
        FaceTraceData['leftEyeOpen'] = leftEyeOpen
        FaceTraceData['get_3DPoints'] = get_3DPoints
        FaceTraceData['Quaternion'] = Quaternion
        FaceTraceData['rotation'] = rotation
        FaceTraceData['translation'] = translation
        FaceTraceData['confidence'] = confidence
        FaceTraceData['points'] = points
        FaceTraceData['points3D'] = points3D
        FaceTraceData['features'] = features


def osf_update_function(obj, st):
    # define at debug_ren
    show_osf_track_data()
    
    if bool(FaceTraceData) is False:
        return
    
    obj.blend_parameter(
        name="ParamEyeLOpen", 
        value=FaceTraceData["leftEyeOpen"], 
        weight=3.0, 
        blend="Overwrite"
        )
    obj.blend_parameter(
        name="ParamEyeROpen", 
        value=FaceTraceData["rightEyeOpen"], 
        weight=3.0, 
        blend="Overwrite"
        )
    obj.blend_parameter(
        name="ParamAngleX", 
        value=FaceTraceData["rotation"][1], 
        weight=1.0, 
        blend="Overwrite"
        )
    obj.blend_parameter(
        name="ParamAngleY", 
        value=FaceTraceData["rotation"][0], 
        weight=1.0, 
        blend="Overwrite"
        )
    obj.blend_parameter(
        name="ParamAngleZ", 
        value=FaceTraceData["rotation"][2], 
        weight=1.0, 
        blend="Overwrite"
        )
    obj.blend_parameter(
        name="ParamE", 
        value=FaceTraceData["features"]['MouthWide'], 
        weight=1.0, 
        blend="Overwrite"
        )
    obj.blend_parameter(
        name="ParamO", 
        value=FaceTraceData["features"]['MouthOpen'], 
        weight=1.0, 
        blend="Overwrite"
        )
    obj.blend_parameter(
        name="ParamBrowLForm", 
        value=FaceTraceData["features"]['EyebrowUpDownLeft'], 
        weight=1.0, 
        blend="Overwrite"
        )
    obj.blend_parameter(
        name="ParamBrowRForm", 
        value=FaceTraceData["features"]['EyebrowUpDownRight'], 
        weight=1.0, 
        blend="Overwrite"
        )
    
    return 0.0


osf_thread = threading.Thread(target=osf_update_socket)
osf_thread.start()
"""renpy

init python:
"""

import socket
import struct
import threading

mouth_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mouth_udp_socket.bind(('127.0.0.1', 8000))

LastMouthData = (0, 0, 0, 0, 0)
GetMouthData = [0, 0, 0, 0, 0, 0]


def read_float(i, d):
    return struct.unpack('f', d[i:i+4])[0], i+4


def pymouth_update_socket():
    while True:
        data, addr = mouth_udp_socket.recvfrom(1024*2)
        
        index = 0

        Silence, index = read_float(index, data)
        A, index = read_float(index, data)
        I, index = read_float(index, data)
        U, index = read_float(index, data)
        E, index = read_float(index, data)
        O, index = read_float(index, data)
        GetMouthData[0] = Silence
        GetMouthData[1] = A
        GetMouthData[2] = I
        GetMouthData[3] = U
        GetMouthData[4] = E
        GetMouthData[5] = O


def pymouth_update_function(obj, st):
    silence, a, i, u, e, o = GetMouthData
    silence = 1.0 - silence
    
    # define at debug_ren.py
    show_mouth_track_data()

    weight = 0.5

    mouth = (
        (LastMouthData[0] * (1.0 - weight) + a * weight) * silence,
        (LastMouthData[1] * (1.0 - weight) + i * weight) * silence,
        (LastMouthData[2] * (1.0 - weight) + u * weight) * silence,
        (LastMouthData[3] * (1.0 - weight) + e * weight) * silence,
        (LastMouthData[4] * (1.0 - weight) + o * weight) * silence,
    )

    obj.blend_parameter(
        name="ParamA", 
        value=mouth[0], 
        weight=1.0, 
        blend="Overwrite"
        )
    obj.blend_parameter(
        name="ParamI", 
        value=mouth[1], 
        weight=1.0, 
        blend="Overwrite"
        )
    obj.blend_parameter(
        name="ParamU", 
        value=mouth[2], 
        weight=1.0, 
        blend="Overwrite"
        )
    obj.blend_parameter(
        name="ParamE", 
        value=mouth[3], 
        weight=1.0, 
        blend="Overwrite"
        )
    obj.blend_parameter(
        name="ParamO", 
        value=mouth[4], 
        weight=1.0, 
        blend="Overwrite"
        )
    obj.blend_parameter(
        name="ParamMouthUp", 
        value=0, 
        weight=1.0, 
        blend="Overwrite"
        )
    
    global LastMouthData
    LastMouthData = mouth
        
    return 0.0


mouth_thread = threading.Thread(target=pymouth_update_socket)
# mouth_thread.start()
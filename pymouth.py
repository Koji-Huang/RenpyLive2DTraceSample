import pymouth
import time
import socket
import struct

HOST = '127.0.0.1'
PORT = 8000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def callback(md: dict[str, float], data):
    data = bytes()
    for key, value in md.items():
        print(key, "%.4f" % value)
        data += struct.pack('f', value)
    s.sendto(data, (HOST, PORT))


with pymouth.VowelAnalyser() as a:
    a.action_noblock('test.flac', 44100, output_device=6, callback=callback, auto_play=True)  # no block
    print("end")
    time.sleep(1000000)

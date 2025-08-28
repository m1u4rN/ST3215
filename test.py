

import serial, json, time

ser = serial.Serial("/dev/ttyAMA0", 115200, timeout=1)

cmd = {"T":133,"X":0,"Y":0,"SPD":80,"ACC":50}
ser.write((json.dumps(cmd) + "\n").encode())

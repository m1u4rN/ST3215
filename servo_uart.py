from st3215 import ST3215

servo = ST3215('/dev/ttyAMA0')
ids = servo.ListServos()
if ids:
    servo.MoveTo(ids[0], 2048)

print(servo.PingServo(1))
print(ids)

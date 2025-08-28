import serial

ser = serial.Serial("/dev/ttyAMA0", 115200, timeout=1)


try:
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if line:
            print("<<", line)
except KeyboardInterrupt:
    print("\n=== Остановлено ===")


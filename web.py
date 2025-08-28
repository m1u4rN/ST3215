# web.py  — минимальный Flask backend для управления ST3215 по UART (JSON)
from flask import Flask, request, jsonify, render_template
import serial, json

# --- Настройки (поменять при необходимости) ---
SERIAL_PORT = "/dev/ttyAMA0"
BAUD = 115200
STEP = 10                       # градусы на один клик
CENTER = 90
MIN_ANGLE = 0
MAX_ANGLE = 180
# -----------------------------------------------

app = Flask(__name__, template_folder="templates")

# Открываем последовательный порт единожды при старте
ser = serial.Serial(SERIAL_PORT, BAUD, timeout=0.5)

# Простое локальное состояние — инициализация центра
state = {"x": CENTER, "y": CENTER}

def clamp(v):
    v = int(round(v))
    if v < MIN_ANGLE: return MIN_ANGLE
    if v > MAX_ANGLE: return MAX_ANGLE
    return v

def send_uart(cmd: dict):
    """Отправляет JSON-команду на плату (заканчивает \n)."""
    s = json.dumps(cmd) + "\n"
    ser.write(s.encode("utf-8"))
    # Обновляем локальное состояние, если это команда перемещения T:133
    if cmd.get("T") == 133:
        if "X" in cmd: state["x"] = clamp(cmd["X"])
        if "Y" in cmd: state["y"] = clamp(cmd["Y"])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/status")
def status():
    # Возвращаем локальное состояние (независимо от того, отдает ли плата реальные позиции)
    return jsonify({"x": state["x"], "y": state["y"]})

@app.route("/move_by", methods=["POST"])
def move_by():
    data = request.json or {}
    dx = int(data.get("dx", 0))
    dy = int(data.get("dy", 0))
    spd = int(data.get("spd", 80))
    acc = int(data.get("acc", 50))

    new_x = clamp(state["x"] + dx)
    new_y = clamp(state["y"] + dy)

    cmd = {"T":133, "X": new_x, "Y": new_y, "SPD": spd, "ACC": acc}
    send_uart(cmd)
    return jsonify({"status":"ok", "sent":cmd, "x": new_x, "y": new_y})

@app.route("/home", methods=["POST"])
def home():
    cmd = {"T":133, "X": CENTER, "Y": CENTER, "SPD": 80, "ACC": 50}
    send_uart(cmd)
    return jsonify({"status":"ok", "sent":cmd})

@app.route("/stop", methods=["POST"])
def stop():
    # Если устройство поддержует L/R stop (we saw T:1 L/R in web UI), используем её.
    cmd = {"T":1, "L":0.0, "R":0.0}
    send_uart(cmd)
    return jsonify({"status":"ok", "sent":cmd})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

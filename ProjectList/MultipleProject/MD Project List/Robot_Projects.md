# 🤖 Robot Projects — ESP32 MicroPython

> All projects use the `systemio` library with `setup()`, `main()`, and `cleanup()` functions.
> Code style follows the `from digital import *` / `from analog import *` pattern.

---

## Table of Contents

1. [Line Following Robot](#1-line-following-robot)
2. [Obstacle Avoidance Robot](#2-obstacle-avoidance-robot)
3. [Fire Alarm Robot](#3-fire-alarm-robot)
4. [Rain Detection Robot](#4-rain-detection-robot)
5. [Light Following Robot](#5-light-following-robot)
6. [Bluetooth Controlled Robot](#6-bluetooth-controlled-robot)
7. [Wi-Fi Controlled Robot](#7-wi-fi-controlled-robot)
8. [Voice Controlled Robot](#8-voice-controlled-robot)
9. [Maze Solving Robot](#9-maze-solving-robot)
10. [Robot Status Indicator System](#10-robot-status-indicator-system)

---

## 1. Line Following Robot

### 🎯 Objective
Build a robot that follows a black line on a white surface using IR sensors.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| IR Line Sensor Module | 2 (Left & Right) |
| DC Motors + Motor Driver (L298N) | 2 Motors |
| Chassis + Wheels | 1 Set |
| 9V Battery | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LEFT_SENSOR | 34 | IR Sensor (Left) |
| RIGHT_SENSOR | 35 | IR Sensor (Right) |
| LEFT_MOTOR_1 | 12 | Left Motor Forward |
| LEFT_MOTOR_2 | 13 | Left Motor Backward |
| RIGHT_MOTOR_1 | 2 | Right Motor Forward |
| RIGHT_MOTOR_2 | 4 | Right Motor Backward |

### 💡 Working Principle
- IR sensor reads **LOW (0)** on black line, **HIGH (1)** on white surface
- Both sensors on white → Move Forward
- Left on black, Right on white → Turn Left
- Right on black, Left on white → Turn Right
- Both on black → Stop

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

LEFT_SENSOR   = 34
RIGHT_SENSOR  = 35

LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4

def setup():
    pinMode(LEFT_SENSOR,   INPUT)
    pinMode(RIGHT_SENSOR,  INPUT)
    pinMode(LEFT_MOTOR_1,  OUTPUT)
    pinMode(LEFT_MOTOR_2,  OUTPUT)
    pinMode(RIGHT_MOTOR_1, OUTPUT)
    pinMode(RIGHT_MOTOR_2, OUTPUT)

def move_forward():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def turn_left():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  1)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def turn_right():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 1)

def stop_robot():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 0)

def main():
    setup()
    print("Line Following Robot Started")

    while True:
        left  = digitalRead(LEFT_SENSOR)
        right = digitalRead(RIGHT_SENSOR)

        if left == 1 and right == 1:
            print("Forward")
            move_forward()
        elif left == 0 and right == 1:
            print("Turn Left")
            turn_left()
        elif left == 1 and right == 0:
            print("Turn Right")
            turn_right()
        else:
            print("Stop")
            stop_robot()

        time.sleep(0.05)

def cleanup():
    stop_robot()
    print("Robot Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Line Following Robot Started
Forward
Turn Left
Forward
Turn Right
Forward
```

---

## 2. Obstacle Avoidance Robot

### 🎯 Objective
Build a robot that detects obstacles using an ultrasonic sensor and automatically avoids them.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| HC-SR04 Ultrasonic Sensor | 1 |
| DC Motors + Motor Driver (L298N) | 2 Motors |
| Chassis + Wheels | 1 Set |
| 9V Battery | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| TRIG_PIN | 5 | Ultrasonic Trigger |
| ECHO_PIN | 18 | Ultrasonic Echo |
| LEFT_MOTOR_1 | 12 | Left Motor Forward |
| LEFT_MOTOR_2 | 13 | Left Motor Backward |
| RIGHT_MOTOR_1 | 2 | Right Motor Forward |
| RIGHT_MOTOR_2 | 4 | Right Motor Backward |

### 💡 Working Principle
- Sends a 10µs pulse on TRIG pin
- Measures ECHO pulse duration to calculate distance
- If distance < 20 cm → Stop and Turn Right
- If distance ≥ 20 cm → Move Forward

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time
from machine import Pin

TRIG_PIN      = 5
ECHO_PIN      = 18
SAFE_DISTANCE = 20   # cm

LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

def setup():
    pinMode(LEFT_MOTOR_1,  OUTPUT)
    pinMode(LEFT_MOTOR_2,  OUTPUT)
    pinMode(RIGHT_MOTOR_1, OUTPUT)
    pinMode(RIGHT_MOTOR_2, OUTPUT)

def get_distance():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    while echo.value() == 0:
        pass
    start = time.ticks_us()

    while echo.value() == 1:
        pass
    end = time.ticks_us()

    duration = time.ticks_diff(end, start)
    distance = (duration / 2) / 29.1
    return distance

def move_forward():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def turn_right():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 1)

def stop_robot():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 0)

def main():
    setup()
    print("Obstacle Avoidance Robot Started")

    while True:
        dist = get_distance()
        print(f"Distance: {dist:.1f} cm")

        if dist < SAFE_DISTANCE:
            print("Obstacle! Avoiding...")
            stop_robot()
            time.sleep(0.3)
            turn_right()
            time.sleep(0.5)
        else:
            move_forward()

        time.sleep(0.1)

def cleanup():
    stop_robot()
    print("Robot Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Obstacle Avoidance Robot Started
Distance: 45.2 cm
Distance: 18.3 cm
Obstacle! Avoiding...
Distance: 52.1 cm
```

---

## 3. Fire Alarm Robot

### 🎯 Objective
Build a robot that detects fire using a flame sensor, stops, and triggers a buzzer alarm.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Flame Sensor (Analog) | 1 |
| Buzzer | 1 |
| DC Motors + Motor Driver | 2 Motors |
| 9V Battery | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| FLAME_PIN | 34 | Flame Sensor (Analog) |
| LEFT_MOTOR_1 | 12 | Left Motor Forward |
| LEFT_MOTOR_2 | 13 | Left Motor Backward |
| RIGHT_MOTOR_1 | 2 | Right Motor Forward |
| RIGHT_MOTOR_2 | 4 | Right Motor Backward |
| BUZZER_PIN | 14 | Buzzer |

### 💡 Working Principle
- Flame sensor gives lower analog value when flame is detected
- `analogPercent()` converts raw ADC to percentage
- `100 - percent` = fire intensity (higher = more fire)
- If fire level > 30% → Stop robot + Sound buzzer
- If safe → Move forward + Buzzer off

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

FLAME_PIN  = 34
FIRE_LIMIT = 30

LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4

BUZZER_PIN = 14

def setup():
    analogPin(FLAME_PIN)
    pinMode(LEFT_MOTOR_1,  OUTPUT)
    pinMode(LEFT_MOTOR_2,  OUTPUT)
    pinMode(RIGHT_MOTOR_1, OUTPUT)
    pinMode(RIGHT_MOTOR_2, OUTPUT)
    pinMode(BUZZER_PIN,    OUTPUT)

def move_forward():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def stop_robot():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 0)

def buzzer_on():
    digitalWrite(BUZZER_PIN, 1)

def buzzer_off():
    digitalWrite(BUZZER_PIN, 0)

def main():
    setup()
    print("Fire Alarm Robot Started")

    while True:
        fire_level = 100 - analogPercent(FLAME_PIN)
        print(f"Fire Level: {fire_level} %")

        if fire_level > FIRE_LIMIT:
            print("🔥 FIRE DETECTED!")
            stop_robot()
            buzzer_on()
        else:
            print("✅ Area Safe")
            buzzer_off()
            move_forward()

        time.sleep(0.2)

def cleanup():
    stop_robot()
    buzzer_off()

run(main, cleanup)
```

### 📝 Expected Output
```
Fire Alarm Robot Started
Fire Level: 12 %
✅ Area Safe
Fire Level: 65 %
🔥 FIRE DETECTED!
```

---

## 4. Rain Detection Robot

### 🎯 Objective
Build a system that detects rain using a rain sensor and alerts with a buzzer siren.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Rain Sensor (Analog) | 1 |
| Buzzer | 1 |
| LED (optional indicator) | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| RAIN_PIN | 34 | Rain Sensor (Analog) |
| BUZZER_PIN | 14 | Buzzer |

### 💡 Working Principle
- Rain sensor resistance decreases when wet → higher ADC value
- `100 - analogPercent()` gives rain intensity
- If rain level > 30% → Sound siren (3 short beeps)
- If dry → Buzzer off

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

RAIN_PIN   = 34
BUZZER_PIN = 14
RAIN_LIMIT = 30

def setup():
    analogPin(RAIN_PIN)
    pinMode(BUZZER_PIN, OUTPUT)

def siren():
    for _ in range(3):
        digitalWrite(BUZZER_PIN, 1)
        time.sleep(0.1)
        digitalWrite(BUZZER_PIN, 0)
        time.sleep(0.1)

def main():
    setup()
    print("Rain Detection System Started")

    while True:
        rain = 100 - analogPercent(RAIN_PIN)

        if rain > RAIN_LIMIT:
            status = "RAIN DETECTED ☔"
            print(f"Rain Level: {rain:3d}%  Status: {status}")
            siren()
        else:
            status = "NO RAIN ☀"
            print(f"Rain Level: {rain:3d}%  Status: {status}")
            digitalWrite(BUZZER_PIN, 0)

        time.sleep(1)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)

run(main, cleanup)
```

### 📝 Expected Output
```
Rain Detection System Started
Rain Level:  10%  Status: NO RAIN ☀
Rain Level:  55%  Status: RAIN DETECTED ☔
Rain Level:  80%  Status: RAIN DETECTED ☔
```

---

## 5. Light Following Robot

### 🎯 Objective
Build a robot that follows a light source using two LDR sensors.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| LDR (Light Dependent Resistor) | 2 |
| 10kΩ Resistor | 2 |
| DC Motors + Motor Driver (L298N) | 2 Motors |
| Chassis + Wheels | 1 Set |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LEFT_LDR | 34 | Left LDR Sensor |
| RIGHT_LDR | 35 | Right LDR Sensor |
| LEFT_MOTOR_1 | 12 | Left Motor Forward |
| LEFT_MOTOR_2 | 13 | Left Motor Backward |
| RIGHT_MOTOR_1 | 2 | Right Motor Forward |
| RIGHT_MOTOR_2 | 4 | Right Motor Backward |

### 💡 Working Principle
- LDR gives lower ADC value in bright light, higher in darkness
- Compare left and right LDR values
- Robot turns toward the side with more light (lower ADC)
- If both equal → Move forward

### 🖥️ Code

```python
from analog import analogPin, analogRead
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LEFT_LDR      = 34
RIGHT_LDR     = 35
THRESHOLD     = 200   # Minimum difference to trigger turn

LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4

def setup():
    analogPin(LEFT_LDR)
    analogPin(RIGHT_LDR)
    pinMode(LEFT_MOTOR_1,  OUTPUT)
    pinMode(LEFT_MOTOR_2,  OUTPUT)
    pinMode(RIGHT_MOTOR_1, OUTPUT)
    pinMode(RIGHT_MOTOR_2, OUTPUT)

def move_forward():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def turn_left():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  1)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def turn_right():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 1)

def stop_robot():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 0)

def main():
    setup()
    print("Light Following Robot Started")

    while True:
        left_val  = analogRead(LEFT_LDR)
        right_val = analogRead(RIGHT_LDR)
        diff = left_val - right_val

        print(f"Left LDR: {left_val}  Right LDR: {right_val}  Diff: {diff}")

        if abs(diff) < THRESHOLD:
            print("Moving Forward")
            move_forward()
        elif diff < 0:
            # Left has less value = more light on left → turn left
            print("Turning Left (Light on Left)")
            turn_left()
        else:
            # Right has less value = more light on right → turn right
            print("Turning Right (Light on Right)")
            turn_right()

        time.sleep(0.1)

def cleanup():
    stop_robot()
    print("Robot Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Light Following Robot Started
Left LDR: 1200  Right LDR: 1250  Diff: -50
Moving Forward
Left LDR: 800   Right LDR: 1800  Diff: -1000
Turning Left (Light on Left)
```

---

## 6. Bluetooth Controlled Robot

### 🎯 Objective
Control a robot wirelessly via Bluetooth using a smartphone app (e.g., Serial Bluetooth Terminal).

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| DC Motors + Motor Driver (L298N) | 2 Motors |
| Chassis + Wheels | 1 Set |
| Smartphone with BT App | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LEFT_MOTOR_1 | 12 | Left Motor Forward |
| LEFT_MOTOR_2 | 13 | Left Motor Backward |
| RIGHT_MOTOR_1 | 2 | Right Motor Forward |
| RIGHT_MOTOR_2 | 4 | Right Motor Backward |

### 📱 Control Commands
| Command | Action |
|---|---|
| `F` | Move Forward |
| `B` | Move Backward |
| `L` | Turn Left |
| `R` | Turn Right |
| `S` | Stop |

### 💡 Working Principle
- ESP32 uses built-in Bluetooth Classic (UART)
- Smartphone app sends single character commands
- Robot reads the character and performs the corresponding movement

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import bluetooth
from machine import UART
import time

LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4

bt = UART(1, baudrate=9600, tx=17, rx=16)

def setup():
    pinMode(LEFT_MOTOR_1,  OUTPUT)
    pinMode(LEFT_MOTOR_2,  OUTPUT)
    pinMode(RIGHT_MOTOR_1, OUTPUT)
    pinMode(RIGHT_MOTOR_2, OUTPUT)

def move_forward():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def move_backward():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  1)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 1)

def turn_left():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  1)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def turn_right():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 1)

def stop_robot():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 0)

def main():
    setup()
    print("Bluetooth Robot Ready — Waiting for commands...")

    while True:
        if bt.any():
            cmd = bt.read(1).decode('utf-8').strip().upper()
            print(f"Command: {cmd}")

            if cmd == 'F':
                print("Moving Forward")
                move_forward()
            elif cmd == 'B':
                print("Moving Backward")
                move_backward()
            elif cmd == 'L':
                print("Turning Left")
                turn_left()
            elif cmd == 'R':
                print("Turning Right")
                turn_right()
            elif cmd == 'S':
                print("Stop")
                stop_robot()

        time.sleep(0.05)

def cleanup():
    stop_robot()
    print("Bluetooth Robot Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Bluetooth Robot Ready — Waiting for commands...
Command: F
Moving Forward
Command: L
Turning Left
Command: S
Stop
```

---

## 7. Wi-Fi Controlled Robot

### 🎯 Objective
Control a robot over Wi-Fi using a web browser interface hosted on the ESP32.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| DC Motors + Motor Driver (L298N) | 2 Motors |
| Chassis + Wheels | 1 Set |
| Wi-Fi Network | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LEFT_MOTOR_1 | 12 | Left Motor Forward |
| LEFT_MOTOR_2 | 13 | Left Motor Backward |
| RIGHT_MOTOR_1 | 2 | Right Motor Forward |
| RIGHT_MOTOR_2 | 4 | Right Motor Backward |

### 💡 Working Principle
- ESP32 connects to Wi-Fi and gets an IP address
- Opens a simple HTTP server on port 80
- Web page has Forward / Backward / Left / Right / Stop buttons
- Each button sends a URL like `/?cmd=F` to control the robot

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import network
import socket
import time

SSID     = "YourWiFiName"
PASSWORD = "YourPassword"

LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4

HTML = """<!DOCTYPE html>
<html>
<head><title>WiFi Robot</title></head>
<body style="text-align:center; font-family:Arial">
  <h2>WiFi Robot Control</h2>
  <a href="/?cmd=F"><button>Forward</button></a><br><br>
  <a href="/?cmd=L"><button>Left</button></a>
  <a href="/?cmd=S"><button>Stop</button></a>
  <a href="/?cmd=R"><button>Right</button></a><br><br>
  <a href="/?cmd=B"><button>Backward</button></a>
</body></html>"""

def setup():
    pinMode(LEFT_MOTOR_1,  OUTPUT)
    pinMode(LEFT_MOTOR_2,  OUTPUT)
    pinMode(RIGHT_MOTOR_1, OUTPUT)
    pinMode(RIGHT_MOTOR_2, OUTPUT)

def move_forward():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def move_backward():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  1)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 1)

def turn_left():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  1)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def turn_right():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 1)

def stop_robot():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 0)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to Wi-Fi", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\nConnected! IP:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

def main():
    setup()
    ip = connect_wifi()
    print(f"Open browser: http://{ip}")

    server = socket.socket()
    server.bind(('', 80))
    server.listen(5)

    while True:
        conn, addr = server.accept()
        request = conn.recv(1024).decode()

        if '?cmd=F' in request: move_forward();  print("Forward")
        elif '?cmd=B' in request: move_backward(); print("Backward")
        elif '?cmd=L' in request: turn_left();     print("Left")
        elif '?cmd=R' in request: turn_right();    print("Right")
        elif '?cmd=S' in request: stop_robot();    print("Stop")

        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + HTML)
        conn.close()

def cleanup():
    stop_robot()
    print("WiFi Robot Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Connecting to Wi-Fi....
Connected! IP: 192.168.1.105
Open browser: http://192.168.1.105
Forward
Left
Stop
```

---

## 8. Voice Controlled Robot

### 🎯 Objective
Control a robot using voice commands processed via a serial interface or a voice recognition module (e.g., DFRobot Voice Sensor or UART-based module).

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Voice Recognition Module (UART) | 1 |
| DC Motors + Motor Driver (L298N) | 2 Motors |
| Chassis + Wheels | 1 Set |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| VOICE_TX | 16 | Voice Module TX → ESP32 RX |
| VOICE_RX | 17 | Voice Module RX → ESP32 TX |
| LEFT_MOTOR_1 | 12 | Left Motor Forward |
| LEFT_MOTOR_2 | 13 | Left Motor Backward |
| RIGHT_MOTOR_1 | 2 | Right Motor Forward |
| RIGHT_MOTOR_2 | 4 | Right Motor Backward |

### 🎙️ Voice Commands
| Voice Command | Code | Action |
|---|---|---|
| "Go Forward" | `0x11` | Move Forward |
| "Go Back" | `0x12` | Move Backward |
| "Turn Left" | `0x13` | Turn Left |
| "Turn Right" | `0x14` | Turn Right |
| "Stop" | `0x15` | Stop |

### 💡 Working Principle
- Voice recognition module listens for pre-trained commands
- Sends UART byte code to ESP32 when command is detected
- ESP32 reads the byte and executes the corresponding movement

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import UART
import time

LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4

voice = UART(1, baudrate=9600, tx=17, rx=16)

VOICE_FORWARD  = 0x11
VOICE_BACKWARD = 0x12
VOICE_LEFT     = 0x13
VOICE_RIGHT    = 0x14
VOICE_STOP     = 0x15

def setup():
    pinMode(LEFT_MOTOR_1,  OUTPUT)
    pinMode(LEFT_MOTOR_2,  OUTPUT)
    pinMode(RIGHT_MOTOR_1, OUTPUT)
    pinMode(RIGHT_MOTOR_2, OUTPUT)

def move_forward():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def move_backward():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  1)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 1)

def turn_left():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  1)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def turn_right():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 1)

def stop_robot():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 0)

def main():
    setup()
    print("Voice Controlled Robot Ready")
    print("Say: Go Forward / Go Back / Turn Left / Turn Right / Stop")

    while True:
        if voice.any():
            data = voice.read(1)
            if data:
                cmd = data[0]
                print(f"Voice Code: {hex(cmd)}")

                if cmd == VOICE_FORWARD:
                    print("Moving Forward")
                    move_forward()
                elif cmd == VOICE_BACKWARD:
                    print("Moving Backward")
                    move_backward()
                elif cmd == VOICE_LEFT:
                    print("Turning Left")
                    turn_left()
                elif cmd == VOICE_RIGHT:
                    print("Turning Right")
                    turn_right()
                elif cmd == VOICE_STOP:
                    print("Stop")
                    stop_robot()

        time.sleep(0.05)

def cleanup():
    stop_robot()
    print("Voice Robot Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Voice Controlled Robot Ready
Say: Go Forward / Go Back / Turn Left / Turn Right / Stop
Voice Code: 0x11
Moving Forward
Voice Code: 0x13
Turning Left
Voice Code: 0x15
Stop
```

---

## 9. Maze Solving Robot

### 🎯 Objective
Build a robot that navigates through a maze using the Left-Hand Rule (always turn left if possible).

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| HC-SR04 Ultrasonic Sensor | 3 (Front, Left, Right) |
| DC Motors + Motor Driver (L298N) | 2 Motors |
| Chassis + Wheels | 1 Set |

### 📌 Pin Configuration
| Sensor | TRIG | ECHO | Direction |
|---|---|---|---|
| Front | 5 | 18 | Forward |
| Left | 19 | 21 | Left Wall |
| Right | 22 | 23 | Right Wall |

| Motor Pin | GPIO |
|---|---|
| LEFT_MOTOR_1 | 12 |
| LEFT_MOTOR_2 | 13 |
| RIGHT_MOTOR_1 | 2 |
| RIGHT_MOTOR_2 | 4 |

### 💡 Left-Hand Rule Algorithm
1. If left is open → Turn Left → Move Forward
2. Else if front is open → Move Forward
3. Else if right is open → Turn Right → Move Forward
4. Else → Turn Back (dead end)

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import Pin
import time

# Ultrasonic Pins
F_TRIG, F_ECHO = 5,  18   # Front
L_TRIG, L_ECHO = 19, 21   # Left
R_TRIG, R_ECHO = 22, 23   # Right

SAFE_DIST = 15   # cm

LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4

def setup():
    pinMode(LEFT_MOTOR_1,  OUTPUT)
    pinMode(LEFT_MOTOR_2,  OUTPUT)
    pinMode(RIGHT_MOTOR_1, OUTPUT)
    pinMode(RIGHT_MOTOR_2, OUTPUT)

def get_distance(trig_pin, echo_pin):
    trig = Pin(trig_pin, Pin.OUT)
    echo = Pin(echo_pin, Pin.IN)
    trig.value(0); time.sleep_us(2)
    trig.value(1); time.sleep_us(10)
    trig.value(0)
    while echo.value() == 0: pass
    t1 = time.ticks_us()
    while echo.value() == 1: pass
    t2 = time.ticks_us()
    return (time.ticks_diff(t2, t1) / 2) / 29.1

def move_forward():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def turn_left_90():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  1)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)
    time.sleep(0.5)

def turn_right_90():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 1)
    time.sleep(0.5)

def turn_back():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 1)
    time.sleep(1.0)

def stop_robot():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 0)

def main():
    setup()
    print("Maze Solving Robot Started — Left Hand Rule")

    while True:
        front = get_distance(F_TRIG, F_ECHO)
        left  = get_distance(L_TRIG, L_ECHO)
        right = get_distance(R_TRIG, R_ECHO)

        print(f"F:{front:.1f}  L:{left:.1f}  R:{right:.1f}")

        if left > SAFE_DIST:
            print("Turn Left")
            turn_left_90()
            move_forward()
        elif front > SAFE_DIST:
            print("Move Forward")
            move_forward()
        elif right > SAFE_DIST:
            print("Turn Right")
            turn_right_90()
            move_forward()
        else:
            print("Dead End — Turn Back")
            stop_robot()
            turn_back()

        time.sleep(0.3)

def cleanup():
    stop_robot()
    print("Maze Robot Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Maze Solving Robot Started — Left Hand Rule
F:45.2  L:12.5  R:38.1
Move Forward
F:15.1  L:42.0  R:18.3
Turn Left
F:38.5  L:14.2  R:40.1
Move Forward
```

---

## 10. Robot Status Indicator System

### 🎯 Objective
Use an LED to visually display the robot's current operating mode through different blink patterns.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| LED | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LED_PIN | 4 | Status LED |

### 💡 Blink Patterns
| Mode | Pattern | Description |
|---|---|---|
| MOVING | Fast blink × 5 | 0.2s ON / 0.2s OFF |
| IDLE | Slow blink × 3 | 0.8s ON / 0.8s OFF |
| WARNING | Rapid blink × 10 | 0.05s ON / 0.05s OFF |

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LED_PIN = 4

def setup():
    pinMode(LED_PIN, OUTPUT)

def blink_pattern(on_time, off_time):
    digitalWrite(LED_PIN, 1)
    time.sleep(on_time)
    digitalWrite(LED_PIN, 0)
    time.sleep(off_time)

def main():
    setup()
    print("Robot Status Indicator Started")

    while True:
        print("Mode: MOVING")
        for _ in range(5):
            blink_pattern(0.2, 0.2)

        print("Mode: IDLE")
        for _ in range(3):
            blink_pattern(0.8, 0.8)

        print("Mode: WARNING")
        for _ in range(10):
            blink_pattern(0.05, 0.05)

def cleanup():
    digitalWrite(LED_PIN, 0)
    print("Status LED OFF")

run(main, cleanup)
```

### 📝 Expected Output
```
Robot Status Indicator Started
Mode: MOVING
Mode: IDLE
Mode: WARNING
Mode: MOVING
...
```

---

## 📚 Quick Reference — Common Functions

### Motor Control
```python
def move_forward():   # Both motors forward
def move_backward():  # Both motors backward
def turn_left():      # Left backward, Right forward
def turn_right():     # Left forward, Right backward
def stop_robot():     # All motors off
```

### Sensor Reading
```python
analogRead(pin)           # Raw ADC value (0–4095)
analogPercent(pin)        # Percentage (0–100%)
digitalRead(pin)          # Digital value (0 or 1)
get_distance(trig, echo)  # Distance in cm (Ultrasonic)
```

### systemio Pattern
```python
from systemio import run

def setup():   pass   # Run once at start
def main():    pass   # Main loop
def cleanup(): pass   # Run on stop / Ctrl+C

run(main, cleanup)
```

---

*All projects designed for ESP32 with MicroPython using Thonny IDE.*
*Custom `systemio` library required — `from digital import *` / `from analog import *`*

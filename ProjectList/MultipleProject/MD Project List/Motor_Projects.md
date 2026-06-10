# ⚙️ Motor Projects — ESP32 MicroPython

> All projects use the `systemio` library with `setup()`, `main()`, and `cleanup()` functions.
> Code style follows the `from digital import *` / `from analog import *` pattern.

---

## Table of Contents

1. [Forward-Reverse Motor Control](#1-forward-reverse-motor-control)
2. [Robot Car Movement Control](#2-robot-car-movement-control)
3. [Automatic Gate System](#3-automatic-gate-system)
4. [Conveyor Belt Simulator](#4-conveyor-belt-simulator)
5. [Smart Fan Speed Controller](#5-smart-fan-speed-controller)
6. [Obstacle Avoidance Robot](#6-obstacle-avoidance-robot)
7. [Fire Fighting Robot](#7-fire-fighting-robot)
8. [Rain-Protected Window System](#8-rain-protected-window-system)
9. [Automatic Curtain System](#9-automatic-curtain-system)
10. [Motor Direction Indicator](#10-motor-direction-indicator)

---

## 1. Forward-Reverse Motor Control

### 🎯 Objective
Control a single DC motor to run forward, stop, and reverse using push buttons.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| DC Motor | 1 |
| L298N Motor Driver | 1 |
| Push Button | 3 |
| 10kΩ Pull-up Resistor | 3 |
| LED (Direction Indicator) | 2 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| MOTOR_1 | 12 | Motor Input 1 |
| MOTOR_2 | 13 | Motor Input 2 |
| BTN_FWD | 4 | Forward Button |
| BTN_REV | 5 | Reverse Button |
| BTN_STP | 18 | Stop Button |
| LED_FWD | 19 | Forward Indicator LED |
| LED_REV | 21 | Reverse Indicator LED |

### 💡 Working Principle
- MOTOR_1=1, MOTOR_2=0 → Motor spins Forward
- MOTOR_1=0, MOTOR_2=1 → Motor spins Reverse
- MOTOR_1=0, MOTOR_2=0 → Motor Stops
- LEDs indicate current direction

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

MOTOR_1 = 12
MOTOR_2 = 13
BTN_FWD = 4
BTN_REV = 5
BTN_STP = 18
LED_FWD = 19
LED_REV = 21

def setup():
    pinMode(MOTOR_1, OUTPUT)
    pinMode(MOTOR_2, OUTPUT)
    pinMode(BTN_FWD, INPUT)
    pinMode(BTN_REV, INPUT)
    pinMode(BTN_STP, INPUT)
    pinMode(LED_FWD, OUTPUT)
    pinMode(LED_REV, OUTPUT)

def motor_forward():
    digitalWrite(MOTOR_1, 1)
    digitalWrite(MOTOR_2, 0)
    digitalWrite(LED_FWD, 1)
    digitalWrite(LED_REV, 0)
    print("▶️  Motor: FORWARD")

def motor_reverse():
    digitalWrite(MOTOR_1, 0)
    digitalWrite(MOTOR_2, 1)
    digitalWrite(LED_FWD, 0)
    digitalWrite(LED_REV, 1)
    print("◀️  Motor: REVERSE")

def motor_stop():
    digitalWrite(MOTOR_1, 0)
    digitalWrite(MOTOR_2, 0)
    digitalWrite(LED_FWD, 0)
    digitalWrite(LED_REV, 0)
    print("⏹️  Motor: STOP")

def main():
    setup()
    motor_stop()
    print("Forward-Reverse Motor Control Ready")
    print("FWD button = Forward  |  REV button = Reverse  |  STP = Stop")

    last_fwd = 0
    last_rev = 0
    last_stp = 0

    while True:
        fwd = digitalRead(BTN_FWD)
        rev = digitalRead(BTN_REV)
        stp = digitalRead(BTN_STP)

        if last_fwd == 0 and fwd == 1:
            motor_forward()
        if last_rev == 0 and rev == 1:
            motor_reverse()
        if last_stp == 0 and stp == 1:
            motor_stop()

        last_fwd = fwd
        last_rev = rev
        last_stp = stp
        time.sleep(0.05)

def cleanup():
    motor_stop()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Forward-Reverse Motor Control Ready
FWD button = Forward  |  REV button = Reverse  |  STP = Stop
▶️  Motor: FORWARD
⏹️  Motor: STOP
◀️  Motor: REVERSE
⏹️  Motor: STOP
```

---

## 2. Robot Car Movement Control

### 🎯 Objective
Control a 4-direction robot car (Forward, Backward, Left, Right, Stop) using push buttons.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| DC Motors | 2 |
| L298N Motor Driver | 1 |
| Push Button | 5 |
| 10kΩ Pull-up Resistor | 5 |
| Robot Chassis + Wheels | 1 Set |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LEFT_MOTOR_1 | 12 | Left Motor Forward |
| LEFT_MOTOR_2 | 13 | Left Motor Backward |
| RIGHT_MOTOR_1 | 2 | Right Motor Forward |
| RIGHT_MOTOR_2 | 4 | Right Motor Backward |
| BTN_FWD | 5 | Forward Button |
| BTN_BCK | 18 | Backward Button |
| BTN_LFT | 19 | Left Button |
| BTN_RGT | 21 | Right Button |
| BTN_STP | 22 | Stop Button |

### 💡 Motor Truth Table
| Direction | LM1 | LM2 | RM1 | RM2 |
|---|---|---|---|---|
| Forward | 1 | 0 | 1 | 0 |
| Backward | 0 | 1 | 0 | 1 |
| Left | 0 | 1 | 1 | 0 |
| Right | 1 | 0 | 0 | 1 |
| Stop | 0 | 0 | 0 | 0 |

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4

BTN_FWD = 5
BTN_BCK = 18
BTN_LFT = 19
BTN_RGT = 21
BTN_STP = 22

BUTTONS = [BTN_FWD, BTN_BCK, BTN_LFT, BTN_RGT, BTN_STP]
MOTORS  = [LEFT_MOTOR_1, LEFT_MOTOR_2, RIGHT_MOTOR_1, RIGHT_MOTOR_2]

def setup():
    for pin in MOTORS:  pinMode(pin, OUTPUT)
    for pin in BUTTONS: pinMode(pin, INPUT)

def drive(lm1, lm2, rm1, rm2):
    digitalWrite(LEFT_MOTOR_1,  lm1)
    digitalWrite(LEFT_MOTOR_2,  lm2)
    digitalWrite(RIGHT_MOTOR_1, rm1)
    digitalWrite(RIGHT_MOTOR_2, rm2)

def move_forward():  drive(1, 0, 1, 0); print("⬆️  FORWARD")
def move_backward(): drive(0, 1, 0, 1); print("⬇️  BACKWARD")
def turn_left():     drive(0, 1, 1, 0); print("⬅️  LEFT")
def turn_right():    drive(1, 0, 0, 1); print("➡️  RIGHT")
def stop_robot():    drive(0, 0, 0, 0); print("⏹️  STOP")

def main():
    setup()
    stop_robot()
    print("Robot Car Movement Control Ready")

    last = [0] * 5

    while True:
        btns = [digitalRead(b) for b in BUTTONS]

        if last[0] == 0 and btns[0] == 1: move_forward()
        if last[1] == 0 and btns[1] == 1: move_backward()
        if last[2] == 0 and btns[2] == 1: turn_left()
        if last[3] == 0 and btns[3] == 1: turn_right()
        if last[4] == 0 and btns[4] == 1: stop_robot()

        last = btns
        time.sleep(0.05)

def cleanup():
    stop_robot()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Robot Car Movement Control Ready
⬆️  FORWARD
⬅️  LEFT
⬆️  FORWARD
➡️  RIGHT
⏹️  STOP
```

---

## 3. Automatic Gate System

### 🎯 Objective
Simulate an automatic gate that opens when an object is detected by an IR/ultrasonic sensor and closes after a delay.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| IR Sensor / Ultrasonic HC-SR04 | 1 |
| DC Motor (Gate Motor) | 1 |
| L298N Motor Driver | 1 |
| Green LED (Open) | 1 |
| Red LED (Closed) | 1 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SENSOR_PIN | 5 | IR Sensor Output |
| MOTOR_1 | 12 | Gate Motor Input 1 |
| MOTOR_2 | 13 | Gate Motor Input 2 |
| GREEN_LED | 4 | Gate Open LED |
| RED_LED | 18 | Gate Closed LED |

### 💡 Working Principle
- IR sensor detects vehicle / person → Gate opens (motor forward for 2s)
- Gate stays open for 4 seconds
- No detection → Gate closes (motor reverse for 2s)
- LEDs show current gate state

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

SENSOR_PIN = 5
MOTOR_1    = 12
MOTOR_2    = 13
GREEN_LED  = 4
RED_LED    = 18

OPEN_TIME  = 2.0    # Seconds to run motor to open
HOLD_TIME  = 4.0    # Seconds gate stays open
CLOSE_TIME = 2.0    # Seconds to run motor to close

def setup():
    pinMode(SENSOR_PIN, INPUT)
    pinMode(MOTOR_1,    OUTPUT)
    pinMode(MOTOR_2,    OUTPUT)
    pinMode(GREEN_LED,  OUTPUT)
    pinMode(RED_LED,    OUTPUT)

def gate_open():
    print("🔓 Gate OPENING...")
    digitalWrite(MOTOR_1, 1)
    digitalWrite(MOTOR_2, 0)
    time.sleep(OPEN_TIME)
    digitalWrite(MOTOR_1, 0)
    digitalWrite(MOTOR_2, 0)
    digitalWrite(GREEN_LED, 1)
    digitalWrite(RED_LED,   0)
    print("✅ Gate OPEN")

def gate_close():
    print("🔒 Gate CLOSING...")
    digitalWrite(GREEN_LED, 0)
    digitalWrite(MOTOR_1, 0)
    digitalWrite(MOTOR_2, 1)
    time.sleep(CLOSE_TIME)
    digitalWrite(MOTOR_1, 0)
    digitalWrite(MOTOR_2, 0)
    digitalWrite(RED_LED, 1)
    print("🔴 Gate CLOSED")

def main():
    setup()
    gate_closed = True
    digitalWrite(RED_LED, 1)

    print("Automatic Gate System Ready")

    while True:
        detected = digitalRead(SENSOR_PIN)

        if detected == 1 and gate_closed:
            print("🚗 Vehicle/Person Detected!")
            gate_open()
            gate_closed = False
            time.sleep(HOLD_TIME)
            gate_close()
            gate_closed = True

        time.sleep(0.1)

def cleanup():
    digitalWrite(MOTOR_1,   0)
    digitalWrite(MOTOR_2,   0)
    digitalWrite(GREEN_LED, 0)
    digitalWrite(RED_LED,   0)
    print("Gate System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Automatic Gate System Ready
🚗 Vehicle/Person Detected!
🔓 Gate OPENING...
✅ Gate OPEN
🔒 Gate CLOSING...
🔴 Gate CLOSED
```

---

## 4. Conveyor Belt Simulator

### 🎯 Objective
Simulate a conveyor belt system — start/stop belt with a button, detect items with a sensor, and count them.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| DC Motor (Belt Motor) | 1 |
| L298N Motor Driver | 1 |
| IR Sensor (Item Detector) | 1 |
| Push Button (Start/Stop) | 1 |
| 10kΩ Pull-up Resistor | 1 |
| Green LED (Running) | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| MOTOR_1 | 12 | Belt Motor Input 1 |
| MOTOR_2 | 13 | Belt Motor Input 2 |
| IR_PIN | 5 | IR Item Sensor |
| BTN_PIN | 18 | Start/Stop Button |
| LED_PIN | 4 | Belt Running LED |

### 💡 Working Principle
- Button toggles belt ON / OFF
- IR sensor counts each item that passes on the belt
- Item count and belt status printed to serial monitor
- Motor stops immediately when button is pressed again

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

MOTOR_1 = 12
MOTOR_2 = 13
IR_PIN  = 5
BTN_PIN = 18
LED_PIN = 4

def setup():
    pinMode(MOTOR_1, OUTPUT)
    pinMode(MOTOR_2, OUTPUT)
    pinMode(IR_PIN,  INPUT)
    pinMode(BTN_PIN, INPUT)
    pinMode(LED_PIN, OUTPUT)

def belt_start():
    digitalWrite(MOTOR_1, 1)
    digitalWrite(MOTOR_2, 0)
    digitalWrite(LED_PIN, 1)
    print("▶️  Belt STARTED")

def belt_stop():
    digitalWrite(MOTOR_1, 0)
    digitalWrite(MOTOR_2, 0)
    digitalWrite(LED_PIN, 0)
    print("⏹️  Belt STOPPED")

def main():
    setup()
    belt_stop()
    running    = False
    item_count = 0
    last_btn   = 0
    last_ir    = 0

    print("Conveyor Belt Simulator Ready")
    print("Press button to Start / Stop belt")

    while True:
        btn = digitalRead(BTN_PIN)
        ir  = digitalRead(IR_PIN)

        # Toggle belt
        if last_btn == 0 and btn == 1:
            running = not running
            if running: belt_start()
            else:       belt_stop()

        # Count items (only when belt running)
        if running and last_ir == 1 and ir == 0:
            item_count += 1
            print(f"📦 Item detected! Total count: {item_count}")

        last_btn = btn
        last_ir  = ir
        time.sleep(0.05)

def cleanup():
    belt_stop()
    print(f"Final item count: {item_count if 'item_count' in dir() else 0}")

run(main, cleanup)
```

### 📝 Expected Output
```
Conveyor Belt Simulator Ready
Press button to Start / Stop belt
▶️  Belt STARTED
📦 Item detected! Total count: 1
📦 Item detected! Total count: 2
📦 Item detected! Total count: 3
⏹️  Belt STOPPED
```

---

## 5. Smart Fan Speed Controller

### 🎯 Objective
Automatically adjust fan speed based on temperature using a DHT11 sensor and PWM motor control.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| DHT11 Temperature Sensor | 1 |
| DC Fan / Motor | 1 |
| L298N Motor Driver | 1 |
| 10kΩ Pull-up Resistor | 1 |
| LED Speed Indicators | 3 |
| 220Ω Resistor | 3 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| DHT_PIN | 14 | DHT11 Data |
| FAN_PWM | 4 | Fan PWM Speed Control |
| LED_LOW | 18 | Low Speed LED |
| LED_MED | 19 | Medium Speed LED |
| LED_HIGH | 21 | High Speed LED |

### 💡 Speed Zones
| Temperature | Fan Speed | PWM Duty | LED |
|---|---|---|---|
| < 25°C | OFF | 0 | All OFF |
| 25–30°C | LOW | 350 | LED_LOW |
| 30–35°C | MEDIUM | 650 | LED_MED |
| > 35°C | HIGH | 1023 | LED_HIGH |

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, pwmSetup, pwmWrite, pwmStop, OUTPUT
from systemio import run
from machine import Pin
import dht
import time

DHT_PIN  = 14
FAN_PWM  = 4
LED_LOW  = 18
LED_MED  = 19
LED_HIGH = 21

sensor = dht.DHT11(Pin(DHT_PIN))

def setup():
    pwmSetup(FAN_PWM, freq=1000)
    pinMode(LED_LOW,  OUTPUT)
    pinMode(LED_MED,  OUTPUT)
    pinMode(LED_HIGH, OUTPUT)

def all_leds_off():
    digitalWrite(LED_LOW,  0)
    digitalWrite(LED_MED,  0)
    digitalWrite(LED_HIGH, 0)

def set_fan(duty, label, led=None):
    pwmWrite(FAN_PWM, duty)
    all_leds_off()
    if led: digitalWrite(led, 1)
    print(f"Fan Speed: {label}  (PWM: {duty})")

def main():
    setup()
    print("Smart Fan Speed Controller Started")

    while True:
        try:
            sensor.measure()
            temp = sensor.temperature()
            print(f"Temperature: {temp:.1f}°C", end="  ")

            if temp < 25:
                set_fan(0,    "OFF ⚫")
            elif temp < 30:
                set_fan(350,  "LOW 🌀",    LED_LOW)
            elif temp < 35:
                set_fan(650,  "MEDIUM 💨", LED_MED)
            else:
                set_fan(1023, "HIGH 🌪️",  LED_HIGH)

        except OSError:
            print("❌ Sensor Error")

        time.sleep(2)

def cleanup():
    pwmStop(FAN_PWM)
    all_leds_off()
    print("Fan OFF — System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Smart Fan Speed Controller Started
Temperature: 22.0°C  Fan Speed: OFF ⚫  (PWM: 0)
Temperature: 27.5°C  Fan Speed: LOW 🌀  (PWM: 350)
Temperature: 32.0°C  Fan Speed: MEDIUM 💨  (PWM: 650)
Temperature: 38.0°C  Fan Speed: HIGH 🌪️  (PWM: 1023)
```

---

## 6. Obstacle Avoidance Robot

### 🎯 Objective
Build a robot that detects obstacles with an ultrasonic sensor and automatically steers around them.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| HC-SR04 Ultrasonic Sensor | 1 |
| DC Motors + L298N Driver | 2 Motors |
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

### 💡 Avoidance Logic
- Distance > 20 cm → Move Forward
- Distance 10–20 cm → Slow down / Caution
- Distance < 10 cm → Stop → Turn Right → Resume

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import Pin
import time

TRIG_PIN      = 5
ECHO_PIN      = 18
SAFE_DIST     = 20
CAUTION_DIST  = 10

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
    trig.value(0); time.sleep_us(2)
    trig.value(1); time.sleep_us(10)
    trig.value(0)
    while echo.value() == 0: pass
    t1 = time.ticks_us()
    while echo.value() == 1: pass
    t2 = time.ticks_us()
    return (time.ticks_diff(t2, t1) / 2) / 29.1

def drive(lm1, lm2, rm1, rm2):
    digitalWrite(LEFT_MOTOR_1,  lm1); digitalWrite(LEFT_MOTOR_2,  lm2)
    digitalWrite(RIGHT_MOTOR_1, rm1); digitalWrite(RIGHT_MOTOR_2, rm2)

def move_forward():  drive(1, 0, 1, 0)
def turn_right():    drive(1, 0, 0, 1)
def stop_robot():    drive(0, 0, 0, 0)

def main():
    setup()
    print("Obstacle Avoidance Robot Started")

    while True:
        dist = get_distance()
        print(f"Distance: {dist:5.1f} cm", end="  ")

        if dist < CAUTION_DIST:
            print("🛑 OBSTACLE! Avoiding...")
            stop_robot()
            time.sleep(0.3)
            turn_right()
            time.sleep(0.5)
        elif dist < SAFE_DIST:
            print("⚠️  Caution — Slowing")
            stop_robot()
            time.sleep(0.1)
        else:
            print("✅ Clear — Forward")
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
Distance:  65.2 cm  ✅ Clear — Forward
Distance:  18.4 cm  ⚠️  Caution — Slowing
Distance:   7.1 cm  🛑 OBSTACLE! Avoiding...
Distance:  48.5 cm  ✅ Clear — Forward
```

---

## 7. Fire Fighting Robot

### 🎯 Objective
Build a robot that navigates toward fire detected by a flame sensor and activates a pump/buzzer to suppress it.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Flame Sensor (Analog) | 1 |
| DC Motors + L298N Driver | 2 Motors |
| Mini Water Pump / Buzzer | 1 |
| Chassis + Wheels | 1 Set |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| FLAME_PIN | 34 | Flame Sensor Analog |
| LEFT_MOTOR_1 | 12 | Left Motor Forward |
| LEFT_MOTOR_2 | 13 | Left Motor Backward |
| RIGHT_MOTOR_1 | 2 | Right Motor Forward |
| RIGHT_MOTOR_2 | 4 | Right Motor Backward |
| PUMP_PIN | 14 | Water Pump / Buzzer |

### 💡 Fire Fighting Logic
- Fire level > 60% → Robot stops + Pump ON (suppress fire)
- Fire level 30–60% → Robot moves toward fire slowly
- Fire level < 30% → Robot patrols (moves forward normally)

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

FLAME_PIN     = 34
LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4
PUMP_PIN      = 14

SUPPRESS_LVL = 60
APPROACH_LVL = 30

def setup():
    analogPin(FLAME_PIN)
    for pin in [LEFT_MOTOR_1, LEFT_MOTOR_2,
                RIGHT_MOTOR_1, RIGHT_MOTOR_2, PUMP_PIN]:
        pinMode(pin, OUTPUT)

def drive(lm1, lm2, rm1, rm2):
    digitalWrite(LEFT_MOTOR_1,  lm1); digitalWrite(LEFT_MOTOR_2,  lm2)
    digitalWrite(RIGHT_MOTOR_1, rm1); digitalWrite(RIGHT_MOTOR_2, rm2)

def move_forward():  drive(1, 0, 1, 0)
def move_slow():     drive(1, 0, 1, 0)   # Same pins — reduce via PWM in advanced version
def stop_robot():    drive(0, 0, 0, 0)
def pump_on():       digitalWrite(PUMP_PIN, 1)
def pump_off():      digitalWrite(PUMP_PIN, 0)

def main():
    setup()
    print("Fire Fighting Robot Started")

    while True:
        fire = 100 - analogPercent(FLAME_PIN)
        print(f"Fire Level: {fire:3d}%", end="  ")

        if fire > SUPPRESS_LVL:
            print("🔥 FIRE! Suppressing...")
            stop_robot()
            pump_on()
        elif fire > APPROACH_LVL:
            print("🔶 Approaching fire...")
            pump_off()
            move_slow()
        else:
            print("✅ No fire — Patrolling")
            pump_off()
            move_forward()

        time.sleep(0.2)

def cleanup():
    stop_robot()
    pump_off()
    print("Robot Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Fire Fighting Robot Started
Fire Level:  12%  ✅ No fire — Patrolling
Fire Level:  42%  🔶 Approaching fire...
Fire Level:  75%  🔥 FIRE! Suppressing...
Fire Level:  18%  ✅ No fire — Patrolling
```

---

## 8. Rain-Protected Window System

### 🎯 Objective
Automatically close a window (motor reverses) when rain is detected and reopen it when rain stops.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Rain Sensor (Analog) | 1 |
| DC Motor (Window Motor) | 1 |
| L298N Motor Driver | 1 |
| Green LED (Open) | 1 |
| Blue LED (Closed) | 1 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| RAIN_PIN | 34 | Rain Sensor Analog |
| MOTOR_1 | 12 | Window Motor Input 1 |
| MOTOR_2 | 13 | Window Motor Input 2 |
| GREEN_LED | 4 | Window Open LED |
| BLUE_LED | 5 | Window Closed LED |

### 💡 Working Principle
- Rain detected (level > 35%) → Motor closes window (reverse 2s)
- Rain cleared (level < 20%) → Motor opens window (forward 2s)
- Hysteresis prevents constant motor switching at threshold boundary
- Motor only runs during transition — stops after reaching position

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

RAIN_PIN   = 34
MOTOR_1    = 12
MOTOR_2    = 13
GREEN_LED  = 4
BLUE_LED   = 5

RAIN_LIMIT  = 35    # Above = rain → close window
CLEAR_LIMIT = 20    # Below = clear → open window
MOVE_TIME   = 2.0   # Seconds to open/close

def setup():
    analogPin(RAIN_PIN)
    pinMode(MOTOR_1,   OUTPUT)
    pinMode(MOTOR_2,   OUTPUT)
    pinMode(GREEN_LED, OUTPUT)
    pinMode(BLUE_LED,  OUTPUT)

def motor_run(m1, m2, duration):
    digitalWrite(MOTOR_1, m1)
    digitalWrite(MOTOR_2, m2)
    time.sleep(duration)
    digitalWrite(MOTOR_1, 0)
    digitalWrite(MOTOR_2, 0)

def close_window():
    print("🌧️  Rain detected — Closing window...")
    motor_run(0, 1, MOVE_TIME)
    digitalWrite(GREEN_LED, 0)
    digitalWrite(BLUE_LED,  1)
    print("🔵 Window CLOSED")

def open_window():
    print("☀️  Rain cleared — Opening window...")
    motor_run(1, 0, MOVE_TIME)
    digitalWrite(BLUE_LED,  0)
    digitalWrite(GREEN_LED, 1)
    print("🟢 Window OPEN")

def main():
    setup()
    window_closed = False
    digitalWrite(GREEN_LED, 1)   # Start open

    print("Rain-Protected Window System Started")

    while True:
        rain = 100 - analogPercent(RAIN_PIN)
        print(f"Rain: {rain:3d}%", end="  ")

        if rain > RAIN_LIMIT and not window_closed:
            close_window()
            window_closed = True
        elif rain < CLEAR_LIMIT and window_closed:
            open_window()
            window_closed = False
        else:
            state = "CLOSED 🔵" if window_closed else "OPEN 🟢"
            print(f"Window {state} — no change")

        time.sleep(2)

def cleanup():
    digitalWrite(MOTOR_1,   0)
    digitalWrite(MOTOR_2,   0)
    digitalWrite(GREEN_LED, 0)
    digitalWrite(BLUE_LED,  0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Rain-Protected Window System Started
Rain:  10%  Window OPEN 🟢 — no change
Rain:  48%  🌧️  Rain detected — Closing window...
🔵 Window CLOSED
Rain:  55%  Window CLOSED 🔵 — no change
Rain:  12%  ☀️  Rain cleared — Opening window...
🟢 Window OPEN
```

---

## 9. Automatic Curtain System

### 🎯 Objective
Automatically open curtains (motor forward) when it is bright and close them (motor reverse) when dark, using an LDR.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| LDR Sensor | 1 |
| 10kΩ Pull-down Resistor | 1 |
| DC Motor (Curtain Motor) | 1 |
| L298N Motor Driver | 1 |
| Push Button (Manual Override) | 1 |
| Yellow LED (Open) | 1 |
| Blue LED (Closed) | 1 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LDR_PIN | 34 | LDR Analog Input |
| MOTOR_1 | 12 | Curtain Motor Input 1 |
| MOTOR_2 | 13 | Curtain Motor Input 2 |
| BTN_PIN | 5 | Manual Override Button |
| YELLOW_LED | 4 | Curtain Open LED |
| BLUE_LED | 18 | Curtain Closed LED |

### 💡 Operating Logic
| Condition | Action |
|---|---|
| Light > 60% (Bright) | Open curtains |
| Light < 30% (Dark) | Close curtains |
| Button press | Toggle manual override |
| Long press (2s) | Return to auto mode |

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

LDR_PIN    = 34
MOTOR_1    = 12
MOTOR_2    = 13
BTN_PIN    = 5
YELLOW_LED = 4
BLUE_LED   = 18

OPEN_LIMIT  = 60
CLOSE_LIMIT = 30
MOVE_TIME   = 2.0
LONG_PRESS  = 2.0

def setup():
    analogPin(LDR_PIN)
    pinMode(MOTOR_1,    OUTPUT)
    pinMode(MOTOR_2,    OUTPUT)
    pinMode(BTN_PIN,    INPUT)
    pinMode(YELLOW_LED, OUTPUT)
    pinMode(BLUE_LED,   OUTPUT)

def motor_run(m1, m2, duration):
    digitalWrite(MOTOR_1, m1)
    digitalWrite(MOTOR_2, m2)
    time.sleep(duration)
    digitalWrite(MOTOR_1, 0)
    digitalWrite(MOTOR_2, 0)

def open_curtain():
    print("🌅 Opening curtains...")
    motor_run(1, 0, MOVE_TIME)
    digitalWrite(YELLOW_LED, 1)
    digitalWrite(BLUE_LED,   0)
    print("🟡 Curtains OPEN")

def close_curtain():
    print("🌙 Closing curtains...")
    motor_run(0, 1, MOVE_TIME)
    digitalWrite(YELLOW_LED, 0)
    digitalWrite(BLUE_LED,   1)
    print("🔵 Curtains CLOSED")

def main():
    setup()
    curtain_open  = False
    manual_mode   = False
    last_btn      = 0
    press_start   = 0
    digitalWrite(BLUE_LED, 1)   # Start closed

    print("Automatic Curtain System Started")
    print("Short press = Manual toggle  |  Long press 2s = Auto mode")

    while True:
        light = analogPercent(LDR_PIN)
        btn   = digitalRead(BTN_PIN)

        # Button press start
        if last_btn == 0 and btn == 1:
            press_start = time.time()

        # Button release
        if last_btn == 1 and btn == 0:
            held = time.time() - press_start
            if held >= LONG_PRESS:
                manual_mode = False
                print("🔄 AUTO MODE Restored")
            else:
                manual_mode = True
                if curtain_open:
                    close_curtain()
                    curtain_open = False
                else:
                    open_curtain()
                    curtain_open = True

        last_btn = btn

        # Auto mode
        if not manual_mode:
            if light > OPEN_LIMIT and not curtain_open:
                open_curtain()
                curtain_open = True
            elif light < CLOSE_LIMIT and curtain_open:
                close_curtain()
                curtain_open = False
            else:
                mode  = "AUTO"
                state = "OPEN 🟡" if curtain_open else "CLOSED 🔵"
                print(f"Light: {light:3d}%  Mode: {mode}  Curtain: {state}")

        time.sleep(1)

def cleanup():
    digitalWrite(MOTOR_1,    0)
    digitalWrite(MOTOR_2,    0)
    digitalWrite(YELLOW_LED, 0)
    digitalWrite(BLUE_LED,   0)
    print("Curtain System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Automatic Curtain System Started
Short press = Manual toggle  |  Long press 2s = Auto mode
Light:  25%  Mode: AUTO  Curtain: CLOSED 🔵
Light:  72%  🌅 Opening curtains...
🟡 Curtains OPEN
Light:  68%  Mode: AUTO  Curtain: OPEN 🟡
Light:  18%  🌙 Closing curtains...
🔵 Curtains CLOSED
```

---

## 10. Motor Direction Indicator

### 🎯 Objective
Indicate the motor's running direction and speed using LEDs and serial output with real-time PWM control.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| DC Motor | 1 |
| L298N Motor Driver | 1 |
| Potentiometer | 1 |
| Green LED (Forward) | 1 |
| Red LED (Reverse) | 1 |
| Yellow LED (Stop) | 1 |
| 220Ω Resistor | 3 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| MOTOR_PWM | 12 | Motor Speed (PWM) |
| MOTOR_DIR | 13 | Motor Direction |
| POT_PIN | 34 | Potentiometer (Speed) |
| BTN_DIR | 5 | Direction Toggle Button |
| LED_FWD | 4 | Forward LED |
| LED_REV | 18 | Reverse LED |
| LED_STP | 19 | Stop LED |

### 💡 Working Principle
- Potentiometer controls motor speed via PWM (0 → 1023)
- Button toggles direction between Forward and Reverse
- When POT is at zero → Motor stops → Yellow LED ON
- Direction LEDs update in real time

### 🖥️ Code

```python
from analog import analogPin, analogRead, mapValue
from digital import pinMode, digitalWrite, digitalRead, pwmSetup, pwmWrite, pwmStop, INPUT, OUTPUT
from systemio import run
import time

MOTOR_PWM = 12
MOTOR_DIR = 13
POT_PIN   = 34
BTN_DIR   = 5
LED_FWD   = 4
LED_REV   = 18
LED_STP   = 19

DEAD_ZONE = 30    # PWM values below this = treated as stop

def setup():
    analogPin(POT_PIN)
    pwmSetup(MOTOR_PWM, freq=1000)
    pinMode(MOTOR_DIR, OUTPUT)
    pinMode(BTN_DIR,   INPUT)
    pinMode(LED_FWD,   OUTPUT)
    pinMode(LED_REV,   OUTPUT)
    pinMode(LED_STP,   OUTPUT)

def all_leds_off():
    digitalWrite(LED_FWD, 0)
    digitalWrite(LED_REV, 0)
    digitalWrite(LED_STP, 0)

def update_indicator(direction, speed):
    all_leds_off()
    if speed <= DEAD_ZONE:
        digitalWrite(LED_STP, 1)
    elif direction == 0:
        digitalWrite(LED_FWD, 1)
    else:
        digitalWrite(LED_REV, 1)

def main():
    setup()
    direction  = 0      # 0 = Forward, 1 = Reverse
    last_btn   = 0

    print("Motor Direction Indicator Ready")
    print("Potentiometer = Speed  |  Button = Toggle Direction")

    while True:
        btn = digitalRead(BTN_DIR)

        # Toggle direction on button press
        if last_btn == 0 and btn == 1:
            direction = 1 if direction == 0 else 0
            label = "FORWARD ▶️" if direction == 0 else "REVERSE ◀️"
            print(f"Direction: {label}")

        last_btn = btn

        # Read potentiometer
        raw   = analogRead(POT_PIN)
        speed = mapValue(raw, 0, 4095, 0, 1023)

        # Apply motor control
        if speed <= DEAD_ZONE:
            pwmWrite(MOTOR_PWM, 0)
            digitalWrite(MOTOR_DIR, 0)
            label = "STOP ⏹️"
        else:
            pwmWrite(MOTOR_PWM, speed)
            digitalWrite(MOTOR_DIR, direction)
            pct   = int((speed / 1023) * 100)
            label = f"{'FWD ▶️' if direction == 0 else 'REV ◀️'}  Speed: {pct}%"

        update_indicator(direction, speed)
        print(f"ADC: {raw:4d}  PWM: {speed:4d}  Status: {label}")
        time.sleep(0.1)

def cleanup():
    pwmStop(MOTOR_PWM)
    digitalWrite(MOTOR_DIR, 0)
    all_leds_off()
    print("Motor OFF — System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Motor Direction Indicator Ready
Potentiometer = Speed  |  Button = Toggle Direction
ADC:    0  PWM:    0  Status: STOP ⏹️
ADC: 1200  PWM:  300  Status: FWD ▶️  Speed: 29%
ADC: 3500  PWM:  875  Status: FWD ▶️  Speed: 85%
Direction: REVERSE ◀️
ADC: 3500  PWM:  875  Status: REV ◀️  Speed: 85%
```

---

## 📚 Quick Reference — Motor Control

### L298N Motor Truth Table
```python
# Single Motor
digitalWrite(MOTOR_1, 1); digitalWrite(MOTOR_2, 0)  # Forward
digitalWrite(MOTOR_1, 0); digitalWrite(MOTOR_2, 1)  # Reverse
digitalWrite(MOTOR_1, 0); digitalWrite(MOTOR_2, 0)  # Stop

# Dual Motor Robot
def drive(lm1, lm2, rm1, rm2):
    digitalWrite(LEFT_MOTOR_1,  lm1); digitalWrite(LEFT_MOTOR_2,  lm2)
    digitalWrite(RIGHT_MOTOR_1, rm1); digitalWrite(RIGHT_MOTOR_2, rm2)

drive(1, 0, 1, 0)   # Forward
drive(0, 1, 0, 1)   # Backward
drive(0, 1, 1, 0)   # Turn Left
drive(1, 0, 0, 1)   # Turn Right
drive(0, 0, 0, 0)   # Stop
```

### PWM Speed Control
```python
pwmSetup(FAN_PIN, freq=1000)    # Initialize PWM
pwmWrite(FAN_PIN, 512)          # 50% speed (0–1023)
pwmWrite(FAN_PIN, 1023)         # Full speed
pwmWrite(FAN_PIN, 0)            # Stop
pwmStop(FAN_PIN)                # Release PWM pin
```

### Timed Motor Movement
```python
def motor_run(m1, m2, duration):
    digitalWrite(MOTOR_1, m1)
    digitalWrite(MOTOR_2, m2)
    time.sleep(duration)         # Run for set time
    digitalWrite(MOTOR_1, 0)
    digitalWrite(MOTOR_2, 0)     # Stop after duration

motor_run(1, 0, 2.0)   # Forward for 2 seconds
motor_run(0, 1, 1.5)   # Reverse for 1.5 seconds
```

### Ultrasonic Distance
```python
def get_distance():
    trig.value(1); time.sleep_us(10); trig.value(0)
    while echo.value() == 0: pass
    t1 = time.ticks_us()
    while echo.value() == 1: pass
    t2 = time.ticks_us()
    return (time.ticks_diff(t2, t1) / 2) / 29.1   # cm
```

### systemio Pattern
```python
from systemio import run

def setup():   pass   # Runs once at start
def main():    pass   # Main loop
def cleanup(): pass   # Runs on stop / Ctrl+C

run(main, cleanup)
```

---

*All projects designed for ESP32 with MicroPython using Thonny IDE.*
*Custom `systemio` library required — `from digital import *` / `from analog import *`*

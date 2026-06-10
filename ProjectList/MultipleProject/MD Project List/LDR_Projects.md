# 💡 LDR Projects — ESP32 MicroPython

> All projects use the `systemio` library with `setup()`, `main()`, and `cleanup()` functions.
> Code style follows the `from digital import *` / `from analog import *` pattern.

---

## Table of Contents

1. [Automatic Street Light](#1-automatic-street-light)
2. [Light Intensity Meter](#2-light-intensity-meter)
3. [Smart Night Lamp](#3-smart-night-lamp)
4. [Sunlight Detection System](#4-sunlight-detection-system)
5. [Solar Tracker Indicator](#5-solar-tracker-indicator)
6. [Day/Night Detection System](#6-daynight-detection-system)
7. [LDR-Based Robot Headlight](#7-ldr-based-robot-headlight)
8. [Light Following Robot](#8-light-following-robot)
9. [Light Security Alarm](#9-light-security-alarm)
10. [Smart Garden Light](#10-smart-garden-light)

---

## 1. Automatic Street Light

### 🎯 Objective
Automatically turn ON a street light when it gets dark and turn it OFF when daylight returns, using an LDR sensor.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| LDR (Light Dependent Resistor) | 1 |
| 10kΩ Pull-down Resistor | 1 |
| LED (White / Yellow) | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LDR_PIN | 34 | LDR Analog Input |
| LED_PIN | 4 | Street Light LED |

### 💡 Working Principle
- LDR resistance increases in darkness → lower ADC value
- `analogPercent()` gives light intensity (higher = brighter)
- If light < 30% → It is dark → LED turns ON
- If light ≥ 30% → It is bright → LED turns OFF

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LDR_PIN    = 34
LED_PIN    = 4
DARK_LIMIT = 30    # Below 30% = dark

def setup():
    analogPin(LDR_PIN)
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    print("Automatic Street Light Started")

    while True:
        light = analogPercent(LDR_PIN)
        print(f"Light: {light:3d}%", end="  ")

        if light < DARK_LIMIT:
            print("🌙 DARK  — Light ON")
            digitalWrite(LED_PIN, 1)
        else:
            print("☀️  BRIGHT — Light OFF")
            digitalWrite(LED_PIN, 0)

        time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN, 0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Automatic Street Light Started
Light:  75%  ☀️  BRIGHT — Light OFF
Light:  22%  🌙 DARK  — Light ON
Light:  10%  🌙 DARK  — Light ON
```

---

## 2. Light Intensity Meter

### 🎯 Objective
Measure and display ambient light intensity as a percentage and a visual bar graph on the serial monitor.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| LDR | 1 |
| 10kΩ Pull-down Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LDR_PIN | 34 | LDR Analog Input |

### 💡 Working Principle
- Reads raw ADC value (0–4095) from LDR
- Converts to percentage using `analogPercent()`
- Draws a visual ASCII bar graph scaled to 20 characters
- Classifies intensity into: DARK / DIM / MODERATE / BRIGHT / VERY BRIGHT

### 🖥️ Code

```python
from analog import analogPin, analogPercent, analogRead
from systemio import run
import time

LDR_PIN = 34

def setup():
    analogPin(LDR_PIN)

def draw_bar(value):
    filled = int(value / 5)
    bar    = "█" * filled + "░" * (20 - filled)
    return f"[{bar}]"

def get_label(value):
    if value < 20:   return "DARK 🌑"
    elif value < 40: return "DIM 🌘"
    elif value < 60: return "MODERATE 🌤️"
    elif value < 80: return "BRIGHT ☀️"
    else:            return "VERY BRIGHT 🌞"

def main():
    setup()
    print("Light Intensity Meter Started")
    print("-" * 45)

    while True:
        raw   = analogRead(LDR_PIN)
        light = analogPercent(LDR_PIN)
        bar   = draw_bar(light)
        label = get_label(light)

        print(f"ADC: {raw:4d}  {bar} {light:3d}%  {label}")
        time.sleep(0.5)

def cleanup():
    print("Meter Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Light Intensity Meter Started
---------------------------------------------
ADC:  320  [████░░░░░░░░░░░░░░░░]  16%  DARK 🌑
ADC: 1640  [████████░░░░░░░░░░░░]  40%  DIM 🌘
ADC: 2870  [██████████████░░░░░░]  70%  BRIGHT ☀️
ADC: 3950  [████████████████████]  96%  VERY BRIGHT 🌞
```

---

## 3. Smart Night Lamp

### 🎯 Objective
Create a night lamp that automatically adjusts LED brightness based on ambient light level using PWM.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| LDR | 1 |
| 10kΩ Pull-down Resistor | 1 |
| LED | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LDR_PIN | 34 | LDR Analog Input |
| LED_PIN | 4 | PWM LED Output |

### 💡 Working Principle
- Brighter environment → Lower PWM duty → LED dims
- Darker environment → Higher PWM duty → LED brightens
- Lamp is OFF in full daylight and fully ON in complete darkness
- Uses `mapValue()` to invert and scale LDR reading to PWM range

### 🖥️ Code

```python
from analog import analogPin, analogRead, mapValue
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

LDR_PIN = 34
LED_PIN = 4

def setup():
    analogPin(LDR_PIN)
    pwmSetup(LED_PIN, freq=1000)

def main():
    setup()
    print("Smart Night Lamp Started")

    while True:
        raw        = analogRead(LDR_PIN)
        # Invert: dark (low ADC) → high brightness
        brightness = mapValue(raw, 0, 4095, 1023, 0)
        pwmWrite(LED_PIN, brightness)

        percent = int((brightness / 1023) * 100)
        print(f"Light ADC: {raw:4d}  →  Lamp Brightness: {percent:3d}%")
        time.sleep(0.1)

def cleanup():
    pwmStop(LED_PIN)
    print("Lamp OFF")

run(main, cleanup)
```

### 📝 Expected Output
```
Smart Night Lamp Started
Light ADC:  350  →  Lamp Brightness:  91%
Light ADC: 2100  →  Lamp Brightness:  48%
Light ADC: 3900  →  Lamp Brightness:   4%
```

---

## 4. Sunlight Detection System

### 🎯 Objective
Detect the presence of direct sunlight and trigger an indicator when strong sunlight is detected.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| LDR | 1 |
| 10kΩ Pull-down Resistor | 1 |
| Yellow LED | 1 |
| Buzzer | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LDR_PIN | 34 | LDR Analog Input |
| LED_PIN | 4 | Sunlight Indicator LED |
| BUZZER_PIN | 14 | Alert Buzzer |

### 💡 Sunlight Zones
| Light Level | Zone | Action |
|---|---|---|
| > 85% | Direct Sunlight | LED ON + Beep |
| 60–85% | Bright | LED ON |
| 30–60% | Moderate | LED OFF |
| < 30% | Dark/Cloudy | LED OFF |

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LDR_PIN    = 34
LED_PIN    = 4
BUZZER_PIN = 14

SUNLIGHT_LIMIT = 85
BRIGHT_LIMIT   = 60

def setup():
    analogPin(LDR_PIN)
    pinMode(LED_PIN,    OUTPUT)
    pinMode(BUZZER_PIN, OUTPUT)

def alert_beep():
    digitalWrite(BUZZER_PIN, 1)
    time.sleep(0.1)
    digitalWrite(BUZZER_PIN, 0)

def main():
    setup()
    print("Sunlight Detection System Started")

    while True:
        light = analogPercent(LDR_PIN)
        print(f"Light: {light:3d}%", end="  ")

        if light > SUNLIGHT_LIMIT:
            print("☀️  DIRECT SUNLIGHT!")
            digitalWrite(LED_PIN, 1)
            alert_beep()
        elif light > BRIGHT_LIMIT:
            print("🌤️  BRIGHT")
            digitalWrite(LED_PIN,    1)
            digitalWrite(BUZZER_PIN, 0)
        else:
            print("🌥️  MODERATE / DARK")
            digitalWrite(LED_PIN,    0)
            digitalWrite(BUZZER_PIN, 0)

        time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN,    0)
    digitalWrite(BUZZER_PIN, 0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Sunlight Detection System Started
Light:  25%  🌥️  MODERATE / DARK
Light:  68%  🌤️  BRIGHT
Light:  91%  ☀️  DIRECT SUNLIGHT!
```

---

## 5. Solar Tracker Indicator

### 🎯 Objective
Use two LDR sensors to detect the direction of maximum light and indicate which side to rotate a solar panel.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| LDR | 2 (Left & Right) |
| 10kΩ Pull-down Resistor | 2 |
| Green LED | 1 |
| Left Arrow LED (Yellow) | 1 |
| Right Arrow LED (Yellow) | 1 |
| 220Ω Resistor | 3 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LEFT_LDR | 34 | Left LDR Sensor |
| RIGHT_LDR | 35 | Right LDR Sensor |
| LEFT_LED | 4 | Turn Left Indicator |
| RIGHT_LED | 5 | Turn Right Indicator |
| CENTER_LED | 18 | Aligned / Centered LED |

### 💡 Tracking Logic
- Compare left and right LDR values
- If left is brighter → rotate panel LEFT (Left LED ON)
- If right is brighter → rotate panel RIGHT (Right LED ON)
- If both equal (within threshold) → panel is ALIGNED (Center LED ON)

### 🖥️ Code

```python
from analog import analogPin, analogRead
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LEFT_LDR   = 34
RIGHT_LDR  = 35
LEFT_LED   = 4
RIGHT_LED  = 5
CENTER_LED = 18

THRESHOLD  = 150    # Minimum difference to trigger rotation

def setup():
    analogPin(LEFT_LDR)
    analogPin(RIGHT_LDR)
    pinMode(LEFT_LED,   OUTPUT)
    pinMode(RIGHT_LED,  OUTPUT)
    pinMode(CENTER_LED, OUTPUT)

def all_leds_off():
    digitalWrite(LEFT_LED,   0)
    digitalWrite(RIGHT_LED,  0)
    digitalWrite(CENTER_LED, 0)

def main():
    setup()
    print("Solar Tracker Indicator Started")

    while True:
        left_val  = analogRead(LEFT_LDR)
        right_val = analogRead(RIGHT_LDR)
        diff      = left_val - right_val

        print(f"Left: {left_val:4d}  Right: {right_val:4d}  Diff: {diff:+5d}", end="  ")

        all_leds_off()

        if abs(diff) <= THRESHOLD:
            print("✅ ALIGNED — Optimal Position")
            digitalWrite(CENTER_LED, 1)
        elif diff > 0:
            print("⬅️  ROTATE LEFT — More light on Left")
            digitalWrite(LEFT_LED, 1)
        else:
            print("➡️  ROTATE RIGHT — More light on Right")
            digitalWrite(RIGHT_LED, 1)

        time.sleep(0.3)

def cleanup():
    all_leds_off()
    print("Tracker Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Solar Tracker Indicator Started
Left: 2800  Right: 2820  Diff:  -20  ✅ ALIGNED — Optimal Position
Left: 3200  Right: 1800  Diff: +1400  ⬅️  ROTATE LEFT — More light on Left
Left: 1500  Right: 3100  Diff: -1600  ➡️  ROTATE RIGHT — More light on Right
```

---

## 6. Day/Night Detection System

### 🎯 Objective
Detect whether it is day or night using an LDR and switch between day mode and night mode with status display.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| LDR | 1 |
| 10kΩ Pull-down Resistor | 1 |
| Yellow LED (Day) | 1 |
| Blue LED (Night) | 1 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LDR_PIN | 34 | LDR Analog Input |
| DAY_LED | 4 | Day Mode Indicator |
| NIGHT_LED | 5 | Night Mode Indicator |

### 💡 Working Principle
- Hysteresis prevents flickering at the threshold boundary
- DAY threshold: light > 50% → switch to DAY mode
- NIGHT threshold: light < 35% → switch to NIGHT mode
- Between 35–50%: stays in current mode (hysteresis zone)

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LDR_PIN   = 34
DAY_LED   = 4
NIGHT_LED = 5

DAY_THRESHOLD   = 50
NIGHT_THRESHOLD = 35

def setup():
    analogPin(LDR_PIN)
    pinMode(DAY_LED,   OUTPUT)
    pinMode(NIGHT_LED, OUTPUT)

def set_day_mode():
    digitalWrite(DAY_LED,   1)
    digitalWrite(NIGHT_LED, 0)
    print("☀️  DAY MODE")

def set_night_mode():
    digitalWrite(DAY_LED,   0)
    digitalWrite(NIGHT_LED, 1)
    print("🌙 NIGHT MODE")

def main():
    setup()
    light   = analogPercent(LDR_PIN)
    is_day  = light >= DAY_THRESHOLD
    if is_day: set_day_mode()
    else:      set_night_mode()

    print("Day/Night Detection System Started")

    while True:
        light = analogPercent(LDR_PIN)
        print(f"Light: {light:3d}%", end="  ")

        if is_day and light < NIGHT_THRESHOLD:
            is_day = False
            set_night_mode()
        elif not is_day and light > DAY_THRESHOLD:
            is_day = True
            set_day_mode()
        else:
            mode = "DAY" if is_day else "NIGHT"
            print(f"Mode: {mode} (no change)")

        time.sleep(1)

def cleanup():
    digitalWrite(DAY_LED,   0)
    digitalWrite(NIGHT_LED, 0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Day/Night Detection System Started
Light:  78%  Mode: DAY (no change)
Light:  42%  Mode: DAY (no change)
Light:  28%  🌙 NIGHT MODE
Light:  18%  Mode: NIGHT (no change)
Light:  55%  ☀️  DAY MODE
```

---

## 7. LDR-Based Robot Headlight

### 🎯 Objective
Automatically turn ON a robot's headlights when ambient light is low, simulating an auto headlight system.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| LDR | 1 |
| 10kΩ Pull-down Resistor | 1 |
| White LED (Headlight) | 2 |
| Red LED (Tail Light) | 2 |
| 220Ω Resistor | 4 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LDR_PIN | 34 | LDR Analog Input |
| HEAD_LEFT | 4 | Left Headlight LED |
| HEAD_RIGHT | 5 | Right Headlight LED |
| TAIL_LEFT | 18 | Left Tail Light LED |
| TAIL_RIGHT | 19 | Right Tail Light LED |

### 💡 Light Modes
| Ambient Light | Mode | Headlights | Tail Lights |
|---|---|---|---|
| > 60% | DAY MODE | OFF | OFF |
| 30–60% | DIM MODE | ON (dim) | ON |
| < 30% | NIGHT MODE | ON (full) | ON |

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, pwmSetup, pwmWrite, pwmStop, OUTPUT
from systemio import run
import time

LDR_PIN     = 34
HEAD_LEFT   = 4
HEAD_RIGHT  = 5
TAIL_LEFT   = 18
TAIL_RIGHT  = 19

DAY_LIMIT   = 60
DIM_LIMIT   = 30

def setup():
    analogPin(LDR_PIN)
    pwmSetup(HEAD_LEFT,  freq=1000)
    pwmSetup(HEAD_RIGHT, freq=1000)
    pinMode(TAIL_LEFT,  OUTPUT)
    pinMode(TAIL_RIGHT, OUTPUT)

def headlights(duty):
    pwmWrite(HEAD_LEFT,  duty)
    pwmWrite(HEAD_RIGHT, duty)

def tail_lights(state):
    digitalWrite(TAIL_LEFT,  state)
    digitalWrite(TAIL_RIGHT, state)

def main():
    setup()
    print("LDR Robot Headlight System Started")

    while True:
        light = analogPercent(LDR_PIN)
        print(f"Ambient Light: {light:3d}%", end="  ")

        if light > DAY_LIMIT:
            print("🌞 DAY MODE — Lights OFF")
            headlights(0)
            tail_lights(0)
        elif light > DIM_LIMIT:
            print("🌆 DIM MODE — Partial Lights")
            headlights(400)    # ~40% brightness
            tail_lights(1)
        else:
            print("🌙 NIGHT MODE — Full Lights")
            headlights(1023)   # 100% brightness
            tail_lights(1)

        time.sleep(1)

def cleanup():
    headlights(0)
    tail_lights(0)
    pwmStop(HEAD_LEFT)
    pwmStop(HEAD_RIGHT)
    print("Lights OFF")

run(main, cleanup)
```

### 📝 Expected Output
```
LDR Robot Headlight System Started
Ambient Light:  82%  🌞 DAY MODE — Lights OFF
Ambient Light:  45%  🌆 DIM MODE — Partial Lights
Ambient Light:  18%  🌙 NIGHT MODE — Full Lights
```

---

## 8. Light Following Robot

### 🎯 Objective
Build a robot that detects the direction of a light source using two LDRs and steers toward it.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| LDR | 2 (Left & Right) |
| 10kΩ Pull-down Resistor | 2 |
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

### 💡 Movement Logic
| Condition | Action |
|---|---|
| Both LDRs equal (within threshold) | Move Forward |
| Left LDR brighter (higher ADC) | Turn Left |
| Right LDR brighter (higher ADC) | Turn Right |
| Both very dark (< 500) | Stop |

### 🖥️ Code

```python
from analog import analogPin, analogRead
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LEFT_LDR      = 34
RIGHT_LDR     = 35
THRESHOLD     = 200
DARK_LIMIT    = 500

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
        diff      = left_val - right_val

        print(f"L: {left_val:4d}  R: {right_val:4d}", end="  ")

        if left_val < DARK_LIMIT and right_val < DARK_LIMIT:
            print("🌑 Too Dark — Stop")
            stop_robot()
        elif abs(diff) <= THRESHOLD:
            print("➡️  Forward")
            move_forward()
        elif diff > 0:
            print("⬅️  Turn Left")
            turn_left()
        else:
            print("➡️  Turn Right")
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
L: 2800  R: 2820  ➡️  Forward
L: 3200  R: 1500  ⬅️  Turn Left
L: 1600  R: 3100  ➡️  Turn Right
L:  300  R:  280  🌑 Too Dark — Stop
```

---

## 9. Light Security Alarm

### 🎯 Objective
Trigger a security alarm when someone blocks or interrupts a light beam detected by an LDR.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| LDR | 1 |
| 10kΩ Pull-down Resistor | 1 |
| Torch / LED light source | 1 |
| Buzzer | 1 |
| Red LED | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LDR_PIN | 34 | LDR Analog Input |
| BUZZER_PIN | 14 | Alarm Buzzer |
| LED_PIN | 4 | Alert LED |

### 💡 Working Principle
- A constant light beam (torch) shines on the LDR
- System calibrates base light level at startup
- If light drops suddenly below base by > 30% → beam broken → ALARM
- Used as a tripwire / perimeter security sensor

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LDR_PIN    = 34
BUZZER_PIN = 14
LED_PIN    = 4

DROP_LIMIT = 30    # % drop from baseline to trigger alarm

def setup():
    analogPin(LDR_PIN)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(LED_PIN,    OUTPUT)

def alarm_siren():
    for _ in range(10):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(LED_PIN,    1)
        time.sleep(0.05)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(LED_PIN,    0)
        time.sleep(0.05)

def calibrate():
    print("Calibrating... Keep beam steady for 3 seconds")
    total = 0
    for _ in range(10):
        total += analogPercent(LDR_PIN)
        time.sleep(0.3)
    baseline = total / 10
    print(f"Baseline Light Level: {baseline:.1f}%")
    return baseline

def main():
    setup()
    print("Light Security Alarm Started")
    baseline = calibrate()
    print("System Armed — Do NOT break the beam!")

    while True:
        light = analogPercent(LDR_PIN)
        drop  = baseline - light

        print(f"Light: {light:3.0f}%  Baseline: {baseline:.0f}%  Drop: {drop:+.0f}%", end="  ")

        if drop > DROP_LIMIT:
            print("🚨 BEAM BROKEN — INTRUDER!")
            alarm_siren()
        else:
            print("✅ Beam Intact")
            digitalWrite(BUZZER_PIN, 0)
            digitalWrite(LED_PIN,    0)

        time.sleep(0.2)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    print("Alarm Disarmed")

run(main, cleanup)
```

### 📝 Expected Output
```
Light Security Alarm Started
Calibrating... Keep beam steady for 3 seconds
Baseline Light Level: 82.0%
System Armed — Do NOT break the beam!
Light:  81%  Baseline: 82%  Drop: +1%  ✅ Beam Intact
Light:  44%  Baseline: 82%  Drop: +38%  🚨 BEAM BROKEN — INTRUDER!
Light:  80%  Baseline: 82%  Drop: +2%  ✅ Beam Intact
```

---

## 10. Smart Garden Light

### 🎯 Objective
Automatically manage garden lighting — turn lights ON at night and OFF at sunrise, with a manual override button.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| LDR | 1 |
| 10kΩ Pull-down Resistor | 1 |
| Push Button | 1 |
| 10kΩ Pull-up Resistor | 1 |
| White LED (Garden Light) | 1 |
| Green LED (Status) | 1 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| LDR_PIN | 34 | LDR Analog Input |
| BUTTON_PIN | 5 | Manual Override Button |
| LIGHT_PIN | 4 | Garden Light LED |
| STATUS_LED | 18 | Auto/Manual Status LED |

### 💡 Operating Modes
| Mode | Trigger | Light Behaviour |
|---|---|---|
| AUTO | Default | ON at dark, OFF at dawn |
| MANUAL ON | Button press (when auto OFF) | Force light ON |
| MANUAL OFF | Button press (when ON) | Force light OFF |
| Back to AUTO | Long press (2s) | Returns to auto mode |

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

LDR_PIN    = 34
BUTTON_PIN = 5
LIGHT_PIN  = 4
STATUS_LED = 18

DARK_LIMIT   = 35
PRESS_TIME   = 2.0    # Seconds for long press → return to auto

def setup():
    analogPin(LDR_PIN)
    pinMode(BUTTON_PIN, INPUT)
    pinMode(LIGHT_PIN,  OUTPUT)
    pinMode(STATUS_LED, OUTPUT)

def main():
    setup()
    manual_mode  = False
    light_on     = False
    press_start  = 0
    last_button  = 0

    print("Smart Garden Light Started")
    print("Short press = Toggle  |  Long press (2s) = Auto Mode")

    while True:
        light  = analogPercent(LDR_PIN)
        button = digitalRead(BUTTON_PIN)

        # Button press logic
        if button == 1 and last_button == 0:
            press_start = time.time()

        if button == 0 and last_button == 1:
            held = time.time() - press_start
            if held >= PRESS_TIME:
                manual_mode = False
                print("🔄 AUTO MODE Restored")
            else:
                manual_mode = True
                light_on    = not light_on
                state = "ON" if light_on else "OFF"
                print(f"🖐️  MANUAL — Light {state}")

        last_button = button

        # Auto mode control
        if not manual_mode:
            if light < DARK_LIMIT:
                light_on = True
            else:
                light_on = False

        # Apply light state
        digitalWrite(LIGHT_PIN,  1 if light_on  else 0)
        digitalWrite(STATUS_LED, 0 if manual_mode else 1)  # Green = AUTO

        mode = "MANUAL" if manual_mode else "AUTO"
        state = "ON" if light_on else "OFF"
        print(f"Light: {light:3d}%  Mode: {mode:6s}  Garden Light: {state}")

        time.sleep(0.5)

def cleanup():
    digitalWrite(LIGHT_PIN,  0)
    digitalWrite(STATUS_LED, 0)
    print("Garden Light OFF")

run(main, cleanup)
```

### 📝 Expected Output
```
Smart Garden Light Started
Short press = Toggle  |  Long press (2s) = Auto Mode
Light:  72%  Mode: AUTO    Garden Light: OFF
Light:  28%  Mode: AUTO    Garden Light: ON
🖐️  MANUAL — Light OFF
Light:  22%  Mode: MANUAL  Garden Light: OFF
🔄 AUTO MODE Restored
Light:  20%  Mode: AUTO    Garden Light: ON
```

---

## 📚 Quick Reference — LDR Functions

### Analog Reading
```python
analogPin(pin)              # Initialize analog pin
analogRead(pin)             # Raw ADC value (0–4095)
analogPercent(pin)          # Light as percentage (0–100%)
analogThreshold(pin, val)   # True if above threshold
mapValue(raw, 0, 4095, 0, 1023)  # Map to PWM range
```

### LDR Behaviour
```python
# LDR in BRIGHT light  → Low resistance → Higher ADC
# LDR in DARK          → High resistance → Lower ADC

light_percent = analogPercent(LDR_PIN)
# High % = Bright environment
# Low %  = Dark environment
```

### PWM Brightness Control
```python
pwmSetup(LED_PIN, freq=1000)   # Setup PWM on pin
pwmWrite(LED_PIN, duty)        # duty: 0 (off) to 1023 (full)
pwmStop(LED_PIN)               # Stop PWM

# Invert for night lamp (dark → bright)
brightness = mapValue(raw, 0, 4095, 1023, 0)
```

### Two-LDR Comparison (Tracking / Following)
```python
left_val  = analogRead(LEFT_LDR)
right_val = analogRead(RIGHT_LDR)
diff      = left_val - right_val

if abs(diff) <= THRESHOLD:  # Balanced — go straight
    ...
elif diff > 0:              # Left brighter — turn left
    ...
else:                       # Right brighter — turn right
    ...
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

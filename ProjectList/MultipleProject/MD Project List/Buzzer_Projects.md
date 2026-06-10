# 🔔 Buzzer Projects — ESP32 MicroPython

> All projects use the `systemio` library with `setup()`, `main()`, and `cleanup()` functions.
> Code style follows the `from digital import *` / `from analog import *` pattern.

---

## Table of Contents

1. [Fire Alarm Siren](#1-fire-alarm-siren)
2. [Rain Alert System](#2-rain-alert-system)
3. [Intruder Alarm](#3-intruder-alarm)
4. [Door Open Warning Alarm](#4-door-open-warning-alarm)
5. [Reverse Parking Buzzer](#5-reverse-parking-buzzer)
6. [Touch Sensor Bell](#6-touch-sensor-bell)
7. [Gas Leak Warning Siren](#7-gas-leak-warning-siren)
8. [Emergency SOS Buzzer](#8-emergency-sos-buzzer)
9. [Temperature Alert Alarm](#9-temperature-alert-alarm)
10. [Motion Detection Alert](#10-motion-detection-alert)

---

## 1. Fire Alarm Siren

### 🎯 Objective
Detect fire using a flame sensor and sound a rapid siren with a red LED alert.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Flame Sensor (Analog) | 1 |
| Buzzer | 1 |
| Red LED | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| FLAME_PIN | 34 | Flame Sensor (Analog) |
| BUZZER_PIN | 14 | Buzzer |
| LED_PIN | 4 | Red Alert LED |

### 💡 Working Principle
- Flame sensor output drops in the presence of fire/IR radiation
- `100 - analogPercent()` gives fire intensity (higher = more fire)
- If fire level > 30% → Fast siren pattern + RED LED flashing
- Three siren modes: ALERT → RAPID → EMERGENCY based on intensity

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

FLAME_PIN  = 34
BUZZER_PIN = 14
LED_PIN    = 4

FIRE_LIMIT = 30

def setup():
    analogPin(FLAME_PIN)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(LED_PIN,    OUTPUT)

def beep(on_time, off_time, count):
    for _ in range(count):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(LED_PIN,    1)
        time.sleep(on_time)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(LED_PIN,    0)
        time.sleep(off_time)

def siren_alert():
    beep(0.3, 0.1, 3)

def siren_rapid():
    beep(0.1, 0.1, 6)

def siren_emergency():
    beep(0.05, 0.05, 12)

def main():
    setup()
    print("Fire Alarm Siren Started")

    while True:
        fire_level = 100 - analogPercent(FLAME_PIN)
        print(f"Fire Level: {fire_level:3d}%", end="  ")

        if fire_level > 70:
            print("🔥 EMERGENCY!")
            siren_emergency()
        elif fire_level > 50:
            print("🔥 RAPID ALARM!")
            siren_rapid()
        elif fire_level > FIRE_LIMIT:
            print("🔥 FIRE DETECTED!")
            siren_alert()
        else:
            print("✅ Safe")
            digitalWrite(BUZZER_PIN, 0)
            digitalWrite(LED_PIN,    0)

        time.sleep(0.2)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Fire Alarm Siren Started
Fire Level:  10%  ✅ Safe
Fire Level:  45%  🔥 FIRE DETECTED!
Fire Level:  60%  🔥 RAPID ALARM!
Fire Level:  80%  🔥 EMERGENCY!
```

---

## 2. Rain Alert System

### 🎯 Objective
Detect rainfall using a rain sensor and sound a buzzer alert with level-based siren patterns.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Rain Sensor (Analog) | 1 |
| Buzzer | 1 |
| Blue LED | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| RAIN_PIN | 34 | Rain Sensor (Analog) |
| BUZZER_PIN | 14 | Buzzer |
| LED_PIN | 4 | Blue Rain Indicator LED |

### 💡 Buzzer Alert Patterns
| Rain Level | Pattern | Description |
|---|---|---|
| Light Rain (30–60%) | 2 short beeps | Slow rhythm |
| Heavy Rain (> 60%) | 5 rapid beeps | Fast rhythm |

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

RAIN_PIN   = 34
BUZZER_PIN = 14
LED_PIN    = 4

LIGHT_RAIN = 30
HEAVY_RAIN = 60

def setup():
    analogPin(RAIN_PIN)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(LED_PIN,    OUTPUT)

def beep(on_time, off_time, count):
    for _ in range(count):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(LED_PIN,    1)
        time.sleep(on_time)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(LED_PIN,    0)
        time.sleep(off_time)

def main():
    setup()
    print("Rain Alert System Started")

    while True:
        rain = 100 - analogPercent(RAIN_PIN)
        print(f"Rain Level: {rain:3d}%", end="  ")

        if rain > HEAVY_RAIN:
            print("🌧️  HEAVY RAIN!")
            beep(0.1, 0.1, 5)
        elif rain > LIGHT_RAIN:
            print("🌦️  LIGHT RAIN")
            beep(0.3, 0.3, 2)
        else:
            print("☀️  No Rain")
            digitalWrite(BUZZER_PIN, 0)
            digitalWrite(LED_PIN,    0)

        time.sleep(1)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Rain Alert System Started
Rain Level:   8%  ☀️  No Rain
Rain Level:  42%  🌦️  LIGHT RAIN
Rain Level:  78%  🌧️  HEAVY RAIN!
```

---

## 3. Intruder Alarm

### 🎯 Objective
Detect intruders using a PIR motion sensor and trigger a loud multi-pattern alarm with LED.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| PIR Motion Sensor (HC-SR501) | 1 |
| Buzzer | 1 |
| Red LED | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| PIR_PIN | 5 | PIR Sensor Output |
| BUZZER_PIN | 14 | Buzzer |
| LED_PIN | 4 | Alert LED |

### 💡 Alarm Behaviour
- Motion detected → Rising edge (0→1) triggers alarm
- Alarm plays 3 cycles of escalating siren
- After motion clears → System resets and re-arms
- Prints intruder count to serial monitor

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

PIR_PIN    = 5
BUZZER_PIN = 14
LED_PIN    = 4

def setup():
    pinMode(PIR_PIN,    INPUT)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(LED_PIN,    OUTPUT)

def beep(on_time, off_time, count):
    for _ in range(count):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(LED_PIN,    1)
        time.sleep(on_time)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(LED_PIN,    0)
        time.sleep(off_time)

def intruder_siren():
    for _ in range(3):
        beep(0.3, 0.1, 3)   # Slow burst
        beep(0.1, 0.1, 5)   # Fast burst
        beep(0.05, 0.05, 8) # Rapid burst

def main():
    setup()
    last_state     = 0
    intruder_count = 0

    print("Intruder Alarm Armed")
    print("Stabilizing PIR sensor...")
    time.sleep(2)
    print("System Ready — Monitoring...")

    while True:
        motion = digitalRead(PIR_PIN)

        if last_state == 0 and motion == 1:
            intruder_count += 1
            print(f"🚨 INTRUDER DETECTED! Count: {intruder_count}")
            intruder_siren()

        elif motion == 0 and last_state == 1:
            print("✅ Area Clear — System Re-Armed")
            digitalWrite(BUZZER_PIN, 0)
            digitalWrite(LED_PIN,    0)

        last_state = motion
        time.sleep(0.1)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    print("Alarm Disarmed")

run(main, cleanup)
```

### 📝 Expected Output
```
Intruder Alarm Armed
Stabilizing PIR sensor...
System Ready — Monitoring...
🚨 INTRUDER DETECTED! Count: 1
✅ Area Clear — System Re-Armed
🚨 INTRUDER DETECTED! Count: 2
```

---

## 4. Door Open Warning Alarm

### 🎯 Objective
Sound a buzzer warning when a door is left open using a magnetic reed switch or push button sensor.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Magnetic Reed Switch / Push Button | 1 |
| Buzzer | 1 |
| Yellow LED | 1 |
| 10kΩ Pull-up Resistor | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| DOOR_PIN | 5 | Reed Switch / Button |
| BUZZER_PIN | 14 | Buzzer |
| LED_PIN | 4 | Door Open LED |

### 💡 Working Principle
- Reed switch: CLOSED (0) = Door shut, OPEN (1) = Door open
- If door open > 5 seconds → Buzzer starts beeping
- Beep interval shortens the longer the door stays open
- Door closed → Buzzer OFF immediately

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

DOOR_PIN   = 5
BUZZER_PIN = 14
LED_PIN    = 4

WARN_DELAY = 5    # Seconds before warning starts

def setup():
    pinMode(DOOR_PIN,   INPUT)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(LED_PIN,    OUTPUT)

def beep(on_time, off_time, count):
    for _ in range(count):
        digitalWrite(BUZZER_PIN, 1)
        time.sleep(on_time)
        digitalWrite(BUZZER_PIN, 0)
        time.sleep(off_time)

def main():
    setup()
    door_open_time = 0
    print("Door Open Warning Alarm Started")

    while True:
        door = digitalRead(DOOR_PIN)

        if door == 1:
            door_open_time += 0.1
            digitalWrite(LED_PIN, 1)

            if door_open_time >= WARN_DELAY:
                elapsed = int(door_open_time)
                print(f"⚠️  Door Open for {elapsed}s — WARNING!")

                if elapsed >= 15:
                    beep(0.05, 0.05, 5)   # Urgent
                elif elapsed >= 10:
                    beep(0.15, 0.15, 3)   # Fast
                else:
                    beep(0.3, 0.3, 2)     # Slow

        else:
            if door_open_time > 0:
                print("✅ Door Closed")
            door_open_time = 0
            digitalWrite(LED_PIN,    0)
            digitalWrite(BUZZER_PIN, 0)

        time.sleep(0.1)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Door Open Warning Alarm Started
⚠️  Door Open for 5s — WARNING!
⚠️  Door Open for 10s — WARNING!
⚠️  Door Open for 15s — WARNING!
✅ Door Closed
```

---

## 5. Reverse Parking Buzzer

### 🎯 Objective
Simulate a car reverse parking assistant using an ultrasonic sensor — beep faster as obstacle gets closer.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| HC-SR04 Ultrasonic Sensor | 1 |
| Buzzer | 1 |
| Red LED | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| TRIG_PIN | 5 | Ultrasonic Trigger |
| ECHO_PIN | 18 | Ultrasonic Echo |
| BUZZER_PIN | 14 | Buzzer |
| LED_PIN | 4 | Proximity LED |

### 💡 Beep Zones
| Distance | Beep Pattern | Status |
|---|---|---|
| > 50 cm | Silent | Safe |
| 30–50 cm | 1 slow beep | Caution |
| 15–30 cm | 2 medium beeps | Warning |
| 5–15 cm | 4 fast beeps | Danger |
| < 5 cm | Continuous | STOP! |

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import Pin
import time

TRIG_PIN   = 5
ECHO_PIN   = 18
BUZZER_PIN = 14
LED_PIN    = 4

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

def setup():
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(LED_PIN,    OUTPUT)

def get_distance():
    trig.value(0); time.sleep_us(2)
    trig.value(1); time.sleep_us(10)
    trig.value(0)
    while echo.value() == 0: pass
    t1 = time.ticks_us()
    while echo.value() == 1: pass
    t2 = time.ticks_us()
    return (time.ticks_diff(t2, t1) / 2) / 29.1

def beep(on_time, off_time, count):
    for _ in range(count):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(LED_PIN,    1)
        time.sleep(on_time)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(LED_PIN,    0)
        time.sleep(off_time)

def main():
    setup()
    print("Reverse Parking Buzzer Started")

    while True:
        dist = get_distance()
        print(f"Distance: {dist:5.1f} cm", end="  ")

        if dist < 5:
            print("🛑 STOP!")
            digitalWrite(BUZZER_PIN, 1)
            digitalWrite(LED_PIN,    1)
            time.sleep(0.05)
        elif dist < 15:
            print("⚠️  DANGER")
            beep(0.05, 0.05, 4)
        elif dist < 30:
            print("⚠️  WARNING")
            beep(0.15, 0.15, 2)
        elif dist < 50:
            print("🟡 CAUTION")
            beep(0.3, 0.5, 1)
        else:
            print("✅ Safe")
            digitalWrite(BUZZER_PIN, 0)
            digitalWrite(LED_PIN,    0)

        time.sleep(0.1)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Reverse Parking Buzzer Started
Distance:  80.0 cm  ✅ Safe
Distance:  42.5 cm  🟡 CAUTION
Distance:  22.3 cm  ⚠️  WARNING
Distance:   8.1 cm  ⚠️  DANGER
Distance:   3.2 cm  🛑 STOP!
```

---

## 6. Touch Sensor Bell

### 🎯 Objective
Create a doorbell that rings when the touch sensor is pressed, with a pleasant double-beep pattern.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Touch Sensor Module | 1 |
| Buzzer | 1 |
| Green LED | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| TOUCH_PIN | 5 | Touch Sensor Output |
| BUZZER_PIN | 14 | Buzzer |
| LED_PIN | 4 | Ring Indicator LED |

### 💡 Working Principle
- Touch sensor outputs HIGH (1) when touched
- Edge detection prevents repeated triggers while held
- Double beep plays once per touch
- Ring count displayed on serial monitor

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

TOUCH_PIN  = 5
BUZZER_PIN = 14
LED_PIN    = 4

def setup():
    pinMode(TOUCH_PIN,  INPUT)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(LED_PIN,    OUTPUT)

def ring_bell():
    # Double beep — classic doorbell pattern
    digitalWrite(BUZZER_PIN, 1)
    digitalWrite(LED_PIN,    1)
    time.sleep(0.2)
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    time.sleep(0.1)
    digitalWrite(BUZZER_PIN, 1)
    digitalWrite(LED_PIN,    1)
    time.sleep(0.1)
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)

def main():
    setup()
    last_touch = 0
    ring_count = 0

    print("Touch Sensor Bell Ready")
    print("Touch the sensor to ring the bell...")

    while True:
        touch = digitalRead(TOUCH_PIN)

        if last_touch == 0 and touch == 1:
            ring_count += 1
            print(f"🔔 DING DONG!  (Ring #{ring_count})")
            ring_bell()

        last_touch = touch
        time.sleep(0.05)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    print("Bell Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Touch Sensor Bell Ready
Touch the sensor to ring the bell...
🔔 DING DONG!  (Ring #1)
🔔 DING DONG!  (Ring #2)
🔔 DING DONG!  (Ring #3)
```

---

## 7. Gas Leak Warning Siren

### 🎯 Objective
Detect gas leakage using an MQ-2 sensor and sound a graduated warning siren with LED alert.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| MQ-2 Gas Sensor (Analog) | 1 |
| Buzzer | 1 |
| Yellow LED | 1 |
| Red LED | 1 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| GAS_PIN | 34 | MQ-2 Sensor Analog Output |
| BUZZER_PIN | 14 | Buzzer |
| YELLOW_LED | 4 | Caution Indicator |
| RED_LED | 5 | Danger Indicator |

### 💡 Alert Levels
| Gas Level | Siren | LEDs | Status |
|---|---|---|---|
| < 20% | Silent | All OFF | Normal |
| 20–40% | 1 slow beep | Yellow ON | Caution |
| > 40% | Rapid siren | Red Flashing | DANGER |

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

GAS_PIN     = 34
BUZZER_PIN  = 14
YELLOW_LED  = 4
RED_LED     = 5

DANGER_LIMIT  = 40
CAUTION_LIMIT = 20

def setup():
    analogPin(GAS_PIN)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(YELLOW_LED, OUTPUT)
    pinMode(RED_LED,    OUTPUT)

def all_off():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(YELLOW_LED, 0)
    digitalWrite(RED_LED,    0)

def caution_beep():
    digitalWrite(YELLOW_LED, 1)
    digitalWrite(BUZZER_PIN, 1)
    time.sleep(0.4)
    digitalWrite(BUZZER_PIN, 0)
    time.sleep(0.6)

def danger_siren():
    for _ in range(8):
        digitalWrite(RED_LED,    1)
        digitalWrite(BUZZER_PIN, 1)
        time.sleep(0.05)
        digitalWrite(RED_LED,    0)
        digitalWrite(BUZZER_PIN, 0)
        time.sleep(0.05)

def main():
    setup()
    print("Gas Leak Warning Siren Started")
    print("MQ-2 Sensor warming up...")
    time.sleep(2)

    while True:
        gas_level = analogPercent(GAS_PIN)
        print(f"Gas Level: {gas_level:3d}%", end="  ")

        if gas_level > DANGER_LIMIT:
            print("⛽ DANGER! GAS LEAKAGE!")
            all_off()
            danger_siren()
        elif gas_level > CAUTION_LIMIT:
            print("⚠️  CAUTION — Gas Rising")
            digitalWrite(RED_LED, 0)
            caution_beep()
        else:
            print("✅ Air Normal")
            all_off()

        time.sleep(0.5)

def cleanup():
    all_off()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Gas Leak Warning Siren Started
MQ-2 Sensor warming up...
Gas Level:  12%  ✅ Air Normal
Gas Level:  28%  ⚠️  CAUTION — Gas Rising
Gas Level:  58%  ⛽ DANGER! GAS LEAKAGE!
```

---

## 8. Emergency SOS Buzzer

### 🎯 Objective
Trigger an internationally recognised SOS signal (··· — — — ···) using a push button for emergency situations.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Push Button | 1 |
| Buzzer | 1 |
| Red LED | 1 |
| 10kΩ Pull-up Resistor | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| BUTTON_PIN | 5 | Push Button |
| BUZZER_PIN | 14 | Buzzer |
| LED_PIN | 4 | SOS Indicator LED |

### 💡 Morse Code SOS Pattern
| Symbol | Sound | Duration |
|---|---|---|
| `.` (dot) | Short beep | 0.15s ON |
| `—` (dash) | Long beep | 0.45s ON |
| Gap between symbols | Silence | 0.15s |
| Gap between letters | Silence | 0.45s |

**SOS = · · · — — — · · ·**

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

BUTTON_PIN = 5
BUZZER_PIN = 14
LED_PIN    = 4

DOT_TIME  = 0.15
DASH_TIME = 0.45
GAP_TIME  = 0.15
LETTER_GAP = 0.45

def setup():
    pinMode(BUTTON_PIN, INPUT)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(LED_PIN,    OUTPUT)

def dot():
    digitalWrite(BUZZER_PIN, 1)
    digitalWrite(LED_PIN,    1)
    time.sleep(DOT_TIME)
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    time.sleep(GAP_TIME)

def dash():
    digitalWrite(BUZZER_PIN, 1)
    digitalWrite(LED_PIN,    1)
    time.sleep(DASH_TIME)
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    time.sleep(GAP_TIME)

def send_sos():
    print("🆘 SOS SIGNAL SENDING: · · · — — — · · ·")

    # S = · · ·
    dot(); dot(); dot()
    time.sleep(LETTER_GAP)

    # O = — — —
    dash(); dash(); dash()
    time.sleep(LETTER_GAP)

    # S = · · ·
    dot(); dot(); dot()
    time.sleep(LETTER_GAP * 2)   # Long pause between repeats

def main():
    setup()
    last_button = 0
    sos_count   = 0

    print("Emergency SOS Buzzer Ready")
    print("Press button to send SOS signal")

    while True:
        button = digitalRead(BUTTON_PIN)

        if last_button == 0 and button == 1:
            sos_count += 1
            print(f"SOS #{sos_count} activated!")
            send_sos()
            print("SOS signal sent. Press again to repeat.")

        last_button = button
        time.sleep(0.05)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    print("SOS System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Emergency SOS Buzzer Ready
Press button to send SOS signal
SOS #1 activated!
🆘 SOS SIGNAL SENDING: · · · — — — · · ·
SOS signal sent. Press again to repeat.
SOS #2 activated!
🆘 SOS SIGNAL SENDING: · · · — — — · · ·
```

---

## 9. Temperature Alert Alarm

### 🎯 Objective
Monitor temperature using a DHT11 sensor and trigger different buzzer alarms for HIGH and LOW temperature conditions.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| DHT11 Temperature Sensor | 1 |
| Buzzer | 1 |
| Red LED | 1 |
| Blue LED | 1 |
| 10kΩ Pull-up Resistor | 1 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| DHT_PIN | 14 | DHT11 Data Pin |
| BUZZER_PIN | 5 | Buzzer |
| RED_LED | 4 | High Temp LED |
| BLUE_LED | 18 | Low Temp LED |

### 💡 Alert Conditions
| Condition | Threshold | Buzzer Pattern | LED |
|---|---|---|---|
| NORMAL | 15°C – 35°C | Silent | All OFF |
| HIGH TEMP | > 35°C | 3 fast beeps | Red ON |
| LOW TEMP | < 15°C | 2 slow beeps | Blue ON |

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import Pin
import dht
import time

DHT_PIN    = 14
BUZZER_PIN = 5
RED_LED    = 4
BLUE_LED   = 18

TEMP_HIGH = 35
TEMP_LOW  = 15

sensor = dht.DHT11(Pin(DHT_PIN))

def setup():
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(RED_LED,    OUTPUT)
    pinMode(BLUE_LED,   OUTPUT)

def all_off():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(RED_LED,    0)
    digitalWrite(BLUE_LED,   0)

def high_temp_alarm():
    for _ in range(3):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(RED_LED,    1)
        time.sleep(0.1)
        digitalWrite(BUZZER_PIN, 0)
        time.sleep(0.1)

def low_temp_alarm():
    for _ in range(2):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(BLUE_LED,   1)
        time.sleep(0.4)
        digitalWrite(BUZZER_PIN, 0)
        time.sleep(0.4)

def main():
    setup()
    print("Temperature Alert Alarm Started")

    while True:
        try:
            sensor.measure()
            temp = sensor.temperature()
            hum  = sensor.humidity()

            print(f"Temp: {temp:.1f}°C  Humidity: {hum:.1f}%", end="  ")

            if temp > TEMP_HIGH:
                print("🌡️  HIGH TEMP ALERT!")
                all_off()
                high_temp_alarm()
                digitalWrite(RED_LED, 1)
            elif temp < TEMP_LOW:
                print("🧊 LOW TEMP ALERT!")
                all_off()
                low_temp_alarm()
                digitalWrite(BLUE_LED, 1)
            else:
                print("✅ Temperature Normal")
                all_off()

        except OSError:
            print("❌ Sensor Read Error")

        time.sleep(2)

def cleanup():
    all_off()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Temperature Alert Alarm Started
Temp: 28.0°C  Humidity: 55.0%  ✅ Temperature Normal
Temp: 37.5°C  Humidity: 48.0%  🌡️  HIGH TEMP ALERT!
Temp: 12.0°C  Humidity: 65.0%  🧊 LOW TEMP ALERT!
```

---

## 10. Motion Detection Alert

### 🎯 Objective
Detect motion using a PIR sensor and sound a buzzer alert with escalating alarm intensity.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| PIR Motion Sensor (HC-SR501) | 1 |
| Buzzer | 1 |
| Red LED | 1 |
| Green LED | 1 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| PIR_PIN | 5 | PIR Sensor Output |
| BUZZER_PIN | 14 | Buzzer |
| RED_LED | 4 | Motion Detected LED |
| GREEN_LED | 18 | Area Clear LED |

### 💡 Escalating Alert Logic
- 1st detection → Short alert (3 beeps)
- 2nd detection within 30s → Medium alert (6 beeps)
- 3rd+ detection → Full alarm (rapid continuous siren)
- 30s without motion → Alert level resets

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

PIR_PIN    = 5
BUZZER_PIN = 14
RED_LED    = 4
GREEN_LED  = 18

RESET_TIME = 30   # Seconds to reset alert level

def setup():
    pinMode(PIR_PIN,    INPUT)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(RED_LED,    OUTPUT)
    pinMode(GREEN_LED,  OUTPUT)

def beep(on_time, off_time, count):
    for _ in range(count):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(RED_LED,    1)
        time.sleep(on_time)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(RED_LED,    0)
        time.sleep(off_time)

def level_1_alert():
    print("Level 1 — Short Alert")
    beep(0.2, 0.2, 3)

def level_2_alert():
    print("Level 2 — Medium Alert")
    beep(0.15, 0.15, 6)

def level_3_alert():
    print("Level 3 — FULL ALARM!")
    beep(0.05, 0.05, 20)

def main():
    setup()
    last_state    = 0
    alert_level   = 0
    last_detected = 0
    detect_count  = 0

    print("Motion Detection Alert Ready")
    print("Stabilizing PIR...")
    time.sleep(2)
    print("System Armed")

    digitalWrite(GREEN_LED, 1)

    while True:
        motion = digitalRead(PIR_PIN)
        now    = time.time()

        # Reset alert level after inactivity
        if detect_count > 0 and (now - last_detected) > RESET_TIME:
            detect_count = 0
            alert_level  = 0
            print("🔄 Alert Level Reset")

        if last_state == 0 and motion == 1:
            detect_count  += 1
            last_detected  = now
            alert_level    = min(detect_count, 3)

            digitalWrite(GREEN_LED, 0)
            print(f"🚨 MOTION! Detection #{detect_count}")

            if alert_level == 1:
                level_1_alert()
            elif alert_level == 2:
                level_2_alert()
            else:
                level_3_alert()

        elif motion == 0 and last_state == 1:
            print("✅ Motion Cleared")
            digitalWrite(BUZZER_PIN, 0)
            digitalWrite(RED_LED,    0)
            digitalWrite(GREEN_LED,  1)

        last_state = motion
        time.sleep(0.1)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(RED_LED,    0)
    digitalWrite(GREEN_LED,  0)
    print("System Disarmed")

run(main, cleanup)
```

### 📝 Expected Output
```
Motion Detection Alert Ready
Stabilizing PIR...
System Armed
🚨 MOTION! Detection #1
Level 1 — Short Alert
✅ Motion Cleared
🚨 MOTION! Detection #2
Level 2 — Medium Alert
✅ Motion Cleared
🚨 MOTION! Detection #3
Level 3 — FULL ALARM!
🔄 Alert Level Reset
```

---

## 📚 Quick Reference — Buzzer Patterns

### Common Beep Functions
```python
# Generic reusable beep function
def beep(on_time, off_time, count):
    for _ in range(count):
        digitalWrite(BUZZER_PIN, 1)
        time.sleep(on_time)
        digitalWrite(BUZZER_PIN, 0)
        time.sleep(off_time)

# Usage examples
beep(0.05, 0.05, 10)   # Rapid siren
beep(0.1,  0.1,  5)    # Fast alert
beep(0.2,  0.2,  3)    # Medium beep
beep(0.4,  0.4,  2)    # Slow warning
beep(0.5,  0.0,  1)    # Single long tone
```

### Morse Code Timing
```python
DOT_TIME   = 0.15   # Short beep
DASH_TIME  = 0.45   # Long beep  (3× dot)
GAP_TIME   = 0.15   # Between symbols
LETTER_GAP = 0.45   # Between letters (3× gap)

# SOS = · · ·  — — —  · · ·
```

### Edge Detection Pattern
```python
# Trigger only ONCE per press (not continuously)
last_state = 0

while True:
    state = digitalRead(SENSOR_PIN)
    if last_state == 0 and state == 1:
        # Rising edge → do action once
        trigger_alarm()
    last_state = state
    time.sleep(0.05)
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

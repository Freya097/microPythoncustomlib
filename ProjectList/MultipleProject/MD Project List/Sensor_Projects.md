# 🔬 Sensor Projects — ESP32 MicroPython

> All projects use the `systemio` library with `setup()`, `main()`, and `cleanup()` functions.
> Code style follows the `from digital import *` / `from analog import *` pattern.

---

## Table of Contents

1. [Soil Moisture Monitoring System](#1-soil-moisture-monitoring-system)
2. [Smart Plant Watering Indicator](#2-smart-plant-watering-indicator)
3. [Rain Detection System](#3-rain-detection-system)
4. [Fire Detection Alarm](#4-fire-detection-alarm)
5. [Gas Leakage Alarm using MQ Sensor](#5-gas-leakage-alarm-using-mq-sensor)
6. [Temperature Monitoring System](#6-temperature-monitoring-system)
7. [Humidity Monitoring System](#7-humidity-monitoring-system)
8. [Motion Detection Alarm using PIR](#8-motion-detection-alarm-using-pir)
9. [Water Level Indicator](#9-water-level-indicator)
10. [Sound Level Detection System](#10-sound-level-detection-system)

---

## 1. Soil Moisture Monitoring System

### 🎯 Objective
Monitor soil moisture levels using an analog soil moisture sensor and display the status on the serial monitor.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Soil Moisture Sensor (Analog) | 1 |
| LED (optional indicator) | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SOIL_PIN | 34 | Soil Moisture Sensor (Analog) |
| LED_PIN | 4 | Status LED |

### 💡 Working Principle
- Soil moisture sensor resistance decreases when soil is wet → lower ADC value
- `100 - analogPercent()` converts to moisture percentage (higher = wetter)
- Moisture levels are classified as: DRY / MODERATE / WET
- LED turns ON when soil is DRY (needs watering)

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

SOIL_PIN   = 34
LED_PIN    = 4

DRY_LIMIT  = 30    # Below 30% = Dry
WET_LIMIT  = 70    # Above 70% = Wet

def setup():
    analogPin(SOIL_PIN)
    pinMode(LED_PIN, OUTPUT)

def get_status(moisture):
    if moisture < DRY_LIMIT:
        return "DRY 🌵"
    elif moisture < WET_LIMIT:
        return "MODERATE 🌱"
    else:
        return "WET 💧"

def main():
    setup()
    print("Soil Moisture Monitoring System Started")

    while True:
        moisture = 100 - analogPercent(SOIL_PIN)
        status   = get_status(moisture)

        print(f"Moisture: {moisture:3d}%  Status: {status}")

        if moisture < DRY_LIMIT:
            digitalWrite(LED_PIN, 1)   # LED ON → Dry soil
        else:
            digitalWrite(LED_PIN, 0)

        time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN, 0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Soil Moisture Monitoring System Started
Moisture:  18%  Status: DRY 🌵
Moisture:  45%  Status: MODERATE 🌱
Moisture:  82%  Status: WET 💧
```

---

## 2. Smart Plant Watering Indicator

### 🎯 Objective
Automatically indicate when a plant needs watering using a soil moisture sensor, LED, and buzzer alert.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Soil Moisture Sensor (Analog) | 1 |
| Green LED | 1 |
| Red LED | 1 |
| Buzzer | 1 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SOIL_PIN | 34 | Soil Moisture Sensor |
| GREEN_LED | 4 | Plant OK Indicator |
| RED_LED | 5 | Needs Water Indicator |
| BUZZER_PIN | 18 | Buzzer Alert |

### 💡 Working Principle
- GREEN LED ON → Soil moisture is adequate, plant is healthy
- RED LED ON + Buzzer beeps → Soil is dry, plant needs water
- Threshold is set at 40% moisture level

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

SOIL_PIN   = 34
GREEN_LED  = 4
RED_LED    = 5
BUZZER_PIN = 18

WATER_LIMIT = 40    # Below 40% = Needs watering

def setup():
    analogPin(SOIL_PIN)
    pinMode(GREEN_LED,  OUTPUT)
    pinMode(RED_LED,    OUTPUT)
    pinMode(BUZZER_PIN, OUTPUT)

def alert_beep():
    for _ in range(2):
        digitalWrite(BUZZER_PIN, 1)
        time.sleep(0.2)
        digitalWrite(BUZZER_PIN, 0)
        time.sleep(0.2)

def main():
    setup()
    print("Smart Plant Watering Indicator Started")

    while True:
        moisture = 100 - analogPercent(SOIL_PIN)
        print(f"Soil Moisture: {moisture:3d}%")

        if moisture < WATER_LIMIT:
            print("⚠️  NEEDS WATERING!")
            digitalWrite(GREEN_LED, 0)
            digitalWrite(RED_LED,   1)
            alert_beep()
        else:
            print("✅ Plant is Healthy")
            digitalWrite(RED_LED,   0)
            digitalWrite(GREEN_LED, 1)
            digitalWrite(BUZZER_PIN, 0)

        time.sleep(2)

def cleanup():
    digitalWrite(GREEN_LED,  0)
    digitalWrite(RED_LED,    0)
    digitalWrite(BUZZER_PIN, 0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Smart Plant Watering Indicator Started
Soil Moisture:  72%
✅ Plant is Healthy
Soil Moisture:  25%
⚠️  NEEDS WATERING!
```

---

## 3. Rain Detection System

### 🎯 Objective
Detect rain using a rain sensor and trigger a buzzer siren with level display on the serial monitor.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Rain Sensor (Analog) | 1 |
| Buzzer | 1 |
| LED (optional) | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| RAIN_PIN | 34 | Rain Sensor (Analog) |
| BUZZER_PIN | 14 | Buzzer |

### 💡 Working Principle
- Rain sensor resistance decreases when wet → higher ADC reading
- `100 - analogPercent()` gives rain intensity percentage
- If rain level > 30% → Sound siren (3 short beeps)
- If dry → Buzzer OFF, display "NO RAIN"

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
    print("System Stopped")

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

## 4. Fire Detection Alarm

### 🎯 Objective
Detect fire or flame using a flame sensor and trigger a buzzer alarm with LED indicator.

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
- Flame sensor output drops when flame IR radiation is detected
- `100 - analogPercent()` = fire intensity (higher = more fire)
- If fire level > 30% → RED LED ON + Buzzer alarm
- If safe → LED OFF + Buzzer OFF

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

def fire_alarm():
    for _ in range(5):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(LED_PIN,    1)
        time.sleep(0.1)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(LED_PIN,    0)
        time.sleep(0.1)

def main():
    setup()
    print("Fire Detection Alarm Started")

    while True:
        fire_level = 100 - analogPercent(FLAME_PIN)
        print(f"Fire Level: {fire_level:3d}%")

        if fire_level > FIRE_LIMIT:
            print("🔥 FIRE DETECTED! EVACUATE!")
            fire_alarm()
        else:
            print("✅ No Fire — Area Safe")
            digitalWrite(BUZZER_PIN, 0)
            digitalWrite(LED_PIN,    0)

        time.sleep(0.5)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Fire Detection Alarm Started
Fire Level:  12%
✅ No Fire — Area Safe
Fire Level:  68%
🔥 FIRE DETECTED! EVACUATE!
```

---

## 5. Gas Leakage Alarm using MQ Sensor

### 🎯 Objective
Detect hazardous gas leakage (LPG / Smoke / CO) using an MQ-2 sensor and trigger an alarm.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| MQ-2 Gas Sensor (Analog) | 1 |
| Buzzer | 1 |
| Red LED | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| GAS_PIN | 34 | MQ-2 Sensor Analog Output |
| BUZZER_PIN | 14 | Buzzer |
| LED_PIN | 4 | Warning LED |

### 💡 Working Principle
- MQ-2 sensor resistance decreases when gas concentration increases → higher ADC value
- `analogPercent()` gives gas concentration as a percentage
- If gas level > 40% → Sound alarm + LED ON (DANGER)
- If gas level 20–40% → Warning message (CAUTION)
- If gas level < 20% → Normal / Safe

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

GAS_PIN    = 34
BUZZER_PIN = 14
LED_PIN    = 4

DANGER_LIMIT  = 40
CAUTION_LIMIT = 20

def setup():
    analogPin(GAS_PIN)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(LED_PIN,    OUTPUT)

def danger_alarm():
    for _ in range(6):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(LED_PIN,    1)
        time.sleep(0.05)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(LED_PIN,    0)
        time.sleep(0.05)

def main():
    setup()
    print("Gas Leakage Alarm System Started")
    print("Sensor warming up...")
    time.sleep(2)

    while True:
        gas_level = analogPercent(GAS_PIN)
        print(f"Gas Level: {gas_level:3d}%", end="  ")

        if gas_level > DANGER_LIMIT:
            print("⛽ DANGER! GAS LEAKAGE!")
            danger_alarm()
        elif gas_level > CAUTION_LIMIT:
            print("⚠️  CAUTION — Gas Rising")
            digitalWrite(LED_PIN, 1)
            digitalWrite(BUZZER_PIN, 0)
        else:
            print("✅ Air Quality Normal")
            digitalWrite(BUZZER_PIN, 0)
            digitalWrite(LED_PIN,    0)

        time.sleep(0.5)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Gas Leakage Alarm System Started
Sensor warming up...
Gas Level:  15%  ✅ Air Quality Normal
Gas Level:  28%  ⚠️  CAUTION — Gas Rising
Gas Level:  55%  ⛽ DANGER! GAS LEAKAGE!
```

---

## 6. Temperature Monitoring System

### 🎯 Objective
Read and display temperature using a DHT11 sensor with status alerts on the serial monitor.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| DHT11 Temperature Sensor | 1 |
| LED (optional alert) | 1 |
| 10kΩ Pull-up Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| DHT_PIN | 14 | DHT11 Data Pin |
| LED_PIN | 4 | High Temp Alert LED |

### 💡 Working Principle
- DHT11 measures temperature using a capacitive humidity sensor and thermistor
- Reads Celsius and converts to Fahrenheit
- If temperature > 35°C → LED ON + High Temp Warning
- Updates every 2 seconds (DHT11 minimum interval)

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import Pin
import dht
import time

DHT_PIN  = 14
LED_PIN  = 4

TEMP_HIGH = 35    # °C — High temperature threshold
TEMP_LOW  = 15    # °C — Low temperature threshold

sensor = dht.DHT11(Pin(DHT_PIN))

def setup():
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    print("Temperature Monitoring System Started")

    while True:
        try:
            sensor.measure()
            temp_c = sensor.temperature()
            temp_f = temp_c * (9 / 5) + 32.0

            print(f"Temperature: {temp_c:.1f} °C  /  {temp_f:.1f} °F", end="  ")

            if temp_c > TEMP_HIGH:
                print("🌡️  HIGH TEMP WARNING!")
                digitalWrite(LED_PIN, 1)
            elif temp_c < TEMP_LOW:
                print("🧊 LOW TEMP WARNING!")
                digitalWrite(LED_PIN, 0)
            else:
                print("✅ Normal")
                digitalWrite(LED_PIN, 0)

        except OSError:
            print("❌ Sensor Read Error")

        time.sleep(2)

def cleanup():
    digitalWrite(LED_PIN, 0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Temperature Monitoring System Started
Temperature: 28.0 °C  /  82.4 °F  ✅ Normal
Temperature: 36.5 °C  /  97.7 °F  🌡️  HIGH TEMP WARNING!
Temperature: 12.0 °C  /  53.6 °F  🧊 LOW TEMP WARNING!
```

---

## 7. Humidity Monitoring System

### 🎯 Objective
Monitor air humidity levels using a DHT11 sensor and indicate comfort level via LED and serial output.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| DHT11 Temperature & Humidity Sensor | 1 |
| Green LED | 1 |
| Red LED | 1 |
| 10kΩ Pull-up Resistor | 1 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| DHT_PIN | 14 | DHT11 Data Pin |
| GREEN_LED | 4 | Normal Humidity LED |
| RED_LED | 5 | High/Low Humidity LED |

### 💡 Humidity Levels
| Range | Status | Indicator |
|---|---|---|
| < 30% | TOO DRY | Red LED |
| 30% – 60% | COMFORTABLE | Green LED |
| > 60% | TOO HUMID | Red LED |

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import Pin
import dht
import time

DHT_PIN   = 14
GREEN_LED = 4
RED_LED   = 5

DRY_LIMIT  = 30    # Below 30% = Dry
HUM_LIMIT  = 60    # Above 60% = Humid

sensor = dht.DHT11(Pin(DHT_PIN))

def setup():
    pinMode(GREEN_LED, OUTPUT)
    pinMode(RED_LED,   OUTPUT)

def main():
    setup()
    print("Humidity Monitoring System Started")

    while True:
        try:
            sensor.measure()
            humidity = sensor.humidity()
            temp     = sensor.temperature()

            print(f"Humidity: {humidity:.1f}%  Temp: {temp:.1f}°C", end="  ")

            if humidity < DRY_LIMIT:
                print("Status: TOO DRY 🏜️")
                digitalWrite(GREEN_LED, 0)
                digitalWrite(RED_LED,   1)
            elif humidity > HUM_LIMIT:
                print("Status: TOO HUMID 💦")
                digitalWrite(GREEN_LED, 0)
                digitalWrite(RED_LED,   1)
            else:
                print("Status: COMFORTABLE 😊")
                digitalWrite(RED_LED,   0)
                digitalWrite(GREEN_LED, 1)

        except OSError:
            print("❌ Sensor Read Error")

        time.sleep(2)

def cleanup():
    digitalWrite(GREEN_LED, 0)
    digitalWrite(RED_LED,   0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Humidity Monitoring System Started
Humidity: 55.0%  Temp: 28.0°C  Status: COMFORTABLE 😊
Humidity: 75.0%  Temp: 30.0°C  Status: TOO HUMID 💦
Humidity: 22.0%  Temp: 25.0°C  Status: TOO DRY 🏜️
```

---

## 8. Motion Detection Alarm using PIR

### 🎯 Objective
Detect human or animal motion using a PIR sensor and trigger a buzzer alarm with LED indicator.

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

### 💡 Working Principle
- PIR sensor outputs HIGH when infrared motion is detected
- Edge detection: triggers alarm only on the rising edge (0 → 1)
- Alarm sounds for 3 seconds, then resets
- Detects new motion after the cooldown period

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

def trigger_alarm():
    print("🚨 MOTION DETECTED! ALARM TRIGGERED!")
    for _ in range(15):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(LED_PIN,    1)
        time.sleep(0.1)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(LED_PIN,    0)
        time.sleep(0.1)

def main():
    setup()
    last_state = 0
    print("Motion Detection Alarm Started")
    print("Sensor stabilizing... please wait 30 seconds")
    time.sleep(3)    # Allow PIR to stabilize (use 30s in real deployment)
    print("System Armed — Monitoring for motion...")

    while True:
        motion = digitalRead(PIR_PIN)

        if last_state == 0 and motion == 1:
            trigger_alarm()

        elif motion == 0 and last_state == 1:
            print("✅ Motion Cleared")
            digitalWrite(BUZZER_PIN, 0)
            digitalWrite(LED_PIN,    0)

        last_state = motion
        time.sleep(0.1)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    print("System Disarmed")

run(main, cleanup)
```

### 📝 Expected Output
```
Motion Detection Alarm Started
Sensor stabilizing... please wait 30 seconds
System Armed — Monitoring for motion...
🚨 MOTION DETECTED! ALARM TRIGGERED!
✅ Motion Cleared
🚨 MOTION DETECTED! ALARM TRIGGERED!
```

---

## 9. Water Level Indicator

### 🎯 Objective
Monitor water level in a tank using an analog water level sensor and indicate level with LEDs.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Water Level Sensor (Analog) | 1 |
| Green LED | 1 |
| Yellow LED | 1 |
| Red LED | 1 |
| Buzzer | 1 |
| 220Ω Resistor | 3 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| WATER_PIN | 34 | Water Level Sensor |
| GREEN_LED | 4 | High Level (Full) |
| YELLOW_LED | 5 | Medium Level |
| RED_LED | 18 | Low Level (Empty) |
| BUZZER_PIN | 19 | Low Level Buzzer Alert |

### 💡 Water Level Zones
| Level | Range | LED | Status |
|---|---|---|---|
| HIGH | > 70% | Green ON | Tank Full |
| MEDIUM | 30%–70% | Yellow ON | Normal |
| LOW | < 30% | Red ON + Buzzer | Tank Empty |

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

WATER_PIN   = 34
GREEN_LED   = 4
YELLOW_LED  = 5
RED_LED     = 18
BUZZER_PIN  = 19

HIGH_LIMIT  = 70
LOW_LIMIT   = 30

def setup():
    analogPin(WATER_PIN)
    pinMode(GREEN_LED,  OUTPUT)
    pinMode(YELLOW_LED, OUTPUT)
    pinMode(RED_LED,    OUTPUT)
    pinMode(BUZZER_PIN, OUTPUT)

def all_leds_off():
    digitalWrite(GREEN_LED,  0)
    digitalWrite(YELLOW_LED, 0)
    digitalWrite(RED_LED,    0)

def low_alert():
    digitalWrite(BUZZER_PIN, 1)
    time.sleep(0.3)
    digitalWrite(BUZZER_PIN, 0)
    time.sleep(0.3)

def main():
    setup()
    print("Water Level Indicator Started")

    while True:
        level = analogPercent(WATER_PIN)
        print(f"Water Level: {level:3d}%", end="  ")

        all_leds_off()

        if level > HIGH_LIMIT:
            print("Status: 🟢 TANK FULL")
            digitalWrite(GREEN_LED,  1)
            digitalWrite(BUZZER_PIN, 0)
        elif level > LOW_LIMIT:
            print("Status: 🟡 NORMAL")
            digitalWrite(YELLOW_LED, 1)
            digitalWrite(BUZZER_PIN, 0)
        else:
            print("Status: 🔴 TANK EMPTY!")
            digitalWrite(RED_LED, 1)
            low_alert()

        time.sleep(1)

def cleanup():
    all_leds_off()
    digitalWrite(BUZZER_PIN, 0)
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Water Level Indicator Started
Water Level:  85%  Status: 🟢 TANK FULL
Water Level:  50%  Status: 🟡 NORMAL
Water Level:  18%  Status: 🔴 TANK EMPTY!
```

---

## 10. Sound Level Detection System

### 🎯 Objective
Detect ambient sound level using an analog sound sensor and display intensity with LED indication.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Sound Sensor Module (Analog) | 1 |
| Green LED | 1 |
| Yellow LED | 1 |
| Red LED | 1 |
| 220Ω Resistor | 3 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SOUND_PIN | 34 | Sound Sensor Analog Output |
| GREEN_LED | 4 | Low Sound Level |
| YELLOW_LED | 5 | Medium Sound Level |
| RED_LED | 18 | High / Loud Sound Level |

### 💡 Sound Level Zones
| Zone | Range | LED | Status |
|---|---|---|---|
| QUIET | < 30% | Green | Normal |
| MODERATE | 30%–65% | Yellow | Caution |
| LOUD | > 65% | Red | Warning |

### 🖥️ Code

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

SOUND_PIN   = 34
GREEN_LED   = 4
YELLOW_LED  = 5
RED_LED     = 18

LOUD_LIMIT     = 65
MODERATE_LIMIT = 30

def setup():
    analogPin(SOUND_PIN)
    pinMode(GREEN_LED,  OUTPUT)
    pinMode(YELLOW_LED, OUTPUT)
    pinMode(RED_LED,    OUTPUT)

def all_leds_off():
    digitalWrite(GREEN_LED,  0)
    digitalWrite(YELLOW_LED, 0)
    digitalWrite(RED_LED,    0)

def draw_bar(level):
    filled = int(level / 5)
    bar    = "█" * filled + "░" * (20 - filled)
    return f"[{bar}] {level:3d}%"

def main():
    setup()
    print("Sound Level Detection System Started")

    while True:
        sound = analogPercent(SOUND_PIN)
        bar   = draw_bar(sound)

        all_leds_off()

        if sound > LOUD_LIMIT:
            print(f"Sound: {bar}  🔴 LOUD!")
            digitalWrite(RED_LED, 1)
        elif sound > MODERATE_LIMIT:
            print(f"Sound: {bar}  🟡 MODERATE")
            digitalWrite(YELLOW_LED, 1)
        else:
            print(f"Sound: {bar}  🟢 QUIET")
            digitalWrite(GREEN_LED, 1)

        time.sleep(0.1)

def cleanup():
    all_leds_off()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Sound Level Detection System Started
Sound: [████░░░░░░░░░░░░░░░░]  20%  🟢 QUIET
Sound: [████████████░░░░░░░░]  60%  🟡 MODERATE
Sound: [█████████████████░░░]  85%  🔴 LOUD!
```

---

## 📚 Quick Reference — Sensor Functions

### Analog Sensors
```python
analogPin(pin)              # Initialize analog pin
analogRead(pin)             # Raw ADC value (0–4095)
analogPercent(pin)          # Percentage 0–100%
analogThreshold(pin, val)   # Returns True if above threshold
```

### Digital Sensors
```python
pinMode(pin, INPUT)         # Set as input
digitalRead(pin)            # Read 0 or 1
```

### DHT11 Sensor
```python
import dht
from machine import Pin

sensor = dht.DHT11(Pin(14))
sensor.measure()
temp = sensor.temperature()   # Celsius
hum  = sensor.humidity()      # Percentage
```

### Sensor → Percentage Conversion
```python
# Sensors that read LOWER when active (flame, soil moisture, rain):
value = 100 - analogPercent(pin)

# Sensors that read HIGHER when active (gas, sound, water level):
value = analogPercent(pin)
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

# 🏆 STEM Exhibition Projects — ESP32 MicroPython

> All projects use the `systemio` library with `setup()`, `main()`, and `cleanup()` functions.
> Code style follows the `from digital import *` / `from analog import *` / `from oled import *` pattern.
> These projects are designed for STEM exhibitions — each combines multiple sensors and outputs.

---

## Table of Contents

1. [Smart Irrigation System](#1-smart-irrigation-system)
2. [Smart Home Automation](#2-smart-home-automation)
3. [Fire Detection and Alert System](#3-fire-detection-and-alert-system)
4. [Smart Weather Monitoring Station](#4-smart-weather-monitoring-station)
5. [Smart Parking Indicator](#5-smart-parking-indicator)
6. [Intelligent Street Lighting](#6-intelligent-street-lighting)
7. [Smart Dustbin](#7-smart-dustbin)
8. [Smart Water Tank Monitoring](#8-smart-water-tank-monitoring)
9. [IoT-Based Plant Monitoring](#9-iot-based-plant-monitoring)
10. [Multi-Sensor Security Robot](#10-multi-sensor-security-robot)

---

## 1. Smart Irrigation System

### 🎯 Objective
Automatically water plants by activating a pump when soil is dry and stopping when moisture is adequate. Displays live status on OLED.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Soil Moisture Sensor (Analog) | 1 |
| DHT11 Temperature & Humidity | 1 |
| Mini Water Pump + Relay Module | 1 |
| SSD1306 OLED (128×64) | 1 |
| Green LED (Pump ON) | 1 |
| Red LED (Dry Alert) | 1 |
| Buzzer | 1 |
| 220Ω Resistors | 2 |
| 10kΩ Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| SOIL_PIN | 34 | Soil Moisture Sensor |
| DHT_PIN | 14 | DHT11 Data |
| PUMP_PIN | 4 | Relay / Water Pump |
| GREEN_LED | 5 | Pump Running LED |
| RED_LED | 18 | Dry Alert LED |
| BUZZER_PIN | 19 | Alert Buzzer |

### 💡 System Logic
| Soil Moisture | Action | Display |
|---|---|---|
| < 30% (DRY) | Pump ON + Buzzer beep | 🔴 DRY — Watering |
| 30–70% (OK) | Pump OFF | 🟡 MODERATE |
| > 70% (WET) | Pump OFF | 🟢 WET — Healthy |

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow, oledRect, oledFill
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import Pin
import dht
import time

SOIL_PIN   = 34
DHT_PIN    = 14
PUMP_PIN   = 4
GREEN_LED  = 5
RED_LED    = 18
BUZZER_PIN = 19

DRY_LIMIT  = 30
WET_LIMIT  = 70

sensor = dht.DHT11(Pin(DHT_PIN))

def setup():
    oledSetup()
    analogPin(SOIL_PIN)
    for pin in [PUMP_PIN, GREEN_LED, RED_LED, BUZZER_PIN]:
        pinMode(pin, OUTPUT)

def pump_on():
    digitalWrite(PUMP_PIN,  1)
    digitalWrite(GREEN_LED, 1)
    digitalWrite(RED_LED,   0)

def pump_off():
    digitalWrite(PUMP_PIN,  0)
    digitalWrite(GREEN_LED, 0)

def alert_beep():
    digitalWrite(BUZZER_PIN, 1)
    time.sleep(0.1)
    digitalWrite(BUZZER_PIN, 0)

def draw_bar(val, y):
    oledRect(0, y, 128, 8)
    fill_w = int((val / 100) * 124)
    if fill_w > 0:
        oledFill(2, y + 2, fill_w, 4)

def draw_display(moisture, temp, hum, pumping):
    status = "WATERING 💧" if pumping else ("DRY 🌵" if moisture < DRY_LIMIT else ("WET 💦" if moisture > WET_LIMIT else "OK  🌱"))
    oledClear()
    oledText("Smart Irrigation",      0,  0)
    oledText("-" * 21,                0,  9)
    oledText(f"Soil : {moisture:3d}%", 0, 18)
    draw_bar(moisture,                    26)
    oledText(f"Temp : {temp:.1f}C  Hum:{hum:.0f}%", 0, 36)
    oledText(f"Pump : {'ON  ' if pumping else 'OFF '}", 0, 46)
    oledText(status,                  0, 56)
    oledShow()

def main():
    setup()
    pumping     = False
    pump_cycles = 0
    print("Smart Irrigation System Started")

    while True:
        moisture = 100 - analogPercent(SOIL_PIN)

        try:
            sensor.measure()
            temp = sensor.temperature()
            hum  = sensor.humidity()
        except OSError:
            temp, hum = 0.0, 0.0

        if moisture < DRY_LIMIT and not pumping:
            print(f"💧 DRY ({moisture}%) — Pump ON")
            pump_on()
            pumping = True
            pump_cycles += 1
            alert_beep()
            digitalWrite(RED_LED, 1)

        elif moisture >= WET_LIMIT and pumping:
            print(f"✅ WET ({moisture}%) — Pump OFF")
            pump_off()
            pumping = False
            digitalWrite(RED_LED, 0)

        draw_display(moisture, temp, hum, pumping)
        print(f"Soil:{moisture}%  Temp:{temp}°C  Hum:{hum}%  Pump:{'ON' if pumping else 'OFF'}  Cycles:{pump_cycles}")
        time.sleep(2)

def cleanup():
    pump_off()
    digitalWrite(RED_LED,    0)
    digitalWrite(BUZZER_PIN, 0)
    oledClear()
    oledText("System OFF", 24, 28)
    oledShow()
    print("Irrigation System Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Smart Irrigation       │
│ ─────────────────────  │
│ Soil :  22%            │
│ [████░░░░░░░░░░░░░░░░] │
│ Temp : 29.0C  Hum:58%  │
│ Pump : ON              │
│ WATERING 💧            │
└────────────────────────┘
```

---

## 2. Smart Home Automation

### 🎯 Objective
Automate home appliances — lights based on LDR, fan based on temperature, and security alert based on PIR motion. All status shown on OLED.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| LDR Sensor | 1 |
| DHT11 Sensor | 1 |
| PIR Motion Sensor | 1 |
| LED (Room Light) | 1 |
| DC Fan / Motor | 1 |
| L298N Motor Driver | 1 |
| Buzzer (Security) | 1 |
| 10kΩ Resistors | 2 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| LDR_PIN | 34 | LDR Sensor |
| DHT_PIN | 14 | DHT11 Data |
| PIR_PIN | 5 | PIR Sensor |
| LIGHT_PIN | 4 | Room Light LED |
| FAN_PIN | 18 | Fan PWM |
| BUZZER_PIN | 19 | Security Buzzer |

### 💡 Automation Rules
| Sensor | Condition | Action |
|---|---|---|
| LDR | Light < 30% | Room light ON |
| DHT11 | Temp > 30°C | Fan ON (HIGH) |
| DHT11 | Temp 25–30°C | Fan ON (LOW) |
| PIR | Motion detected | Buzzer alert |

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, digitalRead, pwmSetup, pwmWrite, pwmStop, INPUT, OUTPUT
from systemio import run
from machine import Pin
import dht
import time

LDR_PIN    = 34
DHT_PIN    = 14
PIR_PIN    = 5
LIGHT_PIN  = 4
FAN_PIN    = 18
BUZZER_PIN = 19

sensor = dht.DHT11(Pin(DHT_PIN))

def setup():
    oledSetup()
    analogPin(LDR_PIN)
    pinMode(PIR_PIN,    INPUT)
    pinMode(LIGHT_PIN,  OUTPUT)
    pinMode(BUZZER_PIN, OUTPUT)
    pwmSetup(FAN_PIN, freq=1000)

def security_beep():
    for _ in range(4):
        digitalWrite(BUZZER_PIN, 1)
        time.sleep(0.08)
        digitalWrite(BUZZER_PIN, 0)
        time.sleep(0.08)

def draw_dashboard(light_pct, temp, hum, light_on, fan_speed, motion):
    fan_label = "HIGH" if fan_speed > 600 else ("LOW " if fan_speed > 0 else "OFF ")
    oledClear()
    oledText("Smart Home",          20,  0)
    oledText("-" * 21,               0,  9)
    oledText(f"Light: {light_pct:3d}%  Lamp:{'ON ' if light_on else 'OFF'}", 0, 18)
    oledText(f"Temp : {temp:.1f}C   Fan:{fan_label}", 0, 28)
    oledText(f"Humid: {hum:.0f}%",   0, 38)
    oledText(f"PIR  : {'MOTION! 🚨' if motion else 'Clear  ✅'}", 0, 48)
    oledShow()

def main():
    setup()
    last_pir  = 0
    print("Smart Home Automation Started")

    while True:
        light_pct = analogPercent(LDR_PIN)
        motion    = digitalRead(PIR_PIN)

        try:
            sensor.measure()
            temp = sensor.temperature()
            hum  = sensor.humidity()
        except OSError:
            temp, hum = 0.0, 0.0

        # Auto Light
        light_on = light_pct < 30
        digitalWrite(LIGHT_PIN, 1 if light_on else 0)

        # Auto Fan
        if temp > 30:
            pwmWrite(FAN_PIN, 1023)
            fan_speed = 1023
        elif temp > 25:
            pwmWrite(FAN_PIN, 450)
            fan_speed = 450
        else:
            pwmWrite(FAN_PIN, 0)
            fan_speed = 0

        # Security PIR
        if last_pir == 0 and motion == 1:
            print("🚨 MOTION DETECTED!")
            security_beep()

        draw_dashboard(light_pct, temp, hum, light_on, fan_speed, motion)
        print(f"Light:{light_pct}% {'ON' if light_on else 'OFF'}  Temp:{temp}°C  Fan:{fan_speed}  PIR:{'MOTION' if motion else 'Clear'}")

        last_pir = motion
        time.sleep(1)

def cleanup():
    digitalWrite(LIGHT_PIN,  0)
    digitalWrite(BUZZER_PIN, 0)
    pwmStop(FAN_PIN)
    oledClear()
    oledText("System OFF", 24, 28)
    oledShow()
    print("Home Automation Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│     Smart Home         │
│ ─────────────────────  │
│ Light:  22%  Lamp: ON  │
│ Temp : 31.0C  Fan:HIGH │
│ Humid: 60%             │
│ PIR  : Clear  ✅       │
└────────────────────────┘
```

---

## 3. Fire Detection and Alert System

### 🎯 Objective
Detect fire using a flame sensor and gas using an MQ-2 sensor. Trigger multi-level alarms and display threat status on OLED.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| Flame Sensor (Analog) | 1 |
| MQ-2 Gas Sensor (Analog) | 1 |
| Buzzer | 1 |
| Red LED | 1 |
| Yellow LED | 1 |
| 220Ω Resistors | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| FLAME_PIN | 34 | Flame Sensor Analog |
| GAS_PIN | 35 | MQ-2 Gas Sensor Analog |
| BUZZER_PIN | 14 | Buzzer |
| RED_LED | 4 | Fire / Danger LED |
| YELLOW_LED | 5 | Gas / Caution LED |

### 💡 Alert Levels
| Level | Condition | Siren | Display |
|---|---|---|---|
| SAFE | Both < 20% | Silent | ✅ All Clear |
| CAUTION | Gas 20–40% | Slow beep | ⚠️ Gas Rising |
| FIRE | Flame > 30% | Rapid | 🔥 Fire Alert |
| EMERGENCY | Flame > 60% OR Gas > 40% | Continuous | 🆘 EMERGENCY |

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

FLAME_PIN  = 34
GAS_PIN    = 35
BUZZER_PIN = 14
RED_LED    = 4
YELLOW_LED = 5

def setup():
    oledSetup()
    analogPin(FLAME_PIN)
    analogPin(GAS_PIN)
    for pin in [BUZZER_PIN, RED_LED, YELLOW_LED]:
        pinMode(pin, OUTPUT)

def all_off():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(RED_LED,    0)
    digitalWrite(YELLOW_LED, 0)

def beep(on_t, off_t, count):
    for _ in range(count):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(RED_LED,    1)
        time.sleep(on_t)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(RED_LED,    0)
        time.sleep(off_t)

def draw_display(flame, gas, level, msg):
    oledClear()
    oledText("Fire Alert System",   0,  0)
    oledText("-" * 21,              0,  9)
    oledText(f"Flame: {flame:3d}%", 0, 18)
    oledText(f"Gas  : {gas:3d}%",   0, 28)
    oledText(f"Level: {level}",     0, 38)
    oledText(msg,                   0, 52)
    oledShow()

def main():
    setup()
    print("Fire Detection and Alert System Started")

    while True:
        flame = 100 - analogPercent(FLAME_PIN)
        gas   = analogPercent(GAS_PIN)

        print(f"Flame: {flame}%  Gas: {gas}%", end="  ")

        if flame > 60 or gas > 40:
            level = "EMERGENCY"
            msg   = "🆘 EVACUATE NOW!"
            all_off()
            beep(0.05, 0.05, 15)
            digitalWrite(RED_LED,    1)
            digitalWrite(YELLOW_LED, 1)
            print(msg)
        elif flame > 30:
            level = "FIRE"
            msg   = "🔥 FIRE DETECTED!"
            all_off()
            beep(0.1, 0.1, 6)
            digitalWrite(RED_LED, 1)
            print(msg)
        elif gas > 20:
            level = "CAUTION"
            msg   = "⚠️  GAS RISING"
            all_off()
            digitalWrite(YELLOW_LED, 1)
            beep(0.3, 0.5, 2)
            print(msg)
        else:
            level = "SAFE"
            msg   = "✅ ALL CLEAR"
            all_off()
            print(msg)

        draw_display(flame, gas, level, msg)
        time.sleep(0.5)

def cleanup():
    all_off()
    oledClear()
    oledText("System OFF", 24, 28)
    oledShow()
    print("Alert System Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Fire Alert System      │
│ ─────────────────────  │
│ Flame:  65%            │
│ Gas  :  18%            │
│ Level: EMERGENCY       │
│                        │
│ 🆘 EVACUATE NOW!       │
└────────────────────────┘
```

---

## 4. Smart Weather Monitoring Station

### 🎯 Objective
Build a complete weather station that measures temperature, humidity, light intensity, and rain, displaying all data on OLED with status classification.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| DHT11 Sensor | 1 |
| LDR Sensor | 1 |
| Rain Sensor (Analog) | 1 |
| Buzzer | 1 |
| 10kΩ Resistors | 2 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| DHT_PIN | 14 | DHT11 Data |
| LDR_PIN | 34 | LDR Sensor |
| RAIN_PIN | 35 | Rain Sensor |
| BUZZER_PIN | 4 | Rain Alert Buzzer |

### 💡 Weather Conditions
| Inputs | Condition Label |
|---|---|
| Light > 70%, Temp > 28°C | Sunny & Hot |
| Light > 70%, Temp ≤ 28°C | Sunny & Cool |
| Rain > 30% | Rainy |
| Hum > 70% | Cloudy / Humid |
| Temp < 18°C | Cold |
| Others | Pleasant |

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import Pin, RTC
import dht
import time

DHT_PIN    = 14
LDR_PIN    = 34
RAIN_PIN   = 35
BUZZER_PIN = 4

sensor = dht.DHT11(Pin(DHT_PIN))
rtc    = RTC()

def setup():
    oledSetup()
    analogPin(LDR_PIN)
    analogPin(RAIN_PIN)
    pinMode(BUZZER_PIN, OUTPUT)
    rtc.datetime((2025, 1, 1, 2, 9, 0, 0, 0))

def get_condition(temp, hum, light, rain):
    if rain > 30:                     return "Rainy      🌧️"
    elif light > 70 and temp > 28:    return "Sunny&Hot  ☀️"
    elif light > 70:                  return "Sunny&Cool 🌤️"
    elif hum > 70:                    return "Humid      💧"
    elif temp < 18:                   return "Cold       🧊"
    else:                             return "Pleasant   😊"

def heat_index(t, h):
    return round(-8.78 + 1.61*t + 2.34*h - 0.15*t*h - 0.012*t**2 - 0.016*h**2, 1)

def rain_beep():
    for _ in range(2):
        digitalWrite(BUZZER_PIN, 1)
        time.sleep(0.1)
        digitalWrite(BUZZER_PIN, 0)
        time.sleep(0.1)

def draw_station(temp, hum, hi, light, rain, cond):
    dt = rtc.datetime()
    oledClear()
    oledText("Weather Station",             0,  0)
    oledText(f"{dt[4]:02d}:{dt[5]:02d}  {dt[2]:02d}/{dt[1]:02d}/{dt[0]}", 0,  9)
    oledText(f"Temp:{temp:.1f}C  Hum:{hum:.0f}%", 0, 19)
    oledText(f"HI  :{hi}C  Rain:{rain:2d}%",  0, 29)
    oledText(f"Light: {light:3d}%",           0, 39)
    oledText(cond,                            0, 52)
    oledShow()

def main():
    setup()
    prev_rain = False
    print("Smart Weather Station Started")

    while True:
        try:
            sensor.measure()
            temp = sensor.temperature()
            hum  = sensor.humidity()
            hi   = heat_index(temp, hum)
        except OSError:
            temp, hum, hi = 0.0, 0.0, 0.0

        light = analogPercent(LDR_PIN)
        rain  = 100 - analogPercent(RAIN_PIN)
        cond  = get_condition(temp, hum, light, rain)

        if rain > 30 and not prev_rain:
            print("🌧️  Rain started!")
            rain_beep()
            prev_rain = True
        elif rain <= 30:
            prev_rain = False
            digitalWrite(BUZZER_PIN, 0)

        draw_station(temp, hum, hi, light, rain, cond)
        print(f"T:{temp}°C  H:{hum}%  HI:{hi}  L:{light}%  R:{rain}%  {cond}")
        time.sleep(3)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    oledClear()
    oledText("Station OFF", 18, 28)
    oledShow()
    print("Weather Station Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Weather Station        │
│ 09:15  01/01/2025      │
│ Temp:28.0C  Hum:65%    │
│ HI  :30.2C  Rain: 8%   │
│ Light:  72%            │
│                        │
│ Sunny&Hot  ☀️          │
└────────────────────────┘
```

---

## 5. Smart Parking Indicator

### 🎯 Objective
Simulate a 3-slot smart parking system — each slot uses an ultrasonic/IR sensor to detect occupancy and shows availability on OLED with LED indicators.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| IR Sensor Module | 3 |
| Green LED | 3 |
| Red LED | 3 |
| Buzzer | 1 |
| 220Ω Resistors | 6 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| SLOT1_IR | 4 | Slot 1 IR Sensor |
| SLOT2_IR | 5 | Slot 2 IR Sensor |
| SLOT3_IR | 18 | Slot 3 IR Sensor |
| SLOT1_GRN | 12 | Slot 1 Green LED |
| SLOT1_RED | 13 | Slot 1 Red LED |
| SLOT2_GRN | 2 | Slot 2 Green LED |
| SLOT2_RED | 15 | Slot 2 Red LED |
| SLOT3_GRN | 0 | Slot 3 Green LED |
| SLOT3_RED | 16 | Slot 3 Red LED |
| BUZZER_PIN | 19 | Entry/Exit Buzzer |

### 💡 Slot Logic
- IR sensor HIGH = Slot OCCUPIED (car present)
- IR sensor LOW = Slot FREE
- Green LED = Free, Red LED = Occupied
- OLED shows slot map and total available count

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow, oledRect, oledFill
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

SLOT_IR  = [4,  5,  18]
SLOT_GRN = [12, 2,  0 ]
SLOT_RED = [13, 15, 16]
BUZZER   = 19

def setup():
    oledSetup()
    for pin in SLOT_IR:  pinMode(pin, INPUT)
    for pin in SLOT_GRN: pinMode(pin, OUTPUT)
    for pin in SLOT_RED: pinMode(pin, OUTPUT)
    pinMode(BUZZER, OUTPUT)

def entry_beep():
    digitalWrite(BUZZER, 1)
    time.sleep(0.1)
    digitalWrite(BUZZER, 0)

def full_beep():
    for _ in range(3):
        digitalWrite(BUZZER, 1)
        time.sleep(0.05)
        digitalWrite(BUZZER, 0)
        time.sleep(0.05)

def draw_parking(occupied, free_count):
    oledClear()
    oledText("Smart Parking",                          0,  0)
    oledText("-" * 21,                                 0,  9)
    oledText(f"Available: {free_count} / {len(SLOT_IR)}", 0, 18)
    oledText("-" * 21,                                 0, 27)

    for i in range(len(SLOT_IR)):
        x     = 4 + i * 42
        state = "OCC" if occupied[i] else "FREE"
        oledRect(x, 30, 38, 22)
        if occupied[i]:
            oledFill(x + 1, 31, 36, 20)
        oledText(f"S{i+1}",  x + 12, 33)
        oledText(state,      x + 3,  43)

    status = "FULL! No Space" if free_count == 0 else f"{free_count} Slot(s) Free"
    oledText(status, 0, 56)
    oledShow()

def main():
    setup()
    prev_occupied = [False] * len(SLOT_IR)
    print("Smart Parking Indicator Started")

    while True:
        occupied   = [digitalRead(p) == 1 for p in SLOT_IR]
        free_count = occupied.count(False)

        for i in range(len(SLOT_IR)):
            digitalWrite(SLOT_GRN[i], 0 if occupied[i] else 1)
            digitalWrite(SLOT_RED[i], 1 if occupied[i] else 0)

            if occupied[i] != prev_occupied[i]:
                action = "ENTERED" if occupied[i] else "EXITED"
                print(f"Slot {i+1}: {action}")
                entry_beep()

        if free_count == 0 and any(occupied[i] != prev_occupied[i] for i in range(len(SLOT_IR))):
            full_beep()

        draw_parking(occupied, free_count)
        print(f"Slots: {['OCC' if o else 'FREE' for o in occupied]}  Free: {free_count}")
        prev_occupied = list(occupied)
        time.sleep(0.5)

def cleanup():
    for pin in SLOT_GRN + SLOT_RED: digitalWrite(pin, 0)
    digitalWrite(BUZZER, 0)
    oledClear()
    oledText("Parking OFF", 18, 28)
    oledShow()
    print("Parking System Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Smart Parking          │
│ ─────────────────────  │
│ Available: 2 / 3       │
│ ─────────────────────  │
│ ┌──────┐┌──────┐┌─────┐│
│ │  S1  ││  S2  ││  S3 ││
│ │ OCC  ││ FREE ││ FREE││
│ 2 Slot(s) Free         │
└────────────────────────┘
```

---

## 6. Intelligent Street Lighting

### 🎯 Objective
Automatically dim or brighten street lights based on ambient light (LDR) and switch to emergency mode when motion is detected at night.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| LDR Sensor | 1 |
| PIR Motion Sensor | 1 |
| LED (Street Light) | 3 |
| 10kΩ Pull-down Resistor | 1 |
| 220Ω Resistors | 3 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| LDR_PIN | 34 | LDR Analog Input |
| PIR_PIN | 5 | PIR Motion Sensor |
| LIGHT1 | 4 | Street Light 1 (PWM) |
| LIGHT2 | 18 | Street Light 2 (PWM) |
| LIGHT3 | 19 | Street Light 3 (PWM) |

### 💡 Control Modes
| Mode | Condition | Light Level |
|---|---|---|
| DAY | Light > 60% | All OFF |
| DIM | Light 30–60% | 30% brightness |
| NIGHT | Light < 30%, No motion | 60% brightness |
| MOTION | Light < 30% + Motion | 100% brightness |

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from analog import analogPin, analogPercent
from digital import pinMode, digitalRead, pwmSetup, pwmWrite, pwmStop, INPUT
from systemio import run
import time

LDR_PIN = 34
PIR_PIN = 5
LIGHTS  = [4, 18, 19]

DUTY_OFF    = 0
DUTY_DIM    = 300
DUTY_NIGHT  = 600
DUTY_FULL   = 1023

def setup():
    oledSetup()
    analogPin(LDR_PIN)
    pinMode(PIR_PIN, INPUT)
    for pin in LIGHTS:
        pwmSetup(pin, freq=1000)

def set_lights(duty):
    for pin in LIGHTS:
        pwmWrite(pin, duty)

def draw_display(light_pct, motion, mode, duty):
    brightness = int((duty / 1023) * 100)
    oledClear()
    oledText("Street Lighting",          0,  0)
    oledText("-" * 21,                   0,  9)
    oledText(f"Ambient : {light_pct:3d}%", 0, 18)
    oledText(f"Motion  : {'YES 🏃' if motion else 'No  ✅'}", 0, 28)
    oledText(f"Mode    : {mode}",         0, 38)
    oledText(f"Lights  : {brightness:3d}% brightness", 0, 50)
    oledShow()

def main():
    setup()
    motion_timer = 0
    print("Intelligent Street Lighting Started")

    while True:
        light_pct = analogPercent(LDR_PIN)
        motion    = digitalRead(PIR_PIN)

        if motion == 1:
            motion_timer = 10    # Stay bright for 10 cycles after motion

        if motion_timer > 0:
            motion_timer -= 1

        active_motion = motion_timer > 0

        if light_pct > 60:
            mode = "DAY    ☀️"
            duty = DUTY_OFF
        elif light_pct > 30:
            mode = "DIM    🌆"
            duty = DUTY_DIM
        elif active_motion:
            mode = "MOTION 🏃"
            duty = DUTY_FULL
        else:
            mode = "NIGHT  🌙"
            duty = DUTY_NIGHT

        set_lights(duty)
        draw_display(light_pct, active_motion, mode, duty)
        print(f"Light:{light_pct}%  Motion:{'YES' if active_motion else 'No'}  Mode:{mode.strip()}  Duty:{duty}")
        time.sleep(1)

def cleanup():
    set_lights(0)
    for pin in LIGHTS:
        pwmStop(pin)
    oledClear()
    oledText("Lights OFF", 22, 28)
    oledShow()
    print("Street Lighting Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Street Lighting        │
│ ─────────────────────  │
│ Ambient :  18%         │
│ Motion  : YES 🏃       │
│ Mode    : MOTION 🏃    │
│ Lights  : 100% brightness│
└────────────────────────┘
```

---

## 7. Smart Dustbin

### 🎯 Objective
Build a dustbin that opens its lid automatically when a hand is detected nearby using an ultrasonic sensor, and shows fill level on OLED.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| HC-SR04 Ultrasonic (Lid) | 1 |
| HC-SR04 Ultrasonic (Fill Level) | 1 |
| Servo Motor (Lid) | 1 |
| Green LED (Ready) | 1 |
| Red LED (Full) | 1 |
| Buzzer | 1 |
| 220Ω Resistors | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| LID_TRIG | 5 | Lid Sensor Trigger |
| LID_ECHO | 18 | Lid Sensor Echo |
| FILL_TRIG | 19 | Fill Level Trigger |
| FILL_ECHO | 21 | Fill Level Echo |
| SERVO_PIN | 4 | Servo Motor (Lid) |
| GREEN_LED | 12 | Ready LED |
| RED_LED | 13 | Full LED |
| BUZZER_PIN | 14 | Full Alert Buzzer |

### 💡 System Logic
- Hand within 15 cm of lid sensor → Servo opens lid → waits 3s → closes
- Fill sensor measures bin depth; calculates % filled
- If fill > 80% → RED LED + Buzzer alert + OLED warning

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow, oledRect, oledFill
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import Pin, PWM
import time

LID_TRIG   = 5
LID_ECHO   = 18
FILL_TRIG  = 19
FILL_ECHO  = 21
SERVO_PIN  = 4
GREEN_LED  = 12
RED_LED    = 13
BUZZER_PIN = 14

BIN_DEPTH_CM = 30    # Total bin depth in cm
HAND_DIST    = 15    # Trigger distance for lid
FULL_LIMIT   = 80    # % fill to trigger alert

lid_trig  = Pin(LID_TRIG,  Pin.OUT)
lid_echo  = Pin(LID_ECHO,  Pin.IN)
fill_trig = Pin(FILL_TRIG, Pin.OUT)
fill_echo = Pin(FILL_ECHO, Pin.IN)
servo     = PWM(Pin(SERVO_PIN), freq=50)

def setup():
    oledSetup()
    for pin in [GREEN_LED, RED_LED, BUZZER_PIN]:
        pinMode(pin, OUTPUT)
    servo.duty(77)    # Start closed

def get_dist(trig, echo):
    trig.value(0); time.sleep_us(2)
    trig.value(1); time.sleep_us(10)
    trig.value(0)
    while echo.value() == 0: pass
    t1 = time.ticks_us()
    while echo.value() == 1: pass
    t2 = time.ticks_us()
    return (time.ticks_diff(t2, t1) / 2) / 29.1

def open_lid():
    servo.duty(128)    # ~90 degrees open

def close_lid():
    servo.duty(77)     # ~0 degrees closed

def full_alert():
    for _ in range(3):
        digitalWrite(BUZZER_PIN, 1)
        time.sleep(0.1)
        digitalWrite(BUZZER_PIN, 0)
        time.sleep(0.1)

def draw_display(hand_dist, fill_pct, lid_open):
    fill_h = int((fill_pct / 100) * 20)
    oledClear()
    oledText("Smart Dustbin",       0,  0)
    oledText("-" * 21,              0,  9)
    oledText(f"Hand : {hand_dist:.1f} cm", 0, 18)
    oledText(f"Fill : {fill_pct:3d}%", 0, 28)
    oledText(f"Lid  : {'OPEN 🔓' if lid_open else 'CLOSED 🔒'}", 0, 38)
    oledRect(100, 10, 24, 22)
    if fill_h > 0:
        oledFill(101, 10 + (22 - fill_h), 22, fill_h)
    if fill_pct >= FULL_LIMIT:
        oledText("⚠️  BIN FULL!",  12, 52)
    else:
        oledText("Ready ✅",        28, 52)
    oledShow()

def main():
    setup()
    lid_open      = False
    lid_timer     = 0
    print("Smart Dustbin Started")

    while True:
        hand_dist = get_dist(lid_trig, lid_echo)
        fill_dist = get_dist(fill_trig, fill_echo)
        fill_pct  = max(0, min(100, int(((BIN_DEPTH_CM - fill_dist) / BIN_DEPTH_CM) * 100)))

        # Auto open/close lid
        if hand_dist < HAND_DIST and not lid_open:
            print("🖐️  Hand detected — Opening lid")
            open_lid()
            lid_open  = True
            lid_timer = 6     # ~3 seconds at 0.5s loop
            digitalWrite(GREEN_LED, 1)

        if lid_open:
            lid_timer -= 1
            if lid_timer <= 0:
                print("🔒 Closing lid")
                close_lid()
                lid_open = False
                digitalWrite(GREEN_LED, 0)

        # Fill alert
        if fill_pct >= FULL_LIMIT:
            digitalWrite(RED_LED, 1)
            full_alert()
            print(f"⚠️  BIN FULL! {fill_pct}%")
        else:
            digitalWrite(RED_LED,    0)
            digitalWrite(BUZZER_PIN, 0)

        draw_display(hand_dist, fill_pct, lid_open)
        print(f"Hand:{hand_dist:.1f}cm  Fill:{fill_pct}%  Lid:{'OPEN' if lid_open else 'CLOSED'}")
        time.sleep(0.5)

def cleanup():
    close_lid()
    for pin in [GREEN_LED, RED_LED, BUZZER_PIN]:
        digitalWrite(pin, 0)
    oledClear()
    oledText("Dustbin OFF", 18, 28)
    oledShow()
    print("Smart Dustbin Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Smart Dustbin          │
│ ─────────────────────  │
│ Hand : 10.2 cm         │
│ Fill :  45%            │
│ Lid  : OPEN 🔓         │
│                        │
│     Ready ✅           │
└────────────────────────┘
```

---

## 8. Smart Water Tank Monitoring

### 🎯 Objective
Monitor a water tank's fill level using an ultrasonic sensor, auto-control a pump to refill it, and display live level on OLED.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| HC-SR04 Ultrasonic Sensor | 1 |
| Water Pump + Relay Module | 1 |
| Green LED (Full) | 1 |
| Yellow LED (Medium) | 1 |
| Red LED (Low) | 1 |
| Buzzer | 1 |
| 220Ω Resistors | 3 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| TRIG_PIN | 5 | Ultrasonic Trigger |
| ECHO_PIN | 18 | Ultrasonic Echo |
| PUMP_PIN | 4 | Water Pump Relay |
| GREEN_LED | 12 | Full Indicator |
| YELLOW_LED | 13 | Medium Indicator |
| RED_LED | 14 | Low Indicator |
| BUZZER_PIN | 19 | Low Level Buzzer |

### 💡 Tank Level Zones
| Level | % Fill | Pump | LED |
|---|---|---|---|
| FULL | > 80% | OFF | Green |
| MEDIUM | 40–80% | OFF | Yellow |
| LOW | 20–40% | ON (refill) | Red |
| CRITICAL | < 20% | ON + Alarm | Red Flash |

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow, oledRect, oledFill
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import Pin
import time

TRIG_PIN    = 5
ECHO_PIN    = 18
PUMP_PIN    = 4
GREEN_LED   = 12
YELLOW_LED  = 13
RED_LED     = 14
BUZZER_PIN  = 19

TANK_DEPTH_CM = 25    # Tank height in cm
FULL_LIMIT    = 80
LOW_LIMIT     = 40
CRITICAL_LIMIT = 20

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

def setup():
    oledSetup()
    for pin in [PUMP_PIN, GREEN_LED, YELLOW_LED, RED_LED, BUZZER_PIN]:
        pinMode(pin, OUTPUT)

def get_distance():
    trig.value(0); time.sleep_us(2)
    trig.value(1); time.sleep_us(10)
    trig.value(0)
    while echo.value() == 0: pass
    t1 = time.ticks_us()
    while echo.value() == 1: pass
    t2 = time.ticks_us()
    return (time.ticks_diff(t2, t1) / 2) / 29.1

def all_leds_off():
    for pin in [GREEN_LED, YELLOW_LED, RED_LED]:
        digitalWrite(pin, 0)

def critical_alarm():
    for _ in range(4):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(RED_LED,    1)
        time.sleep(0.08)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(RED_LED,    0)
        time.sleep(0.08)

def draw_tank(level_pct, pumping, mode):
    fill_h = int((level_pct / 100) * 40)
    oledClear()
    oledText("Water Tank Monitor",  0,  0)
    oledText("-" * 21,              0,  9)
    # Tank graphic (right side)
    oledRect(96, 8, 30, 44)
    if fill_h > 0:
        oledFill(97, 8 + (44 - fill_h), 28, fill_h)
    oledText(f"{level_pct}%", 98, 54)
    # Data (left side)
    oledText(f"Level: {level_pct:3d}%",             0, 18)
    oledText(f"Mode : {mode}",                       0, 28)
    oledText(f"Pump : {'ON  💧' if pumping else 'OFF ✅'}", 0, 38)
    oledShow()

def main():
    setup()
    pumping = False
    print("Smart Water Tank Monitoring Started")

    while True:
        dist      = get_distance()
        level_pct = max(0, min(100, int(((TANK_DEPTH_CM - dist) / TANK_DEPTH_CM) * 100)))

        all_leds_off()
        digitalWrite(BUZZER_PIN, 0)

        if level_pct > FULL_LIMIT:
            mode    = "FULL   🟢"
            digitalWrite(GREEN_LED, 1)
            if pumping:
                pumping = False
                digitalWrite(PUMP_PIN, 0)
                print("✅ Tank FULL — Pump OFF")

        elif level_pct > LOW_LIMIT:
            mode = "MEDIUM 🟡"
            digitalWrite(YELLOW_LED, 1)

        elif level_pct > CRITICAL_LIMIT:
            mode    = "LOW    🔴"
            digitalWrite(RED_LED, 1)
            if not pumping:
                pumping = True
                digitalWrite(PUMP_PIN, 1)
                print(f"💧 LOW ({level_pct}%) — Pump ON")

        else:
            mode = "CRITICAL ⚠️"
            critical_alarm()
            if not pumping:
                pumping = True
                digitalWrite(PUMP_PIN, 1)
                print(f"🆘 CRITICAL ({level_pct}%) — Pump ON + ALARM")

        draw_tank(level_pct, pumping, mode)
        print(f"Level:{level_pct}%  Mode:{mode.strip()}  Pump:{'ON' if pumping else 'OFF'}")
        time.sleep(2)

def cleanup():
    digitalWrite(PUMP_PIN,   0)
    all_leds_off()
    digitalWrite(BUZZER_PIN, 0)
    oledClear()
    oledText("Tank Monitor OFF", 4, 28)
    oledShow()
    print("Water Tank Monitor Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Water Tank Monitor     │
│ ─────────────────────  │
│ Level:  35%     ┌────┐ │
│ Mode : LOW 🔴   │    │ │
│ Pump : ON 💧    │████│ │
│                 │████│ │
│                  35%   │
└────────────────────────┘
```

---

## 9. IoT-Based Plant Monitoring

### 🎯 Objective
Monitor plant health using soil moisture, temperature, humidity, and light sensors. Serve live data on a Wi-Fi web dashboard and display on OLED.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| Soil Moisture Sensor | 1 |
| DHT11 Sensor | 1 |
| LDR Sensor | 1 |
| Water Pump + Relay | 1 |
| Green LED | 1 |
| 10kΩ Resistors | 2 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| SOIL_PIN | 34 | Soil Moisture |
| DHT_PIN | 14 | DHT11 Data |
| LDR_PIN | 35 | LDR Sensor |
| PUMP_PIN | 4 | Water Pump |
| LED_PIN | 5 | Status LED |

### 💡 Web Dashboard
Open browser to `http://<ESP32-IP>` to view live:
- Soil moisture % + status
- Temperature & humidity
- Light level
- Pump state

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import Pin
import dht
import network
import socket
import time

SOIL_PIN = 34
DHT_PIN  = 14
LDR_PIN  = 35
PUMP_PIN = 4
LED_PIN  = 5

SSID     = "YourWiFiName"
PASSWORD = "YourPassword"
DRY_LIM  = 35

sensor = dht.DHT11(Pin(DHT_PIN))

def setup():
    oledSetup()
    analogPin(SOIL_PIN)
    analogPin(LDR_PIN)
    for pin in [PUMP_PIN, LED_PIN]:
        pinMode(pin, OUTPUT)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    oledClear()
    oledText("Connecting WiFi...", 0, 28)
    oledShow()
    for _ in range(20):
        if wlan.isconnected(): break
        time.sleep(0.5)
    ip = wlan.ifconfig()[0] if wlan.isconnected() else "No WiFi"
    print(f"IP: {ip}")
    return ip

def make_html(soil, temp, hum, light, pumping):
    soil_c = "#4CAF50" if soil > 50 else ("#FF9800" if soil > DRY_LIM else "#f44336")
    return f"""<!DOCTYPE html>
<html>
<head>
  <title>Plant Monitor</title>
  <meta http-equiv="refresh" content="5">
  <style>
    body {{ font-family:Arial; text-align:center; background:#f0f4f0; }}
    h1   {{ color:#2e7d32; }}
    .card {{ display:inline-block; margin:10px; padding:20px; background:white;
             border-radius:12px; box-shadow:0 2px 8px #ccc; width:140px; }}
    .val  {{ font-size:2em; font-weight:bold; }}
  </style>
</head>
<body>
  <h1>🌿 Plant Monitor</h1>
  <div class="card"><div>🌱 Soil</div>
    <div class="val" style="color:{soil_c}">{soil}%</div></div>
  <div class="card"><div>🌡️ Temp</div>
    <div class="val">{temp:.1f}°C</div></div>
  <div class="card"><div>💧 Humid</div>
    <div class="val">{hum:.0f}%</div></div>
  <div class="card"><div>☀️ Light</div>
    <div class="val">{light}%</div></div>
  <div class="card"><div>🚿 Pump</div>
    <div class="val" style="color:{'#2196F3' if pumping else '#9E9E9E'}">
    {'ON' if pumping else 'OFF'}</div></div>
</body></html>"""

def draw_oled(soil, temp, hum, light, pumping, ip):
    oledClear()
    oledText("Plant Monitor",                             0,  0)
    oledText("-" * 21,                                    0,  9)
    oledText(f"Soil : {soil:3d}%  {'DRY!' if soil < DRY_LIM else 'OK  '}", 0, 18)
    oledText(f"Temp : {temp:.1f}C  Hum:{hum:.0f}%",      0, 28)
    oledText(f"Light: {light:3d}%",                       0, 38)
    oledText(f"Pump : {'ON 💧' if pumping else 'OFF'}",   0, 48)
    oledShow()

def main():
    setup()
    ip      = connect_wifi()
    pumping = False

    oledClear()
    oledText("Plant Monitor", 4, 0)
    oledText(f"IP:{ip}", 0, 20)
    oledText("Open browser!", 4, 40)
    oledShow()
    time.sleep(2)

    server = socket.socket()
    server.bind(('', 80))
    server.listen(3)
    server.settimeout(0.1)
    print(f"Web dashboard: http://{ip}")

    while True:
        soil  = 100 - analogPercent(SOIL_PIN)
        light = analogPercent(LDR_PIN)
        try:
            sensor.measure()
            temp = sensor.temperature()
            hum  = sensor.humidity()
        except OSError:
            temp, hum = 0.0, 0.0

        pumping = soil < DRY_LIM
        digitalWrite(PUMP_PIN, 1 if pumping else 0)
        digitalWrite(LED_PIN,  1 if pumping else 0)

        draw_oled(soil, temp, hum, light, pumping, ip)
        print(f"Soil:{soil}%  Temp:{temp}°C  Hum:{hum}%  Light:{light}%  Pump:{'ON' if pumping else 'OFF'}")

        try:
            conn, _ = server.accept()
            conn.recv(1024)
            html = make_html(soil, temp, hum, light, pumping)
            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html)
            conn.close()
        except OSError:
            pass

        time.sleep(3)

def cleanup():
    digitalWrite(PUMP_PIN, 0)
    digitalWrite(LED_PIN,  0)
    oledClear()
    oledText("Monitor OFF", 18, 28)
    oledShow()
    print("Plant Monitor Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Plant Monitor          │
│ ─────────────────────  │
│ Soil :  24%  DRY!      │
│ Temp : 29.0C  Hum:58%  │
│ Light:  68%            │
│ Pump : ON 💧           │
└────────────────────────┘
```

---

## 10. Multi-Sensor Security Robot

### 🎯 Objective
Build a security patrol robot that combines obstacle avoidance, flame detection, gas detection, and PIR motion alert — all displayed live on OLED.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| HC-SR04 Ultrasonic Sensor | 1 |
| Flame Sensor (Analog) | 1 |
| MQ-2 Gas Sensor (Analog) | 1 |
| PIR Motion Sensor | 1 |
| DC Motors + L298N Driver | 2 |
| Buzzer | 1 |
| Red LED | 1 |
| Chassis + Wheels | 1 Set |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| TRIG_PIN | 5 | Ultrasonic Trigger |
| ECHO_PIN | 18 | Ultrasonic Echo |
| FLAME_PIN | 34 | Flame Sensor Analog |
| GAS_PIN | 35 | MQ-2 Gas Sensor Analog |
| PIR_PIN | 23 | PIR Motion Sensor |
| LEFT_MOTOR_1 | 12 | Left Motor Forward |
| LEFT_MOTOR_2 | 13 | Left Motor Backward |
| RIGHT_MOTOR_1 | 2 | Right Motor Forward |
| RIGHT_MOTOR_2 | 4 | Right Motor Backward |
| BUZZER_PIN | 14 | Alert Buzzer |
| RED_LED | 15 | Threat Alert LED |

### 💡 Security Logic
| Threat | Condition | Robot Action |
|---|---|---|
| OBSTACLE | Distance < 20 cm | Stop + Turn Right |
| FIRE | Flame > 30% | Stop + Alarm |
| GAS | Gas > 35% | Stop + Alarm |
| MOTION | PIR HIGH | Alarm + Flash LED |
| SAFE | All clear | Patrol Forward |

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
from machine import Pin
import time

TRIG_PIN      = 5
ECHO_PIN      = 18
FLAME_PIN     = 34
GAS_PIN       = 35
PIR_PIN       = 23
LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4
BUZZER_PIN    = 14
RED_LED       = 15

SAFE_DIST  = 20
FIRE_LIMIT = 30
GAS_LIMIT  = 35

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

def setup():
    oledSetup()
    analogPin(FLAME_PIN)
    analogPin(GAS_PIN)
    pinMode(PIR_PIN,       INPUT)
    pinMode(BUZZER_PIN,    OUTPUT)
    pinMode(RED_LED,       OUTPUT)
    for pin in [LEFT_MOTOR_1, LEFT_MOTOR_2, RIGHT_MOTOR_1, RIGHT_MOTOR_2]:
        pinMode(pin, OUTPUT)

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

def move_forward(): drive(1, 0, 1, 0)
def turn_right():   drive(1, 0, 0, 1)
def stop_robot():   drive(0, 0, 0, 0)

def threat_alarm(count=6):
    for _ in range(count):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(RED_LED,    1)
        time.sleep(0.07)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(RED_LED,    0)
        time.sleep(0.07)

def draw_dashboard(dist, flame, gas, motion, status, threat):
    oledClear()
    oledText("Security Robot",          0,  0)
    oledText("-" * 21,                  0,  9)
    oledText(f"Dist  : {dist:5.1f} cm", 0, 18)
    oledText(f"Flame : {flame:3d}%  Gas:{gas:3d}%", 0, 28)
    oledText(f"Motion: {'YES 🚨' if motion else 'No  ✅'}", 0, 38)
    oledText(f"Mode  : {status}",        0, 48)
    if threat:
        oledText(">>> THREAT DETECTED <<<", 0, 56)
    oledShow()

def main():
    setup()
    patrol_count = 0
    threat_count = 0
    print("Multi-Sensor Security Robot Started")

    while True:
        dist   = get_distance()
        flame  = 100 - analogPercent(FLAME_PIN)
        gas    = analogPercent(GAS_PIN)
        motion = digitalRead(PIR_PIN)

        threat = False
        status = "PATROLLING 🤖"

        # Priority threat checks
        if flame > FIRE_LIMIT:
            status = "FIRE!  🔥"
            threat = True
            stop_robot()
            threat_alarm(10)
            threat_count += 1
            print(f"🔥 FIRE DETECTED! Flame:{flame}%")

        elif gas > GAS_LIMIT:
            status = "GAS!   ⛽"
            threat = True
            stop_robot()
            threat_alarm(8)
            threat_count += 1
            print(f"⛽ GAS LEAK! Gas:{gas}%")

        elif motion == 1:
            status = "MOTION 🚨"
            threat = True
            stop_robot()
            threat_alarm(5)
            threat_count += 1
            print("🚨 MOTION DETECTED!")

        elif dist < SAFE_DIST:
            status = "OBSTACLE ⛔"
            stop_robot()
            time.sleep(0.2)
            turn_right()
            time.sleep(0.4)
            print(f"⛔ Obstacle at {dist:.1f}cm — Avoiding")

        else:
            status = "PATROLLING 🤖"
            move_forward()
            patrol_count += 1

        if not threat:
            digitalWrite(BUZZER_PIN, 0)
            digitalWrite(RED_LED,    0)

        draw_dashboard(dist, flame, gas, motion, status, threat)
        print(f"Dist:{dist:.1f}  Flame:{flame}%  Gas:{gas}%  PIR:{'Y' if motion else 'N'}  {status.strip()}  Threats:{threat_count}")
        time.sleep(0.2)

def cleanup():
    stop_robot()
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(RED_LED,    0)
    oledClear()
    oledText("Robot OFF", 26, 28)
    oledShow()
    print("Security Robot Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Security Robot         │
│ ─────────────────────  │
│ Dist  :  42.5 cm       │
│ Flame :  12%  Gas: 18% │
│ Motion: No  ✅         │
│ Mode  : PATROLLING 🤖  │
└────────────────────────┘
```

---

## 📚 Quick Reference — Exhibition Projects

### Multi-Sensor Read Pattern
```python
# Always wrap DHT11 in try/except
try:
    sensor.measure()
    temp = sensor.temperature()
    hum  = sensor.humidity()
except OSError:
    temp, hum = 0.0, 0.0

# Analog sensors
soil  = 100 - analogPercent(SOIL_PIN)   # Inverted sensors
flame = 100 - analogPercent(FLAME_PIN)
gas   = analogPercent(GAS_PIN)           # Direct sensors
light = analogPercent(LDR_PIN)
```

### Pump / Relay Control
```python
# Pump ON when condition met, OFF otherwise
pumping = moisture < DRY_LIMIT
digitalWrite(PUMP_PIN, 1 if pumping else 0)
```

### OLED Dashboard Template
```python
def draw_dashboard(val1, val2, val3, status):
    oledClear()
    oledText("Project Title",   0,  0)   # Header
    oledText("-" * 21,          0,  9)   # Divider
    oledText(f"Sensor1: {val1}", 0, 18)  # Row 1
    oledText(f"Sensor2: {val2}", 0, 28)  # Row 2
    oledText(f"Sensor3: {val3}", 0, 38)  # Row 3
    oledText(status,             0, 52)  # Status bar
    oledShow()                           # ALWAYS last
```

### Wi-Fi Web Server Pattern
```python
import network, socket

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected(): time.sleep(0.5)

server = socket.socket()
server.bind(('', 80))
server.listen(3)
server.settimeout(0.1)   # Non-blocking

# In loop:
try:
    conn, _ = server.accept()
    conn.recv(1024)
    conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + HTML)
    conn.close()
except OSError:
    pass   # No request this cycle
```

### Escalating Alert Pattern
```python
if value > EMERGENCY_LIMIT:
    beep(0.05, 0.05, 15)   # Rapid continuous
elif value > DANGER_LIMIT:
    beep(0.1,  0.1,  8)    # Fast
elif value > CAUTION_LIMIT:
    beep(0.3,  0.5,  2)    # Slow warning
else:
    all_off()               # Silent
```

### systemio Pattern
```python
from systemio import run

def setup():   pass   # Initialize all hardware once
def main():    pass   # Main control loop
def cleanup(): pass   # Safe shutdown on Ctrl+C

run(main, cleanup)
```

---

*All projects designed for ESP32 with MicroPython using Thonny IDE.*
*Custom `systemio` library required — `from digital import *` / `from analog import *` / `from oled import *`*
*These projects are suitable for STEM exhibitions, science fairs, and project presentations.*

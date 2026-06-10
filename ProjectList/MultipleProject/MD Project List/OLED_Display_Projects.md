# 📟 OLED Display Projects — ESP32 MicroPython

> All projects use the `systemio` library with `setup()`, `main()`, and `cleanup()` functions.
> OLED display uses the `oled` module from the `systemio` library ecosystem.
> Code style follows the `from digital import *` / `from analog import *` / `from oled import *` pattern.

---

## Table of Contents

1. [Digital Counter](#1-digital-counter)
2. [Temperature Display](#2-temperature-display)
3. [Moisture Level Display](#3-moisture-level-display)
4. [Robot Status Dashboard](#4-robot-status-dashboard)
5. [Digital Clock using RTC](#5-digital-clock-using-rtc)
6. [Weather Station](#6-weather-station)
7. [Speedometer Display](#7-speedometer-display)
8. [Sensor Data Logger](#8-sensor-data-logger)
9. [Wi-Fi Status Monitor](#9-wi-fi-status-monitor)
10. [Touch Menu System](#10-touch-menu-system)

---

## OLED Quick Setup

> All OLED projects use the SSD1306 128×64 I2C display connected to the ESP32.

### 📌 OLED Pin Connection (All Projects)
| OLED Pin | ESP32 GPIO | Description |
|---|---|---|
| VCC | 3.3V | Power |
| GND | GND | Ground |
| SDA | 21 | I2C Data |
| SCL | 22 | I2C Clock |

### 🖥️ OLED Import Pattern
```python
from oled import oledSetup, oledClear, oledText, oledShow, oledLine, oledRect, oledFill
```

---

## 1. Digital Counter

### 🎯 Objective
Display a live count on the OLED screen — increment with one button, decrement with another, and reset with a third.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| Push Button | 3 |
| 10kΩ Pull-up Resistor | 3 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| BTN_UP | 4 | Increment Button |
| BTN_DN | 5 | Decrement Button |
| BTN_RST | 18 | Reset Button |

### 💡 Working Principle
- UP button → count increases by 1
- DOWN button → count decreases by 1
- RESET button → count returns to 0
- OLED shows big centered count value and button hints

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from digital import pinMode, digitalWrite, digitalRead, INPUT
from systemio import run
import time

BTN_UP  = 4
BTN_DN  = 5
BTN_RST = 18

def setup():
    oledSetup()
    pinMode(BTN_UP,  INPUT)
    pinMode(BTN_DN,  INPUT)
    pinMode(BTN_RST, INPUT)

def draw_counter(count):
    oledClear()
    oledText("Digital Counter", 0, 0)
    oledText("-" * 21,          0, 10)
    oledText(f"Count: {count}", 20, 28)
    oledText("+ UP  - DN  R RST", 0, 52)
    oledShow()

def main():
    setup()
    count     = 0
    last_up   = 0
    last_dn   = 0
    last_rst  = 0

    draw_counter(count)
    print("Digital Counter Started")

    while True:
        up  = digitalRead(BTN_UP)
        dn  = digitalRead(BTN_DN)
        rst = digitalRead(BTN_RST)

        if last_up == 0 and up == 1:
            count += 1
            print(f"Count: {count}")
            draw_counter(count)

        if last_dn == 0 and dn == 1:
            count -= 1
            print(f"Count: {count}")
            draw_counter(count)

        if last_rst == 0 and rst == 1:
            count = 0
            print("Counter Reset")
            draw_counter(count)

        last_up  = up
        last_dn  = dn
        last_rst = rst
        time.sleep(0.05)

def cleanup():
    oledClear()
    oledText("System OFF", 24, 28)
    oledShow()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Digital Counter        │
│ ─────────────────────  │
│                        │
│      Count: 7          │
│                        │
│  + UP  - DN  R RST     │
└────────────────────────┘
```

---

## 2. Temperature Display

### 🎯 Objective
Read temperature and humidity from a DHT11 sensor and display both values on the OLED screen with status.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| DHT11 Sensor | 1 |
| 10kΩ Pull-up Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| DHT_PIN | 14 | DHT11 Data Pin |

### 💡 Working Principle
- DHT11 reads temperature (°C / °F) and humidity every 2 seconds
- OLED shows both values with a comfort status label
- Status: COOL / NORMAL / WARM / HOT based on temperature range

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from systemio import run
from machine import Pin
import dht
import time

DHT_PIN = 14

sensor = dht.DHT11(Pin(DHT_PIN))

def setup():
    oledSetup()

def get_status(temp):
    if temp < 20:   return "COOL  🧊"
    elif temp < 28: return "NORMAL ✅"
    elif temp < 35: return "WARM  🌤️"
    else:           return "HOT   🔥"

def draw_display(temp_c, temp_f, hum, status):
    oledClear()
    oledText("Temp & Humidity",   0,  0)
    oledText("-" * 21,            0, 10)
    oledText(f"Temp : {temp_c:.1f} C / {temp_f:.1f} F", 0, 20)
    oledText(f"Humid: {hum:.1f} %",                      0, 32)
    oledText(f"Status: {status}",                         0, 44)
    oledShow()

def main():
    setup()
    print("Temperature Display Started")

    while True:
        try:
            sensor.measure()
            temp_c = sensor.temperature()
            temp_f = temp_c * (9 / 5) + 32.0
            hum    = sensor.humidity()
            status = get_status(temp_c)

            draw_display(temp_c, temp_f, hum, status)
            print(f"Temp: {temp_c}°C  Hum: {hum}%  Status: {status}")

        except OSError:
            oledClear()
            oledText("Sensor Error!", 16, 28)
            oledShow()
            print("❌ Sensor Read Error")

        time.sleep(2)

def cleanup():
    oledClear()
    oledText("System OFF", 24, 28)
    oledShow()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Temp & Humidity        │
│ ─────────────────────  │
│ Temp : 28.0 C / 82.4 F │
│ Humid: 55.0 %          │
│ Status: NORMAL ✅      │
│                        │
└────────────────────────┘
```

---

## 3. Moisture Level Display

### 🎯 Objective
Display soil moisture percentage and plant health status on the OLED with a visual progress bar.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| Soil Moisture Sensor (Analog) | 1 |
| LED (optional alert) | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| SOIL_PIN | 34 | Soil Moisture Sensor |
| LED_PIN | 4 | Alert LED |

### 💡 Working Principle
- Moisture sensor reads analog value → converted to percentage
- OLED shows percentage, a bar graph, and status label
- LED turns ON when soil is dry (needs watering)
- Bar graph fills proportionally with moisture level

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow, oledRect, oledFill
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

SOIL_PIN   = 34
LED_PIN    = 4
DRY_LIMIT  = 30
WET_LIMIT  = 70

def setup():
    oledSetup()
    analogPin(SOIL_PIN)
    pinMode(LED_PIN, OUTPUT)

def draw_bar(moisture, y):
    # Outer frame: full width bar
    oledRect(0, y, 128, 10)
    # Inner fill: proportional to moisture
    fill_w = int((moisture / 100) * 124)
    if fill_w > 0:
        oledFill(2, y + 2, fill_w, 6)

def get_status(moisture):
    if moisture < DRY_LIMIT:  return "DRY   — Water Now!"
    elif moisture < WET_LIMIT: return "OK    — Healthy"
    else:                      return "WET   — Overwatered"

def draw_display(moisture, status):
    oledClear()
    oledText("Soil Moisture",   0,  0)
    oledText("-" * 21,          0, 10)
    oledText(f"Level: {moisture:3d}%",  0, 20)
    draw_bar(moisture,              32)
    oledText(status,            0, 46)
    oledShow()

def main():
    setup()
    print("Moisture Level Display Started")

    while True:
        moisture = 100 - analogPercent(SOIL_PIN)
        status   = get_status(moisture)

        draw_display(moisture, status)
        digitalWrite(LED_PIN, 1 if moisture < DRY_LIMIT else 0)
        print(f"Moisture: {moisture}%  Status: {status}")

        time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN, 0)
    oledClear()
    oledText("System OFF", 24, 28)
    oledShow()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Soil Moisture          │
│ ─────────────────────  │
│ Level:  45%            │
│ [████████████░░░░░░░░] │
│                        │
│ OK    — Healthy        │
└────────────────────────┘
```

---

## 4. Robot Status Dashboard

### 🎯 Objective
Display a live robot status dashboard on OLED showing motor state, sensor readings, and battery level.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| IR/Ultrasonic Sensor | 1 |
| DC Motors + L298N Driver | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| TRIG_PIN | 5 | Ultrasonic Trigger |
| ECHO_PIN | 18 | Ultrasonic Echo |
| LEFT_MOTOR_1 | 12 | Left Motor |
| RIGHT_MOTOR_1 | 2 | Right Motor |

### 💡 Dashboard Layout
```
Line 0: Title bar
Line 1: Separator
Line 2: Motor status (L/R direction)
Line 3: Distance from sensor
Line 4: Speed (PWM %)
Line 5: System uptime
```

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import Pin
import time

TRIG_PIN      = 5
ECHO_PIN      = 18
LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

def setup():
    oledSetup()
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

def move_forward(): drive(1, 0, 1, 0); return "FWD"
def turn_right():   drive(1, 0, 0, 1); return "RIGHT"
def stop_robot():   drive(0, 0, 0, 0); return "STOP"

def draw_dashboard(status, dist, uptime):
    oledClear()
    oledText("Robot Dashboard",    0,  0)
    oledText("-" * 21,             0, 10)
    oledText(f"Motion : {status}", 0, 20)
    oledText(f"Dist   : {dist:.1f} cm", 0, 30)
    oledText(f"Safe   : {'YES' if dist > 20 else 'NO !'}", 0, 40)
    oledText(f"Uptime : {uptime}s",  0, 52)
    oledShow()

def main():
    setup()
    start_time = time.time()
    print("Robot Status Dashboard Started")

    while True:
        dist    = get_distance()
        uptime  = int(time.time() - start_time)

        if dist < 15:
            status = turn_right()
            time.sleep(0.4)
        elif dist > 20:
            status = move_forward()
        else:
            status = stop_robot()

        draw_dashboard(status, dist, uptime)
        print(f"Status: {status}  Dist: {dist:.1f}cm  Up: {uptime}s")
        time.sleep(0.2)

def cleanup():
    stop_robot()
    oledClear()
    oledText("Robot OFF", 24, 28)
    oledShow()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Robot Dashboard        │
│ ─────────────────────  │
│ Motion : FWD           │
│ Dist   : 45.2 cm       │
│ Safe   : YES           │
│ Uptime : 12s           │
└────────────────────────┘
```

---

## 5. Digital Clock using RTC

### 🎯 Objective
Display a real-time digital clock on the OLED using the ESP32's built-in RTC module.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| Push Button (Set Time) | 2 |
| 10kΩ Pull-up Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| BTN_H | 4 | Increment Hour Button |
| BTN_M | 5 | Increment Minute Button |

### 💡 Working Principle
- ESP32 RTC stores current time (set at startup or via buttons)
- Clock updates every second on OLED
- BTN_H increments hour, BTN_M increments minute
- Displays date, time in HH:MM:SS, and day of week

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from digital import pinMode, digitalRead, INPUT
from systemio import run
from machine import RTC
import time

BTN_H = 4
BTN_M = 5

rtc  = RTC()
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def setup():
    oledSetup()
    pinMode(BTN_H, INPUT)
    pinMode(BTN_M, INPUT)
    # Set initial time: (year, month, day, weekday, hour, min, sec, subsec)
    rtc.datetime((2025, 1, 1, 2, 9, 0, 0, 0))

def get_time():
    dt  = rtc.datetime()
    return dt[0], dt[1], dt[2], dt[3], dt[4], dt[5], dt[6]

def draw_clock(year, month, day, weekday, hour, minute, second):
    oledClear()
    oledText("Digital Clock",                         0,  0)
    oledText("-" * 21,                                0, 10)
    oledText(f"{DAYS[weekday]}  {day:02d}/{month:02d}/{year}", 0, 20)
    oledText(f"  {hour:02d} : {minute:02d} : {second:02d}",   8, 34)
    oledText("-" * 21,                                0, 48)
    oledText("H+ btn1  M+ btn2",                      0, 54)
    oledShow()

def main():
    setup()
    last_h = 0
    last_m = 0
    print("Digital Clock Started")

    while True:
        btn_h = digitalRead(BTN_H)
        btn_m = digitalRead(BTN_M)

        year, month, day, weekday, hour, minute, second = get_time()

        # Increment hour
        if last_h == 0 and btn_h == 1:
            hour = (hour + 1) % 24
            rtc.datetime((year, month, day, weekday, hour, minute, 0, 0))
            print(f"Hour set to: {hour}")

        # Increment minute
        if last_m == 0 and btn_m == 1:
            minute = (minute + 1) % 60
            rtc.datetime((year, month, day, weekday, hour, minute, 0, 0))
            print(f"Minute set to: {minute}")

        draw_clock(year, month, day, weekday, hour, minute, second)
        print(f"{DAYS[weekday]} {day:02d}/{month:02d}/{year}  {hour:02d}:{minute:02d}:{second:02d}")

        last_h = btn_h
        last_m = btn_m
        time.sleep(1)

def cleanup():
    oledClear()
    oledText("Clock Stopped", 12, 28)
    oledShow()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Digital Clock          │
│ ─────────────────────  │
│ Wed  01/01/2025        │
│    09 : 15 : 42        │
│ ─────────────────────  │
│ H+ btn1  M+ btn2       │
└────────────────────────┘
```

---

## 6. Weather Station

### 🎯 Objective
Display a complete weather station dashboard with temperature, humidity, and heat index on the OLED.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| DHT11 Sensor | 1 |
| LDR Sensor | 1 |
| 10kΩ Resistors | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| DHT_PIN | 14 | DHT11 Data |
| LDR_PIN | 34 | LDR Analog Input |

### 💡 Displayed Metrics
| Row | Metric | Source |
|---|---|---|
| 1 | Temperature °C / °F | DHT11 |
| 2 | Humidity % | DHT11 |
| 3 | Heat Index °C | Calculated |
| 4 | Light Level % | LDR |
| 5 | Conditions | Combined logic |

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from analog import analogPin, analogPercent
from systemio import run
from machine import Pin
import dht
import time

DHT_PIN = 14
LDR_PIN = 34

sensor = dht.DHT11(Pin(DHT_PIN))

def setup():
    oledSetup()
    analogPin(LDR_PIN)

def heat_index(temp, hum):
    # Simplified Steadman heat index
    hi = (-8.78469475556
          + 1.61139411    * temp
          + 2.33854883889 * hum
          - 0.14611605    * temp * hum
          - 0.012308094   * temp ** 2
          - 0.0164248277778 * hum ** 2)
    return round(hi, 1)

def get_condition(temp, hum, light):
    if light > 70 and temp > 28:  return "Sunny & Warm"
    elif light > 70:              return "Sunny & Cool"
    elif hum > 70:                return "Humid / Cloudy"
    elif temp < 20:               return "Cold & Dry"
    else:                         return "Pleasant"

def draw_station(temp_c, temp_f, hum, hi, light, condition):
    oledClear()
    oledText("Weather Station",              0,  0)
    oledText("-" * 21,                       0, 10)
    oledText(f"Temp : {temp_c:.1f}C / {temp_f:.1f}F", 0, 18)
    oledText(f"Humid: {hum:.0f}%   HI: {hi}C",   0, 28)
    oledText(f"Light: {light:3d}%",               0, 38)
    oledText(f"{condition}",                       0, 50)
    oledShow()

def main():
    setup()
    print("Weather Station Started")

    while True:
        try:
            sensor.measure()
            temp_c = sensor.temperature()
            temp_f = temp_c * (9 / 5) + 32.0
            hum    = sensor.humidity()
            hi     = heat_index(temp_c, hum)
            light  = analogPercent(LDR_PIN)
            cond   = get_condition(temp_c, hum, light)

            draw_station(temp_c, temp_f, hum, hi, light, cond)
            print(f"T:{temp_c}°C  H:{hum}%  HI:{hi}  L:{light}%  {cond}")

        except OSError:
            oledClear()
            oledText("Sensor Error", 16, 28)
            oledShow()

        time.sleep(3)

def cleanup():
    oledClear()
    oledText("Station OFF", 20, 28)
    oledShow()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Weather Station        │
│ ─────────────────────  │
│ Temp : 28.0C / 82.4F   │
│ Humid: 65%   HI: 30.2C │
│ Light:  78%            │
│ Sunny & Warm           │
└────────────────────────┘
```

---

## 7. Speedometer Display

### 🎯 Objective
Display a real-time speedometer on the OLED using a rotary encoder or hall effect sensor to measure RPM and speed.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| Hall Effect Sensor / IR Encoder | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| SENSOR_PIN | 5 | Hall / IR Pulse Input |

### 💡 Working Principle
- Each magnet/slot passing the sensor = 1 pulse
- Counts pulses in a 1-second window → RPM
- RPM × wheel circumference → Speed in km/h
- Displays current speed, RPM, and max speed recorded

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from digital import pinMode, digitalRead, INPUT
from systemio import run
import time

SENSOR_PIN      = 5
PULSES_PER_REV  = 1        # Magnets per wheel revolution
WHEEL_CIRC_M    = 0.2      # Wheel circumference in metres

def setup():
    oledSetup()
    pinMode(SENSOR_PIN, INPUT)

def calc_speed(pulses, interval):
    revs   = pulses / PULSES_PER_REV
    dist_m = revs * WHEEL_CIRC_M
    speed_ms  = dist_m / interval
    speed_kmh = speed_ms * 3.6
    rpm       = (revs / interval) * 60
    return round(speed_kmh, 1), round(rpm, 0)

def draw_speedo(speed, rpm, max_speed, total_pulses):
    oledClear()
    oledText("Speedometer",               0,  0)
    oledText("-" * 21,                    0, 10)
    oledText(f"Speed : {speed:5.1f} km/h", 0, 20)
    oledText(f"RPM   : {int(rpm):5d}",     0, 30)
    oledText(f"Max   : {max_speed:5.1f} km/h", 0, 40)
    oledText(f"Pulses: {total_pulses}",    0, 52)
    oledShow()

def main():
    setup()
    max_speed    = 0.0
    total_pulses = 0
    print("Speedometer Display Started")

    while True:
        pulse_count = 0
        last_sensor = 0
        start_t     = time.time()

        # Count pulses for 1 second
        while time.time() - start_t < 1.0:
            sensor = digitalRead(SENSOR_PIN)
            if last_sensor == 0 and sensor == 1:
                pulse_count  += 1
                total_pulses += 1
            last_sensor = sensor

        interval       = time.time() - start_t
        speed, rpm     = calc_speed(pulse_count, interval)
        if speed > max_speed:
            max_speed = speed

        draw_speedo(speed, rpm, max_speed, total_pulses)
        print(f"Speed: {speed} km/h  RPM: {rpm}  Max: {max_speed}")

def cleanup():
    oledClear()
    oledText("Speedo OFF", 20, 28)
    oledShow()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Speedometer            │
│ ─────────────────────  │
│ Speed :  12.5 km/h     │
│ RPM   :   175          │
│ Max   :  18.2 km/h     │
│ Pulses: 324            │
└────────────────────────┘
```

---

## 8. Sensor Data Logger

### 🎯 Objective
Log readings from multiple sensors (temperature, moisture, light) to the OLED and serial monitor with timestamps.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| DHT11 Sensor | 1 |
| Soil Moisture Sensor | 1 |
| LDR Sensor | 1 |
| 10kΩ Resistors | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| DHT_PIN | 14 | DHT11 Data |
| SOIL_PIN | 34 | Soil Moisture |
| LDR_PIN | 35 | LDR Light Sensor |

### 💡 Working Principle
- Reads all 3 sensors every 5 seconds
- OLED cycles through two pages: Page 1 (temp/hum), Page 2 (soil/light)
- Each reading tagged with elapsed time in seconds
- Logs are also printed to serial monitor

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from analog import analogPin, analogPercent
from systemio import run
from machine import Pin
import dht
import time

DHT_PIN  = 14
SOIL_PIN = 34
LDR_PIN  = 35

sensor = dht.DHT11(Pin(DHT_PIN))

def setup():
    oledSetup()
    analogPin(SOIL_PIN)
    analogPin(LDR_PIN)

def draw_page1(temp, hum, ts, log_n):
    oledClear()
    oledText(f"Data Logger #{log_n}", 0,  0)
    oledText("-" * 21,               0, 10)
    oledText(f"Temp  : {temp:.1f} C", 0, 20)
    oledText(f"Humid : {hum:.1f} %",  0, 30)
    oledText(f"Time  : {ts}s",        0, 42)
    oledText("Page 1/2",             88, 54)
    oledShow()

def draw_page2(soil, light, ts, log_n):
    oledClear()
    oledText(f"Data Logger #{log_n}", 0,  0)
    oledText("-" * 21,               0, 10)
    oledText(f"Soil  : {soil:3d} %",  0, 20)
    oledText(f"Light : {light:3d} %", 0, 30)
    oledText(f"Time  : {ts}s",        0, 42)
    oledText("Page 2/2",             88, 54)
    oledShow()

def main():
    setup()
    start_t = time.time()
    log_n   = 0
    print("Sensor Data Logger Started")
    print(f"{'Log':>4} | {'Time':>5} | {'Temp':>5} | {'Hum':>4} | {'Soil':>4} | {'Light':>5}")
    print("-" * 45)

    while True:
        log_n += 1
        ts     = int(time.time() - start_t)

        try:
            sensor.measure()
            temp = sensor.temperature()
            hum  = sensor.humidity()
        except OSError:
            temp, hum = 0.0, 0.0

        soil  = 100 - analogPercent(SOIL_PIN)
        light = analogPercent(LDR_PIN)

        draw_page1(temp, hum, ts, log_n)
        time.sleep(2.5)
        draw_page2(soil, light, ts, log_n)
        time.sleep(2.5)

        print(f"{log_n:>4} | {ts:>5} | {temp:>5.1f} | {hum:>4.0f} | {soil:>4} | {light:>5}")

def cleanup():
    oledClear()
    oledText("Logger Stopped", 8, 28)
    oledShow()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display (Page 1)
```
┌────────────────────────┐
│ Data Logger #5         │
│ ─────────────────────  │
│ Temp  : 28.0 C         │
│ Humid : 55.0 %         │
│                        │
│ Time  : 25s    Page 1/2│
└────────────────────────┘
```

### 📝 Expected Serial Log
```
 Log | Time  | Temp  |  Hum | Soil | Light
---------------------------------------------
   1 |     5 |  28.0 |   55 |   42 |    75
   2 |    10 |  28.5 |   54 |   40 |    78
```

---

## 9. Wi-Fi Status Monitor

### 🎯 Objective
Connect ESP32 to Wi-Fi and display live network status, IP address, signal strength, and connection time on the OLED.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| Wi-Fi Network | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |

### 💡 Displayed Information
| Row | Info |
|---|---|
| 1 | Network SSID |
| 2 | IP Address |
| 3 | Signal Strength (RSSI dBm) |
| 4 | Status (Connected / Reconnecting) |
| 5 | Uptime since connection |

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow
from systemio import run
import network
import time

SSID     = "YourWiFiName"
PASSWORD = "YourPassword"

def setup():
    oledSetup()

def rssi_label(rssi):
    if rssi > -50:   return "Excellent"
    elif rssi > -65: return "Good"
    elif rssi > -75: return "Fair"
    else:            return "Weak"

def draw_connecting(attempt):
    oledClear()
    oledText("Wi-Fi Monitor",     0,  0)
    oledText("-" * 21,            0, 10)
    oledText("Connecting...",     0, 22)
    oledText(f"Attempt: {attempt}", 0, 34)
    oledText(f"SSID: {SSID[:16]}", 0, 46)
    oledShow()

def draw_connected(ip, rssi, uptime):
    label = rssi_label(rssi)
    oledClear()
    oledText("Wi-Fi Monitor",        0,  0)
    oledText("-" * 21,               0, 10)
    oledText(f"IP: {ip}",            0, 18)
    oledText(f"RSSI: {rssi} dBm",    0, 28)
    oledText(f"Sig : {label}",        0, 38)
    oledText(f"Up  : {uptime}s",      0, 50)
    oledShow()

def draw_disconnected():
    oledClear()
    oledText("Wi-Fi Monitor",    0,  0)
    oledText("-" * 21,           0, 10)
    oledText("DISCONNECTED",     16, 26)
    oledText("Reconnecting...",  8,  40)
    oledShow()

def connect_wifi():
    wlan    = network.WLAN(network.STA_IF)
    wlan.active(True)
    attempt = 0

    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            attempt += 1
            draw_connecting(attempt)
            print(f"Connecting... attempt {attempt}")
            time.sleep(1)

    ip = wlan.ifconfig()[0]
    print(f"Connected! IP: {ip}")
    return wlan

def main():
    setup()
    print("Wi-Fi Status Monitor Started")
    wlan       = connect_wifi()
    connect_t  = time.time()

    while True:
        if wlan.isconnected():
            ip     = wlan.ifconfig()[0]
            rssi   = wlan.status('rssi')
            uptime = int(time.time() - connect_t)
            draw_connected(ip, rssi, uptime)
            print(f"IP: {ip}  RSSI: {rssi}dBm  Up: {uptime}s")
        else:
            draw_disconnected()
            print("Disconnected — Reconnecting...")
            wlan      = connect_wifi()
            connect_t = time.time()

        time.sleep(3)

def cleanup():
    oledClear()
    oledText("Monitor OFF", 18, 28)
    oledShow()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display
```
┌────────────────────────┐
│ Wi-Fi Monitor          │
│ ─────────────────────  │
│ IP: 192.168.1.105      │
│ RSSI: -58 dBm          │
│ Sig : Good             │
│ Up  : 120s             │
└────────────────────────┘
```

---

## 10. Touch Menu System

### 🎯 Objective
Build an interactive menu on the OLED — scroll items with one touch sensor, select with another, and display sub-pages.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| SSD1306 OLED (128×64) | 1 |
| Touch Sensor Module | 2 |
| DHT11 (for sub-page demo) | 1 |
| LDR (for sub-page demo) | 1 |
| 10kΩ Resistors | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| SDA | 21 | OLED I2C Data |
| SCL | 22 | OLED I2C Clock |
| NEXT_TOUCH | 5 | Scroll Next Item |
| SEL_TOUCH | 18 | Select / Back |
| DHT_PIN | 14 | DHT11 Data |
| LDR_PIN | 34 | LDR Analog |

### 💡 Menu Structure
```
MAIN MENU
├── 1. Temperature    → Shows live temp & humidity
├── 2. Light Level    → Shows LDR reading + bar
├── 3. System Info    → Shows uptime & memory
└── 4. Clock          → Shows RTC time
```

### 🖥️ Code

```python
from oled import oledSetup, oledClear, oledText, oledShow, oledRect, oledFill
from analog import analogPin, analogPercent
from digital import pinMode, digitalRead, INPUT
from systemio import run
from machine import Pin, RTC
import dht
import time

NEXT_TOUCH = 5
SEL_TOUCH  = 18
DHT_PIN    = 14
LDR_PIN    = 34

sensor = dht.DHT11(Pin(DHT_PIN))
rtc    = RTC()

MENU_ITEMS = [
    "1. Temperature",
    "2. Light Level",
    "3. System Info",
    "4. Clock",
]

def setup():
    oledSetup()
    analogPin(LDR_PIN)
    pinMode(NEXT_TOUCH, INPUT)
    pinMode(SEL_TOUCH,  INPUT)
    rtc.datetime((2025, 1, 1, 2, 9, 0, 0, 0))

def draw_main_menu(selected):
    oledClear()
    oledText("MAIN MENU",   30,  0)
    oledText("-" * 21,       0, 10)
    for i, item in enumerate(MENU_ITEMS):
        y = 18 + i * 11
        if i == selected:
            oledFill(0, y - 1, 128, 11)   # Highlight bar
            oledText(f"> {item}", 0, y)
        else:
            oledText(f"  {item}", 0, y)
    oledShow()

def page_temperature():
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum  = sensor.humidity()
    except OSError:
        temp, hum = 0.0, 0.0
    oledClear()
    oledText("Temperature",  20,  0)
    oledText("-" * 21,        0, 10)
    oledText(f"Temp : {temp:.1f} C", 0, 22)
    oledText(f"Humid: {hum:.1f} %",  0, 34)
    oledText("[SEL] = Back",          0, 54)
    oledShow()

def page_light():
    light  = analogPercent(LDR_PIN)
    fill_w = int((light / 100) * 124)
    oledClear()
    oledText("Light Level",    18,  0)
    oledText("-" * 21,          0, 10)
    oledText(f"Level: {light:3d}%", 0, 22)
    oledRect(0, 34, 128, 10)
    if fill_w > 0: oledFill(2, 36, fill_w, 6)
    oledText("[SEL] = Back",   0, 54)
    oledShow()

def page_sysinfo():
    import gc
    uptime = int(time.time())
    free   = gc.mem_free()
    oledClear()
    oledText("System Info",   14,  0)
    oledText("-" * 21,         0, 10)
    oledText(f"Uptime: {uptime}s",  0, 22)
    oledText(f"FreeMem: {free}B",   0, 34)
    oledText("ESP32 MicroPython",   0, 44)
    oledText("[SEL] = Back",        0, 54)
    oledShow()

def page_clock():
    dt   = rtc.datetime()
    DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    oledClear()
    oledText("Clock",          38,  0)
    oledText("-" * 21,          0, 10)
    oledText(f"{DAYS[dt[3]]}  {dt[2]:02d}/{dt[1]:02d}/{dt[0]}", 0, 20)
    oledText(f"  {dt[4]:02d} : {dt[5]:02d} : {dt[6]:02d}",      8, 34)
    oledText("[SEL] = Back",    0, 54)
    oledShow()

PAGES = [page_temperature, page_light, page_sysinfo, page_clock]

def main():
    setup()
    selected   = 0
    in_page    = False
    last_next  = 0
    last_sel   = 0

    draw_main_menu(selected)
    print("Touch Menu System Started")

    while True:
        next_t = digitalRead(NEXT_TOUCH)
        sel_t  = digitalRead(SEL_TOUCH)

        if not in_page:
            # Navigate menu
            if last_next == 0 and next_t == 1:
                selected = (selected + 1) % len(MENU_ITEMS)
                draw_main_menu(selected)
                print(f"Menu: {MENU_ITEMS[selected]}")

            if last_sel == 0 and sel_t == 1:
                in_page = True
                print(f"Selected: {MENU_ITEMS[selected]}")
        else:
            # Show page content
            PAGES[selected]()

            # SEL touch = go back
            if last_sel == 0 and sel_t == 1:
                in_page = False
                draw_main_menu(selected)
                print("Back to Main Menu")

        last_next = next_t
        last_sel  = sel_t
        time.sleep(0.1)

def cleanup():
    oledClear()
    oledText("Menu OFF", 28, 28)
    oledShow()
    print("System Stopped")

run(main, cleanup)
```

### 📝 Expected OLED Display (Main Menu)
```
┌────────────────────────┐
│      MAIN MENU         │
│ ─────────────────────  │
│ ████████████████████   │
│ > 1. Temperature       │
│   2. Light Level       │
│   3. System Info       │
│   4. Clock             │
└────────────────────────┘
```

### 📝 Expected OLED Display (Temperature Page)
```
┌────────────────────────┐
│    Temperature         │
│ ─────────────────────  │
│                        │
│ Temp : 28.0 C          │
│ Humid: 55.0 %          │
│                        │
│ [SEL] = Back           │
└────────────────────────┘
```

---

## 📚 Quick Reference — OLED Functions

### Setup & Display
```python
from oled import oledSetup, oledClear, oledText, oledShow
from oled import oledLine, oledRect, oledFill

oledSetup()              # Initialize OLED (I2C: SDA=21, SCL=22)
oledClear()              # Clear display buffer
oledShow()               # Push buffer to screen (ALWAYS call after drawing)
```

### Drawing Text
```python
oledText("Hello",  x, y)   # Draw text at position (x=0–127, y=0–63)
oledText(f"Temp: {temp:.1f}°C", 0, 20)   # f-strings supported
```

### Drawing Shapes
```python
oledLine(x1, y1, x2, y2)      # Draw line
oledRect(x, y, width, height)  # Draw rectangle outline
oledFill(x, y, width, height)  # Draw filled rectangle (highlight bar)
```

### Standard OLED Layout (128×64)
```
Y=0   ─ Title bar
Y=10  ─ Separator line
Y=18  ─ Data row 1
Y=28  ─ Data row 2
Y=38  ─ Data row 3
Y=48  ─ Data row 4
Y=56  ─ Status / hint bar
```

### Always Call oledShow()
```python
# ❌ WRONG — changes won't appear
oledClear()
oledText("Hello", 0, 0)

# ✅ CORRECT — always end with oledShow()
oledClear()
oledText("Hello", 0, 0)
oledShow()              # Flush buffer to screen
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
*Custom `systemio` library required — `from oled import *` / `from digital import *` / `from analog import *`*

# ESP32 — 60 LCD Projects Reference
### 30 Analog + 30 Digital | I2C LCD | systemio Library

> **Import pattern used in every project:**
> ```python
> from analog import analogPin, analogRead, analogPercent, analogVoltage, analogAverage
> from digital import pinMode, digitalWrite, digitalRead, blink, pwmSetup, pwmWrite, pwmStop
> from digital import INPUT_PULLUP, OUTPUT
> from systemio import run
> from machine import I2C, Pin
> from i2c_lcd import I2cLcd
> import time
> ```
> **LCD init (same for all projects):**
> ```python
> i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
> lcd = I2cLcd(i2c, 0x27, 2, 16)
> ```

---

## Table of Contents

**Analog Projects (A01–A30)**
A01 Potentiometer Display · A02 LDR Light Meter · A03 Voltage Meter · A04 Soil Moisture Monitor · A05 Temperature Display (LM35) · A06 Sound Level Meter · A07 POT Bar Graph · A08 LDR Auto Brightness · A09 Averaged Sensor Reading · A10 Dual Sensor Dashboard · A11 POT Servo Angle Display · A12 Water Level Indicator · A13 Gas Sensor Alert · A14 Rain Sensor Monitor · A15 IR Distance Display · A16 Flex Sensor Angle · A17 Force Sensor Scale · A18 Turbidity Meter · A19 UV Index Display · A20 Vibration Level Monitor · A21 Heart Rate Placeholder · A22 POT Frequency Generator · A23 Threshold Crossing Counter · A24 Min/Max Logger · A25 Analog Tachometer · A26 Battery Voltage Monitor · A27 Dual Threshold Alert · A28 Sensor Percentage Bargraph · A29 Smoothed Trend Display · A30 Multi-Sensor Summary

**Digital Projects (D01–D30)**
D01 LED ON/OFF Button · D02 Toggle LED Button · D03 LED Blink Rate Control · D04 Button Counter · D05 Debounced Button · D06 PWM Brightness Control · D07 Traffic Light · D08 Buzzer Alarm · D09 7-Segment Digit Display · D10 Button Hold Timer · D11 Morse Code Blinker · D12 PIR Motion Detector · D13 Reed Switch Door Sensor · D14 Tilt Sensor Alert · D15 Digital Dice · D16 Reaction Timer · D17 Up/Down Counter · D18 PWM Fade In/Out · D19 Shift Register LED Bar · D20 Buzzer Melody · D21 Touch Sensor Toggle · D22 Relay Controller · D23 Dual Button Logic Gate · D24 LED Chaser · D25 Button Combo Lock · D26 Stopwatch · D27 PWM RGB LED Color Cycler · D28 Edge Detector · D29 Auto Night Light (Digital Sensor) · D30 System Uptime Display

---

---

# ANALOG PROJECTS

---

## A01 — Potentiometer Display

**Objective:** Read a potentiometer and show raw value and percentage on LCD.  
**Components:** Potentiometer, I2C LCD  
**Pin:** POT → GPIO 34

```python
from analog import analogPin, analogRead, analogPercent
from digital import pinMode
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

POT_PIN = 34

def setup():
    analogPin(POT_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        raw = analogRead(POT_PIN)
        pct = analogPercent(POT_PIN)
        lcd.move_to(0, 0)
        lcd.putstr(f"Raw : {raw:4d}    ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Knob: {pct:3d} %    ")
        time.sleep_ms(300)

def cleanup():
    lcd.clear()
    lcd.putstr("Stopped")

run(main, cleanup)
```

**Expected Output:**
```
Raw : 2048
Knob:  50 %
```

---

## A02 — LDR Light Meter

**Objective:** Display ambient light level as percentage.  
**Components:** LDR + 10kΩ resistor to GND, I2C LCD  
**Pin:** LDR → GPIO 35

```python
from analog import analogPin, analogPercent
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

LDR_PIN = 35

def setup():
    analogPin(LDR_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        light = analogPercent(LDR_PIN)
        label = "Bright" if light > 60 else ("Medium" if light > 30 else "Dark  ")
        lcd.move_to(0, 0)
        lcd.putstr(f"Light: {light:3d} %   ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Level: {label}   ")
        time.sleep_ms(400)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Light:  72 %
Level: Bright
```

---

## A03 — Voltage Meter

**Objective:** Display the voltage at an analog pin (0–3.3V).  
**Components:** Potentiometer or any 0–3.3V source, I2C LCD  
**Pin:** Signal → GPIO 34

```python
from analog import analogPin, analogVoltage
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

SIG_PIN = 34

def setup():
    analogPin(SIG_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        v = analogVoltage(SIG_PIN)
        bar_len = int((v / 3.3) * 16)
        bar = "#" * bar_len + "-" * (16 - bar_len)
        lcd.move_to(0, 0)
        lcd.putstr(f"Voltage: {v:.3f}V  ")
        lcd.move_to(0, 1)
        lcd.putstr(bar)
        time.sleep_ms(300)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Voltage: 1.650V
########--------
```

---

## A04 — Soil Moisture Monitor

**Objective:** Read soil moisture sensor and display status.  
**Components:** Capacitive soil moisture sensor, I2C LCD  
**Pin:** Sensor → GPIO 34  
**Note:** Sensor reads lower when wet. Use `100 - percent` for intuitive display.

```python
from analog import analogPin, analogPercent
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

SOIL_PIN = 34

def setup():
    analogPin(SOIL_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        raw_pct  = analogPercent(SOIL_PIN)
        moisture = 100 - raw_pct          # invert: low reading = wet
        if moisture > 60:
            status = "Wet     "
        elif moisture > 30:
            status = "Moderate"
        else:
            status = "Dry!    "
        lcd.move_to(0, 0)
        lcd.putstr(f"Moisture:{moisture:3d}%  ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Soil : {status}")
        time.sleep_ms(500)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Moisture: 75%
Soil : Wet
```

---

## A05 — Temperature Display (LM35)

**Objective:** Convert LM35 voltage output to temperature in °C and °F.  
**Components:** LM35 temperature sensor, I2C LCD  
**Pin:** LM35 VOUT → GPIO 34  
**Formula:** Temp °C = Voltage × 100

```python
from analog import analogPin, analogVoltage
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

TEMP_PIN = 34

def setup():
    analogPin(TEMP_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        volt   = analogVoltage(TEMP_PIN)
        temp_c = round(volt * 100, 1)
        temp_f = round(temp_c * 9 / 5 + 32, 1)
        lcd.move_to(0, 0)
        lcd.putstr(f"Temp: {temp_c:5.1f} C  ")
        lcd.move_to(0, 1)
        lcd.putstr(f"      {temp_f:5.1f} F  ")
        time.sleep_ms(500)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Temp:  28.5 C
       83.3 F
```

---

## A06 — Sound Level Meter

**Objective:** Read sound sensor microphone and display dB estimate.  
**Components:** Analog sound sensor (KY-037 AO pin), I2C LCD  
**Pin:** AO → GPIO 34

```python
from analog import analogPin, analogRead, analogPercent
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

MIC_PIN = 34

def setup():
    analogPin(MIC_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        level = analogPercent(MIC_PIN)
        bar   = "#" * (level // 6) + "-" * (16 - level // 6)
        tag   = "LOUD!  " if level > 70 else ("Medium " if level > 40 else "Quiet  ")
        lcd.move_to(0, 0)
        lcd.putstr(f"Sound: {level:3d}% {tag}")
        lcd.move_to(0, 1)
        lcd.putstr(bar[:16])
        time.sleep_ms(100)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Sound:  45% Medium
#######---------
```

---

## A07 — Potentiometer Bar Graph

**Objective:** Show a live 16-character bar graph of potentiometer position.  
**Components:** Potentiometer, I2C LCD  
**Pin:** POT → GPIO 34

```python
from analog import analogPin, analogPercent
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

POT_PIN = 34

def setup():
    analogPin(POT_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def bar(pct, width=16):
    filled = int(pct / 100 * width)
    return "#" * filled + "-" * (width - filled)

def main():
    setup()
    while True:
        pct = analogPercent(POT_PIN)
        lcd.move_to(0, 0)
        lcd.putstr(f"  POT: {pct:3d}%     ")
        lcd.move_to(0, 1)
        lcd.putstr(bar(pct))
        time.sleep_ms(100)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
  POT:  63%
##########------
```

---

## A08 — LDR Auto Brightness (PWM LED)

**Objective:** Dim an LED automatically based on ambient light level.  
**Components:** LDR + 10kΩ, LED + 220Ω, I2C LCD  
**Pins:** LDR → GPIO 35, PWM LED → GPIO 2

```python
from analog import analogPin, analogPercent, mapValue
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

LDR_PIN = 35
LED_PIN = 2

def setup():
    analogPin(LDR_PIN)
    pwmSetup(LED_PIN, freq=1000)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        light    = analogPercent(LDR_PIN)
        darkness = 100 - light
        duty     = mapValue(darkness, 0, 100, 0, 1023)
        pwmWrite(LED_PIN, duty)
        lcd.move_to(0, 0)
        lcd.putstr(f"Light : {light:3d}%   ")
        lcd.move_to(0, 1)
        lcd.putstr(f"LED   : {darkness:3d}%   ")
        time.sleep_ms(200)

def cleanup():
    pwmStop(LED_PIN)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Light :  80%
LED   :  20%
```

---

## A09 — Averaged Sensor Reading

**Objective:** Show both raw and 10-sample averaged readings to reduce noise.  
**Components:** Any analog sensor, I2C LCD  
**Pin:** Sensor → GPIO 34

```python
from analog import analogPin, analogPercent, analogAverage
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

SENSOR_PIN = 34

def setup():
    analogPin(SENSOR_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        raw = analogPercent(SENSOR_PIN)
        avg = int(analogAverage(SENSOR_PIN, 10) / 4095 * 100)
        lcd.move_to(0, 0)
        lcd.putstr(f"Raw : {raw:3d} %     ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Avg : {avg:3d} %     ")
        time.sleep_ms(400)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Raw :  52 %
Avg :  50 %
```

---

## A10 — Dual Sensor Dashboard

**Objective:** Display two analog sensors on one LCD screen simultaneously.  
**Components:** Potentiometer + LDR, I2C LCD  
**Pins:** POT → GPIO 34, LDR → GPIO 35

```python
from analog import analogPin, analogPercent
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

POT_PIN = 34
LDR_PIN = 35

def setup():
    analogPin(POT_PIN)
    analogPin(LDR_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        knob  = analogPercent(POT_PIN)
        light = analogPercent(LDR_PIN)
        lcd.move_to(0, 0)
        lcd.putstr(f"Knob : {knob:3d} %    ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Light: {light:3d} %    ")
        time.sleep_ms(300)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Knob :  45 %
Light:  78 %
```

---

## A11 — POT Servo Angle Display

**Objective:** Map potentiometer to 0–180° servo angle and show on LCD.  
**Components:** Potentiometer, I2C LCD  
**Pin:** POT → GPIO 34  
**Note:** Angle display only — connect servo to PWM pin separately if needed.

```python
from analog import analogPin, analogRead, mapValue
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

POT_PIN = 34

def setup():
    analogPin(POT_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        raw   = analogRead(POT_PIN)
        angle = mapValue(raw, 0, 4095, 0, 180)
        arrow = "<" if angle < 60 else ("^" if angle < 120 else ">")
        lcd.move_to(0, 0)
        lcd.putstr(f"Servo Angle:    ")
        lcd.move_to(0, 1)
        lcd.putstr(f"  {angle:3d} deg  {arrow}    ")
        time.sleep_ms(200)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Servo Angle:
   90 deg  ^
```

---

## A12 — Water Level Indicator

**Objective:** Show water level in a tank as percentage and status.  
**Components:** Water level sensor (analog), I2C LCD  
**Pin:** Sensor → GPIO 34

```python
from analog import analogPin, analogPercent
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

WATER_PIN = 34

def setup():
    analogPin(WATER_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        level = analogPercent(WATER_PIN)
        if level > 70:
            status = "FULL    "
        elif level > 40:
            status = "MEDIUM  "
        elif level > 15:
            status = "LOW     "
        else:
            status = "EMPTY!! "
        lcd.move_to(0, 0)
        lcd.putstr(f"Water: {level:3d} %    ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Tank : {status}")
        time.sleep_ms(500)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Water:  35 %
Tank : MEDIUM
```

---

## A13 — Gas Sensor Alert

**Objective:** Read MQ-2 gas sensor and trigger alert when gas detected.  
**Components:** MQ-2 gas sensor (AO pin), Buzzer, I2C LCD  
**Pins:** MQ2 AO → GPIO 34, Buzzer → GPIO 26

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

GAS_PIN    = 34
BUZZER_PIN = 26
GAS_LIMIT  = 50    # % threshold

def setup():
    analogPin(GAS_PIN)
    pinMode(BUZZER_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        gas = analogPercent(GAS_PIN)
        if gas > GAS_LIMIT:
            digitalWrite(BUZZER_PIN, 1)
            status = "!! ALERT !!"
        else:
            digitalWrite(BUZZER_PIN, 0)
            status = "Safe       "
        lcd.move_to(0, 0)
        lcd.putstr(f"Gas  : {gas:3d} %   ")
        lcd.move_to(0, 1)
        lcd.putstr(status[:16])
        time.sleep_ms(300)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Gas  :  65 %
!! ALERT !!
```

---

## A14 — Rain Sensor Monitor

**Objective:** Show rain detection level and wet/dry status.  
**Components:** Rain sensor (AO), I2C LCD  
**Pin:** AO → GPIO 34  
**Note:** Rain sensor reads lower when wet, so invert the reading.

```python
from analog import analogPin, analogPercent
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

RAIN_PIN = 34

def setup():
    analogPin(RAIN_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        raw_pct  = analogPercent(RAIN_PIN)
        wetness  = 100 - raw_pct
        if wetness > 60:
            status = "Heavy Rain"
        elif wetness > 30:
            status = "Light Rain"
        else:
            status = "Dry       "
        lcd.move_to(0, 0)
        lcd.putstr(f"Rain : {wetness:3d} %   ")
        lcd.move_to(0, 1)
        lcd.putstr(status[:16])
        time.sleep_ms(400)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Rain :  75 %
Heavy Rain
```

---

## A15 — IR Distance Display

**Objective:** Read an analog IR distance sensor and show estimated distance.  
**Components:** Sharp GP2Y0A IR sensor or similar, I2C LCD  
**Pin:** Sensor VO → GPIO 34

```python
from analog import analogPin, analogVoltage
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

IR_PIN = 34

def voltage_to_cm(v):
    # Approximate inverse formula for Sharp IR (GP2Y0A21)
    if v < 0.3:
        return 80
    return round(27.0 / (v - 0.1), 1)

def setup():
    analogPin(IR_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        v    = analogVoltage(IR_PIN)
        dist = voltage_to_cm(v)
        zone = "Near  " if dist < 20 else ("Medium" if dist < 50 else "Far   ")
        lcd.move_to(0, 0)
        lcd.putstr(f"Dist: {dist:5.1f} cm  ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Zone : {zone}  ")
        time.sleep_ms(300)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Dist:  23.4 cm
Zone : Medium
```

---

## A16 — Flex Sensor Angle

**Objective:** Map flex sensor resistance to bend angle.  
**Components:** Flex sensor + 10kΩ divider, I2C LCD  
**Pin:** Divider midpoint → GPIO 34

```python
from analog import analogPin, analogRead, mapValue
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

FLEX_PIN  = 34
FLAT_VAL  = 1800    # raw ADC when flat
BENT_VAL  = 3000    # raw ADC when fully bent

def setup():
    analogPin(FLEX_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        raw   = analogRead(FLEX_PIN)
        angle = mapValue(raw, FLAT_VAL, BENT_VAL, 0, 90)
        state = "Flat " if angle < 20 else ("Bent " if angle < 60 else "Full ")
        lcd.move_to(0, 0)
        lcd.putstr(f"Flex: {angle:3d} deg   ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Bend: {state}        ")
        time.sleep_ms(200)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Flex:  45 deg
Bend: Bent
```

---

## A17 — Force Sensor Scale

**Objective:** Display force/pressure as percentage and weight estimate.  
**Components:** FSR (Force Sensitive Resistor) + 10kΩ, I2C LCD  
**Pin:** Divider midpoint → GPIO 34

```python
from analog import analogPin, analogPercent, analogRead, mapValue
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

FSR_PIN  = 34
MAX_GRAM = 500    # calibrate to your FSR

def setup():
    analogPin(FSR_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        pct  = analogPercent(FSR_PIN)
        gram = int(pct / 100 * MAX_GRAM)
        lcd.move_to(0, 0)
        lcd.putstr(f"Force: {pct:3d} %    ")
        lcd.move_to(0, 1)
        lcd.putstr(f"~{gram:4d} g         ")
        time.sleep_ms(200)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Force:  40 %
~ 200 g
```

---

## A18 — Turbidity Meter

**Objective:** Measure water turbidity (cloudiness) with an analog sensor.  
**Components:** Turbidity sensor, I2C LCD  
**Pin:** Sensor AO → GPIO 34

```python
from analog import analogPin, analogVoltage
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

TURB_PIN = 34

def setup():
    analogPin(TURB_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        v = analogVoltage(TURB_PIN)
        # Higher voltage = cleaner water for most turbidity sensors
        ntu = max(0, round((3.3 - v) * 1000, 0))
        if ntu < 100:
            clarity = "Clear   "
        elif ntu < 500:
            clarity = "Cloudy  "
        else:
            clarity = "Dirty!! "
        lcd.move_to(0, 0)
        lcd.putstr(f"NTU : {ntu:5.0f}      ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Water:{clarity}")
        time.sleep_ms(500)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
NTU :    45
Water:Clear
```

---

## A19 — UV Index Display

**Objective:** Read UV sensor output and show UV index level.  
**Components:** ML8511 UV sensor, I2C LCD  
**Pin:** Sensor OUT → GPIO 34

```python
from analog import analogPin, analogVoltage
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

UV_PIN = 34

def voltage_to_uv(v):
    # ML8511 approximate: 1V = UV0, 2.8V = UV15
    return max(0, round((v - 1.0) * (15.0 / 1.8), 1))

def setup():
    analogPin(UV_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        v   = analogVoltage(UV_PIN)
        uvi = voltage_to_uv(v)
        if uvi < 3:
            risk = "Low     "
        elif uvi < 6:
            risk = "Moderate"
        elif uvi < 8:
            risk = "High    "
        else:
            risk = "EXTREME!"
        lcd.move_to(0, 0)
        lcd.putstr(f"UV Index: {uvi:4.1f} ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Risk : {risk}  ")
        time.sleep_ms(500)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
UV Index:  4.2
Risk : Moderate
```

---

## A20 — Vibration Level Monitor

**Objective:** Read analog vibration sensor and display shake intensity.  
**Components:** Analog vibration/piezo sensor, I2C LCD  
**Pin:** Sensor → GPIO 34

```python
from analog import analogPin, analogRead, analogPercent
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

VIB_PIN   = 34
THRESHOLD = 60

def setup():
    analogPin(VIB_PIN)
    global lcd, peak
    peak = 0
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    global peak
    setup()
    while True:
        level = analogPercent(VIB_PIN)
        if level > peak:
            peak = level
        state = "SHAKE!" if level > THRESHOLD else "Stable"
        lcd.move_to(0, 0)
        lcd.putstr(f"Vib: {level:3d}% {state}  ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Peak: {peak:3d} %      ")
        time.sleep_ms(100)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Vib:  72% SHAKE!
Peak:  85 %
```

---

## A21 — Analog Pulse Counter (Threshold Crossing)

**Objective:** Count how many times a signal crosses a threshold level.  
**Components:** Any analog sensor, I2C LCD  
**Pin:** Sensor → GPIO 34

```python
from analog import analogPin, analogRead
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

SENSOR_PIN = 34
THRESHOLD  = 2000
count      = 0
was_above  = False

def setup():
    analogPin(SENSOR_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    global count, was_above
    setup()
    while True:
        val      = analogRead(SENSOR_PIN)
        is_above = val > THRESHOLD
        if is_above and not was_above:
            count += 1
        was_above = is_above
        lcd.move_to(0, 0)
        lcd.putstr(f"Raw  : {val:4d}     ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Count: {count:5d}    ")
        time.sleep_ms(50)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Raw  : 2341
Count:    12
```

---

## A22 — POT Frequency Generator (Buzzer)

**Objective:** Use a potentiometer to control buzzer frequency in real time.  
**Components:** Potentiometer, Buzzer, I2C LCD  
**Pins:** POT → GPIO 34, Buzzer → GPIO 26 (PWM)

```python
from analog import analogPin, analogRead, mapValue
from digital import pwmSetup, pwmWrite, pwmFreq, pwmStop
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

POT_PIN    = 34
BUZZER_PIN = 26

def setup():
    analogPin(POT_PIN)
    pwmSetup(BUZZER_PIN, freq=500)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        raw  = analogRead(POT_PIN)
        freq = mapValue(raw, 0, 4095, 100, 4000)
        pwmFreq(BUZZER_PIN, freq)
        pwmWrite(BUZZER_PIN, 512)
        lcd.move_to(0, 0)
        lcd.putstr(f"Frequency:      ")
        lcd.move_to(0, 1)
        lcd.putstr(f"  {freq:4d} Hz      ")
        time.sleep_ms(100)

def cleanup():
    pwmStop(BUZZER_PIN)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Frequency:
  1250 Hz
```

---

## A23 — Min/Max Logger

**Objective:** Track and display the minimum and maximum sensor values seen.  
**Components:** Any analog sensor, I2C LCD  
**Pin:** Sensor → GPIO 34

```python
from analog import analogPin, analogRead
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

SENSOR_PIN = 34

def setup():
    analogPin(SENSOR_PIN)
    global lcd, s_min, s_max
    s_min = 4095
    s_max = 0
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    global s_min, s_max
    setup()
    while True:
        val   = analogRead(SENSOR_PIN)
        if val < s_min: s_min = val
        if val > s_max: s_max = val
        lcd.move_to(0, 0)
        lcd.putstr(f"Now:{val:4d} Mn:{s_min:4d}")
        lcd.move_to(0, 1)
        lcd.putstr(f"Max: {s_max:4d}         ")
        time.sleep_ms(200)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Now:1843 Mn: 412
Max: 3870
```

---

## A24 — Battery Voltage Monitor

**Objective:** Measure battery voltage via a voltage divider and show charge level.  
**Components:** Battery (use 10kΩ+10kΩ divider for >3.3V), I2C LCD  
**Pin:** Divider midpoint → GPIO 34  
**Note:** Divider halves voltage — multiply reading by 2 for actual battery voltage.

```python
from analog import analogPin, analogVoltage
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BAT_PIN    = 34
FULL_V     = 4.2    # Li-ion full
EMPTY_V    = 3.0    # Li-ion cutoff

def setup():
    analogPin(BAT_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        v_read  = analogVoltage(BAT_PIN)
        v_bat   = round(v_read * 2, 2)    # divider × 2
        pct     = int((v_bat - EMPTY_V) / (FULL_V - EMPTY_V) * 100)
        pct     = max(0, min(100, pct))
        status  = "OK   " if pct > 30 else "LOW! "
        lcd.move_to(0, 0)
        lcd.putstr(f"Bat: {v_bat:.2f}V {status}")
        lcd.move_to(0, 1)
        lcd.putstr(f"Charge: {pct:3d} %   ")
        time.sleep_ms(1000)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Bat: 3.85V OK
Charge:  72 %
```

---

## A25 — Dual Threshold Alert

**Objective:** Show alerts for both LOW and HIGH threshold crossings on a sensor.  
**Components:** Any analog sensor, Buzzer, I2C LCD  
**Pins:** Sensor → GPIO 34, Buzzer → GPIO 26

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

SENSOR_PIN = 34
BUZZER_PIN = 26
LOW_THR    = 20
HIGH_THR   = 80

def setup():
    analogPin(SENSOR_PIN)
    pinMode(BUZZER_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        val = analogPercent(SENSOR_PIN)
        if val < LOW_THR:
            status = "TOO LOW! "
            digitalWrite(BUZZER_PIN, 1)
        elif val > HIGH_THR:
            status = "TOO HIGH!"
            digitalWrite(BUZZER_PIN, 1)
        else:
            status = "Normal   "
            digitalWrite(BUZZER_PIN, 0)
        lcd.move_to(0, 0)
        lcd.putstr(f"Sensor: {val:3d} %   ")
        lcd.move_to(0, 1)
        lcd.putstr(status[:16])
        time.sleep_ms(300)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Sensor:  85 %
TOO HIGH!
```

---

## A26 — Analog Tachometer

**Objective:** Estimate RPM using analog pulses from a hall-effect or IR sensor.  
**Components:** Hall effect sensor (analog), I2C LCD  
**Pin:** Sensor → GPIO 34

```python
from analog import analogPin, analogRead
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

SENSOR_PIN = 34
THRESHOLD  = 2000

def setup():
    analogPin(SENSOR_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    pulse_count = 0
    was_high    = False
    start       = time.ticks_ms()

    while True:
        val     = analogRead(SENSOR_PIN)
        is_high = val > THRESHOLD

        if is_high and not was_high:
            pulse_count += 1
        was_high = is_high

        elapsed = time.ticks_diff(time.ticks_ms(), start)
        if elapsed >= 1000:
            rpm = pulse_count * 60
            lcd.move_to(0, 0)
            lcd.putstr(f"Pulses: {pulse_count:4d}   ")
            lcd.move_to(0, 1)
            lcd.putstr(f"RPM   : {rpm:5d}  ")
            pulse_count = 0
            start = time.ticks_ms()

        time.sleep_ms(5)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Pulses:   24
RPM   :  1440
```

---

## A27 — Smoothed Trend Display

**Objective:** Show current reading and rolling average to visualise trend (rising/falling).  
**Components:** Any analog sensor, I2C LCD  
**Pin:** Sensor → GPIO 34

```python
from analog import analogPin, analogPercent
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

SENSOR_PIN = 34
WINDOW     = 8
buf        = []

def smooth(val):
    buf.append(val)
    if len(buf) > WINDOW:
        buf.pop(0)
    return int(sum(buf) / len(buf))

def setup():
    analogPin(SENSOR_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    global prev_avg
    setup()
    prev_avg = 0
    while True:
        now = analogPercent(SENSOR_PIN)
        avg = smooth(now)
        trend = "^ Up  " if avg > prev_avg + 2 else ("v Down" if avg < prev_avg - 2 else "= Flat")
        prev_avg = avg
        lcd.move_to(0, 0)
        lcd.putstr(f"Now:{now:3d}% Avg:{avg:3d}%")
        lcd.move_to(0, 1)
        lcd.putstr(f"Trend: {trend}    ")
        time.sleep_ms(300)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Now: 55% Avg: 52%
Trend: ^ Up
```

---

## A28 — Sensor Percentage Bar Graph (2 rows)

**Objective:** Use both LCD rows to show a large bargraph for one sensor.  
**Components:** Any analog sensor, I2C LCD  
**Pin:** Sensor → GPIO 34

```python
from analog import analogPin, analogPercent
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

SENSOR_PIN = 34

def setup():
    analogPin(SENSOR_PIN)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def make_bar(pct):
    total  = 32   # 16 chars × 2 rows
    filled = int(pct / 100 * total)
    return "#" * filled + "-" * (total - filled)

def main():
    setup()
    while True:
        pct = analogPercent(SENSOR_PIN)
        bar = make_bar(pct)
        lcd.move_to(0, 0)
        lcd.putstr(bar[:16])
        lcd.move_to(0, 1)
        lcd.putstr(bar[16:] + f" {pct:3d}%")
        time.sleep_ms(200)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
########--------
####--------  63%
```

---

## A29 — Multi-Channel Analog Average

**Objective:** Average two sensors and display individual + combined reading.  
**Components:** 2× analog sensors, I2C LCD  
**Pins:** Sensor A → GPIO 34, Sensor B → GPIO 35

```python
from analog import analogPin, analogPercent
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

PIN_A = 34
PIN_B = 35

def setup():
    analogPin(PIN_A)
    analogPin(PIN_B)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        a   = analogPercent(PIN_A)
        b   = analogPercent(PIN_B)
        avg = (a + b) // 2
        lcd.move_to(0, 0)
        lcd.putstr(f"A:{a:3d}%  B:{b:3d}%  ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Avg  :  {avg:3d} %    ")
        time.sleep_ms(300)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
A: 45%  B: 71%
Avg  :   58 %
```

---

## A30 — Full Analog Dashboard

**Objective:** Display POT, LDR, and a computed score on one LCD screen with status.  
**Components:** Potentiometer, LDR, Buzzer, LED, I2C LCD  
**Pins:** POT→34, LDR→35, Buzzer→26, LED→2

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

POT_PIN    = 34
LDR_PIN    = 35
BUZZER_PIN = 26
LED_PIN    = 2

def setup():
    analogPin(POT_PIN)
    analogPin(LDR_PIN)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(LED_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        knob  = analogPercent(POT_PIN)
        light = analogPercent(LDR_PIN)
        score = (knob + light) // 2

        if score > 75:
            status = "HIGH "
            digitalWrite(BUZZER_PIN, 1)
            digitalWrite(LED_PIN, 1)
        else:
            status = "NORM "
            digitalWrite(BUZZER_PIN, 0)
            digitalWrite(LED_PIN, 0)

        lcd.move_to(0, 0)
        lcd.putstr(f"K:{knob:3d} L:{light:3d}  ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Score:{score:3d}% {status}")
        time.sleep_ms(300)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
K: 80 L: 72
Score: 76% HIGH
```

---

---

# DIGITAL PROJECTS

---

## D01 — LED ON/OFF with Button

**Objective:** Press button to turn LED ON, release to turn OFF.  
**Components:** Push button, LED + 220Ω, I2C LCD  
**Pins:** Button → GPIO 15, LED → GPIO 2

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN_PIN = 15
LED_PIN = 2

def setup():
    pinMode(BTN_PIN, INPUT_PULLUP)
    pinMode(LED_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Button LED Test ")

def main():
    setup()
    while True:
        btn = digitalRead(BTN_PIN) == 0
        digitalWrite(LED_PIN, 1 if btn else 0)
        lcd.move_to(0, 1)
        lcd.putstr("LED: ON  " if btn else "LED: OFF ")
        time.sleep_ms(50)

def cleanup():
    digitalWrite(LED_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Button LED Test
LED: ON
```

---

## D02 — Toggle LED with Button

**Objective:** Each button press toggles LED state (ON→OFF→ON).  
**Components:** Push button, LED, I2C LCD  
**Pins:** Button → GPIO 15, LED → GPIO 2

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN_PIN  = 15
LED_PIN  = 2
led_state = False
prev_btn  = False

def setup():
    pinMode(BTN_PIN, INPUT_PULLUP)
    pinMode(LED_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    global led_state, prev_btn
    setup()
    while True:
        btn = digitalRead(BTN_PIN) == 0
        if btn and not prev_btn:
            led_state = not led_state
            digitalWrite(LED_PIN, 1 if led_state else 0)
        prev_btn = btn
        lcd.move_to(0, 0)
        lcd.putstr("Toggle LED      ")
        lcd.move_to(0, 1)
        lcd.putstr("State: ON " if led_state else "State: OFF")
        time.sleep_ms(30)

def cleanup():
    digitalWrite(LED_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Toggle LED
State: ON
```

---

## D03 — LED Blink Rate Control (Button)

**Objective:** Each button press cycles through blink speeds: Slow → Normal → Fast → Off.  
**Components:** Push button, LED, I2C LCD

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN_PIN = 15
LED_PIN = 2
MODES   = [("Off   ", 0), ("Slow  ", 800), ("Normal", 400), ("Fast  ", 100)]
mode_idx = 0
prev_btn = False

def setup():
    pinMode(BTN_PIN, INPUT_PULLUP)
    pinMode(LED_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    global mode_idx, prev_btn
    setup()
    last_blink = time.ticks_ms()
    led_on = False

    while True:
        btn = digitalRead(BTN_PIN) == 0
        if btn and not prev_btn:
            mode_idx = (mode_idx + 1) % len(MODES)
        prev_btn = btn

        name, interval = MODES[mode_idx]
        if interval == 0:
            digitalWrite(LED_PIN, 0)
        else:
            if time.ticks_diff(time.ticks_ms(), last_blink) >= interval:
                led_on = not led_on
                digitalWrite(LED_PIN, 1 if led_on else 0)
                last_blink = time.ticks_ms()

        lcd.move_to(0, 0)
        lcd.putstr("Blink Speed:    ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Mode: {name}     ")
        time.sleep_ms(20)

def cleanup():
    digitalWrite(LED_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Blink Speed:
Mode: Fast
```

---

## D04 — Button Press Counter

**Objective:** Count total button presses and display on LCD.  
**Components:** Push button, I2C LCD  
**Pin:** Button → GPIO 15

```python
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN_PIN  = 15
count    = 0
prev_btn = False

def setup():
    pinMode(BTN_PIN, INPUT_PULLUP)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Button Counter  ")

def main():
    global count, prev_btn
    setup()
    while True:
        btn = digitalRead(BTN_PIN) == 0
        if btn and not prev_btn:
            count += 1
        prev_btn = btn
        lcd.move_to(0, 1)
        lcd.putstr(f"Count : {count:5d}   ")
        time.sleep_ms(20)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Button Counter
Count :    27
```

---

## D05 — Debounced Button with LCD Feedback

**Objective:** Use software debounce to prevent multiple counts per press.  
**Components:** Push button, I2C LCD

```python
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN_PIN     = 15
DEBOUNCE_MS = 50
count       = 0
last_press  = 0
prev_btn    = False

def setup():
    pinMode(BTN_PIN, INPUT_PULLUP)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Debounce Count  ")

def main():
    global count, prev_btn, last_press
    setup()
    while True:
        btn = digitalRead(BTN_PIN) == 0
        now = time.ticks_ms()
        if btn and not prev_btn:
            if time.ticks_diff(now, last_press) > DEBOUNCE_MS:
                count += 1
                last_press = now
        prev_btn = btn
        lcd.move_to(0, 1)
        lcd.putstr(f"Presses: {count:4d}   ")
        time.sleep_ms(10)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Debounce Count
Presses:   14
```

---

## D06 — PWM Brightness Control

**Objective:** Button cycles LED brightness through 5 levels.  
**Components:** Push button, LED, I2C LCD  
**Pins:** Button→15, PWM LED→2

```python
from digital import pinMode, digitalRead, pwmSetup, pwmWrite, pwmStop, INPUT_PULLUP
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN_PIN  = 15
LED_PIN  = 2
LEVELS   = [0, 200, 450, 700, 1023]
NAMES    = ["Off  ","Low  ","Med  ","High ","Full "]
idx      = 0
prev_btn = False

def setup():
    pinMode(BTN_PIN, INPUT_PULLUP)
    pwmSetup(LED_PIN, freq=1000)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    global idx, prev_btn
    setup()
    while True:
        btn = digitalRead(BTN_PIN) == 0
        if btn and not prev_btn:
            idx = (idx + 1) % len(LEVELS)
            pwmWrite(LED_PIN, LEVELS[idx])
        prev_btn = btn
        pct = int(LEVELS[idx] / 1023 * 100)
        lcd.move_to(0, 0)
        lcd.putstr("PWM Brightness  ")
        lcd.move_to(0, 1)
        lcd.putstr(f"{NAMES[idx]}: {pct:3d} %    ")
        time.sleep_ms(30)

def cleanup():
    pwmStop(LED_PIN)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
PWM Brightness
High : 68 %
```

---

## D07 — Traffic Light Sequence

**Objective:** Simulate a traffic light: Red → Green → Yellow → repeat.  
**Components:** Red, Yellow, Green LEDs, I2C LCD  
**Pins:** Red→2, Yellow→4, Green→5

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

RED_PIN    = 2
YELLOW_PIN = 4
GREEN_PIN  = 5

SEQUENCE = [
    (RED_PIN,    "RED   ", "STOP  ", 4000),
    (GREEN_PIN,  "GREEN ", "GO    ", 4000),
    (YELLOW_PIN, "YELLOW", "SLOW  ", 2000),
]

def setup():
    for pin in [RED_PIN, YELLOW_PIN, GREEN_PIN]:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        for pin, color, msg, duration in SEQUENCE:
            for p in [RED_PIN, YELLOW_PIN, GREEN_PIN]:
                digitalWrite(p, 0)
            digitalWrite(pin, 1)
            lcd.move_to(0, 0)
            lcd.putstr(f"Signal: {color}  ")
            lcd.move_to(0, 1)
            lcd.putstr(f"Action: {msg}   ")
            time.sleep_ms(duration)

def cleanup():
    for pin in [RED_PIN, YELLOW_PIN, GREEN_PIN]:
        digitalWrite(pin, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Signal: GREEN
Action: GO
```

---

## D08 — Buzzer Alarm with Button

**Objective:** Press button to trigger a buzzer alarm that runs for 3 seconds.  
**Components:** Push button, Buzzer, I2C LCD  
**Pins:** Button→15, Buzzer→26

```python
from digital import pinMode, digitalWrite, digitalRead, blink, INPUT_PULLUP, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN_PIN    = 15
BUZZER_PIN = 26

def setup():
    pinMode(BTN_PIN, INPUT_PULLUP)
    pinMode(BUZZER_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Press for Alarm ")

def main():
    setup()
    while True:
        if digitalRead(BTN_PIN) == 0:
            lcd.move_to(0, 1)
            lcd.putstr("!! ALARM !!!    ")
            blink(BUZZER_PIN, times=6, on_ms=200, off_ms=200)
            lcd.move_to(0, 1)
            lcd.putstr("Ready...        ")
        time.sleep_ms(100)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Press for Alarm
!! ALARM !!!
```

---

## D09 — Digital Dice (Button Roll)

**Objective:** Press button to roll a dice and display result.  
**Components:** Push button, I2C LCD

```python
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time, random

BTN_PIN  = 15
prev_btn = False
result   = 1

def setup():
    pinMode(BTN_PIN, INPUT_PULLUP)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Press to Roll!  ")

def main():
    global prev_btn, result
    setup()
    while True:
        btn = digitalRead(BTN_PIN) == 0
        if btn and not prev_btn:
            result = random.randint(1, 6)
            faces  = ["", "[1]", "[2]", "[3]", "[4]", "[5]", "[6]"]
            lcd.move_to(0, 0)
            lcd.putstr(f"Rolled: {result}        ")
            lcd.move_to(0, 1)
            lcd.putstr(f"Face : {faces[result]}       ")
        prev_btn = btn
        time.sleep_ms(30)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Rolled: 4
Face : [4]
```

---

## D10 — Button Hold Timer

**Objective:** Measure how long the button is held down and display in seconds.  
**Components:** Push button, I2C LCD

```python
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN_PIN   = 15
press_time = None

def setup():
    pinMode(BTN_PIN, INPUT_PULLUP)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Hold the button ")

def main():
    global press_time
    setup()
    held_ms  = 0
    while True:
        btn = digitalRead(BTN_PIN) == 0
        if btn:
            if press_time is None:
                press_time = time.ticks_ms()
            held_ms = time.ticks_diff(time.ticks_ms(), press_time)
        else:
            press_time = None
            held_ms    = 0
        secs = held_ms / 1000
        lcd.move_to(0, 1)
        lcd.putstr(f"Held: {secs:5.2f} s    ")
        time.sleep_ms(50)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Hold the button
Held:  2.35 s
```

---

## D11 — Morse Code LED Blinker

**Objective:** Type text on serial/hardcoded string and blink it in Morse code with LCD display.  
**Components:** LED, I2C LCD  
**Pin:** LED → GPIO 2

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

LED_PIN = 2

MORSE = {
    'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....',
    'I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-',
    'R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..'
}
DOT_MS = 150

def blink_morse(char, led):
    code = MORSE.get(char.upper(), '')
    for sym in code:
        if sym == '.':
            digitalWrite(led, 1); time.sleep_ms(DOT_MS)
            digitalWrite(led, 0); time.sleep_ms(DOT_MS)
        elif sym == '-':
            digitalWrite(led, 1); time.sleep_ms(DOT_MS * 3)
            digitalWrite(led, 0); time.sleep_ms(DOT_MS)
    time.sleep_ms(DOT_MS * 3)

def setup():
    pinMode(LED_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    message = "SOS"
    while True:
        for ch in message:
            lcd.move_to(0, 0)
            lcd.putstr(f"Morse: {message}      ")
            lcd.move_to(0, 1)
            lcd.putstr(f"Char : {ch} {MORSE.get(ch.upper(),'')}      ")
            blink_morse(ch, LED_PIN)
        time.sleep_ms(1000)

def cleanup():
    digitalWrite(LED_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Morse: SOS
Char : O ---
```

---

## D12 — PIR Motion Detector

**Objective:** Detect motion using PIR sensor and show alert on LCD.  
**Components:** PIR sensor (HC-SR501), LED, I2C LCD  
**Pins:** PIR → GPIO 14, LED → GPIO 2

```python
from digital import pinMode, digitalWrite, digitalRead, OUTPUT, INPUT_PULLUP
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

PIR_PIN = 14
LED_PIN = 2
motion_count = 0

def setup():
    pinMode(PIR_PIN, 0)    # INPUT
    pinMode(LED_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("PIR Motion Sens ")
    time.sleep(2)    # PIR warmup

def main():
    global motion_count
    setup()
    prev = 0
    while True:
        motion = digitalRead(PIR_PIN)
        if motion and not prev:
            motion_count += 1
            digitalWrite(LED_PIN, 1)
        elif not motion:
            digitalWrite(LED_PIN, 0)
        prev = motion
        lcd.move_to(0, 0)
        lcd.putstr("MOTION! " if motion else "No Motion")
        lcd.move_to(0, 1)
        lcd.putstr(f"Events: {motion_count:4d}   ")
        time.sleep_ms(100)

def cleanup():
    digitalWrite(LED_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
MOTION!
Events:    5
```

---

## D13 — Reed Switch Door Sensor

**Objective:** Detect door open/close with a magnetic reed switch.  
**Components:** Reed switch, I2C LCD  
**Pin:** Reed switch → GPIO 15 (with INPUT_PULLUP)

```python
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

REED_PIN  = 15
open_count = 0
prev_state = None

def setup():
    pinMode(REED_PIN, INPUT_PULLUP)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Door Monitor    ")

def main():
    global open_count, prev_state
    setup()
    while True:
        # Reed closed (magnet near) = LOW, open = HIGH
        is_open = digitalRead(REED_PIN) == 1
        if is_open and prev_state == False:
            open_count += 1
        prev_state = is_open
        lcd.move_to(0, 0)
        lcd.putstr("OPEN !! " if is_open else "Closed  ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Opens: {open_count:4d}     ")
        time.sleep_ms(100)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
OPEN !!
Opens:    3
```

---

## D14 — Tilt Sensor Alert

**Objective:** Detect tilting with a ball-tilt sensor and show on LCD.  
**Components:** Tilt switch (SW-520D), LED, I2C LCD  
**Pins:** Tilt → GPIO 15, LED → GPIO 2

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

TILT_PIN   = 15
LED_PIN    = 2
tilt_count = 0
prev_state = None

def setup():
    pinMode(TILT_PIN, INPUT_PULLUP)
    pinMode(LED_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    global tilt_count, prev_state
    setup()
    while True:
        tilted = digitalRead(TILT_PIN) == 0
        if tilted and prev_state == False:
            tilt_count += 1
        prev_state = tilted
        digitalWrite(LED_PIN, 1 if tilted else 0)
        lcd.move_to(0, 0)
        lcd.putstr("TILTED! " if tilted else "Level   ")
        lcd.move_to(0, 1)
        lcd.putstr(f"Count: {tilt_count:4d}     ")
        time.sleep_ms(100)

def cleanup():
    digitalWrite(LED_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
TILTED!
Count:    8
```

---

## D15 — Reaction Timer Game

**Objective:** LED turns ON randomly — press button as fast as possible. Shows reaction time.  
**Components:** Push button, LED, I2C LCD  
**Pins:** Button→15, LED→2

```python
from digital import pinMode, digitalRead, digitalWrite, INPUT_PULLUP, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time, random

BTN_PIN = 15
LED_PIN = 2

def setup():
    pinMode(BTN_PIN, INPUT_PULLUP)
    pinMode(LED_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        lcd.move_to(0, 0)
        lcd.putstr("Get Ready...    ")
        lcd.move_to(0, 1)
        lcd.putstr("                ")
        time.sleep_ms(random.randint(2000, 5000))

        # Turn LED on — start timing
        digitalWrite(LED_PIN, 1)
        lcd.move_to(0, 0)
        lcd.putstr("PRESS NOW!!     ")
        start = time.ticks_ms()

        # Wait for button press (up to 3 seconds)
        pressed = False
        while time.ticks_diff(time.ticks_ms(), start) < 3000:
            if digitalRead(BTN_PIN) == 0:
                pressed = True
                break
            time.sleep_ms(5)

        rt = time.ticks_diff(time.ticks_ms(), start)
        digitalWrite(LED_PIN, 0)

        lcd.move_to(0, 0)
        lcd.putstr("Reaction Time:  ")
        lcd.move_to(0, 1)
        if pressed:
            lcd.putstr(f"  {rt:4d} ms  OK! ")
        else:
            lcd.putstr("Too slow!       ")
        time.sleep(3)

def cleanup():
    digitalWrite(LED_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Reaction Time:
   342 ms  OK!
```

---

## D16 — Up/Down Counter with Two Buttons

**Objective:** One button increments, other decrements a counter shown on LCD.  
**Components:** 2× Push buttons, I2C LCD  
**Pins:** Button UP → GPIO 15, Button DOWN → GPIO 14

```python
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN_UP   = 15
BTN_DOWN = 14
counter  = 0
prev_up  = False
prev_dn  = False

def setup():
    pinMode(BTN_UP,   INPUT_PULLUP)
    pinMode(BTN_DOWN, INPUT_PULLUP)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Up/Down Counter ")

def main():
    global counter, prev_up, prev_dn
    setup()
    while True:
        up = digitalRead(BTN_UP)   == 0
        dn = digitalRead(BTN_DOWN) == 0
        if up and not prev_up: counter += 1
        if dn and not prev_dn: counter -= 1
        prev_up = up
        prev_dn = dn
        lcd.move_to(0, 1)
        lcd.putstr(f"Value : {counter:+5d}   ")
        time.sleep_ms(30)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Up/Down Counter
Value :   +12
```

---

## D17 — PWM Fade In/Out

**Objective:** LED automatically fades in then out in a smooth loop.  
**Components:** LED, I2C LCD  
**Pin:** PWM LED → GPIO 2

```python
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

LED_PIN = 2

def setup():
    pwmSetup(LED_PIN, freq=1000)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    step = 5
    duty = 0
    direction = 1

    while True:
        duty += step * direction
        if duty >= 1023: duty = 1023; direction = -1
        if duty <= 0:    duty = 0;    direction =  1
        pwmWrite(LED_PIN, duty)
        pct = int(duty / 1023 * 100)
        lcd.move_to(0, 0)
        lcd.putstr("PWM Fade        ")
        lcd.move_to(0, 1)
        state = "Fading In  " if direction == 1 else "Fading Out "
        lcd.putstr(f"{state}{pct:3d}%")
        time.sleep_ms(10)

def cleanup():
    pwmStop(LED_PIN)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
PWM Fade
Fading In   72%
```

---

## D18 — LED Chaser (Knight Rider)

**Objective:** LEDs chase left to right and back like Knight Rider.  
**Components:** 4× LEDs, I2C LCD  
**Pins:** LEDs → GPIO 2, 4, 5, 18

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

LED_PINS = [2, 4, 5, 18]
DELAY_MS = 150

def setup():
    for pin in LED_PINS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("LED Chaser      ")

def main():
    setup()
    while True:
        for i in range(len(LED_PINS)):
            for p in LED_PINS: digitalWrite(p, 0)
            digitalWrite(LED_PINS[i], 1)
            lcd.move_to(0, 1)
            lcd.putstr(f"LED {i+1} ON        ")
            time.sleep_ms(DELAY_MS)
        for i in range(len(LED_PINS) - 2, 0, -1):
            for p in LED_PINS: digitalWrite(p, 0)
            digitalWrite(LED_PINS[i], 1)
            lcd.move_to(0, 1)
            lcd.putstr(f"LED {i+1} ON        ")
            time.sleep_ms(DELAY_MS)

def cleanup():
    for p in LED_PINS: digitalWrite(p, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
LED Chaser
LED 3 ON
```

---

## D19 — Buzzer Melody Player

**Objective:** Play a simple melody on a buzzer while showing note names on LCD.  
**Components:** Buzzer (passive), I2C LCD  
**Pin:** Buzzer → GPIO 26 (PWM)

```python
from digital import pwmSetup, pwmWrite, pwmFreq, pwmStop
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BUZ_PIN = 26

# (note_name, frequency_hz, duration_ms)
MELODY = [
    ("C4", 262, 300), ("D4", 294, 300), ("E4", 330, 300),
    ("F4", 349, 300), ("G4", 392, 400), ("G4", 392, 400),
    ("A4", 440, 300), ("A4", 440, 300), ("G4", 392, 600),
]

def play_note(pin, freq, dur):
    pwmFreq(pin, freq)
    pwmWrite(pin, 512)
    time.sleep_ms(dur)
    pwmWrite(pin, 0)
    time.sleep_ms(50)

def setup():
    pwmSetup(BUZ_PIN, freq=440)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Melody Player   ")

def main():
    setup()
    while True:
        for name, freq, dur in MELODY:
            lcd.move_to(0, 1)
            lcd.putstr(f"Note: {name} {freq}Hz  ")
            play_note(BUZ_PIN, freq, dur)
        time.sleep(1)

def cleanup():
    pwmStop(BUZ_PIN)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Melody Player
Note: G4 392Hz
```

---

## D20 — Touch Sensor Toggle

**Objective:** Capacitive touch sensor toggles LED state with LCD display.  
**Components:** TTP223 touch sensor (or similar digital), LED, I2C LCD  
**Pins:** Touch → GPIO 14, LED → GPIO 2

```python
from digital import pinMode, digitalRead, digitalWrite, OUTPUT, INPUT_PULLUP
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

TOUCH_PIN  = 14
LED_PIN    = 2
led_state  = False
prev_touch = False

def setup():
    pinMode(TOUCH_PIN, 0)    # INPUT
    pinMode(LED_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Touch Sensor    ")

def main():
    global led_state, prev_touch
    setup()
    while True:
        touched = digitalRead(TOUCH_PIN) == 1
        if touched and not prev_touch:
            led_state = not led_state
            digitalWrite(LED_PIN, 1 if led_state else 0)
        prev_touch = touched
        lcd.move_to(0, 1)
        lcd.putstr("LED: ON  " if led_state else "LED: OFF ")
        time.sleep_ms(30)

def cleanup():
    digitalWrite(LED_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Touch Sensor
LED: ON
```

---

## D21 — Relay Controller with Button

**Objective:** Button toggles a relay (to control mains devices safely) with status on LCD.  
**Components:** Push button, 5V Relay module, I2C LCD  
**Pins:** Button→15, Relay IN→26

```python
from digital import pinMode, digitalRead, digitalWrite, INPUT_PULLUP, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN_PIN   = 15
RELAY_PIN = 26
relay_on  = False
prev_btn  = False

def setup():
    pinMode(BTN_PIN,   INPUT_PULLUP)
    pinMode(RELAY_PIN, OUTPUT)
    digitalWrite(RELAY_PIN, 0)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Relay Control   ")

def main():
    global relay_on, prev_btn
    setup()
    while True:
        btn = digitalRead(BTN_PIN) == 0
        if btn and not prev_btn:
            relay_on = not relay_on
            # Most relay modules are active LOW
            digitalWrite(RELAY_PIN, 0 if relay_on else 1)
        prev_btn = btn
        lcd.move_to(0, 1)
        lcd.putstr("Relay: ON  " if relay_on else "Relay: OFF ")
        time.sleep_ms(30)

def cleanup():
    digitalWrite(RELAY_PIN, 1)    # ensure relay off
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Relay Control
Relay: ON
```

---

## D22 — Dual Button Logic Gate (AND/OR)

**Objective:** Two buttons demonstrate AND and OR logic gates with LCD output.  
**Components:** 2× push buttons, LED, I2C LCD  
**Pins:** Button A→15, Button B→14, LED→2

```python
from digital import pinMode, digitalRead, digitalWrite, INPUT_PULLUP, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN_A = 15
BTN_B = 14
LED   = 2

def setup():
    pinMode(BTN_A, INPUT_PULLUP)
    pinMode(BTN_B, INPUT_PULLUP)
    pinMode(LED, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Logic Gate Demo ")

def main():
    setup()
    while True:
        a = digitalRead(BTN_A) == 0
        b = digitalRead(BTN_B) == 0
        result_and = a and b
        result_or  = a or  b
        # AND gate controls LED
        digitalWrite(LED, 1 if result_and else 0)
        lcd.move_to(0, 0)
        lcd.putstr(f"A={int(a)} B={int(b)} AND={int(result_and)}")
        lcd.move_to(0, 1)
        lcd.putstr(f"OR={int(result_or)} LED={'ON ' if result_and else 'OFF'} ")
        time.sleep_ms(50)

def cleanup():
    digitalWrite(LED, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
A=1 B=1 AND=1
OR=1 LED=ON
```

---

## D23 — Button Combo Secret Lock

**Objective:** Enter a 4-press code to unlock. Wrong presses show error.  
**Components:** Push button, LED, Buzzer, I2C LCD  
**Pins:** Button→15, Green LED→2, Buzzer→26

```python
from digital import pinMode, digitalRead, digitalWrite, blink, INPUT_PULLUP, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN_PIN    = 15
GREEN_LED  = 2
BUZZER_PIN = 26
SECRET_LEN = 4
SECRET_HOLD_MS = [200, 500, 200, 200]   # short/long pattern

presses  = []
prev_btn = False

def setup():
    pinMode(BTN_PIN, INPUT_PULLUP)
    pinMode(GREEN_LED, OUTPUT)
    pinMode(BUZZER_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Enter Code:     ")

def main():
    global presses, prev_btn
    setup()
    press_start = None

    while True:
        btn = digitalRead(BTN_PIN) == 0

        if btn and not prev_btn:
            press_start = time.ticks_ms()

        if not btn and prev_btn and press_start is not None:
            held = time.ticks_diff(time.ticks_ms(), press_start)
            presses.append("L" if held > 350 else "S")
            press_start = None

            lcd.move_to(0, 1)
            lcd.putstr(f"{''.join(presses):16s}")

            if len(presses) == SECRET_LEN:
                if presses == ["S", "L", "S", "S"]:
                    lcd.move_to(0, 0)
                    lcd.putstr("** UNLOCKED! ** ")
                    blink(GREEN_LED, 3, 200, 100)
                else:
                    lcd.move_to(0, 0)
                    lcd.putstr("WRONG! Try again")
                    blink(BUZZER_PIN, 2, 100, 100)
                time.sleep(2)
                presses = []
                lcd.clear()
                lcd.move_to(0, 0)
                lcd.putstr("Enter Code:     ")

        prev_btn = btn
        time.sleep_ms(20)

def cleanup():
    digitalWrite(GREEN_LED, 0)
    digitalWrite(BUZZER_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
** UNLOCKED! **
SLSS
```

---

## D24 — Stopwatch with Button Start/Stop/Reset

**Objective:** Button 1 = Start/Stop, Button 2 = Reset. LCD shows elapsed time.  
**Components:** 2× push buttons, I2C LCD  
**Pins:** Start/Stop→15, Reset→14

```python
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN_SS    = 15
BTN_RST   = 14
running   = False
elapsed   = 0
start_t   = 0
prev_ss   = False
prev_rst  = False

def setup():
    pinMode(BTN_SS,  INPUT_PULLUP)
    pinMode(BTN_RST, INPUT_PULLUP)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("   STOPWATCH    ")

def main():
    global running, elapsed, start_t, prev_ss, prev_rst
    setup()
    while True:
        ss  = digitalRead(BTN_SS)  == 0
        rst = digitalRead(BTN_RST) == 0

        if ss and not prev_ss:
            if running:
                elapsed += time.ticks_diff(time.ticks_ms(), start_t)
                running = False
            else:
                start_t = time.ticks_ms()
                running = True

        if rst and not prev_rst:
            running = False
            elapsed = 0

        prev_ss  = ss
        prev_rst = rst

        total_ms = elapsed + (time.ticks_diff(time.ticks_ms(), start_t) if running else 0)
        mins  = total_ms // 60000
        secs  = (total_ms % 60000) // 1000
        ms    = (total_ms % 1000) // 10
        state = "RUN " if running else "STOP"

        lcd.move_to(0, 1)
        lcd.putstr(f"{mins:02d}:{secs:02d}.{ms:02d} {state}")
        time.sleep_ms(20)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
   STOPWATCH
00:12.45 RUN
```

---

## D25 — System Uptime Display

**Objective:** Show how long the ESP32 has been running in hh:mm:ss format.  
**Components:** I2C LCD only

```python
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

start_ms = time.ticks_ms()

def setup():
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("System Uptime:  ")

def main():
    setup()
    while True:
        ms    = time.ticks_diff(time.ticks_ms(), start_ms)
        total = ms // 1000
        h     = total // 3600
        m     = (total % 3600) // 60
        s     = total % 60
        lcd.move_to(0, 1)
        lcd.putstr(f"  {h:02d}:{m:02d}:{s:02d}       ")
        time.sleep_ms(500)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
System Uptime:
  00:05:23
```

---

## D26 — Auto Night Light (LDR + Digital Threshold)

**Objective:** Turn on LED automatically when it gets dark. Show LDR status on LCD.  
**Components:** LDR (digital DO pin), LED, I2C LCD  
**Pins:** LDR DO→14, LED→2  
**Note:** LDR module DO pin goes LOW when dark.

```python
from digital import pinMode, digitalRead, digitalWrite, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

LDR_DO  = 14
LED_PIN = 2

def setup():
    pinMode(LDR_DO,  0)    # INPUT
    pinMode(LED_PIN, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Auto Night Light")

def main():
    setup()
    while True:
        dark = digitalRead(LDR_DO) == 0   # LOW = dark
        digitalWrite(LED_PIN, 1 if dark else 0)
        lcd.move_to(0, 1)
        lcd.putstr("DARK → LED ON " if dark else "Bright→LED OFF")
        time.sleep_ms(200)

def cleanup():
    digitalWrite(LED_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Auto Night Light
DARK → LED ON
```

---

## D27 — PWM RGB Color Cycler

**Objective:** Cycle RGB LED through colors using PWM. Show color name on LCD.  
**Components:** Common cathode RGB LED + 220Ω each, I2C LCD  
**Pins:** R→2, G→4, B→5

```python
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

R_PIN = 2
G_PIN = 4
B_PIN = 5

COLORS = [
    ("Red    ", 1023,    0,    0),
    ("Green  ",    0, 1023,    0),
    ("Blue   ",    0,    0, 1023),
    ("Yellow ", 1023,  512,    0),
    ("Cyan   ",    0, 1023,  512),
    ("Magenta", 1023,    0,  512),
    ("White  ", 1023, 1023, 1023),
    ("Off    ",    0,    0,    0),
]

def setup():
    for pin in [R_PIN, G_PIN, B_PIN]:
        pwmSetup(pin, freq=1000)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    setup()
    while True:
        for name, r, g, b in COLORS:
            pwmWrite(R_PIN, r)
            pwmWrite(G_PIN, g)
            pwmWrite(B_PIN, b)
            lcd.move_to(0, 0)
            lcd.putstr("RGB Color Cycle ")
            lcd.move_to(0, 1)
            lcd.putstr(f"Color: {name}   ")
            time.sleep(1)

def cleanup():
    for pin in [R_PIN, G_PIN, B_PIN]:
        pwmStop(pin)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
RGB Color Cycle
Color: Cyan
```

---

## D28 — Edge Detector (Rising/Falling)

**Objective:** Detect and display rising and falling edges on a button or signal pin.  
**Components:** Push button, I2C LCD  
**Pin:** Button → GPIO 15

```python
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

SIG_PIN = 15
rising  = 0
falling = 0
prev    = None

def setup():
    pinMode(SIG_PIN, INPUT_PULLUP)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Edge Detector   ")

def main():
    global rising, falling, prev
    setup()
    while True:
        val = digitalRead(SIG_PIN)
        if prev is not None:
            if val == 1 and prev == 0: rising  += 1
            if val == 0 and prev == 1: falling += 1
        prev = val
        lcd.move_to(0, 1)
        lcd.putstr(f"R:{rising:4d} F:{falling:4d}")
        time.sleep_ms(10)

def cleanup():
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Edge Detector
R:   7 F:   7
```

---

## D29 — Two-Player Button Race

**Objective:** Two players press their buttons — first to press 5 times wins.  
**Components:** 2× push buttons, 2× LEDs, I2C LCD  
**Pins:** P1 Button→15, P2 Button→14, P1 LED→2, P2 LED→4

```python
from digital import pinMode, digitalRead, digitalWrite, blink, INPUT_PULLUP, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

P1_BTN  = 15
P2_BTN  = 14
P1_LED  = 2
P2_LED  = 4
TARGET  = 5

def setup():
    for pin in [P1_BTN, P2_BTN]: pinMode(pin, INPUT_PULLUP)
    for pin in [P1_LED, P2_LED]: pinMode(pin, OUTPUT)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def play_round():
    p1, p2     = 0, 0
    prev1, prev2 = False, False

    lcd.clear()
    lcd.move_to(0, 0); lcd.putstr("Press to Score! ")
    lcd.move_to(0, 1); lcd.putstr(f"P1:{p1} P2:{p2} Tgt:{TARGET}")

    while p1 < TARGET and p2 < TARGET:
        b1 = digitalRead(P1_BTN) == 0
        b2 = digitalRead(P2_BTN) == 0
        if b1 and not prev1: p1 += 1; digitalWrite(P1_LED, 1)
        else:                          digitalWrite(P1_LED, 0)
        if b2 and not prev2: p2 += 1; digitalWrite(P2_LED, 1)
        else:                          digitalWrite(P2_LED, 0)
        prev1, prev2 = b1, b2
        lcd.move_to(0, 1); lcd.putstr(f"P1:{p1} P2:{p2} Tgt:{TARGET}")
        time.sleep_ms(30)

    winner = "Player 1" if p1 >= TARGET else "Player 2"
    lcd.clear()
    lcd.move_to(0, 0); lcd.putstr(f"{winner} WINS!! ")
    led = P1_LED if p1 >= TARGET else P2_LED
    blink(led, 5, 150, 100)
    time.sleep(2)

def main():
    setup()
    while True:
        lcd.clear()
        lcd.move_to(0, 0); lcd.putstr("  2-Player Race ")
        lcd.move_to(0, 1); lcd.putstr("Press any button")
        if digitalRead(P1_BTN)==0 or digitalRead(P2_BTN)==0:
            play_round()
        time.sleep_ms(100)

def cleanup():
    for p in [P1_LED, P2_LED]: digitalWrite(p, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
Player 1 WINS!!
P1:5 P2:3 Tgt:5
```

---

## D30 — Full Digital Dashboard

**Objective:** Show button states, LED status, uptime, and PWM level all on one LCD.  
**Components:** 2× buttons, PWM LED, Buzzer, I2C LCD  
**Pins:** BTN1→15, BTN2→14, LED→2, Buzzer→26

```python
from digital import pinMode, digitalRead, digitalWrite, pwmSetup, pwmWrite, pwmStop, INPUT_PULLUP, OUTPUT
from systemio import run
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

BTN1_PIN   = 15
BTN2_PIN   = 14
LED_PIN    = 2
BUZZER_PIN = 26
start_ms   = time.ticks_ms()
pwm_level  = 0
prev_b1    = False
prev_b2    = False

def setup():
    pinMode(BTN1_PIN, INPUT_PULLUP)
    pinMode(BTN2_PIN, INPUT_PULLUP)
    pinMode(LED_PIN, OUTPUT)
    pwmSetup(BUZZER_PIN, freq=1000)
    pwmWrite(BUZZER_PIN, 0)
    global lcd
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()

def main():
    global pwm_level, prev_b1, prev_b2
    setup()
    while True:
        b1 = digitalRead(BTN1_PIN) == 0
        b2 = digitalRead(BTN2_PIN) == 0

        # B1: increase PWM
        if b1 and not prev_b1:
            pwm_level = min(1023, pwm_level + 200)
            pwmWrite(BUZZER_PIN, pwm_level)

        # B2: decrease PWM
        if b2 and not prev_b2:
            pwm_level = max(0, pwm_level - 200)
            pwmWrite(BUZZER_PIN, pwm_level)

        # LED follows B1
        digitalWrite(LED_PIN, 1 if b1 else 0)

        prev_b1, prev_b2 = b1, b2

        up_s = time.ticks_diff(time.ticks_ms(), start_ms) // 1000
        pct  = int(pwm_level / 1023 * 100)

        lcd.move_to(0, 0)
        lcd.putstr(f"B1={'1'if b1 else'0'} B2={'1'if b2 else'0'} Buz:{pct:3d}%")
        lcd.move_to(0, 1)
        lcd.putstr(f"Up:{up_s:5d}s LED:{'ON' if b1 else'OF'}")
        time.sleep_ms(50)

def cleanup():
    pwmStop(BUZZER_PIN)
    digitalWrite(LED_PIN, 0)
    lcd.clear()

run(main, cleanup)
```

**Expected Output:**
```
B1=1 B2=0 Buz: 40%
Up:   87s LED:ON
```

---

## Quick Pin Reference

| Label | Suggested GPIO | Type |
|-------|---------------|------|
| Potentiometer | 34 | Analog IN |
| LDR | 35 | Analog IN |
| Soil / Rain / Gas | 34 | Analog IN |
| Temperature (LM35) | 34 | Analog IN |
| Push Button 1 | 15 | Digital IN (PULLUP) |
| Push Button 2 | 14 | Digital IN (PULLUP) |
| PIR / Touch / Tilt | 14 | Digital IN |
| LED (status) | 2 | Digital OUT |
| LED (alert) | 4 | Digital OUT |
| LED (PWM/RGB R) | 2 | PWM OUT |
| LED (RGB G) | 4 | PWM OUT |
| LED (RGB B) | 5 | PWM OUT |
| Buzzer | 26 | Digital/PWM OUT |
| Relay IN | 26 | Digital OUT |
| I2C SDA (LCD) | 21 | I2C |
| I2C SCL (LCD) | 22 | I2C |

---

*ESP32 60-Project Reference · MicroPython · systemio + i2c_lcd library*

# ESP32 MicroPython OLED Display Projects

> All projects use your custom `oled.py` (OLED class) and `ssd1306.py` (SSD1306 class).
> Upload both files to your ESP32 before running any project.

---

## Library Quick Reference

### Using `oled.py` (OLED class)
```python
from oled import OLED
oled = OLED(scl=22, sda=21)   # Uses default I2C addr 0x3C
oled.clear()
oled.text("Hello", 0, 0)
oled.show()
```

### Using `ssd1306.py` (SSD1306 class)
```python
from machine import I2C, Pin
from ssd1306 import SSD1306
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = SSD1306(i2c, addr=0x3C)
oled.fill(0)
oled.text("Hello", 0, 0)
oled.show()
```

---

## Wiring

| OLED Pin | ESP32 Pin |
|----------|-----------|
| VCC      | 3.3V      |
| GND      | GND       |
| SCL      | GPIO 22   |
| SDA      | GPIO 21   |

---

# BEGINNER PROJECTS

---

## Project 1 — Hello World & Static Text Display

**Concepts:** Basic text rendering, screen layout, multi-line text

```python
from oled import OLED
import time

oled = OLED(scl=22, sda=21)

oled.clear()
oled.text("ESP32 + OLED", 8, 0)
oled.line(0, 10, 127, 10)          # Underline separator
oled.text("Hello, World!", 0, 20)
oled.text("MicroPython", 16, 36)
oled.text("by: YOU", 32, 52)
oled.show()
```

**Output:** Static greeting screen with a separator line.

---

## Project 2 — Digital Clock (No RTC)

**Concepts:** `time.ticks_ms()`, uptime counter, formatted strings

```python
from oled import OLED
import time

oled = OLED(scl=22, sda=21)

start = time.ticks_ms()

while True:
    elapsed = time.ticks_diff(time.ticks_ms(), start) // 1000
    h = elapsed // 3600
    m = (elapsed % 3600) // 60
    s = elapsed % 60

    oled.clear()
    oled.text("  UPTIME CLOCK", 0, 0)
    oled.line(0, 10, 127, 10)
    time_str = "{:02d}:{:02d}:{:02d}".format(h, m, s)
    oled.text(time_str, 24, 28)     # Centered-ish on 128px wide screen
    oled.text("hh : mm : ss", 16, 48)
    oled.show()
    time.sleep(1)
```

**Output:** Live uptime timer formatted as HH:MM:SS.

---

## Project 3 — Scrolling Message Ticker

**Concepts:** Horizontal pixel scrolling, string padding, looping animation

```python
from oled import OLED
import time

oled = OLED(scl=22, sda=21)

message = "  ** Welcome to ESP32 OLED Demo! Have fun with MicroPython! **  "
CHAR_W = 8       # Each character is 8 pixels wide
scroll_x = 128   # Start off-screen to the right

while True:
    oled.clear()
    oled.text("TICKER TAPE", 16, 0)
    oled.line(0, 10, 127, 10)

    # Draw the scrolling message at current x position
    oled.fb.text(message, scroll_x, 28, 1)   # Access framebuffer directly
    oled.show()

    scroll_x -= 2   # Move 2 pixels left per frame
    if scroll_x < -(len(message) * CHAR_W):
        scroll_x = 128   # Reset to right side

    time.sleep_ms(40)
```

**Note:** Accesses `oled.fb` (the FrameBuffer) directly for pixel-positioned text.

---

## Project 4 — Animated Progress Bar

**Concepts:** `fill_rect`, dynamic width, percentage display

```python
from oled import OLED
import time

oled = OLED(scl=22, sda=21)

for pct in range(0, 101, 2):
    oled.clear()
    oled.text("Loading...", 24, 0)
    oled.text("{}%".format(pct), 52, 20)

    bar_x, bar_y, bar_h = 4, 40, 14
    bar_total_w = 120
    filled_w = int(bar_total_w * pct / 100)

    oled.rect(bar_x, bar_y, bar_total_w, bar_h)          # Border
    oled.fb.fill_rect(bar_x, bar_y, filled_w, bar_h, 1)  # Fill
    oled.show()
    time.sleep_ms(60)

oled.clear()
oled.text("  DONE!", 24, 24)
oled.show()
```

---

# INTERMEDIATE PROJECTS

---

## Project 5 — Analog Clock Face

**Concepts:** Trigonometry, clock hands, `math.sin/cos`, drawing circles

```python
from oled import OLED
import math, time

oled = OLED(scl=22, sda=21)

CX, CY, R = 32, 32, 30   # Center x, center y, radius

def draw_hand(fb, cx, cy, angle_deg, length, color=1):
    """Draw a clock hand from center at given angle and length."""
    rad = math.radians(angle_deg - 90)
    x2 = int(cx + length * math.cos(rad))
    y2 = int(cy + length * math.sin(rad))
    fb.line(cx, cy, x2, y2, color)

def draw_tick(fb, cx, cy, radius, angle_deg, tick_len=4):
    """Draw hour tick mark on circle edge."""
    rad = math.radians(angle_deg - 90)
    x1 = int(cx + (radius - tick_len) * math.cos(rad))
    y1 = int(cy + (radius - tick_len) * math.sin(rad))
    x2 = int(cx + radius * math.cos(rad))
    y2 = int(cy + radius * math.sin(rad))
    fb.line(x1, y1, x2, y2, 1)

start = time.ticks_ms()

while True:
    elapsed = time.ticks_diff(time.ticks_ms(), start) // 1000
    sec  = elapsed % 60
    minu = (elapsed // 60) % 60
    hour = (elapsed // 3600) % 12

    sec_angle  = sec * 6             # 360 / 60 = 6 deg per second
    min_angle  = minu * 6 + sec * 0.1
    hour_angle = hour * 30 + minu * 0.5

    oled.clear()

    # Draw clock circle & hour ticks
    oled.fb.ellipse(CX, CY, R, R, 1)
    for i in range(12):
        draw_tick(oled.fb, CX, CY, R, i * 30)

    # Draw hands
    draw_hand(oled.fb, CX, CY, hour_angle, 14)   # Hour (short)
    draw_hand(oled.fb, CX, CY, min_angle,  22)   # Minute
    draw_hand(oled.fb, CX, CY, sec_angle,  27)   # Second (long)

    # Digital time on right side
    oled.text("{:02d}:{:02d}".format(int(hour) if int(hour) > 0 else 12, minu), 72, 20)
    oled.text("{:02d}s".format(sec), 80, 36)

    oled.show()
    time.sleep_ms(200)
```

**Note:** `ellipse()` is available in MicroPython 1.20+. For older firmware replace with a Bresenham circle routine.

---

## Project 6 — Temperature & Humidity Dashboard (DHT11/DHT22)

**Concepts:** Sensor reading, exception handling, bar gauge, status icons

**Hardware:** DHT11 or DHT22 on GPIO 4

```python
from oled import OLED
from machine import Pin
import dht, time

oled  = OLED(scl=22, sda=21)
sensor = dht.DHT22(Pin(4))    # Change to dht.DHT11 if using DHT11

def draw_gauge(fb, x, y, w, h, value, vmin, vmax, label):
    """Horizontal bar gauge from vmin to vmax."""
    fb.rect(x, y, w, h, 1)
    pct   = max(0, min(1, (value - vmin) / (vmax - vmin)))
    filled = int((w - 2) * pct)
    fb.fill_rect(x + 1, y + 1, filled, h - 2, 1)
    fb.text(label, x + w + 2, y, 1)

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        humi = sensor.humidity()

        oled.clear()
        oled.text("ENVIRONMENT", 8, 0)
        oled.line(0, 10, 127, 10)

        # Temperature row
        oled.text("T:", 0, 16)
        oled.text("{:.1f}C".format(temp), 80, 16)
        draw_gauge(oled.fb, 16, 16, 60, 8, temp, 0, 50, "")

        # Humidity row
        oled.text("H:", 0, 32)
        oled.text("{:.0f}%".format(humi), 80, 32)
        draw_gauge(oled.fb, 16, 32, 60, 8, humi, 0, 100, "")

        # Status message
        if temp > 35:
            status = "!! HOT !!"
        elif humi > 80:
            status = "HUMID"
        else:
            status = "NORMAL"
        oled.text(status, 40, 50)

    except OSError:
        oled.clear()
        oled.text("SENSOR ERROR", 8, 28)

    oled.show()
    time.sleep(2)
```

---

## Project 7 — Message Notification Display

**Concepts:** Multi-page messages, button input, page counter, word wrap

**Hardware:** Push button on GPIO 0 (BOOT button on most boards)

```python
from oled import OLED
from machine import Pin
import time

oled   = OLED(scl=22, sda=21)
btn    = Pin(0, Pin.IN, Pin.PULL_UP)   # BOOT button = GPIO 0

messages = [
    {"from": "Alice",  "body": "Hey! Are you free tonight for dinner?"},
    {"from": "Server", "body": "CPU usage is above 90 percent!"},
    {"from": "Bob",    "body": "The package has been delivered."},
    {"from": "System", "body": "Battery low: 15 percent remaining."},
]

def wrap_text(text, max_chars=16):
    """Split text into lines of max_chars."""
    words, lines, current = text.split(), [], ""
    for w in words:
        if len(current) + len(w) + 1 <= max_chars:
            current += ("" if current == "" else " ") + w
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

page = 0
prev_btn = 1

while True:
    curr_btn = btn.value()
    if prev_btn == 1 and curr_btn == 0:   # Falling edge = button pressed
        page = (page + 1) % len(messages)
        time.sleep_ms(50)                  # Debounce

    msg = messages[page]
    lines = wrap_text(msg["body"])

    oled.clear()
    # Header bar
    oled.fb.fill_rect(0, 0, 128, 11, 1)
    oled.fb.text("From: " + msg["from"][:9], 0, 2, 0)
    oled.text("[{}/{}]".format(page + 1, len(messages)), 88, 2)

    for i, line in enumerate(lines[:4]):   # Max 4 lines
        oled.text(line, 0, 14 + i * 12)

    oled.show()
    prev_btn = curr_btn
    time.sleep_ms(20)
```

---

## Project 8 — Real-Time Oscilloscope (ADC Waveform)

**Concepts:** ADC sampling, waveform scrolling buffer, live graph rendering

**Hardware:** Signal (0–3.3V) on GPIO 34 (ADC1_CH6)

```python
from oled import OLED
from machine import ADC, Pin
import time

oled = OLED(scl=22, sda=21)
adc  = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)    # Full 0–3.3V range

GRAPH_X = 0
GRAPH_Y = 14
GRAPH_W = 128
GRAPH_H = 48
samples = [GRAPH_H // 2] * GRAPH_W   # Ring buffer initialized to midpoint

while True:
    # Read new sample, scale to graph height
    raw   = adc.read()                                 # 0–4095
    pixel = GRAPH_H - int(raw / 4095 * GRAPH_H) - 1   # Invert Y axis
    samples.pop(0)
    samples.append(pixel)

    voltage = raw * 3.3 / 4095

    oled.clear()
    oled.text("SCOPE  {:.2f}V".format(voltage), 0, 2)
    oled.line(GRAPH_X, GRAPH_Y, GRAPH_X + GRAPH_W, GRAPH_Y, 1)   # Top border

    # Plot waveform
    for x in range(1, GRAPH_W):
        y1 = GRAPH_Y + samples[x - 1]
        y2 = GRAPH_Y + samples[x]
        oled.fb.line(x - 1, y1, x, y2, 1)

    oled.show()
    time.sleep_ms(10)
```

---

## Project 9 — Menu System with Navigation

**Concepts:** State machine, button navigation, selected item highlight, sub-menus

**Hardware:** UP=GPIO 12, DOWN=GPIO 14, SELECT=GPIO 27

```python
from oled import OLED
from machine import Pin
import time

oled = OLED(scl=22, sda=21)

btn_up  = Pin(12, Pin.IN, Pin.PULL_UP)
btn_dn  = Pin(14, Pin.IN, Pin.PULL_UP)
btn_sel = Pin(27, Pin.IN, Pin.PULL_UP)

MENU_ITEMS = ["Settings", "Sensors", "Display", "Network", "About"]
VISIBLE    = 4    # Lines visible at once
cursor     = 0
scroll_top = 0
selected   = None

def debounce(pin):
    if pin.value() == 0:
        time.sleep_ms(40)
        return pin.value() == 0
    return False

while True:
    # --- Input ---
    if debounce(btn_up):
        cursor = (cursor - 1) % len(MENU_ITEMS)
        if cursor < scroll_top:
            scroll_top = cursor
        time.sleep_ms(150)

    if debounce(btn_dn):
        cursor = (cursor + 1) % len(MENU_ITEMS)
        if cursor >= scroll_top + VISIBLE:
            scroll_top = cursor - VISIBLE + 1
        time.sleep_ms(150)

    if debounce(btn_sel):
        selected = MENU_ITEMS[cursor]
        time.sleep_ms(200)

    # --- Draw ---
    oled.clear()
    # Header
    oled.fb.fill_rect(0, 0, 128, 11, 1)
    oled.fb.text("  MAIN MENU", 0, 2, 0)

    for i in range(VISIBLE):
        idx = scroll_top + i
        if idx >= len(MENU_ITEMS):
            break
        y = 14 + i * 13
        if idx == cursor:
            oled.fb.fill_rect(0, y - 1, 128, 12, 1)
            oled.fb.text("> " + MENU_ITEMS[idx], 0, y, 0)
        else:
            oled.text("  " + MENU_ITEMS[idx], 0, y)

    if selected:
        oled.clear()
        oled.text("Selected:", 20, 16)
        oled.text(selected, 20, 32)
        oled.show()
        time.sleep(1)
        selected = None
        continue

    # Scroll indicator dots
    for i in range(len(MENU_ITEMS)):
        dot_y = 14 + int(i * 50 / len(MENU_ITEMS))
        oled.fb.pixel(126, dot_y, 1)
    oled.fb.fill_rect(125, 14 + int(cursor * 50 / len(MENU_ITEMS)), 3, 4, 1)

    oled.show()
    time.sleep_ms(20)
```

---

# ADVANCED PROJECTS

---

## Project 10 — Wi-Fi Connected Live Weather Display

**Concepts:** `urequests`, JSON parsing, Wi-Fi connect, multi-screen refresh

**Hardware:** ESP32 with Wi-Fi (built-in)

```python
from oled import OLED
from machine import Pin
import network, urequests, time, json

# ---- CONFIG ----
SSID     = "YourWiFiName"
PASSWORD = "YourPassword"
# Free API — no key needed for basic weather
CITY    = "Chennai"
API_URL = "http://wttr.in/{}?format=j1".format(CITY)
# ----------------

oled = OLED(scl=22, sda=21)

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    oled.clear()
    oled.text("Connecting...", 8, 28)
    oled.show()
    for _ in range(20):
        if wlan.isconnected():
            return True
        time.sleep(1)
    return False

def fetch_weather():
    try:
        r    = urequests.get(API_URL, timeout=10)
        data = r.json()
        r.close()
        curr = data["current_condition"][0]
        return {
            "temp_c": curr["temp_C"],
            "feels":  curr["FeelsLikeC"],
            "desc":   curr["weatherDesc"][0]["value"][:12],
            "humid":  curr["humidity"],
            "wind":   curr["windspeedKmph"],
        }
    except Exception as e:
        return None

if not wifi_connect():
    oled.clear()
    oled.text("WiFi FAILED", 16, 28)
    oled.show()
else:
    while True:
        w = fetch_weather()
        oled.clear()
        if w:
            oled.fb.fill_rect(0, 0, 128, 11, 1)
            oled.fb.text(" " + CITY + " WEATHER", 0, 2, 0)
            oled.text("Temp:  {}C".format(w["temp_c"]),  0, 14)
            oled.text("Feels: {}C".format(w["feels"]),   0, 24)
            oled.text("Hum:   {}%".format(w["humid"]),   0, 34)
            oled.text("Wind:  {}km/h".format(w["wind"]), 0, 44)
            oled.text(w["desc"], 0, 54)
        else:
            oled.text("Fetch failed", 16, 28)
        oled.show()
        time.sleep(300)   # Refresh every 5 minutes
```

---

## Project 11 — MQTT Notification Display

**Concepts:** MQTT subscribe, `umqtt.simple`, topic-based display, reconnect logic

**Hardware:** ESP32 with Wi-Fi; needs `umqtt.simple` library

```python
from oled import OLED
import network, time
from umqtt.simple import MQTTClient

SSID     = "YourWiFiName"
PASSWORD = "YourPassword"
BROKER   = "broker.hivemq.com"   # Free public broker
TOPIC    = b"esp32/oled/msg"

oled      = OLED(scl=22, sda=21)
last_msg  = "Waiting..."
last_from = "MQTT"

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    for _ in range(20):
        if wlan.isconnected():
            return True
        time.sleep(1)
    return False

def on_message(topic, msg):
    global last_msg, last_from
    payload = msg.decode()
    if "|" in payload:
        parts = payload.split("|", 1)
        last_from, last_msg = parts[0][:12], parts[1][:48]
    else:
        last_msg = payload[:48]

def draw_notification():
    oled.clear()
    oled.fb.fill_rect(0, 0, 128, 11, 1)
    oled.fb.text(last_from, 0, 2, 0)
    # Simple word wrap
    words, line, y = last_msg.split(), "", 14
    for w in words:
        if len(line) + len(w) <= 16:
            line += ("" if not line else " ") + w
        else:
            if y < 56:
                oled.text(line, 0, y)
                y += 12
            line = w
    if line and y < 64:
        oled.text(line, 0, y)
    oled.show()

wifi_connect()
client = MQTTClient("esp32_oled", BROKER)
client.set_callback(on_message)
client.connect()
client.subscribe(TOPIC)

oled.clear()
oled.text("MQTT Ready", 16, 20)
oled.text(BROKER[:16], 0, 36)
oled.show()

while True:
    try:
        client.check_msg()
        draw_notification()
    except Exception:
        time.sleep(5)
        client.connect()
        client.subscribe(TOPIC)
    time.sleep_ms(100)
```

**Test from any MQTT client:**
```
Topic: esp32/oled/msg
Payload: Alice|Hey! Your order is ready for pickup.
```

---

## Project 12 — Multi-Sensor Data Logger with SSD1306

**Concepts:** Multiple sensors, page cycling, `SSD1306.draw_status_bar()`, NVS-style log in memory

**Hardware:** DHT22 on GPIO 4, LDR (via ADC) on GPIO 35, button on GPIO 0

```python
from machine import I2C, Pin, ADC
from ssd1306 import SSD1306
import dht, time

i2c  = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = SSD1306(i2c)
dht_sensor = dht.DHT22(Pin(4))
ldr  = ADC(Pin(35))
ldr.atten(ADC.ATTN_11DB)
btn  = Pin(0, Pin.IN, Pin.PULL_UP)

LOG_MAX = 20
log = []     # Stores dicts: {t, h, lux, ts}

pages   = ["TEMP", "HUMIDITY", "LIGHT", "LOG"]
page    = 0
prev_btn = 1
tick    = 0

def lux_from_adc(raw):
    """Convert ADC reading to approximate lux (depends on LDR circuit)."""
    return int(raw / 4095 * 1000)

def read_sensors():
    try:
        dht_sensor.measure()
        return dht_sensor.temperature(), dht_sensor.humidity()
    except:
        return None, None

while True:
    tick += 1
    curr_btn = btn.value()

    if prev_btn == 1 and curr_btn == 0:
        page = (page + 1) % len(pages)
        time.sleep_ms(50)

    # Sample every 30 ticks (~3s)
    if tick % 30 == 0:
        t, h = read_sensors()
        lux  = lux_from_adc(ldr.read())
        if t is not None:
            log.append({"t": t, "h": h, "lux": lux})
            if len(log) > LOG_MAX:
                log.pop(0)

    last = log[-1] if log else {"t": 0, "h": 0, "lux": 0}

    oled.fill(0)

    if pages[page] == "TEMP":
        oled.draw_status_bar("TEMPERATURE", "{:.1f} C".format(last["t"]))
        # Mini bar graph of last 8 readings
        for i, entry in enumerate(log[-8:]):
            bh = int((entry["t"] / 50) * 30)
            oled.rect(i * 15 + 4, 62 - bh, 12, bh, 1, fill=True)

    elif pages[page] == "HUMIDITY":
        oled.draw_status_bar("HUMIDITY", "{:.0f} %".format(last["h"]))
        for i, entry in enumerate(log[-8:]):
            bh = int((entry["h"] / 100) * 30)
            oled.rect(i * 15 + 4, 62 - bh, 12, bh, 1, fill=True)

    elif pages[page] == "LIGHT":
        oled.draw_status_bar("LIGHT", "{} lux".format(last["lux"]))
        for i, entry in enumerate(log[-8:]):
            bh = int((entry["lux"] / 1000) * 30)
            oled.rect(i * 15 + 4, 62 - bh, 12, bh, 1, fill=True)

    elif pages[page] == "LOG":
        # Show last 4 readings as table
        oled.rect(0, 0, 128, 11, 1, fill=True)
        oled.text("T    H    LUX", 0, 2, color=0)
        for i, entry in enumerate(log[-4:]):
            row = "{:<4.0f} {:<4.0f} {}".format(entry["t"], entry["h"], entry["lux"])
            oled.text(row, 0, 14 + i * 12)

    # Page indicator dots at bottom
    for i in range(len(pages)):
        x = 52 + i * 8
        if i == page:
            oled.rect(x, 60, 5, 5, 1, fill=True)
        else:
            oled.rect(x, 60, 5, 5, 1)

    oled.show()
    prev_btn = curr_btn
    time.sleep_ms(100)
```

---

## Project 13 — Pong Game (Two Player)

**Concepts:** Game loop, collision detection, score tracking, paddles, ball physics

**Hardware:** P1 UP=GPIO 12, P1 DN=GPIO 14, P2 UP=GPIO 26, P2 DN=GPIO 25

```python
from oled import OLED
from machine import Pin
import time, random

oled = OLED(scl=22, sda=21)

p1_up = Pin(12, Pin.IN, Pin.PULL_UP)
p1_dn = Pin(14, Pin.IN, Pin.PULL_UP)
p2_up = Pin(26, Pin.IN, Pin.PULL_UP)
p2_dn = Pin(25, Pin.IN, Pin.PULL_UP)

W, H     = 128, 64
PAD_W    = 3
PAD_H    = 12
PAD_SPD  = 3
BALL_SPD = 2

score    = [0, 0]
p1y = p2y = H // 2 - PAD_H // 2
bx, by   = W // 2, H // 2
bdx = BALL_SPD * random.choice([-1, 1])
bdy = BALL_SPD * random.choice([-1, 1])

def reset_ball():
    global bx, by, bdx, bdy
    bx, by = W // 2, H // 2
    bdx = BALL_SPD * random.choice([-1, 1])
    bdy = BALL_SPD * random.choice([-1, 1])

while True:
    # --- Input ---
    if not p1_up.value(): p1y = max(0, p1y - PAD_SPD)
    if not p1_dn.value(): p1y = min(H - PAD_H, p1y + PAD_SPD)
    if not p2_up.value(): p2y = max(0, p2y - PAD_SPD)
    if not p2_dn.value(): p2y = min(H - PAD_H, p2y + PAD_SPD)

    # --- Physics ---
    bx += bdx
    by += bdy

    if by <= 0 or by >= H - 1:
        bdy = -bdy

    # P1 paddle (left side, x=0..PAD_W)
    if bx <= PAD_W + 1 and p1y <= by <= p1y + PAD_H:
        bdx = abs(bdx)
        bdy += random.randint(-1, 1)

    # P2 paddle (right side, x=W-PAD_W..W)
    if bx >= W - PAD_W - 2 and p2y <= by <= p2y + PAD_H:
        bdx = -abs(bdx)
        bdy += random.randint(-1, 1)

    # Score
    if bx < 0:
        score[1] += 1
        reset_ball()
    if bx > W:
        score[0] += 1
        reset_ball()

    bdy = max(-4, min(4, bdy))   # Cap ball vertical speed

    # --- Draw ---
    oled.clear()
    # Center dashed line
    for y in range(0, H, 6):
        oled.fb.pixel(W // 2, y, 1)

    # Score
    oled.text(str(score[0]), W // 2 - 20, 2)
    oled.text(str(score[1]), W // 2 + 12, 2)

    # Paddles
    oled.fb.fill_rect(0,       p1y, PAD_W, PAD_H, 1)
    oled.fb.fill_rect(W - PAD_W, p2y, PAD_W, PAD_H, 1)

    # Ball
    oled.fb.fill_rect(bx - 1, by - 1, 3, 3, 1)

    oled.show()
    time.sleep_ms(16)   # ~60 FPS target
```

---

## Project 14 — Spectrum Analyzer (FFT Visualizer)

**Concepts:** FFT on ADC input, bar chart display, `ulab.numpy`, frequency bins

**Hardware:** Audio signal (via mic module) on GPIO 34. Requires `ulab` firmware.

```python
from oled import OLED
from machine import ADC, Pin
from ulab import numpy as np
import time

oled = OLED(scl=22, sda=21)
adc  = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)

SAMPLES = 64       # FFT size (power of 2)
BARS    = 16       # Number of frequency bars to display
BAR_W   = 128 // BARS

def sample():
    buf = []
    for _ in range(SAMPLES):
        buf.append(adc.read() - 2048)   # Centre around zero
    return np.array(buf, dtype=np.float)

while True:
    data = sample()

    # Windowing (Hann window reduces spectral leakage)
    n    = len(data)
    hann = 0.5 * (1 - np.cos(2 * 3.14159 * np.arange(n) / (n - 1)))
    windowed = data * hann

    # FFT
    freqs  = np.fft.fft(windowed)
    magnitudes = np.abs(freqs[:n // 2])    # Only positive frequencies

    # Bin magnitudes into BARS groups
    bin_size = len(magnitudes) // BARS
    bars = []
    for i in range(BARS):
        chunk = magnitudes[i * bin_size:(i + 1) * bin_size]
        bars.append(float(np.max(chunk)))

    # Normalize to display height
    max_val = max(bars) if max(bars) > 0 else 1
    bar_heights = [int(b / max_val * 52) for b in bars]

    oled.clear()
    oled.text("SPECTRUM", 28, 0)
    oled.line(0, 10, 127, 10)

    for i, h in enumerate(bar_heights):
        x = i * BAR_W
        if h > 0:
            oled.fb.fill_rect(x, 63 - h, BAR_W - 1, h, 1)

    oled.show()
    time.sleep_ms(30)
```

**Note:** Requires MicroPython firmware with `ulab` built in. Flash `ulab-enabled` firmware from `micropython.org/download/esp32`.

---

## Project 15 — Pomodoro Timer with Productivity Stats

**Concepts:** State machine, timer modes, stats persistence, animated countdown ring

```python
from oled import OLED
from machine import Pin
import time, math

oled  = OLED(scl=22, sda=21)
btn   = Pin(0, Pin.IN, Pin.PULL_UP)

WORK_MINS   = 25
BREAK_MINS  = 5
LONG_BREAK  = 15

states      = ["WORK", "BREAK", "LONG_BREAK", "PAUSED"]
state       = "WORK"
remaining   = WORK_MINS * 60
pomodoros   = 0
paused      = False
prev_btn    = 1
last_tick   = time.ticks_ms()

def draw_arc(fb, cx, cy, r, pct, color=1):
    """Draw an arc from 270° (top) spanning pct * 360 degrees clockwise."""
    steps  = 60
    total  = int(pct * steps)
    for i in range(total):
        angle = math.radians(270 + i * 360 / steps)
        x = int(cx + r * math.cos(angle))
        y = int(cy + r * math.sin(angle))
        fb.pixel(x, y, color)

while True:
    now = time.ticks_ms()
    curr_btn = btn.value()

    # Button: toggle pause / advance on long press
    if prev_btn == 1 and curr_btn == 0:
        paused = not paused
        time.sleep_ms(50)

    if not paused:
        elapsed_ms = time.ticks_diff(now, last_tick)
        if elapsed_ms >= 1000:
            remaining -= 1
            last_tick = now
            if remaining <= 0:
                if state == "WORK":
                    pomodoros += 1
                    state     = "LONG_BREAK" if pomodoros % 4 == 0 else "BREAK"
                    remaining = (LONG_BREAK if state == "LONG_BREAK" else BREAK_MINS) * 60
                else:
                    state     = "WORK"
                    remaining = WORK_MINS * 60

    total_secs = (WORK_MINS if state == "WORK" else (LONG_BREAK if state == "LONG_BREAK" else BREAK_MINS)) * 60
    pct_left   = remaining / total_secs
    mins, secs = remaining // 60, remaining % 60

    oled.clear()

    # Arc ring (right half of screen)
    CX, CY, R = 96, 36, 25
    oled.fb.ellipse(CX, CY, R, R, 1)                         # Background ring
    draw_arc(oled.fb, CX, CY, R, 1 - pct_left, 0)           # Erase consumed arc

    # State label & countdown (left side)
    oled.fb.fill_rect(0, 0, 70, 11, 1)
    label = state.replace("_", " ")
    oled.fb.text(label[:8], 2, 2, 0)
    oled.text("{:02d}:{:02d}".format(mins, secs), 4, 18)
    oled.text("No. {}".format(pomodoros), 4, 34)
    if paused:
        oled.text("PAUSED", 4, 50)
    else:
        oled.text("btn=pause", 0, 50)

    oled.show()
    prev_btn = curr_btn
    time.sleep_ms(50)
```

---

# TIPS & TRICKS

## Centering Text

```python
def center_text(oled, text, y):
    x = max(0, (128 - len(text) * 8) // 2)
    oled.text(text, x, y)
```

## Custom Icons (1-bit sprites)

```python
import framebuf

# 16x16 heart icon (1-bit, MONO_HLSB)
HEART = bytearray([
    0b00110011, 0b00000000,
    0b01111111, 0b10000000,
    0b11111111, 0b11000000,
    0b11111111, 0b11000000,
    0b11111111, 0b11000000,
    0b01111111, 0b10000000,
    0b00111111, 0b00000000,
    0b00011110, 0b00000000,
    0b00001100, 0b00000000,
    0b00000000, 0b00000000,
])
icon_fb = framebuf.FrameBuffer(HEART, 16, 10, framebuf.MONO_HLSB)
oled.fb.blit(icon_fb, 56, 27)   # Blit to center
oled.show()
```

## Contrast Control (SSD1306 only)

```python
oled.contrast(0)    # Dimmest
oled.contrast(128)  # Medium
oled.contrast(255)  # Brightest
```

## Invert Display (SSD1306 only)

```python
oled.invert(True)   # White background, black text
oled.invert(False)  # Back to normal
```

## Power Save

```python
oled.power(False)   # Turn off display (content stays in RAM)
oled.power(True)    # Turn back on
```

---

# PROJECT SUMMARY

| # | Project | Level | Key Concepts |
|---|---------|-------|-------------|
| 1 | Hello World | Beginner | Text, lines |
| 2 | Digital Clock | Beginner | Time, formatted strings |
| 3 | Scrolling Ticker | Beginner | Pixel scrolling, framebuffer |
| 4 | Progress Bar | Beginner | `fill_rect`, percentage |
| 5 | Analog Clock | Intermediate | Trigonometry, hands |
| 6 | Temp/Humidity Dashboard | Intermediate | DHT22, gauges |
| 7 | Message Notification | Intermediate | Button input, word wrap |
| 8 | Oscilloscope | Intermediate | ADC, waveform buffer |
| 9 | Menu System | Intermediate | State machine, navigation |
| 10 | Live Weather (Wi-Fi) | Advanced | urequests, JSON, API |
| 11 | MQTT Notifications | Advanced | MQTT subscribe, topics |
| 12 | Multi-Sensor Logger | Advanced | Multi-page, bar charts |
| 13 | Pong Game | Advanced | Game loop, collision |
| 14 | Spectrum Analyzer | Advanced | FFT, ulab, frequency bins |
| 15 | Pomodoro Timer | Advanced | State machine, arc drawing |

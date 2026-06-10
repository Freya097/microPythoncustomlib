# 50 ESP32 MicroPython Projects
### Using `oled.py` · `wifi.py` · `systemio.py`

> **Each project fits in 10–30 lines of code with safe Ctrl-C exit via `systemio.run()`**

---

## Required Files on ESP32

| File | Purpose |
|------|---------|
| `oled.py` | OLED SSD1306 display driver (I2C, addr 0x3C) |
| `wifi.py` | WiFi connect, HTTP GET/POST, UDP, AP mode |
| `systemio.py` | Safe `run(main, cleanup)` handler |

**Default Wiring:** SDA = GPIO21 · SCL = GPIO22 · OLED addr = `0x3C`

**How to use:** Copy any project below into `main.py` and flash to your ESP32.

---

## 🟢 Basic Level — Projects 1–20
*Digital I/O · Analog · OLED display fundamentals*

---

### Project 1 — Hello World on OLED

**Concepts:** `splash()`, boot message

```python
from oled import OLED
import systemio

oled = OLED()

def main():
    oled.splash("Hello!", "ESP32 Ready", delay_ms=0)
    while True:
        pass

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 2 — Blinking LED with OLED Status

**Concepts:** `Pin`, `print_line()`, digital output

```python
from oled import OLED
from machine import Pin
from time import sleep
import systemio

oled = OLED()
led  = Pin(2, Pin.OUT)

def main():
    while True:
        led.on();  oled.print_line("LED: ON",  0, clear_first=True)
        sleep(0.5)
        led.off(); oled.print_line("LED: OFF", 0, clear_first=True)
        sleep(0.5)

def cleanup():
    led.off(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 3 — Counter Display

**Concepts:** `center_text()`, infinite counter loop

```python
from oled import OLED
from time import sleep
import systemio

oled = OLED()
count = 0

def main():
    global count
    while True:
        oled.clear(); oled.center_text("Count:", 20)
        oled.center_text(str(count), 36); oled.show()
        count += 1
        sleep(1)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 4 — Button Press Counter

**Concepts:** `Pin.IN`, `PULL_UP`, debounce, edge detection

```python
from oled import OLED
from machine import Pin
from time import sleep_ms
import systemio

oled  = OLED()
btn   = Pin(0, Pin.IN, Pin.PULL_UP)
count = 0

def main():
    global count
    prev = 1
    while True:
        cur = btn.value()
        if prev == 1 and cur == 0:
            count += 1
            oled.clear(); oled.center_text("Presses:", 20)
            oled.center_text(str(count), 36); oled.show()
        prev = cur; sleep_ms(50)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 5 — Digital Uptime Clock

**Concepts:** `ticks_ms()`, time formatting, HH:MM:SS display

```python
from oled import OLED
from time import sleep, ticks_ms
import systemio

oled = OLED()

def main():
    while True:
        secs = ticks_ms() // 1000
        h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
        oled.clear()
        oled.center_text("Uptime", 10)
        oled.center_text("{:02d}:{:02d}:{:02d}".format(h, m, s), 30)
        oled.show(); sleep(1)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 6 — Potentiometer Meter

**Concepts:** `ADC`, `ATTN_11DB`, `h_bar()` progress bar

```python
from oled import OLED
from machine import ADC, Pin
from time import sleep_ms
import systemio

oled = OLED()
pot  = ADC(Pin(34)); pot.atten(ADC.ATTN_11DB)

def main():
    while True:
        val = pot.read()
        pct = val * 100 // 4095
        oled.clear()
        oled.status_bar("POT", "{}%".format(pct))
        oled.h_bar(2, 20, 124, 14, pct, 100)
        oled.center_text("{}  {}%".format(val, pct), 42)
        oled.show(); sleep_ms(100)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 7 — PWM LED Brightness Control

**Concepts:** `PWM`, duty cycle, ADC to PWM mapping

```python
from oled import OLED
from machine import ADC, Pin, PWM
from time import sleep_ms
import systemio

oled = OLED()
pot  = ADC(Pin(34)); pot.atten(ADC.ATTN_11DB)
pwm  = PWM(Pin(2), freq=1000)

def main():
    while True:
        val  = pot.read()
        duty = val * 1023 // 4095
        pwm.duty(duty)
        pct  = duty * 100 // 1023
        oled.clear(); oled.status_bar("PWM LED")
        oled.h_bar(2, 20, 124, 14, pct, 100)
        oled.center_text("Duty: {}".format(duty), 42)
        oled.show(); sleep_ms(100)

def cleanup():
    pwm.deinit(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 8 — Digital Input Monitor

**Concepts:** `Pin.IN`, sensor reading, ON/OFF display

```python
from oled import OLED
from machine import Pin
from time import sleep_ms
import systemio

oled   = OLED()
sensor = Pin(14, Pin.IN, Pin.PULL_UP)

def main():
    while True:
        state = "ON" if sensor.value() == 0 else "OFF"
        oled.clear(); oled.center_text("Digital IN", 15)
        oled.center_text(state, 35); oled.show()
        sleep_ms(200)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 9 — WiFi Connect and Show IP

**Concepts:** `wifi.connect()`, `wifi.ip()`, connection status

```python
from oled import OLED
import wifi, systemio

oled = OLED()

def main():
    oled.splash("Connecting", "WiFi...", delay_ms=500)
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    if wifi.connect():
        oled.clear(); oled.status_bar("WiFi OK")
        oled.center_text(wifi.ip(), 30); oled.show()
    else:
        oled.splash("WiFi FAIL", "Check creds")
    while True:
        pass

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 10 — Scrolling Text Banner

**Concepts:** `marquee()`, animated text, offset loop

```python
from oled import OLED
from time import sleep_ms
import systemio

oled = OLED()
msg  = "Welcome to MicroPython on ESP32!   "
off  = 0

def main():
    global off
    while True:
        oled.clear(); off = oled.marquee(msg, off, y=28)
        oled.show(); sleep_ms(30)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 11 — NTC Thermistor Temperature

**Concepts:** ADC, Steinhart-Hart equation, temperature calculation

```python
from oled import OLED
from machine import ADC, Pin
from time import sleep
import math, systemio

oled = OLED()
adc  = ADC(Pin(34)); adc.atten(ADC.ATTN_11DB)

def read_temp():
    raw = adc.read()
    r   = 10000 * raw / (4095 - raw)
    t   = 1 / (math.log(r / 10000) / 3950 + 1/298.15) - 273.15
    return round(t, 1)

def main():
    while True:
        t = read_temp()
        oled.clear(); oled.status_bar("TEMP")
        oled.center_text("{} C".format(t), 30); oled.show()
        sleep(1)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 12 — LDR Light Level Meter

**Concepts:** ADC, percentage mapping, conditional labels

```python
from oled import OLED
from machine import ADC, Pin
from time import sleep_ms
import systemio

oled = OLED()
ldr  = ADC(Pin(35)); ldr.atten(ADC.ATTN_11DB)

def main():
    while True:
        val  = ldr.read()
        pct  = val * 100 // 4095
        oled.clear(); oled.status_bar("LIGHT", "{}%".format(pct))
        oled.h_bar(2, 20, 124, 14, pct, 100)
        label = "Dark" if pct < 30 else "Dim" if pct < 70 else "Bright"
        oled.center_text(label, 44); oled.show(); sleep_ms(300)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 13 — Buzzer Beep on Button Press

**Concepts:** `PWM` buzzer, tone generation, button trigger

```python
from oled import OLED
from machine import Pin, PWM
from time import sleep_ms
import systemio

oled   = OLED()
btn    = Pin(0, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(5), freq=1000, duty=0)

def beep(ms=200):
    buzzer.duty(512); sleep_ms(ms); buzzer.duty(0)

def main():
    oled.splash("Press BTN", "to beep")
    while True:
        if btn.value() == 0:
            beep(200)
            oled.print_line("BEEP!", 3, clear_first=True)
            sleep_ms(300)

def cleanup():
    buzzer.deinit(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 14 — Battery Icon Demo

**Concepts:** `draw_battery()`, animated level, UI widget

```python
from oled import OLED
from time import sleep
import systemio

oled  = OLED()
level = 0

def main():
    global level
    while True:
        oled.clear(); oled.status_bar("Battery")
        oled.draw_battery(50, 25, level)
        oled.center_text("{}%".format(level), 48)
        oled.show(); level = (level + 10) % 110
        sleep(1)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 15 — WiFi Signal Strength Meter

**Concepts:** `wifi.rssi()`, `draw_signal()`, dBm to bars

```python
from oled import OLED
import wifi, systemio
from time import sleep

oled = OLED()

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect()
    while True:
        rssi = wifi.rssi() or -100
        bars = max(0, min(4, (rssi + 100) * 4 // 60))
        oled.clear(); oled.status_bar("WiFi RSSI")
        oled.draw_signal(50, 15, bars)
        oled.center_text("{} dBm".format(rssi), 44)
        oled.show(); sleep(2)

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 16 — Invert Display Toggle

**Concepts:** `oled.invert()`, hardware pixel inversion, toggle state

```python
from oled import OLED
from machine import Pin
from time import sleep_ms
import systemio

oled = OLED()
btn  = Pin(0, Pin.IN, Pin.PULL_UP)
inv  = False

def main():
    global inv
    oled.splash("Btn = Invert")
    while True:
        if btn.value() == 0:
            inv = not inv; oled.invert(inv)
            sleep_ms(400)
        sleep_ms(50)

def cleanup():
    oled.invert(False); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 17 — Free RAM Display

**Concepts:** `gc.mem_free()`, `gc.mem_alloc()`, memory monitoring

```python
from oled import OLED
import gc, systemio
from time import sleep

oled = OLED()

def main():
    while True:
        gc.collect()
        free = gc.mem_free() // 1024
        used = gc.mem_alloc() // 1024
        oled.clear(); oled.status_bar("Memory")
        oled.text("Free: {}KB".format(free), 0, 16, 1)
        oled.text("Used: {}KB".format(used), 0, 28, 1)
        oled.h_bar(2, 40, 124, 10, used, free + used)
        oled.show(); sleep(2)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 18 — Simple Stopwatch

**Concepts:** `ticks_ms()`, start/stop logic, elapsed time display

```python
from oled import OLED
from machine import Pin
from time import ticks_ms, sleep_ms
import systemio

oled    = OLED()
btn     = Pin(0, Pin.IN, Pin.PULL_UP)
running = False
start   = 0; elapsed = 0

def main():
    global running, start, elapsed
    oled.splash("Stopwatch", "BTN=Start/Stop")
    while True:
        if btn.value() == 0:
            running = not running
            if running: start = ticks_ms() - elapsed
            sleep_ms(400)
        if running: elapsed = ticks_ms() - start
        s  = elapsed // 1000; ms = (elapsed % 1000) // 10
        oled.clear(); oled.center_text("{:02d}.{:02d}s".format(s, ms), 28)
        oled.show(); sleep_ms(50)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 19 — Relay On/Off Control

**Concepts:** `Pin.OUT`, relay toggle, state display

```python
from oled import OLED
from machine import Pin
from time import sleep_ms
import systemio

oled  = OLED()
btn   = Pin(0, Pin.IN, Pin.PULL_UP)
relay = Pin(26, Pin.OUT); relay.off()
state = False

def main():
    global state
    while True:
        if btn.value() == 0:
            state = not state; relay.value(state)
            label = "RELAY ON" if state else "RELAY OFF"
            oled.splash(label); sleep_ms(400)
        sleep_ms(50)

def cleanup():
    relay.off(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 20 — OLED Menu Navigation

**Concepts:** `draw_menu()`, two-button navigation, scrollable list

```python
from oled import OLED
from machine import Pin
from time import sleep_ms
import systemio

oled   = OLED()
up_btn = Pin(14, Pin.IN, Pin.PULL_UP)
dn_btn = Pin(0,  Pin.IN, Pin.PULL_UP)
items  = ["LED Control", "Sensor", "WiFi", "Settings", "About"]
cursor = 0

def main():
    global cursor
    oled.draw_menu(items, cursor, header="MENU")
    while True:
        if up_btn.value() == 0:
            cursor = (cursor - 1) % len(items)
            oled.draw_menu(items, cursor, header="MENU"); sleep_ms(300)
        if dn_btn.value() == 0:
            cursor = (cursor + 1) % len(items)
            oled.draw_menu(items, cursor, header="MENU"); sleep_ms(300)
        sleep_ms(50)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

## 🟡 Intermediate Level — Projects 21–40
*WiFi Networking · Sensors · Charts · Games*

---

### Project 21 — HTTP GET: Fetch Data from Server

**Concepts:** `wifi.httpGet()`, `wrap_text()`, live web data

```python
from oled import OLED
import wifi, systemio
from time import sleep

oled = OLED()

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect()
    while True:
        code, body = wifi.httpGet("http://numbersapi.com/random/trivia")
        oled.clear(); oled.status_bar("Fact!")
        oled.wrap_text(body[:80], 0, 14); oled.show()
        sleep(10)

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 22 — HTTP POST: Send Sensor Data

**Concepts:** `wifi.httpPost()`, JSON payload, response code

```python
from oled import OLED
from machine import ADC, Pin
import wifi, systemio, json
from time import sleep

oled = OLED()
adc  = ADC(Pin(34)); adc.atten(ADC.ATTN_11DB)

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect()
    while True:
        val  = adc.read()
        data = json.dumps({"sensor": "adc", "value": val})
        code, resp = wifi.httpPost("http://YOUR_SERVER/api/data", data)
        oled.clear(); oled.status_bar("POST", str(code))
        oled.center_text("ADC:{}".format(val), 30); oled.show()
        sleep(5)

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 23 — Live Temperature Graph

**Concepts:** `draw_graph()`, rolling sample buffer, real-time chart

```python
from oled import OLED
from machine import ADC, Pin
from time import sleep
import math, systemio

oled    = OLED()
adc     = ADC(Pin(34)); adc.atten(ADC.ATTN_11DB)
samples = []

def read_temp():
    r = 10000 * adc.read() / (4095 - adc.read() + 1)
    return round(1 / (math.log(r / 10000) / 3950 + 1/298.15) - 273.15, 1)

def main():
    while True:
        samples.append(read_temp())
        if len(samples) > 64: samples.pop(0)
        oled.clear(); oled.status_bar("TEMP", "{}C".format(samples[-1]))
        oled.draw_graph(samples, y=12, h=50, vmin=15, vmax=40)
        oled.show(); sleep(1)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 24 — UDP Sender

**Concepts:** `wifi.udpSend()`, broadcast datagram, network TX

```python
from oled import OLED
from machine import ADC, Pin
import wifi, systemio
from time import sleep

oled = OLED()
adc  = ADC(Pin(34)); adc.atten(ADC.ATTN_11DB)

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect()
    while True:
        val = adc.read()
        wifi.udpSend("192.168.1.255", 5000, "ADC:{}".format(val))
        oled.clear(); oled.status_bar("UDP TX")
        oled.center_text("Sent: {}".format(val), 30)
        oled.show(); sleep(1)

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 25 — UDP Receiver

**Concepts:** `wifi.udpReceive()`, listening on port, incoming message display

```python
from oled import OLED
import wifi, systemio

oled = OLED()

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect()
    oled.splash("UDP Listen", "Port 5000")
    while True:
        data, addr = wifi.udpReceive(5000, timeout=5)
        if data:
            oled.clear(); oled.status_bar("UDP RX")
            oled.wrap_text(str(data), 0, 14); oled.show()

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 26 — Access Point Mode

**Concepts:** `wifi.startAP()`, AP IP display, hotspot creation

```python
from oled import OLED
import wifi, systemio
from time import sleep

oled = OLED()

def main():
    ap_ip = wifi.startAP("ESP32-AP", "12345678")
    oled.clear(); oled.status_bar("AP Mode")
    oled.text("SSID: ESP32-AP", 0, 16, 1)
    oled.text("Pass: 12345678", 0, 28, 1)
    oled.text("IP: " + ap_ip,    0, 40, 1)
    oled.show()
    while True: sleep(1)

def cleanup():
    wifi.stopAP(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 27 — 4-Channel Analog Bar Chart

**Concepts:** `draw_bar_chart()`, multi-ADC reading, auto-scale

```python
from oled import OLED
from machine import ADC, Pin
from time import sleep_ms
import systemio

oled = OLED()
pins = [34, 35, 32, 33]
adcs = [ADC(Pin(p)) for p in pins]
for a in adcs: a.atten(ADC.ATTN_11DB)

def main():
    while True:
        vals = [a.read() * 100 // 4095 for a in adcs]
        oled.clear(); oled.status_bar("4-CH ADC")
        oled.draw_bar_chart(vals, y=14, h=48, vmin=0, vmax=100)
        oled.show(); sleep_ms(200)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 28 — WiFi Network Scanner

**Concepts:** `wifi.scan()`, SSID listing, `draw_menu()`

```python
from oled import OLED
import wifi, systemio
from time import sleep

oled = OLED()

def main():
    nets  = wifi.scan()
    items = []
    for n in nets:
        ssid = n[0].decode() if isinstance(n[0], bytes) else n[0]
        items.append("{} {}dBm".format(ssid[:10], n[3]))
    oled.draw_menu(items, 0, header="WiFi Scan")
    while True: sleep(1)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 29 — Reaction Timer Game

**Concepts:** `random`, `ticks_ms()`, user response measurement

```python
from oled import OLED
from machine import Pin
from time import ticks_ms, sleep, sleep_ms
from random import randint
import systemio

oled = OLED()
btn  = Pin(0, Pin.IN, Pin.PULL_UP)

def main():
    while True:
        oled.splash("Get Ready!", "Wait for GO")
        sleep(randint(2, 5))
        oled.clear(); oled.center_text("GO!", 28); oled.show()
        t0 = ticks_ms()
        while btn.value() == 1: pass
        ms = ticks_ms() - t0
        oled.splash("{}ms".format(ms), "Press again"); sleep(2)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 30 — Notification Card from Web

**Concepts:** `notification()`, HTTP GET, card UI layout

```python
from oled import OLED
import wifi, systemio
from time import sleep

oled = OLED()

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    if wifi.connect():
        code, body = wifi.httpGet("http://api.kanye.rest/")
        oled.notification("Kanye Says", body[:60])
    else:
        oled.notification("Error", "No WiFi connection found")
    while True: sleep(1)

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 31 — PWM Fan Speed Controller

**Concepts:** `PWM` 25kHz, ADC to duty, percentage display

```python
from oled import OLED
from machine import ADC, Pin, PWM
from time import sleep_ms
import systemio

oled = OLED()
pot  = ADC(Pin(34)); pot.atten(ADC.ATTN_11DB)
fan  = PWM(Pin(5), freq=25000)

def main():
    while True:
        val  = pot.read()
        duty = val // 4
        fan.duty(duty)
        pct  = duty * 100 // 1023
        oled.clear(); oled.status_bar("FAN", "{}%".format(pct))
        oled.h_bar(2, 20, 124, 14, pct, 100)
        oled.center_text("Speed: {}%".format(pct), 44)
        oled.show(); sleep_ms(100)

def cleanup():
    fan.duty(0); fan.deinit(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 32 — Multi-Page Display with Page Dots

**Concepts:** `page_dots()`, multi-page layout, button paging

```python
from oled import OLED
from machine import Pin
from time import sleep_ms
import systemio

oled    = OLED()
btn     = Pin(0, Pin.IN, Pin.PULL_UP)
content = ["Welcome to\nESP32 IoT!", "ADC: --\nTemp: --C", "IP: 0.0.0.0\nRSSI: --"]
page    = 0

def show_page(p):
    oled.clear(); oled.center_text(content[p].split("\n")[0], 18)
    oled.center_text(content[p].split("\n")[1], 32)
    oled.page_dots(len(content), p); oled.show()

def main():
    global page
    show_page(page)
    while True:
        if btn.value() == 0:
            page = (page + 1) % len(content)
            show_page(page); sleep_ms(400)
        sleep_ms(50)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 33 — Auto WiFi Reconnect Monitor

**Concepts:** `wifi.keepAlive()`, connection state, live IP display

```python
from oled import OLED
import wifi, systemio
from time import sleep

oled = OLED()

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect()
    while True:
        wifi.keepAlive()
        status = "Online" if wifi.isConnected() else "Offline"
        ip     = wifi.ip() or "---"
        oled.clear(); oled.status_bar("WiFi", status)
        oled.center_text(ip, 30); oled.show()
        sleep(3)

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 34 — Voltage Meter (0–3.3V)

**Concepts:** ADC to voltage conversion, `h_bar()`, raw + voltage display

```python
from oled import OLED
from machine import ADC, Pin
from time import sleep_ms
import systemio

oled = OLED()
adc  = ADC(Pin(34)); adc.atten(ADC.ATTN_11DB)

def main():
    while True:
        raw  = adc.read()
        volt = raw * 3.3 / 4095
        oled.clear(); oled.status_bar("Voltmeter")
        oled.center_text("{:.2f} V".format(volt), 20)
        oled.h_bar(2, 36, 124, 12, raw, 4095)
        oled.center_text("RAW: {}".format(raw), 52)
        oled.show(); sleep_ms(200)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 35 — Countdown Timer

**Concepts:** countdown logic, `h_bar()` depletion, time-up alert

```python
from oled import OLED
from time import sleep, ticks_ms
import systemio

oled    = OLED()
SECONDS = 30

def main():
    start = ticks_ms()
    while True:
        elapsed = (ticks_ms() - start) // 1000
        remain  = max(0, SECONDS - elapsed)
        m, s    = remain // 60, remain % 60
        oled.clear(); oled.status_bar("Countdown")
        oled.center_text("{:02d}:{:02d}".format(m, s), 25)
        oled.h_bar(2, 44, 124, 10, remain, SECONDS)
        oled.show()
        if remain == 0:
            oled.splash("TIME UP!", "Press RST"); break
        sleep(1)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 36 — PIR Motion Alert

**Concepts:** PIR sensor, buzzer alert, motion counter, `status_bar()`

```python
from oled import OLED
from machine import Pin, PWM
from time import sleep_ms
import systemio

oled   = OLED()
pir    = Pin(14, Pin.IN)
buzzer = PWM(Pin(5), freq=2000, duty=0)
count  = 0

def main():
    global count
    oled.splash("PIR Monitor", "Watching...")
    while True:
        if pir.value() == 1:
            count += 1; buzzer.duty(200)
            oled.clear(); oled.status_bar("ALERT!", str(count))
            oled.center_text("Motion!", 25)
            oled.center_text("Count:{}".format(count), 40)
            oled.show(); sleep_ms(1000); buzzer.duty(0)
        else:
            oled.print_line("No motion...", 3, clear_first=True)
        sleep_ms(200)

def cleanup():
    buzzer.deinit(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 37 — Serial Data Logger

**Concepts:** timestamped logging, `print()` to serial, log list

```python
from oled import OLED
from machine import ADC, Pin
from time import sleep, ticks_ms
import systemio

oled = OLED()
adc  = ADC(Pin(34)); adc.atten(ADC.ATTN_11DB)
log  = []

def main():
    while True:
        val = adc.read()
        t   = ticks_ms() // 1000
        log.append((t, val))
        print("T={} ADC={}".format(t, val))
        oled.clear(); oled.status_bar("Logger", "#{}".format(len(log)))
        oled.center_text("ADC: {}".format(val), 25)
        oled.center_text("T: {}s".format(t), 40)
        oled.show(); sleep(2)

def cleanup():
    print("Log entries:", len(log)); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 38 — OpenWeather Dashboard

**Concepts:** Real REST API, JSON parsing, weather display

> ⚙️ Replace `YOUR_OPENWEATHER_KEY` with a free key from [openweathermap.org](https://openweathermap.org)

```python
from oled import OLED
import wifi, systemio, json
from time import sleep

oled   = OLED()
CITY   = "Chennai"
APIKEY = "YOUR_OPENWEATHER_KEY"

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect()
    while True:
        url  = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric".format(CITY, APIKEY)
        c, b = wifi.httpGet(url)
        if c == 200:
            d    = json.loads(b)
            temp = d["main"]["temp"]
            desc = d["weather"][0]["main"]
            oled.clear(); oled.status_bar(CITY)
            oled.center_text("{}C".format(temp), 20)
            oled.center_text(desc, 36); oled.show()
        sleep(60)

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 39 — RGB LED Color Mixer

**Concepts:** 3× ADC + 3× PWM, real-time RGB mixing

```python
from oled import OLED
from machine import ADC, Pin, PWM
from time import sleep_ms
import systemio

oled = OLED()
pots = [ADC(Pin(p)) for p in [34, 35, 32]]
for p in pots: p.atten(ADC.ATTN_11DB)
rgb  = [PWM(Pin(p), freq=1000) for p in [25, 26, 27]]

def main():
    while True:
        vals = [p.read() // 4 for p in pots]
        for i, pwm in enumerate(rgb): pwm.duty(vals[i])
        pcts = [v * 100 // 1023 for v in vals]
        oled.clear(); oled.status_bar("RGB Mixer")
        oled.text("R:{:3d}% G:{:3d}%".format(pcts[0], pcts[1]), 0, 16, 1)
        oled.text("B:{:3d}%".format(pcts[2]), 0, 28, 1)
        oled.show(); sleep_ms(100)

def cleanup():
    for p in rgb: p.duty(0); p.deinit()
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 40 — OLED Oscilloscope

**Concepts:** ADC waveform capture, pixel-by-pixel line draw, real-time scope

```python
from oled import OLED
from machine import ADC, Pin
from time import sleep_ms
import systemio

oled = OLED()
adc  = ADC(Pin(34)); adc.atten(ADC.ATTN_11DB)
buf  = [0] * 128

def main():
    while True:
        for i in range(128):
            buf[i] = adc.read() * 50 // 4095
        oled.clear(); oled.status_bar("SCOPE")
        for x in range(127):
            y0 = 63 - buf[x]; y1 = 63 - buf[x + 1]
            oled.line(x, y0, x + 1, y1, 1)
        oled.show(); sleep_ms(10)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

## 🔴 Advanced Level — Projects 41–50
*Full IoT Systems · Dashboards · Automation*

---

### Project 41 — HTTP JSON Sensor Dashboard

**Concepts:** Voltage + JSON POST + HTTP status display, full IoT loop

```python
from oled import OLED
from machine import ADC, Pin
import wifi, systemio, json
from time import sleep

oled = OLED()
adc  = ADC(Pin(34)); adc.atten(ADC.ATTN_11DB)

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect()
    while True:
        val  = adc.read()
        volt = round(val * 3.3 / 4095, 2)
        data = json.dumps({"device": "esp32", "voltage": volt, "raw": val})
        code, resp = wifi.httpPost("http://YOUR_SERVER/sensors", data)
        oled.clear(); oled.status_bar("IoT POST", str(code))
        oled.text("Volt: {}V".format(volt), 0, 18, 1)
        oled.text("RAW:  {}".format(val),   0, 30, 1)
        oled.text("Code: {}".format(code),  0, 42, 1)
        oled.show(); sleep(5)

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 42 — Smart Alarm Clock

**Concepts:** Button-set timer, buzzer alarm, reset control, progress bar

```python
from oled import OLED
from machine import Pin, PWM
from time import ticks_ms, sleep_ms
import systemio

oled    = OLED()
btn_set = Pin(14, Pin.IN, Pin.PULL_UP)
btn_rst = Pin(0,  Pin.IN, Pin.PULL_UP)
buzzer  = PWM(Pin(5), freq=2000, duty=0)
alarm   = 10; elapsed = 0; start = ticks_ms(); ringing = False

def main():
    global alarm, elapsed, start, ringing
    while True:
        elapsed = (ticks_ms() - start) // 1000
        if btn_set.value() == 0:
            alarm += 5; start = ticks_ms(); elapsed = 0
            ringing = False; buzzer.duty(0); sleep_ms(300)
        if elapsed >= alarm and not ringing:
            ringing = True; buzzer.duty(512)
        if ringing and btn_rst.value() == 0:
            ringing = False; buzzer.duty(0); start = ticks_ms(); sleep_ms(300)
        oled.clear(); oled.status_bar("Alarm", "{}s".format(alarm))
        oled.center_text("{}/{}s".format(elapsed, alarm), 25)
        oled.h_bar(2, 40, 124, 10, elapsed, alarm)
        if ringing: oled.center_text("ALARM!", 52)
        oled.show(); sleep_ms(100)

def cleanup():
    buzzer.deinit(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 43 — IoT Sensor Hub (2-Channel, POST every 30s)

**Concepts:** Multi-channel ADC, timed POST, `keepAlive()`, status display

```python
from oled import OLED
from machine import ADC, Pin
import wifi, systemio, json
from time import ticks_ms, sleep_ms

oled     = OLED()
ch       = [ADC(Pin(p)) for p in [34, 35]]
for c in ch: c.atten(ADC.ATTN_11DB)
INTERVAL = 30000

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect(); last = 0
    while True:
        wifi.keepAlive()
        v = [c.read() * 3.3 / 4095 for c in ch]
        oled.clear(); oled.status_bar("Sensor Hub")
        oled.text("CH1: {:.2f}V".format(v[0]), 0, 14, 1)
        oled.text("CH2: {:.2f}V".format(v[1]), 0, 26, 1)
        now = ticks_ms()
        if now - last > INTERVAL:
            data = json.dumps({"ch1": round(v[0],2), "ch2": round(v[1],2)})
            code, _ = wifi.httpPost("http://YOUR_SERVER/hub", data)
            last = now; oled.text("POST:{}".format(code), 0, 40, 1)
        oled.show(); sleep_ms(500)

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 44 — OTA Version Checker

**Concepts:** HTTP GET version file, version compare, update notice

```python
from oled import OLED
import wifi, systemio
from time import sleep

oled        = OLED()
CURRENT_VER = "1.0.0"
VERSION_URL = "http://YOUR_SERVER/version.txt"

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect()
    code, latest = wifi.httpGet(VERSION_URL)
    latest       = latest.strip() if code == 200 else "unknown"
    up_to_date   = latest == CURRENT_VER
    oled.clear(); oled.status_bar("OTA Check")
    oled.text("Current: " + CURRENT_VER, 0, 14, 1)
    oled.text("Latest:  " + latest,      0, 26, 1)
    oled.center_text("Up to date!" if up_to_date else "UPDATE!", 44)
    oled.show()
    while True: sleep(1)

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 45 — Scrollable Live Log + Graph

**Concepts:** Rolling log lines + graph combo, `draw_graph()`, text overlay

```python
from oled import OLED
from machine import ADC, Pin
from time import ticks_ms, sleep_ms
import systemio

oled      = OLED()
adc       = ADC(Pin(34)); adc.atten(ADC.ATTN_11DB)
history   = []; log_lines = []

def main():
    while True:
        v  = adc.read() * 3.3 / 4095
        t  = ticks_ms() // 1000
        history.append(v)
        if len(history) > 64: history.pop(0)
        log_lines.append("{:4d}s {:.2f}V".format(t, v))
        if len(log_lines) > 3: log_lines.pop(0)
        oled.clear(); oled.status_bar("Live Log")
        oled.draw_graph(history, y=12, h=30, vmin=0, vmax=3.3)
        for i, line in enumerate(log_lines):
            oled.text(line, 0, 44 + i * 10, 1)
        oled.show(); sleep_ms(500)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 46 — WiFi-Controlled LED

**Concepts:** HTTP polling for command, remote LED on/off control

```python
from oled import OLED
from machine import Pin
import wifi, systemio
from time import sleep

oled = OLED()
led  = Pin(2, Pin.OUT)

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect()
    while True:
        code, body = wifi.httpGet("http://YOUR_SERVER/led_state")
        if code == 200:
            state = body.strip().lower()
            led.value(1 if state == "on" else 0)
            oled.clear(); oled.status_bar("LED Ctrl")
            oled.center_text("LED: " + state.upper(), 30)
            oled.show()
        sleep(3)

def cleanup():
    led.off(); wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 47 — Multi-Sensor Environmental Monitor

**Concepts:** Temp + LDR + PIR combined display, multi-sensor dashboard

```python
from oled import OLED
from machine import ADC, Pin
from time import sleep
import math, systemio

oled     = OLED()
temp_adc = ADC(Pin(34)); temp_adc.atten(ADC.ATTN_11DB)
ldr_adc  = ADC(Pin(35)); ldr_adc.atten(ADC.ATTN_11DB)
pir      = Pin(14, Pin.IN)

def get_temp():
    r = 10000 * temp_adc.read() / max(1, 4095 - temp_adc.read())
    return round(1 / (math.log(r / 10000) / 3950 + 1/298.15) - 273.15, 1)

def main():
    while True:
        t      = get_temp()
        light  = ldr_adc.read() * 100 // 4095
        motion = "YES" if pir.value() else "NO"
        oled.clear(); oled.status_bar("ENV Monitor")
        oled.text("Temp:  {}C".format(t),    0, 14, 1)
        oled.text("Light: {}%".format(light), 0, 26, 1)
        oled.text("Motion:{}".format(motion), 0, 38, 1)
        oled.show(); sleep(2)

def cleanup():
    oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 48 — Ping / Latency Tester

**Concepts:** HTTP timing, `ticks_ms()` delta, signal quality rating

```python
from oled import OLED
import wifi, systemio
from time import ticks_ms, sleep

oled = OLED()
HOST = "http://google.com"

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect()
    while True:
        t0       = ticks_ms()
        code, _  = wifi.httpGet(HOST)
        latency  = ticks_ms() - t0
        quality  = "Good" if latency < 300 else "Slow" if latency < 800 else "Bad"
        oled.clear(); oled.status_bar("Ping Test")
        oled.center_text("{}ms".format(latency), 20)
        oled.center_text(quality, 36)
        oled.draw_signal(50, 46, min(4, 4 - latency // 300))
        oled.show(); sleep(5)

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 49 — Threshold Alert System

**Concepts:** ADC limit detection, buzzer + UDP alert, `h_bar()` live gauge

```python
from oled import OLED
from machine import ADC, Pin, PWM
import wifi, systemio
from time import sleep

oled      = OLED()
adc       = ADC(Pin(34)); adc.atten(ADC.ATTN_11DB)
buzzer    = PWM(Pin(5), freq=1500, duty=0)
THRESHOLD = 3000

def main():
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect()
    while True:
        val   = adc.read()
        alert = val > THRESHOLD
        if alert:
            buzzer.duty(400)
            wifi.udpSend("192.168.1.255", 5001, "ALERT:ADC={}".format(val))
        else:
            buzzer.duty(0)
        oled.clear(); oled.status_bar("Threshold", "ALERT" if alert else "OK")
        oled.h_bar(2, 18, 124, 12, val, 4095)
        oled.center_text("ADC: {}".format(val), 36)
        oled.center_text("Limit: {}".format(THRESHOLD), 48)
        oled.show(); sleep(1)

def cleanup():
    buzzer.deinit(); wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

### Project 50 — Full IoT Dashboard ⭐

**Concepts:** Sensor + WiFi + live graph + timed POST + RSSI — complete IoT system

```python
from oled import OLED
from machine import ADC, Pin
import wifi, systemio, json, math
from time import ticks_ms, sleep_ms

oled     = OLED()
adc      = ADC(Pin(34)); adc.atten(ADC.ATTN_11DB)
history  = []; POST_EVERY = 30000; last_post = 0

def get_temp():
    r = 10000 * adc.read() / max(1, 4095 - adc.read())
    return round(1 / (math.log(r / 10000) / 3950 + 1/298.15) - 273.15, 1)

def main():
    global last_post
    wifi.setWiFi("YOUR_SSID", "YOUR_PASSWORD")
    wifi.connect()
    while True:
        wifi.keepAlive()
        t = get_temp()
        history.append(t)
        if len(history) > 64: history.pop(0)
        now = ticks_ms(); posted = ""
        if now - last_post > POST_EVERY:
            data = json.dumps({"temp": t, "ip": wifi.ip(), "rssi": wifi.rssi()})
            code, _ = wifi.httpPost("http://YOUR_SERVER/dashboard", data)
            last_post = now; posted = str(code)
        oled.clear()
        oled.status_bar("IoT Hub", posted or wifi.ip() or "--")
        oled.draw_graph(history, y=12, h=38, vmin=15, vmax=45)
        oled.text("{}C".format(t), 0, 54, 1)
        oled.text("{}dBm".format(wifi.rssi() or 0), 70, 54, 1)
        oled.show(); sleep_ms(1000)

def cleanup():
    wifi.disconnect(); oled.clear(); oled.show()

systemio.run(main, cleanup)
```

---

## Quick Reference — Library Functions

### `oled.py` — Display Methods

| Method | Description |
|--------|-------------|
| `oled.clear()` | Clear framebuffer |
| `oled.show()` | Push buffer to screen |
| `oled.text(str, x, y, color)` | Draw text at position |
| `oled.center_text(str, y)` | Horizontally centred text |
| `oled.print_line(str, line)` | Quick single-line write |
| `oled.splash(title, subtitle)` | Centred splash screen |
| `oled.status_bar(title, value)` | Header bar with title/value |
| `oled.notification(sender, body)` | Message card |
| `oled.h_bar(x,y,w,h, val, max)` | Horizontal progress bar |
| `oled.draw_graph(samples)` | Line chart |
| `oled.draw_bar_chart(values)` | Vertical bar chart |
| `oled.draw_battery(x,y,pct)` | Battery icon |
| `oled.draw_signal(x,y,bars)` | Signal strength icon |
| `oled.draw_menu(items, cursor)` | Scrollable menu |
| `oled.page_dots(total, current)` | Pagination dots |
| `oled.marquee(msg, offset)` | Scrolling text frame |
| `oled.wrap_text(str, x, y)` | Auto word-wrap text |
| `oled.invert(True/False)` | Invert all pixels |
| `oled.contrast(0–255)` | Set brightness |

### `wifi.py` — Network Methods

| Method | Description |
|--------|-------------|
| `wifi.setWiFi(ssid, pwd)` | Set credentials |
| `wifi.connect()` | Connect to WiFi |
| `wifi.disconnect()` | Disconnect |
| `wifi.isConnected()` | Check status |
| `wifi.ip()` | Get IP address |
| `wifi.rssi()` | Signal strength (dBm) |
| `wifi.keepAlive()` | Auto-reconnect tick |
| `wifi.scan()` | Scan nearby networks |
| `wifi.httpGet(url)` | HTTP GET → (code, body) |
| `wifi.httpPost(url, body)` | HTTP POST → (code, body) |
| `wifi.udpSend(host, port, msg)` | Send UDP datagram |
| `wifi.udpReceive(port)` | Receive UDP datagram |
| `wifi.startAP(ssid, pwd)` | Start Access Point |
| `wifi.stopAP()` | Stop Access Point |

### `systemio.py` — Safe Run

| Method | Description |
|--------|-------------|
| `systemio.run(main, cleanup)` | Run with safe Ctrl-C exit |

---

## Wiring Reference

```
ESP32          SSD1306 OLED
─────────────────────────────
3.3V    →      VCC
GND     →      GND
GPIO21  →      SDA
GPIO22  →      SCL
```

> Add 4.7kΩ pull-up resistors from SDA and SCL to 3.3V if your module does not have them built in.

---

*Made for students learning MicroPython IoT with ESP32*

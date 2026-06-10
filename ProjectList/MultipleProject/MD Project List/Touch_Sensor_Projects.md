# 👆 Touch Sensor Projects — ESP32 MicroPython

> All projects use the `systemio` library with `setup()`, `main()`, and `cleanup()` functions.
> Code style follows the `from digital import *` / `from analog import *` pattern.

---

## Table of Contents

1. [Touch-Controlled LED](#1-touch-controlled-led)
2. [Touch-Controlled Fan](#2-touch-controlled-fan)
3. [Touch Door Bell](#3-touch-door-bell)
4. [Touch Password Lock](#4-touch-password-lock)
5. [Touch Lamp](#5-touch-lamp)
6. [Touch Music Player Control](#6-touch-music-player-control)
7. [Touch Robot Start/Stop](#7-touch-robot-startstop)
8. [Touch Relay Switch](#8-touch-relay-switch)
9. [Touch Counter System](#9-touch-counter-system)
10. [Touch Menu Navigation](#10-touch-menu-navigation)

---

## 1. Touch-Controlled LED

### 🎯 Objective
Toggle an LED ON and OFF each time the touch sensor is pressed using edge detection.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Touch Sensor Module | 1 |
| LED | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| TOUCH_PIN | 5 | Touch Sensor Output |
| LED_PIN | 4 | LED Output |

### 💡 Working Principle
- Touch sensor outputs HIGH (1) when touched
- Edge detection (0 → 1) ensures one toggle per touch
- Each touch flips the LED state between ON and OFF
- Serial monitor prints current LED state

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

TOUCH_PIN = 5
LED_PIN   = 4

def setup():
    pinMode(TOUCH_PIN, INPUT)
    pinMode(LED_PIN,   OUTPUT)

def main():
    setup()
    led_state  = 0
    last_touch = 0

    print("Touch-Controlled LED Ready")
    print("Touch sensor to toggle LED...")

    while True:
        touch = digitalRead(TOUCH_PIN)

        if last_touch == 0 and touch == 1:
            led_state = 1 if led_state == 0 else 0
            digitalWrite(LED_PIN, led_state)
            state_str = "ON 💡" if led_state else "OFF ⚫"
            print(f"LED: {state_str}")

        last_touch = touch
        time.sleep(0.05)

def cleanup():
    digitalWrite(LED_PIN, 0)
    print("LED OFF — System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Touch-Controlled LED Ready
Touch sensor to toggle LED...
LED: ON 💡
LED: OFF ⚫
LED: ON 💡
LED: OFF ⚫
```

---

## 2. Touch-Controlled Fan

### 🎯 Objective
Control a DC fan (via motor driver) with a touch sensor — cycle through OFF, LOW, and HIGH speed modes.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Touch Sensor Module | 1 |
| DC Fan / DC Motor | 1 |
| L298N Motor Driver | 1 |
| LED (Speed Indicator) | 2 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| TOUCH_PIN | 5 | Touch Sensor Output |
| FAN_PIN | 4 | Fan PWM Control |
| LED_LOW | 18 | Low Speed Indicator |
| LED_HIGH | 19 | High Speed Indicator |

### 💡 Speed Modes
| Touch Count | Mode | PWM Duty | Display |
|---|---|---|---|
| 0 | OFF | 0 | All LEDs OFF |
| 1 | LOW | 400 (~40%) | LED_LOW ON |
| 2 | HIGH | 1023 (100%) | LED_HIGH ON |
| 3 | OFF | 0 | Cycle resets |

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, pwmSetup, pwmWrite, pwmStop, INPUT, OUTPUT
from systemio import run
import time

TOUCH_PIN = 5
FAN_PIN   = 4
LED_LOW   = 18
LED_HIGH  = 19

SPEEDS = [0, 400, 1023]
LABELS = ["OFF ⚫", "LOW 🌀", "HIGH 💨"]

def setup():
    pinMode(TOUCH_PIN, INPUT)
    pinMode(LED_LOW,   OUTPUT)
    pinMode(LED_HIGH,  OUTPUT)
    pwmSetup(FAN_PIN, freq=1000)

def apply_speed(mode):
    pwmWrite(FAN_PIN, SPEEDS[mode])
    digitalWrite(LED_LOW,  1 if mode == 1 else 0)
    digitalWrite(LED_HIGH, 1 if mode == 2 else 0)
    print(f"Fan Mode: {LABELS[mode]}")

def main():
    setup()
    mode       = 0
    last_touch = 0

    apply_speed(mode)
    print("Touch-Controlled Fan Ready")
    print("Touch to cycle: OFF → LOW → HIGH → OFF")

    while True:
        touch = digitalRead(TOUCH_PIN)

        if last_touch == 0 and touch == 1:
            mode = (mode + 1) % 3
            apply_speed(mode)

        last_touch = touch
        time.sleep(0.05)

def cleanup():
    pwmStop(FAN_PIN)
    digitalWrite(LED_LOW,  0)
    digitalWrite(LED_HIGH, 0)
    print("Fan OFF — System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Fan Mode: OFF ⚫
Touch-Controlled Fan Ready
Touch to cycle: OFF → LOW → HIGH → OFF
Fan Mode: LOW 🌀
Fan Mode: HIGH 💨
Fan Mode: OFF ⚫
Fan Mode: LOW 🌀
```

---

## 3. Touch Door Bell

### 🎯 Objective
Create a doorbell that plays a double-beep chime when the touch sensor is pressed.

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
- Touch → Rising edge detected → Bell rings once
- Classic DING-DONG pattern: long beep + short beep
- Ring count tracked and displayed on serial monitor
- Ignores held touches — only triggers on fresh press

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

def ding_dong():
    # DING — long tone
    digitalWrite(BUZZER_PIN, 1)
    digitalWrite(LED_PIN,    1)
    time.sleep(0.35)
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    time.sleep(0.12)

    # DONG — short tone
    digitalWrite(BUZZER_PIN, 1)
    digitalWrite(LED_PIN,    1)
    time.sleep(0.18)
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)

def main():
    setup()
    last_touch = 0
    ring_count = 0

    print("Touch Door Bell Ready")
    print("Touch to ring the bell...")

    while True:
        touch = digitalRead(TOUCH_PIN)

        if last_touch == 0 and touch == 1:
            ring_count += 1
            print(f"🔔 DING DONG!  Ring #{ring_count}")
            ding_dong()

        last_touch = touch
        time.sleep(0.05)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    print("Bell System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Touch Door Bell Ready
Touch to ring the bell...
🔔 DING DONG!  Ring #1
🔔 DING DONG!  Ring #2
🔔 DING DONG!  Ring #3
```

---

## 4. Touch Password Lock

### 🎯 Objective
Implement a 4-touch password system — touch the sensor in a secret pattern to unlock, wrong pattern triggers alarm.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Touch Sensor Module | 1 |
| Green LED (Unlocked) | 1 |
| Red LED (Locked / Wrong) | 1 |
| Buzzer | 1 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| TOUCH_PIN | 5 | Touch Sensor Output |
| GREEN_LED | 4 | Unlock Indicator |
| RED_LED | 18 | Lock / Wrong Indicator |
| BUZZER_PIN | 14 | Alert Buzzer |

### 💡 Password Logic
- Secret password = number of taps in groups with pauses
- Example: tap 3 times → pause → tap 2 times = `[3, 2]`
- System counts taps and compares with stored pattern
- 3 wrong attempts → Lockout for 10 seconds

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

TOUCH_PIN  = 5
GREEN_LED  = 4
RED_LED    = 18
BUZZER_PIN = 14

PASSWORD      = [3, 2]    # Secret: 3 taps, pause, 2 taps
TAP_TIMEOUT   = 1.5       # Seconds of silence = end of group
ENTRY_TIMEOUT = 8.0       # Seconds to enter full password
MAX_ATTEMPTS  = 3
LOCKOUT_TIME  = 10        # Seconds

def setup():
    pinMode(TOUCH_PIN,  INPUT)
    pinMode(GREEN_LED,  OUTPUT)
    pinMode(RED_LED,    OUTPUT)
    pinMode(BUZZER_PIN, OUTPUT)

def beep(times, on_t=0.1, off_t=0.1):
    for _ in range(times):
        digitalWrite(BUZZER_PIN, 1)
        time.sleep(on_t)
        digitalWrite(BUZZER_PIN, 0)
        time.sleep(off_t)

def unlock():
    print("✅ UNLOCKED!")
    digitalWrite(GREEN_LED, 1)
    digitalWrite(RED_LED,   0)
    beep(2, 0.2, 0.1)
    time.sleep(3)
    digitalWrite(GREEN_LED, 0)

def wrong_password(attempts_left):
    print(f"❌ WRONG PASSWORD! Attempts left: {attempts_left}")
    digitalWrite(RED_LED, 1)
    beep(3, 0.05, 0.05)
    time.sleep(1)
    digitalWrite(RED_LED, 0)

def lockout():
    print(f"🔒 LOCKED OUT for {LOCKOUT_TIME} seconds!")
    digitalWrite(RED_LED, 1)
    for i in range(LOCKOUT_TIME, 0, -1):
        print(f"  Lockout: {i}s remaining...")
        time.sleep(1)
    digitalWrite(RED_LED, 0)
    print("🔓 Ready for new attempt")

def read_pattern():
    groups      = []
    tap_count   = 0
    last_touch  = 0
    last_tap_t  = time.time()
    start_t     = time.time()

    print("  Listening for taps...")

    while True:
        now   = time.time()
        touch = digitalRead(TOUCH_PIN)

        # Timeout — entry window expired
        if now - start_t > ENTRY_TIMEOUT:
            if tap_count > 0:
                groups.append(tap_count)
            print(f"  Pattern entered: {groups}")
            return groups

        # New tap detected
        if last_touch == 0 and touch == 1:
            tap_count  += 1
            last_tap_t  = now
            print(f"  Tap! Group count: {tap_count}")

        # Pause detected — end of group
        if tap_count > 0 and (now - last_tap_t) > TAP_TIMEOUT:
            groups.append(tap_count)
            tap_count  = 0
            last_tap_t = now
            print(f"  Group saved: {groups}")

        last_touch = touch
        time.sleep(0.05)

def main():
    setup()
    attempts = 0
    digitalWrite(RED_LED, 1)   # Start locked

    print("Touch Password Lock Ready")
    print(f"Password hint: {len(PASSWORD)} groups of taps")
    print("Touch to begin entering password...")

    while True:
        touch = digitalRead(TOUCH_PIN)

        if touch == 1:
            digitalWrite(RED_LED, 0)
            print("\n🔑 Password Entry Started")
            pattern = read_pattern()

            if pattern == PASSWORD:
                attempts = 0
                unlock()
            else:
                attempts += 1
                wrong_password(MAX_ATTEMPTS - attempts)
                if attempts >= MAX_ATTEMPTS:
                    lockout()
                    attempts = 0

            digitalWrite(RED_LED, 1)
            print("Touch to try again...")

        time.sleep(0.05)

def cleanup():
    digitalWrite(GREEN_LED,  0)
    digitalWrite(RED_LED,    0)
    digitalWrite(BUZZER_PIN, 0)
    print("Lock System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Touch Password Lock Ready
Password hint: 2 groups of taps
Touch to begin entering password...

🔑 Password Entry Started
  Listening for taps...
  Tap! Group count: 1
  Tap! Group count: 2
  Tap! Group count: 3
  Group saved: [3]
  Tap! Group count: 1
  Tap! Group count: 2
  Group saved: [3, 2]
  Pattern entered: [3, 2]
✅ UNLOCKED!
```

---

## 5. Touch Lamp

### 🎯 Objective
Create a touch lamp that cycles through OFF → DIM → MEDIUM → BRIGHT brightness levels with each touch.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Touch Sensor Module | 1 |
| LED | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| TOUCH_PIN | 5 | Touch Sensor Output |
| LED_PIN | 4 | PWM LED Output |

### 💡 Brightness Levels
| Touch | Level | PWM Duty | Brightness |
|---|---|---|---|
| 1st | DIM | 100 | ~10% |
| 2nd | MEDIUM | 512 | ~50% |
| 3rd | BRIGHT | 1023 | 100% |
| 4th | OFF | 0 | 0% |

### 🖥️ Code

```python
from digital import pinMode, digitalRead, pwmSetup, pwmWrite, pwmStop, INPUT
from systemio import run
import time

TOUCH_PIN = 5
LED_PIN   = 4

LEVELS = [
    (0,    "OFF ⚫"),
    (100,  "DIM 🔅"),
    (512,  "MEDIUM 💡"),
    (1023, "BRIGHT 🌟"),
]

def setup():
    pinMode(TOUCH_PIN, INPUT)
    pwmSetup(LED_PIN, freq=1000)

def main():
    setup()
    level      = 0
    last_touch = 0

    duty, label = LEVELS[level]
    pwmWrite(LED_PIN, duty)
    print("Touch Lamp Ready")
    print("Touch to change brightness...")
    print(f"Current: {label}")

    while True:
        touch = digitalRead(TOUCH_PIN)

        if last_touch == 0 and touch == 1:
            level = (level + 1) % len(LEVELS)
            duty, label = LEVELS[level]
            pwmWrite(LED_PIN, duty)
            print(f"Brightness: {label}  (PWM: {duty})")

        last_touch = touch
        time.sleep(0.05)

def cleanup():
    pwmStop(LED_PIN)
    print("Lamp OFF — System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Touch Lamp Ready
Touch to change brightness...
Current: OFF ⚫
Brightness: DIM 🔅  (PWM: 100)
Brightness: MEDIUM 💡  (PWM: 512)
Brightness: BRIGHT 🌟  (PWM: 1023)
Brightness: OFF ⚫  (PWM: 0)
Brightness: DIM 🔅  (PWM: 100)
```

---

## 6. Touch Music Player Control

### 🎯 Objective
Simulate a music player controller using touch sensors — one sensor for Play/Pause, another for Next Track.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Touch Sensor Module | 2 |
| Buzzer | 1 |
| Green LED (Playing) | 1 |
| Yellow LED (Track Change) | 1 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| PLAY_TOUCH | 5 | Play / Pause Touch Sensor |
| NEXT_TOUCH | 18 | Next Track Touch Sensor |
| BUZZER_PIN | 14 | Buzzer (Track Chime) |
| PLAY_LED | 4 | Playing Indicator LED |
| TRACK_LED | 19 | Track Change LED |

### 💡 Controls
| Sensor | Action | Response |
|---|---|---|
| PLAY_TOUCH | Toggle Play / Pause | Green LED + beep |
| NEXT_TOUCH | Next Track | Yellow LED flash + chime |

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

PLAY_TOUCH = 5
NEXT_TOUCH = 18
BUZZER_PIN = 14
PLAY_LED   = 4
TRACK_LED  = 19

TRACKS = [
    "Track 1 — Beethoven Symphony",
    "Track 2 — Mozart Sonata",
    "Track 3 — Bach Prelude",
    "Track 4 — Chopin Nocturne",
    "Track 5 — Vivaldi Spring",
]

def setup():
    pinMode(PLAY_TOUCH, INPUT)
    pinMode(NEXT_TOUCH, INPUT)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(PLAY_LED,   OUTPUT)
    pinMode(TRACK_LED,  OUTPUT)

def play_beep():
    digitalWrite(BUZZER_PIN, 1)
    time.sleep(0.1)
    digitalWrite(BUZZER_PIN, 0)

def track_chime():
    for dur in [0.05, 0.05, 0.1]:
        digitalWrite(BUZZER_PIN, 1)
        time.sleep(dur)
        digitalWrite(BUZZER_PIN, 0)
        time.sleep(0.05)

def main():
    setup()
    is_playing    = False
    track_index   = 0
    last_play     = 0
    last_next     = 0

    print("Touch Music Player Ready")
    print(f"Now Loaded: {TRACKS[track_index]}")
    print("PLAY sensor = Play/Pause  |  NEXT sensor = Next Track")

    while True:
        play_touch = digitalRead(PLAY_TOUCH)
        next_touch = digitalRead(NEXT_TOUCH)

        # Play / Pause
        if last_play == 0 and play_touch == 1:
            is_playing = not is_playing
            digitalWrite(PLAY_LED, 1 if is_playing else 0)
            status = "▶️  PLAYING" if is_playing else "⏸️  PAUSED"
            print(f"{status} — {TRACKS[track_index]}")
            play_beep()

        # Next Track
        if last_next == 0 and next_touch == 1:
            track_index = (track_index + 1) % len(TRACKS)
            print(f"⏭️  NEXT — {TRACKS[track_index]}")
            digitalWrite(TRACK_LED, 1)
            track_chime()
            time.sleep(0.3)
            digitalWrite(TRACK_LED, 0)

        last_play = play_touch
        last_next = next_touch
        time.sleep(0.05)

def cleanup():
    digitalWrite(PLAY_LED,   0)
    digitalWrite(TRACK_LED,  0)
    digitalWrite(BUZZER_PIN, 0)
    print("Player Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Touch Music Player Ready
Now Loaded: Track 1 — Beethoven Symphony
PLAY sensor = Play/Pause  |  NEXT sensor = Next Track
▶️  PLAYING — Track 1 — Beethoven Symphony
⏸️  PAUSED — Track 1 — Beethoven Symphony
⏭️  NEXT — Track 2 — Mozart Sonata
▶️  PLAYING — Track 2 — Mozart Sonata
⏭️  NEXT — Track 3 — Bach Prelude
```

---

## 7. Touch Robot Start/Stop

### 🎯 Objective
Start and stop a robot's movement using a touch sensor as a toggle switch, with LED status indicators.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Touch Sensor Module | 1 |
| DC Motors + Motor Driver (L298N) | 2 Motors |
| Green LED (Running) | 1 |
| Red LED (Stopped) | 1 |
| 220Ω Resistor | 2 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| TOUCH_PIN | 5 | Touch Sensor Output |
| LEFT_MOTOR_1 | 12 | Left Motor Forward |
| LEFT_MOTOR_2 | 13 | Left Motor Backward |
| RIGHT_MOTOR_1 | 2 | Right Motor Forward |
| RIGHT_MOTOR_2 | 4 | Right Motor Backward |
| GREEN_LED | 18 | Running Indicator |
| RED_LED | 19 | Stopped Indicator |

### 💡 Working Principle
- First touch → Robot starts moving forward + Green LED ON
- Second touch → Robot stops + Red LED ON
- Alternates between running and stopped on each touch

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

TOUCH_PIN    = 5
LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4
GREEN_LED    = 18
RED_LED      = 19

def setup():
    pinMode(TOUCH_PIN,    INPUT)
    pinMode(LEFT_MOTOR_1,  OUTPUT)
    pinMode(LEFT_MOTOR_2,  OUTPUT)
    pinMode(RIGHT_MOTOR_1, OUTPUT)
    pinMode(RIGHT_MOTOR_2, OUTPUT)
    pinMode(GREEN_LED,    OUTPUT)
    pinMode(RED_LED,      OUTPUT)

def move_forward():
    digitalWrite(LEFT_MOTOR_1,  1); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)
    digitalWrite(GREEN_LED, 1)
    digitalWrite(RED_LED,   0)

def stop_robot():
    digitalWrite(LEFT_MOTOR_1,  0); digitalWrite(LEFT_MOTOR_2,  0)
    digitalWrite(RIGHT_MOTOR_1, 0); digitalWrite(RIGHT_MOTOR_2, 0)
    digitalWrite(GREEN_LED, 0)
    digitalWrite(RED_LED,   1)

def main():
    setup()
    is_running = False
    last_touch = 0

    stop_robot()
    print("Touch Robot Start/Stop Ready")
    print("Touch sensor to START / STOP the robot")
    print("Status: STOPPED 🔴")

    while True:
        touch = digitalRead(TOUCH_PIN)

        if last_touch == 0 and touch == 1:
            is_running = not is_running

            if is_running:
                move_forward()
                print("🟢 Robot STARTED — Moving Forward")
            else:
                stop_robot()
                print("🔴 Robot STOPPED")

        last_touch = touch
        time.sleep(0.05)

def cleanup():
    stop_robot()
    print("Robot Stopped — System OFF")

run(main, cleanup)
```

### 📝 Expected Output
```
Touch Robot Start/Stop Ready
Touch sensor to START / STOP the robot
Status: STOPPED 🔴
🟢 Robot STARTED — Moving Forward
🔴 Robot STOPPED
🟢 Robot STARTED — Moving Forward
🔴 Robot STOPPED
```

---

## 8. Touch Relay Switch

### 🎯 Objective
Toggle a relay ON and OFF using a touch sensor to control high-power appliances like a bulb or fan.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Touch Sensor Module | 1 |
| Relay Module (5V) | 1 |
| LED (Relay Status) | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| TOUCH_PIN | 5 | Touch Sensor Output |
| RELAY_PIN | 4 | Relay Control Pin |
| LED_PIN | 18 | Status LED |

### 💡 Working Principle
- Touch toggles relay between ON and OFF
- Relay ON = HIGH signal on RELAY_PIN → appliance powered
- LED mirrors relay state for visual feedback
- State and toggle count printed to serial monitor

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

TOUCH_PIN = 5
RELAY_PIN = 4
LED_PIN   = 18

def setup():
    pinMode(TOUCH_PIN, INPUT)
    pinMode(RELAY_PIN, OUTPUT)
    pinMode(LED_PIN,   OUTPUT)
    digitalWrite(RELAY_PIN, 0)   # Start with relay OFF
    digitalWrite(LED_PIN,   0)

def main():
    setup()
    relay_state  = 0
    last_touch   = 0
    toggle_count = 0

    print("Touch Relay Switch Ready")
    print("Touch to toggle relay (appliance ON/OFF)")
    print("Relay: OFF")

    while True:
        touch = digitalRead(TOUCH_PIN)

        if last_touch == 0 and touch == 1:
            relay_state  = 1 if relay_state == 0 else 0
            toggle_count += 1
            digitalWrite(RELAY_PIN, relay_state)
            digitalWrite(LED_PIN,   relay_state)
            state_str = "ON  ⚡" if relay_state else "OFF 🔌"
            print(f"Relay: {state_str}  (Toggle #{toggle_count})")

        last_touch = touch
        time.sleep(0.05)

def cleanup():
    digitalWrite(RELAY_PIN, 0)
    digitalWrite(LED_PIN,   0)
    print("Relay OFF — System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Touch Relay Switch Ready
Touch to toggle relay (appliance ON/OFF)
Relay: OFF
Relay: ON  ⚡  (Toggle #1)
Relay: OFF 🔌  (Toggle #2)
Relay: ON  ⚡  (Toggle #3)
```

---

## 9. Touch Counter System

### 🎯 Objective
Count touch sensor presses and display a running total, with reset functionality on long press.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Touch Sensor Module | 1 |
| LED (Count Indicator) | 1 |
| Buzzer (Count Beep) | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| TOUCH_PIN | 5 | Touch Sensor Output |
| LED_PIN | 4 | Count Flash LED |
| BUZZER_PIN | 14 | Count Beep Buzzer |

### 💡 Counter Features
- Each short touch → count increases by 1
- Long press (hold > 2 seconds) → counter resets to 0
- LED flashes and buzzer beeps on each count
- Milestone alerts at every 10 counts

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

TOUCH_PIN  = 5
LED_PIN    = 4
BUZZER_PIN = 14

RESET_HOLD = 2.0    # Seconds to hold for reset

def setup():
    pinMode(TOUCH_PIN,  INPUT)
    pinMode(LED_PIN,    OUTPUT)
    pinMode(BUZZER_PIN, OUTPUT)

def count_beep():
    digitalWrite(LED_PIN,    1)
    digitalWrite(BUZZER_PIN, 1)
    time.sleep(0.05)
    digitalWrite(LED_PIN,    0)
    digitalWrite(BUZZER_PIN, 0)

def milestone_beep():
    for _ in range(3):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(LED_PIN,    1)
        time.sleep(0.1)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(LED_PIN,    0)
        time.sleep(0.08)

def reset_beep():
    digitalWrite(BUZZER_PIN, 1)
    time.sleep(0.5)
    digitalWrite(BUZZER_PIN, 0)

def main():
    setup()
    count       = 0
    last_touch  = 0
    press_start = 0

    print("Touch Counter System Ready")
    print("Short touch = Count  |  Hold 2s = Reset")
    print(f"Count: {count}")

    while True:
        touch = digitalRead(TOUCH_PIN)

        # Detect press start
        if last_touch == 0 and touch == 1:
            press_start = time.time()

        # Detect release
        if last_touch == 1 and touch == 0:
            held = time.time() - press_start

            if held >= RESET_HOLD:
                count = 0
                print(f"🔄 RESET! Count: {count}")
                reset_beep()
            else:
                count += 1
                print(f"👆 Count: {count}", end="")

                if count % 10 == 0:
                    print(f"  🎉 Milestone: {count}!")
                    milestone_beep()
                else:
                    print()
                    count_beep()

        last_touch = touch
        time.sleep(0.05)

def cleanup():
    digitalWrite(LED_PIN,    0)
    digitalWrite(BUZZER_PIN, 0)
    print(f"Final Count: {count if 'count' in dir() else 0} — System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Touch Counter System Ready
Short touch = Count  |  Hold 2s = Reset
Count: 0
👆 Count: 1
👆 Count: 2
👆 Count: 9
👆 Count: 10  🎉 Milestone: 10!
👆 Count: 11
🔄 RESET! Count: 0
👆 Count: 1
```

---

## 10. Touch Menu Navigation

### 🎯 Objective
Navigate through a simple on-screen menu using two touch sensors — one to scroll, one to select.

### 🔧 Components
| Component | Quantity |
|---|---|
| ESP32 | 1 |
| Touch Sensor Module | 2 |
| LED (Selection Indicator) | 1 |
| Buzzer | 1 |
| 220Ω Resistor | 1 |

### 📌 Pin Configuration
| Pin | GPIO | Description |
|---|---|---|
| NEXT_TOUCH | 5 | Scroll / Next Item |
| SELECT_TOUCH | 18 | Select / Confirm Item |
| LED_PIN | 4 | Selection Flash |
| BUZZER_PIN | 14 | Navigation Beep |

### 💡 Navigation Controls
| Sensor | Action |
|---|---|
| NEXT_TOUCH | Move to next menu item (wraps around) |
| SELECT_TOUCH | Select the highlighted item |

### 🖥️ Code

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

NEXT_TOUCH   = 5
SELECT_TOUCH = 18
LED_PIN      = 4
BUZZER_PIN   = 14

MENU = [
    "1. LED Blink Test",
    "2. Buzzer Test",
    "3. Sensor Read",
    "4. Motor Test",
    "5. System Info",
]

ACTIONS = [
    "Running LED Blink Test...",
    "Running Buzzer Test...",
    "Reading Sensors...",
    "Testing Motors...",
    "Displaying System Info...",
]

def setup():
    pinMode(NEXT_TOUCH,   INPUT)
    pinMode(SELECT_TOUCH, INPUT)
    pinMode(LED_PIN,      OUTPUT)
    pinMode(BUZZER_PIN,   OUTPUT)

def nav_beep():
    digitalWrite(BUZZER_PIN, 1)
    time.sleep(0.04)
    digitalWrite(BUZZER_PIN, 0)

def select_beep():
    for _ in range(2):
        digitalWrite(BUZZER_PIN, 1)
        digitalWrite(LED_PIN,    1)
        time.sleep(0.1)
        digitalWrite(BUZZER_PIN, 0)
        digitalWrite(LED_PIN,    0)
        time.sleep(0.05)

def display_menu(current):
    print("\n" + "=" * 30)
    print("  📋 MAIN MENU")
    print("=" * 30)
    for i, item in enumerate(MENU):
        if i == current:
            print(f"  ▶ {item}  ◀")
        else:
            print(f"    {item}")
    print("=" * 30)
    print("NEXT = Scroll  |  SELECT = Choose")

def run_action(index):
    print(f"\n✅ Selected: {MENU[index]}")
    print(f"   {ACTIONS[index]}")
    digitalWrite(LED_PIN, 1)
    time.sleep(2)
    digitalWrite(LED_PIN, 0)
    print("   Done! Returning to menu...")

def main():
    setup()
    current     = 0
    last_next   = 0
    last_select = 0

    print("Touch Menu Navigation Ready")
    display_menu(current)

    while True:
        next_t   = digitalRead(NEXT_TOUCH)
        select_t = digitalRead(SELECT_TOUCH)

        # Scroll to next item
        if last_next == 0 and next_t == 1:
            current = (current + 1) % len(MENU)
            nav_beep()
            display_menu(current)

        # Select current item
        if last_select == 0 and select_t == 1:
            select_beep()
            run_action(current)
            display_menu(current)

        last_next   = next_t
        last_select = select_t
        time.sleep(0.05)

def cleanup():
    digitalWrite(LED_PIN,    0)
    digitalWrite(BUZZER_PIN, 0)
    print("Menu System Stopped")

run(main, cleanup)
```

### 📝 Expected Output
```
Touch Menu Navigation Ready

==============================
  📋 MAIN MENU
==============================
  ▶ 1. LED Blink Test  ◀
    2. Buzzer Test
    3. Sensor Read
    4. Motor Test
    5. System Info
==============================
NEXT = Scroll  |  SELECT = Choose

==============================
  📋 MAIN MENU
==============================
    1. LED Blink Test
  ▶ 2. Buzzer Test  ◀
    3. Sensor Read
    4. Motor Test
    5. System Info
==============================
✅ Selected: 2. Buzzer Test
   Running Buzzer Test...
   Done! Returning to menu...
```

---

## 📚 Quick Reference — Touch Sensor Patterns

### Edge Detection (One Trigger Per Touch)
```python
last_touch = 0

while True:
    touch = digitalRead(TOUCH_PIN)

    if last_touch == 0 and touch == 1:
        # Rising edge — trigger ONCE per press
        do_action()

    last_touch = touch
    time.sleep(0.05)
```

### Long Press Detection
```python
press_start = 0
last_touch  = 0

while True:
    touch = digitalRead(TOUCH_PIN)

    if last_touch == 0 and touch == 1:
        press_start = time.time()          # Record press time

    if last_touch == 1 and touch == 0:
        held = time.time() - press_start
        if held >= 2.0:
            long_press_action()            # Held ≥ 2 seconds
        else:
            short_press_action()           # Quick tap

    last_touch = touch
    time.sleep(0.05)
```

### Mode Cycling
```python
MODES  = ["OFF", "LOW", "HIGH"]
mode   = 0

# Each touch advances to next mode
mode = (mode + 1) % len(MODES)
print(MODES[mode])
```

### Two-Sensor Control
```python
pinMode(TOUCH_A, INPUT)
pinMode(TOUCH_B, INPUT)

last_a = 0
last_b = 0

while True:
    a = digitalRead(TOUCH_A)
    b = digitalRead(TOUCH_B)

    if last_a == 0 and a == 1:
        action_a()    # Sensor A pressed

    if last_b == 0 and b == 1:
        action_b()    # Sensor B pressed

    last_a = a
    last_b = b
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

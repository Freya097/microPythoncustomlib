from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

LED_PIN   = 4
TOUCH_PIN = 5

def setup():
    pinMode(LED_PIN, OUTPUT)
    pinMode(TOUCH_PIN, INPUT)

def main():
    setup()
    led_state = 0
    last_touch = 0

    print("Touch Sensor Light Started")

    while True:
        touch = digitalRead(TOUCH_PIN)

        # Toggle LED when touch is detected
        if last_touch == 0 and touch == 1:
            led_state = not led_state
            digitalWrite(LED_PIN, led_state)
            print("LED:", "ON" if led_state else "OFF")

        last_touch = touch
        time.sleep(0.05)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
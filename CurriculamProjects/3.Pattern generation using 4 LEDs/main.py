from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LEDS = [2, 4, 5, 18]

def setup():
    for led in LEDS:
        pinMode(led, OUTPUT)
        digitalWrite(led, 0)

def main():
    setup()
    print("LED Chaser Started")
    while True:
        for led in LEDS:
            digitalWrite(led, 1)
            time.sleep(0.2)
            digitalWrite(led, 0)
        for led in reversed(LEDS):
            digitalWrite(led, 1)
            time.sleep(0.2)
            digitalWrite(led, 0)

def cleanup():
    for led in LEDS:
        digitalWrite(led, 0)
    print("All LEDs OFF — Safe Exit")

run(main, cleanup)
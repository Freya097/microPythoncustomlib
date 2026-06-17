from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

RED_LED = 12
BLUE_LED = 13

def setup():
    pinMode(RED_LED, OUTPUT)
    pinMode(BLUE_LED, OUTPUT)

def main():
    setup()
    print("Police Siren Light Started")

    while True:
        # Red LED flashes
        for i in range(5):
            digitalWrite(RED_LED, 1)
            digitalWrite(BLUE_LED, 0)
            time.sleep(0.1)

            digitalWrite(RED_LED, 0)
            time.sleep(0.1)

        # Blue LED flashes
        for i in range(5):
            digitalWrite(BLUE_LED, 1)
            digitalWrite(RED_LED, 0)
            time.sleep(0.1)

            digitalWrite(BLUE_LED, 0)
            time.sleep(0.1)

        # Fast alternating siren effect
        for i in range(20):
            digitalWrite(RED_LED, 1)
            digitalWrite(BLUE_LED, 0)
            time.sleep(0.05)

            digitalWrite(RED_LED, 0)
            digitalWrite(BLUE_LED, 1)
            time.sleep(0.05)

def cleanup():
    digitalWrite(RED_LED, 0)
    digitalWrite(BLUE_LED, 0)

run(main, cleanup)
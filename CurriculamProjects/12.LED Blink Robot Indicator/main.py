from digital import *
from systemio import run
import time

LEFT_BTN  = 34
RIGHT_BTN = 35

LEFT_LEDS  = [21, 18, 19]
RIGHT_LEDS = [13, 12, 14]

def setup():

    pinMode(LEFT_BTN, INPUT_PULLUP)
    pinMode(RIGHT_BTN, INPUT_PULLUP)

    for led in LEFT_LEDS:
        pinMode(led, OUTPUT)

    for led in RIGHT_LEDS:
        pinMode(led, OUTPUT)

def leds_write(leds, state):
    for led in leds:
        digitalWrite(led, state)

def blink_group(leds, on_time, off_time):
    leds_write(leds, 1)
    time.sleep(on_time)

    leds_write(leds, 0)
    time.sleep(off_time)

def main():

    setup()

    print("Left / Right Indicator")

    while True:

        left_pressed = digitalRead(LEFT_BTN) == 0
        right_pressed = digitalRead(RIGHT_BTN) == 0

        if left_pressed:

            # Moving Mode
            for _ in range(5):
                blink_group(LEFT_LEDS, 0.2, 0.2)

            # Idle Mode
            for _ in range(3):
                blink_group(LEFT_LEDS, 0.8, 0.8)

            # Warning Mode
            for _ in range(10):
                blink_group(LEFT_LEDS, 0.05, 0.05)

        elif right_pressed:

            # Moving Mode
            for _ in range(5):
                blink_group(RIGHT_LEDS, 0.2, 0.2)

            # Idle Mode
            for _ in range(3):
                blink_group(RIGHT_LEDS, 0.8, 0.8)

            # Warning Mode
            for _ in range(10):
                blink_group(RIGHT_LEDS, 0.05, 0.05)

        else:
            leds_write(LEFT_LEDS, 0)
            leds_write(RIGHT_LEDS, 0)

        time.sleep(0.01)

def cleanup():

    leds_write(LEFT_LEDS, 0)
    leds_write(RIGHT_LEDS, 0)

run(main, cleanup)
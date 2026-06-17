from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

RED_PIN    = 15
YELLOW_PIN = 4
GREEN_PIN  = 25

LIGHTS = [RED_PIN, YELLOW_PIN, GREEN_PIN]

def setup():
    for pin in LIGHTS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)

def set_light(red, yellow, green):
    digitalWrite(RED_PIN,    red)
    digitalWrite(YELLOW_PIN, yellow)
    digitalWrite(GREEN_PIN,  green)

def main():
    setup()
    print("Traffic Light Started")
    while True:
        print("RED")
        set_light(1, 0, 0)
        time.sleep(3)

        print("YELLOW")
        set_light(0, 1, 0)
        time.sleep(1)

        print("GREEN")
        set_light(0, 0, 1)
        time.sleep(3)

        print("YELLOW")
        set_light(0, 1, 0)
        time.sleep(1)

def cleanup():
    for pin in LIGHTS:
        digitalWrite(pin, 0)
    print("All lights OFF")

run(main, cleanup)
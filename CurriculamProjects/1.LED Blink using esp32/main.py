from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LED = 2

def setup():
    pinMode(LED, OUTPUT)

def main():
    setup()
    print("LED Blink Started")
    while True:
        digitalWrite(LED, 1)
        print("ON")
        time.sleep(1)
        digitalWrite(LED, 0)
        print("OFF")
        time.sleep(1)

def cleanup():
    digitalWrite(LED, 0)
    print("LED OFF — Safe Exit")

run(main, cleanup)
from digital import pinMode, digitalWrite, digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
import time

LED = 2
BTN = 4

def setup():
    pinMode(LED, OUTPUT)
    pinMode(BTN, INPUT_PULLUP)

def main():
    setup()
    print("Button LED Ready")
    while True:
        digitalWrite(LED, not digitalRead(BTN))
        time.sleep(0.01)

def cleanup():
    digitalWrite(LED, 0)
    print("LED OFF — Safe Exit")

run(main, cleanup)
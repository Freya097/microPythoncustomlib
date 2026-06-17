from analog import analogPin, analogThreshold
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LDR_PIN   = 34
LED_PIN   = 4
THRESHOLD = 2000   # Adjust based on your LDR readings

def setup():
    analogPin(LDR_PIN)
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()

    print(f"LDR Threshold Alert - ADC > {THRESHOLD}")

    while True:
        bright = analogThreshold(LDR_PIN, THRESHOLD, samples=5)

        digitalWrite(LED_PIN, 1 if bright else 0)

        print("BRIGHT ☀️" if bright else "DARK 🌙", end="\r")

        time.sleep(0.2)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
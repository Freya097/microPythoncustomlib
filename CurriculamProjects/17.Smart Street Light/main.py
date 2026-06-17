from analog import analogPin, analogThreshold
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

SENSOR_PIN = 34
LED_PIN    = 4
THRESHOLD  = 2000     # ~48% of 4095 — adjust to your sensor

def setup():
    analogPin(SENSOR_PIN)
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    print(f"Threshold Alert — trigger at ADC > {THRESHOLD}")
    while True:
        triggered = analogThreshold(SENSOR_PIN, THRESHOLD, samples=5)
        digitalWrite(LED_PIN, 1 if triggered else 0)
        print("ALERT!" if triggered else "Normal", end="\r")
        time.sleep(0.2)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
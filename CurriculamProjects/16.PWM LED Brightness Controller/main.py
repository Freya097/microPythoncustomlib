from analog import analogPin, analogRead, mapValue
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

POT_PIN = 34
LED_PIN = 4

def setup():
    analogPin(POT_PIN)
    pwmSetup(LED_PIN, freq=1000)

def main():
    setup()
    print("Pot → LED Brightness")
    while True:
        raw   = analogRead(POT_PIN)              # 0 – 4095
        duty  = mapValue(raw, 0, 4095, 0, 1023)  # map to PWM range
        pwmWrite(LED_PIN, duty)
        print(f"ADC: {raw}  →  PWM Duty: {duty}")
        time.sleep(0.05)

def cleanup():
    pwmStop(LED_PIN)

run(main, cleanup)
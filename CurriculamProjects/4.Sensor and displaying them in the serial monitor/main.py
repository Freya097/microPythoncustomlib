from analog import analogPin, analogSmooth
from systemio import run
import time

SOIL_PIN = 34

def setup():
    analogPin(SOIL_PIN)

def main():
    setup()
    print("Soil Moisture Monitor")

    while True:
        value = analogSmooth(SOIL_PIN, window=12)

        # Adjust if your sensor behaves differently
        moisture = int((4095 - value) * 100 / 4095)

        if moisture < 30:
            status = "DRY ⚠️"
        elif moisture < 70:
            status = "MOIST 🌱"
        else:
            status = "WET 💧"

        print(f"Soil Moisture: {moisture:3d}%   Status: {status}")

        time.sleep(1)

def cleanup():
    print("Stopped")

run(main, cleanup)
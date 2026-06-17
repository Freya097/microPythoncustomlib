from oled import OLED
from systemio import run
import time

def main():
    oled = OLED(scl=22, sda=21)
    oled.clear()
    oled.text("Hello, World!", 0, 0)
    oled.text("MicroPython", 16, 20)
    oled.text(" Ready", 16, 40)
    oled.show()
    print("Display updated")
    while True:
        time.sleep(1)

def cleanup():
    print("Stopped")

run(main, cleanup)
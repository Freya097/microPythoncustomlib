from oled import OLED
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
import time

IRSENSOR_PIN = 5
count   = 0

def main():
    global count
    oled     = OLED(scl=22, sda=21)
    last_btn = 1
    pinMode(IRSENSOR_PIN, INPUT_PULLUP)

    while True:
        btn = digitalRead(IRSENSOR_PIN)
        if last_btn == 1 and btn == 0:
            count += 1
        last_btn = btn

        oled.clear()
        oled.text("Visitor Counter", 0, 0)
        oled.line(0, 12, 128, 12)
        oled.text("Press count:", 0, 24)
        oled.text(str(count), 56, 40)
        oled.show()
        time.sleep(0.05)

def cleanup():
    print("Final count:", count)

run(main, cleanup)
import wifi
import time
import adafruitio
import systemio

SMOKE = 33

# ── setup ────────────────────────────────────────────────
wifi.setWiFi("YOUR_WIFI","YOUR_PASSWORD")
wifi.connect()

io = adafruitio.AdafruitIO( "IOName","YOUR_AIO_KEY")
io.addDevice("light",  18)
io.addDevice("light1", 19)
io.addDevice("light2", 26)
io.addAnalogSensor("sensor", SMOKE)
io.begin()
print("System Ready")

# ── main loop ────────────────────────────────────────────
def main():
    while True:
        io.run()
        wifi.keepAlive()
        time.sleep_ms(100)

# ── cleanup (runs on Ctrl+C or any error) ────────────────
def cleanup():
    print("Disconnecting MQTT...")
    try:
        io.disconnect()
    except:
        pass
    print("Turning off all devices...")
    try:
        io.allOff()       # if your adafruitio lib has this
    except:
        pass

# ── entry point ──────────────────────────────────────────
systemio.run(main, cleanup)

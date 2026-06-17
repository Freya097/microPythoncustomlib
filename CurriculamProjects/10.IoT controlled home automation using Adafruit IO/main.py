import wifi
import time
import adafruitIO
SMOKE = 34
wifi.setWiFi("YOUR_WIFI","YOUR_PASSWORD")
wifi.connect()

io = adafruitIO.AdafruitIO( "IOName","YOUR_AIO_KEY")
io.addDevice("light", 12)
io.addDevice("light1", 13)
io.addDevice("light2", 14)
io.addAnalogSensor("sensor", SMOKE)
io.begin()

print("System Ready")

while True:
    # MQTT + Analog Send
    io.run()
    # WiFi Auto Reconnect
    wifi.keepAlive()
    time.sleep_ms(100)
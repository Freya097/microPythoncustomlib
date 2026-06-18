from machine import Pin, ADC
import urequests
import time
import wifi

# ---------------- WIFI ----------------

SSID = "SSID"
PASSWORD = "Passcode@321#"

wifi.connect(SSID, PASSWORD)

# ---------------- THINGSPEAK ----------------

WRITE_API_KEY = "232323"

READ_API_KEY = "232323"

CHANNEL_ID = "435345345"

# ---------------- RELAYS / LEDs ----------------

relay1 = Pin(12, Pin.OUT)
relay2 = Pin(13, Pin.OUT)
relay3 = Pin(14, Pin.OUT)
relay4 = Pin(27, Pin.OUT)

relays = [relay1, relay2, relay3, relay4]

# OFF initially

for relay in relays:
    relay.value(0)

# ---------------- SMOKE SENSOR ----------------

smoke = ADC(Pin(34))

smoke.atten(ADC.ATTN_11DB)

# ---------------- MAP FUNCTION ----------------

def map_value(x, in_min, in_max, out_min, out_max):

    return int((x - in_min) * (out_max - out_min) /
               (in_max - in_min) + out_min)

# ---------------- MAIN LOOP ----------------

while True:

    try:

        print("--------------------------------")

        # ---------- READ SMOKE SENSOR ----------

        raw = smoke.read()

        smoke_percent = map_value(raw, 0, 4095, 0, 100)

        print("Raw Smoke:", raw)
        print("Smoke %:", smoke_percent)

        # ---------- SEND SMOKE TO THINGSPEAK ----------

        send_url = (
            "https://api.thingspeak.com/update"
            "?api_key={}&field1={}"
        ).format(
            WRITE_API_KEY,
            smoke_percent
        )

        print("Uploading Smoke Data...")

        response = urequests.get(send_url)

        upload_id = response.text

        response.close()

        print("Upload ID:", upload_id)

        # ---------- READ RELAY DATA ----------

        read_url = (
            "https://api.thingspeak.com/channels/{}/feeds/last.json"
            "?api_key={}"
        ).format(
            CHANNEL_ID,
            READ_API_KEY
        )

        print("Reading Relay Data...")

        response = urequests.get(read_url)

        data = response.json()

        response.close()

        print(data)

        # ---------- SAFE FIELD READ ----------

        r1 = int(data.get("field2") or 0)
        r2 = int(data.get("field3") or 0)
        r3 = int(data.get("field4") or 0)
        r4 = int(data.get("field5") or 0)

        values = [r1, r2, r3, r4]

        # ---------- RELAY CONTROL ----------

        for i in range(4):

            if values[i] == 1:

                print("Relay", i + 1, "ON")

                # ACTIVE HIGH RELAY
                relays[i].value(1)

                time.sleep(3)

                print("Relay", i + 1, "OFF")

                relays[i].value(0)

                time.sleep(3)

            else:

                relays[i].value(0)

                print("Relay", i + 1, "OFF")

        # ---------- STATUS ----------

        print("Relay States:")

        print("Relay1:", relay1.value())
        print("Relay2:", relay2.value())
        print("Relay3:", relay3.value())
        print("Relay4:", relay4.value())

    except Exception as e:

        print("ERROR:", e)

    # ThingSpeak free version delay

    time.sleep(15)


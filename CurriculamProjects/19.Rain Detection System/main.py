from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, pwmSetup, pwmWrite, pwmStop, OUTPUT
from systemio import run
import time

# ─── PIN DEFINITIONS ────────────────────────────────────────

RAIN_PIN    = 34    # Rain sensor analog output
BUZZER_PIN  = 14    # Buzzer digital output
SERVO_PIN   = 13    # Servo motor PWM signal

# ─── CONFIGURATION ──────────────────────────────────────────

RAIN_LIMIT  = 30    # % above this = rain detected
ANGLE_RAIN  = 120   # degrees — cover CLOSED (rain)
ANGLE_DRY   = 30    # degrees — cover OPEN   (no rain)

# ─── SERVO HELPERS ──────────────────────────────────────────

def angle_to_duty(angle):
    """
    Convert servo angle (0–180°) to PWM duty (0–1023) at 50Hz.
    Pulse range: 0.5ms (0°) to 2.5ms (180°) within 20ms period.
    duty = 26 + (angle / 180) * 102
    """
    duty = int(26 + (angle / 180) * 102)
    return max(26, min(128, duty))   # clamp within safe range

def servo_move(angle):
    """Move servo to given angle and print confirmation."""
    duty = angle_to_duty(angle)
    pwmWrite(SERVO_PIN, duty)
    print(f"[SERVO] Moving to {angle}°  (duty={duty})")

# ─── BUZZER SIREN ───────────────────────────────────────────

def siren():
    """3 short beeps to indicate rain alert."""
    for _ in range(3):
        digitalWrite(BUZZER_PIN, 1)
        time.sleep_ms(100)
        digitalWrite(BUZZER_PIN, 0)
        time.sleep_ms(100)

# ─── SETUP ──────────────────────────────────────────────────

def setup():
    # Sensor
    analogPin(RAIN_PIN)

    # Buzzer
    pinMode(BUZZER_PIN, OUTPUT)
    digitalWrite(BUZZER_PIN, 0)

    # Servo — 50Hz is the standard frequency for servo motors
    pwmSetup(SERVO_PIN, freq=50)

    # Start at dry position
    servo_move(ANGLE_DRY)
    time.sleep_ms(500)

    print("=" * 38)
    print("  Rain Detection + Servo System")
    print("=" * 38)
    print(f"  Rain threshold : {RAIN_LIMIT}%")
    print(f"  Servo DRY      : {ANGLE_DRY}°  (open)")
    print(f"  Servo RAIN     : {ANGLE_RAIN}°  (closed)")
    print("-" * 38)

# ─── MAIN LOOP ──────────────────────────────────────────────

def main():
    setup()

    prev_state = None    # track state changes to avoid repeated servo moves

    while True:

        # Rain sensor reads HIGH when dry, LOW when wet
        # So invert: 100 - percent = actual rain level
        rain = 100 - analogPercent(RAIN_PIN)

        if rain > RAIN_LIMIT:

            # ── RAIN DETECTED ──────────────────────────
            status = "RAIN DETECTED"

            if prev_state != "RAIN":
                servo_move(ANGLE_RAIN)   # close cover → 120°
                prev_state = "RAIN"

            siren()                      # beep alarm
            print(f"[SENSOR] Rain: {rain:3d}%  Status: {status} ☔")

        else:

            # ── NO RAIN ────────────────────────────────
            status = "NO RAIN"

            if prev_state != "DRY":
                servo_move(ANGLE_DRY)    # open cover → 30°
                prev_state = "DRY"

            digitalWrite(BUZZER_PIN, 0)  # buzzer off
            print(f"[SENSOR] Rain: {rain:3d}%  Status: {status} ☀")

        time.sleep(1)

# ─── CLEANUP ────────────────────────────────────────────────

def cleanup():
    servo_move(ANGLE_DRY)        # return to open position
    time.sleep_ms(500)
    pwmStop(SERVO_PIN)           # release servo PWM
    digitalWrite(BUZZER_PIN, 0)  # buzzer off
    print("\n[CLEANUP] System stopped safely")

# ─── RUN ────────────────────────────────────────────────────

run(main, cleanup)
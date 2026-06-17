from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

# Flame Sensor
FLAME_PIN = 34
FIRE_LIMIT = 30

# Motors
LEFT_MOTOR_1  = 12
LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2
RIGHT_MOTOR_2 = 4

# Buzzer
BUZZER_PIN = 14

def setup():
    analogPin(FLAME_PIN)

    pinMode(LEFT_MOTOR_1, OUTPUT)
    pinMode(LEFT_MOTOR_2, OUTPUT)
    pinMode(RIGHT_MOTOR_1, OUTPUT)
    pinMode(RIGHT_MOTOR_2, OUTPUT)

    pinMode(BUZZER_PIN, OUTPUT)

def move_forward():
    digitalWrite(LEFT_MOTOR_1, 1)
    digitalWrite(LEFT_MOTOR_2, 0)

    digitalWrite(RIGHT_MOTOR_1, 1)
    digitalWrite(RIGHT_MOTOR_2, 0)

def stop_robot():
    digitalWrite(LEFT_MOTOR_1, 0)
    digitalWrite(LEFT_MOTOR_2, 0)

    digitalWrite(RIGHT_MOTOR_1, 0)
    digitalWrite(RIGHT_MOTOR_2, 0)

def buzzer_on():
    digitalWrite(BUZZER_PIN, 1)

def buzzer_off():
    digitalWrite(BUZZER_PIN, 0)

def main():
    setup()

    print("Fire Alarm Robot Started")

    while True:
        fire_level = 100 - analogPercent(FLAME_PIN)

        print("Fire Level:", fire_level, "%")

        if fire_level > FIRE_LIMIT:
            print("🔥 FIRE DETECTED!")

            stop_robot()
            buzzer_on()

        else:
            print("✅ Area Safe")

            buzzer_off()
            move_forward()

        time.sleep(0.2)

def cleanup():
    stop_robot()
    buzzer_off()

run(main, cleanup)
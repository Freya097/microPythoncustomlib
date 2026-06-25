# ============================================================
#  motor.py  –  DC Motor Driver Library for MicroPython
#  Supports: L298N / L293D / TB6612 (dual H-bridge)
#  PWM speed control via digital.py  (optional)
#  No PWM = just direction pins  (simple on/off)
# ============================================================
#
#  HOW A DC MOTOR DRIVER WORKS (student notes)
#  ─────────────────────────────────────────────
#  A motor driver chip (L298N etc.) has two pins per motor:
#    IN1 (or A)  + IN2 (or B)
#
#  Truth table:
#    IN1=1  IN2=0  →  Motor spins FORWARD
#    IN1=0  IN2=1  →  Motor spins REVERSE
#    IN1=0  IN2=0  →  Motor STOPS (coast / free spin)
#    IN1=1  IN2=1  →  Motor BRAKES (short-circuit stop)
#
#  PWM (optional):
#    Connect the driver's ENA/ENB pin to an ESP32 GPIO.
#    PWM duty 0–100% controls speed.
#    If no EN pin is wired, the motor runs at full speed.
#
# ============================================================

from machine import Pin
import time

# Try to import digital.py for PWM support
try:
    import digital as _dig
    _PWM_AVAILABLE = True
except ImportError:
    _PWM_AVAILABLE = False


# ── Single Motor ──────────────────────────────────────────────

class Motor:
    """
    Controls one DC motor through a H-bridge driver (L298N / L293D).

    Parameters (all required except en_pin and pwm_freq)
    ──────────────────────────────────────────────────────
    in1_pin  : GPIO number for IN1 / A pin
    in2_pin  : GPIO number for IN2 / B pin
    en_pin   : GPIO number for ENA/ENB pin  (optional – omit if not wired)
    pwm_freq : PWM frequency in Hz           (default 1000 Hz)

    Usage
    ─────
    m = Motor(in1_pin=2, in2_pin=4)              # no speed control
    m = Motor(in1_pin=2, in2_pin=4, en_pin=5)    # with PWM speed

    m.forward()          # full speed forward
    m.forward(75)        # 75% speed forward
    m.reverse(50)        # 50% speed reverse
    m.stop()             # coast stop
    m.brake()            # hard brake
    m.speed(80)          # change speed without changing direction
    """

    def __init__(self, in1_pin: int, in2_pin: int,
                 en_pin: int = None, pwm_freq: int = 1000):

        self._in1 = Pin(in1_pin, Pin.OUT)
        self._in2 = Pin(in2_pin, Pin.OUT)
        self._en_pin   = en_pin
        self._has_pwm  = False
        self._cur_dir  = 0      # 0=stop  1=fwd  -1=rev
        self._cur_spd  = 100    # last set speed %

        # Set up PWM on EN pin if provided and digital.py is available
        if en_pin is not None:
            if _PWM_AVAILABLE:
                _dig.pwmSetup(en_pin, pwm_freq)
                self._has_pwm = True
            else:
                # Fall back to plain output (always-on)
                self._en_gpio = Pin(en_pin, Pin.OUT)
                self._en_gpio.on()

        self.stop()   # safe initial state

    # ── Internal helpers ──────────────────────────────────────

    def _set_pins(self, in1: int, in2: int):
        self._in1.value(in1)
        self._in2.value(in2)

    def _apply_speed(self, percent: int):
        """Set EN pin PWM to percent (0-100). No-op if no EN pin."""
        if self._has_pwm and self._en_pin is not None:
            _dig.pwmWritePercent(self._en_pin, max(0, min(100, percent)))
        self._cur_spd = max(0, min(100, percent))

    # ── Public API ────────────────────────────────────────────

    def forward(self, speed: int = 100):
        """
        Spin motor forward.

        Parameters
        ----------
        speed : 0-100 percent  (only used if en_pin was declared)
        """
        self._apply_speed(speed)
        self._set_pins(1, 0)
        self._cur_dir = 1

    def reverse(self, speed: int = 100):
        """
        Spin motor in reverse.

        Parameters
        ----------
        speed : 0-100 percent  (only used if en_pin was declared)
        """
        self._apply_speed(speed)
        self._set_pins(0, 1)
        self._cur_dir = -1

    def stop(self):
        """Coast stop – motor freewheels to a halt."""
        self._set_pins(0, 0)
        if self._has_pwm and self._en_pin is not None:
            _dig.pwmWritePercent(self._en_pin, 0)
        self._cur_dir = 0

    def brake(self):
        """Hard brake – short-circuits motor terminals, stops instantly."""
        self._set_pins(1, 1)
        self._cur_dir = 0

    def speed(self, percent: int):
        """
        Change speed without changing direction.
        Call after forward() or reverse() to adjust mid-run.

        Parameters
        ----------
        percent : 0-100
        """
        self._apply_speed(percent)
        # Re-apply current direction at new speed
        if   self._cur_dir ==  1: self._set_pins(1, 0)
        elif self._cur_dir == -1: self._set_pins(0, 1)

    def ramp(self, target: int, step: int = 5, delay_ms: int = 50):
        """
        Smoothly ramp speed from current to target percent.

        Parameters
        ----------
        target   : target speed percent (0-100)
        step     : how many % to change per tick
        delay_ms : milliseconds between ticks
        """
        cur = self._cur_spd
        direction = 1 if target > cur else -1
        for s in range(cur, target + direction, direction * step):
            self.speed(max(0, min(100, s)))
            time.sleep_ms(delay_ms)
        self.speed(target)   # ensure we land exactly on target

    def get_speed(self) -> int:
        """Return current speed percent (0-100)."""
        return self._cur_spd

    def get_direction(self) -> str:
        """Return current direction as a string."""
        return {1: "forward", -1: "reverse", 0: "stop"}[self._cur_dir]


# ── Robot (two motors) ────────────────────────────────────────

class Robot:
    """
    Two-wheel differential drive robot.

    Uses two Motor instances internally.
    All movement commands accept an optional speed (0-100%).

    Parameters
    ──────────
    left_in1  : GPIO for left  motor IN1
    left_in2  : GPIO for left  motor IN2
    right_in1 : GPIO for right motor IN1
    right_in2 : GPIO for right motor IN2
    left_en   : GPIO for left  motor ENA  (optional – PWM speed)
    right_en  : GPIO for right motor ENB  (optional – PWM speed)
    pwm_freq  : PWM frequency in Hz        (default 1000)

    Usage
    ─────
    # No PWM (simple direction only)
    bot = Robot(left_in1=2, left_in2=4, right_in1=16, right_in2=17)

    # With PWM speed control
    bot = Robot(left_in1=2, left_in2=4, right_in1=16, right_in2=17,
                left_en=5, right_en=18)

    bot.forward(80)
    bot.left(60)
    bot.stop()
    """

    def __init__(self,
                 left_in1:  int, left_in2:  int,
                 right_in1: int, right_in2: int,
                 left_en:   int = None,
                 right_en:  int = None,
                 pwm_freq:  int = 1000):

        self.left  = Motor(left_in1,  left_in2,  en_pin=left_en,  pwm_freq=pwm_freq)
        self.right = Motor(right_in1, right_in2, en_pin=right_en, pwm_freq=pwm_freq)

    # ── Movement commands ─────────────────────────────────────

    def forward(self, speed: int = 100):
        """Drive straight forward."""
        self.left.forward(speed)
        self.right.forward(speed)

    def reverse(self, speed: int = 100):
        """Drive straight backward."""
        self.left.reverse(speed)
        self.right.reverse(speed)

    def left(self, speed: int = 60):
        """
        Turn left in place (left motor reverse, right forward).
        Both motors turn the robot on its axis.
        """
        self.left.reverse(speed)
        self.right.forward(speed)

    def right(self, speed: int = 60):
        """
        Turn right in place (right motor reverse, left forward).
        """
        self.left.forward(speed)
        self.right.reverse(speed)

    def pivot_left(self, speed: int = 60):
        """Gentle left curve – right motor only."""
        self.left.stop()
        self.right.forward(speed)

    def pivot_right(self, speed: int = 60):
        """Gentle right curve – left motor only."""
        self.left.forward(speed)
        self.right.stop()

    def stop(self):
        """Coast stop both motors."""
        self.left.stop()
        self.right.stop()

    def brake(self):
        """Hard brake both motors instantly."""
        self.left.brake()
        self.right.brake()

    def speed(self, percent: int):
        """Set speed on both motors without changing direction."""
        self.left.speed(percent)
        self.right.speed(percent)

    def ramp_forward(self, target: int = 100, step: int = 5, delay_ms: int = 50):
        """Smoothly ramp both motors forward to target speed."""
        for s in range(0, target + step, step):
            s = min(s, target)
            self.left.forward(s)
            self.right.forward(s)
            time.sleep_ms(delay_ms)

    def ramp_stop(self, step: int = 5, delay_ms: int = 50):
        """Smoothly slow down and stop."""
        cur = self.left.get_speed()
        for s in range(cur, -step, -step):
            s = max(s, 0)
            self.left.speed(s)
            self.right.speed(s)
            time.sleep_ms(delay_ms)
        self.stop()

    def move(self, command: str, speed: int = 100):
        """
        String-command interface – useful for Bluetooth / serial control.

        Commands: 'F' forward  'B' reverse  'L' left  'R' right
                  'S' stop     'X' brake
        """
        cmd = command.upper().strip()
        actions = {
            'F': lambda: self.forward(speed),
            'B': lambda: self.reverse(speed),
            'L': lambda: self.left(speed),
            'R': lambda: self.right(speed),
            'S': self.stop,
            'X': self.brake,
        }
        fn = actions.get(cmd)
        if fn:
            fn()
        else:
            print(f"[motor] Unknown command: '{cmd}'")

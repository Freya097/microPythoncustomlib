# ================================================================
#  buzzer.py  –  Buzzer Tones & Melody Library  (MicroPython)
#  Built on top of digital.py  (uses pwmSetup / pwmWrite / pwmStop)
#
#  Supports:
#    • Single beep / burst beep
#    • Musical note frequencies  (C3 – B6)
#    • Play melodies from note lists
#    • Built-in tones: alert, success, error, startup, mario, etc.
#    • SOS morse pattern
#    • Passive buzzer  (PWM tones)  or  Active buzzer  (on/off only)
#
#  Wiring:
#    Passive buzzer (+) → GPIO pin → 100Ω → GND
#    Active  buzzer (+) → GPIO pin,  (-)  → GND
# ================================================================

import time
import digital as _d     # digital.py must be on the device

# ── Note frequency table (Hz)  ────────────────────────────────
#    Octave 3-6 covers the useful buzzer range
NOTES = {
    # Octave 3
    "C3": 131,  "CS3": 139, "D3": 147,  "DS3": 156,
    "E3": 165,  "F3": 175,  "FS3": 185, "G3": 196,
    "GS3": 208, "A3": 220,  "AS3": 233, "B3": 247,
    # Octave 4
    "C4": 262,  "CS4": 277, "D4": 294,  "DS4": 311,
    "E4": 330,  "F4": 349,  "FS4": 370, "G4": 392,
    "GS4": 415, "A4": 440,  "AS4": 466, "B4": 494,
    # Octave 5
    "C5": 523,  "CS5": 554, "D5": 587,  "DS5": 622,
    "E5": 659,  "F5": 698,  "FS5": 740, "G5": 784,
    "GS5": 831, "A5": 880,  "AS5": 932, "B5": 988,
    # Octave 6
    "C6": 1047, "CS6": 1109,"D6": 1175, "DS6": 1245,
    "E6": 1319, "F6": 1397, "FS6": 1480,"G6": 1568,
    "GS6": 1661,"A6": 1760, "AS6": 1865,"B6": 1976,
    # Aliases  (no sharp sign)
    "C":  262, "D":  294, "E":  330, "F":  349,
    "G":  392, "A":  440, "B":  494,
    # Special
    "REST": 0,
}

# ── Built-in melody definitions ───────────────────────────────
#    Each melody = list of (note_name, duration_ms)
#    note_name "REST" = silence

MELODIES = {

    "startup": [
        ("C4", 100), ("E4", 100), ("G4", 100), ("C5", 200),
    ],

    "success": [
        ("G4", 120), ("A4", 120), ("B4", 120), ("C5", 240),
    ],

    "error": [
        ("G4", 150), ("REST", 60), ("D4", 150), ("REST", 60), ("C4", 300),
    ],

    "alert": [
        ("A5", 80), ("REST", 60), ("A5", 80), ("REST", 60), ("A5", 80),
    ],

    "beep_double": [
        ("C5", 80), ("REST", 80), ("C5", 80),
    ],

    "beep_triple": [
        ("C5", 80), ("REST", 60), ("C5", 80), ("REST", 60), ("C5", 80),
    ],

    "warning": [
        ("E5", 200), ("REST", 100), ("E5", 200), ("REST", 100),
        ("E5", 200), ("REST", 100), ("C5", 400),
    ],

    "mario": [
        ("E5", 150), ("E5", 150), ("REST", 150), ("E5", 150),
        ("REST", 150), ("C5", 150), ("E5", 150), ("REST", 150),
        ("G5", 150), ("REST", 300), ("G4", 150), ("REST", 300),
        ("C5", 200), ("REST", 150), ("G4", 200), ("REST", 150),
        ("E4", 200), ("REST", 150), ("A4", 150), ("REST", 150),
        ("B4", 150), ("REST", 150), ("AS4", 150), ("A4", 150),
        ("REST", 150), ("G4", 150), ("E5", 150), ("G5", 150),
        ("A5", 200), ("REST", 150), ("F5", 150), ("G5", 150),
        ("REST", 150), ("E5", 150), ("REST", 150), ("C5", 150),
        ("D5", 150), ("B4", 200),
    ],

    "birthday": [
        ("C4", 200), ("C4", 100), ("D4", 300), ("C4", 300),
        ("F4", 300), ("E4", 600), ("C4", 200), ("C4", 100),
        ("D4", 300), ("C4", 300), ("G4", 300), ("F4", 600),
    ],

    "sos": [
        # S = ...  O = ---  S = ...
        ("C5", 100), ("REST", 80), ("C5", 100), ("REST", 80), ("C5", 100),
        ("REST", 160),
        ("C5", 300), ("REST", 80), ("C5", 300), ("REST", 80), ("C5", 300),
        ("REST", 160),
        ("C5", 100), ("REST", 80), ("C5", 100), ("REST", 80), ("C5", 100),
        ("REST", 400),
    ],

    "scale_up": [
        ("C4", 120), ("D4", 120), ("E4", 120), ("F4", 120),
        ("G4", 120), ("A4", 120), ("B4", 120), ("C5", 240),
    ],

    "scale_down": [
        ("C5", 120), ("B4", 120), ("A4", 120), ("G4", 120),
        ("F4", 120), ("E4", 120), ("D4", 120), ("C4", 240),
    ],
}


# ================================================================
#  Buzzer class
# ================================================================

class Buzzer:
    """
    Buzzer driver for MicroPython  (passive PWM or active on/off).

    Parameters
    ──────────
    pin    : GPIO pin number
    active : True  = active  buzzer (digital HIGH/LOW only)
             False = passive buzzer (PWM frequency control)  ← default

    Usage
    ─────
    from buzzer import Buzzer
    bz = Buzzer(pin=15)

    bz.beep()                    # single beep
    bz.beep(freq=1000, ms=300)   # custom frequency + duration
    bz.tone("alert")             # built-in tone
    bz.note("E5", 200)           # single musical note
    bz.melody([("C4",200),("E4",200),("G4",400)])  # custom melody
    bz.sos()                     # SOS distress signal
    """

    def __init__(self, pin: int, active: bool = False):
        self._pin    = pin
        self._active = active

        if active:
            # Active buzzer: just a digital output
            _d.pinMode(pin, _d.OUTPUT)
            _d.digitalWrite(pin, 0)
        else:
            # Passive buzzer: set up PWM, start silent
            _d.pwmSetup(pin, freq=1000)
            _d.pwmWrite(pin, 0)          # 0 duty = silent

    # ── Internal ──────────────────────────────────────────────

    def _play_freq(self, freq: int, duty: int = 512):
        """Start a tone at freq Hz  (passive only, duty 0-1023)."""
        if self._active:
            _d.digitalWrite(self._pin, 1)
        else:
            if freq == 0:
                _d.pwmWrite(self._pin, 0)
            else:
                _d.pwmFreq(self._pin, freq)
                _d.pwmWrite(self._pin, duty)

    def _silent(self):
        """Stop any tone."""
        if self._active:
            _d.digitalWrite(self._pin, 0)
        else:
            _d.pwmWrite(self._pin, 0)

    # ── Public API ────────────────────────────────────────────

    def beep(self, freq: int = 1000, ms: int = 200, duty: int = 512):
        """
        Play a single beep.

        Parameters
        ──────────
        freq : tone frequency in Hz  (default 1000)
        ms   : duration in milliseconds  (default 200)
        duty : PWM duty 0-1023, controls volume  (default 512 = 50%)
        """
        self._play_freq(freq, duty)
        time.sleep_ms(ms)
        self._silent()

    def beep_burst(self, count: int = 3, freq: int = 1000,
                   on_ms: int = 100, off_ms: int = 80):
        """
        Rapid repeated beeps.

        Parameters
        ──────────
        count  : number of beeps
        freq   : tone frequency Hz
        on_ms  : beep on duration ms
        off_ms : gap between beeps ms
        """
        for i in range(count):
            self._play_freq(freq)
            time.sleep_ms(on_ms)
            self._silent()
            if i < count - 1:
                time.sleep_ms(off_ms)

    def note(self, name: str, ms: int = 200, duty: int = 512):
        """
        Play a single musical note by name.

        Parameters
        ──────────
        name : note name e.g. "C4", "G5", "FS4", "REST"
               see NOTES dict for full list
        ms   : duration in milliseconds
        duty : volume (0-1023)

        Example
        ───────
        bz.note("A4", 300)
        bz.note("REST", 100)   # silence gap
        """
        freq = NOTES.get(name.upper(), 0)
        if freq == 0:
            time.sleep_ms(ms)   # REST
        else:
            self._play_freq(freq, duty)
            time.sleep_ms(ms)
            self._silent()

    def melody(self, notes: list, duty: int = 512):
        """
        Play a melody from a list of (note_name, duration_ms) tuples.

        Parameters
        ──────────
        notes : list of (note, ms)  e.g. [("C4",200), ("E4",200)]
        duty  : volume (0-1023)

        Example
        ───────
        bz.melody([("C4",200),("E4",200),("G4",200),("C5",400)])
        """
        for name, ms in notes:
            freq = NOTES.get(name.upper(), 0)
            if freq == 0:
                self._silent()
                time.sleep_ms(ms)
            else:
                self._play_freq(freq, duty)
                time.sleep_ms(ms)
                self._silent()
                time.sleep_ms(20)   # tiny gap between notes

    def tone(self, name: str, duty: int = 512):
        """
        Play a built-in tone by name.

        Available tones:
          startup, success, error, alert, warning
          beep_double, beep_triple
          mario, birthday, sos, scale_up, scale_down

        Example
        ───────
        bz.tone("success")
        bz.tone("mario")
        """
        mel = MELODIES.get(name)
        if mel is None:
            print("[buzzer] Unknown tone: '{}'. Available: {}".format(
                name, list(MELODIES.keys())))
            return
        self.melody(mel, duty)

    def sweep(self, start_hz: int = 200, end_hz: int = 2000,
              step: int = 50, ms_per_step: int = 20):
        """
        Frequency sweep from start_hz to end_hz.
        Creates a rising or falling siren effect.

        Example
        ───────
        bz.sweep(200, 2000)       # rising sweep
        bz.sweep(2000, 200, 50)   # falling sweep
        """
        direction = 1 if end_hz > start_hz else -1
        freq = start_hz
        while (direction == 1 and freq <= end_hz) or \
              (direction == -1 and freq >= end_hz):
            self._play_freq(freq)
            time.sleep_ms(ms_per_step)
            freq += direction * step
        self._silent()

    def siren(self, cycles: int = 3, low: int = 600, high: int = 1200,
              step: int = 30, ms_per_step: int = 15):
        """
        Siren: sweep up then down, repeated.

        Parameters
        ──────────
        cycles      : how many up-down cycles
        low / high  : frequency range Hz
        step        : Hz per step
        ms_per_step : ms per step (lower = faster)
        """
        for _ in range(cycles):
            self.sweep(low,  high, step, ms_per_step)
            self.sweep(high, low,  step, ms_per_step)

    def sos(self):
        """Play SOS morse code pattern (…---…)."""
        self.tone("sos")

    def silent(self):
        """Stop any currently playing tone immediately."""
        self._silent()

    def cleanup(self):
        """Stop tone and release PWM resource."""
        self._silent()
        if not self._active:
            _d.pwmStop(self._pin)

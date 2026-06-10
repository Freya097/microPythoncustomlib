# ============================================================
#  dino.py  —  T-Rex Game  |  All Components / Game Engine
#  Works with : oled.py  (your uploaded full-featured library)
#
#  WHAT IS INSIDE THIS FILE
#  ─────────────────────────
#  SECTION 1 : PIN CONFIG   — button GPIO number
#  SECTION 2 : SPRITES      — dino icon, tree icon (pixel art)
#  SECTION 3 : GAME STATE   — all game variables in one dict
#  SECTION 4 : JUMP         — button read + gravity physics
#  SECTION 5 : TREE         — scroll + score + speed-up
#  SECTION 6 : COLLISION    — hit detection
#  SECTION 7 : DRAW DINO    — animated sprite
#  SECTION 8 : DRAW TREE    — cactus sprite
#  SECTION 9 : DRAW GROUND  — ground line + scrolling pebbles
#  SECTION 10: DRAW SCORE   — SC / HI text at top
#  SECTION 11: SPLASH SCREEN
#  SECTION 12: GAME OVER SCREEN
# ============================================================

from machine import Pin
import framebuf, time, random


# ============================================================
#  SECTION 1 — PIN CONFIGURATION
#  Change BTN_PIN if your button is on a different GPIO.
#  Default = GPIO 0 (built-in BOOT button on most ESP32 boards)
# ============================================================

BTN_PIN = 14
_btn    = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)   # LOW when pressed

def is_pressed():
    """True while jump button is held down."""
    return _btn.value() == 0

def wait_press():
    """Block until button is pressed, then released."""
    while not is_pressed(): time.sleep_ms(10)
    while is_pressed():     time.sleep_ms(10)


# ============================================================
#  SECTION 2 — SPRITES  (8 x 8 pixel icons)
#  Format : MONO_HLSB  — one byte per row, bit-7 = left pixel
#
#  Reading the bits visually (1 = white pixel, 0 = black):
#    0b00011100  →  ...XXX..
#    0b01111110  →  .XXXXXX.
# ============================================================

# ── Dino frame A — right leg forward ────────────────────────
_DINO_A_DATA = bytearray([
    0b00011100,   # ...XXX..   head top
    0b00011110,   # ...XXXX.   head + eye
    0b01111100,   # .XXXXX..   neck + body
    0b11111100,   # XXXXXX..   body
    0b11111110,   # XXXXXXX.   full body
    0b01111000,   # .XXXX...   lower body
    0b01100000,   # .XX.....   legs  (right leg forward)
    0b00100000,   # ..X.....
])

# ── Dino frame B — left leg forward  (run animation swap) ───
_DINO_B_DATA = bytearray([
    0b00011100,   # ...XXX..   head top
    0b00011110,   # ...XXXX.   head + eye
    0b01111100,   # .XXXXX..   neck + body
    0b11111100,   # XXXXXX..   body
    0b11111110,   # XXXXXXX.   full body
    0b01111000,   # .XXXX...   lower body
    0b00101000,   # ..X.X...   legs  (left leg forward)
    0b00100000,   # ..X.....
])

# ── Tree / Cactus icon ───────────────────────────────────────
_TREE_DATA = bytearray([
    0b00010000,   # ...X....   tip
    0b00010000,   # ...X....
    0b10010000,   # X..X....   left arm
    0b11110000,   # XXXX....
    0b11111000,   # XXXXX...   right arm joins
    0b00111000,   # ..XXX...
    0b00010000,   # ...X....   trunk
    0b00011000,   # ...XX...   base
])

# Build FrameBuffer objects (needed to blit onto the OLED fb)
dino_a = framebuf.FrameBuffer(_DINO_A_DATA, 8, 8, framebuf.MONO_HLSB)
dino_b = framebuf.FrameBuffer(_DINO_B_DATA, 8, 8, framebuf.MONO_HLSB)
tree   = framebuf.FrameBuffer(_TREE_DATA,   8, 8, framebuf.MONO_HLSB)


# ============================================================
#  SECTION 3 — GAME STATE
#  One dictionary holds every variable the game needs.
#  reset_game() restores all of them (except hi = high score).
# ============================================================

GROUND = 54    # y-pixel of the ground line on screen
DINO_X = 10   # dino stays fixed at this x position

state = {
    "dy":     GROUND - 8,   # dino top-y  (8px sprite, so feet = GROUND)
    "vy":     0,            # dino vertical velocity (negative = upward)
    "tx":     128,          # tree x position (starts off-screen right)
    "score":  0,            # points scored this round
    "hi":     0,            # all-time high score (never reset)
    "speed":  2,            # tree scroll speed in pixels per frame
    "alive":  True,         # False triggers game-over screen
    "frame":  0,            # frame counter used for leg animation
    "dots":   [i * 16 for i in range(8)],  # ground pebble x positions
}

def reset_game():
    """Restart game. Keeps high score."""
    state["dy"]    = GROUND - 8
    state["vy"]    = 0
    state["tx"]    = 128
    state["score"] = 0
    state["speed"] = 2
    state["alive"] = True
    state["frame"] = 0
    state["dots"]  = [i * 16 for i in range(8)]


# ============================================================
#  SECTION 4 — JUMP FUNCTION
#  Called every frame from main.py.
#  Reads the button, applies upward velocity, then gravity.
# ============================================================

def jump():
    """
    Handle jump input + gravity physics.
    Call once per frame in the game loop.
    """
    # Only allow jump when dino is standing on the ground
    if is_pressed() and state["dy"] >= GROUND - 8:
        state["vy"] = -8          # kick upward  (negative = up on screen)

    # Gravity pulls dino down every frame
    state["vy"] += 1              # velocity gets more positive each frame
    state["dy"] += state["vy"]   # move dino by current velocity

    # Floor clamp — never sink below the ground
    if state["dy"] >= GROUND - 8:
        state["dy"] = GROUND - 8
        state["vy"] = 0


# ============================================================
#  SECTION 5 — TREE (OBSTACLE) FUNCTION
#  Called every frame from main.py.
#  Scrolls the tree left, resets it, updates score & speed.
# ============================================================

def move_tree():
    """
    Scroll tree left by current speed.
    When it exits left edge: reset, add score, maybe speed up.
    Call once per frame in the game loop.
    """
    state["tx"] -= state["speed"]

    # Tree has fully left the screen on the left side
    if state["tx"] < -8:
        # Reappear at right with a random gap
        state["tx"]    = 128 + random.randint(10, 40)
        state["score"] += 1

        # Keep high score updated live
        if state["score"] > state["hi"]:
            state["hi"] = state["score"]

        # Speed up every 3 points cleared, max speed = 7
        if state["speed"] < 7 and state["score"] % 3 == 0:
            state["speed"] += 1


# ============================================================
#  SECTION 6 — COLLISION FUNCTION
#  Simple AABB (Axis-Aligned Bounding Box) check.
#  PAD shrinks the hitbox a little so it feels fair.
# ============================================================

def check_collision():
    """
    Detect overlap between dino and tree.
    Sets state["alive"] = False when hit.
    Call once per frame in the game loop.
    """
    PAD = 2                          # forgiveness pixels (smaller = harder)
    # Dino box
    dx, dy, dw, dh = DINO_X, state["dy"], 8, 8
    # Tree box
    tx, ty, tw, th = state["tx"], GROUND - 8, 8, 8

    hit = (
        dx + PAD     < tx + tw - PAD and   # dino right edge > tree left
        dx + dw - PAD > tx + PAD      and   # dino left edge  < tree right
        dy + PAD     < ty + th        and   # dino bottom     > tree top
        dy + dh      > ty + PAD             # dino top        < tree bottom
    )
    if hit:
        state["alive"] = False


# ============================================================
#  SECTION 7 — DRAW DINO
#  Uses oled.blit() to paste the sprite.
#  Alternates between frame A and B every 6 frames → run anim.
#  Stops animation when in the air (jumping).
# ============================================================

def draw_dino(oled):
    """
    Draw animated dino sprite at its current position.
    Pass the OLED object from main.py.
    """
    state["frame"] += 1
    in_air = state["dy"] < GROUND - 8

    if in_air or (state["frame"] // 6) % 2 == 0:
        oled.blit(dino_a, DINO_X, state["dy"])   # frame A
    else:
        oled.blit(dino_b, DINO_X, state["dy"])   # frame B


# ============================================================
#  SECTION 8 — DRAW TREE
#  Pastes the cactus icon at its current x position.
# ============================================================

def draw_tree(oled):
    """
    Draw cactus sprite at current scroll position.
    Pass the OLED object from main.py.
    """
    oled.blit(tree, state["tx"], GROUND - 8)


# ============================================================
#  SECTION 9 — DRAW GROUND
#  Ground line + scrolling pebble dots for motion feel.
# ============================================================

def draw_ground(oled):
    """
    Draw ground line and scrolling pebbles.
    Pass the OLED object from main.py.
    """
    # Solid ground line
    oled.hline(0, GROUND, 128)

    # Scroll pebble dots left at same speed as tree
    for i in range(len(state["dots"])):
        state["dots"][i] -= state["speed"]
        if state["dots"][i] < 0:
            state["dots"][i] += 128           # wrap around to the right
        oled.pixel(state["dots"][i],      GROUND + 2)
        oled.pixel((state["dots"][i]+6) % 128, GROUND + 4)


# ============================================================
#  SECTION 10 — DRAW SCORE
#  Shows current score (left) and high score (right).
#  Uses oled.text() and oled.right_text() from your library.
# ============================================================

def draw_score(oled):
    """
    Draw score bar at top of screen.
    Pass the OLED object from main.py.
    """
    oled.text("SC:{}".format(state["score"]), 0, 0)
    oled.right_text("HI:{}".format(state["hi"]), 0, margin=2)


# ============================================================
#  SECTION 11 — SPLASH SCREEN
#  Uses: center_text(), blit(), hline(), h_bar()
#  Shows title, dino + tree icons, instruction text.
#  Waits for button press before returning.
# ============================================================

def show_splash(oled):
    """
    Display title / start screen.
    Blocks until player presses jump button.
    Pass the OLED object from main.py.
    """
    oled.clear()

    # Title with a filled top bar (uses status_bar from your library)
    oled.status_bar("T-REX  GAME", "ESP32")

    # Dino and tree preview in the middle
    oled.blit(dino_a, 50, 26)
    oled.blit(tree,   68, 26)
    oled.hline(0, 36, 128)         # mini ground line under icons

    # High score (only show if player has scored before)
    if state["hi"] > 0:
        oled.center_text("BEST: {}".format(state["hi"]), 40)

    # Instruction at bottom with a pulsing bar underneath
    oled.center_text("Press JUMP to Start", 50)
    oled.h_bar(10, 60, 108, 3, 1.0, border=False)   # solid bar decoration

    oled.show()
    wait_press()


# ============================================================
#  SECTION 12 — GAME OVER SCREEN
#  Uses: invert(), fill_round_rect(), fill_rect(),
#        center_text(), h_bar(), show()
#  Flashes screen, shows scores, waits for retry press.
# ============================================================

def show_game_over(oled):
    """
    Display game-over screen with flash effect.
    Waits for button press, then resets game state.
    Pass the OLED object from main.py.
    """
    # Flash effect using oled.invert()
    for _ in range(4):
        oled.invert(True);  time.sleep_ms(80)
        oled.invert(False); time.sleep_ms(80)

    # Draw game-over card using your library's round rect
    oled.clear()
    oled.fill_round_rect(16, 10, 96, 44, 5)         # white card background
    oled.fill_rect(18, 12, 92, 40, 0)               # black card interior

    oled.center_text("GAME  OVER",  17)

    # Score row
    sc_str = "SC:{}".format(state["score"])
    hi_str = "HI:{}".format(state["hi"])
    oled.center_text("{} {}".format(sc_str, hi_str), 28)

    # New record banner
    if state["score"] >= state["hi"] and state["score"] > 0:
        oled.center_text("** NEW RECORD **", 39)
    else:
        oled.center_text("JUMP = Retry", 39)

    # Thin progress bar at very bottom as decoration
    oled.h_bar(10, 56, 108, 4,
               state["score"] / max(state["hi"], 1),
               border=True)

    oled.show()
    time.sleep_ms(600)     # prevent instant button re-read
    wait_press()
    reset_game()           # ready for next round

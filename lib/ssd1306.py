# =============================================================
#  ssd1306.py  —  Full-featured SSD1306 OLED driver for ESP32
#  Resolution : 128 × 64  (or 128 × 32)
#  Interface  : I2C  (pass any machine.I2C object)
#  MicroPython: v1.19+
# =============================================================
#
#  HOW THE OLED WORKS
#  ───────────────────
#  The SSD1306 chip drives a 128×64 grid of pixels.
#  Pixels live in a "framebuffer" — a bytearray in RAM.
#  In MONO_VLSB format each BYTE holds 8 vertical pixels
#  in one column (bit-0 = top pixel of that group of 8).
#  Nothing changes on-screen until show() is called.
#
#  Coordinate system:
#    (0,0)   = top-left
#    (127,0) = top-right
#    (0,63)  = bottom-left
#
#  I2C framing:
#    Control byte 0x00 → following bytes are COMMANDS
#    Control byte 0x40 → following bytes are PIXEL DATA
#
# =============================================================
#
#  NEW in this version vs original:
#  ─────────────────────────────────
#  • Supports 128×32 OLEDs (pass height=32)
#  • rotate() — flip display 180°
#  • partial_show() — update only a page band (faster refresh)
#  • pixel(), hline(), vline()
#  • circle(), fill_circle()
#  • ellipse() with firmware-version fallback
#  • triangle(), fill_triangle()
#  • round_rect(), fill_round_rect()
#  • arc()
#  • fill_rect() now first-class (was inside rect)
#  • text_bg() — text with solid background
#  • center_text(), right_text()
#  • wrap_text() — auto word-wrap
#  • scroll_text() — animated vertical scroll
#  • draw_bitmap() — 1-bit sprite blit
#  • h_bar(), v_bar() — progress bars
#  • draw_graph()  — line chart from sample list
#  • draw_bar_chart() — vertical bar chart
#  • draw_battery() — battery icon
#  • draw_signal()  — signal-strength bars
#  • status_bar()   — header bar (updated signature)
#  • notification() — sender + body card
#  • splash()       — centered title + subtitle
#  • draw_menu()    — scrollable highlighted menu
#  • page_dots()    — pagination dots
#  • marquee()      — per-frame horizontal scroll helper
#  • print_line()   — single-line quick-write
# =============================================================

import framebuf
import math
import time

# ── Command byte constants ────────────────────────────────────
_SET_CONTRAST        = 0x81
_SET_ENTIRE_ON       = 0xA4
_SET_NORM_INV        = 0xA6
_SET_DISP_OFF        = 0xAE
_SET_DISP_ON         = 0xAF
_SET_MEM_ADDR        = 0x20
_SET_COL_ADDR        = 0x21
_SET_PAGE_ADDR       = 0x22
_SET_DISP_START_LINE = 0x40
_SET_SEG_REMAP       = 0xA0
_SET_MUX_RATIO       = 0xA8
_SET_COM_OUT_DIR     = 0xC0
_SET_DISP_OFFSET     = 0xD3
_SET_COM_PIN_CFG     = 0xDA
_SET_DISP_CLK_DIV    = 0xD5
_SET_PRECHARGE       = 0xD9
_SET_VCOM_DESEL      = 0xDB
_SET_CHARGE_PUMP     = 0x8D


class SSD1306:
    """
    Full-featured SSD1306 I2C OLED driver.

    Parameters
    ----------
    i2c    : machine.I2C object (already constructed)
    addr   : I2C address, default 0x3C  (some modules use 0x3D)
    width  : display width  in pixels   (default 128)
    height : display height in pixels   (default 64; use 32 for 128×32 OLEDs)

    Quick-start
    -----------
        from machine import I2C, Pin
        from ssd1306 import SSD1306

        bus  = I2C(0, scl=Pin(22), sda=Pin(21), freq=400_000)
        oled = SSD1306(bus)

        oled.fill(0)
        oled.text("Hello!", 0, 0)
        oled.show()
    """

    def __init__(self, i2c, addr=0x3C, width=128, height=64):
        self._i2c   = i2c
        self._addr  = addr
        self.width  = width
        self.height = height
        self.pages  = height // 8

        self._buf = bytearray(width * height // 8)
        self._fb  = framebuf.FrameBuffer(self._buf, width, height, framebuf.MONO_VLSB)

        self._contrast = 0x7F
        self._inverted = False

        self._init_display()
        self.fill(0)
        self.show()

    # ═══════════════════════════════════════════════════════════
    #  LOW-LEVEL I2C
    # ═══════════════════════════════════════════════════════════

    def _write(self, buf):
        """Write raw bytes to the I2C bus."""
        self._i2c.writeto(self._addr, buf)

    def _cmd(self, *cmds):
        """Send one or more command bytes."""
        for c in cmds:
            self._write(bytes([0x80, c]))

    def _data(self, buf):
        """Send pixel data bytes in chunks."""
        chunk  = 16
        prefix = bytes([0x40])
        for i in range(0, len(buf), chunk):
            self._write(prefix + bytes(buf[i:i + chunk]))

    # ═══════════════════════════════════════════════════════════
    #  INITIALISATION
    # ═══════════════════════════════════════════════════════════

    def _init_display(self):
        """Send full SSD1306 init sequence from datasheet."""
        com_pin = 0x02 if self.height == 32 else 0x12
        for c in (
            _SET_DISP_OFF,
            _SET_MEM_ADDR,        0x00,
            _SET_DISP_START_LINE | 0x00,
            _SET_SEG_REMAP       | 0x01,
            _SET_MUX_RATIO,       self.height - 1,
            _SET_COM_OUT_DIR     | 0x08,
            _SET_DISP_OFFSET,     0x00,
            _SET_COM_PIN_CFG,     com_pin,
            _SET_DISP_CLK_DIV,    0x80,
            _SET_PRECHARGE,       0xF1,
            _SET_VCOM_DESEL,      0x30,
            _SET_CONTRAST,        self._contrast,
            _SET_ENTIRE_ON,
            _SET_NORM_INV,
            _SET_CHARGE_PUMP,     0x14,
            _SET_DISP_ON,
        ):
            self._cmd(c)

    # ═══════════════════════════════════════════════════════════
    #  DISPLAY CONTROL
    # ═══════════════════════════════════════════════════════════

    def show(self):
        """
        Push the entire framebuffer to the display.
        Nothing appears on-screen until this is called.
        """
        self._cmd(_SET_COL_ADDR,  0, self.width  - 1)
        self._cmd(_SET_PAGE_ADDR, 0, self.pages  - 1)
        self._data(self._buf)

    def partial_show(self, y_start=0, y_end=None):
        """
        Push only a horizontal band of pages to the display.
        Faster than show() when only a portion of the screen changes.

        Parameters
        ----------
        y_start : top pixel row (rounded down to nearest page boundary)
        y_end   : bottom pixel row (inclusive), defaults to screen bottom
        """
        if y_end is None:
            y_end = self.height - 1
        p0 = y_start // 8
        p1 = y_end   // 8
        self._cmd(_SET_COL_ADDR,  0, self.width - 1)
        self._cmd(_SET_PAGE_ADDR, p0, p1)
        b0 = p0 * self.width
        b1 = (p1 + 1) * self.width
        self._data(self._buf[b0:b1])

    def fill(self, color=0):
        """
        Fill the entire framebuffer.
        color = 0 → black (all pixels off)
        color = 1 → white (all pixels on)
        """
        self._fb.fill(color)

    def clear(self, show=False):
        """
        Clear the screen to black.
        Pass show=True to immediately push to hardware.
        """
        self._fb.fill(0)
        if show:
            self.show()

    def contrast(self, level):
        """
        Set display brightness.
        level : 0 (dimmest) … 255 (brightest)
        """
        level = max(0, min(255, int(level)))
        self._contrast = level
        self._cmd(_SET_CONTRAST, level)

    def invert(self, on=True):
        """Invert all pixels on hardware (framebuffer unchanged)."""
        self._inverted = on
        self._cmd(_SET_NORM_INV | (1 if on else 0))

    def power(self, on=True):
        """Turn display on or off. Content stays in framebuffer RAM."""
        self._cmd(_SET_DISP_ON if on else _SET_DISP_OFF)

    def rotate(self, flipped=True):
        """
        Rotate the display 180° (useful for upside-down mounting).
        flipped=True  → rotated 180°
        flipped=False → normal orientation
        """
        if flipped:
            self._cmd(_SET_SEG_REMAP | 0x00)
            self._cmd(_SET_COM_OUT_DIR | 0x00)
        else:
            self._cmd(_SET_SEG_REMAP | 0x01)
            self._cmd(_SET_COM_OUT_DIR | 0x08)

    # ═══════════════════════════════════════════════════════════
    #  BASIC DRAWING
    # ═══════════════════════════════════════════════════════════

    def pixel(self, x, y, color=1):
        """Set a single pixel."""
        self._fb.pixel(x, y, color)

    def hline(self, x, y, w, color=1):
        """Draw a horizontal line."""
        self._fb.hline(x, y, w, color)

    def vline(self, x, y, h, color=1):
        """Draw a vertical line."""
        self._fb.vline(x, y, h, color)

    def line(self, x0, y0, x1, y1, color=1):
        """Draw a line between two points."""
        self._fb.line(x0, y0, x1, y1, color)

    def rect(self, x, y, w, h, color=1, fill=False):
        """Draw a rectangle. fill=True fills it solid."""
        if fill:
            self._fb.fill_rect(x, y, w, h, color)
        else:
            self._fb.rect(x, y, w, h, color)

    def fill_rect(self, x, y, w, h, color=1):
        """Draw a filled rectangle (explicit convenience method)."""
        self._fb.fill_rect(x, y, w, h, color)

    def round_rect(self, x, y, w, h, r=4, color=1):
        """Draw a rectangle with rounded corners. r = corner radius."""
        r = min(r, w // 2, h // 2)
        self._fb.hline(x + r, y,         w - 2 * r, color)
        self._fb.hline(x + r, y + h - 1, w - 2 * r, color)
        self._fb.vline(x,         y + r, h - 2 * r, color)
        self._fb.vline(x + w - 1, y + r, h - 2 * r, color)
        for dx in range(r + 1):
            dy = int(math.sqrt(r * r - dx * dx))
            self._fb.pixel(x + r - dx,          y + r - dy,          color)
            self._fb.pixel(x + w - r - 1 + dx,  y + r - dy,          color)
            self._fb.pixel(x + r - dx,          y + h - r - 1 + dy,  color)
            self._fb.pixel(x + w - r - 1 + dx,  y + h - r - 1 + dy,  color)

    def fill_round_rect(self, x, y, w, h, r=4, color=1):
        """Draw a filled rectangle with rounded corners."""
        r = min(r, w // 2, h // 2)
        self._fb.fill_rect(x + r, y,         w - 2 * r, h,          color)
        self._fb.fill_rect(x,     y + r,     r,          h - 2 * r,  color)
        self._fb.fill_rect(x + w - r, y + r, r,          h - 2 * r,  color)
        for dx in range(r + 1):
            dy = int(math.sqrt(r * r - dx * dx))
            self._fb.vline(x + r - dx,         y + r - dy, dy * 2 + h - 2 * r, color)
            self._fb.vline(x + w - r - 1 + dx, y + r - dy, dy * 2 + h - 2 * r, color)

    def circle(self, cx, cy, r, color=1):
        """Draw a circle outline (Bresenham)."""
        x, y, d = r, 0, 1 - r
        while x >= y:
            for px, py in [(cx+x,cy+y),(cx-x,cy+y),(cx+x,cy-y),(cx-x,cy-y),
                           (cx+y,cy+x),(cx-y,cy+x),(cx+y,cy-x),(cx-y,cy-x)]:
                self._fb.pixel(px, py, color)
            y += 1
            d  = d + 2 * y + 1 if d < 0 else d + 2 * (y - x + 1)
            if d >= 0:
                x -= 1

    def fill_circle(self, cx, cy, r, color=1):
        """Draw a filled circle."""
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self._fb.hline(cx - dx, cy + dy, 2 * dx + 1, color)

    def ellipse(self, cx, cy, rx, ry, color=1):
        """Draw an ellipse outline."""
        try:
            self._fb.ellipse(cx, cy, rx, ry, color)
        except AttributeError:
            steps = max(rx, ry) * 4
            for i in range(steps):
                a = 2 * math.pi * i / steps
                self._fb.pixel(int(cx + rx * math.cos(a)), int(cy + ry * math.sin(a)), color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color=1):
        """Draw a triangle outline."""
        self._fb.line(x0, y0, x1, y1, color)
        self._fb.line(x1, y1, x2, y2, color)
        self._fb.line(x2, y2, x0, y0, color)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, color=1):
        """Draw a filled triangle (scan-line algorithm)."""
        pts = sorted([(x0,y0),(x1,y1),(x2,y2)], key=lambda p: p[1])
        (ax,ay),(bx,by),(cx,cy) = pts

        def lerp(ya, yb, xa, xb, y):
            return xa if yb == ya else xa + (xb - xa) * (y - ya) // (yb - ya)

        for y in range(ay, cy + 1):
            xa = lerp(ay, cy, ax, cx, y)
            xb = lerp(ay, by, ax, bx, y) if y < by else lerp(by, cy, bx, cx, y)
            if xa > xb:
                xa, xb = xb, xa
            self._fb.hline(xa, y, xb - xa + 1, color)

    def arc(self, cx, cy, r, start_deg, end_deg, color=1):
        """
        Draw an arc. 0° = top (12 o'clock), angles increase clockwise.

        Parameters
        ----------
        start_deg : start angle in degrees
        end_deg   : end   angle in degrees
        """
        steps = max(16, r * 2)
        for i in range(steps + 1):
            t = i / steps
            a = math.radians(start_deg + t * (end_deg - start_deg) - 90)
            self._fb.pixel(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), color)

    # ═══════════════════════════════════════════════════════════
    #  TEXT
    # ═══════════════════════════════════════════════════════════

    def text(self, string, x, y, color=1):
        """
        Write text at pixel position (x, y).
        Built-in 8×8 font; ASCII only.
        16 chars per row at x=0 (128/8=16).
        """
        self._fb.text(str(string), x, y, color)

    def text_bg(self, string, x, y, fg=1, bg=0):
        """Draw text with a solid background fill."""
        self._fb.fill_rect(x, y, len(string) * 8, 8, bg)
        self._fb.text(string, x, y, fg)

    def center_text(self, string, y, color=1):
        """Draw text horizontally centered."""
        x = max(0, (self.width - len(string) * 8) // 2)
        self._fb.text(string, x, y, color)

    def right_text(self, string, y, color=1, margin=0):
        """Draw text right-aligned."""
        x = self.width - len(string) * 8 - margin
        self._fb.text(string, max(0, x), y, color)

    def wrap_text(self, msg, x, y, max_width=None, color=1, line_spacing=10):
        """
        Draw text with automatic word-wrap.

        Parameters
        ----------
        msg         : string to render
        x, y        : top-left starting position
        max_width   : pixel width (defaults to display width − x)
        line_spacing: vertical gap between lines in pixels

        Returns
        -------
        y coordinate after the last rendered line
        """
        if max_width is None:
            max_width = self.width - x
        max_chars = max_width // 8
        words     = msg.split()
        line      = ""
        cy        = y
        for word in words:
            test = (line + " " + word).strip()
            if len(test) <= max_chars:
                line = test
            else:
                if line:
                    self._fb.text(line, x, cy, color)
                    cy += line_spacing
                line = word
        if line:
            self._fb.text(line, x, cy, color)
            cy += line_spacing
        return cy

    def scroll_text(self, lines, delay_ms=40, repeat=1):
        """
        Animate a list of text lines scrolling upward.

        Parameters
        ----------
        lines    : list of strings
        delay_ms : delay per pixel row
        repeat   : number of full scrolls (0 = loop forever)
        """
        all_lines = lines + [""] * (self.height // 8)
        total_h   = len(all_lines) * 8
        offset    = 0
        count     = 0
        while repeat == 0 or count < repeat:
            self._fb.fill(0)
            for i, ln in enumerate(all_lines):
                ty = i * 8 - offset
                if -8 < ty < self.height:
                    self._fb.text(ln, 0, ty, 1)
            self.show()
            time.sleep_ms(delay_ms)
            offset += 1
            if offset >= total_h:
                offset = 0
                count += 1

    # ═══════════════════════════════════════════════════════════
    #  BITMAP / SPRITE
    # ═══════════════════════════════════════════════════════════

    def draw_bitmap(self, data, x, y, w, h, color=1):
        """
        Draw a 1-bit MONO_HLSB bitmap at (x, y).

        Parameters
        ----------
        data  : bytearray — rows of bits, MSB first (MONO_HLSB)
        x, y  : top-left destination
        w, h  : width and height of bitmap in pixels
        color : 1 = normal, 0 = inverted

        Example
        -------
            HEART = bytearray([
                0b00110011,0b00000000,
                0b01111111,0b10000000,
                0b11111111,0b11000000,
                0b01111111,0b10000000,
                0b00111111,0b00000000,
                0b00011110,0b00000000,
                0b00001100,0b00000000,
                0b00000000,0b00000000,
            ])
            oled.draw_bitmap(HEART, 56, 28, 16, 8)
        """
        icon_fb = framebuf.FrameBuffer(bytearray(data), w, h, framebuf.MONO_HLSB)
        self._fb.blit(icon_fb, x, y, 0 if color else 1)

    def blit(self, src_fb, x, y, key=-1):
        """Blit a FrameBuffer object onto this display."""
        self._fb.blit(src_fb, x, y, key)

    def scroll(self, dx, dy):
        """Scroll framebuffer by (dx, dy) pixels."""
        self._fb.scroll(dx, dy)

    # ═══════════════════════════════════════════════════════════
    #  GAUGES & BARS
    # ═══════════════════════════════════════════════════════════

    def h_bar(self, x, y, w, h, pct, color=1, border=True):
        """
        Horizontal progress bar.

        Parameters
        ----------
        pct : fill ratio 0.0 … 1.0
        """
        pct = max(0.0, min(1.0, pct))
        if border:
            self._fb.rect(x, y, w, h, color)
            fw = max(0, int((w - 2) * pct))
            self._fb.fill_rect(x + 1, y + 1, fw, h - 2, color)
        else:
            fw = max(0, int(w * pct))
            self._fb.fill_rect(x, y, fw, h, color)

    def v_bar(self, x, y, w, h, pct, color=1, border=True):
        """
        Vertical progress bar (fills bottom-up).

        Parameters
        ----------
        pct : fill ratio 0.0 … 1.0
        """
        pct = max(0.0, min(1.0, pct))
        if border:
            self._fb.rect(x, y, w, h, color)
            fh = max(0, int((h - 2) * pct))
            self._fb.fill_rect(x + 1, y + h - 1 - fh, w - 2, fh, color)
        else:
            fh = max(0, int(h * pct))
            self._fb.fill_rect(x, y + h - fh, w, fh, color)

    def draw_battery(self, x, y, pct, w=24, h=12):
        """
        Draw a battery icon showing charge level.

        Parameters
        ----------
        x, y : top-left of battery body
        pct  : 0.0 (empty) … 1.0 (full)
        w, h : body dimensions (a 3px terminal nub is added to the right)
        """
        pct = max(0.0, min(1.0, pct))
        self._fb.rect(x, y, w, h, 1)
        nub_h = max(2, h // 3)
        self._fb.fill_rect(x + w, y + (h - nub_h) // 2, 3, nub_h, 1)
        fill_w = max(0, int((w - 4) * pct))
        self._fb.fill_rect(x + 2, y + 2, fill_w, h - 4, 1)
        if pct < 0.20:
            # Low: clear interior and draw cross
            self._fb.fill_rect(x + 2, y + 2, w - 4, h - 4, 0)
            self._fb.line(x + 4, y + 3, x + w - 4, y + h - 3, 1)
            self._fb.line(x + w - 4, y + 3, x + 4, y + h - 3, 1)

    def draw_signal(self, x, y, level, bars=4, bar_w=4, gap=2):
        """
        Draw a signal-strength / WiFi icon.

        Parameters
        ----------
        x, y  : bottom-left anchor
        level : filled bars (0 … bars)
        bars  : total number of bars
        bar_w : width of each bar in pixels
        gap   : gap between bars in pixels
        """
        max_h = bars * 3
        for i in range(bars):
            bh = (i + 1) * (max_h // bars)
            bx = x + i * (bar_w + gap)
            by = y - bh
            if i < level:
                self._fb.fill_rect(bx, by, bar_w, bh, 1)
            else:
                self._fb.rect(bx, by, bar_w, bh, 1)

    # ═══════════════════════════════════════════════════════════
    #  GRAPH / CHART
    # ═══════════════════════════════════════════════════════════

    def draw_graph(self, samples, x=0, y=14, w=None, h=48,
                   vmin=0, vmax=100, color=1, axes=True):
        """
        Draw a line chart from a list of samples.

        Parameters
        ----------
        samples : list of numeric values
        x, y    : top-left of the chart area
        w, h    : chart width and height in pixels
        vmin    : value mapped to chart bottom
        vmax    : value mapped to chart top
        axes    : draw top and bottom border lines
        """
        if w is None:
            w = self.width - x
        if not samples:
            return
        if axes:
            self._fb.hline(x, y,         w, color)
            self._fb.hline(x, y + h - 1, w, color)
        n    = len(samples)
        span = vmax - vmin if vmax != vmin else 1

        def sy(v):
            return y + h - 1 - int((v - vmin) / span * (h - 1))

        px0, py0 = x, sy(samples[0])
        for i in range(1, n):
            px1 = x + int(i * (w - 1) / max(n - 1, 1))
            py1 = sy(samples[i])
            self._fb.line(px0, py0, px1, py1, color)
            px0, py0 = px1, py1

    def draw_bar_chart(self, values, x=0, y=14, w=None, h=48,
                       vmin=0, vmax=None, gap=1, color=1):
        """
        Draw a vertical bar chart.

        Parameters
        ----------
        values : list of numbers
        vmax   : auto-scaled if None
        gap    : pixel gap between bars
        """
        if w is None:
            w = self.width - x
        if not values:
            return
        if vmax is None:
            vmax = max(values)
        span  = vmax - vmin if vmax != vmin else 1
        n     = len(values)
        bar_w = max(1, (w - gap * (n - 1)) // n)
        for i, v in enumerate(values):
            bh = max(1, int((v - vmin) / span * h))
            bx = x + i * (bar_w + gap)
            self._fb.fill_rect(bx, y + h - bh, bar_w, bh, color)

    # ═══════════════════════════════════════════════════════════
    #  UI WIDGETS
    # ═══════════════════════════════════════════════════════════

    def status_bar(self, title, value="", bg=1, fg=0):
        """
        Draw a filled header bar at the top of the screen.

        Parameters
        ----------
        title : left text  (max ~10 chars)
        value : right text (max ~8 chars)
        bg    : bar background color (1 = white)
        fg    : text color on bar    (0 = black)
        """
        self._fb.fill_rect(0, 0, self.width, 11, bg)
        self._fb.text(title[:10], 2, 2, fg)
        if value:
            rx = self.width - len(value) * 8 - 2
            self._fb.text(value[:8], max(0, rx), 2, fg)

    def draw_status_bar(self, title, value=""):
        """
        Legacy convenience wrapper — fills screen black, draws header,
        then writes value below it.  Calls show() automatically.
        """
        self._fb.fill(0)
        self.status_bar(title, "")
        self._fb.text(value[:16], 0, 20, 1)
        self.show()

    def notification(self, sender, body, show_now=True):
        """
        Display a notification card: sender in header, body below with word-wrap.

        Parameters
        ----------
        sender   : sender label shown in the header bar
        body     : message body (auto word-wrapped)
        show_now : push to display immediately
        """
        self._fb.fill(0)
        self.status_bar(sender)
        self.wrap_text(body, 0, 14, line_spacing=11)
        if show_now:
            self.show()

    def splash(self, title, subtitle="", delay_ms=0):
        """
        Show a centered splash screen.

        Parameters
        ----------
        title    : main text
        subtitle : secondary text
        delay_ms : hold time in ms; 0 = return immediately
        """
        self._fb.fill(0)
        ty = 20 if subtitle else 28
        self.center_text(title, ty)
        if subtitle:
            self.center_text(subtitle, ty + 14)
        self.show()
        if delay_ms > 0:
            time.sleep_ms(delay_ms)

    def draw_menu(self, items, cursor=0, scroll_top=0, visible=4,
                  header=None, show_now=True):
        """
        Draw a scrollable menu with a highlighted selection.

        Parameters
        ----------
        items      : list of strings
        cursor     : selected index
        scroll_top : first visible index
        visible    : number of visible rows
        header     : optional header bar text

        Returns
        -------
        (cursor, scroll_top)
        """
        self._fb.fill(0)
        y_off = 0
        if header:
            self.status_bar(header)
            y_off = 13

        row_h = (self.height - y_off) // visible

        for i in range(visible):
            idx = scroll_top + i
            if idx >= len(items):
                break
            ry = y_off + i * row_h
            if idx == cursor:
                self._fb.fill_rect(0, ry, self.width, row_h, 1)
                self._fb.text(items[idx][:16], 2, ry + (row_h - 8) // 2, 0)
            else:
                self._fb.text(items[idx][:16], 2, ry + (row_h - 8) // 2, 1)

        # Scrollbar
        if len(items) > visible:
            sb_h = max(4, self.height * visible // len(items))
            sb_y = y_off + (self.height - y_off - sb_h) * scroll_top // max(1, len(items) - visible)
            self._fb.fill_rect(self.width - 3, y_off, 2, self.height - y_off, 0)
            self._fb.fill_rect(self.width - 3, sb_y,  2, sb_h, 1)

        if show_now:
            self.show()
        return cursor, scroll_top

    def page_dots(self, total, current, y=None, color=1):
        """
        Draw pagination indicator dots at the bottom of the screen.

        Parameters
        ----------
        total   : total page count
        current : current page index (0-based)
        y       : y position (defaults to last 6 rows)
        """
        if y is None:
            y = self.height - 6
        dot_w  = 5
        gap    = 3
        total_w = total * dot_w + (total - 1) * gap
        sx      = (self.width - total_w) // 2
        for i in range(total):
            dx = sx + i * (dot_w + gap)
            if i == current:
                self._fb.fill_rect(dx, y, dot_w, dot_w, color)
            else:
                self._fb.rect(dx, y, dot_w, dot_w, color)

    def marquee(self, msg, offset, y=0, color=1):
        """
        Render one frame of a right-to-left scrolling marquee.
        Call in a loop, incrementing the returned offset each frame.

        Returns
        -------
        New offset (auto-resets when text scrolls fully off-screen)

        Example
        -------
            off = 0
            while True:
                oled.fill(0)
                off = oled.marquee("Hello scrolling world!  ", off)
                oled.show()
                time.sleep_ms(30)
        """
        self._fb.text(msg, self.width - offset, y, color)
        offset += 2
        if offset > len(msg) * 8 + self.width:
            offset = 0
        return offset

    # ═══════════════════════════════════════════════════════════
    #  CONVENIENCE
    # ═══════════════════════════════════════════════════════════

    def print_line(self, msg, line=0, clear_first=False, color=1):
        """
        Write a string to a specific text row (0–7) and push to display.

        Parameters
        ----------
        line        : row 0 … 7  (row height = 8 px)
        clear_first : clear screen before writing
        """
        if clear_first:
            self._fb.fill(0)
        self._fb.text(str(msg)[:16], 0, line * 8, color)
        self.show()

    def __repr__(self):
        return "SSD1306({}×{} @ I2C 0x{:02X})".format(self.width, self.height, self._addr)

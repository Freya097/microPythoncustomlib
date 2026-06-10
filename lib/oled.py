# =============================================================
#  oled.py  —  Full-featured SSD1306 OLED driver for ESP32
#  Resolution : 128 × 64 pixels  (also supports 128 × 32)
#  Interface  : I2C  (default SCL=22, SDA=21, addr=0x3C)
#  MicroPython: v1.19+
# =============================================================
#
#  NEW in this version vs original:
#  ─────────────────────────────────
#  • Configurable width / height (128×32 support)
#  • contrast(), power(), invert() hardware controls
#  • fill_rect(), pixel(), ellipse(), circle(), triangle()
#  • hline(), vline()
#  • center_text(), right_text(), text_color() with bg support
#  • wrap_text()   — automatic word-wrap
#  • scroll_text() — animated vertical scroll
#  • draw_bitmap() — 1-bit sprite / icon blit
#  • h_bar(), v_bar() — progress / gauge bars
#  • draw_graph()  — live waveform / line chart
#  • draw_menu()   — highlighted scrollable menu
#  • notification()— header + body message card
#  • status_bar()  — header bar with title & value
#  • splash()      — centered title + subtitle splash
#  • draw_battery()— battery icon with fill level
#  • draw_signal() — WiFi / signal strength bars
#  • marquee()     — one-shot horizontal marquee step
#  • page_dots()   — pagination indicator
#  • partial_show()— update only a horizontal band (faster)
#  • show() fixed  — proper page-address setup before data
# =============================================================

from machine import I2C, Pin
import framebuf
import time
import math


# ── SSD1306 command constants ─────────────────────────────────
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


class OLED:
    """
    Full-featured SSD1306 I2C OLED driver.

    Parameters
    ----------
    scl    : GPIO pin number for I2C clock
    sda    : GPIO pin number for I2C data
    addr   : I2C address (0x3C default, some boards use 0x3D)
    width  : display width  in pixels (default 128)
    height : display height in pixels (default 64, use 32 for 128×32 OLEDs)
    i2c_id : I2C peripheral index (0 or 1, default 0)
    freq   : I2C bus frequency in Hz (default 400_000)

    Quick-start
    -----------
        from oled import OLED
        oled = OLED(scl=22, sda=21)
        oled.clear()
        oled.text("Hello!", 0, 0)
        oled.show()
    """

    def __init__(self, scl=22, sda=21, addr=0x3C,
                 width=128, height=64, i2c_id=0, freq=400_000):

        self.width  = width
        self.height = height
        self.addr   = addr
        self.pages  = height // 8

        self.i2c = I2C(i2c_id, scl=Pin(scl), sda=Pin(sda), freq=freq)

        self.buf = bytearray(width * height // 8)
        self.fb  = framebuf.FrameBuffer(self.buf, width, height, framebuf.MONO_VLSB)

        self._contrast  = 0x7F
        self._inverted  = False
        self._powered   = True

        self._init_display()
        self.clear()
        self.show()

    # ═══════════════════════════════════════════════════════════
    #  LOW-LEVEL I2C
    # ═══════════════════════════════════════════════════════════

    def _cmd(self, cmd):
        """Send a single command byte."""
        self.i2c.writeto(self.addr, bytearray([0x80, cmd]))

    def _cmds(self, *cmds):
        """Send multiple command bytes in one call."""
        for c in cmds:
            self._cmd(c)

    def _write_data(self, data):
        """Send pixel data bytes (prefixed with 0x40 control byte)."""
        self.i2c.writeto(self.addr, bytearray([0x40]) + data)

    # ═══════════════════════════════════════════════════════════
    #  INITIALISATION
    # ═══════════════════════════════════════════════════════════

    def _init_display(self):
        """Send full SSD1306 initialisation sequence."""
        com_pin_cfg = 0x02 if self.height == 32 else 0x12
        mux_ratio   = self.height - 1

        for cmd in (
            _SET_DISP_OFF,
            _SET_MEM_ADDR,   0x00,           # Horizontal addressing mode
            _SET_DISP_START_LINE | 0x00,     # Start line = 0
            _SET_SEG_REMAP   | 0x01,         # Segment remap (flip H)
            _SET_MUX_RATIO,  mux_ratio,      # MUX ratio
            _SET_COM_OUT_DIR | 0x08,         # COM scan direction (flip V)
            _SET_DISP_OFFSET, 0x00,          # Display offset = 0
            _SET_COM_PIN_CFG, com_pin_cfg,   # COM pin config
            _SET_DISP_CLK_DIV, 0x80,         # Clock div ratio
            _SET_PRECHARGE,  0xF1,           # Pre-charge period
            _SET_VCOM_DESEL, 0x30,           # VCOMH deselect level
            _SET_CONTRAST,   self._contrast, # Contrast
            _SET_ENTIRE_ON,                  # Output follows RAM
            _SET_NORM_INV,                   # Normal (non-inverted)
            _SET_CHARGE_PUMP, 0x14,          # Charge pump ON
            _SET_DISP_ON,                    # Display ON
        ):
            self._cmd(cmd)

    # ═══════════════════════════════════════════════════════════
    #  DISPLAY CONTROL
    # ═══════════════════════════════════════════════════════════

    def show(self):
        """
        Push the entire framebuffer to the display.
        Nothing appears on-screen until this is called.
        """
        self._cmds(_SET_COL_ADDR,  0, self.width  - 1)
        self._cmds(_SET_PAGE_ADDR, 0, self.pages  - 1)
        chunk = 16
        for i in range(0, len(self.buf), chunk):
            self._write_data(self.buf[i:i + chunk])

    def partial_show(self, y_start=0, y_end=None):
        """
        Push only a horizontal band of pages to the display.
        Faster than full show() when only part of screen changes.

        Parameters
        ----------
        y_start : top pixel row of the region (rounded down to page boundary)
        y_end   : bottom pixel row (inclusive), defaults to screen bottom
        """
        if y_end is None:
            y_end = self.height - 1
        page_start = y_start // 8
        page_end   = y_end   // 8
        self._cmds(_SET_COL_ADDR,  0, self.width - 1)
        self._cmds(_SET_PAGE_ADDR, page_start, page_end)
        byte_start = page_start * self.width
        byte_end   = (page_end + 1) * self.width
        chunk = 16
        for i in range(byte_start, byte_end, chunk):
            self._write_data(self.buf[i:i + chunk])

    def clear(self, color=0):
        """Fill framebuffer with color (0=black, 1=white). Does NOT call show()."""
        self.fb.fill(color)

    def fill(self, color=0):
        """Alias for clear()."""
        self.fb.fill(color)

    def contrast(self, level):
        """
        Set display brightness.
        level : 0 (dimmest) … 255 (brightest)
        """
        level = max(0, min(255, int(level)))
        self._contrast = level
        self._cmds(_SET_CONTRAST, level)

    def invert(self, on=True):
        """Invert all pixels on hardware (no framebuffer change)."""
        self._inverted = on
        self._cmd(_SET_NORM_INV | (1 if on else 0))

    def power(self, on=True):
        """Turn display on or off. Content stays in RAM."""
        self._powered = on
        self._cmd(_SET_DISP_ON if on else _SET_DISP_OFF)

    def rotate(self, flipped=True):
        """
        Rotate display 180°.
        flipped=True  → upside-down mount
        flipped=False → normal orientation
        """
        if flipped:
            self._cmds(_SET_SEG_REMAP | 0x00, _SET_COM_OUT_DIR | 0x00)
        else:
            self._cmds(_SET_SEG_REMAP | 0x01, _SET_COM_OUT_DIR | 0x08)

    # ═══════════════════════════════════════════════════════════
    #  BASIC DRAWING PRIMITIVES
    # ═══════════════════════════════════════════════════════════

    def pixel(self, x, y, color=1):
        """Draw a single pixel."""
        self.fb.pixel(x, y, color)

    def hline(self, x, y, w, color=1):
        """Draw a horizontal line."""
        self.fb.hline(x, y, w, color)

    def vline(self, x, y, h, color=1):
        """Draw a vertical line."""
        self.fb.vline(x, y, h, color)

    def line(self, x1, y1, x2, y2, color=1):
        """Draw a line between two points."""
        self.fb.line(x1, y1, x2, y2, color)

    def rect(self, x, y, w, h, color=1):
        """Draw a rectangle outline."""
        self.fb.rect(x, y, w, h, color)

    def fill_rect(self, x, y, w, h, color=1):
        """Draw a filled rectangle."""
        self.fb.fill_rect(x, y, w, h, color)

    def round_rect(self, x, y, w, h, r=4, color=1):
        """
        Draw a rectangle with rounded corners.
        r : corner radius in pixels (max = min(w,h)//2)
        """
        r = min(r, w // 2, h // 2)
        # Sides
        self.fb.hline(x + r, y,         w - 2 * r, color)
        self.fb.hline(x + r, y + h - 1, w - 2 * r, color)
        self.fb.vline(x,         y + r, h - 2 * r, color)
        self.fb.vline(x + w - 1, y + r, h - 2 * r, color)
        # Corners using Bresenham circle quadrants
        for dx in range(r + 1):
            dy = int(math.sqrt(r * r - dx * dx))
            self.fb.pixel(x + r - dx,         y + r - dy,         color)
            self.fb.pixel(x + w - r - 1 + dx, y + r - dy,         color)
            self.fb.pixel(x + r - dx,         y + h - r - 1 + dy, color)
            self.fb.pixel(x + w - r - 1 + dx, y + h - r - 1 + dy, color)

    def fill_round_rect(self, x, y, w, h, r=4, color=1):
        """Draw a filled rectangle with rounded corners."""
        r = min(r, w // 2, h // 2)
        self.fb.fill_rect(x + r, y,     w - 2 * r, h,     color)
        self.fb.fill_rect(x,     y + r, r,         h - 2*r, color)
        self.fb.fill_rect(x + w - r, y + r, r,    h - 2*r, color)
        for dx in range(r + 1):
            dy = int(math.sqrt(r * r - dx * dx))
            self.fb.vline(x + r - dx,          y + r - dy, dy * 2 + (h - 2*r), color)
            self.fb.vline(x + w - r - 1 + dx,  y + r - dy, dy * 2 + (h - 2*r), color)

    def circle(self, cx, cy, r, color=1):
        """Draw a circle outline using Bresenham's algorithm."""
        x, y, d = r, 0, 1 - r
        while x >= y:
            for pts in [(cx+x, cy+y),(cx-x, cy+y),(cx+x, cy-y),(cx-x, cy-y),
                        (cx+y, cy+x),(cx-y, cy+x),(cx+y, cy-x),(cx-y, cy-x)]:
                self.fb.pixel(pts[0], pts[1], color)
            y += 1
            if d < 0:
                d += 2 * y + 1
            else:
                x -= 1
                d += 2 * (y - x) + 1

    def fill_circle(self, cx, cy, r, color=1):
        """Draw a filled circle."""
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.fb.hline(cx - dx, cy + dy, 2 * dx + 1, color)

    def ellipse(self, cx, cy, rx, ry, color=1):
        """Draw an ellipse outline."""
        try:
            self.fb.ellipse(cx, cy, rx, ry, color)
        except AttributeError:
            # Fallback for older MicroPython without framebuf.ellipse
            steps = max(rx, ry) * 4
            for i in range(steps):
                angle = 2 * math.pi * i / steps
                x = int(cx + rx * math.cos(angle))
                y = int(cy + ry * math.sin(angle))
                self.fb.pixel(x, y, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color=1):
        """Draw a triangle outline."""
        self.fb.line(x0, y0, x1, y1, color)
        self.fb.line(x1, y1, x2, y2, color)
        self.fb.line(x2, y2, x0, y0, color)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, color=1):
        """Draw a filled triangle using scan-line fill."""
        # Sort vertices by y
        pts = sorted([(x0,y0),(x1,y1),(x2,y2)], key=lambda p: p[1])
        (ax,ay),(bx,by),(cx,cy) = pts

        def interp(ya, yb, xa, xb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) // (yb - ya)

        for y in range(ay, cy + 1):
            if y < by:
                xa = interp(ay, cy, ax, cx, y)
                xb = interp(ay, by, ax, bx, y)
            else:
                xa = interp(ay, cy, ax, cx, y)
                xb = interp(by, cy, bx, cx, y)
            if xa > xb:
                xa, xb = xb, xa
            self.fb.hline(xa, y, xb - xa + 1, color)

    def arc(self, cx, cy, r, start_deg, end_deg, color=1):
        """
        Draw an arc from start_deg to end_deg (clockwise, 0=top).
        Angles in degrees; 0° = 12-o'clock (top), clockwise.
        """
        steps = max(16, r * 2)
        for i in range(steps + 1):
            t     = i / steps
            angle = math.radians(start_deg + t * (end_deg - start_deg) - 90)
            x     = int(cx + r * math.cos(angle))
            y     = int(cy + r * math.sin(angle))
            self.fb.pixel(x, y, color)

    # ═══════════════════════════════════════════════════════════
    #  TEXT HELPERS
    # ═══════════════════════════════════════════════════════════

    def text(self, msg, x, y, color=1):
        """Draw text at (x, y). Font is 8×8 pixels."""
        self.fb.text(str(msg), x, y, color)

    def text_bg(self, msg, x, y, fg=1, bg=0):
        """Draw text with a solid background rectangle."""
        w = len(msg) * 8
        self.fb.fill_rect(x, y, w, 8, bg)
        self.fb.text(msg, x, y, fg)

    def center_text(self, msg, y, color=1):
        """Draw text horizontally centered on the display."""
        x = max(0, (self.width - len(msg) * 8) // 2)
        self.fb.text(msg, x, y, color)

    def right_text(self, msg, y, color=1, margin=0):
        """Draw text right-aligned."""
        x = self.width - len(msg) * 8 - margin
        self.fb.text(msg, max(0, x), y, color)

    def wrap_text(self, msg, x, y, max_width=None, color=1, line_spacing=10):
        """
        Draw text with automatic word-wrap.

        Parameters
        ----------
        msg         : string to display
        x, y        : top-left starting position
        max_width   : pixel width limit (default: display width - x)
        color       : pixel color
        line_spacing: pixels between lines (default 10)

        Returns
        -------
        y position after the last line
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
                    self.fb.text(line, x, cy, color)
                    cy += line_spacing
                line = word
        if line:
            self.fb.text(line, x, cy, color)
            cy += line_spacing
        return cy

    def scroll_text(self, lines, delay_ms=40, repeat=1):
        """
        Scroll a list of text lines vertically upward across the screen.

        Parameters
        ----------
        lines    : list of strings (each displayed as one 8px-tall row)
        delay_ms : milliseconds per pixel step
        repeat   : how many times to scroll through (0 = infinite)
        """
        all_text = lines + [""] * (self.height // 8)
        total_h  = len(all_text) * 8
        count    = 0
        offset   = 0

        while repeat == 0 or count < repeat:
            self.fb.fill(0)
            for i, line in enumerate(all_text):
                ty = i * 8 - offset
                if -8 < ty < self.height:
                    self.fb.text(line, 0, ty, 1)
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
        Draw a 1-bit bitmap at (x, y).

        Parameters
        ----------
        data  : bytearray in MONO_HLSB format (rows of bits, MSB first)
        x, y  : top-left position
        w, h  : width and height in pixels
        color : 1 = white, 0 = black (XOR-like: set pixel when bit=1)

        Example — 8×8 smiley face:
            SMILEY = bytearray([
                0b00111100,
                0b01000010,
                0b10100101,
                0b10000001,
                0b10100101,
                0b10011001,
                0b01000010,
                0b00111100,
            ])
            oled.draw_bitmap(SMILEY, 60, 28, 8, 8)
        """
        icon_buf = framebuf.FrameBuffer(bytearray(data), w, h, framebuf.MONO_HLSB)
        self.fb.blit(icon_buf, x, y, 0 if color else 1)

    def blit(self, src_fb, x, y, key=-1):
        """Blit a FrameBuffer object directly onto this display."""
        self.fb.blit(src_fb, x, y, key)

    # ═══════════════════════════════════════════════════════════
    #  GAUGES & BARS
    # ═══════════════════════════════════════════════════════════

    def h_bar(self, x, y, w, h, pct, color=1, border=True):
        """
        Horizontal progress / gauge bar.

        Parameters
        ----------
        x, y     : top-left corner
        w, h     : total bar size in pixels
        pct      : fill percentage  0.0 … 1.0
        color    : fill color
        border   : draw border rectangle (True/False)
        """
        if border:
            self.fb.rect(x, y, w, h, color)
            fill_w = max(0, int((w - 2) * max(0.0, min(1.0, pct))))
            self.fb.fill_rect(x + 1, y + 1, fill_w, h - 2, color)
        else:
            fill_w = max(0, int(w * max(0.0, min(1.0, pct))))
            self.fb.fill_rect(x, y, fill_w, h, color)

    def v_bar(self, x, y, w, h, pct, color=1, border=True):
        """
        Vertical progress / gauge bar (fills from bottom up).

        Parameters
        ----------
        x, y     : top-left corner of full bar area
        w, h     : total bar size in pixels
        pct      : fill percentage  0.0 … 1.0
        """
        if border:
            self.fb.rect(x, y, w, h, color)
            fill_h = max(0, int((h - 2) * max(0.0, min(1.0, pct))))
            self.fb.fill_rect(x + 1, y + h - 1 - fill_h, w - 2, fill_h, color)
        else:
            fill_h = max(0, int(h * max(0.0, min(1.0, pct))))
            self.fb.fill_rect(x, y + h - fill_h, w, fill_h, color)

    def draw_battery(self, x, y, pct, w=24, h=12):
        """
        Draw a battery icon with fill level.

        Parameters
        ----------
        x, y : top-left of the battery body
        pct  : charge level 0.0 … 1.0
        w, h : body dimensions (terminal nub adds 3px to the right)
        """
        # Body
        self.fb.rect(x, y, w, h, 1)
        # Terminal nub
        nub_h = max(2, h // 3)
        self.fb.fill_rect(x + w, y + (h - nub_h) // 2, 3, nub_h, 1)
        # Fill
        fill_w = max(0, int((w - 4) * max(0.0, min(1.0, pct))))
        self.fb.fill_rect(x + 2, y + 2, fill_w, h - 4, 1)
        # Low battery indicator (clear the fill and draw an X pattern)
        if pct < 0.20:
            self.fb.fill_rect(x + 2, y + 2, w - 4, h - 4, 0)
            self.fb.line(x + 4, y + 3, x + w - 4, y + h - 3, 1)
            self.fb.line(x + w - 4, y + 3, x + 4, y + h - 3, 1)

    def draw_signal(self, x, y, level, bars=4, bar_w=4, gap=2):
        """
        Draw a WiFi / signal strength bar chart icon.

        Parameters
        ----------
        x, y  : bottom-left origin
        level : signal level 0 … bars
        bars  : total number of bars (default 4)
        bar_w : width of each bar in pixels
        gap   : pixels between bars
        """
        max_h = bars * 3
        for i in range(bars):
            bh  = (i + 1) * (max_h // bars)
            bx  = x + i * (bar_w + gap)
            by  = y - bh
            if i < level:
                self.fb.fill_rect(bx, by, bar_w, bh, 1)
            else:
                self.fb.rect(bx, by, bar_w, bh, 1)

    # ═══════════════════════════════════════════════════════════
    #  GRAPH / WAVEFORM
    # ═══════════════════════════════════════════════════════════

    def draw_graph(self, samples, x=0, y=14, w=None, h=48,
                   vmin=0, vmax=100, color=1, axes=True):
        """
        Draw a line graph from a list of numeric samples.

        Parameters
        ----------
        samples : list / tuple of numbers
        x, y    : top-left of graph area
        w, h    : graph width and height in pixels (default full width)
        vmin    : value that maps to the bottom of the graph
        vmax    : value that maps to the top of the graph
        color   : line color
        axes    : draw top and bottom border lines
        """
        if w is None:
            w = self.width - x
        if not samples:
            return
        if axes:
            self.fb.hline(x, y,         w, color)
            self.fb.hline(x, y + h - 1, w, color)

        n    = len(samples)
        span = vmax - vmin if vmax != vmin else 1

        def sy(v):
            return y + h - 1 - int((v - vmin) / span * (h - 1))

        prev_px = x
        prev_py = sy(samples[0])

        for i in range(1, n):
            px = x + int(i * (w - 1) / max(n - 1, 1))
            py = sy(samples[i])
            self.fb.line(prev_px, prev_py, px, py, color)
            prev_px, prev_py = px, py

    def draw_bar_chart(self, values, x=0, y=14, w=None, h=48,
                       vmin=0, vmax=None, gap=1, color=1):
        """
        Draw a vertical bar chart.

        Parameters
        ----------
        values : list of numbers
        x, y   : top-left of chart area
        w, h   : chart width and height
        vmin   : minimum value (bar floor)
        vmax   : maximum value (bar ceiling); auto if None
        gap    : pixel gap between bars
        """
        if w is None:
            w = self.width - x
        if not values:
            return
        if vmax is None:
            vmax = max(values)
        span   = vmax - vmin if vmax != vmin else 1
        n      = len(values)
        bar_w  = max(1, (w - gap * (n - 1)) // n)

        for i, v in enumerate(values):
            bh = max(1, int((v - vmin) / span * h))
            bx = x + i * (bar_w + gap)
            by = y + h - bh
            self.fb.fill_rect(bx, by, bar_w, bh, color)

    # ═══════════════════════════════════════════════════════════
    #  UI WIDGETS
    # ═══════════════════════════════════════════════════════════

    def status_bar(self, title, value="", bg=1, fg=0):
        """
        Draw a filled header bar at the top of the screen.

        Parameters
        ----------
        title : left-aligned title text (max ~10 chars)
        value : right-aligned value text
        bg    : bar background color (default 1=white)
        fg    : text color on bar     (default 0=black)
        """
        self.fb.fill_rect(0, 0, self.width, 11, bg)
        self.fb.text(title[:10], 2, 2, fg)
        if value:
            rx = self.width - len(value) * 8 - 2
            self.fb.text(value[:8], max(0, rx), 2, fg)

    def notification(self, sender, body, show_now=True):
        """
        Display a notification card: sender header + body with word-wrap.

        Parameters
        ----------
        sender   : sender name (shown in header bar)
        body     : message body text (auto word-wrapped)
        show_now : call show() immediately (default True)
        """
        self.fb.fill(0)
        self.status_bar(sender)
        self.wrap_text(body, 0, 14, line_spacing=11)
        if show_now:
            self.show()

    def splash(self, title, subtitle="", delay_ms=0):
        """
        Display a centered splash screen.

        Parameters
        ----------
        title    : main title text
        subtitle : secondary text shown below
        delay_ms : if > 0, hold for this many milliseconds then return
        """
        self.fb.fill(0)
        ty = 20 if subtitle else 28
        self.center_text(title,    ty)
        if subtitle:
            self.center_text(subtitle, ty + 14)
        self.show()
        if delay_ms > 0:
            time.sleep_ms(delay_ms)

    def draw_menu(self, items, cursor=0, scroll_top=0, visible=4,
                  header=None, show_now=True):
        """
        Draw a scrollable menu with a highlighted cursor row.

        Parameters
        ----------
        items      : list of menu item strings
        cursor     : currently selected index
        scroll_top : index of the first visible item
        visible    : number of rows visible at once (default 4)
        header     : optional header bar text (uses top 11 pixels if set)
        show_now   : call show() immediately

        Returns
        -------
        (cursor, scroll_top) — updated after clamping
        """
        self.fb.fill(0)
        y_offset = 0

        if header:
            self.status_bar(header)
            y_offset = 13

        row_h = (self.height - y_offset) // visible

        for i in range(visible):
            idx = scroll_top + i
            if idx >= len(items):
                break
            ry = y_offset + i * row_h
            if idx == cursor:
                self.fb.fill_rect(0, ry, self.width, row_h, 1)
                self.fb.text(items[idx][:16], 2, ry + (row_h - 8) // 2, 0)
            else:
                self.fb.text(items[idx][:16], 2, ry + (row_h - 8) // 2, 1)

        # Scrollbar on right edge
        if len(items) > visible:
            sb_h   = max(4, self.height * visible // len(items))
            sb_y   = y_offset + (self.height - y_offset - sb_h) * scroll_top // max(1, len(items) - visible)
            self.fb.fill_rect(self.width - 3, y_offset, 2, self.height - y_offset, 0)
            self.fb.fill_rect(self.width - 3, sb_y, 2, sb_h, 1)

        if show_now:
            self.show()
        return cursor, scroll_top

    def page_dots(self, total, current, y=None, color=1):
        """
        Draw pagination indicator dots at the bottom of the screen.

        Parameters
        ----------
        total   : total number of pages
        current : current page index (0-based)
        y       : y position (default: bottom row)
        """
        if y is None:
            y = self.height - 6
        dot_w  = 5
        gap    = 3
        total_w = total * dot_w + (total - 1) * gap
        start_x = (self.width - total_w) // 2
        for i in range(total):
            dx = start_x + i * (dot_w + gap)
            if i == current:
                self.fb.fill_rect(dx, y, dot_w, dot_w, color)
            else:
                self.fb.rect(dx, y, dot_w, dot_w, color)

    def marquee(self, msg, offset, y=0, color=1):
        """
        Draw a single frame of a horizontal scrolling marquee.
        Call repeatedly, incrementing offset each frame.

        Parameters
        ----------
        msg    : string to scroll
        offset : current pixel offset from right (increase each frame)
        y      : vertical position
        color  : text color

        Returns
        -------
        New offset value (resets automatically when text has fully scrolled off)

        Example usage:
            offset = 0
            while True:
                oled.clear()
                offset = oled.marquee("Hello scrolling world!  ", offset)
                oled.show()
                time.sleep_ms(30)
        """
        x = self.width - offset
        self.fb.text(msg, x, y, color)
        offset += 2
        if offset > len(msg) * 8 + self.width:
            offset = 0
        return offset

    # ═══════════════════════════════════════════════════════════
    #  CONVENIENCE
    # ═══════════════════════════════════════════════════════════

    def scan(self):
        """Return list of I2C addresses found on the bus."""
        return self.i2c.scan()

    def print_line(self, msg, line=0, clear_first=False, color=1):
        """
        Write a single text line (by line number 0-7) and call show().

        Parameters
        ----------
        line        : row number 0 … 7  (each row = 8 pixels)
        clear_first : fill screen black before writing
        """
        if clear_first:
            self.fb.fill(0)
        self.fb.text(str(msg)[:16], 0, line * 8, color)
        self.show()

    def __repr__(self):
        return "OLED({}x{} @ I2C 0x{:02X})".format(self.width, self.height, self.addr)

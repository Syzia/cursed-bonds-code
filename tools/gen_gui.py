"""Generate the Cursed Bonds GUI images from the palette.

    python3 tools/gen_gui.py            # phase 2's four pictures (pure Python)
    python3 tools/gen_gui.py --all      # those, and the phase-1 set (needs Pillow)

Phase 2's four (PHASE2_DESIGN.md section 5, row 9), drawn with tools/raster.py,
so they need nothing installed. Each is a stand-in the game already looks for
by name; a painted file of the same name and size may replace any of them.

    gui/grade_sheen.png  1024x64   the Special Grade oil-slick strip. It tiles
                                   left to right; sb_grades.rpy slides a 512 px
                                   window along it behind the chip.
    gui/hot_ring.png     96x96     the soft glow under a room hotspot. The 72 px
                                   icon button sits in its middle, so the glow
                                   is what shows around the button.
    gui/soft_box.png     96x96     white, fading to clear over 24 px at every
                                   edge: Frame("gui/soft_box.png", 24, 24) is
                                   the feathered mask of a painted pose's box.
    gui/card_back.png    120x168   the back of a playing card.

The phase-1 set (panels, pips, the textbox, sliders, the seal, the window icon)
is derived from the same tokens as gui.rpy and is only redrawn when asked for,
with --all: it needs Pillow (pip install pillow), and a different Pillow
version can write the same picture as different bytes. Re-run with --all after
changing a colour.
"""
import os, sys, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "game", "gui")

INK    = (7, 6, 12)
PANEL  = (20, 17, 29)
PANEL2 = (27, 23, 39)
LINE   = (42, 36, 56)
LINE2  = (64, 56, 84)
DIM    = (157, 149, 174)
MUTE   = (106, 100, 120)
VIOLET = (162, 89, 255)
VIOLET_DEEP = (45, 28, 82)
SEAL   = (232, 51, 79)
GOLD   = (255, 209, 102)
PAPER  = (236, 231, 245)

SHEEN_SIZE = (1024, 64)
RING_SIZE = (96, 96)
SOFT_SIZE, SOFT_EDGE = (96, 96), 24
CARD_SIZE = (120, 168)


def put(im, x, y, c, a=255):
    i = (y * im.w + x) * 4
    im.buf[i:i + 4] = bytes((c[0], c[1], c[2], max(0, min(255, int(a)))))


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# --- the Special Grade sheen: an oil slick, tileable left to right -------------------
# The colours of oil on water, in the order they come round; the last runs back
# into the first. Mid-dark on purpose: the chip's text is the pale gui.paper,
# and the game lays the strip at 0.85 over the dark base #16121f.
SHEEN_STOPS = [(22, 128, 136), (44, 84, 176), (112, 60, 184), (176, 56, 140),
               (184, 124, 64), (64, 150, 104)]


def grade_sheen():
    """One slow turn of SHEEN_STOPS across the strip, so the 512 px window the
    game shows holds two or three colours at a time and drifts through the
    rest. The position along the palette wobbles (whole numbers of waves, so
    column 1023 runs into column 0 with no seam), the bands lean like light on
    oil (x + 0.9 y), and a pale gloss runs along the upper third."""
    w, h = SHEEN_SIZE
    im = Img(w, h, alpha=True)
    tau = 2 * math.pi
    n = len(SHEEN_STOPS)
    for y in range(h):
        gloss = 0.16 * math.exp(-((y - 18) / 11.0) ** 2)
        for x in range(w):
            u = ((x + 0.9 * y) % w) / float(w)
            t = (u + 0.035 * math.sin(tau * 3 * u) + 0.012 * math.sin(tau * 7 * u + 1.3)) % 1.0
            k = int(t * n)
            f = smooth(t * n - k)
            c0, c1 = SHEEN_STOPS[k % n], SHEEN_STOPS[(k + 1) % n]
            lum = 0.92 + 0.10 * math.sin(tau * 4 * u + 2.4) + gloss
            put(im, x, y, tuple(max(0, min(255, int((c0[i] + (c1[i] - c0[i]) * f) * lum))) for i in range(3)))
    return im


# --- the hotspot glow: a soft rounded square, brightest where the button's edge is ----
def hot_ring():
    """The game shows it at 96x96 with a 72 px button over the middle. Inside
    the button's outline the glow is faint (it shows through the dark panel);
    from the outline outwards it fades to nothing at the picture's edge."""
    w, h = RING_SIZE
    im = Img(w, h, alpha=True)
    half, rad, reach = 35.0, 8.0, 12.5
    col = (196, 160, 255)
    for y in range(h):
        for x in range(w):
            px, py = abs(x + 0.5 - w / 2.0), abs(y + 0.5 - h / 2.0)
            dx, dy = max(px - (half - rad), 0.0), max(py - (half - rad), 0.0)
            d = math.sqrt(dx * dx + dy * dy) - rad      # < 0 inside the outline
            if d <= 0:
                a = 0.30 + 0.55 * smooth(1.0 + d / 6.0)
            else:
                a = 0.85 * (1.0 - smooth(d / reach)) ** 1.5
            put(im, x, y, col, 255 * a)
    return im


# --- the soft box: the feathered mask of a pose's box ---------------------------------
def soft_box():
    w, h = SOFT_SIZE
    e = float(SOFT_EDGE)
    im = Img(w, h, alpha=True)
    for y in range(h):
        for x in range(w):
            dx = max(e - (x + 0.5), (x + 0.5) - (w - e), 0.0)
            dy = max(e - (y + 0.5), (y + 0.5) - (h - e), 0.0)
            put(im, x, y, (255, 255, 255), 255 * smooth(1.0 - math.sqrt(dx * dx + dy * dy) / e))
    return im


# --- the card back: ink, a violet border, a diamond lattice, the seal's diamond -------
def card_back():
    S = 3                                              # drawn large, then averaged down
    w, h = CARD_SIZE
    big = Img(w * S, h * S, alpha=True)
    big.rrect(0, 0, w * S - 1, h * S - 1, 8 * S, VIOLET)
    big.rrect(2 * S, 2 * S, (w - 2) * S - 1, (h - 2) * S - 1, 6.5 * S, PANEL)
    big.rrect(8 * S, 8 * S, (w - 8) * S - 1, (h - 8) * S - 1, 3 * S, LINE2)
    big.rrect(9 * S, 9 * S, (w - 9) * S - 1, (h - 9) * S - 1, 2.5 * S, VIOLET_DEEP)
    # the lattice: small diamonds on a 12 px pitch, every other row shifted
    step = 12 * S
    row = 0
    y = 9 * S + step // 2
    while y < (h - 9) * S:
        x = 9 * S + (step // 2 if row % 2 == 0 else step)
        while x < (w - 9) * S - step // 4:
            r = 2.2 * S
            big.poly([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], LINE2, 0.9)
            x += step
        y += step // 2
        row += 1
    # the centre: the seal's square, turned, with a violet diamond in it
    cx, cy = w * S / 2.0, h * S / 2.0
    for r, c in ((30 * S, PANEL), (27 * S, SEAL), (24 * S, PANEL), (15 * S, VIOLET)):
        big.poly([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], c)
    from raster import resample
    return resample(big, w, h)


PHASE2 = (("grade_sheen.png", grade_sheen, SHEEN_SIZE), ("hot_ring.png", hot_ring, RING_SIZE),
          ("soft_box.png", soft_box, SOFT_SIZE), ("card_back.png", card_back, CARD_SIZE))


def phase2():
    for name, draw, size in PHASE2:
        im = draw()
        assert (im.w, im.h) == size and im.ch == 4, name
        im.save(os.path.join(OUT, name))
        print("%-16s %dx%d" % (name, im.w, im.h))


# --- the phase-1 set (needs Pillow): python3 tools/gen_gui.py --all -------------------
def phase1():
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise SystemExit("--all redraws the phase-1 pictures with Pillow: pip install pillow")

    def rgba(c, a=255):
        return (c[0], c[1], c[2], a)

    def save(im, name):
        p = os.path.join(OUT, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        im.save(p)

    # --- 9-slice panels: 1px hairline border, translucent fill. Use Frame(img, 4, 4). --------
    def panel(name, fill, fill_a, border, border_w=1, rail=None, rail_w=0, size=32):
        im = Image.new("RGBA", (size, size), rgba(fill, fill_a))
        d = ImageDraw.Draw(im)
        for i in range(border_w):
            d.rectangle([i, i, size - 1 - i, size - 1 - i], outline=rgba(border))
        if rail:
            d.rectangle([0, 0, rail_w - 1, size - 1], fill=rgba(rail))
        save(im, name)

    panel("panel.png",         PANEL, 236, LINE)
    panel("panel_solid.png",   PANEL, 255, LINE)
    panel("panel_hover.png",   PANEL2, 245, LINE2)
    panel("panel_active.png",  VIOLET_DEEP, 245, VIOLET)
    panel("panel_gold.png",    PANEL, 236, GOLD)
    panel("panel_dark.png",    INK, 232, LINE)
    panel("panel_ghost.png",   INK, 170, LINE)
    panel("rail_violet.png",   PANEL2, 245, VIOLET, rail=VIOLET, rail_w=6)
    panel("rail_only.png",     PANEL, 0, PANEL, border_w=0, rail=VIOLET, rail_w=4)   # transparent, just the rail

    # --- textbox: vertical gradient, transparent -> ink ----------------------------------
    W, H = 1920, 340
    im = Image.new("RGBA", (W, H))
    px = im.load()
    for y in range(H):
        t = y / (H - 1)
        # ease so the top is very soft and the bottom nearly solid
        a = 0.0 if t < 0.04 else min(1.0, ((t - 0.04) / 0.5) ** 1.35)
        a = 0.94 * a if t < 0.6 else 0.94 + (t - 0.6) / 0.4 * 0.04
        col = rgba(INK, int(255 * a))
        for x in range(W):
            px[x, y] = col
    save(im, "textbox.png")

    # --- main-menu overlay: horizontal gradient, ink on the left -------------------------
    im = Image.new("RGBA", (W, 1080))
    px = im.load()
    for x in range(W):
        t = x / (W - 1)
        a = 0.93 - 0.85 * (t ** 1.1)
        col = rgba(INK, int(255 * max(0.06, a)))
        for y in range(1080):
            px[x, y] = col
    save(im, "overlay/main_menu.png")

    # game menu: near-solid ink so the content reads
    im = Image.new("RGBA", (W, 1080), rgba(INK, 242))
    save(im, "overlay/game_menu.png")
    im = Image.new("RGBA", (W, 1080), rgba(INK, 200))
    save(im, "overlay/confirm.png")

    # --- diamond pips (period tracker, action cost, check/radio) --------------------------
    def diamond(name, size, fill=None, outline=None, ow=2):
        S = size * 4  # supersample
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = S / 2
        r = S / 2 - ow * 2
        pts = [(c, c - r), (c + r, c), (c, c + r), (c - r, c)]
        if fill:
            d.polygon(pts, fill=rgba(fill))
        if outline:
            d.line(pts + [pts[0]], fill=rgba(outline), width=ow * 4, joint="curve")
        im = im.resize((size, size), Image.LANCZOS)
        save(im, name)

    diamond("pip_on.png",   16, fill=VIOLET)
    diamond("pip_past.png", 16, fill=MUTE)
    diamond("pip_off.png",  16, outline=DIM, ow=1)
    diamond("pip_gold.png", 16, fill=GOLD)
    diamond("pip_seal.png", 16, fill=SEAL)
    diamond("pip_small.png", 12, fill=VIOLET)
    diamond("pin.png",      18, fill=VIOLET)
    diamond("pin_here.png", 22, fill=GOLD)

    # check / radio foregrounds: 30px square, diamond centred-left (button has left padding)
    def fg(name, size=30, fill=None, outline=None):
        S = size * 4
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = S / 2; r = S * 0.30
        pts = [(c, c - r), (c + r, c), (c, c + r), (c - r, c)]
        if fill: d.polygon(pts, fill=rgba(fill))
        if outline: d.line(pts + [pts[0]], fill=rgba(outline), width=6, joint="curve")
        im = im.resize((size, size), Image.LANCZOS)
        save(im, name)

    fg("button/check_foreground.png", outline=MUTE)
    fg("button/check_selected_foreground.png", fill=VIOLET)
    fg("button/radio_foreground.png", outline=MUTE)
    fg("button/radio_selected_foreground.png", fill=VIOLET)

    # --- sliders / scrollbars: flat (bars are Solid() in screens.rpy) ---------------------
    def flat(name, w, h, col, a=255):
        save(Image.new("RGBA", (w, h), rgba(col, a)), name)

    for pre in ("idle", "hover"):
        # slider bars are as tall as the thumb (26px) with a 6px band through the middle
        col = LINE if pre == "idle" else LINE2
        im = Image.new("RGBA", (64, 26), (0, 0, 0, 0)); ImageDraw.Draw(im).rectangle([0, 10, 63, 15], fill=rgba(col))
        save(im, "slider/horizontal_%s_bar.png" % pre)
        im = Image.new("RGBA", (26, 64), (0, 0, 0, 0)); ImageDraw.Draw(im).rectangle([10, 0, 15, 63], fill=rgba(col))
        save(im, "slider/vertical_%s_bar.png" % pre)
        flat("scrollbar/horizontal_%s_bar.png" % pre, 64, 6, LINE, 0 if pre == "idle" else 255)
        flat("scrollbar/vertical_%s_bar.png" % pre, 6, 64, LINE, 0 if pre == "idle" else 255)
        flat("scrollbar/horizontal_%s_thumb.png" % pre, 64, 6, MUTE if pre == "idle" else DIM)
        flat("scrollbar/vertical_%s_thumb.png" % pre, 6, 64, MUTE if pre == "idle" else DIM)

    # slider thumb: a diamond
    diamond("slider/horizontal_idle_thumb.png", 26, fill=DIM)
    diamond("slider/horizontal_hover_thumb.png", 26, fill=VIOLET)
    diamond("slider/vertical_idle_thumb.png", 26, fill=DIM)
    diamond("slider/vertical_hover_thumb.png", 26, fill=VIOLET)

    # --- hanko seal: red square outline, used behind a kanji text (only ever at 44px) --------
    for size in (44,):
        S = size * 4
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rectangle([4, 4, S - 5, S - 5], outline=rgba(SEAL), width=9)
        im = im.resize((size, size), Image.LANCZOS)
        save(im, "seal_%d.png" % size)

    # --- window icon ----------------------------------------------------------------------
    S = 256
    im = Image.new("RGBA", (S, S), rgba(INK))
    d = ImageDraw.Draw(im)
    d.rectangle([24, 24, S - 25, S - 25], outline=rgba(SEAL), width=14)
    c = S / 2; r = 58
    d.polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)], fill=rgba(VIOLET))
    save(im, "window_icon.png")


if __name__ == "__main__":
    unknown = [a for a in sys.argv[1:] if a != "--all"]
    if unknown:
        print(__doc__); raise SystemExit(1)
    phase2()
    if "--all" in sys.argv:
        phase1()
    print("ok")

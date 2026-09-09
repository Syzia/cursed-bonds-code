"""Generate the Cursed Bonds GUI images from the palette. Needs Pillow (pip install pillow).

    python3 tools/gen_gui.py

Everything here is derived from the same tokens as gui.rpy. Re-run after changing a colour.
"""
from PIL import Image, ImageDraw
import os, math

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
panel("panel_seal.png",    PANEL, 236, SEAL)
panel("panel_dark.png",    INK, 232, LINE)
panel("panel_ghost.png",   INK, 170, LINE)
panel("rail_violet.png",   PANEL2, 245, VIOLET, rail=VIOLET, rail_w=6)
panel("rail_gold.png",     PANEL2, 245, GOLD,   rail=GOLD, rail_w=6)
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

# --- bars / sliders / scrollbars: flat ----------------------------------------------
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
    flat("bar/left.png", 64, 6, VIOLET); flat("bar/right.png", 64, 6, LINE)
    flat("bar/top.png", 6, 64, VIOLET); flat("bar/bottom.png", 6, 64, LINE)

# slider thumb: a diamond
diamond("slider/horizontal_idle_thumb.png", 26, fill=DIM)
diamond("slider/horizontal_hover_thumb.png", 26, fill=VIOLET)
diamond("slider/vertical_idle_thumb.png", 26, fill=DIM)
diamond("slider/vertical_hover_thumb.png", 26, fill=VIOLET)

# --- hanko seal: red square outline, used behind a kanji text ---------------------------
for size in (44, 60, 84):
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

print("ok")

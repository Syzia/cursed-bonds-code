"""The reusable figure: head, face, body, uniform. Spec-driven."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anime import Cel, curve, bez, hexc, lerp, W, H

# --- layout (1x coordinates in a 760x1400 canvas) ---------------------------
CX      = 380
HEAD_T  = 152
CHIN    = 404
HEAD_H  = CHIN - HEAD_T
HW      = 106                     # head half-width
EYE_Y   = HEAD_T + HEAD_H * 0.60
EYE_DX  = 46
EYE_W   = 54
EYE_H   = 46
NOSE_Y  = HEAD_T + HEAD_H * 0.775
MOUTH_Y = HEAD_T + HEAD_H * 0.875
NECK_T  = CHIN - 12
SH_Y    = 494
HIP_Y   = 812
KNEE_Y  = 1090
FOOT_Y  = 1358


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


# --- head ------------------------------------------------------------------
def head_path():
    return curve([
        (CX,        HEAD_T),
        (CX + HW*0.72, HEAD_T + HEAD_H*0.10),
        (CX + HW,      HEAD_T + HEAD_H*0.34),
        (CX + HW*0.94, HEAD_T + HEAD_H*0.58),
        (CX + HW*0.66, HEAD_T + HEAD_H*0.84),
        (CX,        CHIN),
        (CX - HW*0.66, HEAD_T + HEAD_H*0.84),
        (CX - HW*0.94, HEAD_T + HEAD_H*0.58),
        (CX - HW,      HEAD_T + HEAD_H*0.34),
        (CX - HW*0.72, HEAD_T + HEAD_H*0.10),
    ], steps=10)


# --- the eye: the piece that decides whether this reads as anime ------------
EXPR = {
    #            lid   brow_in brow_out browy  mouth   pupil
    "neutral":  (0.00,  0.00,  0.00,   0.0,   "soft",  1.00),
    "happy":    (0.22,  0.06, -0.10,  -2.0,   "smile", 1.00),
    "serious":  (0.14, -0.10,  0.04,   3.0,   "flat",  0.88),
    "angry":    (0.20, -0.26,  0.10,   6.0,   "frown", 0.80),
    "surprised":(-0.14, 0.10,  0.10,  -7.0,   "open",  0.72),
    "sad":      (0.10,  0.22, -0.14,  -3.0,   "sad",   1.06),
}


def eye(c, cx, cy, side, iris, expr, skin):
    lid, bi, bo, by, mouth, pup = EXPR[expr]
    w, h = EYE_W * 0.5, EYE_H * 0.5
    h_open = h * (1.0 - lid)
    top = cy - h_open
    bot = cy + h * 0.92

    # sclera
    c.ellipse(cx, cy, w, h_open * 1.02, hexc("#fdfbff"), soft=1.4)
    c.ellipse(cx, cy + h_open*0.42, w*0.92, h_open*0.46, hexc("#e6dfef"), 0.55, soft=2.0)

    # iris: tall, cropped to the eye opening
    ir = w * 0.62 * pup
    iy = cy + h_open * 0.06
    c.ellipse(cx, iy, ir, h_open*0.96, shade(iris, 0.72), soft=1.2,
              ymin=top, ymax=bot)
    c.ellipse(cx, iy + h_open*0.20, ir*0.94, h_open*0.72, iris, soft=1.2,
              ymin=top, ymax=bot)
    c.ellipse(cx, iy + h_open*0.46, ir*0.80, h_open*0.40, shade(iris, 1.35), 0.8,
              soft=1.6, ymin=top, ymax=bot)
    # pupil
    c.ellipse(cx, iy + h_open*0.08, ir*0.42, h_open*0.56, hexc("#1a1016"), soft=1.0,
              ymin=top, ymax=bot)
    # highlights
    c.ellipse(cx - ir*0.42, iy - h_open*0.34, ir*0.34, h_open*0.30, hexc("#ffffff"), 0.96, soft=1.0)
    c.ellipse(cx + ir*0.44, iy + h_open*0.40, ir*0.18, h_open*0.16, hexc("#ffffff"), 0.7, soft=1.0)

    # upper lid — thick, sweeping past the outer corner into a lash
    ox = side
    lid_pts = curve([
        (cx - w*1.06, cy + h_open*0.16),
        (cx - w*0.44, top - h_open*0.20),
        (cx + w*0.30, top - h_open*0.10),
        (cx + w*1.02, cy - h_open*0.16),
    ], steps=8)
    if ox < 0:
        lid_pts = [(2*cx - x, y) for x, y in lid_pts]
    c.stroke(lid_pts, EYE_H*0.17)
    # lash flick at the outer corner
    outer = (cx + ox*w*1.02, cy - h_open*0.16)
    c.taper(curve([outer, (outer[0] + ox*w*0.30, outer[1] - h*0.22),
                   (outer[0] + ox*w*0.52, outer[1] - h*0.44)], steps=6),
            EYE_H*0.16, 0.6)
    # lower lid — thin
    low = curve([(cx - w*0.86, cy + h*0.62), (cx, bot*0.995), (cx + w*0.86, cy + h*0.58)], steps=6)
    c.stroke(low, EYE_H*0.055, a=0.62)

    # brow
    brow_y = top - EYE_H*0.52 + by
    inner = (cx - ox*w*0.86, brow_y + bi*EYE_H)
    outer_b = (cx + ox*w*1.00, brow_y + bo*EYE_H + EYE_H*0.10)
    c.taper(curve([inner, (cx + ox*w*0.06, brow_y - EYE_H*0.13), outer_b], steps=8),
            EYE_H*0.15, EYE_H*0.05)


def mouth(c, expr, skin):
    kind = EXPR[expr][4]
    y = MOUTH_Y
    line = hexc("#4a2c30")
    if kind == "smile":
        c.stroke(curve([(CX-24, y-3), (CX, y+9), (CX+24, y-3)], steps=8), 4.0, line)
    elif kind == "flat":
        c.stroke([(CX-17, y), (CX+17, y)], 3.4, line)
    elif kind == "frown":
        c.stroke(curve([(CX-22, y+6), (CX, y-3), (CX+22, y+6)], steps=8), 4.2, line)
    elif kind == "open":
        c.outlined_ellipse(CX, y+4, 15, 19, hexc("#5e2b33"), 2.6)
        c.ellipse(CX, y+11, 10, 8, hexc("#c9566a"), 0.8)
    elif kind == "sad":
        c.stroke(curve([(CX-20, y+5), (CX, y-1), (CX+20, y+5)], steps=8), 3.4, line)
    else:
        c.stroke(curve([(CX-16, y-1), (CX, y+4), (CX+15, y-1)], steps=8), 3.4, line)


def face(c, spec, expr):
    skin = hexc(spec["skin"])
    iris = hexc(spec["iris"])
    # ears
    for s in (-1, 1):
        c.outlined_ellipse(CX + s*HW*0.97, EYE_Y + 6, 15, 26, skin, 3.0)
    # head
    hp = head_path()
    c.outlined(hp, skin, 3.4)
    # cheek/jaw shadow
    c.ellipse(CX, CHIN - 34, HW*0.62, 30, shade(skin, 0.93), 0.5, soft=8)
    # eyes
    eye(c, CX - EYE_DX, EYE_Y, -1, iris, expr, skin)
    eye(c, CX + EYE_DX, EYE_Y, 1, iris, expr, skin)
    # nose
    c.stroke(curve([(CX+3, NOSE_Y-7), (CX+7, NOSE_Y), (CX-1, NOSE_Y+3)], steps=5),
             2.6, shade(skin, 0.66), 0.85)
    mouth(c, expr, skin)
    # Yuji's under-eye marks
    if spec.get("eye_marks"):
        for s in (-1, 1):
            mx = CX + s*EYE_DX
            c.taper(curve([(mx - 13, EYE_Y + EYE_H*0.66),
                           (mx, EYE_Y + EYE_H*0.74),
                           (mx + 13, EYE_Y + EYE_H*0.64)], steps=6),
                    4.4, 1.2, shade(skin, 0.55), 0.9)


# --- body ------------------------------------------------------------------
def body(c, spec):
    skin = hexc(spec["skin"])
    uni  = hexc(spec["uniform"])
    uni_d = shade(uni, 0.72)
    uni_l = shade(uni, 1.16)
    inner = hexc(spec.get("inner", "#b8323c"))
    build = spec.get("build", 1.0)
    shw = 172 * build
    hipw = 116 * build

    # hood, first, so it sits behind everything at the neck
    if spec.get("hood"):
        c.outlined(curve([
            (CX - 118, SH_Y + 18), (CX - 112, SH_Y - 54), (CX - 58, SH_Y - 86),
            (CX, SH_Y - 94), (CX + 58, SH_Y - 86), (CX + 112, SH_Y - 54),
            (CX + 118, SH_Y + 18), (CX + 60, SH_Y + 34), (CX, SH_Y + 38),
            (CX - 60, SH_Y + 34),
        ], steps=8), inner, 3.6)
        c.stroke(curve([(CX - 96, SH_Y - 34), (CX, SH_Y - 62), (CX + 96, SH_Y - 34)], steps=8),
                 3.0, shade(inner, 0.62), 0.8)

    # neck
    c.outlined([(CX-32, NECK_T-8), (CX+32, NECK_T-8), (CX+30, SH_Y-6), (CX-30, SH_Y-6)],
               shade(skin, 0.86), 3.0)

    # legs — thicker, with a knee break
    for s_ in (-1, 1):
        x = CX + s_*hipw*0.54
        leg = curve([
            (x - 46*build, HIP_Y - 30), (x + 46*build, HIP_Y - 30),
            (x + 42*build, KNEE_Y), (x + 38*build, FOOT_Y - 34),
            (x - 38*build, FOOT_Y - 34), (x - 42*build, KNEE_Y),
        ], steps=4)
        c.outlined(leg, uni_d, 3.6)
    

    # shoes
    for s_ in (-1, 1):
        x = CX + s_*hipw*0.54
        c.outlined([(x-44*build, FOOT_Y-40), (x+40*build, FOOT_Y-40),
                    (x+46*build, FOOT_Y), (x-50*build, FOOT_Y)], hexc("#efeae2"), 3.2)
        c.stroke([(x-42*build, FOOT_Y-14), (x+42*build, FOOT_Y-14)], 2.4, shade(uni, 0.9), 0.5)

    # torso: sloped shoulders into a taper
    torso = curve([
        (CX - shw, SH_Y + 40), (CX - shw*0.96, SH_Y + 2),
        (CX - shw*0.70, SH_Y - 28), (CX - shw*0.26, SH_Y - 40),
        (CX + shw*0.26, SH_Y - 40), (CX + shw*0.70, SH_Y - 28),
        (CX + shw*0.96, SH_Y + 2), (CX + shw, SH_Y + 40),
        (CX + hipw, HIP_Y), (CX - hipw, HIP_Y),
    ], steps=6)
    c.outlined(torso, uni, 3.8)

    # hoodie showing in the open front — narrow strip only
    c.poly([(CX-44, SH_Y-30), (CX+44, SH_Y-30), (CX+14, HIP_Y-90), (CX-14, HIP_Y-90)], inner)

    # jacket panels laid over, leaving that strip visible
    for s_ in (-1, 1):
        panel = [(CX + s_*shw*0.99, SH_Y+34), (CX + s_*shw*0.72, SH_Y-30),
                 (CX + s_*46, SH_Y-32), (CX + s_*20, HIP_Y-88),
                 (CX + s_*24, HIP_Y-4), (CX + s_*hipw*0.99, HIP_Y-2)]
        c.outlined(panel, uni if s_ < 0 else uni_l, 3.2)

    # standing collar
    c.outlined([(CX-72, SH_Y-14), (CX+72, SH_Y-14), (CX+48, SH_Y-70), (CX-48, SH_Y-70)],
               uni_l, 3.2)
    c.stroke([(CX, SH_Y-66), (CX, SH_Y-16)], 2.6, shade(uni, 0.55), 0.7)

    # arms — tapered, attached at the shoulder, hands at the hip
    for s_ in (-1, 1):
        xs = CX + s_*shw*0.74
        xe = CX + s_*(hipw + 18*build)
        arm = curve([
            (xs - 27*build, SH_Y - 16), (xs + 27*build, SH_Y - 8),
            (xe + 22*build, HIP_Y + 46), (xe - 22*build, HIP_Y + 50),
        ], steps=5)
        c.outlined(arm, shade(uni, 0.86), 3.4)
        c.outlined_ellipse(xe, HIP_Y + 78, 24*build, 29*build, skin, 3.0)
        c.outlined_ellipse(xs, SH_Y + 4, 34*build, 40*build, shade(uni, 0.94), 3.2)

    # cel shadow down one side
    c.poly([(CX - shw, SH_Y + 26), (CX - shw*0.45, SH_Y + 4),
            (CX - hipw*0.5, HIP_Y), (CX - hipw, HIP_Y)], shade(uni, 0.8), 0.5)

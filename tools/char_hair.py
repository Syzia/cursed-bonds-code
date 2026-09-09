"""Hair styles. Drawn in two passes: a back mass behind the head, then front
locks over the forehead, so the face sits inside the hair rather than under it."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anime import curve, hexc
from char_rig import CX, HEAD_T, CHIN, HEAD_H, HW, EYE_Y, shade


def _lock(c, base, tip, ctrl, w0, w1, col):
    c.taper(curve([base, ctrl, tip], steps=8), w0, w1, col)


def undercut(c, col, dark, back=False):
    """Yuji: shaved dark sides, pink spiky top pushed up and back."""
    if back:
        # dark undercut mass hugging the skull
        c.outlined_ellipse(CX, HEAD_T + HEAD_H*0.40, HW*1.02, HEAD_H*0.50, dark, 3.0)
        return

    # pink cap sitting on the cranium
    cap = curve([
        (CX - HW*1.02, HEAD_T + HEAD_H*0.44),
        (CX - HW*0.86, HEAD_T + HEAD_H*0.06),
        (CX,           HEAD_T - HEAD_H*0.08),
        (CX + HW*0.86, HEAD_T + HEAD_H*0.06),
        (CX + HW*1.02, HEAD_T + HEAD_H*0.44),
        (CX + HW*0.72, HEAD_T + HEAD_H*0.30),
        (CX,           HEAD_T + HEAD_H*0.36),
        (CX - HW*0.72, HEAD_T + HEAD_H*0.30),
    ], steps=9)
    c.outlined(cap, col, 3.4)

    # spikes along the top, swept back
    spikes = [
        (-0.96, 0.32, -1.34, 44), (-0.78, 0.10, -1.16, 52), (-0.54, -0.04, -0.92, 58),
        (-0.28, -0.12, -0.64, 62), ( 0.00, -0.14, -0.30, 64), ( 0.28, -0.12,  0.14, 62),
        ( 0.54, -0.04,  0.52, 58), ( 0.78,  0.10,  0.92, 52), ( 0.96,  0.32,  1.24, 44),
    ]
    for fx, fy, tx, ln in spikes:
        bx = CX + HW*fx*0.92
        by = HEAD_T + HEAD_H*fy + HEAD_H*0.10
        tipx = CX + HW*tx*1.06
        tipy = by - ln
        _lock(c, (bx, by + 22), (tipx, tipy), (bx + (tipx-bx)*0.35, by - ln*0.62), 34, 2, col)

    # fringe falling over the brow
    for fx, drop in [(-0.60, 0.34), (-0.30, 0.40), (0.02, 0.38), (0.34, 0.42), (0.62, 0.32)]:
        bx = CX + HW*fx
        _lock(c, (bx, HEAD_T + HEAD_H*0.14), (bx + HW*0.10, HEAD_T + HEAD_H*drop),
              (bx + HW*0.06, HEAD_T + HEAD_H*0.26), 26, 8, col)
    # highlight band
    c.taper(curve([(CX - HW*0.62, HEAD_T + HEAD_H*0.16),
                   (CX, HEAD_T + HEAD_H*0.07),
                   (CX + HW*0.62, HEAD_T + HEAD_H*0.16)], steps=8),
            9, 4, shade(col, 1.28), 0.75)


def spiky_black(c, col, dark, back=False):
    """Megumi: heavy black spikes up and back, some falling forward."""
    if back:
        c.outlined_ellipse(CX, HEAD_T + HEAD_H*0.36, HW*1.10, HEAD_H*0.56, shade(col, 0.8), 3.0)
        return
    cap = curve([
        (CX - HW*1.06, HEAD_T + HEAD_H*0.46),
        (CX - HW*0.88, HEAD_T + HEAD_H*0.02),
        (CX,           HEAD_T - HEAD_H*0.12),
        (CX + HW*0.88, HEAD_T + HEAD_H*0.02),
        (CX + HW*1.06, HEAD_T + HEAD_H*0.46),
        (CX + HW*0.70, HEAD_T + HEAD_H*0.32),
        (CX,           HEAD_T + HEAD_H*0.38),
        (CX - HW*0.70, HEAD_T + HEAD_H*0.32),
    ], steps=9)
    c.outlined(cap, col, 3.4)
    for fx, ln, tx in [(-0.92, 52, -0.52), (-0.68, 66, -0.40), (-0.40, 74, -0.22),
                       (-0.08, 78, 0.02), (0.24, 74, 0.22), (0.54, 64, 0.42),
                       (0.80, 54, 0.60), (0.98, 40, 0.76)]:
        bx = CX + HW*fx*0.9
        by = HEAD_T + HEAD_H*0.06
        _lock(c, (bx, by + 22), (CX + HW*tx*1.14, by - ln), (bx, by - ln*0.55), 28, 2, col)
    for fx, drop in [(-0.52, 0.46), (-0.18, 0.52), (0.20, 0.50), (0.54, 0.42)]:
        bx = CX + HW*fx
        _lock(c, (bx, HEAD_T + HEAD_H*0.10), (bx - HW*0.08, HEAD_T + HEAD_H*drop),
              (bx, HEAD_T + HEAD_H*0.30), 24, 5, col)


def bob(c, col, dark, back=False):
    """Nobara: chin-length bob, long side-swept fringe."""
    if back:
        c.outlined_ellipse(CX, HEAD_T + HEAD_H*0.52, HW*1.16, HEAD_H*0.72, shade(col, 0.86), 3.0)
        return
    cap = curve([
        (CX - HW*1.10, HEAD_T + HEAD_H*0.86),
        (CX - HW*1.06, HEAD_T + HEAD_H*0.12),
        (CX,           HEAD_T - HEAD_H*0.06),
        (CX + HW*1.06, HEAD_T + HEAD_H*0.12),
        (CX + HW*1.10, HEAD_T + HEAD_H*0.86),
        (CX + HW*0.80, HEAD_T + HEAD_H*0.70),
        (CX + HW*0.72, HEAD_T + HEAD_H*0.30),
        (CX,           HEAD_T + HEAD_H*0.36),
        (CX - HW*0.72, HEAD_T + HEAD_H*0.30),
        (CX - HW*0.80, HEAD_T + HEAD_H*0.70),
    ], steps=10)
    c.outlined(cap, col, 3.4)
    # side-swept fringe across the brow
    _lock(c, (CX + HW*0.86, HEAD_T + HEAD_H*0.10), (CX - HW*0.92, HEAD_T + HEAD_H*0.44),
          (CX, HEAD_T + HEAD_H*0.10), 44, 12, col)
    for fx, drop in [(-0.66, 0.40), (0.30, 0.34), (0.66, 0.30)]:
        bx = CX + HW*fx
        _lock(c, (bx, HEAD_T + HEAD_H*0.12), (bx + HW*0.12, HEAD_T + HEAD_H*drop),
              (bx + HW*0.06, HEAD_T + HEAD_H*0.24), 22, 6, col)


STYLES = {"undercut": undercut, "spiky_black": spiky_black, "bob": bob}

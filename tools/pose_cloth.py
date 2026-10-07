"""
The school uniform's cloth on a painted pose, against the one ramp.

    tools/py_art.sh tools/pose_cloth.py <pose.png> <room.png> x,y,w,h
    tools/py_art.sh tools/pose_cloth.py <pose.png> <room.png> x,y,w,h --match <out.png>

docs/UI2_DESIGN.md D59. Every sprite that shows the school uniform lies on
one colour ramp (tools/cloth_match.py). A painted pose of one of the six is a
new drawing of the same cloth, so tools/install_pose.py runs this on the box
round the figure: it finds the uniform's cloth there (the pixels the editor
changed that are dark and cool-coloured, in big pieces), reads its dark, main
and streak tones, and says how far it is from the ramp, in levels.

--match writes a copy of the pose with that cloth moved onto the ramp, by the
same step cloth_match.py uses on a sprite. It changes no pixel outside the
cloth and refuses to write if it would, or if the cloth would still be off
the ramp afterwards.

Both pictures are 1920x1080 (install_pose.py has already fitted the render).
The ramp, the tones and the match are cloth_match.py's own: nothing is
copied here. numpy, scipy and Pillow: start it through tools/py_art.sh.

Exit status 0 when it measured (or found no cloth to measure), 1 on an error.
"""
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import numpy as np
    from PIL import Image
    from scipy import ndimage as ndi
except ImportError:
    raise SystemExit("numpy, scipy and Pillow are needed: start this with tools/py_art.sh")
import cloth_match

CHANGED = 24            # a pixel is the figure's when any channel differs from the room by more than this
MIN_CLOTH = 1500        # fewer cloth pixels than this: nothing to measure (a hand, a face, a figure far away)


def cloth_in_box(pose, room, box):
    """The uniform's cloth inside the box: changed from the room, dark, cool-coloured, in big pieces."""
    x, y, w, h = box
    fig = np.zeros(pose.shape[:2], bool)
    fig[y:y + h, x:x + w] = np.abs(pose[y:y + h, x:x + w, :3] - room[y:y + h, x:x + w, :3]).max(axis=2) > CHANGED
    r, g, b = pose[..., 0], pose[..., 1], pose[..., 2]
    luma = (r + g + b) / 3
    ok = fig & (luma < 135) & (b >= r - 6) & (b >= g - 6)
    m = ndi.binary_opening(ok, iterations=1)
    lab, n = ndi.label(m)
    if n:
        sizes = ndi.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, 1 + np.where(sizes > 400)[0])
    m = ndi.binary_dilation(m, iterations=1) & ok
    if not m.any():
        return m
    hist, edges = np.histogram(luma[m], bins=64, range=(0, 128))
    main = (edges[hist.argmax()] + edges[hist.argmax() + 1]) / 2
    return m & (luma <= np.percentile(luma[m], 97.5) + 12) & ~((luma > main + 18) & (b - r < 14))


def main(argv):
    out = None
    if "--match" in argv:
        i = argv.index("--match")
        out = argv[i + 1]
        del argv[i:i + 2]
    if len(argv) != 3:
        print(__doc__); raise SystemExit(1)
    pose = np.asarray(Image.open(argv[0]).convert("RGB")).astype(float)
    room = np.asarray(Image.open(argv[1]).convert("RGB")).astype(float)
    box = [int(v) for v in argv[2].split(",")]
    if pose.shape != room.shape:
        raise SystemExit("the pose and the room are not the same size")
    m = cloth_in_box(pose, room, box)
    n = int(m.sum())
    if n < MIN_CLOTH:
        print("no uniform cloth to measure in the box (%d dark cool pixels; %d are needed)" % (n, MIN_CLOTH))
        return
    t = cloth_match.tones(pose, m)
    d = cloth_match.off_ramp(pose, m)
    # A painted figure is small and may be sitting: it need not show all three of a sprite's tones. What is
    # held is the colour: every cloth pixel on the ramp's colour for its own brightness.
    on = d <= cloth_match.ON_RAMP
    print("the uniform's cloth in the box: %d px; dark / main / streak %.1f / %.1f / %.1f (the ramp: %.1f / %.1f / "
          "%.1f); %.2f levels off the ramp: %s"
          % (n, t["dark"], t["base"], t["high"], cloth_match.REF["dark"], cloth_match.REF["base"],
             cloth_match.REF["high"], d, "on the ramp" if on else "OFF the ramp"))
    if on:
        return
    if not out:
        print("to move it onto the ramp, install with --match-cloth (the same match the sprites had; no pixel "
              "outside the cloth changes)")
        return
    new = cloth_match.match(pose, m, t)
    diff = np.abs(new - pose).max(axis=2)
    if (diff[~m] > 0).any():
        raise SystemExit("a pixel outside the cloth would change; nothing written")
    after = cloth_match.off_ramp(new, m)
    if after > cloth_match.ON_RAMP:
        raise SystemExit("the cloth would still be %.2f levels off the ramp; nothing written" % after)
    Image.fromarray(new.astype(np.uint8), "RGB").save(out)
    print("moved onto the ramp: %d pixels changed, the largest by %.0f levels; now %.2f levels off"
          % (int((diff > 0).sum()), float(diff.max()), after))


if __name__ == "__main__":
    main(sys.argv[1:])

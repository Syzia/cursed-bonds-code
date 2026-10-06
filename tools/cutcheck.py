"""
A second pair of eyes on a cut-out: the anime-trained model, run directly.

    python3 tools/cutcheck.py <render.png>                 # cuts it with the new edge, then looks
    python3 tools/cutcheck.py <render.png> <cutout.png>    # looks at a cut-out already made (the render's size)
    python3 tools/cutcheck.py <render.png> --matte <file.png>    # also keep what the model saw

It only reports. It never changes a pixel, of the render or of the cut-out:
no model's result is used as a cut-out (docs/UI2_DESIGN.md D58). On pictures
whose true cut-out is known a model's matte as it comes left 20,000 to 27,000
visibly wrong edge pixels where our own edge leaves about 600. What the model
is good at is finding the figure: BiRefNet_toonout, trained on anime
characters, lost 20 to 37 pixels of figure over four characters where the
other four models tried lost 66 to 940. So it is asked three questions about a
cut-out our own tool made:

  a piece cut off     the cut-out is clear where the model is sure there is
                      figure (well inside what it calls figure). A real piece
                      lost, or a gap the model filled in: a lace loop, the
                      space between an arm and the body. Look at each.
  a gap left filled   the cut-out is solid where the model sees no figure at
                      all. Backdrop that stayed, or something thin the model
                      missed. Look at each.
  stray marks         separate specks of the cut-out, at least a tenth solid,
                      that the model does not call figure anywhere: dust in
                      the backdrop. Fainter specks are counted apart: the new
                      edge leaves a few hundred single pixels under a tenth
                      solid within four pixels of a real render's outline;
                      they show on no ground and are gone once the sprite is
                      fitted to the game's canvas.

A line of the report is a place to look at on a close-up, not a verdict: the
model is wrong about as often as the cut-out is.

How the model is run, and why (each was learned the hard way on 7 Oct):
  - Directly, in normal precision. ComfyUI's node for this model family runs
    half precision on the processor on a Mac: one picture took sixteen
    minutes. Directly it takes 6 to 20 seconds.
  - On the graphics chip (mps), with PYTORCH_ENABLE_MPS_FALLBACK=1, and with
    the one operation the chip does not have, the deformable convolution, run
    on the processor.
  - At the picture's own shape with its long side at 2048. Never a 2048
    square: that used 26 GB and pushed this Mac into swap.

The weights are ComfyUI's own copy, with the model's code beside them:
~/ComfyUI-Installs/ComfyUI/ComfyUI/models/RMBG/BiRefNet/. Where the weights,
the code or ComfyUI's Python are absent this says so plainly and exits 0: a
missing second look is not a failed cut-out. It never downloads anything.

torch: neither the system python3 nor ComfyUI's standalone Python has it. This
script starts itself again with the Python of ComfyUI's own environment.
"""
import sys, os, time

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")     # before torch is imported

TORCH_PY = os.path.expanduser("~/ComfyUI-Installs/ComfyUI/ComfyUI/.venv/bin/python3")
# CUTCHECK_MODEL_DIR is for the test of "the model is not here" (tools/test_keying.sh)
MODEL_DIR = os.path.expanduser(os.environ.get("CUTCHECK_MODEL_DIR")
                               or "~/ComfyUI-Installs/ComfyUI/ComfyUI/models/RMBG/BiRefNet")
WEIGHTS = "BiRefNet_toonout.safetensors"
NEEDED = (WEIGHTS, "birefnet.py", "BiRefNet_config.py")
LONG_SIDE = 2048
SURE_IN, SURE_OUT = 0.9, 0.1       # the model's matte: sure of figure, sure of none
DEPTH = 3                          # px inside either outline before the two are compared: edges always differ
MIN_PATCH = 12                     # px; smaller patches are counted, not listed
SHOWS = 0.1                        # a speck less solid than this shows on no ground


def skip(why):
    print("cutcheck: skipped. " + why)
    raise SystemExit(0)


def missing():
    return [f for f in NEEDED if not os.path.exists(os.path.join(MODEL_DIR, f))]


def load_model(device):
    """BiRefNet from ComfyUI's files. The model's code is a package file there
    (`from .BiRefNet_config import ...`), so it is read and compiled as a
    module of its own with that one import made absolute."""
    import types, importlib.util
    import torch
    from safetensors.torch import load_file
    spec = importlib.util.spec_from_file_location("BiRefNet_config", os.path.join(MODEL_DIR, "BiRefNet_config.py"))
    cfg = importlib.util.module_from_spec(spec)
    sys.modules["BiRefNet_config"] = cfg
    spec.loader.exec_module(cfg)
    src = open(os.path.join(MODEL_DIR, "birefnet.py"), encoding="utf-8").read().replace(
        "from .BiRefNet_config", "from BiRefNet_config")
    mod = types.ModuleType("birefnet_cutcheck")
    sys.modules[mod.__name__] = mod
    exec(compile(src, os.path.join(MODEL_DIR, "birefnet.py"), "exec"), mod.__dict__)
    if device != "cpu" and "deform_conv2d" in mod.__dict__:
        # the graphics chip has no deformable convolution: that one call goes
        # to the processor and its result comes back
        real = mod.__dict__["deform_conv2d"]

        def on_cpu(input, offset, weight, bias=None, stride=(1, 1), padding=(0, 0), dilation=(1, 1), mask=None):
            c = lambda t: None if t is None else t.cpu()
            return real(c(input), c(offset), c(weight), c(bias), stride=stride, padding=padding,
                        dilation=dilation, mask=c(mask)).to(input.device)
        mod.__dict__["deform_conv2d"] = on_cpu
    model = mod.BiRefNet(cfg.BiRefNetConfig())
    model.load_state_dict(load_file(os.path.join(MODEL_DIR, WEIGHTS)), strict=True)
    return model.eval().float().to(device)


def working_size(w, h, long_side=LONG_SIDE):
    """The picture's own shape, long side at 2048, each side a multiple of 32
    (the model's stride). Never square."""
    s = long_side / float(max(w, h))
    return max(32, int(round(w * s / 32)) * 32), max(32, int(round(h * s / 32)) * 32)


def model_matte(im, device):
    """What the model calls figure, 0..1, at the picture's own size."""
    import torch, torch.nn.functional as TF
    from torchvision import transforms
    from PIL import Image
    w, h = im.size
    tw, th = working_size(w, h)
    norm = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    x = norm(transforms.ToTensor()(im.convert("RGB").resize((tw, th), Image.BILINEAR))).unsqueeze(0).to(device)
    model = load_model(device)
    with torch.no_grad():
        out = model(x)
    p = (out[-1] if isinstance(out, (list, tuple)) else out).sigmoid().float().cpu()
    p = TF.interpolate(p, size=(h, w), mode="bilinear", align_corners=False)[0, 0].clamp(0, 1)
    del model, x, out
    if device == "mps":
        torch.mps.empty_cache()                    # hand the graphics memory back
    return p.numpy(), (tw, th)


def patches(mask, limit=6):
    """(count, pixels, the largest few as (pixels, x, y))"""
    import numpy as np
    from scipy import ndimage as ndi
    lab, n = ndi.label(mask, structure=np.ones((3, 3)))
    if not n:
        return 0, 0, []
    size = ndi.sum(mask, lab, index=np.arange(1, n + 1))
    where = ndi.find_objects(lab)
    big = [(int(size[i]), int((where[i][1].start + where[i][1].stop) // 2), int((where[i][0].start + where[i][0].stop) // 2))
           for i in np.argsort(-size)[:limit] if size[i] >= MIN_PATCH]
    return int(n), int(mask.sum()), big


def compare(alpha, matte):
    """The three questions. alpha: the cut-out's, 0..1. matte: the model's, 0..1."""
    import numpy as np
    from scipy import ndimage as ndi
    solid = alpha >= 0.5
    sure = ndi.binary_erosion(matte > SURE_IN, iterations=DEPTH)
    cut_off = sure & (alpha < 0.1)
    filled = ndi.binary_erosion(solid, iterations=DEPTH) & (matte < SURE_OUT)
    lab, n = ndi.label(alpha > 0, structure=np.ones((3, 3)))
    stray = faint = np.zeros_like(solid)
    if n:
        idx = np.arange(1, n + 1)
        unseen = ~(ndi.maximum(matte, lab, index=idx) > 0.5)
        shows = ndi.maximum(alpha, lab, index=idx) >= SHOWS
        stray = np.concatenate([[False], unseen & shows])[lab]
        faint = np.concatenate([[False], unseen & ~shows])[lab]
    return {"a piece cut off": patches(cut_off), "a gap left filled": patches(filled & ~stray),
            "stray marks": patches(stray), "fainter specks": patches(faint)}


def main(argv):
    matte_out = None
    if "--matte" in argv:
        i = argv.index("--matte")
        if i + 1 >= len(argv):
            raise SystemExit("--matte needs a file name")
        matte_out = os.path.expanduser(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    args = [a for a in argv if not a.startswith("--")]
    if len(args) not in (1, 2):
        print(__doc__); raise SystemExit(1)
    gone = missing()
    if gone:
        skip("The model is not on this machine: no %s in %s. Nothing was downloaded." % (", ".join(gone), MODEL_DIR))
    try:
        import warnings
        warnings.filterwarnings("ignore", category=FutureWarning)             # timm's notes about its own imports
        import torch, torchvision, safetensors, numpy as np, scipy           # noqa: F401
        from PIL import Image
    except ImportError:
        if os.path.exists(TORCH_PY) and os.path.realpath(sys.executable) != os.path.realpath(TORCH_PY):
            os.execv(TORCH_PY, [TORCH_PY, os.path.abspath(__file__)] + sys.argv[1:])
        skip("torch is needed to run the model, and ComfyUI's Python (%s) is not here or has none." % TORCH_PY)

    src = os.path.expanduser(args[0])
    im = Image.open(src)
    w, h = im.size
    if len(args) == 2:
        cut = np.asarray(Image.open(os.path.expanduser(args[1])).convert("RGBA"))
        if cut.shape[:2] != (h, w):
            raise SystemExit("cutcheck: the cut-out is %dx%d and the render %dx%d: give the cut-out at the render's "
                             "own size (tools/keyedge.py writes one)" % (cut.shape[1], cut.shape[0], w, h))
        what = os.path.basename(args[1])
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import keyedge
        try:
            cut, _ = keyedge.cut_file(src)
        except keyedge.NoHue as e:
            raise SystemExit("cutcheck: " + str(e))
        what = "the new edge's cut-out"
    alpha = cut[..., 3] / 255.0

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    t = time.time()
    matte, (tw, th) = model_matte(im, device)
    print("cutcheck  %s (%dx%d), %s; the model at %dx%d on %s in %.0fs"
          % (os.path.basename(src), w, h, what, tw, th, device, time.time() - t))
    if matte_out:
        Image.fromarray((matte * 255 + 0.5).astype(np.uint8)).save(matte_out)
        print("  the model's matte -> %s" % matte_out)
    got = compare(alpha, matte)
    for name, (n, px, big) in got.items():
        if name == "fainter specks":
            print("  %-18s %5d px in %d place(s), each under a tenth solid: they do not show" % (name, px, n))
            continue
        line = "  %-18s %5d px in %d place(s)" % (name, px, n)
        if big:
            line += ": " + ", ".join("%d px at (%d, %d)" % b for b in big)
        elif n:
            line += ", none as large as %d px" % MIN_PATCH
        print(line)
    print("  Each line is a place to look at on a close-up, not a verdict. Nothing was changed.")
    return got


if __name__ == "__main__":
    main(sys.argv[1:])

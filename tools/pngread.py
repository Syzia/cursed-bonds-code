"""Minimal PNG decoder so tools can read back their own renders."""
import zlib, struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img


def load(path):
    d = open(path, "rb").read()
    pos, w, h, ct, idat = 8, 0, 0, 6, b""
    while pos < len(d):
        ln = struct.unpack(">I", d[pos:pos+4])[0]
        tag = d[pos+4:pos+8]
        data = d[pos+8:pos+8+ln]
        if tag == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", data[:10])
        elif tag == b"IDAT":
            idat += data
        pos += 12 + ln
    raw = zlib.decompress(idat)
    ch = 4 if ct == 6 else 3
    im = Img(w, h, alpha=(ch == 4))
    stride = w * ch
    prev = bytearray(stride)
    o = 0
    for y in range(h):
        f = raw[o]; o += 1
        line = bytearray(raw[o:o+stride]); o += stride
        if f == 1:
            for i in range(ch, stride): line[i] = (line[i] + line[i-ch]) & 255
        elif f == 2:
            for i in range(stride): line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i-ch] if i >= ch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i-ch] if i >= ch else 0
                b = prev[i]; c = prev[i-ch] if i >= ch else 0
                p = a + b - c
                pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        im.buf[y*stride:(y+1)*stride] = line
        prev = line
    return im

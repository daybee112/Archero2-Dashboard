import numpy as np, colorsys
from PIL import Image
def feats(im):
    w, h = im.size; a = np.asarray(im.convert("RGB").resize((60, 72), Image.BILINEAR), dtype=float) / 255
    H, W = a.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]; xr, yr = xx / W, yy / H
    keep = (yr > 0.22) & (yr < 0.8) & (xr > 0.12) & (xr < 0.9) & ~((xr < 0.45) & (yr > 0.5))
    r, g, b = a[..., 0], a[..., 1], a[..., 2]; mx = a.max(axis=2); mn = a.min(axis=2); s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    hue = np.vectorize(lambda R, G, B: colorsys.rgb_to_hsv(R, G, B)[0] * 360)(r, g, b)
    bg = (s > 0.5) & ((hue > 290) | (hue < 15)) & (mx > 0.25) & (mx < 0.95)   # magenta/red tile background
    fg = keep & ~bg; n = fg.sum() + 1e-9
    gold = fg & (hue > 30) & (hue < 60) & (s > 0.45) & (mx > 0.45)
    blue = fg & (hue > 175) & (hue < 250) & (s > 0.25) & (mx > 0.4)
    silver = fg & (s < 0.22) & (mx > 0.6)
    dark = fg & (mx < 0.25)
    return dict(fg=round(fg.mean(), 2), gold=round(gold.sum() / n, 2), blue=round(blue.sum() / n, 2), silver=round(silver.sum() / n, 2), dark=round(dark.sum() / n, 2))

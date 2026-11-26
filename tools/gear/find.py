# Find gear tiles along a preset's gear row by their frame colour (magenta = Chaotic, red = Mythic).
import numpy as np, colorsys
from PIL import Image
def frame_mask(a):
    r, g, b = a[..., 0] / 255, a[..., 1] / 255, a[..., 2] / 255
    mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b); s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return (s > 0.5) & (mx > 0.35) & (r > g * 1.6) & (r >= b * 0.9)      # reds and magentas
def tiles(img, y0=1225, y1=1395):   # tiles sit on the cream panel: split the row at cream columns
    a = np.asarray(img.convert("RGB"), dtype=float)[y0:y1]
    cream = (a.min(axis=2) > 185) & (a[..., 0] - a[..., 2] < 60) & (a[..., 0] > 225)
    gap = cream.mean(axis=0) > 0.6; out = []; x = 0; W = len(gap)
    while x < W:
        if not gap[x]:
            s = x
            while x < W and not gap[x]: x += 1
            if 140 <= x - s <= 200: out.append((s, y0 - 15, x, y1 + 5))   # whole tiles only (the cut-off ones at the edges are skipped)
        x += 1
    return out
if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]: print(f, tiles(Image.open(f)))

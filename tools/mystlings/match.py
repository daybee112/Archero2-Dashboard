# Prototype of the on-device mystling reader (the dashboard's JS mirrors this).
#  find_in_use(img): the tile under the green "In use" label on a profile's Mystling tab
#  match(img, box): best reference by colour correlation of the tile's picture (frame and stars left out)
#  stars(img, box): the five stars by colour: cyan 1, yellow 2, red 3, pink 4, dark red 5, grey 0
import json, os, sys, colorsys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); APP = os.path.join(HERE, "..", "..", "app")
meta = json.load(open(os.path.join(APP, "mystling-refs.json"))); sheet = Image.open(os.path.join(APP, "mystling-refs.jpg")).convert("RGB")
def art(im):
    w, h = im.size; a = im.crop((int(w * .12), int(h * .12), int(w * .88), int(h * .70))).resize((32, 24), Image.BILINEAR)
    v = np.asarray(a, dtype=float).ravel(); v = v - v.mean(); return v / (np.linalg.norm(v) + 1e-9)
C = meta["cell"]; REFS = []
for k, r in enumerate(meta["refs"]):
    x, y = (k % meta["cols"]) * C, (k // meta["cols"]) * C; REFS.append((r["name"], r["look"], art(sheet.crop((x, y, x + C, y + C)))))
def match(img, box):
    x0, y0, x1, y1 = box; s = x1 - x0; best = None
    for dx in (-0.06, -0.03, 0, 0.03, 0.06):
        for dy in (-0.06, -0.03, 0, 0.03, 0.06):
            d = art(img.crop((int(x0 + dx * s), int(y0 + dy * s), int(x1 + dx * s), int(y1 + dy * s))))
            by = {}
            for n, l, R in REFS: sc = float(d @ R); by[n] = max(by.get(n, -1), sc)
            top = sorted(by.items(), key=lambda t: -t[1])
            if not best or top[0][1] > best[0][1]: best = top; bb = (int(x0 + dx * s), int(y0 + dy * s), int(x1 + dx * s), int(y1 + dy * s))
    return best[:3], bb
def is_empty(img, box):   # the empty egg slot on a preset: flat beige, low saturation
    a = np.asarray(img.crop(box).convert("HSV"), dtype=float); return a[..., 1].mean() < 115 and a[..., 2].mean() > 185
STAR = [("cyan", 1, 165, 200), ("yellow", 2, 35, 60), ("pink", 4, 290, 340)]
def stars(img, box):
    x0, y0, x1, y1 = box; w = x1 - x0; h = y1 - y0; out = []
    for k in range(5):
        cx, cy, r = x0 + (0.15 + 0.175 * k) * w, y0 + 0.84 * h, 0.04 * w
        px = np.asarray(img.crop((int(cx - r), int(cy - r), int(cx + r), int(cy + r))).convert("RGB"), dtype=float).reshape(-1, 3) / 255
        hsv = np.array([colorsys.rgb_to_hsv(*p) for p in px]); sat = hsv[(hsv[:, 1] > .35) & (hsv[:, 2] > .35)]
        if len(sat) < len(px) * .2: out.append(("grey", 0)); continue
        hue = float(np.median(sat[:, 0])) * 360; val = float(np.median(sat[:, 2]))
        if 255 <= hue <= 345: lab = ("pink", 4)                       # pink stars shade into cyan and white
        elif hue < 22 or hue > 345: lab = ("red", 3) if val > .72 else ("dark red", 5)
        elif 28 <= hue <= 65: lab = ("yellow", 2) if val > .8 else ("grey", 0)   # dull gold = a star not earned yet
        elif 140 <= hue <= 210: lab = ("cyan", 1)
        else: lab = ("?", None)
        out.append(lab)
    return out
def find_in_use(img):
    W, H = img.size; s = 300 / W; sm = img.resize((300, int(H * s))); a = np.asarray(sm, dtype=int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = (g > 170) & (r < 150) & (b < 150) & (g - r > 70); dark = a.max(axis=2) < 50
    ys, xs = np.nonzero(green); cand = []
    for y, x in zip(ys, xs):
        win = dark[max(0, y - 3):y + 4, max(0, x - 8):x + 9]
        if win.mean() > .3: cand.append((x, y))
    if len(cand) < 4: return None
    cx = np.median([c[0] for c in cand]) / s; cy = np.median([c[1] for c in cand]) / s
    hw, top, hgt = 0.0788 * W, 0.007 * W, 0.158 * W
    return (int(cx - hw), int(cy + top), int(cx + hw), int(cy + top + hgt))
if __name__ == "__main__":
    for f in ["fix-profile-1.png", "fix-profile-2.png"]:
        im = Image.open(os.path.join(HERE, f)).convert("RGB"); bx = find_in_use(im)
        m, b2 = match(im, bx); st = stars(im, b2)
        print(f, m, st, sum(v for _, v in st if v is not None))
        im.crop(b2).resize((120, 120)).save(os.path.join("/tmp", f + "-tile.png"))

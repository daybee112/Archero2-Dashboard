"""Prototype of the results reader's on-device sorting (resultsKind in app/index.html).

Usage: python3 tools/results/kind.py tests/fixtures/results/w1124-r1/*.png

Everything is placed from the window's blue title bar ("Details" or "Schedule"), in units of the image width:
- guild tabs at title + 0.16 W (x 0.29 / 0.71): the selected one is yellow (255, 231, 42), the other brown (165, 100, 71);
  on a Schedule screen both spots are the window's tan background.
- lane tabs at title + 1.25 W (x 0.225 / 0.5 / 0.775): the selected one is a little lighter (223, 173, 125 vs 215, 162, 113).
- Schedule flags at title + 0.52 W (battle 1) and + 0.885 W (battle 2), x 0.20 / 0.415 / 0.62: a red flag (right guild won
  the lane) has ~230 red pixels in the box, a blue one (left guild won) 0-5.
"""
import sys
from PIL import Image

def kind(path):
    im = Image.open(path).convert("RGB"); W, H = im.size
    at = lambda x, y: im.getpixel((min(W - 1, max(0, int(x))), min(H - 1, max(0, int(y)))))
    def avg(cx, cy, hw, hh):
        px = [at(x, y) for y in range(int(cy - hh), int(cy + hh) + 1, 2) for x in range(int(cx - hw), int(cx + hw) + 1, 2)]
        return [sum(p[i] for p in px) / len(px) for i in range(3)]
    ty = next((y for y in range(int(H * 0.08), int(H * 0.45)) if (lambda p: p[2] > 200 and p[1] > 150 and p[0] < 80)(at(W / 2, y))), None)
    if ty is None or ty + 1.26 * W >= H: return {"kind": "other"}
    u = W
    yellow = lambda p: p[0] > 225 and p[1] > 195 and p[2] < 110
    tabc = [avg(fx * W, ty + 0.16 * u, 0.03 * W, 0.008 * u) for fx in (0.29, 0.71)]; tabs = [yellow(p) for p in tabc]
    lanes = [avg(fx * W, ty + 1.25 * u, 0.04 * W, 0.006 * u) for fx in (0.225, 0.5, 0.775)]
    if not any(tabs) and all(p[0] > 205 and 150 < p[1] < 200 and 100 < p[2] < 150 for p in tabc):
        flags = []
        for dy in (0.52, 0.885):
            row = []
            for cx in (0.20, 0.415, 0.62):
                red = sum(1 for x in range(int((cx - 0.04) * W), int((cx + 0.04) * W), 2) for y in range(int(ty + (dy - 0.05) * u), int(ty + (dy + 0.04) * u), 2)
                          if (lambda p: p[0] > 190 and p[1] < 80 and p[2] < 80)(at(x, y)))
                row.append("right" if red > 40 else "left")
            flags.append(row)
        return {"kind": "schedule", "flags": flags}
    if tabs[0] == tabs[1]: return {"kind": "other"}
    br = [sum(p) for p in lanes]; top = max(br); rest = sorted(br)[:2]
    lane = ["left", "middle", "right"][br.index(top)] if top - rest[1] >= 12 else None
    return {"kind": "details", "side": 0 if tabs[0] else 1, "lane": lane}

if __name__ == "__main__":
    for f in sys.argv[1:]: print(f, kind(f))

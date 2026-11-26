import numpy as np
from PIL import Image, ImageFilter
import find
SLOTS = ["weapon", "armor", "ring", "helmet", "amulet", "boots"]          # order on a preset's gear row
PROFILE = {"weapon": (87, 495), "amulet": (87, 615), "ring": (87, 735), "helmet": (415, 495), "armor": (415, 615), "boots": (415, 735)}   # 590-wide profile Gear tab
def prof_box(slot, W=590): x, y = PROFILE[slot]; s = W / 590; return (int(x * s), int((y - 12) * s), int((x + 88) * s), int((y + 88) * s))
def art(im, mode):
    w, h = im.size; a = im.crop((int(w * .18), int(h * .2), int(w * .88), int(h * .72))).resize((36, 30), Image.BILINEAR)
    if mode == "rgb": v = np.asarray(a.convert("RGB"), dtype=float).ravel()
    elif mode == "edge": v = np.asarray(a.convert("L").filter(ImageFilter.FIND_EDGES), dtype=float).ravel()
    else:   # rgb with the background (quality colour) pushed to grey: keep only how far each pixel is from a red/magenta
        x = np.asarray(a.convert("RGB"), dtype=float); r, g, b = x[..., 0], x[..., 1], x[..., 2]
        bg = (r > g * 1.6) & (r > 90); x[bg] = 0; v = x.ravel()
    v = v - v.mean(); return v / (np.linalg.norm(v) + 1e-9)
REF = []
def addref(sett, slot, im, src): REF.append((sett, slot, im, src))
for slot in PROFILE:
    addref("Dragoon", slot, Image.open("profile-dragoon.png").convert("RGB").crop(prof_box(slot)), "profile")
    addref("Oracle", slot, Image.open("profile-oracle.png").convert("RGB").crop(prof_box(slot)), "profile")
ga = find.tiles(Image.open("griffin-preset-a.png")); gb = find.tiles(Image.open("griffin-preset-b.png"))
for k, slot in enumerate(SLOTS[:5]): addref("Griffin", slot, Image.open("griffin-preset-a.png").convert("RGB").crop(ga[k]), "preset")
addref("Griffin", "boots", Image.open("griffin-preset-b.png").convert("RGB").crop(gb[4]), "preset")
TRUTH = {"5": "w DDDDD", "11": "a DDDDD", "15.5": "w OOOOO", "20": "a DDDDD", "23.5": "a DDDDD", "29": "a DDDDD", "33": "a OOOOO", "37": "a DDDGD"}
full = {"D": "Dragoon", "O": "Oracle", "G": "Griffin"}
if __name__ == "__main__":
  for mode in ("rgb",):
    R = [(s, sl, art(im, mode)) for s, sl, im, _ in REF]; ok = n = 0; bad = []
    for t, tr in TRUTH.items():
        im = Image.open(f"/home/claude/vid-myst/pre_{t}.png").convert("RGB"); bx = find.tiles(im)
        start = 0 if tr[0] == "w" else 1
        for k, b in enumerate(bx):
            slot = SLOTS[start + k]; d = art(im.crop(b), mode)
            sc = sorted(((float(d @ v), s) for s, sl, v in R if sl == slot), reverse=True)
            n += 1; want = full[tr[2 + k]]
            if sc[0][1] == want: ok += 1
            else: bad.append((t, slot, want, [(s, round(x, 2)) for x, s in sc]))
    print(mode, ok, "/", n); [print("   ", b) for b in bad]

# Builds app/gear-refs.jpg + .json: one cell per reference gear tile (frame, S and Lv label included), 120x144, 10 per row,
# plus app/gear-digits.json (the +N badge digits as small yellow masks).
# Sources: the pilot profile video's Gear tabs (Dragoon: daybee, Oracle: second player), Daby's Team Info presets
# (Nov 25: daybee, Heynow Dragoon; Shoex, Archerojj Oracle; Gaga94's Griffin amulet) and his Griffin preset clip (Nov 25).
import json, os
import numpy as np
from PIL import Image
import find
HERE = os.path.dirname(os.path.abspath(__file__)); APP = os.path.join(HERE, "..", "..", "app")
SLOTS = ["weapon", "armor", "ring", "helmet", "amulet", "boots"]      # order along a preset's gear row
PROFILE = {"weapon": (87, 495), "amulet": (87, 615), "ring": (87, 735), "helmet": (415, 495), "armor": (415, 615), "boots": (415, 735)}
def prof_box(slot, W): x, y = PROFILE[slot]; s = W / 590; return (int(x * s), int((y - 12) * s), int((x + 88) * s), int((y + 88) * s))
O = lambda f: Image.open(os.path.join(HERE, f)).convert("RGB")
refs = []
for f, sett in (("profile-dragoon.png", "Dragoon"), ("profile-oracle.png", "Oracle")):
    im = O(f)
    for slot in PROFILE: refs.append((sett, slot, im.crop(prof_box(slot, im.size[0])), f))
def preset(f, sett, first, take):
    im = O(f); bx = find.tiles(im)
    for k, b in enumerate(bx):
        slot = SLOTS[first + k]
        if slot in take: refs.append((sett, slot, im.crop(b), f))
preset("preset-daybee.png", "Dragoon", 0, ["weapon", "armor", "ring", "helmet", "amulet"]); preset("preset-heynow.png", "Dragoon", 1, ["boots"])
preset("preset-shoex.png", "Oracle", 0, ["weapon", "armor", "ring", "helmet", "amulet"]); preset("preset-archerojj.png", "Oracle", 1, ["boots"])
preset("griffin-preset-a.png", "Griffin", 0, ["weapon", "armor", "ring", "helmet", "amulet"]); preset("griffin-preset-b.png", "Griffin", 1, ["boots"])
preset("preset-gaga94.png", "Griffin", 1, ["amulet"])
CW, CH, N = 120, 144, 10
sheet = Image.new("RGB", (CW * N, CH * ((len(refs) + N - 1) // N)), "black")
for k, (_, _, im, _) in enumerate(refs): sheet.paste(im.resize((CW, CH), Image.LANCZOS), ((k % N) * CW, (k // N) * CH))
sheet.save(os.path.join(APP, "gear-refs.jpg"), quality=92)
json.dump({"cw": CW, "ch": CH, "cols": N, "refs": [{"set": s, "slot": sl, "src": f} for s, sl, _, f in refs]}, open(os.path.join(APP, "gear-refs.json"), "w"), indent=1)
# digits: yellow strokes in the badge, from known Mythic+N tiles
def badge_mask(tile):
    w, h = tile.size; a = np.asarray(tile.crop((int(w * .40), int(h * .80), int(w * .66), int(h * .97))).resize((26, 17)), dtype=float) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]; return (r > .59) & (g > .47) & (b < .51) & (r - b > .24) & (g > r * .75)   # loose enough for small tiles; g/r keeps the orange diamond of a plain Mythic out
dig = {}
for f, first, labels in (("griffin-preset-a.png", 0, ["4", "3", "4", None, None]), ("griffin-preset-b.png", 1, ["3", "4", None, None, "3"]), ("preset-gaga94.png", 1, [None, None, "3", "2", None])):
    im = O(f)
    for b, lab in zip(find.tiles(im), labels):
        if lab and lab not in dig: dig[lab] = badge_mask(im.crop(b)).astype(int).tolist()
json.dump({"w": 26, "h": 17, "digits": dig}, open(os.path.join(APP, "gear-digits.json"), "w"))
print(len(refs), "refs;", sorted(dig))

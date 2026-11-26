# Builds app/mystling-refs.jpg + .json: one 120px cell per reference tile (the whole tile, frame and stars included).
# Sources: Daby's Mystling inventory video (Nov 25), a preset screen for the normal white Snow Owl, his Egg Demon screenshot.
import json, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); APP = os.path.join(HERE, "..", "..", "app")
cols = [(50, 286), (337, 573), (625, 861), (916, 1152)]; rows = [(1158, 1392), (1497, 1731), (1835, 2069)]
def inv(f, c, r): x0, x1 = cols[c]; y0, y1 = rows[r]; return Image.open(os.path.join(HERE, f)).crop((x0, y0, x1, y1))
REFS = [
    ("Queen Medusa", "normal", inv("full_5.png", 0, 0)),
    ("Fool", "normal", inv("full_1.png", 1, 0)),
    ("Death Mage", "normal", inv("full_10.png", 0, 0)),
    ("Witch", "normal", inv("full_17.png", 0, 0)),
    ("Mr. Meeseeks", "normal", inv("full_14.png", 1, 0)),
    ("Nian Beast", "normal", inv("full_21.png", 0, 0)),
    ("Snow Owl", "variant", inv("full_21.png", 3, 2)),
    ("Snow Owl", "normal", Image.open(os.path.join(HERE, "pre_23.5.png")).crop((872, 744, 1026, 898))),
    ("Death Mage", "normal", Image.open(os.path.join(HERE, "pre_5.png")).crop((872, 744, 1026, 898))),
    ("Egg Demon", "normal", Image.open(os.path.join(HERE, "egg-demon-screenshot.png")).crop((627, 1157, 863, 1393))),
]
C, N = 120, 10
sheet = Image.new("RGB", (C * N, C * ((len(REFS) + N - 1) // N)), "black")
for k, (_, _, im) in enumerate(REFS): sheet.paste(im.convert("RGB").resize((C, C), Image.LANCZOS), ((k % N) * C, (k // N) * C))
sheet.save(os.path.join(APP, "mystling-refs.jpg"), quality=92)
json.dump({"cell": C, "cols": N, "refs": [{"name": n, "look": l} for n, l, _ in REFS]}, open(os.path.join(APP, "mystling-refs.json"), "w"), indent=1)
print(len(REFS), "refs")

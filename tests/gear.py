import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
FIX = _os.path.join(HERE, "fixtures", "gear")
# Gear read on the device: set from the piece's colours + picture against gear-refs.jpg, quality from the frame colour and the +N digit.
# Expected values checked by eye. Presets: Zeuzo (11, rainbow Dragoon pieces), Venom17 (23.5), DrShabz (29), Gaga94 (37, Mythic and a
# Griffin amulet) from Daby's Nov 25 Team Info video; his Griffin clip (a, b). Profiles: the pilot video's Gear tabs.
import asyncio, threading, http.server, functools, base64
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8809), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
BOXES = {"griffin-preset-a": [[131, 1210, 292, 1400], [314, 1210, 476, 1400], [498, 1210, 659, 1400], [684, 1210, 841, 1400], [868, 1210, 1024, 1400]], "griffin-preset-b": [[127, 1210, 289, 1400], [311, 1210, 472, 1400], [497, 1210, 653, 1400], [681, 1210, 837, 1400], [862, 1210, 1023, 1400]], "preset-11": [[156, 1210, 313, 1400], [340, 1210, 496, 1400], [523, 1210, 679, 1400], [707, 1210, 863, 1400], [890, 1210, 1047, 1400]], "preset-23.5": [[156, 1210, 313, 1400], [340, 1210, 496, 1400], [523, 1210, 680, 1400], [707, 1210, 863, 1400], [890, 1210, 1047, 1400]], "preset-29": [[156, 1210, 313, 1400], [340, 1210, 496, 1400], [523, 1210, 680, 1400], [707, 1210, 863, 1400], [890, 1210, 1047, 1400]], "preset-37": [[155, 1210, 314, 1400], [340, 1210, 496, 1400], [521, 1210, 682, 1400], [704, 1210, 866, 1400], [890, 1210, 1047, 1400]]}
SLOTS = ["weapon", "armor", "ring", "helmet", "amulet", "boots"]
PRESET = {   # file: (first slot, [(set, quality) per tile])
  "griffin-preset-a": (0, [("Griffin", "Mythic+4"), ("Griffin", "Mythic+3"), ("Griffin", "Mythic+4"), ("Griffin", "Chaotic"), ("Griffin", "Chaotic")]),
  "griffin-preset-b": (1, [("Griffin", "Mythic+3"), ("Griffin", "Mythic+4"), ("Griffin", "Chaotic"), ("Griffin", "Chaotic"), ("Griffin", "Mythic+3")]),
  "preset-11": (1, [("Dragoon", "Chaotic")] * 5),
  "preset-23.5": (1, [("Dragoon", "Chaotic")] * 5),
  "preset-29": (1, [("Dragoon", "Chaotic")] * 5),
  "preset-37": (1, [("Dragoon", "Mythic"), ("Dragoon", "Chaotic"), ("Dragoon", "Mythic+3"), ("Griffin", "Mythic+2"), ("Dragoon", "Chaotic")]),
}
PROFILE = {"profile-dragoon.png": "Dragoon", "profile-oracle.png": "Oracle"}
B64 = lambda f: base64.b64encode(open(_os.path.join(FIX, f), "rb").read()).decode()
BLOB = "const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0)); const blob = new Blob([bin]);"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs = []
        c = await b.new_context(); await c.add_init_script("window.__expose = true;" + MOCK)
        pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8809/index.html#roster"); await pg.wait_for_timeout(2500)
        for f, sett in PROFILE.items():
            r = await pg.evaluate("async (b64) => { " + BLOB + " return await window.__readGear(blob); }", B64(f))
            got = {k: (v["set"], v["q"]) for k, v in (r or {}).get("slots", {}).items()}
            check(f"{f}: all six read as {sett}, Chaotic", r and all(v == (sett, "Chaotic") for v in got.values()) and len(got) == 6, str(got))
        wrong = []; n = 0
        for f, (first, want) in PRESET.items():
            data = B64(f + ".jpg")
            for k, (bx, (ws, wq)) in enumerate(zip(BOXES[f], want)):
                slot = SLOTS[first + k]; n += 1
                r = await pg.evaluate("async ([b64, box, slot]) => { " + BLOB + " return await window.__gearTile(blob, box, slot); }", [data, bx, slot])
                if (r["set"], r["q"]) != (ws, wq): wrong.append((f, slot, (ws, wq), (r["set"], r["q"], r["margin"])))
        check(f"preset tiles: set and quality right on all {n}", not wrong, str(wrong))
        r = await pg.evaluate("async (b64) => { " + BLOB + " return await window.__readGear(blob); }", B64("preset-11.jpg"))
        check("a screen that isn't a Gear tab gives nothing, not a guess", r is None, str(r)[:200])
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

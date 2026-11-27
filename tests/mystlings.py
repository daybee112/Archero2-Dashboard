import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
FIX = _os.path.join(HERE, "fixtures", "mystlings")
# Mystlings matched on the device against mystling-refs.jpg, stars read by colour (cyan 1, yellow 2, red 3, pink 4, dark red 5).
# Expected values checked by eye: two profile Mystling tabs from the pilot video, seven preset screens from Daby's Nov 25 Team Info video.
import asyncio, threading, http.server, functools, base64
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8808), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
PROFILE = {"fix-profile-1.png": ("Death Mage", 9), "fix-profile-2.png": ("Death Mage", 18)}   # 4 yellow + 1 cyan; 3 pink + 2 red
BOX = [872, 744, 1026, 898]   # the mystling tile on a preset screen (1180-wide recording)
PRESET = {"preset-5.jpg": "Death Mage", "preset-15.5.jpg": "Queen Medusa", "preset-20.jpg": "Death Mage", "preset-23.5.jpg": "Snow Owl",
          "preset-29.jpg": "Snow Owl", "preset-37.jpg": "Egg Demon", "preset-33.jpg": None}   # 33: empty egg slot
B64 = lambda f: base64.b64encode(open(_os.path.join(FIX, f), "rb").read()).decode()
BLOB = "const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0)); const blob = new Blob([bin]);"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs = []
        c = await b.new_context(); await c.add_init_script("window.__expose = true;" + MOCK)
        pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8808/index.html#roster"); await pg.wait_for_timeout(2500)
        for f, (name, stars) in PROFILE.items():
            r = await pg.evaluate("async (b64) => { " + BLOB + " return await window.__readMystling(blob); }", B64(f))
            check(f"{f}: found the In use tile and matched {name}", r and r["found"] and r["name"] == name, str(r))
            check(f"{f}: stars by colour = {stars}", r and r.get("stars") == stars, str(r and r.get("starCols")))
        for f, name in PRESET.items():
            r = await pg.evaluate("async ([b64, box]) => { " + BLOB + " return await window.__matchMystTile(blob, box); }", [B64(f), BOX])
            ok = r["score"] >= 0.8 and r["score"] - r["second"] >= 0.1
            if name: check(f"{f}: {name}", ok and r["name"] == name, str(r))
            else: check(f"{f}: empty slot isn't passed off as a mystling", not ok, str(r))
        r = await pg.evaluate("async ([b64, box]) => { " + BLOB + " return await window.__matchMystTile(blob, box); }", [B64("flame-demon.jpg"), [155, 932, 411, 1194]])
        check("Flame Demon (DrFuko's) matched", r["name"] == "Flame Demon" and r["score"] >= 0.8, str(r))
        # a screen with no In use label (an artifact page) gives "not found", not a guess
        r = await pg.evaluate("async (b64) => { " + BLOB + " return await window.__readMystling(blob); }", B64("preset-5.jpg"))
        check("no In use label: not found", r and r["found"] is False, str(r))
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

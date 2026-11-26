import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
# Mystlings use the in-game names (Fool, Snow Owl); old saves with The Fool / Snowy Owl are read as the new names.
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8807), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
# an old inventory saved with the old names
PRE = {"inventory/m-tuup": {"memberId": "m-tuup", "ign": "Tuup", "inv": {"chars": {}, "gear": {}, "runes": {}, "mystlings": {"The Fool": 8, "Snowy Owl": 3, "Witch": 2}}, "at": 1, "by": "x", "byOfficer": True, "v": 3}}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs = []
        c = await b.new_context(viewport={"width": 1200, "height": 900})
        await c.add_init_script(MOCK + "window.__preseed = " + json.dumps(PRE) + ";")
        pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8807/index.html#roster"); await pg.wait_for_timeout(3000)
        d = await pg.evaluate("fetch('build-data.json').then(r=>r.json())")
        names = [m["name"] for m in d["mystlings"]]
        check("in-game names, plus Mr. Meeseeks and Egg Demon", names == ["Witch", "Fool", "Queen Medusa", "Nian Beast", "Death Mage", "Snow Owl", "Mr. Meeseeks", "Egg Demon"], str(names))
        txt = await pg.inner_text("body")
        check("old names don't show anywhere on the roster", "The Fool" not in txt and "Snowy Owl" not in txt)
        # Tuup's saved preset says "The Fool": the profile shows Fool
        await pg.click("#view-roster >> text=Tuup >> nth=0"); await pg.wait_for_timeout(1200)
        t = await pg.inner_text("body")
        check("Tuup's preset mystling shows as Fool", "Fool" in t and "The Fool" not in t, t[t.find("ystling"):t.find("ystling") + 80] if "ystling" in t else "")
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

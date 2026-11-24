import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
FIX = _os.path.join(HERE, "fixtures", "runes")
# Rune icons matched on the device against rune-refs.jpg. Expected names checked by eye against the screenshots
# (None = should stay blank: a rune with no reference yet, or too close to call).
import asyncio, threading, http.server, functools, base64
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8798), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
EXPECT = {
  "preset-hago26.png": ("preset", ["Sharp Arrow", "Giant Meteor", "Sprite Link", "Sprite Multishot", "Revive", "Lucky Shadow", "Arrow of Echoes", "Sprite's Awe", None,
                                   "Melee Sprite", "Arrow Rain", "Healing Sprite", "Star of Fury"]),
  "preset-silverscope.png": ("preset", ["Frostshock Seal", "Sharp Arrow", "Sawblade Circle", "Spin SPD Up", "Revive", "Guardian", "Arrow of Echoes", "Pulsing Orb", "Elemental Crit",
                                        "Frostshock Touch", "Arrow Rain", "Ring of Agony", "Circle"]),
  "profile-daybee-small.jpg": ("profile", ["Sprite Multishot", "Sprite Link", "Sharp Arrow", "Flamenox Seal", "Revive", "Lucky Shadow", "Sprite Assist", "Sprite's Awe", "Arrow of Echoes",
                                           "Melee Sprite", "Healing Sprite", "Arrow Rain", "Flamenox Touch"]),
  # other players' profiles from the pilot video (blue window, character and glow in front of some runes); not used as references
  "profile-video-12.jpg": ("profile", ["Dragonflight Sword", "Sawblade Circle", "Potion Magnet", "Spin SPD Up", "Revive", "Lucky Shadow", "Pulsing Orb", None, "Swordstrike Aerie",
                                       "Circle", "Ring of Agony", "Sword of Time", "Arrow Rain"]),
  "profile-video-27.jpg": ("profile", ["Sharp Arrow", "Frostshock Seal", "Potion Magnet", "Flamenox Seal", "Revive", "Lucky Shadow", "Arrow of Echoes", "Elemental Crit", "Sprite's Awe",
                                       None, "Arrow Rain", "Flamenox Touch", "Frostshock Touch"]),
  "profile-video-35.jpg": ("profile", ["Sharp Arrow", "Sprite Link", "Potion Magnet", "Sprite Multishot", "Intelligence", "Rabbit's Foot", "Arrow of Echoes", "Sprite's Awe", "Sprite Assist",
                                       "Arrow Rain", "Ring of Agony", "Melee Sprite", "Healing Sprite"]),
  "profile-video-45.jpg": ("profile", ["Sharp Arrow", "Potion Magnet", "Frostshock Seal", "Sprite Multishot", "Revive", "Guardian", None, "Sprite's Awe", "Arrow of Echoes",
                                       "Arrow Rain", "Melee Sprite", "Frostshock Touch", "Healing Sprite"]),
}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs = []
        c = await b.new_context(); await c.add_init_script("window.__expose = true;" + MOCK)
        pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8798/index.html#roster"); await pg.wait_for_timeout(2500)
        for f, (layout, names) in EXPECT.items():
            data = base64.b64encode(open(_os.path.join(FIX, f), "rb").read()).decode()
            r = await pg.evaluate("async (b64) => { const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0)); return await window.__readRunes(new Blob([bin])); }", data)
            got = [s["name"] for s in r["slots"]] if r else []
            check(f"{f}: layout {layout}", r and r["layout"] == layout)
            wrong = [(e, g) for e, g in zip(names, got) if g is not None and g != e]
            check(f"{f}: no wrong names", not wrong, str(wrong))
            known = sum(1 for e, g in zip(names, got) if g is not None and g == e)
            need = 10 if f.startswith("profile-video") else 11
            check(f"{f}: at least {need} of 13 read", known >= need, f"{known} read; blanks at {[i for i, g in enumerate(got) if g is None]}")
            if f == "preset-hago26.png":
                check("Mythic tier from the red frame (Sharp Arrow, Arrow Rain)", r["slots"][0]["q"] == "Mythic" and r["slots"][10]["q"] == "Mythic", str([s["q"] for s in r["slots"]]))
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

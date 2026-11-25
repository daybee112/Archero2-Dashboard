import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
FIX = _os.path.join(HERE, "fixtures", "matchup")   # Daby's Nov 24 matchup + Schedule tabs
# New week: read the matchup and schedule screenshots into editable fields, then create the week and its guilds.
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8804), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
READ = {"guilds": [{"name": "ArchAcademy", "power": "390.45M"}, {"name": "Unity", "power": "1.19B"}, {"name": "용기사", "power": "715.16M"}, {"name": "그랑", "power": "655.42M"}],
        "rounds": [{"n": 1, "opponent": "Unity", "starts_in": "02d 05h", "other": ["용기사", "그랑"]},
                   {"n": 2, "opponent": "그랑", "starts_in": "03d 05h", "other": ["용기사", "Unity"]},
                   {"n": 3, "opponent": "용기사", "starts_in": "04d 05h", "other": ["Unity", "그랑"]}]}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs = []
        c = await b.new_context(viewport={"width": 390, "height": 844})
        await c.add_init_script(MOCK + "window.__sampleImpl = async (prompt, opts) => { window.__nwImgs = (opts.images || []).length; window.__nwPrompt = prompt; return { text: JSON.stringify(" + json.dumps(READ) + ") }; };")
        pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8804/index.html#expedition"); await pg.wait_for_timeout(2500)
        await pg.click("#exp-new-week"); await pg.wait_for_timeout(100)
        check("Read is off until screenshots are picked", await pg.is_disabled("#exp-new-week-box >> text=Read screenshots"))
        await pg.set_input_files("#nw-files", [_os.path.join(FIX, f) for f in ("main.jpg", "r1.jpg", "r2.jpg", "r3.jpg")])
        check("thumbnails shown", await pg.locator("#exp-new-week-box img").count() == 4)
        await pg.click("#exp-new-week-box >> text=Read screenshots"); await pg.wait_for_timeout(500)
        check("all 4 screenshots sent in one call", await pg.evaluate("window.__nwImgs") == 4)
        vals = await pg.eval_on_selector_all("#exp-new-week-box tbody input", "i=>i.map(x=>x.value)")
        print(vals)
        check("opponents and powers filled in by round", vals[0] == "Unity" and vals[1] == "1.19B" and vals[3] == "그랑" and vals[4] == "655.42M" and vals[6] == "용기사" and vals[7] == "715.16M")
        check("round dates from the countdowns, in order", all(len(v) == 10 for v in (vals[2], vals[5], vals[8])) and vals[2] < vals[5] < vals[8], str(vals[2::3]))
        t = await pg.inner_text("#exp-new-week-box")
        check("says 3 of 3 rounds filled", "3 of 3 rounds filled in" in t)
        check("new guilds named", "New guilds: Unity, 그랑, 용기사" in t, t[-200:])
        await pg.fill("#exp-new-week-box tbody tr:nth-child(1) td:nth-child(3) input", "1.2B")   # a correction
        await pg.click("#exp-new-week-box >> text=Create week"); await pg.wait_for_timeout(800)
        w = await pg.evaluate("window.__store.get('expedition/2026-11-24')")
        check("week saved under its Tuesday id", w is not None, str(w)[:200])
        g = {x["guild"]: x.get("power") for x in (w or {}).get("group", [])}
        check("group powers saved, correction kept (1.2B = 1200M)", g == {"ArchAcademy": 390.45, "Unity": 1200, "그랑": 655.42, "용기사": 715.16}, str(g))
        check("other matchups kept", (w or {}).get("otherMatches", {}).get("1") == ["용기사", "그랑"] or (w or {}).get("otherMatches", {}).get(1) == ["용기사", "그랑"], str((w or {}).get("otherMatches")))
        r1 = await pg.evaluate("window.__store.get('expedition/2026-11-24/rounds/1')")
        check("round 1 vs Unity with its date", r1 and r1["opponent"] == "Unity" and r1["date"] == vals[2], str(r1)[:200])
        opps = await pg.evaluate("Object.values(Object.fromEntries(window.__store)).filter(v=>v&&['Unity','그랑','용기사'].includes(v.name)).map(v=>[v.name,v.weeks,v.power])")
        check("each new guild gets a record with this week", sorted(o[0] for o in opps) == sorted(["Unity", "그랑", "용기사"]) and all(o[1] == ["2026-11-24"] for o in opps), str(opps))
        sel = await pg.eval_on_selector("#exp-week", "s=>s.options[s.selectedIndex].text")
        check("the new week is selected and labeled by its Tuesday", sel.startswith("Week of Nov 24"), sel)
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

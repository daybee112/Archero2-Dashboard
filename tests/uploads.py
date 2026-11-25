import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
# Expedition > Uploads: officers only; one row per thing a week needs, with status; profile-video rows open the reader for the right guild.
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8805), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs = []
        c = await b.new_context(viewport={"width": 390, "height": 844}); await c.add_init_script(MOCK)
        pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8805/index.html#expedition"); await pg.wait_for_timeout(2500)
        check("officers see the Uploads sub-tab", await pg.is_visible("#exp-sub button[data-sub=uploads]"))
        # a fresh week
        await pg.click("#exp-new-week"); await pg.wait_for_timeout(100)
        for i, (n, pw) in enumerate([("Unity", "1.19B"), ("그랑", "655.42M"), ("Happiness", "340M")]):
            await pg.fill(f"#exp-new-week-box .nw-round:nth-child({i+1}) input >> nth=0", n)
            await pg.fill(f"#exp-new-week-box .nw-round:nth-child({i+1}) input >> nth=1", pw)
        await pg.click("#exp-new-week-box >> text=Create week"); await pg.wait_for_timeout(800)
        await pg.click("#exp-sub button[data-sub=uploads]"); await pg.wait_for_timeout(300)
        t = await pg.inner_text("#exp-uploads")
        check("title names the week", "Uploads for the week of Nov 24" in t, t[:80])
        tl = t.lower()
        check("sections in order", all(x in tl for x in ("this week", "our guild", "round 1 · vs unity", "round 2 · vs 그랑", "round 3 · vs happiness")) and tl.index("this week") < tl.index("our guild") < tl.index("round 1 · vs unity") < tl.index("round 2 · vs 그랑") < tl.index("round 3 · vs happiness"), t[:400])
        check("matchup saved (3 of 3 opponents)", "matchup and schedule" in tl and "saved" in tl.split("matchup and schedule")[1][:200])
        check("lanes/presets and results readers marked coming soon", tl.count("reader coming soon") == 6, str(tl.count("reader coming soon")))
        check("opponent rows not uploaded yet", tl.count("not uploaded") >= 4)
        # opens the reader pointed at Unity
        await pg.click("#exp-uploads tr:has-text('Unity roster and profiles') button"); await pg.wait_for_timeout(300)
        check("video reader opens inside Uploads", await pg.is_visible("#exp-uploads ~ * #vid-panel, #exp-uploads #vid-panel") or await pg.evaluate("!!document.querySelector('#exp-uploads #vid-panel')"))
        check("…pointed at Unity", await pg.eval_on_selector("#vid-target", "s=>s.value") == "Unity")
        # a finished read survives the list being redrawn when new data arrives
        await pg.evaluate("document.querySelector('#vid-result').append(Object.assign(document.createElement('div'), { id: 'fake-review', textContent: 'review here' }))")
        await pg.evaluate("""(async () => { const db = await window.claude.use('db'); await db.doc('opponents/o-4772616e67/scans/x').set({ date: '2026-11-20', players: [], v: 3 }); })()""")
        await pg.wait_for_timeout(600)
        check("review survives a redraw of the list", await pg.is_visible("#exp-uploads #fake-review"))
        await pg.click("#exp-uploads tr:has-text('Our roster and profiles') button"); await pg.wait_for_timeout(300)
        check("…or at our guild", await pg.eval_on_selector("#vid-target", "s=>s.value") == "__us")
        # leaving Uploads puts the reader back on the Roster
        await pg.click("#exp-sub button[data-sub=rounds]"); await pg.wait_for_timeout(200)
        check("reader returns to the Roster tab", await pg.evaluate("!!document.querySelector('#view-roster #vid-panel')"))
        # a scan dated this week marks the row saved
        await pg.evaluate("""(async () => { const db = await window.claude.use('db');
          await db.doc('opponents/o-556e697479/scans/2026-11-25').set({ date: '2026-11-25', source: 'profile video', players: [{ name: 'A' }, { name: 'B' }], v: 3 }); })()""")
        await pg.wait_for_timeout(500)
        await pg.click("#exp-sub button[data-sub=uploads]"); await pg.wait_for_timeout(300)
        row = await pg.inner_text("#exp-uploads tr:has-text('Unity roster and profiles')")
        check("a scan from this week marks it saved", "saved" in row.lower() and "2 players on 2026-11-25" in row, row)
        # members don't see Uploads
        c2 = await b.new_context(viewport={"width": 390, "height": 844}); await c2.add_init_script("window.__member = true;" + MOCK)
        p2 = await c2.new_page(); p2.on("pageerror", lambda e: errs.append(str(e)))
        await p2.goto("http://127.0.0.1:8805/index.html#expedition"); await p2.wait_for_timeout(2500)
        check("members don't see Uploads", await p2.is_hidden("#exp-sub button[data-sub=uploads]"))
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
# Roster Builds column: Main and Exp chips (complete / gaps / none), tap shows the gaps, a "missing a build" filter, sorting.
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8810), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
R = lambda n: {"name": n, "q": "Legendary"}
FULL = {"blessing": [R("Revive"), R("Guardian")], "enhancement": [R("Sharp Arrow"), R("Potion Magnet"), R("Flamenox Seal"), R("Frostshock Seal")],
        "ability": [R("Arrow Rain"), R("Ring of Agony"), R("Frostshock Touch"), R("Flamenox Touch")], "etched": [R("Arrow of Echoes"), R("Elemental Crit"), R("Elemental Domain")]}
G = {k: {"set": "Oracle", "q": "Chaotic"} for k in ["weapon", "amulet", "ring", "helmet", "armor", "boots"]}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs = []
        c = await b.new_context(viewport={"width": 1300, "height": 900}); await c.add_init_script(MOCK); pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8810/index.html#roster"); await pg.wait_for_timeout(2500)
        # give SilverScope a complete main build and Expedition preset
        await pg.evaluate("""(async ([g, r]) => { const db = await window.claude.use('db'); const ref = db.doc('roster/m-silverscope'); const m = window.__store.get('roster/m-silverscope') || {};
          await ref.set({ ...m, ign: 'SilverScope', mainBuild: { chars: [null, null, null], gear: g, runes: r, mystling: { name: 'Queen Medusa', stars: 12 }, date: '2026-11-25' },
            preset: { chars: [{ name: 'Phynx' }, { name: 'Cleo' }, { name: 'Thor' }], gear: g, runes: r, mystling: { name: 'Queen Medusa', stars: 12 }, behavior: { range: 'Mid', movement: 'Balanced' } }, v: 3 }); })""", [G, FULL])
        await pg.wait_for_timeout(800)
        row = lambda n: pg.locator(f"#roster-body tr:has-text('{n}')").first
        t = await row("SilverScope").inner_text()
        check("complete builds show two ticks", "✓ Main" in t and "✓ Exp" in t, t)
        t = await row("daybee").inner_text()
        check("daybee: no main build (✗) and an Expedition preset with gaps (◐)", "✗ Main" in t and "◐ Exp" in t, t)
        await row("daybee").locator("button:has-text('Exp')").click(); await pg.wait_for_timeout(200)
        t = await row("daybee").inner_text()
        check("tapping a chip lists the gaps", "no runes" in t, t)
        await pg.check("#roster-missing"); await pg.wait_for_timeout(300)
        names = await pg.eval_on_selector_all("#roster-body tr b", "x=>x.map(e=>e.textContent)")
        check("missing-a-build filter hides SilverScope, keeps daybee", "SilverScope" not in names and "daybee" in names, str(len(names)))
        await pg.uncheck("#roster-missing")
        await pg.click("#roster-head button:has-text('Builds')"); await pg.wait_for_timeout(300)
        first = await pg.eval_on_selector_all("#roster-body tr b", "x=>x.slice(0,3).map(e=>e.textContent)")
        check("sorting by Builds puts the least complete first", "SilverScope" not in first, str(first))
        check("no page errors", not errs, str(errs[:2]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

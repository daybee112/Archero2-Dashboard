import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
GEAR = _os.path.join(HERE, "..", "tools", "gear")          # Daby's full-size preset screenshots (Nov 25)
FX = _os.path.join(HERE, "fixtures")
# Edit screens: pick a build (Expedition preset or Main build) and fill it from 1-2 screenshots. Officers save to the roster,
# members save their own builds through their own record (main build included). The old standalone button is gone.
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8817), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
def sample(answers):
    return "window.__script = " + json.dumps(answers) + """;
window.__sampleImpl = async (prompt, opts) => { const nums = (prompt.match(/screens ([\\d, ]+), in this order/) || [])[1].split(',').map(x => +x.trim());
  return { text: JSON.stringify({ screens: nums.map(i => ({ i, ...(window.__script[i] || { type: 'other' }) })) }) }; };"""
PRE = lambda c: {"type": "preset", "chars": c, "behavior": {"range": "Long", "movement": "Balanced"}}
val = lambda pg, i: pg.evaluate(f"document.getElementById('{i}') ? document.getElementById('{i}').value : null")
cls = lambda pg, i: pg.evaluate(f"document.getElementById('{i}') ? document.getElementById('{i}').className : ''")
async def open_member(pg, who):
    await pg.fill("#roster-search", who); await pg.wait_for_timeout(200); await pg.click("#roster-body tr:first-child"); await pg.wait_for_timeout(400)
async def read(pg, pre, files, build="exp"):
    await pg.click(f"#member-panel .bseg button[data-build={build}]"); await pg.wait_for_timeout(100)
    for k, f in enumerate(files): await pg.set_input_files(f"#{pre}-shot{k + 1}", f)
    await pg.click(f"#{pre}-shot-read")
    await pg.wait_for_function(f"/Filled|Couldn't|doesn't look|went wrong|Pick a/.test(document.getElementById('{pre}-shot-status').textContent)", timeout=120000)
    return await pg.inner_text(f"#{pre}-shot-status")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs = []
        # ---- officer: Gaga94's Expedition preset from his preset screenshot ----
        c = await b.new_context(viewport={"width": 390, "height": 844}); await c.add_init_script("window.__expose = true;" + MOCK + sample({"1": PRE(["Helix", "Hela", "Thor"])}))
        pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8817/index.html#roster"); await pg.wait_for_timeout(2500)
        await open_member(pg, "gaga94")
        check("the old standalone button is gone", await pg.locator("#btn-preset-shot").count() == 0)
        await pg.click("#member-panel >> text=Edit"); await pg.wait_for_timeout(300)
        check("Edit has the build switch and the screenshot box", await pg.is_visible("#member-panel .bseg") and await pg.is_visible("#me-shots"))
        check("the usual edit fields are still there", all([await pg.is_visible(f"#{i}") for i in ("me-rank", "me-power", "me-myth", "me-notes")]))
        before_w = await val(pg, "me-g-weapon")
        st = await read(pg, "me", [_os.path.join(GEAR, "preset-gaga94.png")])
        check("read the preset screenshot", st.startswith("Filled"), st)
        check("characters from Claude", [await val(pg, f"me-c{i}") for i in range(3)] == ["Helix", "Hela", "Thor"])
        check("mystling matched on the device", await val(pg, "me-myst") == "Egg Demon", await val(pg, "me-myst"))
        check("gear matched: helmet Dragoon Mythic+3, amulet Griffin Mythic+2", [await val(pg, "me-g-helmet"), await val(pg, "me-gq-helmet"), await val(pg, "me-g-amulet"), await val(pg, "me-gq-amulet")] == ["Dragoon", "Mythic+3", "Griffin", "Mythic+2"],
              str([await val(pg, "me-g-helmet"), await val(pg, "me-gq-helmet"), await val(pg, "me-g-amulet"), await val(pg, "me-gq-amulet")]))
        check("weapon off the screenshot: kept what was there", await val(pg, "me-g-weapon") == before_w, f"{before_w} -> {await val(pg, 'me-g-weapon')}")
        check("range and movement", [await val(pg, "me-range"), await val(pg, "me-move")] == ["Long", "Balanced"])
        check("filled fields are marked", "fromshot" in await cls(pg, "me-g-helmet") and "fromshot" in await cls(pg, "me-myst") and "fromshot" not in await cls(pg, "me-g-weapon"))
        check("fits a phone (no sideways scroll)", await pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"))
        await pg.click("#member-panel button:text-is('Save')"); await pg.wait_for_timeout(2500)
        d = await pg.evaluate("window.__store.get('roster/m-gaga94')") or {}
        pr = d.get("preset", {})
        check("saved as the Expedition preset", [x and x.get("name") for x in pr.get("chars", [])] == ["Helix", "Hela", "Thor"] and (pr.get("gear") or {}).get("helmet", {}).get("q") == "Mythic+3" and (pr.get("mystling") or {}).get("name") == "Egg Demon", json.dumps(pr)[:240])
        check("source is a preset screenshot", d.get("presetSrc") == "preset screenshot")
        acts = await pg.evaluate("JSON.stringify([...window.__store.entries()].filter(([k]) => k.startsWith('audit/')))")
        check("in the Activity log, marked from screenshots", "Gaga94: " in acts and "(from screenshots)" in acts)
        # ---- officer: a main build from the profile's Gear tab and Runes tab ----
        await open_member(pg, "gaga94"); await pg.click("#member-panel >> text=Edit"); await pg.wait_for_timeout(300)
        st = await read(pg, "me", [_os.path.join(FX, "gear", "profile-oracle.png"), _os.path.join(FX, "runes", "profile-daybee-small.jpg")], "main")
        check("main build: read the Gear and Runes tabs", st.startswith("Filled"), st)
        check("main build: gear from the Gear tab (all Oracle)", all([await val(pg, f"me-g-{s}") == "Oracle" for s in ("weapon", "armor", "ring", "helmet", "amulet", "boots")]), str([await val(pg, f"me-g-{s}") for s in ("weapon", "armor")]))
        check("main build: runes from the Runes tab", await val(pg, "me-r-enhancement-0") == "Sprite Multishot" and await val(pg, "me-r-blessing-1") == "Lucky Shadow", str([await val(pg, "me-r-enhancement-0"), await val(pg, "me-r-blessing-1")]))
        await pg.click("#member-panel .bseg button[data-build=exp]"); await pg.wait_for_timeout(100)
        check("switching back shows the Expedition preset untouched", await val(pg, "me-g-helmet") == "Dragoon")
        await pg.click("#member-panel button:text-is('Save')"); await pg.wait_for_timeout(2500)
        d = await pg.evaluate("window.__store.get('roster/m-gaga94')") or {}
        mb = d.get("mainBuild") or {}
        check("main build saved, Expedition preset left alone", (mb.get("gear") or {}).get("boots", {}).get("set") == "Oracle" and (d.get("preset", {}).get("gear") or {}).get("helmet", {}).get("set") == "Dragoon" and mb.get("src") == "profile screenshots", json.dumps(mb)[:200])
        # ---- turned away: a Team Info screen as a preset ----
        await open_member(pg, "gaga94"); await pg.click("#member-panel >> text=Edit"); await pg.wait_for_timeout(300)
        await pg.evaluate("window.__script = { 1: { type: 'other' } }")
        st = await read(pg, "me", [_os.path.join(FX, "gear", "profile-oracle.png")])
        check("a non-preset screenshot is turned away for the Expedition preset", "doesn't look like a preset" in st or "Couldn't find a preset" in st, st)
        await c.close()
        # ---- member, linked to Shoex: fills their own main build ----
        mc = await b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        await mc.add_init_script("window.__member = true; window.__expose = true;" + MOCK + sample({"1": PRE(["Phynx", "Cleo", "Thor"])}))
        mp = await mc.new_page(); mp.on("pageerror", lambda e: errs.append(str(e)))
        await mp.goto("http://127.0.0.1:8817/index.html#roster"); await mp.wait_for_timeout(2500)
        await open_member(mp, "shoex"); await mp.click("text=This is me: link to my account"); await mp.wait_for_timeout(600)
        check("member: 'Edit my builds' on their own page", await mp.is_visible("#member-panel >> text=Edit my builds"))
        await mp.click("#member-panel >> text=Edit my builds"); await mp.wait_for_timeout(300)
        st = await read(mp, "mp", [_os.path.join(FX, "gear", "profile-oracle.png")], "main")
        check("member: main build gear read", st.startswith("Filled") and await val(mp, "mp-g-weapon") == "Oracle", st)
        await mp.click("#member-panel button:text-is('Save')"); await mp.wait_for_timeout(3000)
        sub = await mp.evaluate("window.__store.get('presets/u-member') || null") or {}
        check("member: main build saved to their own record", (sub.get("mainBuild") or {}).get("gear", {}).get("weapon", {}).get("set") == "Oracle" and sub.get("memberId") == "m-shoex", json.dumps(sub)[:200])
        check("member: the shared roster isn't written", not await mp.evaluate("!!window.__store.get('roster/m-shoex')"))
        log = await mp.evaluate("JSON.stringify([...window.__store.entries()].filter(([k]) => k.startsWith('presets/u-member')))")
        check("member: logged as updated own main build", "updated own main build" in log, log[-200:])
        await mp.wait_for_timeout(800)
        got = await mp.evaluate("((window.__memberGet('m-shoex') || {}).mainBuild || {}).src || null")
        check("member: the roster picks up their new main build", got == "profile screenshots", str(got))
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
GEAR = _os.path.join(HERE, "..", "tools", "gear")   # Daby's full-size preset screenshots (Nov 25)
# One member's Expedition preset from a screenshot, on their Roster page: Claude reads characters and behavior (scripted
# here), the device matches mystling, gear and runes; one review card; officers save to the roster, members through
# their own profile. Both are logged.
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8814), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
def sample(answers):   # by screenshot number
    return "window.__script = " + json.dumps(answers) + """;
window.__sampleImpl = async (prompt, opts) => { const nums = (prompt.match(/screens ([\\d, ]+), in this order/) || [])[1].split(',').map(x => +x.trim());
  return { text: JSON.stringify({ screens: nums.map(i => ({ i, ...(window.__script[i] || { type: 'other' }) })) }) }; };"""
PRE = lambda c: {"type": "preset", "chars": c, "behavior": {"range": "Long", "movement": "Balanced"}}
VALS = """() => Object.fromEntries([...document.querySelectorAll('#sp-result [data-f]')].filter(x => 'value' in x && x.type !== 'radio' && x.type !== 'checkbox').map(x => [x.dataset.f, x.value]))"""
async def open_member(pg, who):
    await pg.fill("#roster-search", who); await pg.wait_for_timeout(200); await pg.click("#roster-body tr:first-child"); await pg.wait_for_timeout(400)
async def read(pg, files):
    await pg.click("#btn-preset-shot"); await pg.set_input_files("#sp-file", files); await pg.click("#sp-read")
    await pg.wait_for_function("/Check it|went wrong|doesn't look|left out|isn't available/.test(document.querySelector('#sp-status').textContent)", timeout=120000)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs = []
        # 1. officer: Gaga94's preset (row scrolled to the armor; helmet Mythic+3, Griffin amulet Mythic+2, Egg Demon)
        c = await b.new_context(viewport={"width": 1200, "height": 900}); await c.add_init_script("window.__expose = true;" + MOCK + sample({"1": PRE(["Helix", "Hela", "Thor"])}))
        pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8814/index.html#roster"); await pg.wait_for_timeout(2500)
        await open_member(pg, "gaga94")
        check("officer: the button is on the member's page", await pg.is_visible("#member-panel #btn-preset-shot"))
        await read(pg, _os.path.join(GEAR, "preset-gaga94.png"))
        st = await pg.inner_text("#sp-status")
        check("read finished", "Check it" in st, st)
        check("one card, for this member", await pg.locator("#sp-result .vcard").count() == 1 and "Gaga94" in await pg.inner_text("#sp-result .vcard"))
        check("no lists or round in the single view", "Who's registered" not in await pg.inner_text("#sp-panel"))
        await pg.click("#sp-result [data-f=edit-gear]") if await pg.locator("#sp-result a[data-f=edit-gear]").is_visible() else None
        v = await pg.evaluate(VALS)
        check("characters from Claude", [v.get("c0"), v.get("c1"), v.get("c2")] == ["Helix", "Hela", "Thor"], str([v.get("c0"), v.get("c1"), v.get("c2")]))
        check("mystling matched on the device (Egg Demon)", v.get("myst") == "Egg Demon", v.get("myst"))
        check("range and movement", v.get("range") == "Long" and v.get("movement") == "Balanced")
        g = {s: (v.get(f"g-{s}-set"), v.get(f"g-{s}-q")) for s in ("armor", "helmet", "amulet")}
        check("gear matched, Mythic+N read at full size", g == {"armor": ("Dragoon", "Mythic"), "helmet": ("Dragoon", "Mythic+3"), "amulet": ("Griffin", "Mythic+2")}, str(g))
        check("boots read (the row is scrolled to the armor)", v.get("g-boots-set") == "Dragoon", v.get("g-boots-set"))
        check("weapon not on the screenshot: left blank (keeps what's on file)", v.get("g-weapon-set") == "", v.get("g-weapon-set"))
        await pg.click("#sp-save"); await pg.wait_for_timeout(2500)
        d = await pg.evaluate("window.__store.get('roster/m-gaga94')")
        pr = d.get("preset", {})
        check("saved as the Expedition preset", [x and x.get("name") for x in pr.get("chars", [])] == ["Helix", "Hela", "Thor"] and (pr.get("mystling") or {}).get("name") == "Egg Demon" and (pr.get("gear") or {}).get("helmet", {}).get("q") == "Mythic+3" and bool(((pr.get("gear") or {}).get("weapon") or {}).get("set")), json.dumps(pr)[:300])   # weapon not shown: kept, not blanked
        check("source is a preset screenshot", d.get("presetSrc") == "preset screenshot" and bool(d.get("presetDate")))
        check("panel closes after saving", not await pg.is_visible("#sp-panel"))
        acts = await pg.evaluate("JSON.stringify([...window.__store.entries()].filter(([k]) => k.startsWith('audit/')))")
        check("in the Activity log", "Gaga94: Expedition preset from a preset screenshot" in acts)
        # not a preset screen
        await pg.evaluate("window.__script = { 1: { type: 'other' } }")
        await read(pg, _os.path.join(GEAR, "profile-oracle.png"))
        check("a non-preset screenshot is turned away", "doesn't look like a preset" in await pg.inner_text("#sp-status"), await pg.inner_text("#sp-status"))
        await pg.click("#sp-panel >> text=Close")
        check("Close removes the panel", not await pg.is_visible("#sp-panel"))
        await c.close()
        # 2. member, linked to Shoex: saves their own preset through their profile, on a phone
        mc = await b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        await mc.add_init_script("window.__member = true; window.__expose = true;" + MOCK + sample({"1": PRE(["Phynx", "Cleo", "Thor"])}))
        mp = await mc.new_page(); mp.on("pageerror", lambda e: errs.append(str(e)))
        await mp.goto("http://127.0.0.1:8814/index.html#roster"); await mp.wait_for_timeout(2500)
        await open_member(mp, "zeuzo")
        check("member: no button on someone else's page", await mp.locator("#member-panel #btn-preset-shot").count() == 0)
        await open_member(mp, "shoex")
        await mp.click("text=This is me: link to my account"); await mp.wait_for_timeout(600)
        check("member: the button is on their own page", await mp.is_visible("#member-panel #btn-preset-shot"))
        await read(mp, _os.path.join(GEAR, "preset-shoex.png"))
        v = await mp.evaluate(VALS)
        check("member: mystling and gear read", v.get("myst") == "Queen Medusa" and v.get("g-weapon-set") == "Oracle", str({k: v.get(k) for k in ("myst", "g-weapon-set", "g-weapon-q")}))
        check("member: fits a phone (no sideways scroll)", await mp.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))
        await mp.click("#sp-save"); await mp.wait_for_timeout(2500)
        sub = await mp.evaluate("window.__store.get('presets/u-member') || null") or {}
        check("member: saved to their own record", sub.get("memberId") == "m-shoex" and [x and x.get("name") for x in (sub.get("preset") or {}).get("chars", [])] == ["Phynx", "Cleo", "Thor"], json.dumps(sub)[:200])
        log = await mp.evaluate("JSON.stringify(window.__store.get('presets/u-member/log') || [...window.__store.entries()].filter(([k]) => k.startsWith('presets/u-member')))")
        check("member: logged as from a preset screenshot", "Shoex (from a preset screenshot)" in log, log[-300:])
        check("member: the shared roster isn't written", not await mp.evaluate("!!window.__store.get('roster/m-shoex')"))
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8784), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read(); res = []
# every entry in the month records under a path, oldest first
EV = lambda pre: f"[...window.__store.entries()].filter(([k])=>k.startsWith('{pre}/')).flatMap(([k,v])=>v.events||[]).sort((a,z)=>a.at-z.at)"
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        # --- officer: a roster gear edit is logged with before -> after and how
        oc = await b.new_context(accept_downloads=True); await oc.add_init_script(MOCK); pg = await oc.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8784/index.html#roster"); await pg.wait_for_timeout(1500)
        await pg.fill("#roster-search", "shoex"); await pg.wait_for_timeout(100)
        await pg.click("#roster-body tr:first-child .gchip:nth-child(1)"); await pg.wait_for_timeout(100)
        await pg.select_option("#gp-q", "Godforge ★2"); await pg.click("#gear-pop >> text=Save"); await pg.wait_for_timeout(700)
        evs = await pg.evaluate(EV("audit/u-officer/months"))
        ev = evs[-1] if evs else {}
        check("officer edit logged", ev.get("action") == "edited roster", str(ev)[:160])
        check("before -> after recorded, no noise", ev.get("changes") == ["preset.gear.weapon.q: Chaotic → Godforge ★2"], str(ev.get("changes"))[:200])
        check("how recorded (typed)", ev.get("src") == "typed")
        top = await pg.evaluate("JSON.stringify(window.__store.get('audit/u-officer'))")
        check("v8: entries go straight into a month record, audit/<id> is an empty marker", json.loads(top) == {"events": [], "v": 3, "movedAt": json.loads(top).get("movedAt")}, top[:120])
        # --- an older page left 400 entries in the single record: on the next visit they move into month records, nothing lost
        await pg.evaluate("""() => { const evs = []; for (let i = 0; i < 400; i++) evs.push({ at: Date.UTC(2026, 9, 1) + i * 60000, action: "old", detail: "e" + i }); window.__store.set('audit/u-officer', { events: evs, v: 2 }); }""")
        snap = await pg.evaluate("JSON.stringify(Object.fromEntries(window.__store))")
        oc2 = await b.new_context(accept_downloads=True); await oc2.add_init_script(f"window.__preseed = {snap};" + MOCK)
        pg = await oc2.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8784/index.html#roster"); await pg.wait_for_timeout(4500)
        await pg.fill("#roster-search", "shoex"); await pg.wait_for_timeout(100)
        await pg.click("#roster-body tr:first-child .gchip:nth-child(1)"); await pg.wait_for_timeout(100)
        await pg.select_option("#gp-q", "Godforge ★3"); await pg.click("#gear-pop >> text=Save"); await pg.wait_for_timeout(900)
        main_n = await pg.evaluate("window.__store.get('audit/u-officer').events.length")
        arch = await pg.evaluate("(window.__store.get('audit/u-officer/months/2026-10')||{events:[]}).events.length")
        total = len(await pg.evaluate(EV("audit/u-officer/months")))
        check("old entries moved into month records, nothing lost", main_n == 0 and arch == 400 and total == 402, f"main {main_n}, Oct {arch}, all {total}")
        # --- activity view
        await pg.click("#release-badge"); await pg.wait_for_timeout(500); await pg.click("#changes-sub button[data-sub=activity]"); await pg.wait_for_timeout(200)
        t = await pg.inner_text("#audit-body")
        check("activity shows how + changes count", "typed in the tool" in t and "change" in t, t[:200])
        check("every month loads with the page (no Older button)", await pg.is_hidden("#audit-older"))
        await pg.fill("#audit-q", "e17"); await pg.wait_for_timeout(200)
        check("…including October's", await pg.locator("#audit-body tr").count() >= 1); await pg.fill("#audit-q", "")
        await pg.select_option("#audit-kind", "edited roster"); await pg.wait_for_timeout(200)
        rows = await pg.locator("#audit-body tr").count()
        check("type filter (both roster edits, nothing lost)", rows == 2, str(rows))
        await pg.select_option("#audit-kind", ""); await pg.fill("#audit-q", "Godforge ★3"); await pg.wait_for_timeout(200)
        check("search finds text inside changes", await pg.locator("#audit-body tr").count() == 1)
        await pg.fill("#audit-q", "")
        async with pg.expect_download() as dl: await pg.click("#audit-csv")
        d = await dl.value; path = await d.path(); csv = open(path, encoding="utf-8-sig").read()
        check("CSV export has every entry + changes", csv.count("\n") >= 401 and "Godforge ★2" in csv and "screenshot" not in csv.split("\n")[0], f"{csv.count(chr(10))} lines")
        # --- tamper evidence: an officer's page copies member entries; later edits/removals by the member get flagged
        await pg.evaluate("""() => { window.__store.set('presets/u-member', { memberId: 'm-shoex', ign: 'Shoex', log: [
            { at: 1795300000000, action: 'updated own preset', detail: 'Shoex (from the Builds tab)', src: 'builds', changes: ['preset.gear.weapon.q: Chaotic → Godforge ★1'] },
            { at: 1795300100000, action: 'posted test', detail: 'Shoex · Main · 50K DPS (id x1)', src: 'typed' } ] }); window.__fire(); }""")
        await pg.evaluate("window.__store.get('audit/u-officer')")  # noop
        await pg.wait_for_timeout(1200)
        a = len([e for e in await pg.evaluate(EV("audit/u-officer/months")) if e.get("mirrorOf")])
        check("officer page copied the member's entries (from an older-style record)", a == 2, str(a))
        await pg.evaluate("""() => { const d = window.__store.get('presets/u-member'); d.log = [ { ...d.log[0], changes: ['preset.gear.weapon.q: Chaotic → Godforge ★9'] } ]; window.__store.set('presets/u-member', d); window.__fire(); }""")
        await pg.wait_for_timeout(1200); await pg.click("#release-badge"); await pg.wait_for_timeout(500); await pg.click("#changes-sub button[data-sub=activity]"); await pg.wait_for_timeout(200)
        t = await pg.inner_text("#audit-body")
        check("edited member entry flagged, original shown", "Changed in the member's own record" in t and "Godforge ★9" in t, "")
        check("removed member entry flagged", "Removed from the member's own record" in t and "50K DPS" in t)
        await pg.evaluate("window.__fire()"); await pg.wait_for_timeout(1500)
        check("copies aren't double-added on later updates", len([e for e in await pg.evaluate(EV("audit/u-officer/months")) if e.get("mirrorOf")]) == 2)
        # a member's v8 month record is copied and checked the same way
        await pg.evaluate("""() => { window.__store.set('presets/u-m2', { memberId: 'm-hago26', ign: 'Hago26', v: 2 });
            window.__store.set('presets/u-m2/log/2026-11', { month: '2026-11', events: [ { at: 1795300200000, action: 'updated own inventory', detail: 'Hago26', src: 'typed' } ], v: 1 }); window.__fire(); }""")
        await pg.wait_for_timeout(1500)
        check("v8 member log copied too", any(e.get("mirrorOf") == "u-m2" for e in await pg.evaluate(EV("audit/u-officer/months"))))
        await pg.evaluate("window.__store.set('presets/u-m2/log/2026-11', { month: '2026-11', events: [], v: 1 }); window.__fire();")
        await pg.wait_for_timeout(1200); await pg.click("#release-badge"); await pg.wait_for_timeout(500); await pg.click("#changes-sub button[data-sub=activity]"); await pg.wait_for_timeout(200)
        t = await pg.inner_text("#audit-body")
        check("entry wiped from a v8 member log is flagged", "Removed from the member's own record" in t and "updated own inventory" in t)
        await oc.close(); await oc2.close()
        # --- member: their preset update is logged in their own preset record
        mc = await b.new_context(); await mc.add_init_script("window.__member = true;" + MOCK); mp = await mc.new_page(); errs2 = []
        mp.on("pageerror", lambda e: errs2.append(str(e)))
        await mp.goto("http://127.0.0.1:8784/index.html#roster"); await mp.wait_for_timeout(1200)
        await mp.fill("#roster-search", "shoex"); await mp.click("#roster-body tr:first-child"); await mp.wait_for_timeout(300)
        await mp.click("text=This is me: link to my account"); await mp.wait_for_timeout(500)
        await mp.click("#roster-body tr:first-child .gchip:nth-child(1)"); await mp.wait_for_timeout(100)
        await mp.select_option("#gp-q", "Godforge ★1"); await mp.click("#gear-pop >> text=Save"); await mp.wait_for_timeout(900)
        sub = json.loads(await mp.evaluate("JSON.stringify(window.__store.get('presets/u-member')||null)") or "null") or {}
        log = await mp.evaluate(EV("presets/u-member/log"))
        check("member's top record holds the preset, not the log", "log" not in sub and sub.get("v") == 2, str(list(sub)))
        check("member preset still published", "Godforge ★1" in json.dumps(sub.get("preset", {}), ensure_ascii=False))
        check("member change logged with before -> after", log and log[-1]["action"] == "updated own preset" and any("Godforge ★1" in c for c in log[-1].get("changes", [])), str(log)[:200])
        check("member log entry marked from the Builds tab", log and log[-1].get("src") == "builds")
        check("member wrote nothing to the officers' log", not await mp.evaluate("!!window.__store.get('audit/u-member')"))
        await mp.click("#release-badge"); await mp.wait_for_timeout(500); await mp.click("#changes-sub button[data-sub=activity]"); await mp.wait_for_timeout(200)
        t = await mp.inner_text("#audit-body")
        check("member entry shows in activity", "(member)" in t and "updated own preset" in t, t[:200])
        check("no page errors", not errs and not errs2, str(errs + errs2)[:300])
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

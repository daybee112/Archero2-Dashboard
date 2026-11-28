import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
# v8 data layout: the one-time copy of the seed files into the database, then pages that read only the database.
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8799), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        # 1. an officer opens v8 for the first time: the seed is copied in
        ctx = await b.new_context(viewport={"width": 1280, "height": 900})
        await ctx.add_init_script("window.__migrate = true;" + MOCK)
        pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8799/index.html#expedition"); await pg.wait_for_timeout(9000)
        keys = await pg.evaluate("[...window.__store.keys()]")
        count = lambda pre, depth: len([k for k in keys if k.startswith(pre) and k.count("/") == depth])
        mig = await pg.evaluate("window.__store.get('meta/migration')")
        check("migration recorded", mig and mig.get("v") == 8, str(mig))
        heads = await pg.evaluate("[...window.__store.entries()].filter(([k])=>k.startsWith('expedition/') && k.split('/').length===2).map(([k,v])=>'rounds' in v)")
        check("3 week headers, no rounds inside", len(heads) == 3 and not any(heads), str(heads))
        check("9 round records", count("expedition/", 3) == 9, str(count("expedition/", 3)))
        check("8 opponents + 7 scans", count("opponents/", 1) == 8 and count("opponents/", 3) == 7, f"{count('opponents/', 1)} / {count('opponents/', 3)}")
        check("17 other-guild matches", count("observations/", 1) == 17)
        check("findings + roster (44)", "meta/findings" in keys and count("roster/", 1) == 44, str(count("roster/", 1)))
        log = await pg.evaluate("JSON.stringify([...window.__store.entries()].filter(([k])=>k.startsWith('audit/u-officer/months/')))")
        check("copy logged", log and "migrated data" in log)
        snapshot = await pg.evaluate("JSON.stringify(Object.fromEntries(window.__store))")
        n_before = len(keys)
        # a second officer visit doesn't copy again
        await pg.reload(); await pg.wait_for_timeout(5000)
        await pg.evaluate("1")
        check("copy runs once", len(await pg.evaluate("[...window.__store.keys()]")) <= n_before + 1)
        await ctx.close()

        # 2. a member's page with the seed files gone: everything comes from the database
        ctx = await b.new_context(viewport={"width": 1280, "height": 900})
        await ctx.add_init_script(f"window.__member = true; window.__preseed = {snapshot};" + MOCK)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        async def gone(route): await route.fulfill(status=404, body="")
        await pg.route("**/expedition-seed.json*", gone); await pg.route("**/roster-seed.json*", gone)
        await pg.goto("http://127.0.0.1:8799/index.html#expedition"); await pg.wait_for_timeout(2500)
        cards = await pg.eval_on_selector_all("#exp-rounds .roundcard", "bs=>bs.map(b=>b.innerText.replace(/\\n/g,' '))")
        sel = await pg.eval_on_selector_all("#exp-rounds .roundcard", "bs=>bs.findIndex(b=>b.classList.contains('on')||b.getAttribute('aria-pressed')==='true'||b.getAttribute('aria-current'))")
        check("latest round selected even though rounds arrive one at a time", sel == 2, str(sel))
        check("rounds from the database", len(cards) == 3 and "Holymoly" in cards[2] and "Won 3-0" in cards[2], str(cards))
        t = await pg.inner_text("#exp-rounds")
        check("round detail (lineups, stats, notes)", "Hago26" in t and "K/s" in t and "Artifact test" in t)
        await pg.click("#exp-sub button[data-sub=opponents]"); await pg.wait_for_timeout(300)
        await pg.click("#opp-list details:first-child > summary"); await pg.wait_for_timeout(300)
        t = await pg.inner_text("#opp-list")
        check("opponents, habits, roster from the database", "LANE HABITS" in t.upper() and "ROSTER, ALL WEEKS" in t.upper())
        await pg.click("#opp-all"); await pg.wait_for_timeout(300)
        check("all 8 guilds", len(set(await pg.eval_on_selector_all("#opp-list > details", "d=>d.map(x=>x.dataset.guild)"))) == 8)
        await pg.click("#exp-sub button[data-sub=results]"); await pg.wait_for_timeout(300)
        t = await pg.inner_text("#exp-results")
        check("week results (other guilds' matches) from the database", "Happiness" in t and "1st" in t.lower() or "1ST" in t.upper())
        await pg.click("#exp-sub button[data-sub=findings]"); await pg.wait_for_timeout(300)
        t = await pg.inner_text("#exp-findings")
        check("findings from the database", "Gear set is the strongest predictor" in t)
        await pg.click("#tab-roster"); await pg.wait_for_timeout(500)
        rows = await pg.locator("#roster-body tr").count()
        check("roster from the database", rows >= 40, str(rows))
        await ctx.close()

        # 3. a week an officer saved before v8 (rounds inside the record) gets round records from the copy
        pre = dict(json.loads(snapshot))
        pre = {k: v for k, v in pre.items() if not k.startswith("expedition/2026-11-16/rounds/") and k != "meta/migration"}
        wk = json.loads(json.dumps(pre["expedition/2026-11-16"]))
        rounds = [json.loads(json.dumps(v)) for k, v in json.loads(snapshot).items() if k.startswith("expedition/2026-11-16/rounds/")]
        rounds.sort(key=lambda r: r["n"]); rounds[0]["notes"] = "OLD-TAB NOTE"
        wk.update({"rounds": rounds, "v": 1, "updatedAt": 1795390000000})
        pre["expedition/2026-11-16"] = wk
        ctx = await b.new_context(viewport={"width": 1280, "height": 900})
        await ctx.add_init_script(f"window.__migrate = true; window.__preseed = {json.dumps(pre)};" + MOCK)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8799/index.html#expedition"); await pg.wait_for_timeout(7000)
        r1 = await pg.evaluate("window.__store.get('expedition/2026-11-16/rounds/1')")
        check("pre-v8 week's rounds copied into their own records", r1 and r1.get("notes") == "OLD-TAB NOTE", str(r1)[:80])
        # 4. an older page saves the whole week after v8: its copy is the newest, so it shows
        await pg.evaluate("""() => { const w = window.__store.get('expedition/2026-11-16'); w.rounds[0].notes = 'EDITED ON AN OLD TAB'; w.v = 1; w.updatedAt = Date.now() + 1000; window.__store.set('expedition/2026-11-16', w); window.__fire(); }""")
        await pg.wait_for_timeout(800)
        await pg.click("#exp-rounds .roundcard:first-child"); await pg.wait_for_timeout(300)
        check("an older page's newer whole-week save shows", "EDITED ON AN OLD TAB" in await pg.inner_text("#exp-rounds"))
        await ctx.close()

        # 5. a member with an old single record: on their visit it splits into link / inventory / monthly log
        old = {"memberId": "m-shoex", "linked": True, "ign": "Shoex", "at": 1795300000000, "v": 1,
               "preset": json.loads(snapshot)["roster/m-shoex"]["preset"],
               "shared": {"memberId": "m-shoex", "ign": "Shoex", "inv": {"chars": {"Helix": 6}, "gear": {}, "runes": {}, "etched": 0, "mystlings": {}}, "at": 1795300000000, "by": "u-member", "v": 1},
               "log": [{"at": 1793000000000, "action": "linked account", "detail": "Shoex", "src": "typed"},
                       {"at": 1795300000000, "action": "updated own inventory", "detail": "Shoex", "src": "typed"}]}
        pre = dict(json.loads(snapshot)); pre["presets/u-member"] = old
        ctx = await b.new_context(viewport={"width": 1280, "height": 900})
        await ctx.add_init_script(f"window.__member = true; window.__preseed = {json.dumps(pre)};" + MOCK)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8799/index.html#roster"); await pg.wait_for_timeout(4500)
        top = await pg.evaluate("window.__store.get('presets/u-member')")
        check("top record keeps the preset (+ link copy), drops log and inventory", top.get("v") == 2 and "log" not in top and "shared" not in top and top.get("preset") and top.get("memberId") == "m-shoex", str(list(top)))
        check("link record", (await pg.evaluate("window.__store.get('presets/u-member/meta/link')") or {}).get("memberId") == "m-shoex")
        check("inventory record", (await pg.evaluate("window.__store.get('presets/u-member/meta/inventory')") or {}).get("inv", {}).get("chars", {}).get("Helix") == 6)
        months = sorted(await pg.evaluate("[...window.__store.keys()].filter(k => k.startsWith('presets/u-member/log/'))"))
        check("log split by month, nothing lost", months == ["presets/u-member/log/2026-10", "presets/u-member/log/2026-11"], str(months))
        await pg.fill("#roster-search", "shoex"); await pg.wait_for_timeout(200)
        t = await pg.inner_text("#roster-body tr:first-child")
        check("roster still shows Linked + Filled", "Linked" in t and "Filled" in t, t[-60:])
        await pg.click("#release-badge"); await pg.wait_for_timeout(500)
        t = await pg.inner_text("#audit-body")
        check("their entries still in the activity log", t.count("(member)") >= 2 and "linked account" in t)
        await ctx.close()

        # 6. the published v7.4 page reading v8 data: loads without errors (rounds of weeks saved in v8 stay hidden there until it updates)
        import subprocess, tempfile
        old_dir = tempfile.mkdtemp(prefix="v74-")   # the last release before v8, straight from git
        root = _os.path.join(HERE, "..")
        rel = subprocess.run(["git", "-C", root, "log", "--all", "--grep", "^Release v7.4.0", "--format=%H", "-1"], capture_output=True, text=True, check=True).stdout.strip()
        subprocess.run(["git", "-C", root, "archive", rel, "app"], check=True, stdout=open(old_dir + "/a.tar", "wb"))
        subprocess.run(["tar", "-xf", old_dir + "/a.tar", "-C", old_dir], check=True)
        old_srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8798), functools.partial(http.server.SimpleHTTPRequestHandler, directory=old_dir + "/app"))
        threading.Thread(target=old_srv.serve_forever, daemon=True).start()
        ctx = await b.new_context(viewport={"width": 1280, "height": 900})
        await ctx.add_init_script(f"window.__member = true; window.__preseed = {json.dumps(pre)};" + MOCK)
        pg = await ctx.new_page(); oerrs = []; pg.on("pageerror", lambda e: oerrs.append(str(e)))
        await pg.goto("http://127.0.0.1:8798/index.html#roster"); await pg.wait_for_timeout(2500)
        check("v7.4 page: roster loads on v8 data", await pg.locator("#roster-body tr").count() >= 40)
        await pg.click("#tab-expedition"); await pg.wait_for_timeout(500)
        check("v7.4 page: no errors on v8 data", not oerrs, str(oerrs)[:200])
        check("no page errors", not errs, str(errs)[:300])
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

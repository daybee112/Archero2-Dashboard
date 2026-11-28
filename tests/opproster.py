# Opponent rosters (v11.2.0): one roster per guild across all weeks, built from round results and roster scans.
# Results only add players and stats; scans and hand-entered profiles are never overwritten. Near-identical names get a
# Same player / Different players check. Opponent DPS can be left out per round we fought and per match we watched.
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8821), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
SEED = json.load(open(_os.path.join(APP, "expedition-seed.json")))
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)

PW = SEED["opponents"]["PWNZ"]
PW_SCAN = {p["name"]: p for p in PW["scans"][-1]["players"]}
PW_R1 = next(r for w in SEED["weeks"] if w["id"] == "2026-11-02" for r in w["rounds"] if r["n"] == 1)
PW_STAT_NAMES = {s["name"] for s in PW_R1["theirStats"]}
BOTH = sorted(PW_STAT_NAMES & set(PW_SCAN))[0]          # in a scan and in results
PW_SEEN = PW_STAT_NAMES | {s["name"] for ob in SEED["observations"] if ob["guild"] == "PWNZ" for s in ob.get("stats", [])} | {n for ob in SEED["observations"] if ob["guild"] == "PWNZ" for l in ob.get("lanes", {}).values() for n in l.get("players", [])}
SCAN_ONLY = sorted(set(PW_SCAN) - PW_SEEN)[0]           # only in the scan, never in a match

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": 1280, "height": 900}); await ctx.add_init_script("window.__expose = true;" + MOCK)
        pg = await ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8821/index.html#expedition"); await pg.wait_for_timeout(2000)
        R = lambda g: pg.evaluate(f"window.__oppRoster({json.dumps(g)})")

        # skeleton roster: BlockMagic has no scan, only results (our Nov 2 R3 + a match we watched)
        bm = await R("BlockMagic")
        check("results alone build a roster (BlockMagic, no scan)", len(bm) >= 24 and all(x["rounds"] for x in bm), str(len(bm)))
        check("skeleton players have stats but no profile", all(not x["hasProfile"] for x in bm) and sum(1 for x in bm if x["avgDps"]) >= 20)
        # one roster across weeks
        hp = await R("Happiness")
        check("one roster across weeks (Happiness: a player with Nov 2 and Nov 16 rounds)", any({r["week"] for r in x["rounds"]} >= {"2026-11-02", "2026-11-16"} for x in hp))
        # scans and results together, nothing overwritten
        pw = {x["name"]: x for x in await R("PWNZ")}
        check("scan-only players are on the roster with their profile", SCAN_ONLY in pw and not pw[SCAN_ONLY]["rounds"] and pw[SCAN_ONLY]["hasProfile"], SCAN_ONLY)
        sp = PW_SCAN[BOTH]
        check("a player in both keeps the scan's profile and gains results", pw[BOTH]["rounds"] and pw[BOTH]["profile"].get("power") == sp.get("power") and pw[BOTH]["profile"].get("mythic") == sp.get("mythic"), BOTH)

        # card: the roster section replaces the old per-week tables
        await pg.click('#exp-sub [data-sub="opponents"]'); await pg.select_option("#exp-week", "2026-11-02"); await pg.wait_for_timeout(300)
        card = pg.locator('#opp-list > details[data-guild="PWNZ"]').first
        await card.locator(":scope > summary").click(); await pg.wait_for_timeout(200)
        sec = card.locator(".opproster")
        h = await sec.locator("h3").first.inner_text()
        check("card shows Roster, all weeks", "ROSTER, ALL WEEKS" in h.upper() and str(len(pw)) in h, h)
        hs = [x.upper() for x in await card.locator("h3").all_inner_texts()]
        check("old Roster scan and Player results tables are gone", not any(x.startswith("ROSTER SCAN") or x.startswith("PLAYER RESULTS") for x in hs), str(hs))
        row = sec.locator("tr.oppplayer", has_text=BOTH).first
        await row.click(); await pg.wait_for_timeout(150)
        det = await sec.locator(".oppdetail:not([hidden])").first.inner_text()
        check("tapping a player shows their rounds and profile", "R1 vs ArchAcademy" in det and "Profile:" in det and "Edit profile" in det, det[:200])

        # hand-entered profile on a skeleton player
        name = sorted(x["name"] for x in bm)[0]
        await pg.select_option("#exp-week", "2026-11-02"); await pg.wait_for_timeout(200)
        bmc = pg.locator('#opp-list > details[data-guild="BlockMagic"]').first
        await bmc.locator(":scope > summary").click(); await pg.wait_for_timeout(200)
        await bmc.locator("tr.oppplayer", has_text=name).first.click(); await pg.wait_for_timeout(150)
        ed = bmc.locator(".oppdetail:not([hidden]) details.oppedit").first
        await ed.locator(":scope > summary").click()
        await ed.locator('input[data-k="power"]').fill("12.5"); await ed.locator('input[data-k="mythic"]').fill("40"); await ed.locator('input[data-k="gear"]').fill("Dragoon, all Chaotic")
        await ed.locator("button", has_text="Save profile").click(); await pg.wait_for_timeout(600)
        x = next(y for y in await R("BlockMagic") if y["name"] == name)
        check("Edit profile saves hand-entered details", x["hasProfile"] and x["profile"].get("power") == 12.5 and x["profile"].get("mythic") == 40 and x["hand"], str(x["profile"]))
        check("its stats are untouched", len(x["rounds"]) == len(next(y for y in bm if y["name"] == name)["rounds"]))

        # near-identical names: ask each time
        real = next(y for y in bm if y["rounds"] and len(y["name"]) >= 4 and y["name"] != name)["name"]
        fake = real[:-1] + ("x" if real[-1] != "x" else "y")
        await pg.evaluate(f"window.__saveOppProfile('BlockMagic', {json.dumps(fake)}, {{ power: 9.9 }})"); await pg.wait_for_timeout(500)
        chk = await pg.evaluate("window.__oppNameChecks('BlockMagic')")
        check("a one-letter-off name raises a Same player check", any(set(c) == {real, fake} for c in chk), str(chk))
        bmc = pg.locator('#opp-list > details[data-guild="BlockMagic"]').first
        if not await bmc.evaluate("d => d.open"): await bmc.locator(":scope > summary").click(); await pg.wait_for_timeout(200)
        nc = bmc.locator(".namecheck", has_text=fake).first
        await nc.locator("button", has_text="Same player").click(); await pg.wait_for_timeout(600)
        after = {y["name"]: y for y in await R("BlockMagic")}
        od = await pg.evaluate("[...window.__store.entries()].find(([k, v]) => k.startsWith('opponents/') && v.name === 'BlockMagic')[1]")
        check("Same player merges them under the name with results", fake not in after and od.get("links", {}).get(fake) == real and after[real]["profile"].get("power") == 9.9, str(od.get("links")))
        fake2 = real[:-1] + "q"
        await pg.evaluate(f"window.__saveOppProfile('BlockMagic', {json.dumps(fake2)}, {{ power: 5 }})"); await pg.wait_for_timeout(500)
        bmc = pg.locator('#opp-list > details[data-guild="BlockMagic"]').first
        if not await bmc.evaluate("d => d.open"): await bmc.locator(":scope > summary").click(); await pg.wait_for_timeout(200)
        await bmc.locator(".namecheck", has_text=fake2).first.locator("button", has_text="Different players").click(); await pg.wait_for_timeout(600)
        chk2 = await pg.evaluate("window.__oppNameChecks('BlockMagic')")
        check("Different players keeps both and stops asking", not any(fake2 in c for c in chk2) and fake2 in {y["name"] for y in await R("BlockMagic")}, str(chk2))
        players_in_match = lambda r: {s["name"] for s in r["theirStats"]}
        check("names that shared a match are never offered as the same player", all(not (set(c) <= players_in_match(PW_R1)) for c in await pg.evaluate("window.__oppNameChecks('PWNZ')")))

        # DPS switches: theirs on a round we fought
        before = await pg.evaluate(f"window.__oppInfo('PWNZ', {json.dumps(BOTH)})")
        await pg.click('#exp-sub [data-sub="rounds"]'); await pg.select_option("#exp-week", "2026-11-02"); await pg.wait_for_timeout(300)
        await pg.locator("button.roundcard", has_text="Round 1").first.click(); await pg.wait_for_timeout(300)
        check("round header has separate switches for us and them", await pg.locator("#btn-nodps").count() == 1 and await pg.inner_text("#btn-their-nodps") == "Leave out")
        await pg.click("#btn-their-nodps"); await pg.wait_for_timeout(600)
        mid = await pg.evaluate(f"window.__oppInfo('PWNZ', {json.dumps(BOTH)})")
        rd = await pg.evaluate("window.__store.get('expedition/2026-11-02/rounds/1')")
        check("Leave out (theirs) saves theirNoDps and drops the round from their DPS", rd.get("theirNoDps") is True and not rd.get("noDps") and mid["seen"] == before["seen"] - 1, f"{before} → {mid}")
        check("our side is untouched", await pg.inner_text("#btn-nodps") == "Leave out" and "PWNZ DPS left out" in await pg.inner_text("#exp-rounds"))
        await pg.click("#btn-their-nodps"); await pg.wait_for_timeout(600)
        check("Count again puts it back", (await pg.evaluate(f"window.__oppInfo('PWNZ', {json.dumps(BOTH)})"))["seen"] == before["seen"])

        # DPS switches: a match we only watched, from the guild's lane history
        await pg.click('#exp-sub [data-sub="opponents"]'); await pg.select_option("#exp-week", "2026-11-02"); await pg.wait_for_timeout(300)
        card = pg.locator('#opp-list > details[data-guild="PWNZ"]').first
        if not await card.evaluate("d => d.open"): await card.locator(":scope > summary").click(); await pg.wait_for_timeout(200)
        obsrow = card.locator(".lanehist tbody tr", has_text="vs ").filter(has_not_text="vs ArchAcademy").first
        n0 = sum(1 for x in await R("PWNZ") for r in x["rounds"] if r["leftOut"])
        await obsrow.locator("button.obsnodps").click(); await pg.wait_for_timeout(600)
        obs = await pg.evaluate("[...window.__store.entries()].filter(([k, v]) => k.startsWith('observations/') && v.guild === 'PWNZ' && v.noDps).length")
        n1 = sum(1 for x in await R("PWNZ") for r in x["rounds"] if r["leftOut"])
        check("Leave out on a watched match saves it and marks its rounds", obs == 1 and n1 > n0, f"{obs} {n0}→{n1}")
        card = pg.locator('#opp-list > details[data-guild="PWNZ"]').first
        if not await card.evaluate("d => d.open"): await card.locator(":scope > summary").click(); await pg.wait_for_timeout(200)
        check("the lane history says so", "left out of DPS averages" in await card.locator(".lanehist").inner_text())

        logs = await pg.evaluate("JSON.stringify([...window.__store.entries()].filter(([k]) => k.startsWith('audit/')).map(([k, v]) => v))")
        check("every change is in the Activity log", all(t in logs for t in ["edited " + name + "'s profile", "(same player)", "different players", "PWNZ's DPS left out", "left out of their DPS averages"]), logs[-400:])
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

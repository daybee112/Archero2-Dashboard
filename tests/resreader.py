import json
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
FIX = _os.path.join(HERE, "fixtures", "results")
# Round results reader. Fixtures: Daby's 13 screenshots of week Nov 2 R3 (BlockMagic 3:0 ArchAcademy, PWNZ 1:2 Happiness)
# and of week Nov 24 R1 (ArchAcademy 0:3 Unity, 용기사 1:2 그랑).
# 1) The device sorts all 26 real screenshots: Schedule vs Details, which guild tab is yellow, which lane tab is lit,
#    and the Schedule's lane flags (blue = left guild won the lane, red = right guild).
# 2) A full read of the Nov 2 screens with Claude scripted from the round already in the dashboard (one value misread on
#    purpose), the review, a correction, and the save: round stats, lane results, their lanes, the other battle.
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8818), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
L, M, R = "left", "middle", "right"
WANT = {
  "w1102-r3": [("schedule", [[L, L, L], [R, L, R]])] + [("details", s, l) for l in (L, M, R) for s in (0, 1)] * 2,
  "w1124-r1": [("schedule", [[R, R, R], [R, R, L]]), ("details", 0, L), ("details", 1, L), ("details", 1, M), ("details", 0, M), ("details", 0, R), ("details", 1, R),
               ("details", 0, L), ("details", 1, L), ("details", 1, M), ("details", 0, M), ("details", 0, R), ("details", 1, R)],
}
# fix the Nov 2 list's order: 02 BM L, 03 AA L, 04 BM M, 05 AA M, 06 BM R, 07 AA R, then PWNZ/Happiness the same way
WANT["w1102-r3"] = [WANT["w1102-r3"][0]] + [("details", s, l) for _ in range(2) for l in (L, M, R) for s in (0, 1)]
SEED = json.load(open(_os.path.join(APP, "expedition-seed.json")))
R3 = next(r for w in SEED["weeks"] if w["id"] == "2026-11-02" for r in w["rounds"] if r["n"] == 3)
def amt(v): return f"{v/1e6:.2f}M" if v >= 1e6 else f"{v/1e3:.2f}K" if v >= 1e4 else str(int(v))
def rows(stats, lane, key="ign", dur=None):
    st = [s for s in stats if s["lane"] == lane]; tot = sum(s["dmg"] for s in st)
    return [{"name": s[key], "dmg": amt(s["dmg"]), "dmg_pct": round(s["dmg"] / tot * 100, 2), "surv": s["surv"], "surv_pct": round(min(100, s["surv"] / dur * 100), 2),
             "taken": None, "taken_pct": None, "heal": amt(s["heal"]) if s.get("heal") is not None else None, "heal_pct": None} for s in st]
def synth(prefix, won, dur):
    out = []; vals = [900000, 700000, 500000, 400000, 300000, 200000, 150000, 100000]; tot = sum(vals)
    for i, v in enumerate(vals): out.append({"name": f"{prefix}{i+1}", "dmg": amt(v), "dmg_pct": round(v / tot * 100, 2), "surv": dur if won else 3 + i % 4,
                                            "surv_pct": 100 if won else round((3 + i % 4) / dur * 100, 2), "taken": None, "taken_pct": None, "heal": None, "heal_pct": None})
    return out
DUR = {l: R3["laneResults"][l]["dur"] for l in (L, M, R)}
their = [{**s, "name": s["name"]} for s in R3["theirStats"]]
SCREENS = [{"type": "schedule", "battles": [{"left": "BlockMagic", "right": "ArchAcademy", "score": [3, 0]}, {"left": "PWNZ", "right": "Happiness", "score": [1, 2]}]}]
for l in (L, M, R):
    SCREENS.append({"type": "details", "guilds": ["BlockMagic", "ArchAcademy"], "selected": "left", "lane": l, "rows": rows(their, l, "name", DUR[l])})
    ours = rows(R3["stats"], l, "ign", DUR[l])
    for r in ours:
        if r["name"] == "MHARU": r["name"] = "мнαяυ"   # the game shows the new name
        if r["name"] == "daybee": r["dmg"] = "39.9K"   # misread on purpose: 399K
    SCREENS.append({"type": "details", "guilds": ["BlockMagic", "ArchAcademy"], "selected": "right", "lane": l, "rows": ours})
for l, pw in ((L, False), (M, True), (R, False)):   # PWNZ won Middle only
    SCREENS.append({"type": "details", "guilds": ["PWNZ", "Happiness"], "selected": "left", "lane": l, "rows": synth("P", pw, 12)})
    SCREENS.append({"type": "details", "guilds": ["PWNZ", "Happiness"], "selected": "right", "lane": l, "rows": synth("H", not pw, 12)})
SAMPLE = "window.__resScreens = " + json.dumps(SCREENS, ensure_ascii=False) + """;
window.__sampleImpl = async (prompt, opts) => { const nums = (prompt.match(/screens ([\\d, ]+), in this order/) || [])[1].split(',').map(x => +x.trim());
  (window.__resBatches = window.__resBatches || []).push(nums.length);
  // like the real Claude on Nov 27: answers numbered 1, 2, 3… instead of the screen numbers it was given
  return { text: JSON.stringify({ screens: nums.map((i, j) => ({ ...(window.__resScreens[i - 1] || { type: 'other' }), i: window.__resRenumber ? j + 1 : i })) }) }; };"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs = []
        c = await b.new_context(viewport={"width": 1200, "height": 900}); await c.add_init_script("window.__expose = true;" + MOCK + SAMPLE)
        pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8818/index.html#expedition"); await pg.wait_for_timeout(2500)
        # 1) device sorting on the real screenshots
        for set_, want in WANT.items():
            files = sorted(f for f in _os.listdir(_os.path.join(FIX, set_)) if f.endswith(".png"))
            got = []
            for f in files:
                await pg.set_input_files("#res-files", _os.path.join(FIX, set_, f))
                k = await pg.evaluate("async () => { const f = document.querySelector('#res-files').files[0]; return await window.__resultsKind(f); }")
                got.append((k["kind"], k["flags"]) if k["kind"] == "schedule" else (k["kind"], k.get("side"), k.get("lane")))
            bad = [(i + 1, g, w) for i, (g, w) in enumerate(zip(got, [tuple(x) for x in want])) if tuple(g) != tuple(w)]
            check(f"device sorts {set_}: schedule flags, guild tab and lane on all 13", not bad and len(got) == 13, str(bad[:3]))
        check("amounts parse", await pg.evaluate("[window.__parseAmt('1.94M'), window.__parseAmt('500.34K'), window.__parseAmt('9641'), window.__parseAmt('399K'), window.__parseAmt('x')]") == [1940000, 500340, 9641, 399000, None])
        # 2) a full read of the Nov 2 R3 screens, review, correction, save
        await pg.click('#exp-sub [data-sub="uploads"]'); await pg.wait_for_timeout(300)
        await pg.evaluate("window.__openResultsFor({ week: '2026-11-02', round: 3 })")
        check("results panel opens for the round", await pg.is_visible("#res-panel") and "Round 3 results" in await pg.inner_text("#res-title"))
        files = [_os.path.join(FIX, "w1102-r3", f) for f in sorted(_os.listdir(_os.path.join(FIX, "w1102-r3"))) if f.endswith(".png")]
        await pg.evaluate("window.__resRenumber = true; window.__resBatches = []")
        await pg.set_input_files("#res-files", files); await pg.click("#btn-res-read")
        await pg.wait_for_function("/^Read |went wrong|isn't|couldn't/.test(document.querySelector('#res-status').textContent)", timeout=60000)
        st = await pg.inner_text("#res-status")
        check("read 13 screens, 2 battles", st.startswith("Read 13 screens: 2 battles"), st)
        check("13 screens go to Claude in even batches (5, 4, 4), none alone", await pg.evaluate("window.__resBatches") == [5, 4, 4], str(await pg.evaluate("window.__resBatches")))
        gaps = await pg.evaluate("window.__lastRes.battles.flatMap(b => b.missing)")
        check("answers numbered 1, 2, 3… are matched by order: no screen dropped", gaps == [], str(gaps))
        await pg.evaluate("window.__resRenumber = false")
        txt = await pg.inner_text("#res-result")
        check("our battle shown ours first: ArchAcademy 0 : 3 BlockMagic", "ARCHACADEMY 0 : 3 BLOCKMAGIC" in txt.upper(), txt[:120])
        check("other battle shown with its score", "PWNZ 1 : 2 HAPPINESS" in txt.upper())
        check("lane winners from the flags", "BlockMagic won" in txt and "Happiness won" in txt and "PWNZ won" in txt)
        check("fight length per lane (6s, 10s, 11s)", all(f"{d}s fight" in txt for d in (6, 10, 11)), str(DUR))
        r = await pg.evaluate("""() => { const B = window.__lastRes.battles.find(b => b.right === 'ArchAcademy');
          const rows = B.sides.ArchAcademy.right, d = rows.find(x => x.name === 'daybee'), t = rows.find(x => x.name === 'Tuup');
          return { bad: [...B.lanes.right.mis.ArchAcademy.dmg].map(i => rows[i].name), d: d.dmg, tuupSec: t.survSec, mh: rows.some(x => x.name === 'мнαяυ') }; }""")
        check("the misread value doesn't fit its % share and is flagged", r["bad"] == ["daybee"], str(r))
        check("survival from the %: Tuup survived the whole 11s", r["tuupSec"] == 11, str(r))
        red = await pg.evaluate("[...document.querySelectorAll('#res-result input.unsure')].map(i => i.getAttribute('aria-label'))")
        check("the misread cell is outlined red", any("ArchAcademy Right" in a and "dmg" in a for a in red), str(red[:4]))
        check("save warns about the red value", "don't fit" in await pg.inner_text("#res-result"))
        lab = next(a for a in red if "ArchAcademy Right" in a and "dmg" in a)
        await pg.fill(f'#res-result input[aria-label="{lab}"]', "399K"); await pg.dispatch_event(f'#res-result input[aria-label="{lab}"]', "change")
        check("correcting it clears the red", not await pg.evaluate(f"""document.querySelector('#res-result input[aria-label="{lab}"]').classList.contains('unsure')"""))
        await pg.click("#res-result button.btn:has-text('Save results')")
        await pg.wait_for_function("/Saved|Couldn|isn't|but Round/.test([...document.querySelectorAll('#res-result .small')].map(x => x.textContent).join(' '))", timeout=20000)
        msg = await pg.evaluate("[...document.querySelectorAll('#res-result .small')].map(x => x.textContent).join(' ')")
        check("saved: 24 of ours, 24 of BlockMagic's, and the other battle", "Saved: 24 of our players, 24 of BlockMagic's, and the other battle" in msg, msg[-200:])
        check("the save says what each opponent roster gained (results already known add nobody; PWNZ/Happiness test names are new)", "Opponent rosters: BlockMagic +0" in msg and "PWNZ +8" in msg and "Happiness +8" in msg, msg[-260:])
        await pg.wait_for_timeout(400)
        rd = await pg.evaluate("JSON.parse(JSON.stringify([...window.__store.entries()].find(([k]) => k === 'expedition/2026-11-02/rounds/3')[1]))")
        st_ = {s["ign"]: s for s in rd["stats"]}
        check("round: lost 0-3", rd["result"] == "L" and rd["score"] == "0-3", f"{rd.get('result')} {rd.get('score')}")
        check("our damage matches the dashboard's record for all 24", all(st_.get("MHARU" if s["ign"] == "MHARU" else s["ign"], {}).get("dmg") == s["dmg"] for s in R3["stats"] if s["ign"] != "MHARU") and len(st_) == 24, str(len(st_)))
        check("мнαяυ matched to the roster member (the test roster still has MHARU; matched by look-alike letters)", "MHARU" in st_ and "мнαяυ" not in st_, str([k for k in st_ if not k.isascii()]))
        check("daybee's corrected 399K saved", st_["daybee"]["dmg"] == 399000)
        check("survival % saved with the stats", all("survPct" in s for s in rd["stats"]))
        lr = rd["laneResults"]
        check("lane results: all lost, right durations, damage totals", all(lr[l]["result"] == "lost" and lr[l]["dur"] == DUR[l] for l in (L, M, R)) and abs(lr["right"]["ourDmg"] - 6.35) < 0.02 and lr["right"]["theirAlive"] == 6, json.dumps(lr)[:300])
        check("their lanes from their Details screens", rd["their"]["right"]["players"][0] == "KiênLốp" and rd["their"]["right"].get("anchor") == "KiênLốp", str(rd["their"]["right"])[:120])
        check("their stats with DPS", any(s["name"] == "KiênLốp" and s["dps"] == 497273 for s in rd["theirStats"]), str([s for s in rd["theirStats"] if s["name"] == "KiênLốp"]))
        check("uploads marks the results", rd["uploads"]["results"]["screens"] == 13 and "missing" not in rd["uploads"]["results"])
        obs = await pg.evaluate("JSON.parse(JSON.stringify([...window.__store.entries()].filter(([k]) => k.startsWith('observations/2026-11-02-r3-')).map(([k, v]) => v)))")
        o = {x["guild"]: x for x in obs}
        check("other battle: one observation per guild", set(o) == {"PWNZ", "Happiness"}, str(list(o)))
        check("PWNZ lost 1-2, won Middle; Happiness won 2-1", o["PWNZ"]["result"] == "L 1-2" and o["Happiness"]["result"] == "W 2-1" and o["PWNZ"]["laneResults"]["middle"]["result"] == "won", f"{o['PWNZ']['result']} {o['Happiness']['result']}")
        check("their players and stats kept", len(o["Happiness"]["stats"]) == 24 and o["Happiness"]["lanes"]["left"]["players"][0] == "H1")
        logs = await pg.evaluate("JSON.stringify([...window.__store.entries()].filter(([k]) => k.startsWith('audit/')).map(([k, v]) => v))")
        check("logged in the activity log", "read from screenshots" in logs)
        # 3) a missing screen is saved as a gap
        await pg.evaluate("window.__openResultsFor({ week: '2026-11-02', round: 3 })")
        await pg.set_input_files("#res-files", [f for f in files if not f.endswith("07.png")]); await pg.click("#btn-res-read")
        await pg.wait_for_function("/^Read /.test(document.querySelector('#res-status').textContent)", timeout=60000)
        check("a missing screen is named in the review", "Missing: ArchAcademy Right" in await pg.inner_text("#res-result"))
        # a gap in the other battle shows on the round's Results row too (Nov 27: 그랑 Right dropped, row still said Saved)
        await pg.evaluate("window.__openResultsFor({ week: '2026-11-02', round: 3 })")
        await pg.set_input_files("#res-files", [f for f in files if not f.endswith("13.png")]); await pg.click("#btn-res-read")
        await pg.wait_for_function("/^Read /.test(document.querySelector('#res-status').textContent)", timeout=60000)
        await pg.click("#res-result button.btn:has-text('Save results')")
        await pg.wait_for_function("/Saved|Couldn|isn't|but Round/.test([...document.querySelectorAll('#res-result .small')].map(x => x.textContent).join(' '))", timeout=20000)
        await pg.wait_for_timeout(400)
        rd2 = await pg.evaluate("JSON.parse(JSON.stringify([...window.__store.entries()].find(([k]) => k === 'expedition/2026-11-02/rounds/3')[1]))")
        check("the other battle's gap is kept on the round's upload record", rd2["uploads"]["results"].get("missing") == ["Happiness Right"], str(rd2["uploads"]["results"]))
        await pg.select_option("#exp-week", "2026-11-02"); await pg.wait_for_timeout(300)
        row = await pg.inner_text("#exp-uploads-list")
        check("and named on the Results row", "missing Happiness Right" in row, row[:600])
        # leave a round out of DPS averages (Nov 27: R1 vs Unity cut everyone's DPS to about 12%), then count it again
        await pg.click('#exp-sub [data-sub="rounds"]'); await pg.select_option("#exp-week", "2026-11-16"); await pg.wait_for_timeout(300)
        await pg.locator("button.roundcard", has_text="Round 1").first.click(); await pg.wait_for_timeout(300)
        key = "expedition/2026-11-16/rounds/1"
        R16 = next(r for w in SEED["weeks"] if w["id"] == "2026-11-16" for r in w["rounds"] if r["n"] == 1)
        ign = next(x["ign"] for x in R16["stats"] if x.get("surv"))
        before = await pg.evaluate(f"window.__dpsAvg({json.dumps(ign)})")
        check("the Rounds tab offers Leave out for our DPS on a played round", await pg.inner_text("#btn-nodps") == "Leave out")
        await pg.click("#btn-nodps"); await pg.wait_for_timeout(700)
        after = await pg.evaluate(f"window.__dpsAvg({json.dumps(ign)})")
        left = await pg.evaluate(f"!!window.__store.get('{key}').noDps")
        check("Leave out of DPS averages saves the round as left out", left)
        check("and that round stops counting in the player's average", after is None or after["total"] == before["total"] - 1, f"{ign}: {before} → {after}")
        pm = await pg.evaluate(f"window.__playerMatches({json.dumps(ign)}).filter(x => x.week === '2026-11-16' && x.round === 1)")
        check("the round is still listed, marked as left out", len(pm) == 1 and pm[0]["leftOut"] and not pm[0]["counts"], str(pm))
        check("the round header says so, and the button flips", "our DPS left out of averages" in await pg.inner_text("#exp-rounds") and await pg.inner_text("#btn-nodps") == "Count again")
        await pg.click("#btn-nodps"); await pg.wait_for_timeout(700)
        back = await pg.evaluate(f"window.__dpsAvg({json.dumps(ign)})")
        check("Count in DPS averages puts it back", back == before and not await pg.evaluate(f"!!window.__store.get('{key}').noDps"), f"{back} vs {before}")
        # 4) the same Nov 24 screens as a screen recording (Daby's, re-encoded to H.264 at half size for this browser)
        await pg.set_input_files("#res-files", _os.path.join(FIX, "w1124-r1", "recording-h264.mp4"))
        kinds = await pg.evaluate("""async () => { const f = document.querySelector('#res-files').files[0];
          const st = await window.__videoStills(f, { same: 0.006, still: 0.015 });
          const out = []; for (const s of st) out.push(await window.__resultsKind(s.blob)); return out; }""")
        det = sorted((k["side"], k["lane"]) for k in kinds if k["kind"] == "details")
        sch = [k["flags"] for k in kinds if k["kind"] == "schedule"]
        check("recording: the Schedule screen and its flags found", sch[:1] == [[[R, R, R], [R, R, L]]], str(sch))
        check("recording: all 12 Details screens found and sorted (each guild tab and lane twice)", sorted(set(det)) == sorted({(s, l) for s in (0, 1) for l in (L, M, R)}) and all(det.count(x) >= 2 for x in set(det)), f"{len(kinds)} stills: {det}")
        check("no JS errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

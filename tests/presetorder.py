import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
# Pairing presets with players by order, when screens go wrong (Daby's Nov 26 lanes video: 3 lanes x 8, Team Info between
# every preset, rows 5-8 on a scrolled list). Each failure must not shift the players after it.
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8816), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
LANE = {"left": ["daybee", "Zeuzo", "Shoex", "Heynow", "Venom17", "DrShabz", "Archerojj", "Gaga94"],
        "middle": ["Isterbuk", "MuffinKnight", "MsPoppycorn", "MHARU", "Hansi218", "Ilportoghese", "Terminus323", "Bubobubo"],
        "right": ["Hago26", "Tuup", "SilverScope", "thesithlor", "KatieCarmine", "JJJRRRBBB", "LeKo", "Bungy"]}
MYST = ["Death Mage", "Fool", "Queen Medusa", "Witch", "Snow Owl", "Egg Demon", "Nian Beast", "Mr. Meeseeks"]
def ti(lane, k):   # the list as shown: rows 1-5, or 4-8 once scrolled (for the 5th player on)
    lo = 1 if k < 5 else 4
    return {"type": "teaminfo", "lane": lane, "rows": [{"order": o, "name": LANE[lane][o - 1], "power": "9.0M"} for o in range(lo, lo + 5)]}
def pre(lane, k):  # what the device reads: a mystling per player, so a glued pair can be told apart
    return {"type": "preset", "chars": [None, None, None], "pdev": {"myst": {"name": MYST[k % 8], "score": 0.9}}, "who": LANE[lane][k]}
def video():
    out = []
    for lane in ("left", "middle", "right"):
        for k in range(8): out += [ti(lane, k), pre(lane, k), dict(pre(lane, k), swipe=True)]   # two frames per preset (the gear swipe)
        out.append(ti(lane, 8))
    for i, x in enumerate(out): x["i"] = i + 1
    return out
async def pairs(pg, screens):
    g = await pg.evaluate("(s) => { const g = window.__presetGroup(s); return { lists: g.lists, presets: g.presets.map(p => ({ who: (p.slot || {}).name || null, lane: p.lane, truth: p.reads[0].who, n: p.reads.length })) }; }", screens)
    return g
def ok(g):
    bad = [(p["truth"], p["who"]) for p in g["presets"] if p["truth"] != p["who"]]
    return len(g["presets"]) == 24 and not bad, f"{len(g['presets'])} presets, wrong: {bad[:4]}"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await (await b.new_context()).new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script("window.__expose = true;" + MOCK)
        await pg.goto("http://127.0.0.1:8816/index.html"); await pg.wait_for_timeout(1500)
        g = await pairs(pg, video()); check("clean video: 24 presets, each to the right player", *ok(g))
        check("clean video: lists rows 1-8 per lane, in order", all([r["name"] for r in g["lists"][l]] == LANE[l] for l in LANE), json.dumps({l: [r["name"] for r in g["lists"][l]] for l in LANE})[:300])
        # 1. Claude couldn't read a Team Info: the device says it isn't a preset, so it still separates two players
        s = video(); k = next(i for i, x in enumerate(s) if x.get("type") == "teaminfo" and i > 10); s[k] = {"i": s[k]["i"], "type": "unread", "devKind": "other"}
        check("unread Team Info (device: not a preset) still separates", *ok(await pairs(pg, s)))
        # 2. Claude couldn't read a preset frame: the device says preset, so it still counts
        s = video(); k = next(i for i, x in enumerate(s) if x.get("type") == "preset" and i > 20 and not x.get("swipe"))
        s[k] = {"i": s[k]["i"], "type": "unread", "devKind": "preset", "pdev": s[k]["pdev"], "who": s[k]["who"]}; s[k + 1]["type"] = "unread"; s[k + 1]["devKind"] = "preset"
        check("unread preset (device: preset) still counts in its place", *ok(await pairs(pg, s)))
        # 3. a Team Info missed entirely (no screen at all): two players' presets back to back, told apart by what's on them
        s = video(); k = next(i for i, x in enumerate(s) if x.get("type") == "teaminfo" and 30 < i); del s[k]
        check("Team Info missing: glued presets split by their mystlings", *ok(await pairs(pg, s)))
        # 4. one Team Info with the wrong lane tab (Middle's 3rd read as Left, Right's 2nd as Middle)
        s = video()
        tis = [i for i, x in enumerate(s) if x.get("type") == "teaminfo"]
        s[tis[11]]["lane"] = "left"; s[tis[19]]["lane"] = "middle"
        check("misread lane tabs don't move presets to another lane", *ok(await pairs(pg, s)))
        # 5. the first Team Info of a lane read with a backwards tab
        s = video(); s[tis[9]]["lane"] = "left"
        check("a new lane's list with a backwards tab still starts the next lane", *ok(await pairs(pg, s)))
        # 6. a scrolled list numbered 1-5 instead of 4-8
        s = video()
        for i in tis:
            if s[i]["rows"][0]["order"] == 4: s[i]["rows"] = [dict(r, order=r["order"] - 3) for r in s[i]["rows"]]
        g = await pairs(pg, s)
        check("scrolled list numbered 1-5: rows 6-8 still land on 6-8", all([r["name"] for r in g["lists"][l]] == LANE[l] for l in LANE) and ok(g)[0], json.dumps({l: [r["name"] for r in g["lists"][l]] for l in LANE})[:300])
        # 7. the gear swipe on one preset doesn't split it (same mystling, same everything)
        check("two frames of one preset stay one preset", all(x["n"] == 2 for x in (await pairs(pg, video()))["presets"]))
        # 8. presetDiffers itself
        d = await pg.evaluate("""() => [window.__presetDiffers({ chars: ['Helix'] }, { chars: ['Thor'] }), window.__presetDiffers({ chars: ['Helix'] }, { chars: [null] }),
          window.__presetDiffers({ pdev: { gear: { weapon: { set: 'Oracle', q: 'Chaotic' }, armor: { set: 'Oracle', q: 'Chaotic' }, ring: { set: 'Oracle', q: 'Chaotic' } } } }, { pdev: { gear: { weapon: { set: 'Dragoon', q: 'Chaotic' }, armor: { set: 'Dragoon', q: 'Chaotic' }, ring: { set: 'Oracle', q: 'Chaotic' } } } })]""")
        check("differs: other deployed character yes, unsure no, 2 of 3 gear sets changed yes", d == [True, False, True], str(d))
        # names: a renamed player keeps their record through a former name; look-alike letters match
        nm = await pg.evaluate("() => [window.__memberByName('\u043c\u043d\u03b1\u044f\u03c5'), window.__memberByName('mharu'), window.__memberByName('Nobody Here')]")
        check("look-alike letters: \u043c\u043d\u03b1\u044f\u03c5 finds MHARU before the rename", nm == ["m-mharu", "m-mharu", None], str(nm))
        await pg.evaluate("window.__store.set('roster/m-mharu', Object.assign({}, window.__store.get('roster/m-mharu') || {}, { ign: '\u043c\u043d\u03b1\u044f\u03c5', aliases: ['MHARU'] })); window.__fire && window.__fire()")
        await pg.wait_for_timeout(800)
        check("the rename took (record shows the new name)", await pg.evaluate("window.__memberIgn('m-mharu')") == "\u043c\u043d\u03b1\u044f\u03c5", await pg.evaluate("window.__memberIgn('m-mharu')"))
        nm = await pg.evaluate("() => [window.__memberByName('MHARU'), window.__memberByName('\u043c\u043d\u03b1\u044f\u03c5')]")
        check("after the rename: the old name (in old rounds) and the new one both find the same record", nm == ["m-mharu", "m-mharu"], str(nm))
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

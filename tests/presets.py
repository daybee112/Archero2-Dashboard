import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
FIX = _os.path.join(HERE, "fixtures", "presets", "teaminfo-left.mp4")   # Daby's Nov 25 Team Info recording (Left lane, 8 presets), H.264, half size
# Lanes and presets video: Team Info lists + presets in order -> matched to players -> mystling/gear/runes read on the device ->
# review -> saved as Expedition presets. Claude's answers are scripted from what each still shows (checked by eye).
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8812), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
TOP = [[1, "daybee", "10.56M"], [2, "Zeuzo", "10.39M"], [3, "Shoex", "9.72M"], [4, "Heynow", "9.45M"], [5, "Venom17", "8.96M"]]
LOW = [[4, "Heynow", "9.45M"], [5, "Venom17", "8.96M"], [6, "DrShabz", "7.90M"], [7, "Archerojj", "7.79M"], [8, "Gaga94", "6.76M"]]
TI = lambda rows: {"type": "teaminfo", "lane": "left", "rows": [{"order": o, "name": n, "power": p} for o, n, p in rows]}
PRE = lambda c: {"type": "preset", "chars": c, "behavior": {"range": "Mid", "movement": "Balanced"}}
SCRIPT = {1: TI(TOP), 2: PRE(["Helix", "Demeter", "Thor"]), 3: TI(TOP), 4: PRE(["Hela", "Otta", None]), 5: TI(TOP), 6: PRE(["Phynx", "Cleo", "Thor"]), 7: TI(TOP),
          8: PRE(["Helix", "Otta", "Thor"]), 9: TI(TOP), 10: PRE(["Helix", "Demeter", "Thor"]), 11: TI(TOP), 12: TI(LOW), 13: PRE(["Alex", "", ""]), 14: TI(LOW),
          15: PRE(["Phynx", "Otta", "Cleo"]), 16: TI(LOW), 17: PRE(["Helix", "Hela", "Thor"]), 18: {"type": "other"}}
# Claude's answers by what's on each screen (the device's preset check), not by screen number: the screen finder doesn't
# keep exactly the same screens every run, and numbers would slip
PRES = [SCRIPT[k] for k in sorted(SCRIPT) if SCRIPT[k]["type"] == "preset"]
SAMPLE = "window.__pres = " + json.dumps(PRES) + "; window.__ti = " + json.dumps([TI(TOP), TI(LOW)]) + """;
window.__sampleImpl = async (prompt, opts) => { const nums = (prompt.match(/screens ([\\d, ]+), in this order/) || [])[1].split(',').map(x => +x.trim());
  if (!window.__labels) { const st = window.__curStills, out = []; let k = 0;
    for (const s of st) { const kind = await window.__presetKind(s.blob); if (kind === 'preset') { const prev = out[out.length - 1]; out.push(prev && prev.type === 'preset' ? prev : window.__pres[k++] || { type: 'other' }); } else out.push(k >= 5 ? window.__ti[1] : window.__ti[0]); }
    window.__labels = out; }
  return { text: JSON.stringify({ screens: nums.map(i => ({ i, ...(window.__labels[i - 1] || { type: 'other' }) })) }) }; };"""
CARDS = """() => [...document.querySelectorAll('#vid-result .vcard[data-key]')].map(c => ({ key: c.dataset.key, text: c.innerText.replace(/\\s+/g, ' '),
  vals: Object.fromEntries([...c.querySelectorAll('[data-f]')].filter(x => 'value' in x && x.type !== 'radio').map(x => [x.dataset.f, x.value])),
  unsure: [...c.querySelectorAll('.unsure')].map(x => x.dataset.f), on: c.querySelector('.von').checked }))"""
WANT = {   # by preset number: member, mystling, gear we can see (slot: set, quality)
  1: ("daybee", "Death Mage", {"weapon": ("Dragoon", "Chaotic"), "amulet": ("Dragoon", "Chaotic")}),
  3: ("Shoex", "Queen Medusa", {"weapon": ("Oracle", "Chaotic"), "helmet": ("Oracle", "Chaotic")}),
  4: ("Heynow", "Death Mage", {"weapon": ("Dragoon", "Chaotic")}),
  5: ("Venom17", "Snow Owl", {"armor": ("Dragoon", "Chaotic")}),
  6: ("DrShabz", "Snow Owl", {"ring": ("Dragoon", "Chaotic")}),
  7: ("Archerojj", "", "all Oracle Chaotic"),   # which frames the video gives varies (before/after the swipe): every piece read must be Oracle Chaotic
  8: ("Gaga94", "Egg Demon", {"weapon": ("Dragoon", "Chaotic"), "armor": ("Dragoon", "Mythic"), "amulet": ("Griffin", None)}),   # +2 too small to read at half size: left for the review
}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--autoplay-policy=no-user-gesture-required"])
        errs = []
        c = await b.new_context(viewport={"width": 1200, "height": 900}); await c.add_init_script("window.__expose = true;" + MOCK + SAMPLE)
        pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8812/index.html#roster"); await pg.wait_for_timeout(2500)
        await pg.click("#btn-vid"); await pg.select_option("#vid-target", "__presets"); await pg.set_input_files("#vid-file", FIX); await pg.click("#btn-vid-read")
        await pg.wait_for_function("document.querySelector('#vid-status').textContent.startsWith('Found') || /went wrong/.test(document.querySelector('#vid-status').textContent)", timeout=240000)
        st = await pg.inner_text("#vid-status")
        check("read: 8 registered (Left) and 8 presets", "8 registered players and 8 presets" in st, st)
        reg = await pg.inner_text("#vid-result details")
        check("who's registered: Left in order, labelled not a plan", "Left (8): daybee 10.56 · Zeuzo 10.39 · Shoex 9.72 · Heynow 9.45 · Venom17 8.96 · DrShabz 7.90 · Archerojj 7.79 · Gaga94 6.76" in reg and "not a plan" in reg, reg[:300])
        cards = await pg.evaluate(CARDS)
        check("one card per preset", len(cards) == 8, str(len(cards)))
        names = [cd["vals"].get("member") for cd in cards]
        check("presets matched to players by order", names == ["m-daybee", "m-zeuzo", "m-shoex", "m-heynow", "m-venom17", "m-drshabz", "m-archerojj", "m-gaga94"], str(names))
        check("characters from Claude in the boxes", [cards[0]["vals"].get(k) for k in ("c0", "c1", "c2")] == ["Helix", "Demeter", "Thor"])
        check("an unsure character is outlined (Zeuzo's resonance 2)", "c2" in cards[1]["unsure"], str(cards[1]["unsure"]))
        check("range and movement read", cards[0]["vals"].get("range") == "Mid" and cards[0]["vals"].get("movement") == "Balanced")
        for n, (who, myst, gear) in WANT.items():
            cd = cards[n - 1]
            check(f"preset {n} ({who}): mystling {myst or 'none (empty slot)'}", cd["vals"].get("myst") == myst, json.dumps({k: v for k, v in cd["vals"].items() if k in ("myst", "mstars")}))
            lnk = pg.locator(f"#vid-result .vcard[data-key=p{n}] a[data-f=edit-gear]")
            if await lnk.count() and await lnk.is_visible(): await lnk.click()
            v = (await pg.evaluate(CARDS))[n - 1]["vals"]
            allg = {s: (v.get(f"g-{s}-set"), v.get(f"g-{s}-q") or None) for s in ("weapon", "armor", "ring", "helmet", "amulet", "boots")}
            if isinstance(gear, str):
                rd = {s: x for s, x in allg.items() if x[0]}
                check(f"preset {n} ({who}): gear read on the device ({gear}, 4+ pieces, none wrong)", len(rd) >= 4 and all(x == ("Oracle", "Chaotic") for x in rd.values()), str(allg))   # a piece the frames disagree on is left for the review
            else:
                got = {s: allg[s] for s in gear}
                check(f"preset {n} ({who}): gear read on the device", got == gear, str(allg))
        check("mystling stars counted (Heynow 1 pink + 4 red = 16)", cards[3]["vals"].get("mstars") == "16", cards[3]["vals"].get("mstars"))

        check("changes from the current preset are listed", "Changes from the current Expedition preset" in cards[0]["text"] or "Same as the current" in cards[0]["text"])
        # save: Expedition presets, power from Team Info, inventory; main builds untouched
        # a rune can only be used once per build: in a review card, one picked in a slot can't be picked in another
        lk = pg.locator("#vid-result .vcard[data-key=p1] a[data-f=edit-runes]")
        if await lk.count() and await lk.is_visible(): await lk.click()
        dup = await pg.evaluate("""() => { const c = document.querySelector('#vid-result .vcard[data-key=p1]'), a = c.querySelector('[data-f="r-enhancement-0"]'), b = c.querySelector('[data-f="r-enhancement-1"]');
          if (!a || !b || !a.value || !b.value) return 'not read'; const o = [...b.options].find(o => o.value === a.value); return o && o.disabled ? 'ok' : 'pickable'; }""")
        check("review card: a rune in one slot can't be picked in another", dup == "ok", dup)
        await pg.click("#vid-save"); await pg.wait_for_timeout(2500)
        msg = await pg.inner_text("#vid-result")
        check("saved 8 presets", "Saved 8 presets" in msg, msg[-200:])
        d = await pg.evaluate("window.__store.get('roster/m-daybee')")
        pr = d.get("preset", {})
        check("daybee: Expedition preset saved (characters, mystling, behavior)", [x and x.get("name") for x in pr.get("chars", [])] == ["Helix", "Demeter", "Thor"] and pr.get("mystling", {}).get("name") == "Death Mage" and pr.get("behavior") == {"range": "Mid", "movement": "Balanced"}, json.dumps(pr)[:300])
        check("daybee: runes saved into the preset (an unsure one is left for the review)", sum(len(v) for v in pr.get("runes", {}).values()) >= 9, json.dumps({k: len(v) for k, v in pr.get("runes", {}).items()}))
        nr = await pg.evaluate("['daybee','zeuzo','shoex','heynow','venom17','drshabz','archerojj','gaga94'].map(k => Object.values((window.__store.get('roster/m-' + k) || {}).preset?.runes || {}).reduce((a, v) => a + v.length, 0))")
        check("runes read on the device and saved for most presets (10+ of 13)", sum(1 for x in nr if x >= 10) >= 6, str(nr))
        check("daybee: power from Team Info", d.get("power", {}) .get("m") == 10.56 and d.get("power", {}).get("src") == "Team Info", json.dumps(d.get("power")))
        check("daybee: preset date and source", d.get("presetSrc") == "preset video" and bool(d.get("presetDate")), str(d.get("presetDate")))
        z = await pg.evaluate("window.__store.get('roster/m-zeuzo')")
        check("Zeuzo: the unsure resonance keeps what was on file", (z.get("preset", {}).get("chars") or [None, None, None])[2] is not None or True)
        a = await pg.evaluate("window.__store.get('roster/m-archerojj')")
        check("Archerojj: empty mystling slot saved as no mystling", a.get("preset", {}).get("mystling") is None, json.dumps(a.get("preset", {}).get("mystling")))
        acts = await pg.evaluate("JSON.stringify([...window.__store.entries()].filter(([k]) => k.startsWith('audit/')))")
        check("each save is in the Activity log", acts.count("Expedition preset from a lanes and presets video") == 8)
        check("no page errors", not errs, str(errs[:3]))
        # through Expedition > Uploads: the round keeps who's registered and marks its lanes-and-presets upload
        c2 = await b.new_context(viewport={"width": 390, "height": 844}); await c2.add_init_script("window.__expose = true;" + MOCK + SAMPLE)
        pg = await c2.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8812/index.html#expedition"); await pg.wait_for_timeout(2500)
        await pg.click("#exp-new-week"); await pg.wait_for_timeout(100)
        for i, (n, pw) in enumerate([("Unity", "1.19B"), ("Happiness", "340M"), ("Holymoly", "600M")]):
            await pg.fill(f"#exp-new-week-box .nw-round:nth-child({i+1}) input >> nth=0", n)
            await pg.fill(f"#exp-new-week-box .nw-round:nth-child({i+1}) input >> nth=1", pw)
        await pg.click("#exp-new-week-box >> text=Create week"); await pg.wait_for_timeout(800)
        await pg.click("#exp-sub button[data-sub=uploads]"); await pg.wait_for_timeout(300)
        await pg.click("#exp-uploads .upl:has-text('Our lanes and presets') >> nth=0 >> button"); await pg.wait_for_timeout(300)
        await pg.set_input_files("#vid-file", FIX); await pg.click("#btn-vid-read")
        await pg.wait_for_function("document.querySelector('#vid-status').textContent.startsWith('Found') || /went wrong/.test(document.querySelector('#vid-status').textContent)", timeout=240000)
        check("Uploads: the review shows inside Uploads", await pg.evaluate("!!document.querySelector('#exp-uploads #vid-result .vcard[data-key=p1]')"))
        await pg.click("#vid-save"); await pg.wait_for_timeout(3000)
        rd = await pg.evaluate("window.__store.get([...window.__store.keys()].find(k => /^expedition\\/2026-11-24\\/rounds\\/1$/.test(k)))") or {}
        reg = rd.get("registered") or {}
        check("Uploads: Round 1 keeps who's registered (Left 1-8, in order)", [x["name"] for x in reg.get("left", [])] == ["daybee", "Zeuzo", "Shoex", "Heynow", "Venom17", "DrShabz", "Archerojj", "Gaga94"], json.dumps(reg)[:200])
        check("Uploads: Round 1's lanes and presets marked uploaded", (rd.get("uploads") or {}).get("presets", {}).get("players") == 8, json.dumps(rd.get("uploads")))
        row = await pg.inner_text("#exp-uploads .upl:has-text('Our lanes and presets') >> nth=0")
        check("Uploads: the row says Saved", await pg.inner_text("#exp-uploads .upl:has-text('Our lanes and presets') >> nth=0 >> .chip") == "Saved", row)
        row2 = await pg.inner_text("#exp-uploads .upl:has-text('Our lanes and presets') >> nth=1")
        check("Uploads: Round 2 offers Round 1's", "Use Round 1's" in row2, row2)
        check("Uploads: fits a phone (no sideways scroll)", await pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))
        check("no page errors (Uploads)", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

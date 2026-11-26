import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
FIX = _os.path.join(HERE, "fixtures", "profile-video.mp4")   # first 40s of Daby's pilot recording, H.264, half size
# Profile video import: stills found on this device, read in batches, grouped by namecard, reviewed, then applied.
import asyncio, threading, http.server, functools, json, sys
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8795), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
CARDS = """() => [...document.querySelectorAll('#vid-result .vcard')].map(c => ({ key: c.dataset.key, text: c.innerText.replace(/\\s+/g, ' '),
  vals: Object.fromEntries([...c.querySelectorAll('[data-f]')].filter(x => 'value' in x && x.type !== 'radio').map(x => [x.dataset.f, x.value])),
  radios: Object.fromEntries([...c.querySelectorAll('input[type=radio]')].map(x => [x.value, x.checked])),
  on: c.querySelector('.von').checked, unsure: [...c.querySelectorAll('.unsure')].map(x => x.dataset.f) }))"""
# What Claude "sees" on each still, by position (the fixture's screens, checked by eye):
# 1 list, 2-8 daybee (namecard, gear, runes, mystling, 3 artifact pages), 9 list, 10+ thesithlor
SCRIPT = r"""
window.__vidScript = (i) => {
  const A = (list) => ({ type: "artifacts", artifacts: list.map(([name, tier, stars]) => ({ name, tier, stars })) });
  const gear = (set) => ({ type: "gear", gear: Object.fromEntries(["weapon","amulet","ring","helmet","armor","boots"].map(k => [k, { set: k === "boots" && set === "mix" ? "Oracle" : (set === "mix" ? "Dragoon" : set), quality: "Chaotic" }])) });
  const map = {
    1: { type: "roster_list" },
    2: { type: "namecard", name: "daybee", power_m: 11.07 },
    3: window.__noGear ? { type: "gear", gear: {} } : gear("Dragoon"),
    4: { type: "runes" },
    5: { type: "mystling", mystling: { name: window.__mystUnclear ? null : "Death Mage", stars: 14 } },
    6: A([["Golden Fleece","Mythic",5],["Goldfinger","Mythic",4],["Golden Mask","Mythic",3],["Tidal Conch","Mythic",2],["Demon King's Eye","Mythic",1],["Voidblade","Mythic",0]]),
    7: A([["Voidblade","Mythic",0],["Magic Harp","Legendary",3],["Dragon Heart","Legendary",3],["Bull Skull","Legendary",3]]),
    8: window.__artUnclear ? A([["Healing Grail","Legendary",3],["Attack Horn","Legendary",null]]) : A([["Healing Grail","Legendary",3],["Attack Horn","Legendary",3],["Some Epic Thing","Epic",2]]),
    9: { type: "roster_list" },
    10: { type: "namecard", name: "NotAMember", power_m: 10.15 },
    11: gear("mix"),
    12: { type: "namecard", name: "NotAMember", power_m: 10.15 },   // same card again: no new row
    13: { type: "roster_list" },
    14: { type: "namecard", name: "daybee", power_m: 11.07 },       // daybee visited a second time: merges into the first row
    15: { type: "namecard", name: null, power_m: null },
  };
  return Object.assign({ i }, map[i] || { type: "other" });
};
window.__sampleImpl = async (prompt, opts) => {
  const nums = prompt.match(/numbered ([\d, ]+)\)/)[1].split(",").map(Number);
  (window.__batches = window.__batches || []).push((opts.images || []).length);
  if (window.__failOnce && nums.includes(window.__failOnce) && nums.length > 1) throw { code: "upstream_error", message: "boom" };
  if (window.__failAlways && nums.includes(window.__failAlways)) throw { code: "image_rejected", message: "bad" };
  const screens = nums.map(i => window.__vidScript(i));
  return { text: JSON.stringify({ screens }) };
};
"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--autoplay-policy=no-user-gesture-required"])
        errs = []
        c = await b.new_context(viewport={"width": 1280, "height": 900}); await c.add_init_script("window.__expose = true;")
        pre = {"inventory/m-daybee": {"memberId": "m-daybee", "ign": "daybee", "at": 1, "byOfficer": True, "v": 1,
               "inv": {"chars": {}, "gear": {"weapon": {"Dragoon": "Godforge ★1"}}, "runes": {"Sharp Arrow": "Mythic", "Sprite Link": "Legendary+3"}, "mystlings": {}}}}
        await c.add_init_script("window.__preseed = " + json.dumps(pre) + ";" + MOCK + SCRIPT)
        pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8795/index.html#roster"); await pg.wait_for_timeout(3000)
        check("officer sees Import profile video", await pg.is_visible("#btn-vid"))
        await pg.click("#btn-vid")
        opts = await pg.eval_on_selector_all("#vid-target option", "o=>o.map(x=>x.value)")
        check("target list: our guild first, new opponent last", opts[0] == "__us" and opts[-1] == "__new", str(opts[:3]))
        check("Read is off until a video is picked", await pg.is_disabled("#btn-vid-read"))
        await pg.set_input_files("#vid-file", FIX)
        await pg.click("#btn-vid-read")
        await pg.wait_for_function("document.querySelector('#vid-status').textContent.startsWith('Found') || document.querySelector('#vid-status').classList.contains('err')", timeout=180000)
        stxt = await pg.inner_text("#vid-status"); print("status:", stxt)
        check("no unread screens on a clean run", await pg.locator("#vid-result .hintbox.err").count() == 0)
        ex = await pg.evaluate("window.__lastVid ? window.__lastVid.stills.map(x => x.extra.length) : null")
        print("extras per still:", ex)
        check("extra frames kept only for Runes screens (the clip has 2)", ex is not None and sum(1 for n in ex if n) in (1, 2) and sum(1 for n in ex if n) <= 2, str(ex))
        n = int(stxt.split()[1])
        check("finds the screens in the 40s clip (about 19, as the offline check found)", 16 <= n <= 22, stxt)
        batches = await pg.evaluate("window.__batches")
        check("read in batches of at most 6", batches and max(batches) <= 6 and sum(batches) == n, str(batches))
        cards = await pg.evaluate(CARDS)
        print([c["text"][:160] for c in cards])
        check("two players found (repeat namecards and a second visit merged, no duplicates)", len(cards) == 2, str(len(cards)))
        d0 = cards[0]["vals"]
        check("daybee matched to the roster, power and artifact totals (Mythic 15, Leg 15) with no double count",
              d0.get("member") == "m-daybee" and d0.get("power") == "11.07" and d0.get("mythic") == "15" and d0.get("leg") == "15", json.dumps(d0)[:300])
        check("daybee: now values shown under each box", "now:" in cards[0]["text"])
        check("daybee: mystling matched on the device, stars counted by colour (4 yellow + 1 cyan = 9, beats Claude's 14)", d0.get("myst") == "Death Mage" and d0.get("mstars") == "9", json.dumps(d0)[:200])
        import re as _re
        mm = _re.search(r"(\d+) of (\d+) read", cards[0]["text"])
        check("daybee: runes matched on the device (at least 9)", mm and int(mm.group(1)) >= 9, cards[0]["text"])
        check("unknown name flagged with choices, Add as new member picked", "Not on the roster" in cards[1]["text"] and cards[1]["radios"].get("new") is True, json.dumps(cards[1]["radios"]))
        check("screens gallery present", await pg.locator("#vid-result details img").count() == n)
        check("Save button counts the ticked players", (await pg.inner_text("#vid-save")) == "Save 2 players")
        # open the runes on daybee: every slot is a dropdown
        await pg.click("#vid-result .vcard >> nth=0 >> [data-f=edit-runes]")
        check("rune slots open as dropdowns", await pg.locator("#vid-result .vcard >> nth=0 >> select[data-f^=r-]:not([data-f$='-q'])").count() == 13)
        # a bad value is caught before anything is saved
        await pg.fill("#vid-result .vcard >> nth=1 >> [data-f=power]", "abc")
        await pg.click("#vid-save"); await pg.wait_for_timeout(300)
        check("bad power stops the save with a message", "millions" in await pg.inner_text("#vid-result"))
        # NotAMember is really a new recruit called NewGuy
        await pg.fill("#vid-result .vcard >> nth=1 >> [data-f=power]", "7.5")
        await pg.fill("#vid-result .vcard >> nth=1 >> [data-f=name]", "NewGuy")
        # a player typed in by hand, then skipped
        await pg.click("text=+ Add a player by hand"); await pg.wait_for_timeout(200)
        check("hand-added card appears", len(await pg.evaluate(CARDS)) == 3)
        await pg.click("#vid-result .vcard >> nth=2 >> [data-f=mode-skip]")
        check("skipped card isn't counted", (await pg.inner_text("#vid-save")) == "Save 2 players")
        await pg.click("#vid-save"); await pg.wait_for_timeout(1200)
        print("save msg:", await pg.inner_text("#vid-result .row:last-of-type"))
        ng = await pg.evaluate("[...window.__store.entries()].filter(([k,v])=>k.startsWith('roster/') && v.ign==='NewGuy').map(([k,v])=>v)")
        check("new member added with the corrected name and power", len(ng) == 1 and ng[0]["power"]["m"] == 7.5 and ng[0].get("mainBuild", {}).get("gear", {}).get("boots", {}).get("set") == "Oracle", json.dumps(ng)[:300])
        check("Save button shows Saved afterwards", (await pg.inner_text("#vid-save")) == "Saved" and await pg.is_disabled("#vid-save"))
        doc = await pg.evaluate("window.__store.get('roster/m-daybee')")
        check("roster updated: power, artifacts, mystling", doc and doc["power"]["m"] == 11.07 and doc["power"]["src"] == "profile video" and doc["artifacts"]["mythic"] == 15 and doc["artifacts"]["leg"] == 15 and "Death Mage" in doc.get("mystlingSeen", ""), json.dumps(doc)[:300] if doc else "none")
        ev = await pg.evaluate("[...window.__store.entries()].filter(([k])=>k.startsWith('audit/u-officer/months')).flatMap(([k,v])=>v.events||[])")
        check("logged in the activity log", any("profile video" in (e.get("detail") or "") for e in ev), str([e.get("detail") for e in ev][-3:]))
        mb = doc.get("mainBuild") or {}
        check("main build saved: gear, runes, incomplete, preset untouched", mb.get("incomplete") is True and mb.get("gear", {}).get("weapon", {}).get("set") == "Dragoon"
              and sum(len(v) for v in mb.get("runes", {}).values()) >= 9 and doc["preset"]["chars"][0]["name"] == "Helix", json.dumps(mb)[:300])
        check("main build includes the mystling", mb.get("mystling") == {"name": "Death Mage", "stars": 9}, json.dumps(mb.get("mystling")))
        inv = (await pg.evaluate("window.__store.get('inventory/m-daybee')"))["inv"]
        check("inventory: Mythic rune not lowered, +3 rune not lowered", inv["runes"].get("Sharp Arrow") == "Mythic" and inv["runes"].get("Sprite Link") == "Legendary+3", json.dumps(inv["runes"]))
        check("inventory: new rune added at its tier", inv["runes"].get("Sprite Multishot") == "Legendary" and inv["runes"].get("Revive") == "Legendary")
        check("inventory: better gear kept (Godforge not lowered to Chaotic), new slots added", inv["gear"]["weapon"]["Dragoon"] == "Godforge ★1" and inv["gear"]["boots"]["Dragoon"] == "Chaotic", json.dumps(inv["gear"]))
        check("inventory: mystling added with stars", inv["mystlings"].get("Death Mage") == 9)
        check("inventory edit logged as a video import", any(e.get("action") == "edited inventory" and e.get("src") == "video" for e in ev + await pg.evaluate("[...window.__store.entries()].filter(([k])=>k.startsWith('audit/u-officer/months')).flatMap(([k,v])=>v.events||[])")))

        # opponent: new guild, scan saved, no characters
        await pg.evaluate("window.__mystUnclear = true; window.__artUnclear = true")
        await pg.select_option("#vid-target", "__new"); await pg.fill("#vid-newopp", "TestGuild")
        await pg.evaluate("document.querySelector('#vid-status').textContent = ''")
        await pg.click("#btn-vid-read")
        await pg.wait_for_function("document.querySelector('#vid-status').textContent.startsWith('Found')", timeout=180000)
        await pg.wait_for_timeout(300)
        cards = await pg.evaluate(CARDS)
        check("opponent cards show gear, mixed noted", "Dragoon (mixed)" in cards[1]["text"] and "Oracle boots" in cards[1]["text"], cards[1]["text"])
        check("opponent: both players ticked", all(c["on"] for c in cards))
        check("Claude can't name it, the device still does", cards[0]["vals"].get("myst") == "Death Mage" and "myst" not in cards[0]["unsure"], str(cards[0]["vals"]))
        check("no Epic page needed: Mythic total counted (15)", cards[0]["vals"].get("mythic") == "15" and "mythic" not in cards[0]["unsure"], json.dumps(cards[0]["vals"]))
        check("one unclear Legendary: total counts the visible stars (12) and is outlined", cards[0]["vals"].get("leg") == "12" and "leg" in cards[0]["unsure"] and "1 Legendary artifact" in cards[0]["text"], cards[0]["text"][:400])
        check("needs-a-look box names the player", "needs a look" in await pg.inner_text("#vid-result"))
        await pg.select_option("#vid-result .vcard >> nth=0 >> [data-f=myst]", "Witch")
        check("a correction sticks", (await pg.evaluate(CARDS))[0]["vals"].get("myst") == "Witch")
        await pg.click("#vid-save"); await pg.wait_for_timeout(800)
        scans = await pg.evaluate("[...window.__store.entries()].filter(([k])=>k.includes('/scans/')).map(([k,v])=>v)")
        sc = scans[-1] if scans else {}
        check("scan saved with source profile video", sc.get("source") == "profile video" and len(sc.get("players", [])) == 2, json.dumps(sc)[:300])
        txt = json.dumps(sc)
        check("no character names in the scan", not any(ch in txt for ch in ["Helix", "Otta", "Thor", "Phynx", "deployed", "resonance"]))
        check("daybee row in scan has stars and gear", sc["players"][0].get("mythic") == 15 and sc["players"][0].get("gear", "").startswith("Dragoon"))
        check("corrected mystling in the scan", sc["players"][0].get("mystling") == "Witch ★9", json.dumps(sc["players"][0])[:200])
        check("opponent scan has rune names (no qualities)", "Sharp Arrow" in json.dumps(sc["players"][0].get("runes", {})), json.dumps(sc["players"][0].get("runes"))[:200])
        # a second video where daybee's gear wasn't read: the gear already on file stays (it used to be wiped)
        await pg.evaluate("window.__noGear = true; window.__mystUnclear = false; window.__artUnclear = false")
        await pg.select_option("#vid-target", "__us")
        await pg.click("#btn-vid-read")
        await pg.wait_for_function("document.querySelector('#vid-status').textContent.startsWith('Found')", timeout=180000)
        n2 = await pg.locator("#vid-result .vcard").count()
        for k in range(1, n2): await pg.uncheck(f"#vid-result .vcard >> nth={k} >> .von")
        await pg.click("#vid-save"); await pg.wait_for_timeout(1200)
        mb2 = (await pg.evaluate("window.__store.get('roster/m-daybee')")).get("mainBuild", {})
        check("gear not read this time: daybee keeps the gear on file", mb2.get("gear", {}).get("boots", {}).get("set") == "Dragoon" and len(mb2.get("gear", {})) == 6, json.dumps(mb2.get("gear"))[:200])
        check("…and the runes on file", sum(len(v) for v in mb2.get("runes", {}).values()) >= 9)
        # limits: platform allows 3 images per call; one batch fails once (split into singles); screen 5 always fails
        c2 = await b.new_context(viewport={"width": 390, "height": 844})
        await c2.add_init_script(MOCK + SCRIPT + "window.__failOnce = 7; window.__failAlways = 5;")
        p2 = await c2.new_page(); p2.on("pageerror", lambda e: errs.append(str(e)))
        await p2.add_init_script("")
        await p2.goto("http://127.0.0.1:8795/index.html#roster"); await p2.wait_for_timeout(2500)
        await p2.evaluate("(async()=>{const s=await window.claude.use('sample'); s.limits = async()=>({images:{maxCount:3,maxInputBytes:2e7,mediaTypes:['image/jpeg']}});})()")
        await p2.click("#btn-vid"); await p2.set_input_files("#vid-file", FIX); await p2.click("#btn-vid-read")
        await p2.wait_for_function("document.querySelector('#vid-status').textContent.startsWith('Found')", timeout=180000)
        bt = await p2.evaluate("window.__batches")
        check("batches respect the platform's image limit (3)", max(bt) <= 3, str(bt))
        msg = await p2.inner_text("#vid-result .hintbox.err")
        check("one unreadable screen reported with the reason", msg.startswith("1 of") and "picture was rejected" in msg, msg)
        c2v = (await p2.evaluate(CARDS))[0]["vals"]
        check("failed-once batch recovered by reading singly (artifacts still complete)", c2v.get("mythic") == "15" and c2v.get("leg") == "15", json.dumps(c2v)[:200])
        check("mystling missing because screen 5 failed", c2v.get("myst") == "")
        await p2.evaluate("window.__failAlways = 0")
        await p2.click("#vid-result .hintbox.err button"); await p2.wait_for_timeout(1500)
        check("retry reads just the unread screen and fills it in", await p2.locator("#vid-result .hintbox.err").count() == 0 and (await p2.evaluate(CARDS))[0]["vals"].get("myst") == "Death Mage")
        # Stop works mid-read, right away
        c3 = await b.new_context(viewport={"width": 390, "height": 844}); await c3.add_init_script(MOCK + SCRIPT)
        p3 = await c3.new_page(); p3.on("pageerror", lambda e: errs.append(str(e)))
        await p3.goto("http://127.0.0.1:8795/index.html#roster"); await p3.wait_for_timeout(2500)
        await p3.click("#btn-vid"); await p3.set_input_files("#vid-file", FIX); await p3.click("#btn-vid-read")
        await p3.wait_for_function("document.querySelector('#vid-status').textContent.includes('Finding screens')", timeout=30000)
        check("a small preview plays while reading", await p3.is_visible("#vid-preview-box video"))
        await p3.wait_for_timeout(1500); await p3.click("#btn-vid-stop"); await p3.wait_for_timeout(700)
        st3 = await p3.inner_text("#vid-status")
        check("Stop stops within a second", st3 == "Stopped.", st3)
        check("preview removed after stopping", await p3.is_hidden("#vid-preview-box"))
        await c3.close()
        # a browser that won't play it falls back to jumping frame by frame
        c4 = await b.new_context(viewport={"width": 390, "height": 844})
        await c4.add_init_script(MOCK + SCRIPT + "HTMLMediaElement.prototype.play = function () { return Promise.reject(new Error('NotAllowed')); };")
        p4 = await c4.new_page(); p4.on("pageerror", lambda e: errs.append(str(e)))
        await p4.goto("http://127.0.0.1:8795/index.html#roster"); await p4.wait_for_timeout(2500)
        await p4.click("#btn-vid"); await p4.set_input_files("#vid-file", FIX); await p4.click("#btn-vid-read")
        await p4.wait_for_function("document.querySelector('#vid-status').textContent.startsWith('Found')", timeout=300000)
        st4 = await p4.inner_text("#vid-status")
        check("fallback finds the same screens", st4.startswith("Found 1") and "2 players" in st4, st4)
        await c4.close()
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

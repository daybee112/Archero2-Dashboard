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
# What Claude "sees" on each still, by position (the fixture's screens, checked by eye):
# 1 list, 2-8 daybee (namecard, gear, runes, mystling, 3 artifact pages), 9 list, 10+ thesithlor
SCRIPT = r"""
window.__vidScript = (i) => {
  const A = (list) => ({ type: "artifacts", artifacts: list.map(([name, tier, stars]) => ({ name, tier, stars })) });
  const gear = (set) => ({ type: "gear", gear: Object.fromEntries(["weapon","amulet","ring","helmet","armor","boots"].map(k => [k, { set: k === "boots" && set === "mix" ? "Oracle" : (set === "mix" ? "Dragoon" : set), quality: "Chaotic" }])) });
  const map = {
    1: { type: "roster_list" },
    2: { type: "namecard", name: "daybee", power_m: 11.07 },
    3: gear("Dragoon"),
    4: { type: "runes" },
    5: { type: "mystling", mystling: { name: "Death Mage", stars: 14 } },
    6: A([["Golden Fleece","Mythic",5],["Goldfinger","Mythic",4],["Golden Mask","Mythic",3],["Tidal Conch","Mythic",2],["Demon King's Eye","Mythic",1],["Voidblade","Mythic",0]]),
    7: A([["Voidblade","Mythic",0],["Magic Harp","Legendary",3],["Dragon Heart","Legendary",3],["Bull Skull","Legendary",3]]),
    8: A([["Healing Grail","Legendary",3],["Attack Horn","Legendary",3],["Some Epic Thing","Epic",2]]),
    9: { type: "roster_list" },
    10: { type: "namecard", name: "NotAMember", power_m: 10.15 },
    11: gear("mix"),
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
        c = await b.new_context(viewport={"width": 1280, "height": 900}); await c.add_init_script(MOCK + SCRIPT)
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
        n = int(stxt.split()[1])
        check("finds the screens in the 40s clip (about 19, as the offline check found)", 16 <= n <= 22, stxt)
        batches = await pg.evaluate("window.__batches")
        check("read in batches of at most 6", batches and max(batches) <= 6 and sum(batches) == n, str(batches))
        rows = await pg.eval_on_selector_all("#vid-result tbody tr", "r=>r.map(x=>x.innerText.replace(/\\s+/g,' '))")
        print(rows)
        check("two players found", len(rows) == 2, str(len(rows)))
        check("daybee: power and artifact totals (Mythic 15, Leg 15) with no double count", "11.07M" in rows[0] and "→ 15 / 15" in rows[0] and "incomplete" not in rows[0], rows[0])
        check("daybee: mystling", "Death Mage ★14" in rows[0])
        check("unknown name flagged", "not on the roster" in rows[1])
        dis = await pg.eval_on_selector_all("#vid-result tbody input", "i=>i.map(x=>x.disabled)")
        check("unknown player can't be ticked", dis == [False, True], str(dis))
        check("screens gallery present", await pg.locator("#vid-result details img").count() == n)
        await pg.click("#vid-result .btn"); await pg.wait_for_timeout(800)
        doc = await pg.evaluate("window.__store.get('roster/m-daybee')")
        check("roster updated: power, artifacts, mystling", doc and doc["power"]["m"] == 11.07 and doc["power"]["src"] == "profile video" and doc["artifacts"]["mythic"] == 15 and doc["artifacts"]["leg"] == 15 and "Death Mage" in doc.get("mystlingSeen", ""), json.dumps(doc)[:300] if doc else "none")
        ev = await pg.evaluate("[...window.__store.entries()].filter(([k])=>k.startsWith('audit/u-officer/months')).flatMap(([k,v])=>v.events||[])")
        check("logged in the activity log", any("profile video" in (e.get("detail") or "") for e in ev), str([e.get("detail") for e in ev][-3:]))

        # opponent: new guild, scan saved, no characters
        await pg.select_option("#vid-target", "__new"); await pg.fill("#vid-newopp", "TestGuild")
        await pg.evaluate("document.querySelector('#vid-status').textContent = ''")
        await pg.click("#btn-vid-read")
        await pg.wait_for_function("document.querySelector('#vid-status').textContent.startsWith('Found')", timeout=180000)
        await pg.wait_for_timeout(300)
        rows = await pg.eval_on_selector_all("#vid-result tbody tr", "r=>r.map(x=>x.innerText.replace(/\\s+/g,' '))")
        check("opponent rows show gear, mixed noted", "Dragoon (mixed)" in rows[1] and "Oracle boots" in rows[1], rows[1])
        check("opponent: both players can be ticked", await pg.eval_on_selector_all("#vid-result tbody input", "i=>i.every(x=>!x.disabled)"))
        await pg.click("#vid-result .btn"); await pg.wait_for_timeout(800)
        scans = await pg.evaluate("[...window.__store.entries()].filter(([k])=>k.includes('/scans/')).map(([k,v])=>v)")
        sc = scans[-1] if scans else {}
        check("scan saved with source profile video", sc.get("source") == "profile video" and len(sc.get("players", [])) == 2, json.dumps(sc)[:300])
        txt = json.dumps(sc)
        check("no character names in the scan", not any(ch in txt for ch in ["Helix", "Otta", "Thor", "Phynx", "deployed", "resonance"]))
        check("daybee row in scan has stars and gear", sc["players"][0].get("mythic") == 15 and sc["players"][0].get("gear", "").startswith("Dragoon"))
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
        rows2 = await p2.eval_on_selector_all("#vid-result tbody tr", "r=>r.map(x=>x.innerText.replace(/\\s+/g,' '))")
        check("failed-once batch recovered by reading singly (artifacts still complete)", rows2 and "→ 15 / 15" in rows2[0], str(rows2[:1]))
        check("mystling missing because screen 5 failed", rows2 and "Death Mage" not in rows2[0])
        await p2.evaluate("window.__failAlways = 0")
        await p2.click("#vid-result .hintbox.err button"); await p2.wait_for_timeout(1500)
        check("retry reads just the unread screen and fills it in", await p2.locator("#vid-result .hintbox.err").count() == 0 and "Death Mage" in await p2.inner_text("#vid-result tbody"))
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

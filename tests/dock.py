import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
FIX = _os.path.join(HERE, "fixtures", "presets", "teaminfo-left.mp4")   # Daby's Nov 25 Team Info recording (Left lane, 8 presets), H.264, half size
# Lanes and presets video: Team Info lists + presets in order -> matched to players -> mystling/gear/runes read on the device ->
# review -> saved as Expedition presets. Claude's answers are scripted from what each still shows (checked by eye).
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8815), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
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

CARD = "#vid-result .vcard[data-key=p1]"
async def wait_done(pg):
    await pg.wait_for_function("/^Found|went wrong|Stopped/.test(document.querySelector('#vid-status').textContent)", timeout=240000)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--autoplay-policy=no-user-gesture-required"])
        errs = []
        c = await b.new_context(viewport={"width": 390, "height": 844}); await c.add_init_script("window.__expose = true;" + MOCK + SAMPLE)
        pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8815/index.html#expedition"); await pg.wait_for_timeout(2500)
        await pg.click("#exp-new-week"); await pg.wait_for_timeout(100)
        for i, (n, pw) in enumerate([("Unity", "1.19B"), ("Happiness", "340M"), ("Holymoly", "600M")]):
            await pg.fill(f"#exp-new-week-box .nw-round:nth-child({i+1}) input >> nth=0", n)
            await pg.fill(f"#exp-new-week-box .nw-round:nth-child({i+1}) input >> nth=1", pw)
        await pg.click("#exp-new-week-box >> text=Create week"); await pg.wait_for_timeout(800)
        check("no bar before a read", not await pg.is_visible("#vid-dock"))
        await pg.click("#exp-sub button[data-sub=uploads]"); await pg.wait_for_timeout(300)
        await pg.click("#exp-uploads .upl:has-text('Our lanes and presets') >> nth=0 >> button"); await pg.wait_for_timeout(300)
        await pg.set_input_files("#vid-file", FIX); await pg.click("#btn-vid-read")
        await pg.wait_for_function("document.querySelector('#vid-dock-vid video') && /Finding screens/.test(document.querySelector('#vid-dock-txt').textContent)", timeout=30000)
        check("bar shows while reading, holding the video", await pg.is_visible("#vid-dock") and await pg.is_visible("#vid-dock-vid video"))
        check("on the reader's own page: no Open, just Stop", not await pg.is_visible("#vid-dock-open") and await pg.is_visible("#vid-dock-stop"))
        # switch to the main roster mid-read (what Daby did)
        await pg.click("#tab-roster"); await pg.wait_for_timeout(1500)
        t1 = await pg.evaluate("document.querySelector('#vid-dock-vid video')?.currentTime || 0")
        await pg.wait_for_timeout(2500)
        t2 = await pg.evaluate("document.querySelector('#vid-dock-vid video')?.currentTime || 0")
        check("on another tab: the bar is pinned and visible", await pg.is_visible("#vid-dock") and await pg.is_visible("#vid-dock-open"))
        check("bar stays on screen when scrolled down", await pg.evaluate("window.scrollTo(0, document.body.scrollHeight), (() => { const r = document.querySelector('#vid-dock').getBoundingClientRect(); return r.bottom <= innerHeight && r.top >= 0; })()"))
        check("the video keeps going on another tab", t2 > t1 or await pg.evaluate("/Reading|Matching|Found/.test(document.querySelector('#vid-status').textContent)"), f"{t1} -> {t2}")
        await wait_done(pg)
        await pg.wait_for_timeout(300)
        txt = await pg.inner_text("#vid-dock")
        check("finished while away: the bar says the review is ready", "Review ready" in txt and await pg.is_visible("#vid-dock-open"), txt)
        check("bar text is the Review button", await pg.inner_text("#vid-dock-open") == "Review")
        await pg.click("#vid-dock-open"); await pg.wait_for_timeout(800)
        check("Review opens Expedition > Uploads with the review", "#expedition" in pg.url and await pg.is_visible(CARD), pg.url)
        check("the bar goes away once you're looking at it", not await pg.is_visible("#vid-dock"))
        await pg.click("#vid-save"); await pg.wait_for_timeout(3000)
        rd = await pg.evaluate("window.__store.get([...window.__store.keys()].find(k => /^expedition\\/2026-11-24\\/rounds\\/1$/.test(k)))") or {}
        check("saving still works after the trip", (rd.get("uploads") or {}).get("presets", {}).get("players") == 8, json.dumps(rd.get("uploads")))
        # Stop from the bar, from another tab
        await pg.click("#exp-uploads .upl:has-text('Our lanes and presets') >> nth=1 >> button:has-text('Upload')") if await pg.locator("#exp-uploads .upl:has-text('Our lanes and presets') >> nth=1 >> button:has-text('Upload')").count() else await pg.click("#exp-uploads .upl:has-text('Our lanes and presets') >> nth=1 >> button >> nth=-1")
        await pg.wait_for_timeout(300)
        await pg.set_input_files("#vid-file", FIX); await pg.click("#btn-vid-read")
        await pg.wait_for_function("document.querySelector('#vid-dock-vid video')", timeout=30000)
        await pg.click("#tab-builds"); await pg.wait_for_timeout(500)
        await pg.click("#vid-dock-stop"); await pg.wait_for_timeout(1500)
        check("Stop in the bar stops the read and hides the bar", await pg.inner_text("#vid-status") == "Stopped." and not await pg.is_visible("#vid-dock"), await pg.inner_text("#vid-status"))
        # profile video from the Roster, then off to Expedition
        await pg.click("#tab-roster"); await pg.wait_for_timeout(500)
        await pg.click("#btn-vid"); await pg.wait_for_timeout(300)
        check("Roster's import opens the reader on the Roster again", await pg.evaluate("!!document.querySelector('#view-roster #vid-panel') && !document.querySelector('#vid-panel').hidden"))
        check("no sideways scroll with the bar", await pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"))
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

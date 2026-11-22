import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import asyncio, threading, http.server, functools, base64, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8772), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
res=[]
def check(n,c,x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
async def grab(pg, btn_selector, out):
    await pg.click(btn_selector)
    for _ in range(80):
        await pg.wait_for_timeout(100)
        if await pg.locator(".imgov img").count(): break
    if await pg.locator(".imgov img").count():
        data = await pg.evaluate("""async () => { const img = document.querySelector('.imgov img'); const b = await (await fetch(img.src)).blob();
          return await new Promise(r => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(b); }); }""")
        open(out, "wb").write(base64.b64decode(data.split(",")[1]))
        await pg.click(".imgov >> text=Close"); return "overlay"
    return "copied"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": 1280, "height": 900}); await ctx.add_init_script(open(_os.path.join(HERE, "mock.js")).read() + ";Object.defineProperty(navigator, 'clipboard', { value: undefined });")
        pg = await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8772/index.html#expedition"); await pg.wait_for_timeout(1500)
        await pg.click("#exp-rounds .buildtabs button:nth-child(1)"); await pg.wait_for_timeout(200)
        t = await pg.inner_text("#exp-rounds")
        check("R1 shows round results", "round results" in t.lower() and "WON 2–1" in t)
        r = await grab(pg, "#exp-rounds >> text=Lineup image", "/tmp/shots/img-lineup.png"); check("lineup image", r in ("overlay","copied"), r)
        r = await grab(pg, "#exp-rounds >> text=Results image", "/tmp/shots/img-results.png"); check("results image", r in ("overlay","copied"), r)
        # officer posts a new message + a note on R3
        await pg.click("#exp-rounds .buildtabs button:nth-child(3)"); await pg.wait_for_timeout(200)
        await pg.click("#exp-rounds details.notes > summary"); await pg.click("#exp-rounds .notes summary >> text=Add a note"); await pg.fill("#exp-rounds .notes textarea", "From the strategy chat: keep Hansi218 in Middle as the Dragoon control.")
        await pg.click("#exp-rounds .notes >> text=Add note"); await pg.wait_for_timeout(400)
        nd = await pg.evaluate("JSON.stringify(window.__store.get('notes/2026-11-16-r3'))")
        check("note saved", nd and "Dragoon control" in nd and '"kind":"note"' in nd)
        t = await pg.inner_text("#exp-rounds")
        check("note listed", "Notes & reasoning (1)" in t or "NOTES & REASONING (1)" in t.upper())
        await pg.click("#exp-sub button[data-sub=players]"); await pg.wait_for_timeout(200)
        so = await pg.locator("#exp-players .so").count(); check("notable badges are rare", so <= 12, str(so))
        print("   notes shown:", await pg.eval_on_selector_all("#exp-players .so", "s=>s.map(x=>x.closest('tr').children[0].innerText+': '+x.innerText)"))
        r = await grab(pg, "#exp-players >> text=Copy as image", "/tmp/shots/img-players.png"); check("players image", r in ("overlay","copied"), r)
        await pg.click("#exp-players tbody tr:first-child"); await pg.wait_for_timeout(200)
        r = await grab(pg, "#exp-players >> text=Copy as image", "/tmp/shots/img-player.png"); check("player detail image", r in ("overlay","copied"), r)
        await pg.click("#tab-roster"); await pg.wait_for_timeout(300)
        r = await grab(pg, "#roster-img >> text=Copy as image", "/tmp/shots/img-roster.png"); check("roster image", r in ("overlay","copied"), r)
        await pg.click("#tab-expedition"); await pg.click("#exp-sub button[data-sub=rounds]"); await pg.wait_for_timeout(200)
        t = await pg.inner_text("#exp-week-head")
        check("standings not links", await pg.locator("#exp-week-head .chip .linkbtn").count() == 0)
        check("no JS errors", not errs, str(errs))
        await b.close()
    print(sum(res), "/", len(res))
asyncio.run(main())

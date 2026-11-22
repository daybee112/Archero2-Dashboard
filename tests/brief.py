import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import asyncio, threading, http.server, functools, base64
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8773), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
res=[]
def check(n,c,x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": 1280, "height": 900}); await ctx.add_init_script(open(_os.path.join(HERE, "mock.js")).read() + ";Object.defineProperty(navigator, 'clipboard', { value: undefined });")
        pg = await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        # the officer message card shows on unplayed rounds: serve R2 as unplayed
        import json
        async def unplay(route):
            d = json.load(open(APP + "/expedition-seed.json"))
            r = [w for w in d["weeks"] if w["id"] == "2026-11-16"][0]["rounds"][1]
            for k in ("result", "score", "laneResults", "stats", "theirStats"): r.pop(k, None)
            r["status"] = "planned"; r["date"] = "2099-01-01"
            await route.fulfill(status=200, content_type="application/json", body=json.dumps(d))
        await pg.route("**/expedition-seed.json*", unplay)
        await pg.goto("http://127.0.0.1:8773/index.html"); await pg.wait_for_timeout(1500)
        check("lands on roster", not await pg.is_hidden("#view-roster") and await pg.is_hidden("#view-builds"))
        check("roster tab marked current", await pg.get_attribute("#tab-roster", "aria-current") == "page")
        check("roster rendered", await pg.locator("#roster-table tbody tr").count() > 30)
        await pg.click("#tab-expedition"); await pg.wait_for_timeout(500)
        await pg.click("#exp-rounds .buildtabs button:nth-child(2)"); await pg.wait_for_timeout(300)
        card = pg.locator(".briefing")
        check("md headers", await card.locator(".md-head").count() >= 6)
        check("md bullets", await card.locator(".md-li").count() >= 30)
        check("bold renders (no ** shown)", "**" not in await card.inner_text())
        check("clamped long message", await card.locator(".brief-body.clamped").count() == 1)
        await card.locator(".brief-body").screenshot(path="/tmp/shots/brief-card.png")
        await card.locator("text=Show the full message").click(); await pg.wait_for_timeout(200)
        check("expands", await card.locator(".brief-body.clamped").count() == 0)
        await card.locator("text=Copy as image").click(); await pg.wait_for_timeout(800)
        data = await pg.evaluate("""async () => { const img = document.querySelector('.imgov img'); const b = await (await fetch(img.src)).blob();
          return await new Promise(r => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(b); }); }""")
        open("/tmp/shots/brief-img.png","wb").write(base64.b64decode(data.split(",")[1]))
        check("no JS errors", not errs, str(errs))
        await b.close()
    print(sum(res), "/", len(res))
asyncio.run(main())

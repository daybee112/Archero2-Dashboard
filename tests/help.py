import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import asyncio, threading, http.server, functools
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8774), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
res=[]
def check(n,c,x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for vw,name in [((1280,900),"desk"),((390,844),"phone")]:
            ctx = await b.new_context(viewport={"width": vw[0], "height": vw[1]}); await ctx.add_init_script("window.__firstVisit = true;" + open(_os.path.join(HERE, "mock.js")).read())
            pg = await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
            # first visit with a plain link: opens on Help with a welcome line; later plain visits open on the Roster
            await pg.goto("http://127.0.0.1:8774/index.html"); await pg.wait_for_timeout(1500)
            check(f"{name}: first visit opens on Help", not await pg.is_hidden("#view-help") and await pg.is_hidden("#view-roster") and pg.url.endswith("#help"))
            check(f"{name}: welcome line", "Next time, the dashboard opens on the Roster." in await pg.inner_text("#help-welcome"))
            await pg.goto("http://127.0.0.1:8774/index.html"); await pg.wait_for_timeout(1200)
            check(f"{name}: second visit opens on the Roster, no welcome", not await pg.is_hidden("#view-roster") and await pg.locator("#help-welcome").count() == 0)
            await ctx.close()
            # first visit straight to a tab: stays on that tab; the Roster hint still points to Help
            ctx = await b.new_context(viewport={"width": vw[0], "height": vw[1]}); await ctx.add_init_script("window.__firstVisit = true;" + open(_os.path.join(HERE, "mock.js")).read())
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto("http://127.0.0.1:8774/index.html#expedition"); await pg.wait_for_timeout(1500)
            check(f"{name}: a link to a tab isn't redirected", not await pg.is_hidden("#view-expedition") and await pg.is_hidden("#view-help"))
            await pg.goto("http://127.0.0.1:8774/index.html#roster"); await pg.wait_for_timeout(1200)
            check(f"{name}: hint on roster", await pg.locator("#view-roster .help-hint").count() == 1)
            await pg.click("#view-roster .help-hint a"); await pg.wait_for_timeout(300)
            check(f"{name}: help view open", not await pg.is_hidden("#view-help"))
            check(f"{name}: hint gone", await pg.locator(".help-hint").count() == 0)
            await pg.screenshot(path=f"/tmp/shots/help-{name}.png", full_page=False)
            await pg.click("#view-help summary >> text=Key terms"); await pg.wait_for_timeout(200)
            check(f"{name}: details open", await pg.locator("#view-help details[open]").count() == 1)
            await pg.click("#view-help a[data-go=builds]"); await pg.wait_for_timeout(300)
            check(f"{name}: in-guide link works", not await pg.is_hidden("#view-builds"))
            await pg.reload(); await pg.wait_for_timeout(1200)
            await pg.click("#tab-roster"); await pg.wait_for_timeout(300)
            check(f"{name}: hint stays dismissed", await pg.locator(".help-hint").count() == 0)
            check(f"{name}: no JS errors", not errs, str(errs))
            await ctx.close()
        await b.close()
    print(sum(res), "/", len(res))
asyncio.run(main())

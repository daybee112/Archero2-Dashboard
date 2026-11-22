import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import asyncio, threading, http.server, functools
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8771), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1); await ctx.add_init_script(open(_os.path.join(HERE, "mock.js")).read())
        pg = await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8771/index.html#expedition"); await pg.wait_for_timeout(1500)
        await pg.click("#exp-sub button[data-sub=opponents]"); await pg.wait_for_timeout(300)
        await pg.evaluate("[...document.querySelectorAll('#exp-opponents details.inv')].find(d=>d.querySelector('summary').innerText.startsWith('Holymoly')).open=true"); await pg.wait_for_timeout(300)
        h = await pg.evaluate("document.documentElement.scrollHeight")
        await pg.set_viewport_size({"width": 1280, "height": min(h, 4200)}); await pg.wait_for_timeout(300)
        await pg.screenshot(path="/tmp/shots/opponents-page.png")
        await pg.set_viewport_size({"width": 1280, "height": 900})
        await pg.click("#exp-sub button[data-sub=findings]"); await pg.wait_for_timeout(300)
        t = await pg.inner_text("#exp-findings"); print("assumptions" in t.lower(), "Win estimate" in t or "WIN ESTIMATE" in t, errs, h)
        await b.close()
asyncio.run(main())

import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import asyncio, threading, http.server, functools
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8776), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": 1280, "height": 900}); await ctx.add_init_script(open(_os.path.join(HERE, "mock.js")).read() + ";Date.now = () => Date.parse('2026-11-22T06:45:00Z');")
        pg = await ctx.new_page()
        await pg.goto("http://127.0.0.1:8776/index.html#expedition"); await pg.wait_for_timeout(1500)
        await pg.click("#exp-rounds .buildtabs button:nth-child(3)"); await pg.wait_for_timeout(300)
        await pg.add_style_tag(content=".topbar{position:static !important}")
        print([x for x in await pg.locator(".lanecard.ours .prow").all_inner_texts() if "Terminus" in x])
        await pg.locator("#exp-rounds .panel:nth-child(2)").screenshot(path="/tmp/shots/r3-panel.png")
        await b.close()
asyncio.run(main())

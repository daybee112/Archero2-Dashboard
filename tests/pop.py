import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import asyncio, threading, http.server, functools
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8769), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": 1200, "height": 700}); await ctx.add_init_script(open(_os.path.join(HERE, "mock.js")).read())
        pg = await ctx.new_page(); await pg.goto("http://127.0.0.1:8769/index.html#roster"); await pg.wait_for_timeout(1500)
        await pg.fill("#roster-search", "gaga"); await pg.wait_for_timeout(100)
        await pg.click("#roster-body tr:first-child .gchip:nth-child(2)"); await pg.wait_for_timeout(200)
        await pg.screenshot(path="/tmp/shots/gear-pop.png", clip={"x": 60, "y": 150, "width": 1080, "height": 380})
        await b.close()
asyncio.run(main())

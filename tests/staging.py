import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
# Staging copy: env.js decides live vs staging; staging shows a banner and a prefixed title, live shows neither.
import asyncio, threading, http.server, functools
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8794), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read()
STAGING_ENV = open(_os.path.join(HERE, "..", "tools", "staging", "env.js")).read()
res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs = []
        c = await b.new_context(viewport={"width": 1280, "height": 900}); await c.add_init_script(MOCK)
        pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8794/index.html#roster"); await pg.wait_for_timeout(3000)
        check("live: no staging banner", not await pg.is_visible("#envbar"))
        check("live: normal title", not (await pg.title()).startswith("STAGING"), await pg.title())
        s = await b.new_context(viewport={"width": 390, "height": 844}); await s.add_init_script(MOCK)
        await s.route("**/env.js", lambda r: r.fulfill(status=200, content_type="text/javascript", body=STAGING_ENV))
        ps = await s.new_page(); ps.on("pageerror", lambda e: errs.append(str(e)))
        await ps.goto("http://127.0.0.1:8794/index.html#roster"); await ps.wait_for_timeout(3000)
        check("staging: banner shown", await ps.is_visible("#envbar"))
        check("staging: title says STAGING", (await ps.title()).startswith("STAGING"), await ps.title())
        check("staging: roster still loads", await ps.locator("#tab-roster").count() == 1)
        check("no page errors", not errs, str(errs[:3]))
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

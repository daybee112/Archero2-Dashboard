import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import asyncio, threading, http.server, functools
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8767), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page(); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8767/index.html#roster"); await pg.wait_for_timeout(1200)
        names = await pg.eval_on_selector_all("#roster-body tr td:first-child", "t=>t.map(x=>x.innerText)")
        print(len(names), [n for n in names if 'aga' in n.lower()], errs)
        await pg.fill("#roster-search","gaga"); await pg.wait_for_timeout(100)
        print(await pg.inner_text("#roster-body"))
        await b.close()
asyncio.run(main())

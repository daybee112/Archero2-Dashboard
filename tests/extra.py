import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import asyncio, threading, http.server, functools
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8766), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for w, hgt, name in [(1200, 900, "desk"), (390, 844, "mob")]:
            pg = await b.new_page(viewport={"width": w, "height": hgt})
            await pg.goto("http://127.0.0.1:8766/index.html#roster"); await pg.wait_for_timeout(1200)
            await pg.click("#roster-head th:nth-child(6) button"); await pg.wait_for_timeout(100)
            hs = await pg.eval_on_selector_all("#roster-head .sortbtn", "bs=>bs.map(b=>[b.innerText.replace(/\\n/g,' | '), Math.round(b.getBoundingClientRect().height)])")
            lh = await pg.eval_on_selector("#roster-head .sortbtn", "b=>parseFloat(getComputedStyle(b).lineHeight)")
            print(name, "line height", lh, "max lines", max(round(h/lh) for _, h in hs)); print(hs)
            await pg.evaluate("window.scrollTo(0, document.getElementById('roster-table').getBoundingClientRect().top + window.scrollY + 1800)")
            await pg.wait_for_timeout(200)
            await pg.screenshot(path=f"/tmp/shots/{name}-sticky.png")
            pos = await pg.evaluate("[document.querySelector('.topbar').getBoundingClientRect().bottom, document.querySelector('#roster-table thead').getBoundingClientRect().top]")
            print(name, "topbar bottom vs thead top", pos)
            await pg.fill("#roster-search", "gaga"); await pg.click("#roster-body tr:first-child"); await pg.wait_for_timeout(500)
            if name == "desk": print((await pg.inner_text("#member-panel"))[600:1200])
        await b.close()
asyncio.run(main())

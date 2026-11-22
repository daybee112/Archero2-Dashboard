import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import asyncio, threading, http.server, functools
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8768), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK=open(_os.path.join(HERE, "mock.js")).read()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for w in (1200, 390):
          ctx = await b.new_context(viewport={"width": w, "height": 900}); await ctx.add_init_script(MOCK)
          pg = await ctx.new_page(); errs=[]
          pg.on("pageerror", lambda e: errs.append(str(e)))
          await pg.goto("http://127.0.0.1:8768/index.html#roster"); await pg.wait_for_timeout(1500)
          for i in range(1, 12):
            await pg.click(f"#roster-head th:nth-child({i}) button"); await pg.wait_for_timeout(60)
            names = await pg.eval_on_selector_all("#roster-body tr td:first-child", "t=>t.map(x=>x.innerText)")
            if not any('Gaga' in n for n in names) or len(names)!=43: print(w, "col", i, len(names))
          # visible rows within the scroll box: is Gaga reachable by scrolling?
          box = await pg.evaluate("(()=>{const w=document.getElementById('roster-wrap');return [w.clientHeight,w.scrollHeight]})()")
          print(w, "scroll box", box, errs)
          await ctx.close()
        await b.close()
asyncio.run(main())

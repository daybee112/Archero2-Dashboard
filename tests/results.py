import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import asyncio, threading, http.server, functools, base64
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8777), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
res=[]
def check(n,c,x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": 1280, "height": 900}); await ctx.add_init_script(open(_os.path.join(HERE, "mock.js")).read() + ";Object.defineProperty(navigator, 'clipboard', { value: undefined });")
        pg = await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8777/index.html#expedition"); await pg.wait_for_timeout(1500)
        await pg.add_style_tag(content=".topbar{position:static !important}")
        for n in (1, 2, 3):
            await pg.click(f"#exp-rounds .buildtabs button:nth-child({n})"); await pg.wait_for_timeout(250)
            t = await pg.inner_text("#exp-rounds .panel:nth-child(2)")
            check(f"R{n}: results card shown, no officer message card", "round results" in t.lower() and await pg.locator(".briefing:not(.results)").count() == 0)
            check(f"R{n}: lanes in order", t.find("Left (anchor") < t.find("Middle (anchor") < t.find("Right (anchor") and t.find("Left (anchor") > 0)
        t = await pg.inner_text(".briefing.results")
        check("R3 text: score + Terminus DPS", "WON 3–0" in t and "Terminus323 · Dragoon · 118K DPS" in t, t[:300])
        await pg.click(".briefing.results summary"); await pg.wait_for_timeout(200)
        check("plan message available folded", "R3 vs Holymoly: any win clinches" in await pg.inner_text(".briefing.results details"))
        await pg.locator(".briefing.results").screenshot(path="/tmp/shots/results-card.png")
        await pg.click(".briefing.results >> text=Copy as image"); await pg.wait_for_timeout(800)
        data = await pg.evaluate("""async () => { const img = document.querySelector('.imgov img'); const b = await (await fetch(img.src)).blob();
          return await new Promise(r => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(b); }); }""")
        open("/tmp/shots/results-img.png","wb").write(base64.b64decode(data.split(",")[1]))
        check("image rendered", len(data) > 10000)
        theirs = await pg.locator(".lanecard:not(.ours) .prow").all_inner_texts()
        check("R3 opponent rows show damage · time · DPS", len(theirs) == 24 and all("s ·" in x and "/s" in x for x in theirs), str(theirs[:3]))
        check("no JS errors", not errs, str(errs))
        await b.close()
    print(sum(res), "/", len(res))
asyncio.run(main())

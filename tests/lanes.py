import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import asyncio, threading, http.server, functools
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8775), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
res=[]
def check(n,c,x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for vw,name in [((1280,900),"desk"),((390,844),"phone")]:
            ctx = await b.new_context(viewport={"width": vw[0], "height": vw[1]}); await ctx.add_init_script(open(_os.path.join(HERE, "mock.js")).read() + ";Date.now = () => Date.parse('2026-11-22T06:45:00Z');")
            pg = await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto("http://127.0.0.1:8775/index.html"); await pg.wait_for_timeout(1500)
            # single sort then remove
            await pg.click("#roster-table thead th:nth-child(7)"); await pg.wait_for_timeout(150)
            t = await pg.inner_text("#roster-sort")
            check(f"{name}: single sort removable", await pg.locator("#roster-sort .sortx").count() >= 1 and "Reset to power" in t, t)
            await pg.click("#roster-sort >> text=Reset to power"); await pg.wait_for_timeout(150)
            check(f"{name}: back to power", "Power" in await pg.inner_text("#roster-sort") and await pg.locator("#roster-sort .sortx").count() == 0)
            await pg.click("#tab-expedition"); await pg.wait_for_timeout(400)
            await pg.click("#exp-rounds .buildtabs button:nth-child(3)"); await pg.wait_for_timeout(300)
            hdr = await pg.inner_text("#exp-rounds .panel:nth-child(2) .chip")
            check(f"{name}: R3 shows Won 3-0", hdr.startswith("Won 3-0"), hdr)
            ls = await pg.evaluate("(() => { const now = Date.now(); return [now, 0]; })()")
            ours = await pg.locator(".lanecard.ours .prow").all_inner_texts()
            check(f"{name}: played round shows real stats", sum("/s" in x and "· 9s ·" in x or "· 11s ·" in x for x in ours) == len(ours) == 24, str(ours[:3]))
            check(f"{name}: Terminus323 in middle", any("Terminus323" in x for x in ours) and not any("DrFuko" in x for x in ours))
            col = pg.locator(".lanecol").first
            boxes = [await c.bounding_box() for c in await col.locator(".lanecard").all()]
            side = abs(boxes[0]["y"] - boxes[1]["y"]) < 5
            check(f"{name}: side by side on desktop / stacked on phone", side if name == "desk" else not side)
            await pg.locator(".laneboard").screenshot(path=f"/tmp/shots/lanes-{name}.png")
            check(f"{name}: no JS errors", not errs, str(errs))
            await ctx.close()
        await b.close()
    print(sum(res), "/", len(res))
asyncio.run(main())

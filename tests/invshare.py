import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import asyncio, threading, http.server, functools, json
from playwright.async_api import async_playwright
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8786), functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP))
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK = open(_os.path.join(HERE, "mock.js")).read(); res = []
def check(n, c, x=""): res.append(c); print("PASS" if c else "FAIL", n, x)
FUT = 4102444800000  # far future timestamp
async def page(b, member=False, seed=""):
    ctx = await b.new_context(viewport={"width": 1400, "height": 900}); await ctx.add_init_script(("window.__member = true;" if member else "") + MOCK)
    if seed: await ctx.add_init_script(seed)
    pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.goto("http://127.0.0.1:8786/index.html#roster"); await pg.wait_for_timeout(1500)
    return pg, errs
def row(name): return f"(()=>[...document.querySelectorAll('#roster-body tr')].find(r=>r.querySelector('b')?.innerText.trim()==='{name}'))()"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        # ---------- officer
        pg, errs = await page(b)
        heads = await pg.eval_on_selector_all("#roster-head th", "ths=>ths.map(t=>t.innerText.replace(/\\s+/g,' ').trim())")
        check("roster has Account and Inventory columns", any(h.startswith("Account") for h in heads) and any(h.startswith("Inventory") for h in heads), str(heads[-3:]))
        t = await pg.evaluate(f"{row('Shoex')}.innerText")
        check("unlinked + empty shown", "Not linked" in t and "Empty" in t, t[-40:])
        await pg.evaluate(f"{row('Shoex')}.querySelector('.invlink').click()"); await pg.wait_for_timeout(400)
        check("officer opens Shoex's inventory", "#inventory" in pg.url and "Viewing Shoex's inventory" in await pg.inner_text("#inv-viewing"))
        check("officer can edit (Save to Shoex)", await pg.is_visible("#btn-save-inv") and (await pg.inner_text("#btn-save-inv")) == "Save to Shoex" and not await pg.is_disabled("#c-Helix"))
        await pg.select_option("#c-Helix", "6"); await pg.wait_for_timeout(100)
        await pg.click("#btn-save-inv"); await pg.wait_for_timeout(700)
        d = json.loads(await pg.evaluate("JSON.stringify(window.__store.get('inventory/m-shoex')||null)") or "null") or {}
        check("saved to inventory/m-shoex as an officer edit", d.get("byOfficer") and d.get("inv", {}).get("chars", {}).get("Helix") == 6, str(d)[:120])
        a = await pg.evaluate("JSON.stringify(window.__store.get('audit/u-officer').events.slice(-1)[0])")
        check("logged with before -> after", "edited inventory" in a and "inv.chars.Helix: empty → 6" in a and "etched" not in a, a[:200])
        check("officer's own private inventory untouched", not await pg.evaluate("JSON.stringify(window.__store.get('data/users/u-officer/builds-account')||'').includes('Shoex')"))
        await pg.click("#inv-viewing >> text=Back to my inventory"); await pg.wait_for_timeout(200)
        check("back to my own inventory", await pg.is_hidden("#inv-viewing") and (await pg.inner_text("#btn-save-inv")) == "Save")
        await pg.click("#tab-roster"); await pg.wait_for_timeout(300)
        check("roster now shows ✓ Filled", "✓ Filled" in await pg.evaluate(f"{row('Shoex')}.innerText"))
        # leaving the tab while viewing returns to my own
        await pg.evaluate(f"{row('Shoex')}.querySelector('.invlink').click()"); await pg.wait_for_timeout(300)
        await pg.click("#tab-builds"); await pg.wait_for_timeout(200); await pg.click("#tab-inventory"); await pg.wait_for_timeout(200)
        check("switching tabs drops back to my own inventory", await pg.is_hidden("#inv-viewing"))
        o_errs = list(errs)
        # ---------- member: link, pull officer edit, view another read-only
        seed = f"""window.__store.set('inventory/m-shoex', {{ memberId: 'm-shoex', ign: 'Shoex', inv: {{ chars: {{ Helix: 7 }}, gear: {{}}, runes: {{}}, etched: 0, mystlings: {{}} }}, at: {FUT}, byOfficer: true, by: 'u-officer', v: 1 }});
                   window.__store.set('inventory/m-hago26', {{ memberId: 'm-hago26', ign: 'Hago26', inv: {{ chars: {{ Thor: 5 }}, gear: {{}}, runes: {{}}, etched: 0, mystlings: {{}} }}, at: 1795300000000, byOfficer: true, by: 'u-officer', v: 1 }});"""
        mp, merrs = await page(b, member=True, seed=seed)
        await mp.fill("#roster-search", "shoex"); await mp.click("#roster-body tr:first-child"); await mp.wait_for_timeout(300)
        await mp.click("text=This is me: link to my account"); await mp.wait_for_timeout(1200)
        pr = json.loads(await mp.evaluate("JSON.stringify(window.__store.get('presets/u-member')||null)") or "null") or {}
        check("member's link is public (presets/<id>)", pr.get("memberId") == "m-shoex" and pr.get("linked") is True, str(pr)[:120])
        mi = (json.loads(await mp.evaluate("JSON.stringify(window.__store.get('presets/u-member')||null)") or "null") or {}).get("shared") or {}
        check("member never writes the inventory collection", await mp.evaluate("window.__store.get('inventory/u-member')") is None)
        check("member's inventory shared with memberId", mi.get("memberId") == "m-shoex", str(mi)[:120])
        priv = await mp.evaluate("JSON.stringify(window.__store.get('data/users/u-member/builds-account')||null)")
        check("officer's newer edit pulled into the member's own inventory", '"Helix":7' in priv, priv[:160])
        await mp.fill("#roster-search", ""); await mp.wait_for_timeout(200)
        check("roster shows 🔗 Linked for Shoex", "🔗 Linked" in await mp.evaluate(f"{row('Shoex')}.innerText"))
        await mp.evaluate(f"{row('Hago26')}.querySelector('.invlink').click()"); await mp.wait_for_timeout(400)
        check("member can view another player's inventory", "Viewing Hago26's inventory" in await mp.inner_text("#inv-viewing") and await mp.input_value("#c-Thor") == "5")
        check("…read-only for members", await mp.is_disabled("#c-Thor") and await mp.is_hidden("#btn-save-inv"))
        # ---------- first-time share of an existing private inventory
        seed2 = """window.__store.set('data/users/u-member/builds-account', { inv: { chars: { Otta: 4 }, gear: {}, runes: {}, etched: 0, mystlings: {} }, ign: 'Shoex', builds: [], linkedMemberId: 'm-shoex', savedAt: 1795300000000, v: 3 });"""
        fp, ferrs = await page(b, member=True, seed=seed2)
        await fp.wait_for_timeout(800)
        fi = (json.loads(await fp.evaluate("JSON.stringify(window.__store.get('presets/u-member')||null)") or "null") or {}).get("shared") or {}
        check("existing private inventory shared on first visit", fi.get("inv", {}).get("chars", {}).get("Otta") == 4, str(fi)[:120])
        await fp.click("#tab-inventory"); await fp.wait_for_timeout(200)
        check("one-time notice shown", "now visible to the whole guild" in await fp.inner_text("#inv-shared-note"))
        check("no page errors", not o_errs and not merrs and not ferrs, str(o_errs + merrs + ferrs)[:300])
        await b.close()
    print(f"{sum(res)} / {len(res)}")
asyncio.run(main())

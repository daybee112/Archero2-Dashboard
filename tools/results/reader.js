  // ================= Round results =================
  // After a round: the Schedule screen (both battles' scores; each lane's flag is blue when the left guild won it, red
  // when the right one did) and 12 Details screens (2 battles x 3 lanes x 2 guilds). This device sorts the screens by
  // their highlighted tabs (the yellow guild tab, the lighter lane tab) and reads the Schedule flags; Claude reads the
  // names and numbers. Each value is checked against its % share of its side's total, and the survival % gives survival
  // time to a fraction of a second (whole seconds when the % can't be read). Prototype: tools/results/kind.py.
  let resCtx = null, lastRes = null, resCtl = null;
  async function resultsKind(blob) {
    const bmp = await createImageBitmap(blob), W = bmp.width, H = bmp.height, c = document.createElement("canvas"); c.width = W; c.height = H;
    const x = c.getContext("2d", { willReadFrequently: true }); x.drawImage(bmp, 0, 0); const d = x.getImageData(0, 0, W, H).data;
    const at = (px, py) => { const i = (Math.min(H - 1, Math.max(0, Math.round(py))) * W + Math.min(W - 1, Math.max(0, Math.round(px)))) * 4; return [d[i], d[i + 1], d[i + 2]]; };
    const avg = (cx, cy, hw, hh) => { let r = 0, g = 0, b = 0, n = 0;
      for (let yy = cy - hh; yy <= cy + hh; yy += 2) for (let xx = cx - hw; xx <= cx + hw; xx += 2) { const p = at(xx, yy); r += p[0]; g += p[1]; b += p[2]; n++; }
      return [r / n, g / n, b / n]; };
    let ty = -1;   // the window's blue title bar ("Details" or "Schedule"); everything below is placed from it
    for (let y = Math.round(H * 0.08); y < H * 0.45; y++) { const [r, g, b] = at(W / 2, y); if (b > 200 && g > 150 && r < 80) { ty = y; break; } }
    if (ty < 0 || ty + 1.26 * W >= H) return { kind: "other" };
    const u = W, yellow = (p) => p[0] > 225 && p[1] > 195 && p[2] < 110;
    const tabC = [0.29, 0.71].map(fx => avg(fx * W, ty + 0.16 * u, 0.03 * W, 0.008 * u)), tabs = tabC.map(yellow);
    const lanes = [0.225, 0.5, 0.775].map(fx => avg(fx * W, ty + 1.25 * u, 0.04 * W, 0.006 * u));
    // Schedule: no guild tabs there, just the window's tan background where the Details tabs would be
    if (!tabs[0] && !tabs[1] && tabC.every(p => p[0] > 205 && p[1] > 150 && p[1] < 200 && p[2] > 100 && p[2] < 150)) {
      const flags = [0.52, 0.885].map(dy => [0.20, 0.415, 0.62].map(cx => { let red = 0;
        for (let xx = (cx - 0.04) * W; xx < (cx + 0.04) * W; xx += 2) for (let yy = ty + (dy - 0.05) * u; yy < ty + (dy + 0.04) * u; yy += 2) { const p = at(xx, yy); if (p[0] > 190 && p[1] < 80 && p[2] < 80) red++; }
        return red > 40 ? "right" : "left"; }));
      return { kind: "schedule", flags };
    }
    if (tabs[0] === tabs[1]) return { kind: "other" };
    const br = lanes.map(p => p[0] + p[1] + p[2]), top = Math.max(...br), rest = br.filter(v => v !== top);
    const lane = rest.length === 2 && top - Math.max(...rest) >= 12 ? LANES[br.indexOf(top)] : null;
    return { kind: "details", side: tabs[0] ? 0 : 1, lane };
  }
  function resultsPrompt(nums) {
    return `These ${nums.length} screenshots (screens ${nums.join(", ")}, in this order) are from the Guild Expedition results of the mobile game Archero 2.\n` +
      "Each is one of:\n" +
      "- schedule: a Schedule window (\"This round is over\") with two battles. Each battle shows two guild names, one on the left and one on the right, and a score like 0:3 (left guild's lanes won : right guild's).\n" +
      "- details: a Details window with two guild tabs at the top (the selected one is yellow) and Left / Middle / Right tabs at the bottom (the selected one is lighter). Its table has up to 8 rows with Name, Damage, Survival Time, Damage Taken and Healing, and a percentage under each value.\n" +
      "- other: anything else.\n" +
      "Copy numbers exactly as shown, as text with their K or M suffix (like \"1.94M\", \"500.34K\", \"9641\"). Percentages are numbers without the % sign. Survival time is the number of seconds. " +
      "Keep names exactly as written, including Korean, Chinese, Japanese or Cyrillic letters, and include a small raised prefix or suffix as part of the name (like BM in BMKiênLốp). Use null for anything you can't read clearly.\n" +
      'Reply with ONLY this JSON: {"screens":[{"i":1,"type":"schedule","battles":[{"left":"","right":"","score":[0,3]}]},' +
      '{"i":2,"type":"details","guilds":["",""],"selected":"left","lane":"left","rows":[{"name":"","dmg":"1.94M","dmg_pct":30.48,"surv":6,"surv_pct":100,"taken":"20.83K","taken_pct":5.0,"heal":"141.08K","heal_pct":10.12}]}]}\n' +
      '"guilds" are the two tab names, left tab first; "selected" is which tab is yellow (left or right); "lane" is the lighter bottom tab (left, middle or right). Rows top to bottom.';
  }
  function parseAmt(v) {
    if (v == null || v === "") return null; if (typeof v === "number") return isFinite(v) ? v : null;
    const m = String(v).replace(/,/g, "").trim().match(/^(\d+(?:\.\d+)?)\s*([KMB])?$/i); if (!m) return null;
    return Math.round(parseFloat(m[1]) * ({ K: 1e3, M: 1e6, B: 1e9 }[(m[2] || "").toUpperCase()] || 1));
  }
  const pctNum = (v) => { if (v == null || v === "") return null; const n = parseFloat(String(v).replace("%", "")); return isFinite(n) ? n : null; };
  const fmtAmt = (v) => v == null ? "" : v >= 1e6 ? (v / 1e6).toFixed(2) + "M" : v >= 1e4 ? (v / 1e3).toFixed(2) + "K" : String(v);
  function resRow(r) {
    return { name: String(r && r.name || "").trim(), dmg: parseAmt(r && r.dmg), dmgPct: pctNum(r && r.dmg_pct), surv: r && r.surv != null ? parseInt(r.surv, 10) || 0 : null,
      survPct: pctNum(r && r.surv_pct), taken: parseAmt(r && r.taken), takenPct: pctNum(r && r.taken_pct), heal: parseAmt(r && r.heal), healPct: pctNum(r && r.heal_pct) };
  }
  // A value fits when it agrees with its % share. Each row implies the side's total (value ÷ its %); the median of those
  // is the real total, so one misread value stands out instead of throwing every row off. The printed values and
  // percentages are rounded, so allow 0.8% plus what rounding a small % costs.
  function shareMisfits(rows, key, pkey) {
    const out = new Set(), est = rows.map(r => r[key] != null && r[pkey] ? r[key] / (r[pkey] / 100) : null), ok = est.filter(v => v != null && v > 0).sort((a, z) => a - z);
    if (ok.length < 3) return out;
    const med = ok[Math.floor(ok.length / 2)];
    rows.forEach((r, i) => { if (est[i] == null) return; if (Math.abs(est[i] / med - 1) > 0.008 + 0.006 / r[pkey]) out.add(i); });
    return out;
  }
  // fight length and precise survival for one lane (both sides' rows): the fight lasts as long as the longest survivor
  function resLaneTimes(a, b) {
    const all = [...a, ...b], full = all.filter(r => r.survPct != null && r.survPct >= 99.95 && r.surv), D = Math.max(0, ...(full.length ? full : all).map(r => r.surv || 0));
    for (const r of all) {
      r.survSec = r.surv; r.survFrom = "s";
      if (r.survPct != null && D) { const s = Math.round(r.survPct / 100 * D * 100) / 100; if (Math.abs(s - (r.surv || 0)) <= 1) { r.survSec = s; r.survFrom = "pct"; } }
    }
    return D;
  }
  function resultsAssemble(screens, dev) {
    const notes = [], sched = [], dets = [];
    screens.forEach((s, k) => {
      const dv = dev[k] || {}, type = dv.kind && dv.kind !== "other" ? dv.kind : s && s.type;
      if (type === "schedule") sched.push({ s: s || {}, dv, k });
      else if (type === "details") {
        const side = dv.side != null ? dv.side : (s && s.selected === "right" ? 1 : s && s.selected === "left" ? 0 : null);
        const lane = dv.lane || (s && LANES.includes(s.lane) ? s.lane : null);
        if (s && s.selected && dv.side != null && (s.selected === "right" ? 1 : 0) !== dv.side) notes.push(`Screen ${k + 1}: Claude and this device disagree on which guild tab is selected; went with the device.`);
        if (s && s.lane && dv.lane && s.lane !== dv.lane) notes.push(`Screen ${k + 1}: Claude and this device disagree on the lane; went with the device.`);
        dets.push({ k, guilds: (s && s.guilds || []).map(g => String(g || "").trim()), side, lane, rows: (s && s.rows || []).map(resRow).filter(r => r.name || r.dmg != null) });
      }
    });
    const key = (a, b) => [a, b].sort().join("\u0001"), battles = new Map();
    const battle = (a, b) => { const kk = key(a, b); if (!battles.has(kk)) battles.set(kk, { left: a, right: b, score: null, laneWin: {}, sides: { [a]: {}, [b]: {} }, from: {} }); return battles.get(kk); };
    for (const { s, dv } of sched) (s.battles || []).forEach((bt, i) => {
      if (!bt || !bt.left || !bt.right) return; const B = battle(String(bt.left).trim(), String(bt.right).trim());
      if (Array.isArray(bt.score) && bt.score.length === 2) B.score = bt.score.map(n => parseInt(n, 10));
      const fl = dv.flags && dv.flags[i]; if (fl) LANES.forEach((l, j) => { B.laneWin[l] = fl[j] === "right" ? B.right : B.left; });
    });
    for (const dt of dets) {
      if (dt.guilds.length !== 2 || !dt.guilds[0] || !dt.guilds[1] || dt.side == null || !dt.lane) { notes.push(`Screen ${dt.k + 1}: couldn't tell which guild or lane it shows; left out.`); continue; }
      const B = battles.get(key(dt.guilds[0], dt.guilds[1])) || battle(dt.guilds[0], dt.guilds[1]), g = dt.guilds[dt.side];
      if (B.sides[g][dt.lane]) { if (JSON.stringify(B.sides[g][dt.lane]) !== JSON.stringify(dt.rows)) notes.push(`Screens ${B.from[g + dt.lane] + 1} and ${dt.k + 1} are both ${g} ${LANE_LABEL[dt.lane]} but read differently; kept the first.`); }
      else { B.sides[g][dt.lane] = dt.rows; B.from[g + dt.lane] = dt.k; }
    }
    const out = [...battles.values()];
    for (const B of out) {
      B.lanes = {};
      for (const l of LANES) {
        const a = B.sides[B.left][l] || null, b = B.sides[B.right][l] || null;
        const dur = resLaneTimes(a || [], b || []);
        const mis = (rows) => rows ? { dmg: shareMisfits(rows, "dmg", "dmgPct"), taken: shareMisfits(rows, "taken", "takenPct"), heal: shareMisfits(rows, "heal", "healPct") } : null;
        let win = B.laneWin[l] || null;
        if (!win && a && b) {   // no Schedule screen: the side whose players were all alive at the end won
          const allAlive = (rows) => rows.length && rows.every(r => r.survPct != null && r.survPct >= 99.95);
          win = allAlive(a) && !allAlive(b) ? B.left : allAlive(b) && !allAlive(a) ? B.right : null;
        }
        B.lanes[l] = { dur, win, mis: { [B.left]: mis(a), [B.right]: mis(b) } };
      }
      if (!B.score) { const w = LANES.filter(l => B.lanes[l].win === B.left).length, z = LANES.filter(l => B.lanes[l].win === B.right).length; if (w + z === 3) B.score = [w, z]; }
      B.missing = []; for (const g of [B.left, B.right]) for (const l of LANES) if (!B.sides[g][l]) B.missing.push(`${g} ${LANE_LABEL[l]}`);
    }
    if (!sched.length) notes.push("No Schedule screen: lane winners come from who was still alive, and the scores from those.");
    return { battles: out, notes };
  }
  function resOurs(res) { return res.battles.find(B => B.left === "ArchAcademy" || B.right === "ArchAcademy") || null; }
  async function readResults(files, say, signal) {
    const sample = window.claude && typeof claude.use === "function" ? await claude.use("sample") : null;
    if (!sample) throw new Error("Reading screenshots isn't available here. Open this page inside Claude.");
    try { const lim = await sample.limits(); if (!lim || !lim.images) throw new Error("Image reading isn't available on this account."); } catch (e) { if (e && e.message && /available/.test(e.message)) throw e; }
    let stills = [];
    for (const f of files) {
      if (/^video\//.test(f.type)) { const st = await videoStills(f, signal, (p) => say(`Finding screens in the recording… ${Math.round(p * 100)}%`), { same: 0.006, still: 0.015 }); stills.push(...st); }
      else stills.push({ blob: f });
    }
    if (!stills.length) throw new Error("No screens found.");
    say(`Sorting ${stills.length} screens on this device…`);
    const dev = []; for (const s of stills) { try { dev.push(await resultsKind(s.blob)); } catch { dev.push({ kind: "other" }); } }
    let maxImgs = 6; try { const lim = await sample.limits(); maxImgs = Math.max(1, Math.min(6, lim?.images?.maxCount || 6)); } catch {}
    const screens = stills.map((_, k) => ({ i: k + 1, type: "unread" }));
    const nums = screens.map(x => x.i).filter((n) => dev[n - 1].kind !== "other");
    const errs = await vidReadInto(screens, nums, stills, sample, signal, maxImgs, say, resultsPrompt);
    if (errs.fatal) throw new Error(errs.fatal);
    const res = resultsAssemble(screens, dev);
    res.unread = screens.filter((s, k) => s.type === "unread" && dev[k].kind !== "other").map(s => s.i);
    res.skipped = dev.map((d, k) => d.kind === "other" ? k + 1 : null).filter(Boolean);
    res.count = stills.length; res.stills = stills;
    return res;
  }
  function renderResults(res) {
    const box = $("res-result"); box.replaceChildren();
    const ours = resOurs(res), cell = (B, g, l, r, i, key) => {
      const mis = B.lanes[l].mis[g], bad = mis && mis[key] && mis[key].has(i);
      const val = key === "surv" ? (r.survPct != null ? r.survPct + "%" : r.surv != null ? r.surv + "s" : "") : key === "name" ? r.name : fmtAmt(r[key]);
      const inp = el("input", { type: "text", value: val, class: bad || (key === "surv" && r.survFrom === "s" && r.survPct != null) ? "unsure" : "", style: "width:100%;min-width:0;font-size:11px;padding:2px 2px;letter-spacing:-0.2px",
        "aria-label": `${g} ${LANE_LABEL[l]} row ${i + 1} ${key}` });
      inp.addEventListener("change", () => {
        const v = inp.value.trim();
        if (key === "name") r.name = v;
        else if (key === "surv") { if (/%$/.test(v)) r.survPct = pctNum(v); else { r.surv = parseInt(v, 10) || 0; r.survPct = null; } }
        else r[key] = parseAmt(v);
        resLaneTimes(B.sides[B.left][l] || [], B.sides[B.right][l] || []);
        if (mis && mis[key]) { const nm = shareMisfits(B.sides[g][l], key, key + "Pct"); mis[key] = nm; inp.classList.toggle("unsure", nm.has(i)); }
      });
      return el("td", {}, inp);
    };
    const sideTable = (B, g, l) => {
      const rows = B.sides[g][l];
      if (!rows) return el("div", { class: "small warn-msg", text: `${g} ${LANE_LABEL[l]}: no screenshot.` });
      const our = g === "ArchAcademy";
      return el("table", { class: "res-t", style: "width:100%;table-layout:fixed;border-collapse:collapse" },
        el("caption", { class: "small", style: "text-align:left;font-weight:600;padding:2px 0", text: g }),
        el("colgroup", {}, ...["25%", "16%", "15%", "14%", "15%", "15%"].map(wd => el("col", { style: "width:" + wd }))),
        el("tr", { class: "small muted" }, ...["Name", "Damage", "Survival", "Taken", "Healing", "DPS"].map(t => el("th", { style: "text-align:left;font-weight:500", text: t }))),
        ...rows.map((r, i) => { const m = our ? memberByName(r.name) : null;
          return el("tr", { title: our ? (m ? (m.ign !== r.name ? `Matched to ${m.ign}` : "On the roster") : "Not on the roster") : "" },
            cell(B, g, l, r, i, "name"), cell(B, g, l, r, i, "dmg"), cell(B, g, l, r, i, "surv"), cell(B, g, l, r, i, "taken"), cell(B, g, l, r, i, "heal"),
            el("td", { class: "small" + (our && !m ? " warn-msg" : ""), text: (r.dmg != null && r.survSec ? fmtRate(r.dmg / r.survSec) : "") + (our && !m ? " · not on roster" : "") })); }));
    };
    const notes = [...res.notes];
    if (res.unread.length) notes.push(`Claude couldn't read screen${res.unread.length > 1 ? "s" : ""} ${res.unread.join(", ")}.`);
    if (res.skipped.length) notes.push(`Screen${res.skipped.length > 1 ? "s" : ""} ${res.skipped.join(", ")} ${res.skipped.length > 1 ? "aren't" : "isn't"} a Schedule or Details screen; left out.`);
    for (const B of res.battles) {
      const us = B.right === "ArchAcademy" ? [B.right, B.left] : [B.left, B.right], sc = B.score ? (B.right === us[0] ? [B.score[1], B.score[0]] : B.score) : null;
      const lanes = LANES.map(l => { const L = B.lanes[l], w = L.win;
        return el("div", { class: "stack", style: "gap:4px" },
          el("div", { class: "row", style: "gap:8px;flex-wrap:wrap" }, el("b", { text: LANE_LABEL[l] }), el("span", { class: "small muted", text: `${L.dur ? L.dur + "s fight" : "fight length unknown"} · ${w ? w + " won" : "winner unknown"}` })),
          sideTable(B, us[0], l), sideTable(B, us[1], l)); });
      box.append(el("div", { class: "panel stack" },
        el("h3", { style: "margin:0", text: `${us[0]} ${sc ? sc[0] + " : " + sc[1] : "?"} ${us[1]}` }),
        B.missing.length ? el("div", { class: "small warn-msg", text: `Missing: ${B.missing.join(", ")}. What's here can still be saved; the gap is marked.` }) : null,
        ...lanes));
    }
    if (notes.length) box.append(el("ul", { class: "small muted" }, ...notes.map(t => el("li", { text: t }))));
    const nBad = res.battles.reduce((a, B) => a + LANES.reduce((x, l) => x + Object.values(B.lanes[l].mis).reduce((y, m) => y + (m ? m.dmg.size + m.taken.size + m.heal.size : 0), 0), 0), 0);
    const st = el("span", { class: "small" }), save = el("button", { type: "button", class: "btn", text: "Save results" });
    save.disabled = !ours || !resCtx;
    if (!ours) st.textContent = "None of these screens show ArchAcademy's battle, so there's nothing to save for this round.";
    else if (nBad) st.textContent = `${nBad} value${nBad === 1 ? "" : "s"} (red) don't fit their % share. Check ${nBad === 1 ? "it" : "them"} against the screenshot before saving.`;
    save.addEventListener("click", async () => { save.disabled = true; st.textContent = "Saving…";
      try { const n = await saveResults(res); st.className = "small ok-msg"; st.textContent = n; } catch (e) { save.disabled = false; st.className = "small err"; st.textContent = e && e.message || "Couldn't save."; } });
    box.append(el("div", { class: "row" }, save, st));
  }
  function resStat(r, lane, our) {
    const s = { lane, dmg: r.dmg, surv: r.surv, heal: r.heal, taken: r.taken };
    if (r.survPct != null) s.survPct = r.survPct;
    if (r.survSec != null && r.survSec !== r.surv) s.survSec = r.survSec;
    if (our) { const m = memberByName(r.name); s.ign = m ? m.ign : r.name; if (!m) s.unmatched = true; }
    else { s.name = r.name; if (r.dmg != null && (r.survSec || r.surv)) s.dps = Math.round(r.dmg / (r.survSec || r.surv)); }
    return s;
  }
  async function saveResults(res) {
    const w = resCtx && weekById(resCtx.week); if (!w) throw new Error("Pick the round first (Uploads).");
    const B = resOurs(res); if (!B) throw new Error("ArchAcademy's battle isn't in these screens.");
    const nw = clone(w), nr = (nw.rounds || []).find(x => x.n === resCtx.round); if (!nr) throw new Error("That round isn't in this week.");
    const opp = B.left === "ArchAcademy" ? B.right : B.left;
    if (nr.opponent && nr.opponent !== "tbd" && nr.opponent !== opp) throw new Error(`These screens are vs ${opp}, but Round ${nr.n} is vs ${nr.opponent}.`);
    const stats = [], theirStats = [], their = {}, laneResults = {};
    for (const l of LANES) {
      const a = B.sides.ArchAcademy[l], b = B.sides[opp][l], L = B.lanes[l];
      for (const r of (a || [])) stats.push(resStat(r, l, true));
      for (const r of (b || [])) theirStats.push(resStat(r, l, false));
      if (b) their[l] = { ...((nr.their || {})[l] || {}), players: b.map(r => r.name) };
      const sum = (rows) => rows ? Math.round(rows.reduce((x, r) => x + (r.dmg || 0), 0) / 1e4) / 100 : null;
      const alive = (rows, won) => rows ? (won ? rows.filter(r => r.survPct != null ? r.survPct >= 99.95 : r.surv >= L.dur).length : 0) : null;
      laneResults[l] = { result: L.win ? (L.win === "ArchAcademy" ? "won" : "lost") : null, dur: L.dur || null, ourDmg: sum(a), theirDmg: sum(b),
        ourAlive: alive(a, L.win === "ArchAcademy"), theirAlive: alive(b, L.win === opp) };
    }
    const sc = B.score ? (B.left === "ArchAcademy" ? B.score : [B.score[1], B.score[0]]) : null;
    Object.assign(nr, { stats, theirStats, their: { ...(nr.their || {}), ...their }, laneResults, status: "done" });
    if (!nr.opponent || nr.opponent === "tbd") nr.opponent = opp;
    if (sc) { nr.score = `${sc[0]}-${sc[1]}`; nr.result = sc[0] > sc[1] ? "W" : "L"; }
    if (B.missing.length) nr.partialStats = true; else delete nr.partialStats;
    const allMissing = res.battles.flatMap(O => O.missing || []);   // both battles' gaps, so the Results row shows them
    nr.uploads = { ...(nr.uploads || {}), results: { at: Date.now(), date: localDate(Date.now()), screens: res.count, ...(allMissing.length ? { missing: allMissing } : {}) } };
    await saveWeek(nw, `Round ${nr.n} results read from screenshots: ${sc ? (sc[0] > sc[1] ? "won " : "lost ") + sc.join("-") : "score unknown"} vs ${opp} (${w.label})`);
    // the group's other battle: one observation per guild, with its lanes and players
    let other = 0;
    for (const O of res.battles) {
      if (O === B || !db) continue;
      for (const [g, v] of [[O.left, O.right], [O.right, O.left]]) {
        const lanes = {}, ostats = [], lr = {};
        for (const l of LANES) {
          const rows = O.sides[g][l], vrows = O.sides[v][l], L = O.lanes[l];
          if (rows) { lanes[l] = { players: rows.map(r => r.name) }; for (const r of rows) ostats.push(resStat(r, l, false)); }
          const sum = (rr) => rr ? Math.round(rr.reduce((x, r) => x + (r.dmg || 0), 0) / 1e4) / 100 : null;
          lr[l] = { result: L.win ? (L.win === g ? "won" : "lost") : null, dur: L.dur || null, dmg: sum(rows), vsDmg: sum(vrows) };
        }
        const s = O.score ? (O.left === g ? O.score : [O.score[1], O.score[0]]) : null;
        const ob = { week: w.id, round: nr.n, guild: g, vs: v, result: s ? `${s[0] > s[1] ? "W" : "L"} ${s[0]}-${s[1]}` : "", lanes, laneResults: lr, stats: ostats,
          ...(O.missing.length ? { missing: O.missing } : {}), src: "results screenshots", updatedAt: Date.now(), updatedBy: myId, v: 3 };
        await db.doc(`observations/${w.id}-r${nr.n}-${oppId(g)}`).set(ob);
        EXP.observations = [...(EXP.observations || []).filter(o => !(o.week === w.id && o.round === nr.n && o.guild === g)), ob];
        other++;
      }
      logEvent("expedition", `Round ${nr.n}: ${O.left} ${O.score ? O.score.join("-") : "?"} ${O.right} read from screenshots (${w.label})`);
    }
    renderExpedition();
    const un = stats.filter(s => s.unmatched).map(s => s.ign);
    return `Saved: ${stats.length} of our players, ${theirStats.length} of ${opp}'s${other ? ", and the other battle" : ""}.` + (un.length ? ` Not on the roster: ${un.join(", ")}.` : "") + (allMissing.length ? ` Missing: ${allMissing.join(", ")}.` : "");
  }
  function openResultsFor(ctx) {
    const pnl = $("res-panel"); $("exp-uploads-reader").append(pnl);
    const w = weekById(ctx.week), r = w && (w.rounds || []).find(x => x.n === ctx.round);
    const same = resCtx && resCtx.week === ctx.week && resCtx.round === ctx.round && !pnl.hidden;
    resCtx = ctx; $("res-title").textContent = `Round ${ctx.round} results` + (r && r.opponent && r.opponent !== "tbd" ? ` · vs ${r.opponent}` : "");
    if (!same) { $("res-result").replaceChildren(); $("res-status").textContent = ""; }
    pnl.hidden = false; pnl.scrollIntoView({ block: "start", behavior: "smooth" });
  }
  $("res-files").addEventListener("change", () => { $("btn-res-read").disabled = !$("res-files").files.length; });
  $("btn-res-close").addEventListener("click", () => { resCtl?.abort(); $("res-panel").hidden = true; });
  $("btn-res-read").addEventListener("click", async () => {
    const st = $("res-status"), files = [...$("res-files").files]; if (!files.length) return;
    resCtl?.abort(); resCtl = new AbortController(); $("btn-res-read").disabled = true; st.className = "small"; $("res-result").replaceChildren();
    try {
      const res = await readResults(files, (t) => { st.textContent = t; }, resCtl.signal); lastRes = res; if (window.__expose) window.__lastRes = res;
      const B = resOurs(res);
      st.textContent = `Read ${res.count} screen${res.count === 1 ? "" : "s"}: ${res.battles.length} battle${res.battles.length === 1 ? "" : "s"}${B ? "" : ", but none with ArchAcademy"}. Check each lane, correct anything, then save.`;
      renderResults(res);
    } catch (e) { st.className = "small err"; st.textContent = e && e.message === "stopped" ? "Stopped." : (e && e.message) || "Something went wrong reading the screens."; }
    finally { $("btn-res-read").disabled = !$("res-files").files.length; }
  });
  if (window.__expose) { window.__resultsKind = resultsKind; window.__resultsAssemble = resultsAssemble; window.__parseAmt = parseAmt; window.__renderResults = renderResults;
    window.__openResultsFor = openResultsFor; window.__saveResults = saveResults; window.__setResCtx = (c) => { resCtx = c; }; }

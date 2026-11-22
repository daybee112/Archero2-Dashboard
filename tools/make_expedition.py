import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
# Builds dashboard/expedition-seed.json from the project's Expedition logs (weeks of 11-02, 11-09, 11-16).
# Sources: claude/archero2-expedition-log.md, -log-2026-11-09.md, -log-2026-11-16.md, -2026-11-16-r1/r2-postmortem.md,
# -happiness-scan.md, -holymoly-scan.md, tracker sheet (DPS History, Post-Mortem). Only confirmed/derived numbers; blanks where unknown.
import json, re

def team(s):
    """'A, B, C' -> list of names"""
    return [x.strip() for x in s.split(",") if x.strip()]

def stats(block, lane_dur=None):
    """Lines 'lane|ign|damage|surv|heal' (damage like 3.47M / 617K; surv seconds or blank; heal optional)."""
    out = []
    for ln in block.strip().splitlines():
        p = [x.strip() for x in ln.split("|")]
        lane, ign, dmg = p[0], p[1], p[2]
        surv = p[3] if len(p) > 3 else ""
        heal = p[4] if len(p) > 4 else ""
        def num(v):
            if not v: return None
            m = re.match(r"^([\d.]+)\s*([KM]?)$", v)
            return round(float(m.group(1)) * {"": 1, "K": 1e3, "M": 1e6}[m.group(2)])
        r = {"lane": {"L": "left", "M": "middle", "R": "right"}[lane], "ign": ign, "dmg": num(dmg)}
        s = int(surv) if surv else (lane_dur.get(r["lane"]) if lane_dur else None)
        if s: r["surv"] = s
        if heal: r["heal"] = num(heal)
        out.append(r)
    return out

def oppstats(block):
    """Lines 'lane|name|dps' or 'lane|name|dps|dmg|surv' (dps in K/s)."""
    out = []
    for ln in block.strip().splitlines():
        p = [x.strip() for x in ln.split("|")]
        r = {"lane": {"L": "left", "M": "middle", "R": "right"}[p[0]], "name": p[1]}
        if p[2]: r["dps"] = int(p[2]) * 1000
        if len(p) > 3 and p[3]:
            m = re.match(r"^([\d.]+)\s*([KM]?)$", p[3]); r["dmg"] = round(float(m.group(1)) * {"": 1, "K": 1e3, "M": 1e6}[m.group(2)])
        if len(p) > 4 and p[4]: r["surv"] = int(p[4])
        out.append(r)
    return out

def roster(block):
    """Lines 'name|power|mythic|leg|gear|note' (power in M, '' if unknown)."""
    out = []
    for ln in block.strip().splitlines():
        p = [x.strip() for x in ln.split("|")] + [""] * 6
        r = {"name": p[0]}
        if p[1]: r["power"] = float(p[1])
        if p[2]: r["mythic"] = int(p[2])
        if p[3]: r["leg"] = int(p[3])
        if p[4]: r["gear"] = p[4]
        if p[5]: r["note"] = p[5]
        out.append(r)
    return out

def oppfull(block):
    """Lines 'lane|name|damage|surv' straight from a Details screen; DPS is derived (damage / survival)."""
    out = []
    for ln in block.strip().splitlines():
        p = [x.strip() for x in ln.split("|")]
        m = re.match(r"^([\d.]+)\s*([KM]?)$", p[2]); dmg = round(float(m.group(1)) * {"": 1, "K": 1e3, "M": 1e6}[m.group(2)])
        surv = int(p[3])
        out.append({"lane": {"L": "left", "M": "middle", "R": "right"}[p[0]], "name": p[1], "dps": round(dmg / surv / 1000) * 1000, "dmg": dmg, "surv": surv})
    return out

def lanes(l, m, r):
    return {"left": l, "middle": m, "right": r}

def lane(players, anchor=None, **kw):
    d = {"players": team(players) if isinstance(players, str) else players}
    if anchor: d["anchor"] = anchor
    d.update(kw)
    return d

# ======================= WEEK OF 2026-11-02 =======================
w1 = {
 "id": "2026-11-02", "label": "Week of Nov 2",
 "group": [{"guild": "ArchAcademy", "power": 370.80}, {"guild": "PWNZ", "power": 282.56}, {"guild": "Happiness"}, {"guild": "BlockMagic"}],
 "standings": [{"guild": "BlockMagic", "pts": 9, "flags": 8, "dmg": 67.62}, {"guild": "Happiness", "pts": 6, "flags": 5, "dmg": 55.70},
               {"guild": "ArchAcademy", "pts": 3, "flags": 3, "dmg": 41.15}, {"guild": "PWNZ", "pts": 0, "flags": 2, "dmg": 38.38}],
 "final": True,
 "lessons": ["Stack two lanes, dump one, is the standard at this tier; against even opponents the dump-lane guess decides the round.",
             "Two of three opponents never changed lanes all week: record lane habits.",
             "Dragoon gear is the best single predictor of our damage, if the lane survives.",
             "Filled presets matter; empty ones underperform badly.",
             "One official lineup only: unauthorized swaps cost damage in R2."],
 "rounds": [
  {"n": 1, "date": "2026-11-06", "opponent": "PWNZ", "status": "done", "result": "W", "score": "2-1",
   "strategy": "Stacked Middle and Right, kept MHARU as a real anchor on the Left dump lane (dump lane picked blind).",
   "our": lanes(
     lane("MHARU, Heynow, Bubobubo, JJJRRRBBB, TheDragonix725, Michelo, LeKo, Itsgeorgees", "MHARU", role="dump"),
     lane("Isterbuk, SilverScope, Tuup, Zeuzo, Hansi218, Yullong, Ilportoghese, Shoex", "Tuup", role="stack"),
     lane("Hago26, MuffinKnight, 皇黎, MsPoppycorn, daybee, thesithlor, Terminus323, Venom17", "Hago26", role="stack")),
   "power": {"MHARU": 10.08, "Heynow": 7.98, "Bubobubo": 7.70, "JJJRRRBBB": 7.68, "TheDragonix725": 7.56, "Michelo": 7.53, "LeKo": 7.34, "Itsgeorgees": 7.23,
             "Isterbuk": 11.47, "SilverScope": 10.58, "Tuup": 10.54, "Zeuzo": 10.22, "Hansi218": 10.19, "Yullong": 9.81, "Ilportoghese": 9.61, "Shoex": 9.53,
             "Hago26": 13.54, "MuffinKnight": 11.49, "皇黎": 9.89, "MsPoppycorn": 9.87, "daybee": 9.77, "thesithlor": 9.75, "Terminus323": 8.81, "Venom17": 8.63},
   "their": lanes(
     lane("Delocker, 2love4me, Sugarboy, KillerOwns, lolzter, affection, Huuzy, Akiva", "2love4me"),
     lane("Konefedya, Tony2608, 雙弓無煙dee, TAKESHA1, Aimzu, huka, Dudc, CosmicNaruto", "雙弓無煙dee", role="dump"),
     lane("tesseract, Waka, TseChris, FadeShadow, Grenty, TeeeJay, Хюй, JaaayM", "tesseract")),
   "theirPower": {"Delocker": 13.29, "2love4me": 13.06, "Sugarboy": 9.70, "KillerOwns": 9.49, "lolzter": 7.79, "affection": 7.28, "Huuzy": 6.83, "Akiva": 4.87,
                  "Konefedya": 9.13, "Tony2608": 8.98, "雙弓無煙dee": 8.26, "TAKESHA1": 7.93, "Aimzu": 7.44, "huka": 6.39, "Dudc": 5.00, "CosmicNaruto": 4.42,
                  "tesseract": 16.16, "Waka": 12.92, "TseChris": 9.53, "FadeShadow": 9.11, "Grenty": 8.14, "TeeeJay": 7.40, "Хюй": 7.09, "JaaayM": 5.90},
   "laneResults": lanes({"result": "lost", "dur": 16, "ourDmg": 5.80, "theirDmg": 7.03, "ourAlive": 0, "theirAlive": 5},
                        {"result": "won", "dur": 19, "ourDmg": 6.44, "theirDmg": 4.94, "ourAlive": 6, "theirAlive": 0},
                        {"result": "won", "dur": 14, "ourDmg": 6.98, "theirDmg": 4.46, "ourAlive": 8, "theirAlive": 0, "note": "flawless"}),
   "stats": stats("""
L|MHARU|1.93M|16|207K
L|Michelo|1.27M|11|230K
L|Bubobubo|1.06M|13|495K
L|Itsgeorgees|907K|16|441K
L|TheDragonix725|450K|6|182K
L|LeKo|88K|9|123K
L|Heynow|63K|9|151K
L|JJJRRRBBB|32K|4|10K
M|Tuup|2.38M|19|284K
M|Hansi218|1.19M|19|327K
M|Shoex|1.16M|15|125K
M|Isterbuk|468K|19|281K
M|Zeuzo|403K|19|121K
M|Yullong|356K|19|272K
M|SilverScope|260K|19|80K
M|Ilportoghese|222K|9|114K
R|Hago26|3.47M|14|314.68K
R|daybee|1.83M|14|228.42K
R|Venom17|818.75K|14|125.70K
R|皇黎|279.08K|14|193.31K
R|MsPoppycorn|181.18K|14|164.06K
R|MuffinKnight|165.71K|14|366.90K
R|Terminus323|155.16K|14|75.58K
R|thesithlor|84.47K|14|60.32K"""),
   "offSet": ["Zeuzo"],
   "theirStats": [{"lane": "left", "name": "Delocker", "dmg": 3990000, "note": "955K healing, survived"}] + oppfull("""
M|Konefedya|1.40M|13
M|雙弓無煙dee|1.35M|11
M|Tony2608|1.00M|19
M|Dudc|637.16K|10
M|CosmicNaruto|241.62K|13
M|Aimzu|215.55K|15
M|huka|70.99K|4
M|TAKESHA1|26.74K|6
R|Хюй|1.58M|14
R|TseChris|893.87K|10
R|tesseract|479.20K|9
R|Waka|464.94K|10
R|TeeeJay|449.99K|6
R|JaaayM|296.87K|8
R|FadeShadow|177.42K|7
R|Grenty|124.21K|12"""),
   "notes": "Zeuzo was on Oracle with an empty preset this round (switched to Dragoon after). Each lane's top damage dealer did 33-57% of the lane's damage. Empty presets underperformed (JJJRRRBBB, Heynow)."},
  {"n": 2, "date": "2026-11-07", "opponent": "Happiness", "status": "done", "result": "L", "score": "1-2",
   "strategy": "Hago26 stack Left vs their expected dump, Tuup Dragoon stack Middle, MHARU dump Right vs KiLess (Happiness's R1 layout). Happiness kept Left as dump but swapped Middle and Right: KiLess landed on our Middle stack.",
   "our": lanes(
     lane("Hago26, MuffinKnight, MsPoppycorn, Yullong, 皇黎, daybee, Venom17, Bubobubo", "Hago26", role="stack"),
     lane("Isterbuk, Tuup, SilverScope, Hansi218, Zeuzo, Shoex, Michelo, Heynow", "Tuup", role="stack"),
     lane("MHARU, thesithlor, Ilportoghese, TheDragonix725, LeKo, Itsgeorgees, GoatGeass, Terminus323", "MHARU", role="dump")),
   "their": lanes(lane("ISoLamento, Redtalons, MarkizDeSade, JessLiu, Giruffe, Kraven7k, k3nz1k, Tg13", "MarkizDeSade", role="dump"),
                  lane("KiLess, ZorojuroZ, Cableguy, XavierGame, whistlerer, 臭懶蛋, Mocjuju, multiple", "KiLess", role="stack"),
                  lane("SamuelV, Vince13720, Bremsstrahlung, sovegier, Thatkent, 樂樂樂樂樂樂, caiman, BillyDowns", "Bremsstrahlung", role="stack")),
   "laneResults": lanes({"result": "won", "dur": 8, "ourDmg": 5.70, "theirDmg": 1.98, "ourAlive": 8},
                        {"result": "lost", "dur": 12, "ourDmg": 5.47, "theirDmg": 8.74, "theirAlive": 8, "note": "0 kills"},
                        {"result": "lost", "dur": 11, "ourDmg": 2.85, "theirDmg": 6.77, "theirAlive": 8, "note": "0 kills"}),
   "stats": stats("""
L|Hago26|2.68M|8|192.00K
L|daybee|1.18M|8|102.67K
L|Venom17|636.86K|8|59.31K
L|Bubobubo|629.78K|8|128.13K
L|Yullong|208.42K|8|143.11K
L|MuffinKnight|143.56K|8|269.21K
L|皇黎|116.69K|8|25.87K
L|MsPoppycorn|105.83K|8|113.15K
M|Michelo|1.49M|6|491.85K
M|Tuup|1.47M|11|137.43K
M|Zeuzo|856.41K|8|529.15K
M|Hansi218|795.24K|12|535.18K
M|Shoex|480.58K|8|441.74K
M|SilverScope|172.43K|10|366.38K
M|Isterbuk|120.80K|7|88.85K
M|Heynow|83.01K|11|422.11K
R|MHARU|756.53K|6|153.67K
R|TheDragonix725|710.85K|8|474.71K
R|GoatGeass|559.25K|11|112.12K
R|Itsgeorgees|456.32K|11|417.88K
R|Terminus323|225.30K|10|383.79K
R|Ilportoghese|63.40K|3|104.74K
R|LeKo|51.62K|5|6993
R|thesithlor|23.94K|3|0"""),
   "theirStats": oppfull("""
L|ISoLamento|986.45K|8
L|Redtalons|493.66K|5
L|MarkizDeSade|166.31K|8
L|JessLiu|117.11K|3
L|Giruffe|87.38K|5
L|Kraven7k|45.44K|3
L|k3nz1k|44.10K|5
L|Tg13|39.56K|4
M|KiLess|5.57M|12
M|ZorojuroZ|892.31K|12
M|Cableguy|722.10K|12
M|XavierGame|482.55K|12
M|whistlerer|446.79K|12
M|臭懶蛋|229.15K|12
M|Mocjuju|215.88K|12
M|multiple|182.65K|12
R|SamuelV|1.19M|11
R|Vince13720|987.47K|11
R|Bremsstrahlung|960.16K|11
R|sovegier|884.89K|11
R|Thatkent|882.35K|11
R|樂樂樂樂樂樂|801.44K|11
R|caiman|550.65K|11
R|BillyDowns|517.25K|11"""),
   "notes": "Unauthorized swaps: Gaga94 → Heynow (Middle) and TylerG → GoatGeass (Right) after the lineup was set."},
  {"n": 3, "date": "2026-11-08", "opponent": "BlockMagic", "status": "done", "result": "L", "score": "0-3",
   "strategy": "Predicted BlockMagic would repeat their lanes (they did). All-in Dragoon stack on Right vs KiênLốp, their slowest-killing lane; Left and Middle played for damage.",
   "our": lanes(
     lane("Isterbuk, SilverScope, Yullong, Terminus323, GoatGeass, Itsgeorgees, TylerG, Buchacha", "Isterbuk"),
     lane("MuffinKnight, MsPoppycorn, 皇黎, Shoex, Venom17, TheDragonix725, DrShabz, Gaga94", "皇黎"),
     lane("Hago26, Tuup, MHARU, Hansi218, Zeuzo, daybee, Bubobubo, Michelo", "Tuup", role="stack")),
   "their": lanes(lane("Kr0nk, Gà179, oBắpNướng, TeoDocTor, CàPháo, TTSN12P, DragonPk, SongHưng"),
                  lane("TDHoàng, EndlessLevel, Conchymnon, Kin2810, Zodiac599, VNSuma, oooToHooo, SİMGE"),
                  lane("KiênLốp, NightLovell, Migzz, SiêucấpVIP, LâmRâmTặc, MinLibra, DonIsGod, VNĐệThân", "KiênLốp")),
   "laneResults": lanes({"result": "lost", "dur": 6, "ourDmg": 0.42, "theirDmg": 6.36, "theirAlive": 8, "note": "no kills"},
                        {"result": "lost", "dur": 10, "ourDmg": 1.07, "theirDmg": 6.99, "theirAlive": 8, "note": "no kills"},
                        {"result": "lost", "dur": 11, "ourDmg": 6.35, "theirDmg": 8.24, "theirAlive": 6, "note": "killed Migzz and LâmRâmTặc at 8s; KiênLốp survived with 5.47M"}),
   "stats": stats("""
L|TylerG|89.90K|6|123.71K
L|GoatGeass|85.75K|5|8597
L|Terminus323|55.37K|6|310.27K
L|SilverScope|50.00K|6|313.12K
L|Buchacha|43.93K|2|45.44K
L|Itsgeorgees|36.18K|2|55.44K
L|Isterbuk|35.38K|3|278.47K
L|Yullong|20.52K|3|336.22K
M|Venom17|461.95K|10|460.80K
M|Shoex|178.96K|5|308.18K
M|DrShabz|97.34K|6|111.12K
M|MuffinKnight|95.51K|9|605.24K
M|TheDragonix725|88.35K|3|25.78K
M|皇黎|69.16K|5|3133
M|MsPoppycorn|43.29K|4|56.26K
M|Gaga94|38.63K|6|59.13K
R|Hago26|2.62M|8|520.19K
R|Michelo|907.51K|8|156.06K
R|Tuup|696.66K|11|134.05K
R|Zeuzo|526.68K|6|456.27K
R|MHARU|469.57K|3|53.27K
R|Bubobubo|404.08K|6|456.36K
R|daybee|399K|5|59.73K
R|Hansi218|330.36K|11|499.37K"""),
   "theirStats": oppfull("""
L|Kr0nk|1.94M|6
L|Gà179|1.43M|6
L|oBắpNướng|1.21M|6
L|TeoDocTor|500.34K|6
L|CàPháo|454.05K|6
L|TTSN12P|451.63K|6
L|DragonPk|229.85K|6
L|SongHưng|148.86K|6
M|TDHoàng|2.05M|10
M|EndlessLevel|1.28M|10
M|Conchymnon|1.09M|10
M|Kin2810|683.72K|10
M|Zodiac599|539.70K|10
M|VNSuma|469.79K|10
M|oooToHooo|443.17K|10
M|SİMGE|437.41K|10
R|KiênLốp|5.47M|11
R|NightLovell|842.05K|11
R|Migzz|651.33K|8
R|SiêucấpVIP|394.40K|11
R|LâmRâmTặc|390.99K|8
R|MinLibra|271.23K|11
R|DonIsGod|136.23K|11
R|VNĐệThân|87.74K|11"""),
   "notes": "81% of our round damage came from the Right stack, and it produced our only kills vs BlockMagic all week. Their weakest anchor had 7 more Mythic stars than our best."}
 ]
}

# ======================= WEEK OF 2026-11-09 =======================
w2 = {
 "id": "2026-11-09", "label": "Week of Nov 9",
 "group": [{"guild": "Whispers", "power": 477.12}, {"guild": "ArchAcademy", "power": 371.84}, {"guild": "Moonfall", "power": 238.31}, {"guild": "おぶんぐさん", "power": 206.64}],
 "standings": [{"guild": "Whispers", "pts": 9, "flags": 8, "dmg": 56.06}, {"guild": "ArchAcademy", "pts": 6, "flags": 7, "dmg": 48.59},
               {"guild": "おぶんぐさん", "pts": 3, "flags": 3, "dmg": 36.97}, {"guild": "Moonfall", "pts": 0, "flags": 0, "dmg": 15.98}],
 "final": True,
 "lessons": ["Gear set (Dragoon vs Oracle) is the strongest predictor of Expedition DPS: 7 fights, our guild and three opponents.",
             "Artifact tiering does nothing at lane level (R1 and R2 tests). Artifacts track account strength more than they add damage.",
             "Sub Dragoon players out-damage our low Oracle starters (R3 test).",
             "Lining up lane strength against a predictable opponent works.",
             "No unauthorized swaps in R2 or R3."],
 "rounds": [
  {"n": 1, "date": "2026-11-12", "opponent": "Whispers", "status": "done", "result": "L", "score": "1-2",
   "strategy": "Artifact tier test: anchors kept, the other 21 split into High / Medium / Low ATK-bonus tiers.",
   "our": lanes(
     lane("MHARU, MuffinKnight, Shoex, Gaga94, SilverScope, Venom17, Terminus323, TylerG", "MHARU", tier="Medium"),
     lane("Tuup, 皇黎, Isterbuk, Zeuzo, daybee, Bubobubo, Hansi218, Heynow", "Tuup", tier="High"),
     lane("Hago26, MsPoppycorn, Yullong, Michelo, Ilportoghese, JJJRRRBBB, thesithlor, KatieCarmine", "Hago26", tier="Low")),
   "their": lanes(
     lane("Ghetti, Thalli, jt0316, 1223sfhhfnd, CNewb, CrystalMav, xCosmiQ, Realmouseman", "Ghetti"),
     lane("suc1, Mavio, SailingStone, exsign, Notix5k, PAW, GriiiS, Randoome", "suc1", role="stack"),
     lane("DarrenWct, Myng, Tresnja, edhead, floppytoppy, MeiQi, GrImBlaH, DaBlacksmith", "Tresnja")),
   "laneResults": lanes({"result": "lost", "dur": 13, "ourDmg": 5.86, "theirDmg": 8.84, "theirAlive": 8},
                        {"result": "lost", "dur": 12, "ourDmg": 2.23, "theirDmg": 7.36, "note": "4 of ours dead at 3s; only Tuup lasted 12s; 0 kills"},
                        {"result": "won", "dur": 13, "ourDmg": 7.87, "theirDmg": 7.00}),
   "stats": stats("""
L|MHARU|2.35M|11|143.26K
L|Venom17|1.60M|11|209.37K
L|Shoex|671.89K|7|377.97K
L|TylerG|580.30K|7|110.08K
L|MuffinKnight|233.95K|13|611.06K
L|Gaga94|185.70K|6|88.52K
L|Terminus323|151.33K|10|416.10K
L|SilverScope|83.67K|6|7348
M|Tuup|945.34K|12|554.92K
M|daybee|329.36K|3|65.93K
M|Hansi218|296.03K|6|100.91K
M|Zeuzo|278.07K|3|126.47K
M|Bubobubo|209.00K|3|64.58K
M|皇黎|123.91K|4|421.70K
M|Isterbuk|30.50K|3|49.03K
M|Heynow|14.76K|4|15.30K
R|Hago26|4.69M|13|332.29K
R|Michelo|2.19M|10|510.62K
R|KatieCarmine|283.94K|13|86.81K
R|MsPoppycorn|200.62K|10|574.47K
R|Ilportoghese|184.05K|9|536.60K
R|Yullong|170.93K|13|177.98K
R|thesithlor|88.07K|9|375.80K
R|JJJRRRBBB|64.62K|8|31.75K"""),
   "theirStats": oppfull("""
L|Ghetti|6.01M|13
L|Thalli|593.95K|13
L|jt0316|590.52K|13
L|1223sfhhfnd|531.72K|13
L|CNewb|385.35K|13
L|CrystalMav|283.59K|13
L|xCosmiQ|273.93K|13
L|Realmouseman|171.98K|13
M|suc1|1.21M|12
M|exsign|1.15M|12
M|SailingStone|998.49K|12
M|Mavio|979.06K|12
M|Notix5k|933.11K|12
M|PAW|840.33K|12
M|GriiiS|816.35K|12
M|Randoome|432.35K|12
R|DarrenWct|1.39M|9
R|Myng|1.29M|10
R|Tresnja|1.17M|9
R|edhead|1.05M|8
R|floppytoppy|924.85K|13
R|MeiQi|464.89K|7
R|GrImBlaH|425.18K|9
R|DaBlacksmith|289.33K|9"""),
   "offSet": ["KatieCarmine"],
   "notes": "Unauthorized swaps: TheDragonix725 → Heynow (Middle) and Itsgeorgees → JJJRRRBBB (Right), after the 20:51 PT deployment screen. KatieCarmine was on Oracle. Whispers: Ghetti alone carried Left; all three other big anchors stacked Middle."},
  {"n": 2, "date": "2026-11-13", "opponent": "おぶんぐさん", "status": "done", "result": "W", "score": "3-0",
   "strategy": "Rotated-anchor tier test: tiers stay on their lanes, Tuup and Hago26 swap. Every lane out-anchors their best scanned anchor.",
   "our": lanes(
     lane("MHARU, MuffinKnight, Shoex, Gaga94, SilverScope, Venom17, Terminus323, TylerG", "MHARU", tier="Medium"),
     lane("Hago26, 皇黎, Isterbuk, Zeuzo, daybee, Bubobubo, Hansi218, TheDragonix725", "Hago26", tier="High"),
     lane("Tuup, MsPoppycorn, Yullong, Michelo, Ilportoghese, Itsgeorgees, thesithlor, KatieCarmine", "Tuup", tier="Low")),
   "their": lanes(
     lane("すいうい, ほらんど, みるさこ, あいこる, もんちっちい, まにだ, うーにだ, akiฅ", "みるさこ"),
     lane("Kwater, 警備主任, Maeppa, けつなあな2, jatten, incoshu, かむかむ葡萄, シノギヒサノ", "jatten"),
     lane("えむえーさん, Tonari, Takbon, ジャークチキ, かつつつつ, V C, ふくけいと, IamWina", "えむえーさん")),
   "laneResults": lanes({"result": "won", "dur": 14, "ourDmg": 6.12, "theirDmg": 4.54, "ourAlive": 8},
                        {"result": "won", "dur": 7, "ourDmg": 4.93, "theirDmg": 1.00, "ourAlive": 8, "note": "only Kwater of theirs lasted"},
                        {"result": "won", "dur": 15, "ourDmg": 5.54, "theirDmg": 6.73, "ourAlive": 3, "note": "V C was their last player; Tuup, KatieCarmine, Yullong alive"}),
   "stats": stats("""
L|MHARU|2.30M|14|145.59K
L|Venom17|1.26M|14|121.31K
L|Shoex|1.00M|14|49.76K
L|TylerG|818.04K|14|136.89K
L|SilverScope|195.37K|14|38.86K
L|Gaga94|195.31K|14|71.88K
L|Terminus323|189.65K|14|80.37K
L|MuffinKnight|166.45K|14|272.15K
M|Hago26|1.98M|7|128.32K
M|Zeuzo|913.94K|7|92.83K
M|daybee|669.00K|7|80.34K
M|TheDragonix725|538.17K|7|94.27K
M|Bubobubo|477.25K|7|98.55K
M|Hansi218|182.90K|7|129.33K
M|Isterbuk|90.89K|7|80.11K
M|皇黎|78.34K|7|15.14K
R|Michelo|1.81M|9|203.60K
R|Tuup|1.71M|15|173.63K
R|Itsgeorgees|749.40K|10|147.55K
R|KatieCarmine|387.99K|15|92.23K
R|MsPoppycorn|342.55K|13|662.64K
R|Yullong|249.65K|15|146.61K
R|thesithlor|149.78K|10|399.90K
R|Ilportoghese|142.59K|6|138.85K"""),
   "offSet": ["KatieCarmine"],
   "theirStats": oppfull("""
L|ほらんど|1.41M|14
L|すいうい|987.86K|11
L|あいこる|879.39K|14
L|もんちっちい|611.87K|13
L|まにだ|291.20K|8
L|みるさこ|240.18K|7
L|うーにだ|82.79K|9
L|akiฅ|35.44K|9
M|Kwater|594.50K|7
M|Maeppa|145.56K|3
M|けつなあな2|77.78K|4
M|警備主任|61.63K|3
M|かむかむ葡萄|58.62K|4
M|jatten|48.28K|3
M|incoshu|10.07K|2
M|シノギヒサノ|8522|6
R|えむえーさん|4.41M|14
R|Tonari|785.39K|13
R|Takbon|566.22K|9
R|かつつつつ|485.42K|10
R|V C|244.38K|15
R|ジャークチキ|201.30K|8
R|ふくけいと|25.33K|5
R|IamWina|13.30K|6"""),
   "notes": "Their lanes were the same as their R1 vs Moonfall (now confirmed from the Details screens). Lineup matched the plan."},
  {"n": 3, "date": "2026-11-14", "opponent": "Moonfall", "status": "done", "result": "W", "score": "3-0",
   "strategy": "Sub Dragoon swap test: 4 lowest-DPS Oracle starters out, 4 sub Dragoon players in (Middle). Lane strength lined up against Moonfall's repeated lanes.",
   "our": lanes(
     lane("Hago26, 皇黎, Isterbuk, Zeuzo, daybee, Bubobubo, Hansi218, TheDragonix725", "Hago26"),
     lane("Tuup, KatieCarmine, Michelo, Itsgeorgees, Buchacha, DrShabz, Tw3aKZ, KevinShock", "Tuup", tier="Test"),
     lane("MHARU, MuffinKnight, SilverScope, Shoex, Terminus323, Venom17, TylerG, Gaga94", "MHARU")),
   "power": {"Hago26": 14.09, "Isterbuk": 12.08, "Hansi218": 10.54, "Zeuzo": 10.23, "daybee": 10.08, "皇黎": 10.04, "Bubobubo": 7.89, "TheDragonix725": 7.63,
             "Tuup": 11.65, "KatieCarmine": 8.32, "Michelo": 7.85, "Itsgeorgees": 7.39, "Buchacha": 6.92, "DrShabz": 6.80, "Tw3aKZ": 6.32, "KevinShock": 6.25,
             "MuffinKnight": 11.92, "MHARU": 10.72, "SilverScope": 10.70, "Shoex": 9.69, "Terminus323": 9.24, "Venom17": 8.85, "TylerG": 7.09, "Gaga94": 6.81},
   "their": lanes(
     lane("tiaguinhow, Safooe, P109163804, 2tay3em, ELTVM, Pyronic, Ryknowz, BaBaa", "Pyronic"),
     lane("Mikouu, P109263216, Pakito85, ImJonesin, JedjEdjeD, Absolooy", "P109263216"),
     lane("Togyen, Eiaxy, AsTRa, Waikato, RamixArcher, P109184534, Kitkatkhai, Janczyk343", "Waikato")),
   "laneResults": lanes({"result": "won", "dur": 9, "ourDmg": 7.20, "theirDmg": 2.28, "ourAlive": 8, "theirAlive": 0},
                        {"result": "won", "dur": 7, "ourDmg": 4.14, "theirDmg": 0.42, "ourAlive": 8, "theirAlive": 0},
                        {"result": "won", "dur": 11, "ourDmg": 4.64, "theirDmg": 1.93, "ourAlive": 8, "theirAlive": 0}),
   "stats": stats("""
L|Hago26|2.69M|9|202.56K
L|daybee|1.10M|9|152.90K
L|Zeuzo|975.48K|9|125.39K
L|Bubobubo|781.52K|9|192.35K
L|TheDragonix725|532.33K|9|104.25K
L|Hansi218|437.74K|9|124.21K
L|皇黎|404.65K|9|80.86K
L|Isterbuk|281.87K|9|182.75K
M|Michelo|1.23M|7|107.93K
M|DrShabz|697.35K|7|123.73K
M|Tw3aKZ|537.13K|7|147.06K
M|KevinShock|506.40K|7|59.16K
M|Buchacha|442.52K|7|149.55K
M|Tuup|393.16K|7|54.65K
M|Itsgeorgees|310.20K|7|13.35K
M|KatieCarmine|21.64K|7|71.87K
R|Shoex|1.46M|11|64.85K
R|MHARU|1.38M|11|143.42K
R|Venom17|655.71K|11|130.29K
R|TylerG|451.94K|11|98.64K
R|SilverScope|198.67K|11|16.57K
R|Terminus323|184.27K|11|66.73K
R|MuffinKnight|179.27K|11|246.71K
R|Gaga94|134.10K|11|60.43K"""),
   "theirStats": oppfull("""
L|tiaguinhow|971.24K|9
L|Safooe|464.53K|9
L|P109163804|372.63K|7
L|2tay3em|176.88K|5
L|Pyronic|101.47K|4
L|ELTVM|79.93K|5
L|BaBaa|70.98K|5
L|Ryknowz|42.56K|5
M|Pakito85|130.61K|4
M|P109263216|81.21K|6
M|ImJonesin|57.10K|4
M|Mikouu|54.12K|7
M|Absolooy|52.63K|4
M|JedjEdjeD|48.13K|4
R|Eiaxy|864.13K|10
R|Togyen|739.42K|11
R|Waikato|216.75K|7
R|AsTRa|36.40K|3
R|RamixArcher|25.54K|7
R|P109184534|24.10K|8
R|Kitkatkhai|16.47K|5
R|Janczyk343|5965|4"""),
   "offSet": ["KatieCarmine"],
   "notes": "All 24 of ours survived; Moonfall fielded the identical 22 in identical lanes for the third straight round. All 4 sub Dragoon players (63-100K/s) beat the 4 benched Oracle starters' numbers."}
 ]
}

# ======================= WEEK OF 2026-11-16 =======================
w3 = {
 "id": "2026-11-16", "label": "Week of Nov 16",
 "group": [{"guild": "ArchAcademy", "power": 378.29}, {"guild": "Happiness", "power": 338.26}, {"guild": "UkraineArchers", "power": 299.73}, {"guild": "Holymoly", "power": 177.10}],
 "standings": [{"guild": "ArchAcademy", "pts": 9, "flags": 7}, {"guild": "Happiness", "pts": 6, "flags": 6}, {"guild": "UkraineArchers", "pts": 3, "flags": 5}, {"guild": "Holymoly", "pts": 0, "flags": 0}],
 "final": True, "goal": "Win 1st place. Any win over Holymoly in R3 clinches it.",
 "rounds": [
  {"n": 1, "date": "2026-11-20", "opponent": "UkraineArchers", "status": "done", "result": "W", "score": "2-1",
   "strategy": "Spread with a slight stack: top damage dealers under the weakest anchor (MHARU). Tuup and Hago26 out-anchor every UkraineArchers lane.",
   "our": lanes(
     lane("Hago26, Isterbuk, Bubobubo, TheDragonix725, MuffinKnight, Tw3aKZ, Buchacha, KevinShock", "Hago26"),
     lane("Tuup, LeKo, Hansi218, SilverScope, Terminus323, TylerG, Itsgeorgees, KatieCarmine", "Tuup"),
     lane("MHARU, 皇黎, daybee, Zeuzo, Shoex, Venom17, Michelo, DrShabz", "MHARU", role="stack")),
   "their": lanes(
     lane("hctangaa, mystogan2, CursedXJoker, Romko94, BenjiBanass, Sra4ka, mylittleprincess, SRae", "hctangaa"),
     lane("swagginpanda, Ismae96, Rubirosa69, Xenyu, MortyFree, larrygoldjohn, GodShaa, MTVG", "swagginpanda", role="stack"),
     lane("Unmolo56, 1kraP, Hibrios, Sigiris, ZC18, Toolbro, Ranker01, gooatt", "Unmolo56")),
   "laneResults": lanes({"result": "won", "dur": 13, "ourDmg": 6.35, "theirDmg": 2.73, "ourAlive": 8},
                        {"result": "lost", "dur": 18, "ourDmg": 6.43, "theirDmg": 11.13, "theirAlive": 3, "note": "we killed 5; swagginpanda alone 5.43M (49%)"},
                        {"result": "won", "dur": 7, "ourDmg": 4.42, "theirDmg": 4.29, "ourAlive": 4}),
   "stats": stats("""
L|Hago26|3.26M|13|297.75K
L|Bubobubo|616.78K|13|140.64K
L|TheDragonix725|577.43K|13|148.91K
L|Tw3aKZ|512.47K|13|174.02K
L|KevinShock|497.29K|13|128.92K
L|Buchacha|440.41K|13|201.26K
L|Isterbuk|251.95K|13|227.69K
L|MuffinKnight|198.53K|13|392.37K
M|Tuup|1.90M|18|586.79K
M|KatieCarmine|1.47M|16|155.28K
M|Hansi218|938.98K|14|528.40K
M|Itsgeorgees|857.12K|11|77.47K
M|TylerG|739.09K|17|551.04K
M|SilverScope|306.66K|12|362.27K
M|Terminus323|158.31K|9|74.54K
M|LeKo|61.86K|6|19.32K
R|MHARU|1.18M|7|127.93K
R|Michelo|836.02K|7|83.89K
R|Zeuzo|558.84K|7|63.59K
R|daybee|546.87K|4|102.11K
R|Venom17|481.86K|7|60.57K
R|DrShabz|433.97K|5|65.36K
R|Shoex|313.20K|4|84.28K
R|皇黎|66.88K|5|340.86K"""),
   "theirStats": oppfull("""
L|mystogan2|652.13K|6
L|CursedXJoker|593.09K|10
L|Romko94|398.44K|8
L|BenjiBanass|324.25K|7
L|Sra4ka|256.41K|13
L|mylittleprincess|224.95K|11
L|hctangaa|149.68K|7
L|SRae|135.81K|9
M|swagginpanda|5.43M|18
M|Rubirosa69|1.27M|16
M|Xenyu|1.11M|16
M|MortyFree|941.16K|18
M|Ismae96|873.58K|9
M|GodShaa|817.17K|18
M|larrygoldjohn|580.79K|12
M|MTVG|107.71K|8
R|1kraP|1.22M|6
R|ZC18|691.07K|7
R|Hibrios|546.23K|3
R|Toolbro|476.42K|5
R|Sigiris|400.46K|3
R|Unmolo56|398.12K|4
R|Ranker01|280.93K|3
R|gooatt|279.65K|5"""),
   "notes": "Healing: UA's 3 Griffin players healed 500-800K each and stretched the Left fight to 13s.\nGear switch test: KatieCarmine went from 3-26K/s on Oracle to 92K/s on Dragoon, same character and artifacts. The gear set alone made the jump.\nBench Dragoon test: DrShabz 87K, Tw3aKZ 39K, KevinShock 38K and Buchacha 34K/s beat every Oracle starter except Shoex (78K/s); the rest did 10-26K/s.\nWeak-anchor stack test: the carries under MHARU won Right in 7s, but only just (4.42M vs 4.29M, 4 of 8 alive). It held, without much margin.\nMHARU Helix test: 169K/s, top of Right and inside his usual range (121-214K/s), so no clear change from the switch yet.\nArtifact test: not scored on its own here; R3's same-fight test is the cleaner read."},
  {"n": 2, "date": "2026-11-21", "opponent": "Happiness", "status": "done", "result": "W", "score": "2-1",
   "strategy": "Win-only. All-Dragoon stacks Left and Right so no early Oracle deaths feed Happiness's survival bonus; the Oracle lane goes where KiLess was predicted (Middle) as a planned concession. Lineup chosen DPS-first by 5-match average.",
   "our": lanes(
     lane("Tuup, Michelo, MHARU, daybee, DrShabz, Itsgeorgees, TylerG, KevinShock", "Tuup", role="stack"),
     lane("Isterbuk, Shoex, Buchacha, 皇黎, Ilportoghese, MsPoppycorn, SilverScope, MuffinKnight", "Isterbuk", role="dump"),
     lane("Hago26, Zeuzo, KatieCarmine, Venom17, Bubobubo, TheDragonix725, Tw3aKZ, Hansi218", "Hago26", role="stack")),
   "their": lanes(
     lane("MarkizDeSade, Redtalons, k3nz1k, Kraven7k, Tg13, Giruffe, ISoLamento, JessLiu", "MarkizDeSade"),
     lane("KiLess, whistlerer, Mocjuju, XavierGame, 臭懶蛋, Cableguy, ZorojuroZ", "KiLess", role="stack"),
     lane("Bremsstrahlung, Vince13720, caiman, SamuelV, 樂樂樂樂樂樂, Thatkent, sovegier, BillyDowns", "Bremsstrahlung")),
   "theirPower": {"MarkizDeSade": 8.99, "Redtalons": 8.60, "k3nz1k": 8.08, "Kraven7k": 7.75, "Tg13": 7.24, "Giruffe": 7.21, "ISoLamento": 6.99, "JessLiu": 6.82,
                  "KiLess": 22.71, "whistlerer": 11.35, "Mocjuju": 10.08, "XavierGame": 9.87, "臭懶蛋": 9.31, "Cableguy": 7.60, "ZorojuroZ": 7.57,
                  "Bremsstrahlung": 18.60, "Vince13720": 11.85, "caiman": 11.78, "SamuelV": 11.05, "樂樂樂樂樂樂": 9.68, "Thatkent": 9.16, "sovegier": 8.64, "BillyDowns": 7.96},
   "laneResults": lanes({"result": "won", "dur": 7, "ourDmg": 5.58, "theirDmg": 0.89, "ourAlive": 8},
                        {"result": "lost", "dur": 12, "ourDmg": 1.89, "theirDmg": 7.17, "theirAlive": 7, "note": "planned concession"},
                        {"result": "won", "dur": 17, "ourDmg": 8.27, "theirDmg": 6.64, "ourAlive": 5, "note": "Hago26, Venom17, KatieCarmine, Hansi218, TheDragonix725 alive"}),
   "stats": stats("""
L|Michelo|1.11M|7|75K
L|MHARU|879K|7|85K
L|daybee|862K|7|122K
L|Tuup|829K|7|57K
L|DrShabz|719K|7|83K
L|KevinShock|437K|7|67K
L|Itsgeorgees|431K|7|22K
L|TylerG|318K|7|40K
M|Buchacha|413K|4|133K
M|Shoex|237K|4|31K
M|Ilportoghese|374K|8|375K
M|皇黎|209K|8|329K
M|SilverScope|178K|9|313K
M|MuffinKnight|219K|12|190K
M|Isterbuk|159K|10|366K
M|MsPoppycorn|100K|10|392K
R|Hago26|3.82M|17|321K
R|Zeuzo|877K|13|531K
R|Bubobubo|392K|7|447K
R|Venom17|868K|17|140K
R|Tw3aKZ|457K|10|511K
R|KatieCarmine|648K|17|216K
R|Hansi218|616K|17|290K
R|TheDragonix725|587K|17|528K"""),
   "theirStats": oppfull("""
L|ISoLamento|325.98K|5
L|Redtalons|155.46K|3
L|Giruffe|118.14K|5
L|Kraven7k|83.77K|5
L|JessLiu|78.99K|6
L|k3nz1k|53.38K|7
L|MarkizDeSade|47.13K|4
L|Tg13|31.49K|3
M|KiLess|4.29M|12
M|Cableguy|1.09M|12
M|ZorojuroZ|566.95K|12
M|whistlerer|413.41K|12
M|XavierGame|382.09K|12
M|Mocjuju|241.19K|12
M|臭懶蛋|191.15K|12
R|Vince13720|1.39M|11
R|sovegier|1.30M|11
R|Bremsstrahlung|1.02M|9
R|caiman|952.71K|17
R|SamuelV|921.24K|6
R|樂樂樂樂樂樂|476.10K|4
R|BillyDowns|372.86K|8
R|Thatkent|207.56K|5"""),
   "notes": "Plan: KiLess landed in Middle as predicted, so our planned concession soaked their best player while both all-Dragoon stacks won.\nHealing: about 3M of our healing on Right stretched that fight to 17s and lowered everyone's per-second numbers there; compare DPS within a lane.\nLearned: conceding the lane with their one carry (KiLess 4.29M) worked better than fighting it, as we did against swagginpanda in R1.\nNo tests: this round was win-only."},
  {"n": 3, "date": "2026-11-22", "opponent": "Holymoly", "status": "done", "result": "W", "score": "3-0",
   "strategy": "Testing round (any win clinches 1st). Assumes Holymoly repeats the same 24 in the same lanes a third time. Left secures the flag vs their best lane; Middle is a data lane; Right is an artifact test lane.",
   "our": lanes(
     lane("Hago26, MHARU, daybee, Venom17, KatieCarmine, TheDragonix725, Michelo, Itsgeorgees", "Hago26"),
     lane("Hansi218, Terminus323, Shoex, Heynow, LeKo, GoatGeass, slenderu, Abr0", "LeKo"),
     lane("Tuup, Zeuzo, Bubobubo, DrShabz, TylerG, Buchacha, Tw3aKZ, KevinShock", "Tuup")),
   "power": {"Hago26": 14.45, "MHARU": 10.86, "daybee": 10.53, "Venom17": 8.95, "KatieCarmine": 8.27, "TheDragonix725": 8.06, "Michelo": 7.96, "Itsgeorgees": 7.46,
             "Hansi218": 10.69, "Terminus323": 9.24, "Shoex": 9.71, "Heynow": 9.20, "LeKo": 7.73, "GoatGeass": 7.18, "slenderu": 6.59, "Abr0": 6.59,
             "Tuup": 12.13, "Zeuzo": 10.37, "Bubobubo": 8.04, "DrShabz": 7.89, "TylerG": 7.22, "Buchacha": 7.13, "Tw3aKZ": 6.47, "KevinShock": 6.44},
   "their": lanes(
     lane("Summerinwhy, Godfathagianotti, Bigslingus, Zkeler, kisskool93, Strife335, slander1111, SeOz", "Summerinwhy"),
     lane("Călin, iziz, Speshled, PREX, Cage1899, doffa, IMostwantedI, Levianthan", "Călin", role="dump"),
     lane("Bigjerjer, Lokudon, SPITE, FreakMan, amarekan, BigD86, XiTriggz, Puzlan", "Bigjerjer")),
   "laneResults": lanes({"result": "won", "dur": 9, "ourDmg": 5.20, "theirDmg": 1.90, "ourAlive": 8},
                        {"result": "won", "dur": 11, "ourDmg": 3.75, "theirDmg": 0.67, "ourAlive": 8},
                        {"result": "won", "dur": 9, "ourDmg": 5.74, "theirDmg": 2.87, "ourAlive": 8}),
   "stats": stats("""
L|Hago26|1.50M|9|175.37K
L|Michelo|782.18K|9|84.60K
L|daybee|726.60K|9|108.95K
L|MHARU|603.50K|9|139.83K
L|KatieCarmine|537.80K|9|116.32K
L|TheDragonix725|512.20K|9|60.23K
L|Venom17|381.75K|9|50.90K
L|Itsgeorgees|160.54K|9|63.71K
M|Terminus323|1.30M|11|74.98K
M|Hansi218|1.03M|11|116.53K
M|Shoex|685.78K|11|48.12K
M|slenderu|353.02K|11|24.15K
M|GoatGeass|179.03K|11|50.15K
M|LeKo|77.21K|11|4930
M|Heynow|64.48K|11|24.16K
M|Abr0|58.62K|11|27.64K
R|Zeuzo|1.05M|9|106.94K
R|DrShabz|965.32K|9|134.35K
R|Bubobubo|788.37K|9|131.85K
R|KevinShock|736.24K|9|98.97K
R|Buchacha|623.98K|9|129.68K
R|Tuup|593.59K|9|79.99K
R|TylerG|530.76K|9|64.48K
R|Tw3aKZ|449.36K|9|89.54K"""),
   "theirStats": oppstats("""
L|Godfathagianotti|99|495.63K|5
L|SeOz|80|400.10K|5
L|Zkeler|96|384.13K|4
L|Bigslingus|107|320.18K|3
L|Strife335|17|104.49K|6
L|Summerinwhy|13|101.60K|8
L|kisskool93|13|50.53K|4
L|slander1111|5|43.43K|9
M|iziz|23|254.28K|11
M|Speshled|16|109.88K|7
M|Cage1899|10|86.62K|9
M|doffa|11|66.03K|6
M|PREX|16|62.51K|4
M|Călin|5|42.37K|8
M|Levianthan|4|28.43K|7
M|IMostwantedI|4|15.18K|4
R|Lokudon|229|1.83M|8
R|SPITE|43|341.50K|8
R|amarekan|52|259.71K|5
R|FreakMan|25|147.72K|6
R|Bigjerjer|18|105.97K|6
R|Puzlan|10|82.83K|8
R|BigD86|11|63.65K|6
R|XiTriggz|4|39.35K|9"""),
   "notes": "Lineup: set in game Nov 21, 9:53 AM CT, matching the plan. Lanes locked Nov 22, 4:00 AM PT.\nChange: Terminus323 (just switched to Chaotic Dragoon) replaced DrFuko in Middle; Heynow stayed.\nPower: Terminus323's number is his main-profile power (9.24M, per Daby); his deployment screen wasn't captured.\nPrediction: about 95% to win, about 75% to sweep 3-0.\nResult: won 3-0, and all 24 of ours survived every lane. Holymoly fielded the same 24 in the same lanes for the third round in a row.\nArtifact test: higher ATK didn't come out ahead in 2 of 3 Right groups. Tuup did 66K/s at 6.43% ATK vs Zeuzo 117K (4.23%) and DrShabz 107K (2.48%); Tw3aKZ 50K / TylerG 59K / KevinShock 82K ran opposite to their ATK; only Bubobubo 88K vs Buchacha 69K went the expected way. Artifacts still don't predict damage.\nNew players: first numbers for slenderu 32K, GoatGeass 16K and Abr0 5K/s.\nHeynow test: 6K/s on a filled preset vs 7K and 4K on his old bare preset. No visible jump.\nShoex test: 62K/s, best Oracle in Middle again (next best slenderu 32K). His Oracle damage looks repeatable.\nDragoon vs Oracle test: in the same fight, Terminus323 118K and Hansi218 94K/s vs 5-62K/s for Middle's 6 Oracle players.\nHelix test: Helix on Oracle stayed low (slenderu 32K, GoatGeass 16K, LeKo 7K/s), which points to Helix plus Dragoon as the combo, not Helix alone.\nFight length test: KatieCarmine did 60K/s in a 9s fight, after 92K at 16s and 38K at 17s. A short fight didn't bring her back to 92K, so no clear fight-length effect yet.\nRepeat test: Holymoly fielded the same 24 in the same lanes a third time. Check each opponent's last lineup before every round.\nGear switch test: Terminus323 went from 11-18K/s on Oracle to 118K/s on Dragoon, top of Middle. Second case after KatieCarmine; his behavior setting also changed, so it isn't a pure gear-only test."}
 ]
}

# ======================= OPPONENTS =======================
opponents = {
 "PWNZ": {"weeks": ["2026-11-02"], "power": 282.56,
   "behavior": ["Identical lanes all 3 rounds of the week of Nov 2: stacks Left and Right, dumps Middle."],
   "scans": [{"date": "2026-11-06", "source": "artifact screens (Mythic / Legendary)", "players": roster("""
2love4me||18|41
KillerOwns||17|29
tesseract|16.16|15|44
雙弓無煙dee|8.26|16|33
Waka|12.92|14|41
BaTuSai||15|21
FadeShadow|9.11|14|26
Konefedya|9.13|13|27
Delocker|13.29|12|36
Aimzu|7.44|13|26
NeBeP||13|25
Grenty|8.14|13|20
TeeeJay|7.40|12|30
affection|7.28|13|17
TseChris|9.53|12|26
Kenwei||12|21
Sugarboy|9.70|11|29
TAKESHA1|7.93|11|23
Tony2608|8.98|11|20
lolzter|7.79|10|24
Punzer||10|15
JaaayM|5.90|9|22
huka|6.39|8|21
Хюй|7.09|7|23
Adikbai||6|20
Huuzy|6.83|4|19""")}]},
 "Happiness": {"weeks": ["2026-11-02", "2026-11-16"], "power": 341.73,
   "behavior": ["Week of Nov 2: rotated every round. KiLess Right → Middle → Left; dump lane Left, Left, Middle.",
                "Week of Nov 16: groups stay together. The KiLess group and the MarkizDeSade group swapped lanes R1 → R2; the Bremsstrahlung group stayed Right.",
                "Deploys 23 (KiLess's lane has only 7)."],
   "scans": [{"date": "2026-11-20", "source": "profile + artifact screens", "players": roster("""
KiLess|22.98|37|56|Dragoon (mixed, all Chaotic)|Griffin amulet + Oracle armor
XavierGame|9.79|17|28|Oracle
whistlerer|11.73|15|29|Oracle
Mocjuju|10.10|15|25|Oracle
臭懶蛋|9.50|13|30|Oracle
ZorojuroZ|7.58|9|19|Dragoon
Cableguy|7.63|9|21|Dragoon
MarkizDeSade|8.78|16|30|Oracle
Redtalons|8.80|11|23|Oracle
k3nz1k|8.04|10|27|Oracle
Kraven7k|7.75|10|26|Oracle
Giruffe|7.21|9|19|Oracle
Tg13|7.24|8|21|Oracle
JessLiu|6.82|8|18|Oracle
ISoLamento|6.97|7|20|Dragoon
Bremsstrahlung|19.42|22|37|Oracle|Leader; Chaotic
SamuelV|11.05|20|31|Dragoon|all Chaotic
caiman|11.75|18|30|Dragoon (mixed)|Griffin amulet + Oracle armor
Vince13720|11.85|14|28|Dragoon
樂樂樂樂樂樂|9.74|14|26|Dragoon
sovegier|8.63|9|18|Dragoon
Thatkent|9.25|8|27|Oracle
BillyDowns|7.95|3|25|Dragoon
MakMak88|6.88|13|17|Oracle|backup
Enoxum|6.48|12|16|Oracle|backup
Katsubn|6.30|9|21|Oracle|backup
Deeh|6.74|8|23|Oracle|backup
MTÜRK|5.86|6|17|Dragoon|backup
Ericulino|6.25|5|20|Dragoon|backup
Lukian|5.03|9|22|Dragoon|backup, Chaotic
Kwoply|5.13|9|14|Dragoon|backup, Chaotic
Jakubko|5.44|7|17|Oracle|backup
Rockatansky|5.65|6|16|Oracle|backup
SpecterSDF|5.82|5|18|Oracle|backup
hiimwsta|4.84|9|14|Oracle|backup""")}]},
 "BlockMagic": {"weeks": ["2026-11-02"],
   "behavior": ["Identical 24-player lanes all 3 rounds of the week of Nov 2; never dumps a lane.",
                "Their weakest anchor had 7 more Mythic stars than our best (Nov 2)."],
   "scans": []},
 "Whispers": {"weeks": ["2026-11-09"], "power": 477.12,
   "behavior": ["Ghetti (52 Mythic) alone carries Left every round seen.", "R1 (Nov 12): all three other big anchors (suc1, Mavio, SailingStone) stacked Middle; Right was Dragoon damage dealers with 18-19 Mythic anchors."],
   "scans": [{"date": "2026-11-12", "source": "artifact + gear screens (42 of 48)", "players": roster("""
Ghetti|29.00|52|88|Dragoon|mostly Dragoon, Lv200; list power 31.19M
suc1||26|32|Mixed|3 Dragoon + 3 Oracle
Mavio||24|39|Oracle
SailingStone||21|30|Dragoon
Tresnja||19|27|Dragoon
Randoome||18|42|Oracle
DarrenWct||18|33|Dragoon
1223sfhhfnd||17|39|Oracle
GriiiS||17|29|Mixed
CrystalMav||17|26|Oracle
Realmouseman||16|34|Oracle
DaBlacksmith||16|38|Dragoon|Oracle ring
Notix5k||16|27|Dragoon
Brainin||16|23|Oracle
Axslan||16|24|Oracle
PAW||15|37|Dragoon
xCosmiQ||15|33|Oracle
ChuckyFinn||15|32|Oracle
Ezzyla||14|21|Oracle
jt0316||14|25|Dragoon
MENDE5K||14|23|Griffin
GrImBlaH||13|26|Griffin
MeiQi||12|31|Dragoon
edhead||12|27|Dragoon
Myng||12|23|Dragoon
Jeyks||12|20|Oracle
Kavarito||11|31|Oracle
Lzla||11|26|Dragoon
Madhav199||10|33|Oracle
PsRt47||10|20|Griffin
Quintana1||10|27|Oracle
DaniT92||10|24|Oracle
exsign||9|18|Mixed
CNewb||9|25|Oracle
Thalli||9|24|Dragoon
Shikakku||9|25|Oracle
floppytoppy||7|29|Dragoon
Backman05||7|21|Oracle
Seisa||7|26|Oracle
Kubikmeteren||7|26|Oracle
Erkano||6|30|Oracle
Arrowknee||3|15|Oracle""")}]},
 "おぶんぐさん": {"weeks": ["2026-11-09"], "power": 206.64,
   "behavior": ["Fairly even lanes (~59M / 54M / 50M) vs Moonfall; strongest damage dealer えむえーさん on Right."],
   "scans": [{"date": "2026-11-13", "source": "artifact + gear screens", "players": roster("""
えむえーさん|10.13|13|30|Dragoon
みるさこ|10.86|12|30|Oracle
ほらんど|7.77|11|26|Dragoon|Leader
Tonari|8.58|6|28|Dragoon
もんちっちい|7.19|9|23|Oracle
Takbon|7.86|8|22|Dragoon
Kwater|7.00|6|20|Dragoon
すいうい|8.11|5|22|Dragoon
けつなあな2|10.24|5|27|Oracle
Maeppa|11.42|11|28|Oracle
オオクチバス|7.73|6|21|Dragoon
まにだ|6.08|5|12|Oracle|Mythic+N gear
うーにだ|4.13|4|11|Oracle|Mythic+N gear
あいこる|6.75|3|12|Dragoon
jatten|7.07|13|23|Griffin
ジャークチキ|6.72|11|20|Oracle
akiฅ|6.84|5|18|Oracle
incoshu|6.35|5|19|Oracle
かつつつつ|5.61|5|23|Dragoon
ふくけいと|4.45|6|20|Oracle
警備主任|4.88|4|16|Oracle
かむかむ葡萄|4.60|5|17|Griffin
V C|3.67|0|11|Dragoon
lillはま|3.54|4|7|Oracle|only 1 artifact page
みこりつ|3.53|4|11|Oracle
IamWina|3.25|3|11|Oracle
シノギヒサノ|2.82|4|8|Oracle
ばずずず|2.84|1|10|Oracle""")}]},
 "Moonfall": {"weeks": ["2026-11-09"], "power": 238.31,
   "behavior": ["Fielded the identical 22 players in identical lanes all 3 rounds (6 in Middle); left most of their top power out.", "Strongest lane Left (Dragoon damage dealers + Pyronic anchor), then Right; Middle weakest."],
   "scans": [{"date": "2026-11-13", "source": "artifact + gear screens", "players": roster("""
Pyronic|9.85|19|30|Oracle
Katauris|9.28|17|32|Oracle|didn't deploy
ELTVM|6.09|15|27|Mixed|list power 9.48M
Waikato|10.02|13|29|Oracle
Inobie|8.12|12|24|Oracle|didn't deploy
Bårtcher|9.00|10|24|Oracle|VL; didn't deploy
2tay3em|8.07|12|22|Oracle
JedjEdjeD|7.50|10|28|Other|gold set
P109263216|7.45|11|25|Oracle
Safooe|7.86|10|23|Dragoon
P109163804|7.37|13|25|Dragoon
kobeo|6.13|12|22|Oracle|didn't deploy
N2Lose|7.00|9|21|Oracle|didn't deploy
Togyen|7.69|8|22|Dragoon
Eiaxy|6.86|7|22|Dragoon
Meenz|6.64|14|26|Oracle|didn't deploy
Mikouu|6.62|9|15|Oracle
Alex697|6.55|6|22|Oracle|didn't deploy
ImJonesin|6.40|8|15|Oracle
tiaguinhow|5.99|4|19|Dragoon
BaBaa|5.96|5|20|Oracle
JayVu|5.71|10|22|Dragoon|didn't deploy
Logjamdamkil|5.31|8|14|Dragoon|didn't deploy
Vubz|5.26|6|12|Oracle|didn't deploy
Bud3ay|4.94|7|12|Oracle|didn't deploy
一中文名一|5.08|6|15|Oracle|didn't deploy
Pakito85|3.90|7|22|Dragoon|Leader
Nez124|4.42|5|15|Dragoon|VL""")}]},
 "UkraineArchers": {"weeks": ["2026-11-16"], "power": 299.73,
   "behavior": ["One real anchor (swagginpanda +360%), who stacked Middle with 7 Dragoon players in R1.", "3 Griffin players (low damage, heavy healing) grouped on one lane."],
   "scans": [{"date": "2026-11-19", "source": "member list + profiles (35 players)", "players": roster("""
swagginpanda|12.98|17|30|Dragoon|Leader; Chaotic
mylittleprincess|11.05|10|21|Griffin|Chaotic
Unmolo56|10.69|13|29|Dragoon|Chaotic
Sigiris|10.43|12|27|Dragoon
hctangaa|10.22|13|29|Oracle|Chaotic
MortyFree|10.04|9|30|Dragoon|Chaotic
ZC18|9.91|11|29|Dragoon
1kraP|9.71|9|26|Dragoon|Chaotic
Toolbro|9.60|7|26|Dragoon
Merlyns|9.17|6|27|Oracle
Hibrios|8.94|9|22|Dragoon
Xenyu|8.89|9|22|Dragoon|Chaotic
Sra4ka|8.58|6|21|Griffin
SRae|8.09|9|27|Griffin
GodShaa|7.66|6|19|Dragoon
Ffedh|6.80|9|23|Oracle
larrygoldjohn|6.80|2|18|Dragoon
MTVG|6.70|8|24|Dragoon|Chaotic, Griffin boots
Ranker01|6.69|5|13|Dragoon
Kobziks|6.55|8|21|Oracle|Chaotic
zENiTH|6.29|10|15|Oracle|Chaotic
KACHDEEEZNUUTS|6.14|5|17|Oracle
Darkinis|6.11|3|14|Oracle|Chaotic
fisa|5.96|7|25|Oracle|all Mythic
CursedXJoker|5.94|10|25|Dragoon|mostly Chaotic
Rubirosa69|5.72|6|19|Mixed|Dragoon + Oracle
Ramal98|5.64|9|22|Oracle|Chaotic
P116177630|5.64|7|20|Griffin|Chaotic
Ismae96|5.60|3|18|Dragoon|Chaotic
Boobba|5.30|10|24|Dragoon|all Mythic
P116159670|5.11|7|19|Oracle|Chaotic
Healer13|4.66|4|15|Oracle|Chaotic
Emijl|4.62|3|18|Oracle|all Mythic
GigaVip|4.54|6|15|Oracle|mixed quality
gooatt|4.38|6|13|Dragoon|mixed quality""")}]},
 "Holymoly": {"weeks": ["2026-11-16"], "power": 177.06,
   "behavior": ["Identical 24 in identical lanes in R1 and R2 (Left Summerinwhy, Middle Călin, Right Bigjerjer).",
                "Left (4 Chaotic Dragoon + Zkeler) is their only competitive lane; Middle is a low-power Mythic-gear dump lane."],
   "scans": [{"date": "2026-11-20", "source": "artifact + gear screens (28 players)", "players": roster("""
Bigjerjer|8.50|15|24|Oracle|Chaotic
Lokudon|8.38|12|25|Dragoon|Chaotic
FreakMan|8.25|12|17|Oracle|Chaotic
Summerinwhy|4.91|11|28|Dragoon|all Mythic
SPITE|6.32|11|19|Mixed|Leader; Dragoon weapon, mostly Mythic, Oracle armor
Strife335|4.48|10|20|Oracle|all Mythic
Bigslingus|6.46|10|18|Dragoon|Chaotic
Călin|2.85|9|27|Other|mostly Legendary+3
Cage1899|3.37|9|14|Oracle|all Mythic
lakyy|3.87|9|14|Oracle|benched
Zkeler|7.79|8|24|Mixed|Dragoon weapon, Oracle rest
Vramer|7.37|8|22|Oracle|benched; Chaotic
IMostwantedI|3.26|8|21|Oracle|all Mythic
BigD86|4.46|8|18|Oracle|Chaotic
amarekan|6.30|8|16|Oracle|Chaotic
iziz|4.38|8|13|Dragoon|mostly Mythic+4
slander1111|6.94|7|19|Oracle|Chaotic
Godfathagianotti|6.38|7|16|Dragoon|Chaotic
Speshled|3.87|6|14|Dragoon|all Mythic
PREX|3.18|5|14|Oracle|all Mythic
SeOz|4.68|5|13|Dragoon|Chaotic
ViscountVexheart|5.28|4|14|Oracle|benched
Levianthan|2.79|4|13|Oracle|all Mythic
Puzlan|6.21|4|13|Oracle|Chaotic
doffa|3.71|4|11|Oracle|all Mythic
kisskool93|8.10|3|21|Oracle|Chaotic
XiTriggz|5.27|3|12|Oracle|Chaotic
VaZaJa|4.43|3|10|Other|benched; gold set""")}]},
}

# Opponents' other matches (their lanes and DPS when they weren't playing us): behavior history for predictions.
observations = [
 {"week": "2026-11-02", "round": 1, "guild": "Happiness", "vs": "BlockMagic", "result": "L 1-2", "note": "Happiness took Right via KiLess.", "lanes": lanes(lane([], partial=True), lane([], partial=True), lane("KiLess", "KiLess", partial=True))},
 {"week": "2026-11-02", "round": 2, "guild": "BlockMagic", "vs": "PWNZ", "result": "W 3-0", "note": "All 24 survived. Same lanes as their R3 vs us.",
  "lanes": lanes(lane("Kr0nk, Gà179, oBắpNướng, TeoDocTor, CàPháo, TTSN12P, DragonPk, SongHưng"),
                 lane("TDHoàng, Conchymnon, EndlessLevel, Zodiac599, Kin2810, VNSuma, oooToHooo, SİMGE"),
                 lane("KiênLốp, NightLovell, Migzz, LâmRâmTặc, SiêucấpVIP, MinLibra, VNĐệThân, DonIsGod", "KiênLốp")),
  "stats": oppfull("""
L|Kr0nk|1.79M|7
L|Gà179|1.32M|7
L|oBắpNướng|826.22K|7
L|TeoDocTor|685.48K|7
L|CàPháo|547.32K|7
L|TTSN12P|276.92K|7
L|DragonPk|244.86K|7
L|SongHưng|137.74K|7
M|TDHoàng|1.53M|6
M|Conchymnon|914.46K|6
M|EndlessLevel|886.68K|6
M|Zodiac599|609.40K|6
M|Kin2810|581.61K|6
M|VNSuma|433.02K|6
M|oooToHooo|322.03K|6
M|SİMGE|314.77K|6
R|KiênLốp|3.19M|13
R|NightLovell|1.26M|13
R|Migzz|963.13K|13
R|LâmRâmTặc|660.34K|13
R|SiêucấpVIP|389.02K|13
R|MinLibra|256.17K|13
R|VNĐệThân|174.36K|13
R|DonIsGod|125.70K|13""")},
 {"week": "2026-11-02", "round": 2, "guild": "PWNZ", "vs": "BlockMagic", "result": "L 0-3", "note": "Same lanes as their R3 vs Happiness.",
  "lanes": lanes(lane("Delocker, Huuzy, affection, KillerOwns, 2love4me, Sugarboy, lolzter, Akiva", "Delocker"),
                 lane("Konefedya, 雙弓無煙dee, Tony2608, Aimzu, Dudc, CosmicNaruto, huka, TAKESHA1"),
                 lane("Хюй, TseChris, TeeeJay, tesseract, Waka, JaaayM, FadeShadow, Grenty")),
  "stats": oppfull("""
L|Delocker|937.26K|6
L|Huuzy|241.58K|7
L|affection|140.84K|2
L|KillerOwns|41.36K|6
L|2love4me|36.74K|3
L|Sugarboy|34.27K|5
L|lolzter|10.65K|3
L|Akiva|1326|2
M|Konefedya|204.27K|4
M|雙弓無煙dee|130.24K|2
M|Tony2608|104.97K|6
M|Aimzu|61.90K|5
M|Dudc|59.24K|2
M|CosmicNaruto|53.27K|5
M|huka|19.71K|5
M|TAKESHA1|1348|2
R|Хюй|817.72K|13
R|TseChris|590.66K|9
R|TeeeJay|376.17K|10
R|tesseract|341.42K|9
R|Waka|216.99K|6
R|JaaayM|114.17K|6
R|FadeShadow|70.67K|5
R|Grenty|48.63K|8""")},
 {"week": "2026-11-02", "round": 3, "guild": "Happiness", "vs": "PWNZ", "result": "W 2-1", "note": "KiLess Left (4.35M); Middle was their dump lane (PWNZ took it). All 8 survived on Right.",
  "lanes": lanes(lane("KiLess, Cableguy, ZorojuroZ, whistlerer, XavierGame, multiple, Mocjuju, 臭懶蛋", "KiLess"),
                 lane("ISoLamento, Redtalons, MarkizDeSade, Giruffe, Kraven7k, Tg13, k3nz1k, JessLiu", role="dump"),
                 lane("SamuelV, Thatkent, sovegier, Vince13720, caiman, 樂樂樂樂樂樂, Bremsstrahlung, BillyDowns")),
  "stats": oppfull("""
L|KiLess|4.35M|14
L|Cableguy|641.94K|14
L|ZorojuroZ|552.66K|14
L|whistlerer|407.33K|11
L|XavierGame|322.11K|14
L|multiple|215.59K|13
L|Mocjuju|187.30K|8
L|臭懶蛋|185.73K|10
M|ISoLamento|1.50M|14
M|Redtalons|1.00M|11
M|MarkizDeSade|229.27K|11
M|Giruffe|226.92K|10
M|Kraven7k|120.92K|5
M|Tg13|99.72K|8
M|k3nz1k|93.85K|7
M|JessLiu|85.40K|8
R|SamuelV|1.51M|11
R|Thatkent|1.38M|11
R|sovegier|1.10M|11
R|Vince13720|921.11K|11
R|caiman|726.17K|11
R|樂樂樂樂樂樂|698.68K|11
R|Bremsstrahlung|667.17K|11
R|BillyDowns|467.92K|11""")},
 {"week": "2026-11-02", "round": 3, "guild": "PWNZ", "vs": "Happiness", "result": "L 1-2", "note": "Won Middle with all 8 alive; Delocker 6.35M on Left wasn't enough.",
  "lanes": lanes(lane("Delocker, Huuzy, affection, 2love4me, Sugarboy, KillerOwns, lolzter, Akiva", "Delocker"),
                 lane("Konefedya, 雙弓無煙dee, Dudc, Tony2608, CosmicNaruto, Aimzu, huka, TAKESHA1"),
                 lane("Хюй, Waka, TseChris, tesseract, TeeeJay, FadeShadow, JaaayM, Grenty")),
  "stats": oppfull("""
L|Delocker|6.35M|14
L|Huuzy|1.51M|13
L|affection|532.40K|4
L|2love4me|457.40K|13
L|Sugarboy|189.96K|7
L|KillerOwns|156.83K|9
L|lolzter|78.28K|4
L|Akiva|33.33K|6
M|Konefedya|1.71M|14
M|雙弓無煙dee|1.70M|14
M|Dudc|1.07M|14
M|Tony2608|428.48K|14
M|CosmicNaruto|321.62K|14
M|Aimzu|257.67K|14
M|huka|145.62K|14
M|TAKESHA1|48.12K|14
R|Хюй|607.46K|11
R|Waka|464.30K|8
R|TseChris|341.88K|10
R|tesseract|308.06K|7
R|TeeeJay|278.35K|6
R|FadeShadow|119.56K|8
R|JaaayM|99.47K|5
R|Grenty|37.96K|4""")},
 {"week": "2026-11-09", "round": 1, "guild": "おぶんぐさん", "vs": "Moonfall", "result": "W 3-0", "note": "All 24 survived (16s / 14s / 9s).",
  "lanes": lanes(lane("すいうい, ほらんど, みるさこ, あいこる, もんちっちい, まにだ, うーにだ, akiฅ", "みるさこ"),
                 lane("Kwater, 警備主任, Maeppa, けつなあな2, jatten, incoshu, かむかむ葡萄, シノギヒサノ", "jatten"),
                 lane("えむえーさん, Tonari, Takbon, ジャークチキ, かつつつつ, V C, ふくけいと, IamWina", "えむえーさん")),
  "stats": oppfull("""
L|すいうい|1.90M|16
L|ほらんど|1.67M|16
L|みるさこ|1.19M|16
L|あいこる|1.17M|16
L|もんちっちい|963.84K|16
L|まにだ|465.44K|16
L|うーにだ|150.13K|16
L|akiฅ|88.88K|16
M|Kwater|1.66M|14
M|警備主任|1.29M|14
M|Maeppa|639.36K|14
M|けつなあな2|370.30K|14
M|jatten|303.76K|14
M|incoshu|226.75K|14
M|かむかむ葡萄|209.30K|14
M|シノギヒサノ|14.88K|14
R|えむえーさん|2.45M|9
R|Tonari|425.79K|9
R|Takbon|414.66K|9
R|ジャークチキ|356.17K|9
R|かつつつつ|334.58K|9
R|V C|254.50K|9
R|ふくけいと|100.01K|9
R|IamWina|42.69K|9""")},
 {"week": "2026-11-09", "round": 1, "guild": "Moonfall", "vs": "おぶんぐさん", "result": "L 0-3", "note": "Deployed only 22 (6 in Middle).",
  "lanes": lanes(lane("tiaguinhow, Safooe, P109163804, 2tay3em, ELTVM, Pyronic, Ryknowz, BaBaa", "Pyronic"),
                 lane("Mikouu, P109263216, Pakito85, ImJonesin, JedjEdjeD, Absolooy", "P109263216"),
                 lane("Togyen, Eiaxy, AsTRa, Waikato, RamixArcher, P109184534, Kitkatkhai, Janczyk343", "Waikato")),
  "stats": oppfull("""
L|P109163804|1.46M|12
L|tiaguinhow|1.14M|14
L|Safooe|672.51K|16
L|2tay3em|199.60K|4
L|ELTVM|154.52K|8
L|BaBaa|152.70K|8
L|Pyronic|147.47K|4
L|Ryknowz|71.86K|5
M|Mikouu|434.70K|14
M|Pakito85|330.69K|6
M|JedjEdjeD|279.05K|12
M|ImJonesin|177.18K|10
M|P109263216|167.35K|9
M|Absolooy|101.11K|8
R|Togyen|1.18M|9
R|Eiaxy|753.55K|6
R|Waikato|228.94K|6
R|AsTRa|117.60K|6
R|RamixArcher|42.38K|6
R|P109184534|31.56K|8
R|Janczyk343|14.88K|6
R|Kitkatkhai|3911|3""")},
 {"week": "2026-11-09", "round": 2, "guild": "Whispers", "vs": "Moonfall", "result": "W 3-0", "note": "All 24 survived. Tresnja and exsign swapped lanes this round (Tresnja Middle, exsign Right); R1 and R3 had them the other way.",
  "lanes": lanes(lane("Ghetti, 1223sfhhfnd, Thalli, jt0316, CNewb, xCosmiQ, Realmouseman, CrystalMav", "Ghetti"),
                 lane("Mavio, GriiiS, Notix5k, suc1, SailingStone, Randoome, PAW, Tresnja", "suc1"),
                 lane("Myng, exsign, edhead, floppytoppy, DarrenWct, GrImBlaH, MeiQi, DaBlacksmith")),
  "stats": oppfull("""
L|Ghetti|2.92M|7
L|1223sfhhfnd|1.63M|7
L|CNewb|754.40K|7
L|jt0316|630.51K|7
L|xCosmiQ|467.18K|7
L|Thalli|414.66K|7
L|Realmouseman|294.78K|7
L|CrystalMav|102.82K|7
M|Mavio|1.37M|5
M|GriiiS|528.48K|5
M|Notix5k|503.54K|5
M|suc1|470.13K|5
M|SailingStone|392.11K|5
M|Randoome|317.96K|5
M|PAW|246.31K|5
M|Tresnja|180.19K|5
R|Myng|823.60K|9
R|exsign|692.23K|9
R|edhead|671.24K|9
R|floppytoppy|602.78K|9
R|DarrenWct|566.76K|9
R|GrImBlaH|520.48K|9
R|MeiQi|490.92K|9
R|DaBlacksmith|338.28K|9""")},
 {"week": "2026-11-09", "round": 2, "guild": "Moonfall", "vs": "Whispers", "result": "L 0-3", "note": "Identical 22 in identical lanes as R1. Middle did 131K total.",
  "lanes": lanes(lane("tiaguinhow, Safooe, P109163804, 2tay3em, ELTVM, Pyronic, Ryknowz, BaBaa", "Pyronic"),
                 lane("Mikouu, P109263216, Pakito85, ImJonesin, JedjEdjeD, Absolooy", "P109263216"),
                 lane("Togyen, Eiaxy, AsTRa, Waikato, RamixArcher, P109184534, Kitkatkhai, Janczyk343", "Waikato")),
  "stats": oppfull("""
L|tiaguinhow|589.37K|5
L|Safooe|381.78K|7
L|P109163804|366.74K|4
L|2tay3em|159.60K|4
L|ELTVM|156.72K|5
L|Pyronic|86.59K|4
L|Ryknowz|31.62K|2
L|BaBaa|23.51K|3
M|Mikouu|29.83K|5
M|P109263216|26.48K|3
M|Pakito85|25.92K|2
M|ImJonesin|22.69K|3
M|JedjEdjeD|20.57K|3
M|Absolooy|5701|2
R|Togyen|703.39K|9
R|Eiaxy|666.51K|8
R|AsTRa|65.40K|7
R|Waikato|45.50K|4
R|RamixArcher|24.47K|6
R|P109184534|23.28K|9
R|Kitkatkhai|8136|4
R|Janczyk343|3689|4""")},
 {"week": "2026-11-09", "round": 3, "guild": "Whispers", "vs": "おぶんぐさん", "result": "W 3-0", "note": "All 24 survived (6s / 8s / 8s). Same lanes as their R1 vs us.",
  "lanes": lanes(lane("Ghetti, 1223sfhhfnd, Thalli, jt0316, CNewb, xCosmiQ, Realmouseman, CrystalMav", "Ghetti"),
                 lane("suc1, Mavio, SailingStone, Notix5k, PAW, GriiiS, exsign, Randoome", "suc1"),
                 lane("Myng, DarrenWct, edhead, Tresnja, MeiQi, floppytoppy, DaBlacksmith, GrImBlaH", "Tresnja")),
  "stats": oppfull("""
L|Ghetti|2.91M|6
L|1223sfhhfnd|689.18K|6
L|Thalli|594.40K|6
L|jt0316|485.68K|6
L|CNewb|420.02K|6
L|xCosmiQ|373.88K|6
L|Realmouseman|128.07K|6
L|CrystalMav|34.23K|6
M|suc1|1.03M|8
M|Mavio|887.02K|8
M|SailingStone|778.43K|8
M|Notix5k|698.15K|8
M|PAW|641.69K|8
M|GriiiS|600.14K|8
M|exsign|442.38K|8
M|Randoome|198.39K|8
R|Myng|1.43M|8
R|DarrenWct|1.10M|8
R|edhead|820.55K|8
R|Tresnja|812.18K|8
R|MeiQi|657.33K|8
R|floppytoppy|556.28K|8
R|DaBlacksmith|314.74K|8
R|GrImBlaH|256.08K|8""")},
 {"week": "2026-11-09", "round": 3, "guild": "おぶんぐさん", "vs": "Whispers", "result": "L 0-3", "note": "Same 24 in the same lanes all three rounds.",
  "lanes": lanes(lane("すいうい, ほらんど, みるさこ, あいこる, もんちっちい, まにだ, うーにだ, akiฅ", "みるさこ"),
                 lane("Kwater, 警備主任, Maeppa, けつなあな2, jatten, incoshu, かむかむ葡萄, シノギヒサノ", "jatten"),
                 lane("えむえーさん, Tonari, Takbon, ジャークチキ, かつつつつ, V C, ふくけいと, IamWina", "えむえーさん")),
  "stats": oppfull("""
L|すいうい|928.77K|6
L|ほらんど|659.32K|5
L|あいこる|570.12K|5
L|みるさこ|318.78K|6
L|もんちっちい|215.66K|6
L|うーにだ|46.32K|6
L|akiฅ|36.77K|6
L|まにだ|24.69K|5
M|Kwater|409.25K|7
M|警備主任|148.24K|6
M|Maeppa|118.83K|7
M|jatten|50.42K|6
M|けつなあな2|40.25K|3
M|かむかむ葡萄|13.48K|4
M|incoshu|9071|4
M|シノギヒサノ|7494|8
R|えむえーさん|2.61M|6
R|Takbon|679.13K|8
R|Tonari|497.88K|7
R|かつつつつ|257.32K|4
R|V C|171.07K|8
R|ジャークチキ|112.42K|5
R|ふくけいと|39.20K|5
R|IamWina|4993|2""")},
 {"week": "2026-11-16", "round": 1, "guild": "Happiness", "vs": "Holymoly", "result": "W 3-0", "note": "Every Happiness player survived; deployed 23.",
  "lanes": lanes(lane("KiLess, Cableguy, ZorojuroZ, XavierGame, whistlerer, Mocjuju, 臭懶蛋", "KiLess"),
                 lane("ISoLamento, Redtalons, Tg13, Giruffe, Kraven7k, MarkizDeSade, k3nz1k, JessLiu", "MarkizDeSade"),
                 lane("sovegier, Vince13720, SamuelV, 樂樂樂樂樂樂, Bremsstrahlung, caiman, BillyDowns, Thatkent", "Bremsstrahlung")),
  "stats": oppfull("""
L|KiLess|2.48M|10
L|Cableguy|522.19K|10
L|ZorojuroZ|486.82K|10
L|XavierGame|372.72K|10
L|whistlerer|335.67K|10
L|Mocjuju|235.59K|10
L|臭懶蛋|178.00K|10
M|ISoLamento|1.17M|15
M|Redtalons|1.14M|15
M|Tg13|491.61K|15
M|Giruffe|333.84K|15
M|Kraven7k|311.55K|15
M|MarkizDeSade|304.28K|15
M|k3nz1k|250.82K|15
M|JessLiu|155.76K|15
R|sovegier|985.92K|6
R|Vince13720|971.97K|6
R|SamuelV|802.31K|6
R|樂樂樂樂樂樂|747.60K|6
R|Bremsstrahlung|652.62K|6
R|caiman|305.73K|6
R|BillyDowns|268.87K|6
R|Thatkent|187.54K|6""")},
 {"week": "2026-11-16", "round": 1, "guild": "Holymoly", "vs": "Happiness", "result": "L 0-3",
  "lanes": lanes(lane("Summerinwhy, Godfathagianotti, Bigslingus, Zkeler, kisskool93, Strife335, slander1111, SeOz", "Summerinwhy"),
                 lane("Călin, iziz, Speshled, PREX, Cage1899, doffa, IMostwantedI, Levianthan", "Călin", role="dump"),
                 lane("Bigjerjer, Lokudon, SPITE, FreakMan, amarekan, BigD86, XiTriggz, Puzlan", "Bigjerjer")),
  "stats": oppstats("""
L|Godfathagianotti|64|385K|6
L|Bigslingus|74|369K|5
L|Zkeler|50|299K|6
L|Summerinwhy|12|122K|10
L|kisskool93|12|96K|8
L|Strife335|14|72K|5
L|slander1111|5|48K|10
L|SeOz|3|12K|4
M|iziz|34|507K|15
M|Speshled|23|272K|12
M|PREX|24|169K|7
M|Cage1899|16|130K|8
M|doffa|8|89K|11
M|IMostwantedI|10|82K|8
M|Călin|7|72K|10
M|Levianthan|6|47K|8
R|Lokudon|139|556K|4
R|SPITE|27|137K|5
R|FreakMan|23|115K|5
R|amarekan|37|112K|3
R|Bigjerjer|32|97K|3
R|BigD86|10|51K|5
R|XiTriggz|4|22K|6
R|Puzlan|5|21K|4""")},
 {"week": "2026-11-16", "round": 2, "guild": "Holymoly", "vs": "UkraineArchers", "result": "L 0-3", "note": "Identical 24 in identical lanes as R1.",
  "lanes": lanes(lane("Summerinwhy, Godfathagianotti, Bigslingus, Zkeler, kisskool93, Strife335, slander1111, SeOz", "Summerinwhy"),
                 lane("Călin, iziz, Speshled, PREX, Cage1899, doffa, IMostwantedI, Levianthan", "Călin", role="dump"),
                 lane("Bigjerjer, Lokudon, SPITE, FreakMan, amarekan, BigD86, XiTriggz, Puzlan", "Bigjerjer")),
  "stats": oppfull("""
L|Bigslingus|1.32M|13
L|Zkeler|996.49K|10
L|Godfathagianotti|978.11K|11
L|SeOz|735.49K|12
L|kisskool93|281.20K|14
L|Strife335|199.22K|7
L|Summerinwhy|104.09K|9
L|slander1111|102.49K|16
M|iziz|71.64K|3
M|Speshled|49.56K|4
M|IMostwantedI|21.68K|5
M|Călin|14.53K|3
M|PREX|13.47K|2
M|doffa|13.45K|2
M|Levianthan|11.52K|5
M|Cage1899|9970|2
R|Lokudon|716.31K|4
R|SPITE|252.95K|6
R|FreakMan|224.35K|5
R|amarekan|85.22K|3
R|Bigjerjer|80.19K|3
R|Puzlan|61.63K|5
R|BigD86|43.15K|3
R|XiTriggz|38.73K|7""")},
 {"week": "2026-11-16", "round": 2, "guild": "UkraineArchers", "vs": "Holymoly", "result": "W 3-0", "note": "Griffin trio healed ~2.0M on Left.",
  "lanes": lanes(lane("Ranker01, gooatt, Romko94, hctangaa, MTVG, mylittleprincess, Sra4ka, SRae", "hctangaa"), lane("swagginpanda, Ismae96, Rubirosa69, GodShaa, Xenyu, MortyFree, larrygoldjohn, BenjiBanass", "swagginpanda"), lane("1kraP, Sigiris, ZC18, Unmolo56, mystogan2, Hibrios, Toolbro, CursedXJoker")),
  "stats": oppfull("""
L|Ranker01|1.53M|16
L|gooatt|978.28K|16
L|hctangaa|674.33K|16
L|Romko94|367.53K|6
L|mylittleprincess|350.76K|16
L|Sra4ka|324.92K|16
L|MTVG|305.83K|9
L|SRae|291.68K|16
M|swagginpanda|1.07M|5
M|Ismae96|430.19K|5
M|Rubirosa69|405.11K|5
M|GodShaa|361.73K|5
M|Xenyu|354.72K|5
M|MortyFree|313.89K|5
M|larrygoldjohn|288.25K|5
M|BenjiBanass|178.61K|5
R|1kraP|1.31M|7
R|Sigiris|678.20K|7
R|ZC18|653.92K|7
R|Unmolo56|619.58K|7
R|mystogan2|575.80K|7
R|Hibrios|514.68K|7
R|Toolbro|384.19K|7
R|CursedXJoker|322.30K|7""")},
 {"week": "2026-11-16", "round": 3, "guild": "Happiness", "vs": "UkraineArchers", "result": "W 2-1", "note": "Happiness took Middle (KiLess) and Right, UkraineArchers took Left (confirmed, round schedule screen). Same 23 in the same lanes as their R2 vs us.",
  "lanes": lanes(lane("MarkizDeSade, Redtalons, k3nz1k, Kraven7k, Tg13, Giruffe, ISoLamento, JessLiu", "MarkizDeSade"),
                 lane("KiLess, whistlerer, Mocjuju, XavierGame, 臭懶蛋, Cableguy, ZorojuroZ", "KiLess"),
                 lane("Bremsstrahlung, Vince13720, caiman, SamuelV, 樂樂樂樂樂樂, Thatkent, sovegier, BillyDowns", "Bremsstrahlung")),
  "stats": oppstats("""
L|Redtalons|87|1.13M|13
L|ISoLamento|73|1.02M|14
L|MarkizDeSade|29|322.25K|11
L|Giruffe|18|277.23K|15
L|JessLiu|25|273.28K|11
L|Kraven7k|17|243.43K|14
L|Tg13|11|89.49K|8
L|k3nz1k|10|78.08K|8
M|KiLess|353|4.94M|14
M|Cableguy|72|861.83K|12
M|ZorojuroZ|43|608.96K|14
M|whistlerer|41|573.64K|14
M|XavierGame|45|358.66K|8
M|臭懶蛋|38|229.64K|6
M|Mocjuju|20|139.96K|7
R|SamuelV|121|1.45M|12
R|Vince13720|81|969.22K|12
R|sovegier|73|874.61K|12
R|caiman|61|727.69K|12
R|樂樂樂樂樂樂|56|668.05K|12
R|Bremsstrahlung|54|645.20K|12
R|BillyDowns|43|521.55K|12
R|Thatkent|37|219.93K|6""")},
 {"week": "2026-11-16", "round": 3, "guild": "UkraineArchers", "vs": "Happiness", "result": "L 1-2", "note": "Won Left with all 8 alive (Ranker01 2.34M). swagginpanda 4.43M in Middle vs KiLess 4.94M. Romko94, BenjiBanass and mystogan2 not in our scan.",
  "lanes": lanes(lane("Ranker01, gooatt, Romko94, Sra4ka, mylittleprincess, hctangaa, MTVG, SRae"),
                 lane("swagginpanda, GodShaa, Ismae96, Rubirosa69, larrygoldjohn, Xenyu, CursedXJoker, BenjiBanass"),
                 lane("1kraP, Sigiris, Hibrios, ZC18, Toolbro, MortyFree, mystogan2, Unmolo56")),
  "stats": oppstats("""
L|Ranker01|156|2.34M|15
L|gooatt|85|1.27M|15
L|Romko94|68|1.02M|15
L|Sra4ka|25|372.78K|15
L|mylittleprincess|23|343.42K|15
L|hctangaa|23|342.95K|15
L|MTVG|20|305.42K|15
L|SRae|19|286.61K|15
M|swagginpanda|316|4.43M|14
M|GodShaa|76|985.14K|13
M|Ismae96|98|882.21K|9
M|Rubirosa69|74|739.57K|10
M|larrygoldjohn|64|511.65K|8
M|Xenyu|100|498.61K|5
M|CursedXJoker|45|408.23K|9
M|BenjiBanass|52|259.76K|5
R|1kraP|266|1.86M|7
R|Sigiris|92|739.69K|8
R|Hibrios|73|660.02K|9
R|ZC18|90|632.55K|7
R|Toolbro|96|578.84K|6
R|MortyFree|43|513.06K|12
R|mystogan2|89|442.99K|5
R|Unmolo56|60|362.89K|6""")},
]

findings = [
 {"title": "Gear set is the strongest predictor of Expedition DPS", "status": "strong", "evidence": "10+ fights across our guild and 6 opponents: Dragoon median DPS ~4-6x Oracle. Cleanest test: KatieCarmine, same character and artifacts, Oracle 3-26K/s → Dragoon 92K/s (Nov 20)."},
 {"title": "Sub Dragoon players beat low Oracle starters", "status": "strong", "evidence": "Nov 14: 4 sub Dragoon players (63-100K/s) out-damaged the 4 benched Oracle starters with 2-3M less power each. Prefer a Dragoon sub with a mostly filled preset over a low-DPS Oracle starter."},
 {"title": "Artifact tiers don't raise lane DPS", "status": "likely", "evidence": "Two tier tests (Nov 12, 13) showed no tier effect within either gear set. Artifacts correlate with individual DPS mostly through high-artifact anchors (account strength)."},
 {"title": "Anchor Lane HP alone doesn't decide a lane", "status": "likely", "evidence": "Counter-examples: Moonfall's Pyronic (Nov 9 week) and our Tuup vs swagginpanda (Nov 20). A 300K/s Dragoon carry plus a Dragoon lane can beat a higher anchor."},
 {"title": "Helix + Dragoon leads our DPS", "status": "observe", "evidence": "6 rounds in a row Helix on Dragoon has the highest median (e.g. ~121K/s vs ~56K/s for other characters on Dragoon, Nov 21). Observe only; no test yet."},
 {"title": "Healing stretches fights and lowers per-second DPS", "status": "likely", "evidence": "Griffin/heavy-healing lanes (UA Left Nov 20, our Right Nov 21) push everyone's DPS down. Compare DPS within a lane."},
 {"title": "Early deaths snowball", "status": "confirmed mechanic", "evidence": "Expedition Talents: +4% damage per additional player alive and per additional deployed member on the lane. All-Dragoon stacks avoid early Oracle deaths."},
 {"title": "Empty preset slots underperform", "status": "strong", "evidence": "JJJRRRBBB (no resonance, no mystling) 32K, Heynow 63K (Nov 6). Fill presets before deploying."},
]

mechanics = {
 "laneHp": "Anchor = the deployed player with the most Mythic artifact stars on a lane. Lane HP buff = 18% per Mythic star + 1.8% per Legendary star (anchor's stars only).",
 "atk": "Each player: +0.25% ATK per Mythic star, +0.025% per Legendary star.",
 "sacredGear": "Lane member with the most top-quality gear grants DMG reduction to the lane: +1.8% per Chaotic piece, +1.2% per Mythic piece (max 10.8%).",
 "talents": "+4% DMG per additional deployed member on the lane (full lane +28%); +4% DMG to all per additional player alive (death snowball).",
 "stats": "Battle HP fixed at 50,000 and ATK at 200 for everyone; power does not enter battle. Guild-tier ATK bonus starts at 36s; fights end well before.",
 "lock": "Deployments lock Fri 12:00 UTC; the opponent lineup is viewable for 2h after.",
 "ties": "Points (win 3, draw 1) → flags → total damage of deployed players.",
}

# The officer messages exactly as posted to Discord (Discord markdown), one file per round.
import os
BRIEF = {}
for n in (1, 2, 3):
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "briefs", f"2026-11-16-r{n}.md")
    BRIEF[("2026-11-16", n)] = open(f, encoding="utf-8").read().strip()
# Gear switches after the fact: earlier rounds on the old set are shown but not averaged (same rule as offSet above).
SWITCHED = {"Terminus323": "2026-11-22"}   # player -> date of first round on the new set
for ww in (w1, w2, w3):
    for r in ww["rounds"]:
        for ign, since in SWITCHED.items():
            if r.get("date", "") < since and any(x.get("ign") == ign for x in r.get("stats", [])):
                r.setdefault("offSet", [])
                if ign not in r["offSet"]: r["offSet"].append(ign)
for w in (w3,):
    for r in w["rounds"]:
        b = BRIEF.get((w["id"], r["n"]))
        if b: r["briefing"] = {"text": b, "by": "Daby (with Claude)", "at": r["date"]}


# ----- week of 2026-11-16 wrap-up (round key notes + week takeaways; written 2026-11-22 after R3, from the round data) -----
_w3_notes = {
 1: ["Left: Hago26 hit 251K/s and the lane finished 6.35M vs 2.73M with all 8 alive. Right: the MHARU stack closed it in 7s.",
     "Lost Middle to one player: swagginpanda did 5.43M (49% of their lane) and lasted the full 18s. We killed 5 of their 8 but couldn't break him.",
     "KatieCarmine's first Dragoon round: 92K/s, up from 3-26K/s on Oracle with the same character and artifacts. UkraineArchers' Griffin healers (500-800K each) stretched Left to 13s."],
 2: ["The plan worked as drawn: KiLess landed in Middle as predicted, so our planned concession soaked their best player (4.29M) while both all-Dragoon stacks won.",
     "Left was a blowout: 5.58M vs 0.89M in 7s, all 8 alive.",
     "Right decided the round: a 17s fight where about 3M of our healing kept 5 alive and Hago26 did 225K/s. Long fights lower everyone's per-second numbers, so compare DPS within a lane."],
 3: ["Holymoly fielded the same 24 in the same lanes for the third round in a row. We won all three lanes with all 24 alive (5.20M / 3.75M / 5.74M vs 1.90M / 0.67M / 2.87M).",
     "Terminus323's first Dragoon round: 118K/s, top of Middle, up from 11-18K/s on Oracle over 5 rounds. Second same-player switch after KatieCarmine, same result.",
     "Artifact test on Right (same 9s fight): higher ATK bonus did not come out ahead in 2 of 3 groups (Tuup 66K/s at 6.43% vs Zeuzo 117K/s at 4.23%). Heynow on a filled preset: 6K/s, no visible jump."]}
for _r in w3["rounds"]: _r["keyNotes"] = _w3_notes[_r["n"]]
w3["lessons"] = [
 "**Goal met:** 1st place, 3-0, 7 of 9 flags. Best week so far (Nov 2: 1-2, 3rd; Nov 9: 2-1, 2nd).",
 "**Reading lanes is our biggest edge.** Holymoly repeated the same 24 all three rounds, Happiness kept their R2 lanes in R3, and our R2 concession landed exactly on KiLess. Moonfall did the same thing last week. Check each opponent's last lineup before every round.",
 "**Both lanes we lost were Middle vs a single carry** (swagginpanda 5.43M in R1, KiLess 4.29M in R2). Against a guild with one 300K+/s player, conceding that lane on purpose (R2) beat fighting it (R1).",
 "**Dragoon is the upgrade that pays.** Two players switched gear while keeping the same character and artifacts: KatieCarmine 3-26K to 92K/s, Terminus323 11-18K to 118K/s. Moving our remaining Oracle players to Dragoon is the highest-value change we can make.",
 "**Artifacts still don't predict lane damage.** R3's same-fight test matches the Nov 9 tier tests. Don't build lanes around artifact stars.",
 "**Healing sets fight length.** UkraineArchers' Griffin healers and our own ~3M on R2 Right stretched fights to 13-18s. Survival wins long lanes; compare players' DPS within the same lane, not across lanes.",
 "**Hago26 carried every round** (top DPS in his lane all 3 rounds, 214K/s for the week). Pairing him with an all-Dragoon stack gave us the lane every time."]

out = {"_meta": {"purpose": "Starting data for the Expedition tab. Officers' edits are saved to the shared database (expedition/<week>) and replace a week's seed entry.",
                 "generated": "2026-11-21",
                 "sources": ["claude/archero2-expedition-log.md (week of 2026-11-02)", "claude/archero2-expedition-log-2026-11-09.md", "claude/archero2-expedition-log-2026-11-16.md",
                             "claude/archero2-expedition-2026-11-16-r1-postmortem.md", "claude/archero2-expedition-2026-11-16-r2-postmortem.md",
                             "claude/archero2-expedition-2026-11-16-happiness-scan.md", "claude/archero2-expedition-2026-11-16-holymoly-scan.md",
                             "Tracker sheet: Post-Mortem, Deployments, DPS History"],
                 "rules": ["DPS = damage / seconds survived (derived). Rounds listed in offSet (player on a different gear set) are shown but not averaged.",
                           "Lane damage totals are derived from the top player's damage / share where per-player totals weren't recorded.",
                           "Rounds with partialStats only recorded some players and no survival times; they don't count toward DPS averages.",
                           "Opponent characters are never recorded (only readable from our own preset screens)."]},
       "weeks": [w1, w2, w3], "opponents": opponents, "observations": observations, "findings": findings, "mechanics": mechanics}
json.dump(out, open(APP + "/expedition-seed.json", "w"), ensure_ascii=False, indent=1)

# self-checks: 8 per lane, no duplicates within a round, stats players were deployed in that lane
for w in out["weeks"]:
    for r in w["rounds"]:
        seen = []
        for ln in ("left", "middle", "right"):
            ps = r["our"][ln]["players"]; seen += ps
            assert len(ps) == 8, (w["id"], r["n"], ln, len(ps))
            assert r["our"][ln]["anchor"] in ps, (w["id"], r["n"], ln)
        assert len(set(seen)) == 24, (w["id"], r["n"], [x for x in seen if seen.count(x) > 1])
        for s in r.get("stats", []):
            assert s["ign"] in r["our"][s["lane"]]["players"], (w["id"], r["n"], s)
        if r.get("stats") and not r.get("partialStats"): assert len(r["stats"]) == 24, (w["id"], r["n"], len(r["stats"]))
print("ok", sum(len(w["rounds"]) for w in out["weeks"]), "rounds,", len(opponents), "opponents,", len(observations), "observations")

import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
APP = _os.path.join(HERE, "..", "app")
TOOLS = _os.path.join(HERE, "..", "tools")
import json, re
# ---- 2026-11-16 Expedition log snapshot (11-19) + R3 deployment powers (11-21) ----
# player, power(11-19), character, weapon set, quality, mythic, leg
LOG = """Hago26|14.12|Helix|Dragoon|C|22|30
SilverScope|10.84|Helix|Oracle|C|11|32
Yullong|10.28|Phynx|Oracle|C|8|34
Shoex|9.69|Phynx|Oracle|C|13|27
Heynow|9.20|Nyanja|Oracle|C|9|21
Venom17|8.86|Helix|Dragoon|C|11|27
Bungy|7.48|Helix|Dragoon|mixed|9|28
Gaga94|6.93|Nyanja|Oracle|mixed|12|33
Isterbuk|12.14|Nyanja|Oracle|C|15|34
MuffinKnight|12.05|Mymu|Oracle|C|12|29
MHARU|10.72|Helix|Dragoon|C|17|29
MsPoppycorn|10.62|Nyanja|Oracle|C|10|33
thesithlor|10.07|Alex|Oracle|C|8|24
Ilportoghese|10.01|Dracoola|Oracle|C|10|23
Terminus323|9.28|Phynx|Oracle|C|11|24
KatieCarmine|8.43|Hela|Dragoon|C|7|20
Tuup|11.65|Helix|Dragoon|C|22|37
Hansi218|10.59|Seraph|Dragoon|C|12|34
Zeuzo|10.31|Nyanja|Dragoon|C|14|29
daybee|10.22|Helix|Dragoon|C|15|28
皇黎|10.04|Nyanja|Oracle|C|15|33
Bubobubo|8.04|Nyanja|Dragoon|C|13|29
JJJRRRBBB|7.86|Helix|Oracle|C|7|16
Archerojj|7.53|Alex|Oracle|C|8|24
Michelo|7.86|Helix|Dragoon|C|11|23
TheDragonix725|7.86|Helix|Dragoon|C|13|21
DrShabz|7.66|Helix|Dragoon|C|8|19
LeKo|7.64|Helix|Oracle|C|13|31
Itsgeorgees|7.46|Hou Yi|Dragoon|C|10|20
DrFuko|7.34|Nyanja|Oracle|C|8|22
GoatGeass|7.18|Helix|Oracle|C|8|19
Buchacha|7.13|Dracoola|Dragoon|C|8|29
TylerG|7.10|Mymu|Dragoon|C|11|22
Prodegie|6.94|Seraph|Oracle|C|10|21
Bazal|6.69|Nyanja|Oracle|mixed|10|19
slenderu|6.59|Helix|Oracle|C|11|21
Abr0|6.59|Nyanja|Oracle|C|10|20
Tw3aKZ|6.43|Thor|Dragoon|C|12|21
KevinShock|6.32|Demon King Atreus|Dragoon|C|7|17
Banditten|6.04|Helix|Oracle|C|11|21
Legitkit|5.76|Alex|Oracle|C|4|17
Profetafume|5.68|Nyanja|Oracle|mixed|8|21
taz96|3.69|Dracoola|Dragoon|Mythic|11|26"""
R3 = dict(Hago26=14.45, MHARU=10.86, daybee=10.53, Venom17=8.95, KatieCarmine=8.27, TheDragonix725=8.06, Michelo=7.96,
          Itsgeorgees=7.46, Hansi218=10.69, Shoex=9.71, Heynow=9.20, LeKo=7.73, DrFuko=7.34, GoatGeass=7.18, slenderu=6.59,
          Abr0=6.59, Tuup=12.13, Zeuzo=10.37, Bubobubo=8.04, DrShabz=7.89, TylerG=7.22, Buchacha=7.13, Tw3aKZ=6.47, KevinShock=6.44)
# Resonances: only where the source preset screen is trusted (deployed character unchanged since the capture).
RES = {"Hago26": (["Otta","Thor"],"2026-11-06"), "SilverScope": (["Cleo","Demon King Atreus"],"2026-11-06"),
 "Shoex": (["Cleo","Thor"],"2026-11-06"), "Venom17": (["Cleo","Otta"],"2026-11-06"), "Gaga94": (["Demon King Atreus","Dracoola"],"2026-11-06"),
 "Isterbuk": (["Dracoola","Thor"],"2026-11-06"), "MuffinKnight": (["Cleo","Phynx"],"2026-11-06"), "MHARU": (["Otta","Mymu"],"2026-11-21"),
 "MsPoppycorn": (["Dracoola","Thor"],"2026-11-06"), "thesithlor": (["Thor","Wukong"],"2026-11-06"), "Ilportoghese": (["Artemis","Thor"],"2026-11-19"),
 "Terminus323": (["Rolla"],"2026-11-06"), "KatieCarmine": (["Otta","Demon King Atreus"],"2026-11-21"), "Tuup": (["Thor","Loki"],"2026-11-06"),
 "Hansi218": (["Demon King Atreus","Dracoola"],"2026-11-06"), "Zeuzo": (["Thor","Phynx"],"2026-11-06"), "daybee": (["Demeter","Thor"],"2026-11-06"),
 "皇黎": (["Thor","Cleo"],"2026-11-06"), "Bubobubo": (["Thor"],"2026-11-06"), "Michelo": (["Cleo","Otta"],"2026-11-06"),
 "TheDragonix725": (["Thor","Demon King Atreus"],"2026-11-06"), "DrShabz": (["Otta","Thor"],"2026-11-14"), "LeKo": (["Otta","Demon King Atreus"],"2026-11-06"),
 "Itsgeorgees": (["Thor"],"2026-11-19"), "DrFuko": (["Thor","Dracoola"],"2026-11-06"), "GoatGeass": (["Otta","Cleo"],"2026-11-06"),
 "Buchacha": (["Thor"],"2026-11-19"), "TylerG": (["Demon King Atreus","Thor"],"2026-11-06"), "Bazal": (["Dracoola","Thor"],"2026-11-06"),
 "slenderu": (["Cleo","Thor"],"2026-11-06"), "KevinShock": (["Dracoola"],"2026-11-19"), "Legitkit": (["Thor","Demon King Atreus"],"2026-11-19"),
 "Profetafume": (["Thor"],"2026-11-19"), "taz96": (["Loki"],"2026-11-19")}
# Mystling as written on preset captures (guild nicknames + star colors). Mapping per Daby 2026-11-21.
NICK = {"reaper": "Death Mage", "jester": "The Fool", "snake": "Queen Medusa", "goblin witch": "Witch", "dragon": "Nian Beast", "owl": "Snowy Owl"}
# Star colors in order (per Daby): yellow, teal, red, purple/pink/blue fade, dark red. Five icons per tier, so
# stars = 5 x (tier of the higher color) + icons in that color, when the five icons span two ADJACENT tiers.
# "blue" on old captures = teal (per Daby 2026-11-21).
TIER = {"yellow": 0, "teal": 1, "blue": 1, "red": 2, "purple": 3, "dark red": 4}
def stars_from(txt):
    if "0★" in txt: return 0
    parts = re.findall(r"(\d)\s+(dark red|yellow|teal|blue|red|purple)", txt)
    if not parts or sum(int(n) for n, _ in parts) != 5: return None
    tiers = sorted({TIER[c] for _, c in parts})
    if len(tiers) == 2 and tiers[1] - tiers[0] != 1: return None
    top = tiers[-1]
    k = sum(int(n) for n, c in parts if TIER[c] == top)
    return 5 * top + k
def myst_from(txt):
    name = next((v for k, v in NICK.items() if txt.lower().startswith(k)), None)
    return {"name": name, "stars": stars_from(txt)} if name else None
MYST = {"Hago26":"reaper, 3 purple / 2 red","Tuup":"jester, 2 yellow / 3 blue","MHARU":"reaper","daybee":"reaper, 4 yellow / 1 blue",
 "Isterbuk":"reaper","MuffinKnight":"reaper, 5 red","SilverScope":"snake","Zeuzo":"reaper, 4 yellow / 1 blue","Hansi218":"reaper, 5 red",
 "皇黎":"reaper","MsPoppycorn":"reaper, 5 red","thesithlor":"reaper","Ilportoghese":"goblin witch","Shoex":"snake","Venom17":"owl",
 "TheDragonix725":"reaper","Michelo":"reaper","LeKo":"dragon","KatieCarmine":"goblin witch (11-19)","DrShabz":"owl, 2 red / 3 yellow (11-14)",
 "Bazal":"jester, 0★","Tw3aKZ":"reaper, 5 blue","KevinShock":"reaper, 4 yellow / 1 blue","Legitkit":"jester, 0★","TylerG":"reaper, 0★",
 "taz96":"dragon, 2 blue","slenderu":"2 blue","GoatGeass":"2 blue","DrFuko":"1 yellow / 4 blue","Gaga94":"5 yellow"}
STATUS = {"Bungy":"Bare","JJJRRRBBB":"Bare","Archerojj":"Bare","Prodegie":"Bare","Banditten":"Bare","Abr0":"Partial",
 "Itsgeorgees":"Partial","Buchacha":"Partial","TylerG":"Partial","Bazal":"Partial","Tw3aKZ":"Partial","KevinShock":"Partial",
 "Legitkit":"Partial","Profetafume":"Partial","taz96":"Partial","Terminus323":"Partial","Gaga94":"Partial","Heynow":"Complete","KatieCarmine":"Complete"}
NOTES = {"Bungy":"Oracle pieces + Dragoon weapon (Mythic+2).",
 "Gaga94":"Expedition preset mixes all three sets (confirmed by Daby 2026-11-21): Godforge ★5 Oracle weapon, Mythic Dragoon armor, Chaotic Oracle ring, Mythic+3 Dragoon helmet, Mythic+2 Griffin amulet, Chaotic Dragoon boots. Main loadout 9.34M.",
 "Bazal":"Oracle, boots Mythic+4. Owns Cornucopia (0★).","Profetafume":"Oracle: armor Mythic+4, boots Mythic+2, weapon Mythic.",
 "taz96":"All Mythic Dragoon (weapon Mythic+3).","KatieCarmine":"Character is Hela (was misread as Loki). Switched Oracle → Dragoon week of 11-16.",
 "Heynow":"Filled both resonance slots + mystling week of 11-16 (which ones not recorded).","Yullong":"Deployed Loki on 11-06, Phynx by 11-19; resonances not re-captured.",
 "MuffinKnight":"Griffin amulet.","Hago26":"Best mystling in guild (11-06).","Shoex":"High-damage Oracle outlier."}
GEAR_SPECIAL = {
 "Bungy": {"weapon":{"set":"Dragoon","q":"Mythic+2"},"amulet":{"set":"Oracle","q":""},"ring":{"set":"Oracle","q":""},"helmet":{"set":"Oracle","q":""},"armor":{"set":"Oracle","q":""},"boots":{"set":"Oracle","q":""}},
 "Gaga94": {"weapon":{"set":"Oracle","q":"Godforge ★5"},"armor":{"set":"Dragoon","q":"Mythic"},"helmet":{"set":"Dragoon","q":"Mythic+3"},"amulet":{"set":"Griffin","q":"Mythic+2"},"ring":{"set":"Oracle","q":"Chaotic"},"boots":{"set":"Dragoon","q":"Chaotic"}},
 "Bazal": {"weapon":{"set":"Oracle","q":""},"boots":{"set":"","q":"Mythic+4"}},
 "Profetafume": {"weapon":{"set":"Oracle","q":"Mythic"},"armor":{"set":"","q":"Mythic+4"},"boots":{"set":"","q":"Mythic+2"}},
 "taz96": {"weapon":{"set":"Dragoon","q":"Mythic+3"}},
}
SLOTS = ["weapon","amulet","ring","helmet","armor","boots"]

def mid(ign):
    s = re.sub(r"[^a-z0-9]+", "-", ign.lower()).strip("-")
    return ("m-" + s) if s and s.isascii() and re.search(r"[a-z0-9]", ign.lower()) and all(ord(c) < 128 for c in ign) else "m-x" + ign.encode("utf-8").hex()

def gear_for(p, wset, q):
    if p in GEAR_SPECIAL: return GEAR_SPECIAL[p]
    if q == "C":
        g = {s: {"set": "", "q": "Chaotic"} for s in SLOTS}; g["weapon"] = {"set": wset, "q": "Chaotic"}
        if p == "MuffinKnight": g["amulet"] = {"set": "Griffin", "q": "Chaotic"}
        return g
    return {"weapon": {"set": wset, "q": ""}}

# ---- tracker sheet (Roster tab 11-06 ranks, DPS History) ----
sheet = json.load(open(TOOLS + "/sheet.json"))
rank = {r[0]: r[1] for r in sheet["roster"][1:]}
dps_head = sheet["dps"][0]
dps = {}
for r in sheet["dps"][1:]:
    hist = []
    for i, label in enumerate(dps_head[3:], start=3):
        v = r[i] if i < len(r) else ""
        if v == "": continue
        m = re.match(r"^(\d+)\s*(\((.+)\))?$", v.strip())
        hist.append({"match": label, "kps": int(m.group(1)), **({"note": m.group(3)} if m.group(3) else {})})
    dps[r[0]] = {"avg5": int(r[1]) if r[1] else None, "matches": int(r[2]) if len(r) > 2 and r[2] else 0, "history": hist}

def fill_from_weapon(gear):
    """Per Daby 2026-11-21: assume a complete set. Unknown set/quality on any slot = the weapon's.
    Returns the slots where anything was assumed."""
    w = gear.get("weapon") or {}
    assumed = []
    for s in SLOTS:
        g = dict(gear.get(s) or {"set": "", "q": ""})
        changed = False
        if not g.get("set") and w.get("set"): g["set"] = w["set"]; changed = True
        if not g.get("q") and w.get("q"): g["q"] = w["q"]; changed = True
        if changed or s not in gear: assumed.append(s) if (g.get("set") or g.get("q")) else None
        if g.get("set") or g.get("q"): gear[s] = g
    return [a for a in assumed if a != "weapon"]

members = []
for line in LOG.splitlines():
    p, pw, ch, ws, q, my, lg = line.split("|")
    power = R3.get(p); pdate = "2026-11-21" if power else "2026-11-19"; psrc = "Expedition deployment (R3 Team Info)" if power else "Expedition sub list / Team Info"
    if p == "KatieCarmine": psrc = "Preset recheck + R3 Team Info"
    power = power or float(pw)
    res, rdate = RES.get(p, ([], None))
    chars = [{"name": ch, "star": None}] + [{"name": n, "star": None} for n in res]
    while len(chars) < 3: chars.append(None)
    members.append({"id": mid(p), "ign": p, "rank": rank.get(p, "Member"), "status": "active",
      "power": {"m": power, "date": pdate, "src": psrc},
      "artifacts": {"mythic": int(my), "leg": int(lg), "date": "2026-11-19"},
      "preset": (lambda g: {"chars": chars, "gear": g, "_": fill_from_weapon(g), "runes": {"blessing": [], "enhancement": [], "ability": [], "etched": []},
                 "mystling": myst_from(MYST.get(p, "")), "behavior": {"range": "", "movement": ""}})(gear_for(p, ws, q)),
      "presetDate": "2026-11-19", "resonanceDate": rdate, "presetStatus": STATUS.get(p, "Complete"),
      "mystlingSeen": MYST.get(p, ""), "dps": dps.get(p, {"avg5": None, "matches": 0, "history": []}),
      "notes": NOTES.get(p, ""), "src": "Seeded from claude/archero2-expedition-log-2026-11-16.md + tracker sheet"})
# Lepimi: inactive, only 11-06 data
members.append({"id": "m-lepimi", "ign": "Lepimi", "rank": rank.get("Lepimi", "Member"), "status": "inactive",
  "power": {"m": 4.44, "date": "2026-11-06", "src": "Guild member list"}, "artifacts": {"mythic": 7, "leg": 17, "date": "2026-11-19"},
  "preset": {"chars": [{"name": "Thor", "star": None}, None, None], "gear": {s: {"set": "Dragoon", "q": ""} for s in SLOTS},
             "runes": {"blessing": [], "enhancement": [], "ability": [], "etched": []}, "mystling": None, "behavior": {"range": "", "movement": ""}},
  "presetDate": "2026-11-06", "resonanceDate": None, "presetStatus": "Bare", "mystlingSeen": "", "dps": {"avg5": None, "matches": 0, "history": []},
  "notes": "Inactive (not registering), per Daby.", "src": "Seeded from tracker sheet (11-06)"})
assert len({m["id"] for m in members}) == len(members)
out = {"_meta": {"purpose": "Starting roster for the Roster tab. Officers' edits are saved to the shared database and replace a member's seed entry.",
  "generated": "2026-11-21", "sources": ["claude/archero2-expedition-log-2026-11-16.md (snapshot 2026-11-19, R3 deployment 2026-11-21)", "Tracker Google Sheet: Roster tab (ranks, 11-06), DPS History tab"],
  "rules": ["Left the guild: Failwyn, Lodt (not included). Lepimi inactive.",
    "Gear: complete set (per Daby 2026-11-21): any slot with an unknown set or quality takes the weapon's, treated as known; officers correct it as accurate info comes in.",
    "Resonances only where the source preset screen is trusted; resonanceDate says when.",
    "Runes left blank (not reliably captured).", "Mystlings mapped from guild nicknames (reaper=Death Mage, jester=The Fool, snake=Queen Medusa, goblin witch=Witch, dragon=Nian Beast, owl=Snowy Owl). Stars from colors (yellow, teal, red, purple/pink/blue fade, dark red; 5 per color; 'blue' on old captures = teal) only when all five icons were recorded in adjacent colors. The raw capture stays in mystlingSeen."],
  "dpsMatches": dps_head[3:]},
  "members": sorted(members, key=lambda m: (m["status"] != "active", -m["power"]["m"]))}
for m_ in out["members"]: m_["preset"].pop("_", None)
# ---- later preset captures (newest screenshots win) ----
def _patch(ign, f):
    m = next(x for x in out["members"] if x["ign"] == ign); f(m)
def _terminus(m):   # preset screen 2026-11-22: switched Oracle -> Chaotic Dragoon
    m["preset"]["chars"] = [{"name": "Phynx", "star": None}, {"name": "Rolla", "star": None}, {"name": "Otta", "star": None}]
    for k in m["preset"]["gear"]: m["preset"]["gear"][k] = {"set": "Dragoon", "q": "Chaotic"}
    m["preset"]["behavior"] = {"range": "Mid", "movement": "Balanced"}
    m.update(presetDate="2026-11-22", resonanceDate="2026-11-22", presetStatus="Complete", mystlingSeen="naga, 1 rainbow + 4 red stars",
             notes="Switched Oracle to Chaotic Dragoon (preset screen 2026-11-22): all six pieces Chaotic Lv135-138, runes full. Oracle rounds stay in his history but aren't averaged with Dragoon rounds.")
_patch("Terminus323", _terminus)
json.dump(out, open(APP + "/roster-seed.json", "w"), ensure_ascii=False, indent=1)
print(len(members), "members")

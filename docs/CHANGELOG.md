# ArchAcademy Dashboard — Change Log

The authoritative, human-auditable record of every published version of the dashboard
artifact. If the live dashboard ever differs from the latest entry here, someone published
without logging it.

- **Artifact:** ArchAcademy Dashboard · slug `a699eb5d-8093-41f9-a74f-b4e8d5d70341`
- **Link:** https://claude.ai/artifact/MaDLSLGhDxJPiPJcWeJ4si
- **Release archive:** `dashboard/releases/<version>/` in this project (exact copies of every
  file published or changed in that release; the project's doc version for each file equals
  its sha256)
- **In-tool view:** the dashboard's Changes tab shows release notes (from `changelog.json`) and
  an activity log of shared-data changes.

> **Rename (2026-11-21, per Daby):** releases are numbered **v1, v2, v2.1…**, not r1, r2, r2.1.
> Archive folders moved from `releases/r*` to `releases/v*`; every moved file re-verified against
> its sha256. Files published before the rename still say "r1/r2/r2.1" inside (their
> `changelog.json` and the in-page badge). That text is part of what was published and is kept
> as-is so fingerprints stay valid. v1 = r1, v2 = r2, v2.1 = r2.1. From v2.2 on, files say "v".

---

## Version numbering (per Daby, 2026-11-21)

- **Major version** (v3, v4, …): new features, or other changes big enough to warrant it.
- **Sub-version** (v3.1, v3.2, …): bug fixes and minor adjustments to the current major version.
- **Patch** (added 2026-11-22 per Daby): releases that only change data files (round results, roster, opponent scans,
  notes in the seed), with no change to the page itself. Edits officers make inside the tool aren't releases and get no
  number; they're tracked in the activity log (see below). Earlier data-only releases (e.g. v6.3, v6.6) keep their numbers.
- **Format** (per Daby 2026-11-22): **major.minor.patch, each part starting at 0**. A new major is v7.0.0; a page fix after
  it is v7.1.0; a data-only release after that is v7.1.1. Releases before v6.8.0 used two numbers (v6.7 = v6.7.0).

## Release process (every publish follows this)

1. Before publishing: run the audit check below. If live ≠ last logged release, stop and log
   the unlogged change first.
2. Add the release to `changelog.json` (shown in the tool) with id, date, who asked, changes.
3. If the release needs a new permission/capability, declare it first, then publish the files.
4. Publish. Then record the new platform version id, each file's sha256 (from list_files), and
   the declared permission rules here.
5. Archive every file that was published or changed under `dashboard/releases/<version>/`.
   Files carried over unchanged aren't re-archived; the release entry says which earlier
   archive holds them. Confirm each archived file's project version (sha256) matches live.

## In-tool changes (activity log), per Daby 2026-11-22

Changes made inside the tool aren't releases, so they aren't entries here. They live in the activity log (version
number at the top right → Activity): who, when, how (typed in / screenshot import / Builds tab), and before → after,
with filters and CSV export. Officers' entries: `audit/<id>` (only that officer can write); past 400 the oldest 200 move
to `audit/<id>/months/<yyyy-mm>` (removed from the main doc only after the archive write succeeds). Members' entries:
`presets/<id>.log`, copied by any officer's open dashboard into that officer's `audit/<id>` (`mirrorOf`); later edits or
removals by the member are flagged in the log with the original shown. **At each sync, Claude adds one line per week
below ("Activity summaries") counting that week's in-tool changes and pointing to the log.**

### Activity summaries
- Week of Nov 16 (through 2026-11-22): no in-tool changes since 2026-11-22 03:02 UTC. Earlier entries: 6 by Daby
  (account link, 3 roster gear edits, 2 own-preset updates), all from v3.2–v3.3 testing.

## Audit check ("audit the dashboard")

Ask in any chat in this project. Claude will:
1. `list_files` on the artifact and compare each file's sha256 to the latest release below.
2. `read_declaration` and compare the permission rules to the latest release below.
3. Report: match, or exactly which files/rules differ. A difference means an unlogged publish
   (by any Editor, the owner included). The platform does not record WHO published a version,
   so the check proves *that* something changed, not *who* changed it.

## Rollback ("roll back the dashboard to vN")

Claude republishes vN's full file set (from its archive folder, plus any carried-over files
from the earlier archive its entry names) in mode: replace, so files added later are removed;
restores vN's permission rules; then logs the rollback as a NEW sub-version (e.g.
"v3.2 = rollback to v3") so history is never rewritten.

Notes: rollback restores the page, its data files and its rules, not the shared data (leaderboard
results, saved accounts, roster edits, activity log). Older releases read newer saved data best-effort:
- v1 ignores rune qualities saved by v2+.
- v2.1 and earlier read a v2.2+ saved account's characters, gear and runes, but show **no
  mystlings** (v2.2 stores them with stars, which v2.1 doesn't understand) and ignore labeled
  builds and IGN. Nothing is deleted; it all reappears after rolling forward again.
- v2.2 doesn't know the names Sprite Multishot / Sprite Link, so runes saved under them by v2.3+
  are dropped from its view.
- v2.x has no Roster tab: officers' roster edits (`roster/<id>`) stay in the database untouched and
  reappear after rolling forward to v3+.
- v3.x has no Expedition tab: `expedition/` and `opponents/` docs stay in the database and reappear on v4+;
  the roster's DPS Avg falls back to the seeded tracker values.
- v3.2 and earlier ignore players' presets in `presets/<id>` and show the old blank gear slots.
- v3.0 and earlier drop inventory entries saved with unknown stars (★?, added by v3.1's linking)
  from their view, and ignore `linkedMemberId` (members' private links).

## Known limits of this audit trail

- Editors (officers) can publish new page versions and change rules. The activity log's
  protections are page rules, so an Editor could loosen them. The audit check catches rule
  changes, but only after the fact. Keep the Editor list to trusted people.
- In the activity log, each officer can write only their own entries (rule `audit` write:self,
  `audit/{self}` write:admin). An officer can delete their own entries, not anyone else's.
- Roster edits are recorded in the activity log by the page itself. An Editor writing to the
  database by other means wouldn't be logged; the roster doc's `updatedBy` still records who saved it last.
- "One roster profile per account" is enforced by the page, not by database rules. Members' links
  are private to them, so two members claiming the same IGN wouldn't see each other's claim.
- Each archived release is up to ~250 KB of project knowledge (2 MB cap). Prune old releases'
  archives once there are 8+, keeping this log's entries.
- **Retention rule (per Daby, 2026-11-22): keep the archives of the last 5 releases only.** After each publish, the
  oldest archive folder is deleted; its entry and fingerprints stay in this log. Before deleting, any unchanged file a
  kept release still needs is copied into the oldest kept folder, so every kept release can be fully rolled back.
- **Pruned 2026-11-22:** v1–v4 (32 docs, to make room), then v5, v5.1, v6, v6.1, v6.2 (17 docs) under the 5-release
  rule. Kept then: v6.3–v6.7. v6.2's index.html (sha256 `c813f9b0…`) and roster-seed.json (`9e63aecd…`, last archived in
  v6.1) were copied into `v6.3/` first; build-data.json (`6fd7eeda…`) is in `v6.6/`. Where entries say a file is
  "archived in" a deleted folder, use the copy named here.
- **Pruned 2026-11-22 (v6.8.0 publish):** v6.3 (4 docs). roster-seed.json (`9e63aecd…`) copied into `v6.4/` first; v6.3's
  own index.html (`c813f9b0…`) is gone with it. Kept then: v6.4–v6.8.0.
- **Pruned 2026-11-22 (v7.3.0 publish):** v6.8.0 (2 docs). `v6.7/` still holds the carried data files v6.9.0 needs.
  Kept: v6.9.0–v7.3.0. Earliest rollback target: v6.9.0. From v8.0.0 on, releases are kept in the GitHub repo
  `daybee112/archero2-dashboard` (tags), not in this project.
- **Pruned 2026-11-22 (v7.2.0 publish):** v6.7's own index.html and changelog.json (2 docs). The `v6.7/` folder now holds
  only carried files that kept releases need: expedition-seed.json (`71c83975…`, used by v6.8.0 and v6.9.0),
  roster-seed.json (`9e63aecd…`) and build-data.json (`6fd7eeda…`). Kept: v6.8.0–v7.2.0. Earliest rollback target: v6.8.0.
- **Pruned 2026-11-22 (v7.1.0 publish):** v6.6 (4 docs). roster-seed.json (`9e63aecd…`) and build-data.json (`6fd7eeda…`)
  copied into `v6.7/` first. Kept: v6.7–v7.1.0. Earliest rollback target now: v6.7.
- **Pruned 2026-11-22 (v7.0.0 publish):** v6.5 (4 docs). roster-seed.json (`9e63aecd…`) copied into `v6.6/` first;
  v6.5's expedition-seed.json was superseded and not needed. Kept: v6.6–v7.0.0. Earliest rollback target now: v6.6.
- **Pruned 2026-11-22 (v6.9.0 publish):** v6.4 (4 docs). roster-seed.json (`9e63aecd…`) copied into `v6.5/` first.
  Kept: v6.5–v6.9.0. Earliest rollback target now: v6.5.

---

## Releases (newest first)

### v7.3.0 — 2026-11-22 — live
- **Type:** minor (page fixes)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v7.2.0 files exactly, platform version `1795389525-60c2`)
- **Headless test before publish:** Expedition UX suite 27/27 (incl. multi-week guild shows only the selected week; Show
  all guilds shows every week; phone roster floating heading pinned left and under the top bar); expedition 26/26; shared
  inventories 20/20; activity 19/19; weekly results 16/16; lanes 14/14; image/notes 11/11; message 9/9; results 11/11;
  Help 14/14; full regression 66/67 (favicon/font unreachable in sandbox).
- **Platform version:** `1795391812-44ce`
- **Files:**
  - `index.html` · 338,655 bytes · sha256 `3b09840cd2414dc53c9db41dc079b9685cbff4fd71c89e84f1fc9f13d8c62201` (changed)
  - `changelog.json` · 27,102 bytes · sha256 `4522bd2ef5ca3c14215a09ac5f9adc50d3278fdbd407a07c9f5878dc51515dec` (changed)
  - `expedition-seed.json` · sha256 `009ef9b9…` (unchanged, `v7.1.0/`) · `roster-seed.json` · sha256 `9e63aecd…`
    (unchanged, `v6.7/`) · `build-data.json` · sha256 `6fd7eeda…` (unchanged, `v6.7/`)
- **Permission rules:** unchanged from v7.0.0.
- **Changes:**
  - Main Roster: the real heading row is no longer moved (its Player cell is sticky-left again). `buildRosterFloat()`
    makes a separate fixed copy (`#roster-float`: cloned thead + a corner copy of the Player cell), shown by
    `syncRosterFloat()` once the headings scroll under the top bar; widths and padding copied from the real cells,
    side-scroll synced with translateX; clicks forwarded to the real heading buttons. Rebuilt on every header render.
  - Opponents: `weekOnly` (selected week, Show all off) limits the summary week label, "Week of …:" lane habits, lane
    history, player results and the roster scan (scan dated within the week) to the selected week; Show all lists every
    week and the latest scan.
- **Archive:** `dashboard/releases/v7.3.0/` (index.html, changelog.json; sha256 verified) + expedition-seed.json from
  `v7.1.0/`, roster-seed.json and build-data.json from `v6.7/`

### v7.2.0 — 2026-11-22
- **Type:** minor (page improvements and fixes)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v7.1.0 files exactly, platform version `1795385946-d5f0`)
- **Headless test before publish:** Expedition UX suite 25/25 (columns, DPS avg tooltip, perf-dot tooltip, header sort +
  chips + reset, phone: opponent details stay in the screen, roster Player heading pinned left and under the top bar);
  expedition 26/26 (6-round roster DPS; 3-opponent cap: 0 of 3 → form closes at 3; existing guild attached to the week
  without duplicating); shared inventories 20/20; activity 19/19; weekly results 16/16; lanes 14/14; image/notes 11/11;
  message 9/9; results 11/11; Help 14/14; full regression 66/67 (favicon/font unreachable in sandbox). Phone widths checked
  in Chrome at 390px; iPhone Safari not available in the sandbox (Daby to confirm the roster heading fix on device).
- **Platform version:** `1795389525-60c2`
- **Files:**
  - `index.html` · 334,356 bytes · sha256 `90de00dfbd058fd9a9f0e18ae37b94d71c77bdb4452c3a0c95c1f9bf42777a56` (changed)
  - `changelog.json` · 26,476 bytes · sha256 `4072694d1dbe794c73cea00524a70a6f8853ef4e7777cf87cf0d9d1dad0851a7` (changed)
  - `expedition-seed.json` · sha256 `009ef9b9…` (unchanged, `v7.1.0/`) · `roster-seed.json` · sha256 `9e63aecd…`
    (unchanged, `v6.7/`) · `build-data.json` · sha256 `6fd7eeda…` (unchanged, `v6.7/`)
- **Permission rules:** unchanged from v7.0.0.
- **Changes:**
  - `dpsAvg5` now averages the last 6 counted rounds (current gear, full stats); help and labels updated; main Roster uses it.
  - Expedition roster (`PCOLS`, `pSortStack`): Player, Gear, DPS avg, Best DPS, Performance, Notable; vs lane, Alive at end,
    Rounds and the trend sparkline removed (vs lane stays on player pages). Header sorting like the main Roster with sort
    chips and "Reset to DPS avg"; Notable sorts by signed weight; Performance not sortable. DPS avg tooltip "Based on last X
    played rounds". `perfChart()`: last 6 played rounds per player, own scale, right-aligned, hollow dots for other gear set
    or partial rounds, `.perftip` tooltip "Week of … · Round N: X K/s", latest value after the line.
  - Opponents: officers' add form attaches the guild to the week on screen ("New opponent guild name", "Add to this week",
    "x of 3 added"); closes with a note at 3. Fixed: seed opponents have no `name`, so "Edit this opponent" (and adding)
    saved to a nameless doc; `name` is now filled in.
  - Phones: header cells shift individually instead of the whole thead (iPhone Safari dropped the sticky Player heading
    inside a transformed row); the roster's Player heading follows the side-scroll in code (`translate(scrollLeft, shift)`),
    scroll listener in capture mode. `.stack > *` and opponent card bodies get `min-width: 0` so wide tables scroll inside
    their wrapper instead of widening the page. Round cards 178px under 560px; countdown chip "Locks 12h 46m"; lane-dot
    labels don't wrap.
- **Archive:** `dashboard/releases/v7.2.0/` (index.html, changelog.json; sha256 verified) + expedition-seed.json from
  `v7.1.0/`, roster-seed.json and build-data.json from `v6.7/`

### v7.1.0 — 2026-11-22
- **Type:** minor (page fixes plus round-note data)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v7.0.0 files exactly, platform version `1795384098-1448`)
- **Headless test before publish:** Expedition UX suite 20/20 (incl. show/hide all guilds, notes as bullets in the
  results card, R1/R3 test-result notes, pinned Builds bar); expedition 23/23; shared inventories 20/20; activity 19/19;
  weekly results 16/16; lanes 14/14; image/notes 11/11; message 9/9; results 11/11; Help 14/14; full regression 66/67
  (favicon/font unreachable in sandbox).
- **Platform version:** `1795385946-d5f0`
- **Files:**
  - `index.html` · 328,216 bytes · sha256 `256af5dbcb9d3fedbb32be2f3e3ec44d5b54c194eaf93d82f2c77928fccedaf0` (changed)
  - `changelog.json` · 25,257 bytes · sha256 `b37ba9f547796bd6450b2c161e6976301c9103785d496edaf9223aec72117400` (changed)
  - `expedition-seed.json` · 199,809 bytes · sha256 `009ef9b925f67cdda83ca2475ff1e3c9944df3f70970dec1a800b3379f77a781`
    (changed: Nov 16 R1–R3 notes with test results)
  - `roster-seed.json` · sha256 `9e63aecd…` (unchanged, `v6.7/`) · `build-data.json` · sha256 `6fd7eeda…` (unchanged,
    `v6.7/`)
- **Permission rules:** unchanged from v7.0.0.
- **Changes:**
  - `noteLines()` shared by round notes, Round details, Week results and the Round results card; the card's markdown
    (and Copy text) now has a "📝 **Notes**" heading with "- " bullets and bold "Label:" prefixes.
  - Week of Nov 16 notes (make_expedition.py): R1 healing + 5 test results (KatieCarmine gear switch, bench Dragoon,
    weak-anchor stack, MHARU Helix, artifacts deferred to R3); R2 plan, healing, lesson, "no tests"; R3 Lineup/Change/
    Power/Prediction/Result + results for all 8 tests (from `claude/archero2-expedition-2026-11-16-r3-results.md` and the
    R3 officer message), inconclusive ones marked as such.
  - Opponents: v7.0.0's search, faced/seen filter and highlighting removed. Header "<week> opponents" + `#opp-all`
    toggle ("Show all guilds (N)" / "Hide other weeks"); earlier guilds listed below this week's under "Other weeks".
    This week's guild cards show that week's lane history and player results; other guilds show all weeks. Opening an
    off-week guild by link turns the toggle on.
  - Builds: `.buildsbar` (heading, New custom build, Save, build picker, build meta) pinned under the top bar.
- **Archive:** `dashboard/releases/v7.1.0/` (index.html, changelog.json, expedition-seed.json; sha256 verified) +
  roster-seed.json and build-data.json from `v6.7/`

### v7.0.0 — 2026-11-22
- **Type:** major (new features: shared inventories, roster indicators, Opponents search and player results)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v6.9.0 files and rules exactly, platform version `1795373623-5e55`;
  `expedition/` empty, so the seed drives every week)
- **Headless test before publish:** shared inventories 20/20; new Expedition UX suite 17/17 (default round, no goal,
  Roster order, no Rounds column, "245 K/s" no-wrap, one-line headers, pinned round bar and table headers, Opponents
  week scope / search / filters, lane history stats, notes bullets); expedition 23/23; activity 19/19; weekly results
  16/16; lanes 14/14; image/notes 11/11; message 9/9; results 11/11; Help 14/14; full regression 66/67 (favicon/font
  unreachable in sandbox). Round cards checked at desktop and 390px phone width in played, in-progress and upcoming
  states.
- **Platform version:** `1795384098-1448`
- **Files:**
  - `index.html` · 329,432 bytes · sha256 `ed886c5762737aa4050f2385bb352b50d17a6e56bc0fe47f3eeb4c6165755047` (changed)
  - `changelog.json` · 24,441 bytes · sha256 `84cb490d17e61ee58fd3308d4fa4cc3a6250a325d23a98d3391f34319fcc17ed` (changed)
  - `expedition-seed.json` · 197,788 bytes · sha256 `1e49be0cd47c017a2a852f1cb48a9179c862d2691e9499f582ebd6490906f59a`
    (changed: Nov 16 R3 note split into labeled lines)
  - `roster-seed.json` · sha256 `9e63aecd…` (unchanged, `v6.6/`) · `build-data.json` · sha256 `6fd7eeda…` (unchanged,
    `v6.6/`)
- **Permission rules:** unchanged. The planned `inventory/{self}` rule was refused by the platform (this artifact holds
  writing from outside the org, so its declaration can't be changed from here). Workaround: a player's own shared
  inventory lives on `presets/<user id>.shared` (already self-writable); officers' edits for a player go to
  `inventory/<member id>` (`byOfficer: true`, admin write under the root rule). `invSubs` merges both.
- **Changes:**
  - Shared inventories: everyone can view; players edit their own (saving also updates `presets/<id>.shared`); officers
    edit anyone's from the roster ("Save to <IGN>", logged before → after). Officer edits are pulled into the player's
    own inventory on their next visit with a note. Existing private inventories are shared on the player's next visit,
    with a one-time notice. Builds stay private except the Expedition preset.
  - Roster: Account linked (incl. members' own links via `presets/<id>.memberId`) and Inventory columns ("✓ Filled"
    opens the read-only view; officers see "Empty · add").
  - Expedition rounds: fixed-size round cards (220px; round, date, opponent, L/M/R lane dots, status chip with a lock
    countdown) replace the R1/R2/R3 pills; pinned under the top bar (`.stickybar`); open on the first unplayed round,
    or the last round once the week is over (also on week change). Phones scroll the row to the open round.
  - Round notes render as bullets (`notesList`: one per line, else per sentence; "Label:" lines get a bold label).
  - Week header: goal line removed.
  - Players sub-view renamed Roster and moved before Opponents. Rounds column removed; DPS average tooltip gives the
    round count, grey under 3 rounds.
  - `fmtRate()`: DPS reads "92 K/s" everywhere; `td.num` never wraps.
  - Opponents: selected week by default (`#opp-scope`), All weeks option, faced / seen filter (`#opp-kind`), guild or
    player search (`#opp-q`, tags and opens matches, highlights the player). Lane history lists each player's DPS ·
    seconds survived (✓ alive at the end; fight length from lane results or the longest survivor of both sides), plus a
    Player results table (lanes by round, avg / best DPS, avg survived, alive at end, total damage).
  - All tables: headers stay under the top bar (and the round bar) while scrolling, via the generalized
    `syncRosterHead` transform; `th` never wraps.
- **Archive:** `dashboard/releases/v7.0.0/` (index.html, changelog.json, expedition-seed.json; sha256 verified) +
  roster-seed.json and build-data.json from `v6.6/`

### v6.9.0 — 2026-11-22
- **Type:** minor (page fix: player notes)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v6.8.0 files and rules exactly, platform version `1795371680-98e2`; no new
  activity since v6.8.0)
- **Headless test before publish:** activity 19/19; weekly results 16/16; expedition 21/21; lanes 14/14; image/notes
  11/11; message 9/9; results 11/11; Help 14/14; full regression 66/67 (favicon/font unreachable in sandbox). Player
  pages for Terminus323, Hago26 and KatieCarmine checked by hand.
- **Platform version:** `1795373623-5e55`
- **Files:**
  - `index.html` · 304,364 bytes · sha256 `445dad5ddc206d98010ed1eda03b364a04c94e559e4527cca8dc7d934d171ede` (changed)
  - `changelog.json` · 23,908 bytes · sha256 `4139ff6cc41b46af7a15bb10726a11f2bb3e0047d15eac4b02a597a41943bd42` (changed)
  - `expedition-seed.json` · sha256 `71c83975…` (unchanged, `v6.7/`) · `roster-seed.json` · sha256 `9e63aecd…` (unchanged,
    `v6.5/`) · `build-data.json` · sha256 `6fd7eeda…` (unchanged, `v6.6/`)
- **Permission rules:** unchanged from v6.8.0.
- **Changes (reported by Daby on Terminus323's page):** "new: 1 round" contradicted the 8 rounds listed (7 Oracle rounds
  are shown but not counted) and "Consistently out-damages lanemates" rested on his single Dragoon round (4.89× lane
  median; 0.27–0.70× on Oracle). Now: "1 round on current gear" with the count of uncounted earlier rounds;
  "consistently"/"usually" notes need 3+ counted rounds and state median + count; 1–2 rounds → "too early to call it
  a pattern"; players who switched gear get their lane-relative median on the earlier set; the duplicate ⚑ lane line
  is skipped under 3 counted rounds.
- **Archive:** `dashboard/releases/v6.9.0/` (index.html, changelog.json; sha256 verified) + expedition-seed.json from
  `v6.7/`, roster-seed.json from `v6.5/`, build-data.json from `v6.6/`

### v6.8.0 — 2026-11-22
- **Type:** minor (page changes; first release under the three-part numbering, each part starting at 0)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v6.7 files and rules exactly, platform version `1795369347-28f5`; no
  `expedition/`, `notes/` or `presets/` docs; `audit/` holds Daby's 6 entries from v3.2–v3.3, which display fine)
- **Headless test before publish:** activity suite 19/19 (officer before→after + how; 400-entry monthly archive;
  filters, search, CSV; member log in `presets/<id>`; officer copy + tamper flags for edited/removed entries; no
  double copies); weekly results 16/16 (incl. tab order, version badge opens the changelog, `#changes` still works);
  expedition 21/21; lanes 14/14; image/notes 11/11; message 9/9; results 11/11; Help 14/14; full regression 66/67
  (favicon/font unreachable in sandbox). Test mock gained `get()` on collections and `__fire()`.
- **Platform version:** `1795371680-98e2`
- **Files:**
  - `index.html` · 303,043 bytes · sha256 `e03ca708ef81f757e21177ff4e210ba0e73b65bedb5f7613f245c1b1043ecbc5` (changed)
  - `changelog.json` · 23,053 bytes · sha256 `59833465c88f8dbb743b2698a2bc9e12642df2d352299cadf2285fee1602230f` (changed)
  - `expedition-seed.json` · sha256 `71c83975…` (unchanged, `v6.7/`) · `roster-seed.json` · sha256 `9e63aecd…` (unchanged,
    `v6.4/`) · `build-data.json` · sha256 `6fd7eeda…` (unchanged, `v6.6/`)
- **Permission rules:** unchanged from v6.7. Untested against the live database: whether `audit/{self}` covers
  `audit/<id>/months/...`. If not, archiving fails safe (entries stay in the main doc).
- **Changes:**
  - Tabs: Inventory, Builds, Roster, Expedition, Training Ground, Help. Changelog tab removed; the version badge (gold,
    `.vbtn`) opens it (`#changes` still routes there). Help text and both Claude Docs guides updated.
  - Expedition: Week results moved to its own sub-view (`#exp-results`, data-sub `results`).
  - Activity log: `logEvent(action, detail, {changes, src})` with `diffObj` before→after (empty lists/objects ignored;
    `updatedAt/updatedBy/v/presetUpdatedAt` skipped) on saveMember, saveWeek, saveOpponent, notes; `src` typed /
    screenshot / builds. Monthly archive past 400. Members' changes (preset push, Training Ground posts/deletes) →
    `presets/<id>.log` (≤300); preset push keeps the existing log. Officers' pages copy new member entries into their
    own `audit/<id>` (`mirrorOf`); the view shows the copy and flags later edits/removals. Training Ground posts from
    `tg-results` (newest 300) shown too. Filters (who, type), search (incl. changes), Load older entries, CSV export.
  - Versions panel text: only the last 5 releases are archived.
- **Archive:** `dashboard/releases/v6.8.0/` (index.html, changelog.json; sha256 verified) + expedition-seed.json from
  `v6.7/`, roster-seed.json from `v6.5/`, build-data.json from `v6.6/`

### v6.7 — 2026-11-22
- **Type:** sub-version (improvement to the Expedition tab)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v6.6 files and rules exactly, platform version `1795363298-647e`; no
  `expedition/` or `notes/` overrides)
- **Headless test before publish:** new weekly-results suite 11/11 (empty before R1, mid-week with R3 hidden, final;
  week note saved to `notes/<week>-week`; copy as image); expedition 21/21; lanes 14/14; image/notes 11/11;
  message 9/9; results 11/11; Help 14/14; full regression 66/67 (favicon/font unreachable in sandbox). Older tests
  re-scoped to the round notes / round panel where the new card's notes and layout overlapped.
- **Platform version:** `1795369347-28f5`
- **Files:**
  - `index.html` · 289,369 bytes · sha256 `30b7833c3e35cc56bcf0e4884bcaeb72d3becdfc9e1706399f8c92ebb733bc96` (changed)
  - `expedition-seed.json` · 197,747 bytes · sha256 `71c83975b250fc400502e1b107f00722b8a33803723556911772d0ee403ac237` (changed)
  - `changelog.json` · 21,831 bytes · sha256 `0e33ee4fdd0d19cb6901e056c90c9f2ded0046929230169929b90ba2507c7345` (changed)
  - `roster-seed.json` · sha256 `9e63aecd…` (unchanged, `v6.1/`) · `build-data.json` · sha256 `6fd7eeda…` (unchanged, `v6.6/`)
- **Permission rules:** unchanged from v6.6 (week notes at `notes/<week>-week` are covered by the root rule).
- **Changes:**
  - Rounds view: weekly results card above the round tabs (`weekResults`, `weekResultsMd`, `weekResultsCard`).
    Empty before R1; then record, flags of N, points, damage, place, standings so far (our rounds + logged
    observations; 3 pts a win; lists matches not yet logged), each round as a block (result, lanes won + damage,
    up to 3 `keyNotes`, falling back to `notes`), top 3 DPS for the week (2+ counted rounds). Final (w.final and all
    rounds played): game standings and damage total, plus `lessons` as "What we learned this week". Copy text /
    Copy as image. Week notes (officers) at `notes/<week>-week`.
  - Week header: standings chips removed (now in the card).
  - Data: week of Nov 16 `keyNotes` (3 per round) and `lessons` (7 conclusions), written 2026-11-22 after R3.
  - `changelog.json` numbering note updated with the patch rule.
- **Archive:** `dashboard/releases/v6.7/` (index.html, expedition-seed.json, changelog.json; sha256 verified) +
  roster-seed.json from `v6.5/`, build-data.json from `v6.6/`

### v6.6 — 2026-11-22
- **Type:** sub-version (data backfill)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v6.5 files and rules exactly, platform version `1795360870-950f`; no
  `expedition/`, `opponents/` or `notes/` overrides)
- **Headless test before publish:** results 11/11; expedition 21/21; lanes 14/14; image/notes 11/11; message 9/9;
  Help 14/14; full regression 66/67 (favicon/font unreachable in sandbox). Test bounds raised: notable badges ≤12
  (was 6/8) because Nov 2 R2/R3 now count toward DPS; player-detail check no longer pins a specific week.
- **Platform version:** `1795363298-647e`
- **Files:**
  - `expedition-seed.json` · 194,839 bytes · sha256 `20d38fda3bc28de9923ac247a00e707d7da460566db74594efe90e90a22ed595` (changed)
  - `changelog.json` · 20,862 bytes · sha256 `e7efe62a52e09a46925f0721312e061931c6067ca3c5cd79b7a8378e54e76594` (changed)
  - `index.html` · sha256 `7998be8ca9ebc044db6e995792e9b0bcd9886db89b39acb0678df2f4012ff450` (unchanged, archived in `dashboard/releases/v6.5/`)
  - `roster-seed.json` · sha256 `9e63aecd…` (unchanged, `v6.1/`) · `build-data.json` · sha256 `6fd7eeda…` (unchanged, `v3.1/`)
- **Permission rules:** unchanged from v6.5.
- **Changes:** Nov 9 week R1–R3 and Nov 2 week R1 (partial), R2, R3 backfilled from Details screens (Daby,
  2026-11-22): our damage/survival/healing, opponent damage/survival/DPS, full opponent lineups. Observations added
  or completed: おぶんぐさん/Moonfall/Whispers all 3 rounds; BlockMagic vs PWNZ R2; Happiness vs PWNZ R3 (both sides).
  Nov 2 R2/R3 no longer `partialStats`. Lane totals matched to screens (≤0.05M changes).
- **Archive:** `dashboard/releases/v6.6/` (expedition-seed.json, changelog.json, and build-data.json re-archived
  here after v3.1's folder was pruned; all sha256 verified) + index.html from `v6.5/`, roster-seed.json from `v6.1/`.
  (First attempt to archive the seed was refused because the project was full; it went in after the pruning below.)

### v6.5 — 2026-11-22
- **Type:** sub-version (minor adjustment + data backfill)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v6.4 files and rules exactly, platform version `1795359716-9203`; no
  `expedition/` or `opponents/` overrides)
- **Headless test before publish:** results 11/11; expedition 21/21; lanes 14/14; image/notes 11/11; message 9/9;
  Help 14/14; full regression 66/67 (the one "fail" is the favicon and Google font being unreachable from the test
  sandbox). Backfilled opponent DPS (damage ÷ survival) matched every previously logged DPS value.
- **Platform version:** `1795360870-950f`
- **Files:**
  - `index.html` · 282,212 bytes · sha256 `7998be8ca9ebc044db6e995792e9b0bcd9886db89b39acb0678df2f4012ff450` (changed)
  - `expedition-seed.json` · 141,612 bytes · sha256 `fa4ced6373fdf8c070ae7dcd19d2c9456b68d24732afdecdce6a112b2e9e7ffd` (changed)
  - `changelog.json` · 19,770 bytes · sha256 `2f8d57acce03e24913cc4b8f6d0ab92f5793d444bec839ea91a38d65b25550c8` (changed)
  - `roster-seed.json` · sha256 `9e63aecd9280931fccc37123ac0fb0f0bcea01c0d6280220f14721494554c77a` (unchanged, archived in `dashboard/releases/v6.1/`)
  - `build-data.json` · sha256 `6fd7eeda6ff9c542bad0a6123c3a601f8f4ac6f8224b751b2786a9eeabb6722c` (unchanged, archived in `dashboard/releases/v3.1/`)
- **Permission rules:** unchanged from v6.4.
- **Changes:**
  - Lane cards: opponent rows show damage · survival · DPS when logged (same as ours).
  - Week of Nov 16 backfill from Details screens (Daby, 2026-11-22): R1 and R2 opponent damage + survival for all
    players (new `oppfull` helper in make_expedition.py derives DPS); our R1 healing and exact damage; lane totals
    adjusted ≤0.01M to match. Observations: Happiness vs Holymoly R1 full stats; UkraineArchers vs Holymoly R2 full
    stats and full Middle/Right lineups; Holymoly R2 full stats.
  - Results confirmed from schedule screens: R1 AA 2–1 UA (won L, R), Happiness 3–0 Holymoly; R2 AA 2–1 Happiness
    (won L, R), UA 3–0 Holymoly.
- **Archive:** `dashboard/releases/v6.5/` (index.html, expedition-seed.json, changelog.json; sha256 verified) +
  roster-seed.json from `v6.1/`, build-data.json from `v3.1/`

### v6.4 — 2026-11-22
- **Type:** sub-version (minor adjustment + data)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v6.3 files and rules exactly, platform version `1795358172-dc6e`; no
  `expedition/` override)
- **Headless test before publish:** results suite 10/10; expedition 21/21; lanes 14/14; image/notes 11/11;
  message 9/9 (now tested on an unplayed round); Help 14/14; full regression 66/67 (the one "fail" is the favicon and
  Google font being unreachable from the test sandbox).
- **Platform version:** `1795359716-9203`
- **Files:**
  - `index.html` · 282,045 bytes · sha256 `772d5b46700229daf039d2aad6346b6d11bbc22b7100deffc573d17379cea58d` (changed)
  - `expedition-seed.json` · 133,952 bytes · sha256 `25dcd32478011a5d488666891b8b8c0894cc82a70958628009b4d9d05c151a87` (changed)
  - `changelog.json` · 18,777 bytes · sha256 `ea000349e575d3e1928b2cb83679f10961cd3b8682e2996d30586b63beb0e81f` (changed)
  - `roster-seed.json` · sha256 `9e63aecd9280931fccc37123ac0fb0f0bcea01c0d6280220f14721494554c77a` (unchanged, archived in `dashboard/releases/v6.1/`)
  - `build-data.json` · sha256 `6fd7eeda6ff9c542bad0a6123c3a601f8f4ac6f8224b751b2786a9eeabb6722c` (unchanged, archived in `dashboard/releases/v3.1/`)
- **Permission rules:** unchanged from v6.3.
- **Changes:**
  - Played rounds: "Round results" card (Discord markdown built from the round data: score, each lane L/M/R with anchor
    + lane HP, result, damage both sides, fight length, alive count, every player's gear + DPS sorted) with Copy text
    and Copy as image. Replaces the message to the officers on played rounds; the pre-round message stays folded
    under it.
  - Happiness 2–1 UkraineArchers (R3) confirmed from the round schedule screen; final standings confirmed.
  - Terminus323 R3 power 9.24M (main profile, per Daby; deployment screen not captured).
- **Archive:** `dashboard/releases/v6.4/` (index.html, expedition-seed.json, changelog.json; sha256 verified) +
  roster-seed.json from `v6.1/`, build-data.json from `v3.1/`

### v6.3 — 2026-11-22
- **Type:** sub-version (data sync: R3 results)
- **Requested by:** Daby ("go ahead and sync it with the dashboard") · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v6.2 files and rules exactly, platform version `1795330442-e2c5`; no
  `expedition/` or `opponents/` overrides)
- **Headless test before publish:** expedition 21/21 (now runs against R3 with its result stripped, to keep testing an
  unplayed round); lanes 14/14; image/notes 11/11; message/landing 9/9; Help 14/14; full regression 66/67 (the one
  "fail" is the favicon and Google font being unreachable from the test sandbox). Lane damage totals and every
  opponent DPS cross-checked against damage ÷ survival.
- **Platform version:** `1795358172-dc6e`
- **Files:**
  - `expedition-seed.json` · 133,918 bytes · sha256 `133389f58769d45fe7afe41c372481514f8b34cd0b64d67e4d04515c069ca3aa` (changed)
  - `changelog.json` · 17,925 bytes · sha256 `d93226db1016b0c2b3562e45f947d3966bbca370dae9a5ac5c4b9edd062e2752` (changed)
  - `index.html` · sha256 `c813f9b01571464fa8448ec68cedd9554e0e445c3cabecb1fc171701d319a108` (unchanged, archived in `dashboard/releases/v6.2/`)
  - `roster-seed.json` · sha256 `9e63aecd9280931fccc37123ac0fb0f0bcea01c0d6280220f14721494554c77a` (unchanged, archived in `dashboard/releases/v6.1/`)
  - `build-data.json` · sha256 `6fd7eeda6ff9c542bad0a6123c3a601f8f4ac6f8224b751b2786a9eeabb6722c` (unchanged, archived in `dashboard/releases/v3.1/`)
- **Permission rules:** unchanged from v6.2.
- **Changes:**
  - R3 vs Holymoly: won 3–0 (all 24 alive; Left 9s, Middle 11s, Right 9s); both sides' per-player damage/survival (ours
    with healing); Holymoly lanes no longer marked predicted (same 24, same lanes, third time).
  - Observations: Happiness vs UkraineArchers R3, both sides (lanes + damage/survival/DPS). Happiness W 2–1 is
    **derived** from survivors at fight end (see `claude/archero2-expedition-2026-11-16-r3-results.md`).
  - Week of Nov 16 final; standings derived: ArchAcademy 9 pts / 7 flags, Happiness 6 / 6, UkraineArchers 3 / 5,
    Holymoly 0 / 0. Confirm against the final standings screen.
- **Archive:** `dashboard/releases/v6.3/` (expedition-seed.json, changelog.json; sha256 verified) + index.html from
  `v6.2/`, roster-seed.json from `v6.1/`, build-data.json from `v3.1/`

### v6.2 — 2026-11-22
- **Type:** sub-version (minor adjustments)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v6.1 files and rules exactly, platform version `1795329354-8e34`; no
  `expedition/` override)
- **Headless test before publish:** lanes/sort suite 16/16 (desktop + phone); expedition 21/21; image/notes 11/11;
  message/landing 9/9; Help 14/14; full regression 66/67 (the one "fail" is the favicon and Google font being
  unreachable from the test sandbox).
- **Platform version:** `1795330442-e2c5`
- **Files:**
  - `index.html` · 278,514 bytes · sha256 `c813f9b01571464fa8448ec68cedd9554e0e445c3cabecb1fc171701d319a108` (changed)
  - `expedition-seed.json` · 119,909 bytes · sha256 `662382c2a3532b75eee85724b5e71506031367de2c7880aa583fea39e96c5698` (changed)
  - `changelog.json` · 17,256 bytes · sha256 `4a8d7d6f001879f6667f57616d9c6874f2006f91fc7060595ed6843b7e1fefda` (changed)
  - `roster-seed.json` · sha256 `9e63aecd9280931fccc37123ac0fb0f0bcea01c0d6280220f14721494554c77a` (unchanged, archived in `dashboard/releases/v6.1/`)
  - `build-data.json` · sha256 `6fd7eeda6ff9c542bad0a6123c3a601f8f4ac6f8224b751b2786a9eeabb6722c` (unchanged, archived in `dashboard/releases/v3.1/`)
- **Permission rules:** unchanged from v6.1.
- **Changes:**
  - Roster: sort chips with ✕ per sort; "Reset to power" whenever the sort isn't the default (Daby couldn't undo a
    single non-power sort before).
  - Rounds: status from the lock time (12:00 UTC on round day = 4:00 AM PT): "Preparing · locks …" before, "Locked"
    after, until results. R3 seed status `locked` → `planned` (lanes were set in game, not locked).
  - Rounds: our players show DPS avg (last 5 counted) or a gear estimate before a round is played; lanes are rows with
    ArchAcademy and the opponent side by side (stacked under 640px).
  - Terminus323's Oracle rounds added to `offSet` (via `SWITCHED` in make_expedition.py), so his average waits for
    Dragoon data (shows est. 60K/s). offSet wording: "a different gear set than they use now".
  - Help: "Editing permissions" section + heads-up under the quick start.
- **Archive:** `dashboard/releases/v6.2/` (index.html, expedition-seed.json, changelog.json; sha256 verified) +
  roster-seed.json from `v6.1/`, build-data.json from `v3.1/`

### v6.1 — 2026-11-22
- **Type:** sub-version (data update)
- **Requested by:** Daby (lineup change agreed in the weekly chat; "sync it now") · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v6 files and rules exactly, platform version `1795325595-8e58`;
  no `expedition/` override, no `roster/m-terminus323` doc)
- **Headless test before publish:** expedition 21/21; image/notes 11/11; message/landing 9/9; Help 14/14; full
  regression 65/66 (the one "fail" is the favicon and Google font being unreachable from the test sandbox).
- **Platform version:** `1795329354-8e34`
- **Files:**
  - `expedition-seed.json` · 119,729 bytes · sha256 `5b2ea748bd17a6f30a55cc0f539d31ccf3b11941e4b3d2001b0e33a93bd6f4c9` (changed)
  - `roster-seed.json` · 75,025 bytes · sha256 `9e63aecd9280931fccc37123ac0fb0f0bcea01c0d6280220f14721494554c77a` (changed)
  - `changelog.json` · 15,928 bytes · sha256 `861aa4040ee3431218b398d9d10995ff58f809ef4940c4513af8d8eb3bb1c33b` (changed)
  - `index.html` · sha256 `3f134362ac9dd9f357205464fbcb4e10f6599dd5beb3db11850d890a6ab9db48` (unchanged, archived in `dashboard/releases/v6/`)
  - `build-data.json` · sha256 `6fd7eeda6ff9c542bad0a6123c3a601f8f4ac6f8224b751b2786a9eeabb6722c` (unchanged, archived in `dashboard/releases/v3.1/`)
- **Permission rules:** unchanged from v6.
- **Changes:**
  - R3 vs Holymoly: Terminus323 replaces DrFuko in Middle (Heynow stays; DrFuko to subs). Terminus323's deployment
    power pending the new Middle screen.
  - R3 officer message: lanes ordered Left, Middle, Right (Daby); Terminus323 line, DrFuko in subs, tests #2/#3/#4
    updated, new test #8 (Oracle to Dragoon), long-fights DPS note. Source: weekly chat + 11-16 log (revised 11-22).
  - Roster: Terminus323 preset now Chaotic Dragoon, Phynx + Rolla + Otta, Mid / Balanced, status Complete (preset
    screen 11-22). Applied as a patch in `tools/make_seed.py`; every other member unchanged (verified: unpatched output
    matches v3.4's sha256).
- **Why it was published here:** the weekly chat couldn't update the dashboard (artifact tools there run with
  network access off and can only change artifacts made in that chat). Sync process: `dashboard/SYNC.md`.
- **Archive:** `dashboard/releases/v6.1/` (expedition-seed.json, roster-seed.json, changelog.json; sha256 verified)
  + index.html from `v6/`, build-data.json from `v3.1/`

### v6 — 2026-11-21
- **Type:** major version (new feature: Help tab)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v5.1 files and rules exactly, platform version `1795323518-ed1a`)
- **Headless test before publish:** Help suite 14/14 (desktop + phone); message/landing suite 9/9; expedition suite
  21/21; full regression 65/66 (the one "fail" is the favicon and Google font being unreachable from the test sandbox).
- **Platform version:** `1795325595-8e58`
- **Files:**
  - `index.html` · 273,883 bytes · sha256 `3f134362ac9dd9f357205464fbcb4e10f6599dd5beb3db11850d890a6ab9db48` (changed)
  - `changelog.json` · 15,190 bytes · sha256 `63790742dbc454c0bd2b0b8200682dcca6c26452bd624e74ef15623c621f7efd` (changed)
  - `expedition-seed.json` · sha256 `a0eebd1727011bd7d7b625f2fb800bf7b3ea5e6796407e49c6be4d3a3f8796b3` (unchanged, archived in `dashboard/releases/v5.1/`)
  - `roster-seed.json` · sha256 `311bffc810ed67dfd3058ed4274dcbf69767837f6720ab0a30619c6ef232f5b7` (unchanged, archived in `dashboard/releases/v3.4/`)
  - `build-data.json` · sha256 `6fd7eeda6ff9c542bad0a6123c3a601f8f4ac6f8224b751b2786a9eeabb6722c` (unchanged, archived in `dashboard/releases/v3.1/`)
- **Permission rules:** unchanged from v5.1.
- **Changes:**
  - New Help tab (`#help`): Quick start (from the "ArchAcademy Dashboard: Quick Start" doc) with links that jump to
    tabs, plus the full guide (from "ArchAcademy Dashboard: Getting Started") in collapsible sections: tabs in detail,
    common tasks, for officers, key terms, FAQ.
  - First-visit hint on the Roster pointing to Help; dismissed per browser (localStorage `aa-help-seen`, wrapped in
    try/catch).
  - "Changes" tab renamed "Changelog" (the `#changes` link still works).
- **Archive:** `dashboard/releases/v6/` (index.html, changelog.json; sha256 verified) + expedition-seed.json from
  `v5.1/`, roster-seed.json from `v3.4/`, build-data.json from `v3.1/`

### v5.1 — 2026-11-21
- **Type:** sub-version (minor adjustments)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v5 files and rules exactly, platform version `1795322092-2d2c`;
  `expedition/` and `notes/` collections empty, so the seed messages aren't overridden)
- **Headless test before publish:** message/landing suite 9/9; image/notes suite 11/11; expedition suite 21/21; full
  regression 65/66 (the one "fail" is the favicon and Google font being unreachable from the test sandbox).
- **Platform version:** `1795323518-ed1a`
- **Files:**
  - `index.html` · 261,321 bytes · sha256 `8ff1d91d7cb5567cb539b8cfc8f158c2a660857b5219d5055132b7744bf48cfa` (changed)
  - `expedition-seed.json` · 118,587 bytes · sha256 `a0eebd1727011bd7d7b625f2fb800bf7b3ea5e6796407e49c6be4d3a3f8796b3` (changed: officer messages)
  - `changelog.json` · 14,573 bytes · sha256 `daf96aaee5ac40647c940763be70d15621f9b94fee76dbb87ac63c9e865a9348` (changed)
  - `roster-seed.json` · sha256 `311bffc810ed67dfd3058ed4274dcbf69767837f6720ab0a30619c6ef232f5b7` (unchanged, archived in `dashboard/releases/v3.4/`)
  - `build-data.json` · sha256 `6fd7eeda6ff9c542bad0a6123c3a601f8f4ac6f8224b751b2786a9eeabb6722c` (unchanged, archived in `dashboard/releases/v3.1/`)
- **Permission rules:** unchanged from v5.
- **Changes:**
  - Message to the officers renders Discord markdown (bold, italics, bullets incl. nested and numbered, bold lane
    headers, emoji section headers with dividers) in the card and in its image. Long messages are clamped with
    "Show the full message". New "Copy text" button copies the raw Discord markdown.
  - Seed briefings for 11-16 R1-R3 replaced with the exact officer messages posted in Discord (R1 week plan, final R2
    plan with About Happiness, final R3 plan with the 7 tests), from `tools/briefs/` via make_expedition.py.
  - Lineup image no longer includes the message (it has its own image).
  - Default landing view is Roster (was Builds) when the link has no tab.
- **Archive:** `dashboard/releases/v5.1/` (index.html, expedition-seed.json, changelog.json; sha256 verified) +
  roster-seed.json from `v3.4/`, build-data.json from `v3.1/`

### v5 — 2026-11-21
- **Type:** major version (new features: officer messages + round notes, copy-as-image)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v4 files and rules exactly, platform version `1795319546-d693`;
  `expedition/` and `notes/` collections empty, so seed briefings aren't overridden)
- **Headless test before publish:** image/notes suite 11/11; expedition suite 21/21; full regression 65/66 (the one
  "fail" is the favicon and Google font being unreachable from the test sandbox).
- **Platform version:** `1795322092-2d2c`
- **Files:**
  - `index.html` · 255,231 bytes · sha256 `6a8875f801d94aa3dcd36710f170c36362a281181c80865c039db4225578c3e6` (changed)
  - `expedition-seed.json` · 106,794 bytes · sha256 `e4d5040ee04bfc21298f555658e831018111b90c18e61ae341395d20cef9b8c0` (changed: round briefings)
  - `changelog.json` · 13,678 bytes · sha256 `17b1570c012603b91d7a160a4e94fc1f0101079c73a5c17506025b0799f6d587` (changed)
  - `roster-seed.json` · sha256 `311bffc810ed67dfd3058ed4274dcbf69767837f6720ab0a30619c6ef232f5b7` (unchanged, archived in `dashboard/releases/v3.4/`)
  - `build-data.json` · sha256 `6fd7eeda6ff9c542bad0a6123c3a601f8f4ac6f8224b751b2786a9eeabb6722c` (unchanged, archived in `dashboard/releases/v3.1/`)
- **Permission rules:** unchanged from v4 (new collection `notes/<week id>-r<n>` is covered by the root rule:
  everyone views, Editors write).
- **Changes:**
  - Rounds: "Message to the officers" card (latest `briefing` entry in `notes/`, else the seed's `round.briefing`).
    Seed briefings written for 11-16 R1-R3 by Daby (with Claude). Officers post new messages; older ones stay in notes.
  - Rounds: "Notes & reasoning" log per round (append-only). Claude can add notes from regular chats via db_write
    after Daby confirms the text; every post is logged in the activity log ("expedition").
  - Copy as image (canvas PNG; clipboard first, else preview + Download): lineup (both sides, anchors with lane HP%,
    gear color bars), round results, player history, Players table, Roster table.
  - Players: "Notable" column shows only major items (gear switch ≥2×, last round ≥+75%/≤−50%, personal best ≥25%,
    trend ≥+50%/≤−40%), max one per player; minor notes on the player page. Trend is sparkline only.
  - Rounds: "Group" → "Guilds", guild names link to Opponents (ArchAcademy → Roster), player names link to Players.
    Standings are plain text. Played rounds read-only (Round details stays, read-only); lineup editing only for
    unplayed rounds; results maintained by Claude from screenshots.
- **Archive:** `dashboard/releases/v5/` (index.html, expedition-seed.json, changelog.json; sha256 verified) +
  roster-seed.json from `v3.4/`, build-data.json from `v3.1/`

### v4 — 2026-11-21
- **Type:** major version (new feature: Expedition tab)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v3.4 files and rules exactly, platform version `1795317038-6cd8`)
- **Headless test before publish:** expedition suite 17/17; full regression 65/66 (the one "fail" was the favicon
  and Google font being unreachable from the test sandbox). Seed check: all 141 derived per-player DPS values match
  the tracker sheet's DPS History.
- **Platform version:** `1795319546-d693`
- **Files:**
  - `index.html` · 236,865 bytes · sha256 `043b47af64c66a9e899678c69641e9b74676b3c0765eb71b9148cf12eff20669` (changed)
  - `expedition-seed.json` · 104,742 bytes · sha256 `339e9e800d2fd3b1bdef5157dc82bb11363953ce48f64b7b992e50dcf75b038e` (new)
  - `changelog.json` · 12,058 bytes · sha256 `9253a9f756a90a50d66161f577cb407a7335d8c55a34722c97d67fa3343e5d2a` (changed)
  - `roster-seed.json` · sha256 `311bffc810ed67dfd3058ed4274dcbf69767837f6720ab0a30619c6ef232f5b7` (unchanged, archived in `dashboard/releases/v3.4/`)
  - `build-data.json` · sha256 `6fd7eeda6ff9c542bad0a6123c3a601f8f4ac6f8224b751b2786a9eeabb6722c` (unchanged, archived in `dashboard/releases/v3.1/`)
- **Permission rules:** unchanged from v3.3 (new collections `expedition/<week id>` and `opponents/<id>` are covered
  by the root rule: everyone views, Editors write).
- **Changes:**
  - Expedition tab, seeded (`expedition-seed.json`) from the Nov 2 / 9 / 16 logs, post-mortems and scans: 9 rounds
    (both sides' lanes, lane results, durations, per-player damage/survival/healing), 8 opponents (scans, habits),
    10 opponent-vs-others observations, findings, mechanics.
  - Rounds: lane board with live lane math and a per-lane win estimate (DPS × effective HP pool); officer lineup
    editor (slot selects, copy previous round), round details (opponent, status, their lanes), results editor
    (manual + Details screenshot reading via `sample` images), saved to `expedition/<week>` and logged ("expedition").
  - Suggested lineups on request: spread vs stack-two-concede-one, expected flags, reasons; officers can apply.
  - Opponents: lane history, roster scans, habits; officers add/edit (`opponents/<id>`).
  - Players: per-player history, 5-match DPS, best, alive-at-end rate, lane-relative index, trend, notes.
  - Findings: findings, mechanics, estimate sanity check (14/16 past clear-cut lanes), and "Assumptions and limits".
  - Roster DPS Avg now computed from logged Expedition rounds (last 5 counted matches; raw average, can differ ~1K
    from the sheet); profiles link to the player's history.
- **Archive:** `dashboard/releases/v4/` (index.html, expedition-seed.json, changelog.json; sha256 verified) +
  roster-seed.json from `v3.4/`, build-data.json from `v3.1/`

### v3.4 — 2026-11-21
- **Type:** sub-version (minor adjustments)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v3.3 files and rules exactly, platform version `1795316107-2563`)
- **Headless test before publish:** 65/66 checks passed (the one "fail" was the favicon and Google font
  being unreachable from the test sandbox)
- **Platform version:** `1795317038-6cd8`
- **Files:**
  - `index.html` · 168,973 bytes · sha256 `12fd85e145d5b296c0071b6bd03c2fbbc147295ffd4a4ff085cea3fd5d43f314` (changed)
  - `roster-seed.json` · 74,750 bytes · sha256 `311bffc810ed67dfd3058ed4274dcbf69767837f6720ab0a30619c6ef232f5b7` (changed)
  - `changelog.json` · 10,159 bytes · sha256 `280aeffaf9f6cfd04939d59576813ebab9abff44efe78a6438b337335a6f825b` (changed)
  - `build-data.json` · 25,592 bytes · sha256 `6fd7eeda6ff9c542bad0a6123c3a601f8f4ac6f8224b751b2786a9eeabb6722c` (unchanged, archived in `dashboard/releases/v3.1/`)
- **Permission rules:** unchanged from v3.3.
- **Changes:**
  - Roster multi-column sort: the newest header tap is the primary key, earlier taps (up to 4) break ties;
    subscript numbers on the arrows show the order; "Reset sort" returns to power only.
  - Gear filled from the weapon is treated as known (per Daby): no `gearAssumed` in the seed, any older
    marks ignored, no dashed chips. Accurate data to come from officers/imports before next week's Expedition.
  - Inventory: "Load example" and "Clear inventory" ask for confirmation (inline, not a browser pop-up).
- **Archive:** `dashboard/releases/v3.4/` (index.html, roster-seed.json, changelog.json; sha256 verified) +
  build-data.json from `dashboard/releases/v3.1/`

### v3.3 — 2026-11-21
- **Type:** sub-version (Expedition preset sync fix, runes column, full-set gear assumption)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v3.2 files and rules exactly, platform version `1795314715-14bf`).
  Roster collection had one officer doc: `roster/m-daybee` (Daby's link, saved under v3.2).
- **Headless test before publish:** 62/63 checks passed (the one "fail" was the favicon and Google font
  being unreachable from the test sandbox)
- **Platform versions:** `1795316099-1725` (rules: added `presets` read:view write:admin and
  `presets/{self}` read:view write:interact) → `1795316107-2563` (files published)
- **Files:**
  - `index.html` · 166,771 bytes · sha256 `17e670c82cbe3ecb0a3d27553fbaa8fd29bf931dc8690021688e4faa3f707f56` (changed)
  - `roster-seed.json` · 79,006 bytes · sha256 `79c5bcdb91632af1cbd55a06688bc253c96f4998c851e470af3f61c21df6da70` (changed)
  - `changelog.json` · 9,467 bytes · sha256 `32125af9fcebe065530f88ac730ec8b1a1bcc749afd6fbca12e8b4195289ea06` (changed)
  - `build-data.json` · 25,592 bytes · sha256 `6fd7eeda6ff9c542bad0a6123c3a601f8f4ac6f8224b751b2786a9eeabb6722c` (unchanged, archived in `dashboard/releases/v3.1/`)
- **Permission rules (db):** root read:view write:admin · `data/users/{self}` write:interact ·
  `audit` read:view write:self · `audit/{self}` read:view write:admin · **new** `presets` read:view
  write:admin · **new** `presets/{self}` read:view write:interact. `sample` images, `user` profile.
- **Changes:**
  - Fixed (reported by Daby): saving the Builds-tab Expedition preset didn't update the linked roster
    profile. Two-way sync now, newest wins by time (`presetUpdatedAt` on roster docs; build `updatedAt`).
    Officers push to `roster/<id>` (logged "updated own preset"); members publish to `presets/<their id>`
    (one doc each, shown when newer than the roster's copy and only from the officer-linked account if any;
    the Activity log lists each player's latest update). Roster → Builds pull updates the Expedition build
    and copies the pieces' stars/qualities into the Inventory (assumed gear never overwrites a real entry);
    never overwrites unsaved Builds-tab edits.
  - Players can edit their own preset on the Roster tab ("Edit my preset"; own gear chips tappable).
  - Runes column (filled slots out of 13, list on hover). Rune editing stays in the profile editors (inline
    rune editing judged too dense: 13 slots × name + quality).
  - Gear: complete-set assumption (per Daby). Unknown set/quality on any slot = the weapon's, marked
    `gearAssumed` and drawn dashed until confirmed. Applied in the seed and at display time, so older saved
    entries (e.g. `roster/m-daybee`) get it too. Inline/officer edits and imports clear the mark per slot.
  - Roster table tightened to fit desktop width (smaller type, "Last updated" as MM-DD with full date on hover).
- **Archive:** `dashboard/releases/v3.3/` (index.html, roster-seed.json, changelog.json; sha256 verified) +
  build-data.json from `dashboard/releases/v3.1/`

### v3.2 — 2026-11-21
- **Type:** sub-version (Roster adjustments + scrolling bug fix)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v3.1 files and rules exactly, platform version `1795313516-3ad4`);
  roster collection empty
- **Headless test before publish:** 52/53 checks passed (the one "fail" was the favicon and Google font
  being unreachable from the test sandbox)
- **Platform version:** `1795314715-14bf`
- **Files:**
  - `index.html` · 154,235 bytes · sha256 `75bf281b527472e04f4c4851b7260f7604dad2dfe834e4d0d93411afa4067f97` (changed)
  - `roster-seed.json` · 72,298 bytes · sha256 `511b999764dc8ab30d9493bc5930c7e083b924a67a8ad390d8087df11ceb582e` (changed)
  - `changelog.json` · 8,322 bytes · sha256 `718c3a5fdf55e8c643c056f52386ea770d23b8a4b3ba08eb460ba9ce5aeae82f` (changed)
  - `build-data.json` · 25,592 bytes · sha256 `6fd7eeda6ff9c542bad0a6123c3a601f8f4ac6f8224b751b2786a9eeabb6722c` (unchanged, archived in `dashboard/releases/v3.1/`)
- **Permission rules:** unchanged from v3.
- **Changes:**
  - Fixed (reported by Daby as "Gaga94 missing"): v3.1's roster scrolled inside its own 75vh box, so
    low-power rows (Gaga94 at ~row 38) were hidden unless you scrolled inside the table. Data was never
    lost. Now the page scrolls; the column headings are translated to sit under the pinned top bar
    (works with the table's horizontal scroll on phones). Slimmer top bar on phones.
  - Gear by slot: six chips per row (slot icon, set letter on set color, short quality; tooltip has full text),
    with a key under the table.
  - Officers: tap a gear chip to change that slot's set and quality inline (either may be "unknown"); saved
    to `roster/<id>` and logged ("edited roster: <ign>: <slot> <old> → <new>").
  - ⚓ on the top 5 anchors (highest calculated Lane HP among active members).
  - Mystling stars: "blue" on old captures = teal (per Daby). Newly filled: Tuup ★8, daybee ★6, Zeuzo ★6,
    KevinShock ★6, Tw3aKZ ★10. Still blank: taz96 ("2 blue", incomplete), DrShabz ("2 red / 3 yellow",
    non-adjacent), DrFuko (no mystling name).
- **Archive:** `dashboard/releases/v3.2/` (index.html, roster-seed.json, changelog.json; sha256 verified) +
  build-data.json from `dashboard/releases/v3.1/`

### v3.1 — 2026-11-21
- **Type:** sub-version (Roster and Training Ground adjustments)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v3 files and rules exactly, platform version `1795311563-d292`);
  roster collection empty (no officer edits masking the seed changes)
- **Headless test before publish:** 46/47 checks passed (the one "fail" was the favicon and Google font
  being unreachable from the test sandbox)
- **Platform version:** `1795313516-3ad4`
- **Files:**
  - `index.html` · 146,869 bytes · sha256 `a3290f12b7f38678432cd3feb1734037b01038c5a50839b20102bb4a9f1444be` (changed)
  - `roster-seed.json` · 72,322 bytes · sha256 `75b1c252ee9a91fd1a13a9efdc86e78bf1243207bc12e42a1f485ad2664e810e` (changed)
  - `build-data.json` · 25,592 bytes · sha256 `6fd7eeda6ff9c542bad0a6123c3a601f8f4ac6f8224b751b2786a9eeabb6722c` (changed)
  - `changelog.json` · 7,411 bytes · sha256 `1006b7c3498639f15530d3f9c7e7863d8342cd514a0ed14bb5bb734b46f8158f` (changed)
- **Permission rules:** unchanged from v3 (db rules as v2; `sample` images; `user` profile).
- **Changes:**
  - Title and tabs stay pinned at the top while scrolling. Roster table scrolls in its own box with
    pinned headings (two lines max, sort arrow never wraps) and a pinned Player column on phones.
  - Mystlings seeded from guild nicknames (reaper=Death Mage, jester=The Fool, snake=Queen Medusa,
    goblin witch=Witch, dragon=Nian Beast, owl=Snowy Owl). Star colors (per Daby): yellow, teal, red,
    purple/pink/blue fade, dark red, 5 stars each. Stars only where the capture was complete and in
    adjacent colors (Hago26 ★18; MuffinKnight, Hansi218, MsPoppycorn ★15; TylerG, Bazal, Legitkit ★0).
    Captures mentioning "blue" left blank (ambiguous). build-data adds `mystlingStarColors`.
  - Gaga94 preset corrected: Godforge ★5 Oracle weapon, Mythic Dragoon armor, Chaotic Oracle ring,
    Mythic+3 Dragoon helmet, Mythic+2 Griffin amulet, Chaotic Dragoon boots.
  - Training Ground: "Someone else's build" → "Custom build" with a name field; saves as a named build.
  - Preset import: one card per screenshot, each REQUIRES a roster player name (no owner guessing; the
    old guessing code was removed). Same name = one preset read together (shared color, "Same as
    previous"). Up to 8 screenshots / several players per batch; Apply or Apply all. Import section
    moved to the bottom of the Roster tab.
  - Linking: any member can link their account to one roster profile (members' links stored privately as
    `linkedMemberId`; officers' links also shared on the roster doc). Linking fills the Inventory and an
    empty Expedition preset from the profile without overwriting entries; unknown stars stored as `null`
    (shown ★?). One profile per account (page-enforced).
- **Archive:** `dashboard/releases/v3.1/` (all four files; sha256 verified)

### v3 — 2026-11-21
- **Type:** major version (new feature: Roster)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v2.3 files and rules exactly, platform version `1795310454-f7af`)
- **Headless test before publish:** 31/32 checks passed (the one "fail" was the favicon and Google
  font being unreachable from the test sandbox). Found and fixed a live v2.3 bug: Training Ground
  kept a stale copy of the Main build after it was edited on the Builds tab.
- **Platform versions:** `1795311556-4be5` (capability change: `sample` now `{images: true}` for
  screenshot import) → `1795311563-d292` (files published)
- **Files:**
  - `index.html` · 135,088 bytes · sha256 `0ccd568fb9fa15a31afe19d50e9e6dbe96db2ef114963aafd778d61b57a2da4b` (changed)
  - `roster-seed.json` · 70,718 bytes · sha256 `e12a6dd54cc60dc46888ea9dc5cc080ab0877ac1d41d850d6702229f14d5d543` (new)
  - `changelog.json` · 5,506 bytes · sha256 `7efaf82c26a2f10450ce1c46c2f23b7684d5d90d98cb1ec49e6df29dff46b370` (changed)
  - `build-data.json` · 25,324 bytes · sha256 `06e5930ab0124a93493427cf85d711c59932bff70e9ef993f525fd64368cdde9` (unchanged, archived in `dashboard/releases/v2.3/`)
- **Permission rules (db):** unchanged from v2 (roster docs live at `roster/<id>`, covered by the root
  rule: everyone views, Editors write). **Changed:** `sample` declares images. `user` scope profile unchanged.
- **Changes:**
  - New Roster tab, seeded from `claude/archero2-expedition-log-2026-11-16.md` (snapshot 11-19, R3
    deployment powers 11-21) and the tracker sheet (ranks 11-06, DPS History). 44 members: Failwyn and
    Lodt excluded, Lepimi inactive. Gear = weapon set, all six slots Chaotic for "C" players (other
    sets unknown). Resonances only where trusted (blank for Heynow, Yullong). Runes and mystlings blank;
    mystling nickname + star colors kept as text (`mystlingSeen`).
  - Columns: Player, Rank, Power, Character, Gear, Mythic / Leg Artifacts, ATK bonus, Lane HP (if anchor),
    DPS Avg (K/s), Last updated, Preset. Sortable, searchable, status filter.
  - Profiles: preset, gear, runes, mystling, DPS history, notes. ATK bonus (0.25%/Mythic ★ + 0.025%/Leg ★),
    Lane HP (18%/Mythic ★ + 1.8%/Leg ★) and DPS Avg are calculated, never stored, read-only for everyone.
  - Officers: edit profiles, add members, mark inactive/left, link own Claude account to an IGN
    ("This is me"). Each save logged to the activity log (`edited roster`, `added member`,
    `linked account`, `imported preset`).
  - Preset screenshot import (officers, uses their Claude usage): Claude reads 1–3 screenshots, values
    validated against the game data (unknown names dropped; runes only if clearly readable); owner guessed
    by character/resonance/gear/power similarity; officer confirms and sees old vs new before applying.
  - Training Ground: player field suggests roster names; fixed stale Main build (see above).
  - Build editors: entering someone else's build allows a gear quality without a set.
  - Example-account banner only shows on Inventory, Builds and Training Ground.
- **Archive:** `dashboard/releases/v3/` (index.html, roster-seed.json, changelog.json; sha256 verified) +
  build-data.json from `dashboard/releases/v2.3/`

### v2.3 — 2026-11-21
- **Type:** sub-version (minor adjustments)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v2.2 files and rules exactly, platform version `1795309070-3159`)
- **Platform version:** `1795310454-f7af`
- **Files:**
  - `index.html` · 97,891 bytes · sha256 `33b914b2de38886d3058e8bbdce7cc88475cc7d6a27dc0d48b129784f448cb98` (changed)
  - `build-data.json` · 25,324 bytes · sha256 `06e5930ab0124a93493427cf85d711c59932bff70e9ef993f525fd64368cdde9` (changed)
  - `changelog.json` · 4,174 bytes · sha256 `c4b26ba404c6fbd50d56a7373c2e3cdfb56140a130bee55082aea8ad28d5e4cc` (changed)
- **Permission rules:** unchanged from v2.
- **Changes:**
  - Runes renamed to in-game names: Fairy Multishot → **Sprite Multishot**, Fairy Combo →
    **Sprite Link** (build-data `runeRenames`; Elemental DPS template updated). Saved accounts and
    builds with the old names migrate on load.
  - Build editors (Builds tab and Training Ground): a rune or character picked in one slot is
    removed from the other slots' lists; clearing a slot returns it.
- **Known bug at release (fixed in v3):** Training Ground showed a stale Main build after edits on the Builds tab.
- **Archive:** `dashboard/releases/v2.3/` (all three files; sha256 verified)

### v2.2 — 2026-11-21
- **Type:** sub-version (Builds and Training Ground fixes; Roster deferred to v3)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v2.1 files and rules exactly, platform version `1795303959-c825`)
- **Platform version:** `1795309070-3159`
- **Files:**
  - `index.html` · 96,472 bytes · sha256 `e01736405e03f2570cf07d549bd92d36b76dea4a227c0819297be6adc2cd66f5` (changed)
  - `build-data.json` · 25,067 bytes · sha256 `00e75f481bd177281dcd2d58a6c48f720e6bf176ecd8578a2eefe9506fc38fca` (changed)
  - `changelog.json` · 3,699 bytes · sha256 `7cc487a2625b2d4db04753578b9767428a5f4104534ae987f3280570c58f5d78` (changed)
- **Permission rules:** unchanged from v2 (no new storage paths; saved accounts still live at
  `data/users/<id>/builds-account`, now schema v3).
- **Changes:**
  - New Inventory tab, separate from Builds: in-game name, characters, gear, runes (with etched
    slots), mystlings with ★0–25 stars and read-only skill level (Lv up at ★4/9/14/19/24).
  - Builds tab: labeled builds. "Main build" and "Expedition preset" always exist; custom named
    builds can be created, renamed, deleted. Editor offers only inventory items; stars and
    qualities follow the inventory (read-only). One equipped mystling per build. Range/Movement
    behavior. Live check: warnings, synergies, notes, tips.
  - Suggestions now on request only (collapsed "Want a suggestion?" + button). Partial matches
    name the missing piece. A suggestion can be saved as a custom build. Ask Claude explainer kept.
  - Training Ground: player defaults to the IGN; tested build pre-fills from a saved build (Main
    by default) including runes with quality, mystling stars, character stars; "Save to my builds"
    writes it back; "Someone else's build" option. Suggested/current choice removed. Tests now
    store the full build (`build`, `buildName`, test doc v2); older entries still display.
  - build-data.json: added mystling star/skill-level data, `equippedMystlings: 1`, behavior options.
  - Saved v2.1 accounts migrate automatically (mystlings come in at ★0).
- **Known quirk:** the build check's synergy/tip filtering follows the PvP/PvE toggle in the
  suggestion box (defaults to PvP).
- **Archive:** `dashboard/releases/v2.2/` (all three files; sha256 verified)

### v2.1 — 2026-11-21 (published as "r2.1")
- **Type:** sub-version (bug fix)
- **Requested by:** Daby · **Published by:** Claude
- **Pre-publish audit:** clean (live matched v2 files and rules exactly)
- **Platform version:** `1795303959-c825`
- **Files:**
  - `index.html` · 73,927 bytes · sha256 `39f5d5be48a46cee892d315038cfde1309731e30b2ddd31a9e5d4dd1e356158e` (changed)
  - `changelog.json` · 2,551 bytes · sha256 `258150f46e34232f5166900bd576f254fb3ecb6a6290bc8fba670f8c9b4a4d5c` (changed)
  - `build-data.json` · 24,512 bytes · sha256 `e33661676711b5e89257d748a0536eae6993a9c609abd7f2c4b559ff773444ba` (unchanged, archived in `dashboard/releases/v2/`)
- **Permission rules:** unchanged from v2.
- **Changes:**
  - Fixed: all tabs' content showed at once as one long page and tapping tabs did nothing
    (desktop and mobile). Cause: layout classes (`.stack`, `display:grid`) overrode the `hidden`
    attribute. Added a global `[hidden] { display: none !important; }`.
  - Fixed: Training Ground "Their current build" fields were always visible (same cause).
  - Tabs (and the release badge, and "Test this build in Training Ground") now switch views
    directly on tap instead of relying only on the URL hash, and scroll back to the tab bar.
- **Archive:** `dashboard/releases/v2.1/` (index.html, changelog.json; sha256 verified) +
  build-data.json from `dashboard/releases/v2/`

### v2 — 2026-11-21 (published as "r2")
- **Type:** major version
- **Requested by:** Daby · **Published by:** Claude
- **Platform versions:** `1795302794-8729` (permission rules updated) → `1795302803-c15e` (files published)
- **Files:**
  - `index.html` · 73,238 bytes · sha256 `bdbab192bf9765309de59e0591f23d24621ba8b37d27fd4a469e85063baa6ff2`
  - `build-data.json` · 24,512 bytes · sha256 `e33661676711b5e89257d748a0536eae6993a9c609abd7f2c4b559ff773444ba`
  - `changelog.json` · 1,878 bytes · sha256 `c9812471be5fceb243379920360923b783981d92fdd447f6888b6138d1083d0c`
- **Permission rules (db):** root read:view write:admin · `data/users/{self}` write:interact ·
  `audit` read:view write:self · `audit/{self}` read:view write:admin. Also declares `user`
  (scope profile) and `sample` (no images).
- **Changes:**
  - Builds: all three abilities count equally; deployed slot goes to a ★6+ character (or the
    highest-star one). "Deploy" picker replaced by "Build around".
  - Builds: full gear quality ladder (Epic to +3, Legendary to +3, Mythic to +4, Chaotic,
    Godforge ★1–10).
  - Builds: per-rune quality (Common → Mythic, Twinborn). Affects score, substitutes, upgrade tips.
  - Builds: Griffin + Circle requires Thor anywhere in the lineup; Dragoon + Element + Meteor
    requires Cleo and Otta (inferred, unconfirmed).
  - New Training Ground tab: standard 3 × 1-minute Dummy test, movement tips, shared leaderboard
    (`tg-results`), private tracker (`data/users/<id>/tg/tests`).
  - New Changes tab: release notes + activity log (`audit/<id>`, one doc per officer).
  - Fix: PvP/PvE switch crashed when the data file failed to load.
- **Known bug at release (fixed in v2.1):** tabs didn't hide/switch.
- **Archive:** `dashboard/releases/v2/` (all three files verified against sha256; index.html and
  changelog.json rebuilt from v2.1 by reversing v2.1's three edits during the rename, and
  matched the original fingerprints exactly)

### v1 — 2026-11-21 (published as "r1")
- **Type:** major version (first)
- **Requested by:** Daby · **Published by:** Claude
- **Platform versions:** `1795293417-4d35` (files) → `1795293421-c5e7` (capabilities declared)
- **Files:**
  - `index.html` · 47,395 bytes · sha256 `1627793a23cc4fe04d2c93b8b181c1fac9a9e623950a7ce27489c63c35922329`
  - `build-data.json` · 22,706 bytes · sha256 `99ca392124501c5dc1c0576287b1fb73430e2bdae74132913f476a54e3ea7b5b`
- **Permission rules (db):** root read:view write:admin · `data/users/{self}` write:interact.
  Also declares `user` (scope profile) and `sample`.
- **Changes:** first release. Builds tab (account entry, one best PvP/PvE build with reasoning,
  upgrade list, optional Ask Claude explainer), private saved account.
- **Archive:** `dashboard/releases/v1/` (sha256 verified)

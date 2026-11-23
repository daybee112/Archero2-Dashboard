# Data model

How the dashboard stores its data, before and after v8.0.0. Paths are in the artifact's shared database unless marked as files.

## Permission rules (fixed)

The artifact's rules can't be changed from Claude (the platform refuses because the artifact holds other people's writing), so v8 works within them:

| Rule | Meaning |
|---|---|
| `""` read view, write admin | everyone reads everything; officers (Editors) write |
| `data/users/{self}` write interact | each person's private area (not readable by others) |
| `presets` read view, write admin · `presets/{self}` write interact | everyone reads; each person writes their own `presets/<id>` and, we expect, records under it |
| `audit` read view, write self · `audit/{self}` write admin | each officer writes only their own audit records |

Records under `presets/<id>/…` and `audit/<id>/…` rely on the `{self}` rule covering descendants. That isn't documented, so the page tries the new path and falls back to the old single record if a write is refused.

## Before v8 (v7.3.0)

| Data | Where |
|---|---|
| Rounds, lineups, results, stats, notes for every week | file `expedition-seed.json` (`weeks[].rounds[]`); officers' edits replace a whole week at `expedition/<week>` |
| Opponents (habits, scans) | file `expedition-seed.json` (`opponents`); edits replace a whole guild at `opponents/<o-hex>` |
| Other guilds' matches ("observations"), findings, mechanics | file `expedition-seed.json` only |
| Roster | file `roster-seed.json`; officers' edits overlay at `roster/<member>` |
| A member's preset, account link, shared inventory, activity log | one record, `presets/<id>` (`preset`, `memberId/linked`, `shared`, `log[≤300]`) |
| Officers' edits to someone's inventory | `inventory/<member>` |
| Officer activity log | one record `audit/<id>` (≤400 entries), overflow to `audit/<id>/months/<yyyy-mm>` |
| Round notes | `notes/<week>-r<n>`, `notes/<week>-week` |
| Training Ground | `tg-results` (shared), `data/users/<id>/tg/tests` (private) |

## v8.0.0

Data that changes with guild activity moves out of the files and into the database, split into small records so an edit touches one thing.

| Data | New path |
|---|---|
| Week header (group, standings, lessons, final) | `expedition/<week>` |
| Each round (lineups, lane results, stats, notes, briefing, key notes) | `expedition/<week>/rounds/<n>` |
| Opponent guild (name, weeks, power, habits) | `opponents/<o-hex>` |
| Each roster scan of a guild | `opponents/<o-hex>/scans/<date>` |
| Each match between other guilds | `observations/<week>-r<n>-<o-hex>` |
| Findings and mechanics | `meta/findings` |
| Roster (every member, full record) | `roster/<member>` (seed copied in once) |
| Member's Expedition preset | `presets/<id>` (preset fields only) |
| Member's account link | `presets/<id>/meta/link` |
| Member's shared inventory | `presets/<id>/meta/inventory` |
| Member's activity log | `presets/<id>/log/<yyyy-mm>` (one record per month) |
| Officer activity log | `audit/<id>/months/<yyyy-mm>` (one record per month) |

Unchanged: `data/users/<id>/…`, `inventory/<member>`, `notes/…`, `tg-results`.

Files that stay: `index.html`, `changelog.json`, `build-data.json` (game reference data). `expedition-seed.json` and `roster-seed.json` are kept only as the one-time migration source and the fallback for the first load.

## Migration

The first officer to open v8.0.0 copies anything missing from the seed files into the new paths, once (`meta/migration` records when and by whom). Every page reads the new paths first and falls back to the old record or the seed file, so an old tab or a member who hasn't reloaded keeps working. Members' own records move the next time each member saves or opens the dashboard.

## Backups

At each sync, every collection is exported to `data/db-exports/<date>/` in this repo.

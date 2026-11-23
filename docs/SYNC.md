# Keeping weekly chats and the dashboard in sync

Daby starts a new chat for each Expedition week and sends screenshots there most days (Wednesday to Saturday). The dashboard (ArchAcademy Dashboard, https://claude.ai/artifact/MaDLSLGhDxJPiPJcWeJ4si) can only be changed from the chat it was built in (the dashboard chat), so weekly chats **stage** changes and the dashboard chat **syncs** them. Agreed with Daby 2026-11-22; revised for v8 the same day (Daby chose batching from the weekly chat over a daily dashboard chat or in-dashboard uploads).

## In a weekly chat
1. **Start by reading the dashboard's current week** (lineups, message to the officers, notes) and the week's log in `claude/`, so the chat begins from what officers see.
2. **The week's log is the source of truth.** Every agreed lineup change, officer message, test, scan and result read from a screenshot goes into the log (`claude/archero2-expedition-log-<week>.md` and its companion docs) right away.
3. **Stage database changes** in `claude/archero2-staged-<week>.md`, one entry per change, newest at the bottom:
   - date and what it came from (e.g. "R2 Details screens, 3 of ours + 3 of theirs")
   - the record it changes, by v8 path: `expedition/<week>` (week header: group, standings, lessons), `expedition/<week>/rounds/<n>` (lineups, lane results, stats, notes), `opponents/<o-hex>` (guild, habits) and `opponents/<o-hex>/scans/<date>`, `observations/<week>-r<n>-<o-hex>` (other guilds' matches), `roster/<member>` (power, gear, artifacts, preset), `meta/findings`
   - the values, written out in full (no "same as before"), and anything uncertain left blank and flagged
   - Never stage enemy characters.
4. **Don't try to write to the dashboard** from the weekly chat (those writes are refused). Tell Daby when something is staged: "Staged. Say **sync the dashboard** in the dashboard chat when you're ready." For an urgent swap before lock, officers can edit the lineup directly in the dashboard.

## In the dashboard chat ("sync the dashboard")
1. Read the staged file and the week's log, and compare with what the dashboard database holds now (including any officer edits since).
2. Show Daby the differences and get his OK. Conflicts (an officer changed the same record) are called out, not overwritten.
3. **Back up first:** export the collections being changed to `data/db-exports/<date>/` in the GitHub repo.
4. Write the records with db_write (only what changed), then read them back and check them, and check the page shows them.
5. **Log it:** append one entry per sync to the activity log at `audit/<Daby's id>/months/<yyyy-mm>` with `src: "claude"` (shows as "by Claude"), the action ("synced from weekly chat"), what changed, and before → after where it's short. Mark the staged entries as synced (date) in the staged file. Data syncs are **not releases**: no version number, no publish.
6. **Activity summary:** read the activity log (`audit/<id>/months/…`, `presets/<id>/log/…`) and add one line for the week under "Activity summaries" in `dashboard/CHANGELOG.md`: counts of in-tool changes by type and person, plus any tamper flags.

## Releases (page changes only)
Versions are major.minor.patch, each part starting at 0: major = new features, minor = page improvements and adjustments, patch = maintenance and bug fixes. Follow the release process in `dashboard/CHANGELOG.md`. Release history is kept in the GitHub repo `daybee112/Archero2-Dashboard` ("Release vX.Y.Z" commits on `main`).

## Reading the dashboard from any chat
Any project chat can read the dashboard's page and data (lineups, notes, messages to the officers, activity log) even when it can't change them.

## Formatting reminders
- Lanes are always listed Left, Middle, Right, in lane plans and officer messages.
- Officer messages follow the format in the project preferences (Discord markdown in a code block). The dashboard shows them as posted.

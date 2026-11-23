# ArchAcademy Dashboard

Guild dashboard for the Archero 2 guild **ArchAcademy**: roster, inventories and builds, Training Ground, and Guild Expedition planning and results.

- **Live dashboard:** https://claude.ai/artifact/MaDLSLGhDxJPiPJcWeJ4si (a claude.ai artifact, slug `a699eb5d-8093-41f9-a74f-b4e8d5d70341`)
- **Current stable release:** **v9.0.0** (2026-11-23), the first release marked stable.
- **Release history:** release commits ("Release vX.Y.Z") on `main`, tags on GitHub, and [`docs/CHANGELOG.md`](docs/CHANGELOG.md). Claude's sessions can't push tags, so Daby tags each release on GitHub.
- **Data model:** [`docs/DATA-MODEL.md`](docs/DATA-MODEL.md)

## Layout

| Path | What it is |
|---|---|
| `app/` | Exactly the files published to the artifact: `index.html` (the whole app), `changelog.json` (release notes shown by the version badge), `build-data.json` (game reference data), and the seed data files |
| `tools/` | Generators for the seed data (`make_expedition.py`, `make_seed.py`), the officer messages in `briefs/`, and the tracker sheet export |
| `tests/` | Headless browser tests (Playwright + Chrome) with a mock of the artifact runtime (`mock.js`) |
| `data/db-exports/` | Snapshots of the live shared database, one folder per export |
| `docs/` | Release log (`CHANGELOG.md`), data model (`DATA-MODEL.md`), sync process (`SYNC.md`) |

## The live database

The shared database lives inside the artifact (that's what members' dashboards read and write), not in this repo. It's backed up here in `data/db-exports/` at each sync. Permission rules are declared on the artifact and can't currently be changed from Claude, so members can only write their private `data/users/<id>` area and their own `presets/<id>` records; officers can write everything else.

## Branches (from v9.0.0, per Daby)

- **`main`** always matches what's live: `app/` on `main` changes only in a "Release vX.Y.Z" commit. Docs-only commits
  (README, process docs, database exports) can go straight to `main`.
- **Feature branches:** every piece of work gets its own branch off `main`: `feature/<short-name>` for new features and
  improvements, `fix/<short-name>` for bug fixes and maintenance. Commit and run the tests on the branch; push it so the
  work is backed up. Keep it current with `main` (merge `main` in) if a release lands meanwhile.
- **Releases are batched.** When a set of finished branches is worth shipping, merge them into a short-lived
  `release/vX.Y.Z` branch, bump the version, run the full test suite there, show Daby screenshots, and only publish after
  his OK. Then fast-forward `main` to it and delete the merged branches.
- **Version number for a batch:** the biggest change in it decides: any new feature → major; else any page improvement →
  minor; else maintenance/bug fixes only → patch.
- **Urgent bug fix:** a `fix/` branch can be released on its own as a patch when it can't wait for the next batch.
- Older branches: `history` (v6.9.0–v7.2.0, merged into `main`) and `v8` (the v8 work, fully merged) are kept for
  reference; no new work goes on them.

## Releasing

Versions are `major.minor.patch`, each part starting at 0: major = new features, minor = page improvements and adjustments, patch = maintenance and bug fixes. Guild data (rounds, roster, scans) is written straight to the database and isn't a release.

1. On the `release/vX.Y.Z` branch: audit that the artifact's files and rules match the last release on `main`.
2. Add the release to `app/changelog.json` (one entry for the whole batch) and bump the version check in `tests/run.py`.
3. Run the tests (`tests/run_all.sh`); share screenshots and get Daby's OK.
4. Publish `app/` files to the artifact; confirm each file's sha256 matches.
5. Commit as "Release vX.Y.Z", fast-forward `main`, push. Add the entry to `docs/CHANGELOG.md` (and the project copy).
6. Daby tags the release on GitHub (`vX.Y.Z` on that commit).

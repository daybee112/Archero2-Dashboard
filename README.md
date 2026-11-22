# ArchAcademy Dashboard

Guild dashboard for the Archero 2 guild **ArchAcademy**: roster, inventories and builds, Training Ground, and Guild Expedition planning and results.

- **Live dashboard:** https://claude.ai/artifact/MaDLSLGhDxJPiPJcWeJ4si (a claude.ai artifact, slug `a699eb5d-8093-41f9-a74f-b4e8d5d70341`)
- **Release history:** git tags (`v7.3.0`, `v8.0.0`, …) and [`docs/CHANGELOG.md`](docs/CHANGELOG.md)

## Layout

| Path | What it is |
|---|---|
| `app/` | Exactly the files published to the artifact: `index.html` (the whole app), `changelog.json` (release notes shown by the version badge), `build-data.json` (game reference data), and the seed data files |
| `tools/` | Generators for the seed data (`make_expedition.py`, `make_seed.py`), the officer messages in `briefs/`, and the tracker sheet export |
| `tests/` | Headless browser tests (Playwright + Chrome) with a mock of the artifact runtime (`mock.js`) |
| `data/db-exports/` | Snapshots of the live shared database, one folder per export |
| `docs/` | Release log (`CHANGELOG.md`) |

## The live database

The shared database lives inside the artifact (that's what members' dashboards read and write), not in this repo. It's backed up here in `data/db-exports/` at each sync. Permission rules are declared on the artifact and can't currently be changed from Claude, so members can only write their private `data/users/<id>` area and their own `presets/<id>` records; officers can write everything else.

## Releasing

Versions are `major.minor.patch`, each part starting at 0: major = new features, minor = page fixes and improvements, patch = data-only changes.

1. Audit: the artifact's files and rules match the last tag.
2. Add the release to `app/changelog.json` and bump the version check in `tests/run.py`.
3. Run the tests (`tests/run_all.sh`).
4. Publish `app/` files to the artifact; confirm each file's sha256 matches.
5. Commit, tag `vX.Y.Z`, push. Add the entry to `docs/CHANGELOG.md`.

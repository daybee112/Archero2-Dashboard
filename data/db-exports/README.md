Snapshots of the live shared database (db_list of each collection), one folder per export: YYYY-MM-DD/<collection>.json.

Each file is a list of `{id, updatedAt, version, data}`. Empty collections aren't written. Private areas (`data/users/<id>/…`) can't be read by anyone else, so they're never exported.

| Export | Contents |
|---|---|
| 2026-11-22 | Before v8.0.0: `audit` (1 officer, 6 entries), `presets` (1 member: link + shared inventory), `roster` (2 officer edits: daybee, Hago26). Nothing else in the database yet; Expedition data was still in the seed files. |

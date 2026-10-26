---
id: TP-15
title: Automate validate-then-insert into the DB (make db-insert)
status: In Review
assignee: []
created_date: '2026-10-24 12:00'
updated_date: '2026-10-24 12:00'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Automate inserting a training file into the database after it validates. Add a
make goal that processes `data.txt` (validate, then insert into the DB). The
check is that parsing must finish successfully (exit code 0): the DB is only
updated when the file validates, so the goal can gate automation.

The reusable parse -> serialize (validate against the JSON schema) ->
upsert-into-database pipeline is extracted into `src/bulk_export.py` and shared
by both the bulk-export CLI and the single-file insert CLI, so no parse/validate/
insert logic is duplicated.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `make db-insert` processes data.txt (override with FILE= / DB_FILE=)
- [x] #2 A file is inserted into the DB only after it validates
- [x] #3 Success exits 0; a missing/invalid file exits non-zero and leaves the DB untouched
- [x] #4 Re-running on the same file upserts (no duplicate entries)
- [x] #5 The pipeline library lives in src/ and is reused by both entry points
- [x] #6 Tests cover valid insert, per-session workouts, rerun upsert, invalid/missing file
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- `src/bulk_export.py`: the reusable library (session splitting/parsing,
  output-stem assignment, set-/bench-centric export, database upsert) plus a
  `run()` orchestration returning 0 on success and non-zero when any input is
  missing or fails to parse/validate. Only validated sessions are written.
- `bin/bulk_export.py`: thin CLI over `src.bulk_export.run` (used by
  `bin/parse_bulk.sh`).
- `bin/insert_data_to_db.py`: thin CLI over the same library, adding the
  `data.txt` / `<output-dir>/database.json` defaults for `make db-insert`.
- `Makefile`: `db-insert` goal (`FILE?=data.txt`, `DB_FILE?=data/parsed/database.json`).
- Tests: `tests/test_db_insert.py`; `tests/test_bulk_parser.py` still exercises
  `bin/bulk_export.py` end to end.
- In review in PR #26.
<!-- SECTION:NOTES:END -->

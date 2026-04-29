---
id: TP-5
title: Envelope the payload JSONs with the type and schema
status: Completed
assignee: []
created_date: '2026-04-29 09:29'
completed_date: '2026-04-29 13:35'
labels: [envelope, validation, json-schema]
dependencies: []
---

## Summary

Implemented envelope pattern for wrapping workout data payloads with schema metadata.

## Details

See: `backlog/docs/TP-5-envelope-pattern.md`

## Completion

- ✅ Envelope structure implemented (type, schema, payload)
- ✅ Python module with Envelope class
- ✅ wrap_payload() and unwrap_and_validate() functions
- ✅ CLI tool (envelope_tool.py) with wrap/unwrap/validate/convert commands
- ✅ Schema files for envelope validation
- ✅ Validation scripts for both formats
- ✅ Example data updated with envelope structure
- ✅ Tests updated and passing
- ✅ Comprehensive documentation
- ✅ All pre-commit checks passing
- ✅ Rebased on origin/master
- ✅ Pushed to remote

**Commit**: a84aa8a - feat: implement envelope pattern for set-centric and bench-centric data

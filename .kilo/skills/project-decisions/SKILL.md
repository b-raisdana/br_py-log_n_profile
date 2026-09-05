---
name: project-decisions
description: Use for any of — adding a new module/file under the package, placing code under br_py_log_n_profile/, reviewing a layer boundary, or deciding what test type a change needs. One skill, several independent sections — read only the one(s) that match.
---

# Project decisions

## Package layout

Trigger: adding a module/file under `br_py_log_n_profile/`, or reviewing a layer boundary.

Layers:
1. `do_log/` — logging facade, ray IDs, stdlib interception
2. `profiling/` — timing decorators and parameter stringification
3. Future: `tracing/` — OpenTelemetry spans and metrics

Placing new code:
- Pure logging/tracing/profile logic → appropriate sub-package
- Re-exports for backward compat → `__init__.py`

## Test strategy

Trigger: deciding what test type a change needs.

| change is...                                                             | write a...                                                             | marker             |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------- | ------------------ |
| pure function, no I/O (logging format, profile timing)                   | unit test, synthetic in-memory fixture                                 | `unit`             |
| validating the public API contract when installed as a package           | contract test                                                          | `contract`         |
| wiring modules together (log + ray_id + profile together)                | integration test                                                       | `integration`      |
| fixing a bug / protecting an invariant that broke before                 | regression test, named after the invariant, not the ticket             | `regression`       |
| broad "does it still work" check, safe every commit                      | smoke test                                                             | `smoke`            |

## Brief comments

proper naming is always the first choice
a comment just allowed if what it says is not understandable from the name of nearby method and method arguments and requires to add real knowledge and do what is impossible by using proper naming.

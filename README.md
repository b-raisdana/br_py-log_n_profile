# br_logging_and_profiling

Reusable logging/profiling/tracing package extracted from Forecasting-sidecar3.

## Current state

- Logging: Loguru + colorama via `br_py_log_n_profile.do_log.log_it`
- Profiling: `profile_it` decorator (wall-clock timing, colored console output)
- Correlation IDs: `ray_id` via `contextvars.ContextVar`

## Planned

- `tracing/` module: `init_tracing()`, `traced` decorator (OTel span replacement for `profile_it`), `@counted`/`@timed_metric` for hot-loop metrics
- Backend: Prometheus + Jaeger + Grafana + OTel Collector
- Migration phases: Phase 0 (deps/config) → Phase 1 (core tracing) → Phase 2 (migrate by layer) → Phase 3 (metrics) → Phase 4 (backend stack)

## Install

```bash
pip install br-logging-and-profiling
```

## Development

Clone with submodules, or initialize the shared pre-commit tooling after cloning:

```bash
git submodule update --init --recursive
pip install -r requirements-dev.txt
bash br_pre_commit/install.sh "$PWD"
./pre-commit
pytest -m unit
```

The pre-commit gate runs strict mypy against `examples/`, including the `profile_it` type-preservation example.

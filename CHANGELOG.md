# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-05

### Added

- Initial package structure extracted from Forecasting-sidecar3
- `br_py_log_n_profile.do_log.log_it` — Loguru-based logging facade with Loguru + colorama + stdlib interception
- `br_py_log_n_profile.do_log.ray_id` — ContextVar-based correlation ID
- `br_py_log_n_profile.profiling.base` — `profile_it` timing decorator
- Package-level re-exports in `br_py_log_n_profile.__init__`
- pyproject.toml with ruff/mypy/pytest config
- Pre-commit hooks (ruff, mypy, pytest, skill-file sync)
- Incremental ratchet gate for mypy/ruff/loc
- Contract tests for public API surface

# Changelog

## [0.5.0] - 2026-09-09

### Added

-

### Changed

-

### Fixed

-

## [0.4.0] - 2026-09-08

### Added

-

### Changed

-

### Fixed

-

## [0.3.0] - 2026-09-08

### Added

-

### Changed

-

### Fixed

-

## [0.2.1] - 2026-09-08

### Added

-

### Changed

-

### Fixed

-

## [0.2.0] - 2026-09-06

### Added

-

### Changed

-

### Fixed

-

## [0.1.1] - 2026-09-05

### Added

-

### Changed

-

### Fixed

-

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-05

### Added

- Initial package structure extracted from Forecasting-sidecar3/app/helper/logging/
- `br_py_log_n_profile.do_log.log_it` — Loguru-based logging facade with Loguru + colorama + stdlib `logging` interception
- `br_py_log_n_profile.do_log.ray_id` — ContextVar-based correlation ID (`get_ray_id`, `set_ray_id`, `ray_id`)
- `br_py_log_n_profile.profiling.base` — `profile_it` timing decorator with color-coded duration buckets
- Package-level re-exports in `br_py_log_n_profile.__init__` preserving the legacy `helper.logging` public surface
- pyproject.toml with ruff/mypy/pytest config matching Forecasting-sidecar3 standards
- Pre-commit hooks (ruff format/lint, mypy, pytest unit gate, skill-file sync)
- Incremental ratchet gate for mypy/ruff/loc
- Contract tests validating installed package public API surface
- Compatibility shims in Forecasting-sidecar3/app/helper/logging/ re-exporting from installed package
- Wheel/sdist build artifacts in `dist/`

### Changed

- Forecasting-sidecar3 `app/helper/logging/` modules now re-export from `br_py_log_n_profile` instead of containing original implementations
- All legacy import paths (`from helper.logging import ...`, `from helper.logging.do_log import ...`, etc.) continue to work unchanged
- Forecasting-sidecar3 `pytest.ini` registers `contract` marker for new contract tests

### Fixed

- numpy constraint pinned to `<2.2` for TensorFlow 2.19.0 compatibility

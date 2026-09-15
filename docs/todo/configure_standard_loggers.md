# Configure Standard Loggers to Use Custom Logging Infrastructure

## Problem

`logging.getLogger(__name__)` creates child loggers that inherit the root logger's level (default WARNING). Messages from named loggers are filtered before reaching `InterceptHandler`, so DEBUG/INFO calls never appear in loguru output.

## Solution

Add `level=logging.DEBUG` to `logging.basicConfig()` in `_intercept_stdlib_logging()`.

### Change

`br_py_log_n_profile/do_log/log_it.py:70`

```python
# Before
logging.basicConfig(handlers=[InterceptHandler()], force=True)

# After
logging.basicConfig(handlers=[InterceptHandler()], force=True, level=logging.DEBUG)
```

### Effect

- Root logger accepts all levels (DEBUG and above)
- Named loggers (`logging.getLogger(__name__)`) propagate to root, where `InterceptHandler` routes through loguru
- Standard library loggers and third-party loggers also flow through the same pipeline
- No behavior change for explicit `log_d`, `log_i`, `log_w`, `log_e`, `log_exception` calls (they bypass stdlib logging)

### Verification

- `pytest tests/unit/br_py_log_n_profile/do_log/test_log_it.py`
- `pytest tests/unit/br_py_log_n_profile/profiling/test_base.py`

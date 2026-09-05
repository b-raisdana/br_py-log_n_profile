---
name: pytest
description: Use whenever writing, running, or debugging a pytest test in this repo. Covers how to actually execute tests here, plus repo conventions for markers, fixtures, and structure. Load test-strategy first to pick the right test type before using this skill to write it.
---

# pytest (this repo)

## Running tests

```bash
pytest -m unit
```

Fast gate (every commit): `pytest -m unit`. Full run (nightly/manual, includes integration, `e2e`, and `perf`): `pytest`.

## Performance budget

- Unit tests (pre-commit): each individual test must complete in under 500 ms. Any test exceeding this budget belongs in `integration/`.
- Integration tests (pre-push): each individual test must complete in under 5 s. Any test exceeding this budget belongs in `e2e/` or `perf/`.

## Repo config

`pytest.ini` (repo root): `testpaths = tests`, `pythonpath = .` (so absolute imports resolve), `--import-mode=importlib`, `--strict-markers`. Registered markers: `unit`, `integration`, `contract` — `--strict-markers` makes an unregistered marker an authoring error.

## Directory layout

```
pytest.ini                      # repo root: markers, testpaths, pythonpath
tests/
  conftest.py                 # shared fixtures
  unit/<mirrors package path>/test_<module>.py
  integration/<mirrors package path>/test_<flow>.py
```

## Structure: Arrange-Act-Assert

```python
def test_something(simple_fixture):
    # Arrange
    data = simple_fixture
    # Act
    result = do_something(data)
    # Assert
    assert result == expected
```

One assertion focus per test.

## Fixtures

Shared fixtures go in `tests/conftest.py` as factory fixtures (a fixture that returns a function, so each test controls size/shape).

## Naming

`test_<unit>_<state_under_test>_<expected_result>` where the state/expected fit on one line.

## Parametrize over copy-pasted near-duplicates

```python
@pytest.mark.parametrize("input,expected", [(1, 2), (2, 4)])
def test_double(input, expected):
    assert double(input) == expected
```

Reach for this the moment two test functions differ only in literals.

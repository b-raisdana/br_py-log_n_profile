import logging
import sys
from pathlib import Path

import pytest
from loguru import logger

# Ensure br_py_log_n_profile is importable even when not installed as a package
# (e.g. during local development before pip install -e .)
_pkg_root = Path(__file__).resolve().parents[2] / "br_py-log_n_profile"
if _pkg_root.exists() and str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from br_py_log_n_profile import (  # noqa: E402
    get_ray_id,
    log,
    profile_it,
    set_ray_id,
)
from br_py_log_n_profile.do_log.log_it import _nearest_level_name  # noqa: E402
from br_py_log_n_profile.profiling.base import parameters_to_str  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_loguru():
    logger.remove()
    logger.add(sys.stdout, format="{message}", colorize=False, level="DEBUG")
    yield
    logger.remove()


@pytest.fixture(autouse=True)
def _reset_ray_id():
    set_ray_id.__self__.set(None) if hasattr(set_ray_id, "__self__") else None
    ctx_var = get_ray_id.__globals__.get("ray_id_var")
    if ctx_var is not None:
        ctx_var.set(None)
    yield
    if ctx_var is not None:
        ctx_var.set(None)


class TestPublicAPISurface:
    @pytest.mark.contract
    def test_top_level_exports(self):
        import br_py_log_n_profile

        for name in ["log_d", "log_e", "log_i", "log_w", "log", "profile_it", "get_ray_id", "set_ray_id"]:
            assert hasattr(br_py_log_n_profile, name), f"missing export: {name}"

    @pytest.mark.contract
    def test_do_log_exports(self):
        from br_py_log_n_profile import do_log

        for name in ["log_d", "log_e", "log_i", "log_w", "log", "get_ray_id", "set_ray_id"]:
            assert hasattr(do_log, name), f"missing do_log export: {name}"

    @pytest.mark.contract
    def test_profiling_exports(self):
        from br_py_log_n_profile import profiling

        assert hasattr(profiling, "profile_it")


class TestNearestLevelName:
    @pytest.mark.contract
    @pytest.mark.parametrize(
        "severity,expected",
        [
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"),
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
            (logging.CRITICAL, "CRITICAL"),
        ],
    )
    def test_standard_levels(self, severity, expected):
        assert _nearest_level_name(severity) == expected

    @pytest.mark.contract
    @pytest.mark.parametrize(
        "severity,expected",
        [
            (25, "INFO"),
            (35, "WARNING"),
            (45, "ERROR"),
            (55, "CRITICAL"),
            (5, "DEBUG"),
            (0, "DEBUG"),
            (-1, "DEBUG"),
        ],
    )
    def test_non_standard_levels(self, severity, expected):
        assert _nearest_level_name(severity) == expected


class TestLogStackTrace:
    def _captured_message(self, **kwargs) -> str:
        sink: list[str] = []
        sink_id = logger.add(sink.append, format="{message}")
        try:
            _level_2(**kwargs)
        finally:
            logger.remove(sink_id)
        return sink[0]

    @pytest.mark.contract
    def test_stack_limit_zero_omits_trace(self):
        message = self._captured_message(stack_limit=0)
        assert 'File "' not in message

    @pytest.mark.contract
    def test_stack_limit_keeps_last_n_frames_nearest_call_site(self):
        message = self._captured_message(stack_limit=2)
        assert message.count('File "') == 2
        assert "in _level_2" in message
        assert "in _level_3" in message

    @pytest.mark.contract
    def test_stack_offset_skips_additional_frames_from_call_site(self):
        message = self._captured_message(stack_limit=1, stack_offset=1)
        assert message.count('File "') == 1
        assert "in _level_2" in message
        assert "in _level_3" not in message


def _level_2(stack_limit, stack_offset=0):
    _level_3(stack_limit, stack_offset)


def _level_3(stack_limit, stack_offset):
    log("boom", logging.ERROR, stack_limit, stack_offset)


class TestProfileItContract:
    @pytest.mark.contract
    def test_profile_it_returns_result(self):
        @profile_it
        def add(a, b):
            return a + b

        assert add(1, 2) == 3

    @pytest.mark.contract
    def test_profile_it_logs_start_and_end(self):
        @profile_it
        def slow():
            pass

        sink: list[str] = []
        sink_id = logger.add(sink.append, format="{message}")
        try:
            slow()
        finally:
            logger.remove(sink_id)
        messages = [s for s in sink if "slow" in s]
        assert any("started" in m for m in messages)
        assert any("executed in" in m for m in messages)

    @pytest.mark.contract
    def test_profile_it_preserves_function_name(self):
        @profile_it
        def my_function():
            pass

        sink: list[str] = []
        sink_id = logger.add(sink.append, format="{message}")
        try:
            my_function()
        finally:
            logger.remove(sink_id)
        assert any("my_function" in s for s in sink)


class TestRayIdContract:
    @pytest.mark.contract
    def test_get_ray_id_generates_when_missing(self):
        rid = get_ray_id(generate=True)
        assert rid is not None

    @pytest.mark.contract
    def test_set_ray_id_roundtrip(self):
        import uuid

        expected = uuid.uuid4()
        set_ray_id(expected)
        assert get_ray_id(generate=False) == expected

    @pytest.mark.contract
    def test_get_ray_id_no_generate_returns_none_when_missing(self):
        ctx_var = get_ray_id.__globals__.get("ray_id_var")
        if ctx_var is not None:
            ctx_var.set(None)
        assert get_ray_id(generate=False) is None


class TestParametersToStrContract:
    @pytest.mark.contract
    def test_dataframe(self):
        import pandas as pd

        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        result = parameters_to_str((df,), {})
        assert "2*" in result
        assert "a" in result

    @pytest.mark.contract
    def test_ndarray(self):
        import numpy as np

        arr = np.zeros((3, 4))
        result = parameters_to_str((arr,), {})
        assert "(3, 4)" in result

    @pytest.mark.contract
    def test_list(self):
        result = parameters_to_str(([1, 2, 3],), {})
        assert "list" in result

    @pytest.mark.contract
    def test_dict(self):
        result = parameters_to_str(({"key": "val"},), {})
        assert "key" in result
        assert "val" in result

    @pytest.mark.contract
    def test_kwargs(self):
        result = parameters_to_str((), {"x": 1, "y": 2})
        assert "x: 1" in result
        assert "y: 2" in result

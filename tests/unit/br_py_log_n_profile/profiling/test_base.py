import inspect

import numpy as np
import pandas as pd
import pytest
from loguru import logger

from br_py_log_n_profile.profiling.base import parameters_to_str, profile_it


@pytest.mark.unit
class TestParametersToStr:
    def test_dataframe(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        result = parameters_to_str((df,), {})
        assert "2*" in result
        assert "a" in result

    def test_ndarray(self):
        arr = np.zeros((3, 4))
        result = parameters_to_str((arr,), {})
        assert "(3, 4)" in result

    def test_list(self):
        result = parameters_to_str(([1, 2, 3],), {})
        assert "list" in result

    def test_dict(self):
        result = parameters_to_str(({"key": "val"},), {})
        assert "key" in result
        assert "val" in result

    def test_kwargs(self):
        result = parameters_to_str((), {"x": 1, "y": 2})
        assert "x: 1" in result
        assert "y: 2" in result


@pytest.mark.unit
class TestProfileIt:
    def test_profile_it_returns_result(self):
        @profile_it
        def add(a, b):
            return a + b

        assert add(1, 2) == 3

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

    def test_profile_it_preserves_signature_without_unwrapping(self):
        @profile_it
        def my_function(first: int, /, second: str, *, enabled: bool = True) -> None:
            pass

        assert inspect.signature(my_function, follow_wrapped=False) == inspect.signature(my_function.__wrapped__)

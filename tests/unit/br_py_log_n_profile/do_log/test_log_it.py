import logging

import pytest
from loguru import logger

from br_py_log_n_profile.do_log.log_it import _nearest_level_name, log, log_exception


@pytest.mark.unit
class TestNearestLevelName:
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


def _level_2(stack_limit, stack_offset=0):
    _level_3(stack_limit, stack_offset)


def _level_3(stack_limit, stack_offset):
    log("boom", logging.ERROR, stack_limit, stack_offset)


@pytest.mark.unit
class TestLogStackTrace:
    def _captured_message(self, **kwargs) -> str:
        sink: list[str] = []
        sink_id = logger.add(sink.append, format="{message}")
        try:
            _level_2(**kwargs)
        finally:
            logger.remove(sink_id)
        return sink[0]

    def test_stack_limit_zero_omits_trace(self):
        message = self._captured_message(stack_limit=0)
        assert 'File "' not in message

    def test_stack_limit_keeps_last_n_frames_nearest_call_site(self):
        message = self._captured_message(stack_limit=2)
        assert message.count('File "') == 2
        assert "in _level_2" in message
        assert "in _level_3" in message

    def test_stack_offset_skips_additional_frames_from_call_site(self):
        message = self._captured_message(stack_limit=1, stack_offset=1)
        assert message.count('File "') == 1
        assert "in _level_2" in message
        assert "in _level_3" not in message


@pytest.mark.unit
class TestLogRaise:
    def _captured_message(self, **kwargs: int) -> str:
        sink: list[str] = []
        sink_id = logger.add(sink.append, format="{message}")
        try:
            with pytest.raises(ValueError):
                _level_2_log_exception(**kwargs)
        finally:
            logger.remove(sink_id)
        return sink[0]

    def test_raises_specified_exception_with_message(self) -> None:
        with pytest.raises(ValueError, match="boom"):
            log_exception("boom", ValueError, stack_limit=0)

    def test_logs_message_at_error_level(self) -> None:
        message = self._captured_message(stack_limit=0)
        assert "boom" in message

    def test_stack_offset_applied_correctly(self) -> None:
        sink: list[str] = []
        sink_id = logger.add(sink.append, format="{message}")
        try:
            with pytest.raises(ValueError):
                _level_2_log_exception(stack_limit=1, stack_offset=1)
        finally:
            logger.remove(sink_id)
        message = sink[0]
        assert message.count('File "') == 1
        assert "in _level_2_log_exception" in message


def _level_2_log_exception(stack_limit: int, stack_offset: int = 0) -> None:
    _level_3_log_exception(stack_limit, stack_offset)


def _level_3_log_exception(stack_limit: int, stack_offset: int) -> None:
    log_exception("boom", ValueError, stack_limit, stack_offset)

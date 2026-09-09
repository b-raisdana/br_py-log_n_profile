from typing import assert_type

from br_py_log_n_profile import profile_it


@profile_it
def format_value(value: int, *, prefix: str = "value") -> str:
    return f"{prefix}={value}"


assert_type(format_value(3), str)
assert_type(format_value(3, prefix="count"), str)

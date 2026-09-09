from importlib.resources import files

import pytest

import br_py_log_n_profile


@pytest.mark.unit
def test_package_declares_inline_typing_support():
    marker = files(br_py_log_n_profile).joinpath("py.typed")

    assert marker.is_file()

import uuid

import pytest

from br_py_log_n_profile.do_log.ray_id import get_ray_id, ray_id, set_ray_id


@pytest.mark.unit
class TestRayId:
    def test_get_ray_id_generates_when_missing(self):
        rid = get_ray_id(generate=True)
        assert rid is not None

    def test_set_ray_id_roundtrip(self):
        expected = uuid.uuid4()
        set_ray_id(expected)
        assert get_ray_id(generate=False) == expected

    def test_get_ray_id_no_generate_returns_none_when_missing(self):
        set_ray_id(None)
        assert get_ray_id(generate=False) is None

    def test_ray_id_factory_returns_provided_id(self):
        expected = uuid.uuid4()
        result = ray_id(source_type=0, id_of_ray=expected)
        assert result == expected

    def test_ray_id_factory_generates_from_source_type(self):
        result = ray_id(source_type=42)
        assert result is not None
        assert isinstance(result, uuid.UUID)

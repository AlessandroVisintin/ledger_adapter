import pytest

from LedgerAdapter.utils import canonicalize_json

class TestDagHashManager:

    def test_canonicalize_key_sorting(self):
        data = {"b": 2, "c": 3, "a": 1}
        expected = '{"a":1,"b":2,"c":3}'
        assert canonicalize_json(data) == expected

    def test_canonicalize_whitespace_removal(self):
        data = {"key1": "value1", "key2": "value2"}
        expected = '{"key1":"value1","key2":"value2"}'
        assert canonicalize_json(data) == expected

    def test_canonicalize_nested_objects(self):
        data = {
            "z": [3, 1, 2],
            "a": {"y": "foo", "x": "bar"}
        }
        expected = '{"a":{"x":"bar","y":"foo"},"z":[3,1,2]}'
        assert canonicalize_json(data) == expected

    def test_canonicalize_unicode(self):
        data = {"text": "café"}
        expected = '{"text":"café"}'
        assert canonicalize_json(data) == expected

    def test_canonicalize_literals(self):
        data = {"active": True, "deleted": False, "metadata": None}
        expected = '{"active":true,"deleted":false,"metadata":null}'
        assert canonicalize_json(data) == expected

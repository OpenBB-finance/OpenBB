"""Query serialization must preserve provider parameter values."""

from copy import deepcopy
from urllib.parse import parse_qs

import pytest

from openbb_core.provider.utils.helpers import get_querystring


@pytest.mark.parametrize("value", ["S&P", "A+B", "São Paulo", "price=close", "#daily"])
def test_values_survive_url_roundtrip(value):
    assert parse_qs(get_querystring({"symbol": value}, [])) == {"symbol": [value]}


def test_repeated_values_and_exclusion_do_not_mutate_input():
    params = {"symbol": ["A&B", "東京"], "internal": "keep", "missing": None}
    original = deepcopy(params)
    assert parse_qs(get_querystring(params, ["internal"])) == {
        "symbol": ["A&B", "東京"]
    }
    assert params == original


def test_empty_query():
    assert get_querystring({"missing": None, "empty": []}, []) == ""

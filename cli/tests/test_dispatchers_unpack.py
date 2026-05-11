"""Tests for openbb_cli.dispatchers._unpack — canonical response unwrapping."""

from __future__ import annotations

import pytest

from openbb_cli.dispatchers._unpack import safe_json_loads, unpack_response

# --- list payloads ---


def test_unpack_response_strips_single_element_list_wrapper():
    rows, metadata = unpack_response([{"a": 1}])
    assert rows == [{"a": 1}]
    assert metadata == {}


def test_unpack_response_recurses_through_single_element_list_of_envelope():
    rows, metadata = unpack_response([{"refRates": [{"x": 1}, {"x": 2}]}])
    assert rows == [{"x": 1}, {"x": 2}]
    assert metadata == {}


def test_unpack_response_keeps_multi_dict_list_as_rows():
    rows, metadata = unpack_response([{"a": 1}, {"b": 2}])
    assert rows == [{"a": 1}, {"b": 2}]
    assert metadata == {}


def test_unpack_response_wraps_array_of_scalars_as_value_rows():
    rows, metadata = unpack_response(["2026-01-01", "2026-01-02"])
    assert rows == [{"value": "2026-01-01"}, {"value": "2026-01-02"}]
    assert metadata == {}


# --- non-dict / scalar payloads ---


def test_unpack_response_wraps_top_level_scalar_as_value_row():
    rows, metadata = unpack_response("plain text")
    assert rows == [{"value": "plain text"}]
    assert metadata == {}


def test_unpack_response_wraps_top_level_int():
    rows, metadata = unpack_response(42)
    assert rows == [{"value": 42}]
    assert metadata == {}


# --- dict payloads ---


def test_unpack_response_strips_single_array_envelope():
    rows, metadata = unpack_response(
        {"refRates": [{"effectiveDate": "2026-04-30", "type": "TGCR"}]}
    )
    assert rows == [{"effectiveDate": "2026-04-30", "type": "TGCR"}]
    assert metadata == {}


def test_unpack_response_splits_array_from_sibling_metadata():
    """Sibling scalar fields surface as metadata."""
    rows, metadata = unpack_response(
        {
            "asOfDate": "2026-04-30",
            "operations": [{"id": 1}, {"id": 2}],
        }
    )
    assert rows == [{"id": 1}, {"id": 2}]
    assert metadata == {"asOfDate": "2026-04-30"}


def test_unpack_response_descends_through_single_key_dict_envelope():
    rows, metadata = unpack_response(
        {"ambs": {"auctions": [{"operationId": "OR1"}, {"operationId": "OR2"}]}}
    )
    assert rows == [{"operationId": "OR1"}, {"operationId": "OR2"}]
    assert metadata == {}


def test_unpack_response_does_not_descend_into_scalar_single_key_value():
    """``{"symbol": "AAPL"}`` is a row dict, not an envelope around ``"AAPL"``."""
    rows, metadata = unpack_response({"symbol": "AAPL"})
    assert rows == [{"symbol": "AAPL"}]
    assert metadata == {}


def test_unpack_response_returns_multi_property_dict_as_single_row():
    rows, metadata = unpack_response({"a": 1, "b": 2})
    assert rows == [{"a": 1, "b": 2}]
    assert metadata == {}


def test_unpack_response_promotes_scalar_array_under_single_key_envelope():
    """Single-key wrapper around an array of strings -> ``{value: x}`` rows."""
    rows, metadata = unpack_response({"asOfDates": ["2026-04-30", "2026-04-23"]})
    assert rows == [{"value": "2026-04-30"}, {"value": "2026-04-23"}]
    assert metadata == {}


def test_unpack_response_returns_empty_when_payload_is_none():
    rows, metadata = unpack_response(None)
    assert rows == [{"value": None}]
    assert metadata == {}


# --- safe_json_loads ---


def test_safe_json_loads_parses_well_formed_payload_directly():
    """Strict ``json.loads`` succeeds on the fast path — no rewrite triggered."""
    assert safe_json_loads('{"a": 1, "b": [2, 3]}') == {"a": 1, "b": [2, 3]}


def test_safe_json_loads_substitutes_bare_asterisk_with_null():
    """NY Fed-style ``"foo": *`` sentinel becomes ``null`` so the rest of
    the payload still parses instead of failing on the first asterisk."""
    text = '{"a": 1, "b": *, "c": [{"d": *}], "e": "kept"}'
    assert safe_json_loads(text) == {
        "a": 1,
        "b": None,
        "c": [{"d": None}],
        "e": "kept",
    }


def test_safe_json_loads_propagates_unfixable_errors():
    """Genuinely malformed JSON (not just bare ``*``) still raises after
    the sanitization fallback — the fallback isn't a magical rescue."""
    with pytest.raises(ValueError):
        safe_json_loads('{"a": ,}')

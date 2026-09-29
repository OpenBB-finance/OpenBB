"""Tests for shared IAPD helpers."""

from __future__ import annotations

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_sec.utils.adviser_info import (
    clean_date,
    clean_int,
    clean_text,
    embedded_object,
    required_text,
)


def test_required_text_raises_on_none() -> None:
    with pytest.raises(OpenBBError, match="missing foo"):
        required_text(None, "foo")


def test_clean_text_raises_on_bool() -> None:
    with pytest.raises(OpenBBError, match="scalar text"):
        clean_text(True)


def test_clean_int_raises_on_bool() -> None:
    with pytest.raises(OpenBBError, match="integer value"):
        clean_int(True)


def test_clean_int_raises_on_non_numeric_string() -> None:
    with pytest.raises(OpenBBError, match="integer value"):
        clean_int("abc")


def test_clean_date_raises_on_invalid_date() -> None:
    with pytest.raises(OpenBBError, match="valid date"):
        clean_date("not-a-date", "%Y-%m-%d")


def test_embedded_object_raises_on_non_string_non_dict() -> None:
    with pytest.raises(OpenBBError, match="must be an object"):
        embedded_object(42, "field")

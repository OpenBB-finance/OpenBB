"""Tests for the shared serialization mixins."""

import pytest
from pydantic import ValidationError

from openbb_government_us.utils.serializers import (
    NULL_TOKENS,
    NullTokenMixin,
    OmitNoneMixin,
    is_null_token,
)


class _Placeholder(NullTokenMixin):
    """Model coercing source placeholder tokens to None."""

    name: str | None = None
    value: float | None = None


class _Pruned(OmitNoneMixin):
    """Model dropping None-valued fields from the served record."""

    name: str | None = None
    value: float | None = None


class TestIsNullToken:
    """Tests for placeholder token detection."""

    def test_recognized_tokens(self):
        """Every catalogued placeholder is detected regardless of case or padding."""
        assert all(is_null_token(f"  {token.upper()} ") for token in NULL_TOKENS)

    def test_real_values_are_not_tokens(self):
        """Real text and non-text values are not placeholders."""
        assert is_null_token("Corn") is False
        assert is_null_token(0) is False
        assert is_null_token(None) is False


class TestNullTokenMixin:
    """Tests for the placeholder coercion validator."""

    def test_placeholder_fields_become_none(self):
        """A '--' cell is coerced to None instead of surfacing as a value."""
        record = _Placeholder.model_validate({"name": "--", "value": None})
        assert record.name is None

    def test_real_values_survive(self):
        """A populated cell is left untouched."""
        record = _Placeholder.model_validate({"name": "Corn", "value": 1.5})
        assert record.name == "Corn"
        assert record.value == 1.5

    def test_non_mapping_input_is_left_for_pydantic_to_reject(self):
        """A non-mapping payload has no cells to coerce and is rejected as-is."""
        with pytest.raises(ValidationError, match="should be a valid dictionary"):
            _Placeholder.model_validate(["Corn"])


class TestOmitNoneMixin:
    """Tests for the None-dropping serializer."""

    def test_none_fields_are_dropped(self):
        """Unpopulated fields are absent from the record, not served as null."""
        assert _Pruned.model_validate({"name": "Corn"}).model_dump() == {"name": "Corn"}

    def test_placeholder_coercion_still_applies(self):
        """A placeholder cell is coerced to None and then dropped."""
        assert _Pruned.model_validate({"name": "n/a", "value": 2.0}).model_dump() == {
            "value": 2.0
        }

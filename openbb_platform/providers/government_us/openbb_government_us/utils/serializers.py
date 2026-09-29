"""Shared serialization helpers."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from pydantic import model_serializer, model_validator

NULL_TOKENS = frozenset(
    {"", "-", "--", "---", "----", "n/a", "na", "null", "none", "nan"}
)


def is_null_token(value: Any) -> bool:
    """Return whether a value is a source placeholder standing in for null."""
    return isinstance(value, str) and value.strip().casefold() in NULL_TOKENS


class NullTokenMixin(Data):
    """Mixin that coerces source placeholder tokens to None before validation.

    Source files use placeholder tokens such as '--' or blank cells where a
    value does not apply; these are coerced to None so they never surface as
    row values. The coercion runs in a before-validator, which leaves the
    model's field schema intact so column definitions still generate.
    """

    @model_validator(mode="before")
    @classmethod
    def _null_placeholder_tokens(cls, data: Any) -> Any:
        """Coerce placeholder tokens to None before validation."""
        if isinstance(data, dict):
            return {
                key: (None if is_null_token(value) else value)
                for key, value in data.items()
            }
        return data


class OmitNoneMixin(NullTokenMixin):
    """Mixin that also drops None fields from the serialized record.

    Models covering many source tables in one schema leave most fields
    unpopulated for any single table; dropping the None-valued fields keeps
    them out of the response entirely. This replaces the serialized schema
    with a free-form object, so a model using it cannot also carry column
    definitions; use it only where per-table column pruning matters more than
    column presentation.
    """

    @model_serializer(mode="wrap")
    def _serialize(self, handler) -> dict[str, Any]:
        """Drop keys whose value is None."""
        return {k: v for k, v in handler(self).items() if v is not None}

"""Test OptionsChainsData JSON Schema override."""

import json
from datetime import date

import pytest
from openbb_core.provider.standard_models.options_chains import OptionsChainsData


def test_options_chains_schema_is_array_of_records():
    """Verify that the JSON Schema for OptionsChainsData is array-of-records, not columnar."""
    schema = OptionsChainsData.model_json_schema()

    # The schema should be an array type
    assert schema["type"] == "array", "Top-level schema should be array"

    # Items should be object type (records)
    assert schema["items"]["type"] == "object", "Items should be objects (records)"

    # Items should have properties matching the columnar fields
    props = schema["items"]["properties"]
    assert "contract_symbol" in props
    assert "strike" in props
    assert "expiration" in props
    assert "option_type" in props

    # Field types should be scalars, not arrays
    assert props["contract_symbol"]["type"] == "string"
    assert props["strike"]["type"] == "number"
    assert props["expiration"]["type"] == "string"
    assert props["option_type"]["type"] == "string"

    # Required fields should be present
    required = schema["items"].get("required", [])
    assert "contract_symbol" in required
    assert "expiration" in required
    assert "strike" in required


def test_options_chains_serialization_matches_schema():
    """Verify that serialized data matches the schema shape (list of records)."""
    # Create a minimal instance
    data = OptionsChainsData(
        contract_symbol=["SPY250117C00500000", "SPY250117P00500000"],
        expiration=[date(2025, 1, 17), date(2025, 1, 17)],
        strike=[500.0, 500.0],
        option_type=["call", "put"],
        underlying_symbol=["SPY", "SPY"],
        underlying_price=[550.0, 550.0],
        dte=[10, 10],
    )

    # Serialize using model_dump with mode='json' to trigger model_serializer
    serialized = data.model_dump(mode="json")

    # Should be a list
    assert isinstance(serialized, list)
    assert len(serialized) == 2

    # Each item should be a dict (record)
    assert isinstance(serialized[0], dict)
    assert isinstance(serialized[1], dict)

    # Records should have scalar values, not lists
    assert serialized[0]["contract_symbol"] == "SPY250117C00500000"
    assert serialized[0]["strike"] == 500.0
    assert serialized[0]["option_type"] == "call"

    assert serialized[1]["contract_symbol"] == "SPY250117P00500000"
    assert serialized[1]["option_type"] == "put"


def test_options_chains_schema_preserves_metadata():
    """Verify that field metadata (description, x-unit_measurement) is preserved in schema."""
    schema = OptionsChainsData.model_json_schema()
    props = schema["items"]["properties"]

    # Check description preservation
    assert "description" in props["strike"]
    assert "Strike price" in props["strike"]["description"]

    # Check x-unit_measurement preservation
    assert props["strike"].get("x-unit_measurement") == "currency"
    assert props["implied_volatility"].get("x-unit_measurement") == "decimal"

    # Check x-frontend_multiply preservation
    assert props["change_percent"].get("x-frontend_multiply") == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

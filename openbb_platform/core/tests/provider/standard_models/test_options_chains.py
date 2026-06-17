"""Tests for options chains serialization and schema shape."""

from datetime import date, datetime

from fastapi import FastAPI

from openbb_core.app.model.obbject import OBBject
from openbb_core.provider.standard_models.options_chains import OptionsChainsData


def _sample_payload() -> dict:
    return {
        "underlying_symbol": ["FAKE", "FAKE"],
        "underlying_price": [100.0, 100.0],
        "contract_symbol": ["FAKE240117C00100000", "FAKE240117P00100000"],
        "expiration": [date(2030, 1, 17), date(2030, 1, 17)],
        "strike": [100.0, 100.0],
        "option_type": ["call", "put"],
        "open_interest": [10, 5],
        "volume": [100, 50],
        "bid": [1.5, 1.4],
        "ask": [1.6, 1.5],
        "last_trade_time": [datetime(2026, 1, 1, 15, 30), datetime(2026, 1, 1, 15, 31)],
    }


def test_options_chains_model_dump_is_row_records() -> None:
    data = OptionsChainsData(**_sample_payload())
    dumped = data.model_dump()

    assert isinstance(dumped, list)
    assert len(dumped) == 2
    assert dumped[0]["option_type"] == "call"
    assert dumped[1]["option_type"] == "put"
    assert isinstance(dumped[0]["last_trade_time"], str)


def test_options_chains_json_schema_is_array_of_rows() -> None:
    schema = OptionsChainsData.model_json_schema()

    assert schema["type"] == "array"
    assert schema["items"]["type"] == "object"

    strike_types = {
        entry.get("type") for entry in schema["items"]["properties"]["strike"]["anyOf"]
    }
    assert "number" in strike_types
    assert "null" in strike_types


def test_fastapi_openapi_results_references_row_schema() -> None:
    app = FastAPI()

    @app.get("/chains")
    def chains() -> OBBject[OptionsChainsData]:
        return OBBject(results=[])

    openapi = app.openapi()
    components = openapi["components"]["schemas"]

    assert components["OptionsChainsData"]["type"] == "array"

    route_schema = openapi["paths"]["/chains"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    wrapper_name = route_schema["$ref"].rsplit("/", 1)[-1]
    results_schema = components[wrapper_name]["properties"]["results"]
    refs = [
        entry.get("$ref")
        for entry in results_schema.get("anyOf", [results_schema])
        if entry.get("$ref")
    ]
    assert any(ref.endswith("OptionsChainsData") for ref in refs)

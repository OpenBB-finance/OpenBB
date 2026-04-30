"""Tests for ``OptionsChainsData`` — pure-Python serializer + OpenAPI schema fidelity.

These tests intentionally avoid pandas. They exercise the column→row
``@model_serializer`` and the ``__get_pydantic_json_schema__`` override that
keeps the OpenAPI document in sync with the actual JSON wire response.
"""

import json
from datetime import date, datetime

import pytest

from openbb_core.app.model.obbject import OBBject
from openbb_core.provider.standard_models.options_chains import OptionsChainsData


@pytest.fixture
def sample_payload() -> dict:
    """Smallest realistic payload — 2 rows, 1 expiration, 1 strike, call/put."""
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


class TestModelSerializer:
    """Cover ``OptionsChainsData.model_serialize`` row-record output."""

    def test_model_dump_returns_list_of_records(self, sample_payload):
        """``model_dump()`` flips column-oriented fields into row records."""
        data = OptionsChainsData(**sample_payload)
        dumped = data.model_dump()

        assert isinstance(dumped, list)
        assert len(dumped) == 2
        assert isinstance(dumped[0], dict)
        assert dumped[0]["strike"] == 100.0
        assert dumped[0]["option_type"] == "call"
        assert dumped[1]["option_type"] == "put"

    def test_datetime_fields_are_stringified(self, sample_payload):
        """The ``isinstance(value[0], datetime)`` branch stringifies datetimes."""
        data = OptionsChainsData(**sample_payload)
        dumped = data.model_dump()

        # last_trade_time was a datetime list — should appear as a string.
        assert isinstance(dumped[0]["last_trade_time"], str)
        assert "2026-01-01" in dumped[0]["last_trade_time"]

    def test_empty_list_fields_are_dropped(self, sample_payload):
        """Fields whose list is empty are excluded from row records."""
        data = OptionsChainsData(**sample_payload)
        dumped = data.model_dump()

        # ``mark`` and ``rho`` were not provided — they default to []
        # and the ``if value:`` guard drops them from every row.
        assert "mark" not in dumped[0]
        assert "rho" not in dumped[0]

    def test_single_row_payload(self):
        """A 1-row payload produces a 1-element list, not a scalar dict."""
        data = OptionsChainsData(
            contract_symbol=["FAKE"],
            expiration=[date(2030, 1, 17)],
            strike=[100.0],
            option_type=["call"],
        )
        dumped = data.model_dump()
        assert len(dumped) == 1
        assert dumped[0]["strike"] == 100.0

    def test_model_dump_json_roundtrip(self, sample_payload):
        """``model_dump_json`` → ``json.loads`` reproduces the row records."""
        data = OptionsChainsData(**sample_payload)
        text = data.model_dump_json()
        parsed = json.loads(text)

        assert isinstance(parsed, list)
        assert len(parsed) == 2
        assert parsed[0]["strike"] == 100.0
        assert parsed[1]["option_type"] == "put"

    def test_record_keys_match_provided_columns(self, sample_payload):
        """Every record carries exactly the columns that were provided."""
        data = OptionsChainsData(**sample_payload)
        dumped = data.model_dump()

        provided_keys = set(sample_payload.keys())
        for row in dumped:
            assert set(row.keys()) == provided_keys

    def test_expiration_validator_accepts_datetime_list(self, sample_payload):
        payload = dict(sample_payload)
        payload["expiration"] = [datetime(2030, 1, 17), datetime(2030, 1, 17)]

        data = OptionsChainsData(**payload)
        dumped = data.model_dump()

        assert dumped[0]["expiration"] == date(2030, 1, 17)

    def test_expiration_validator_accepts_string_list(self, sample_payload):
        payload = dict(sample_payload)
        payload["expiration"] = ["2030-01-17", "2030-01-17"]

        data = OptionsChainsData(**payload)
        dumped = data.model_dump()

        assert dumped[0]["expiration"] == date(2030, 1, 17)


class TestOpenAPISchema:
    """Cover the ``__get_pydantic_json_schema__`` override on ``OptionsChainsData``.

    The override exists because Pydantic's default schema is generated from
    field annotations (column-of-lists), but the wire response is row-shaped.
    Without the override the OpenAPI document would lie to clients.
    """

    def test_top_level_schema_is_array(self):
        """The model's own JSON schema describes an ``array``."""
        schema = OptionsChainsData.model_json_schema()
        assert schema["type"] == "array"
        assert "items" in schema

    def test_items_is_object_with_scalar_fields(self):
        """Each item is an object whose fields are scalars, not lists."""
        schema = OptionsChainsData.model_json_schema()
        items = schema["items"]
        assert items["type"] == "object"
        props = items["properties"]

        # ``strike`` was annotated ``list[float]`` on the model — the schema
        # for a single record should describe it as a number-or-null scalar.
        strike = props["strike"]
        assert "anyOf" in strike
        types = {entry.get("type") for entry in strike["anyOf"]}
        assert "number" in types
        assert "null" in types

        # ``option_type`` was ``list[str]`` — should now be string-or-null.
        opt_type = props["option_type"]
        types = {entry.get("type") for entry in opt_type["anyOf"]}
        assert "string" in types

    def test_field_descriptions_propagate_to_row_schema(self):
        """Per-field ``description`` survives the row-rewrite."""
        schema = OptionsChainsData.model_json_schema()
        props = schema["items"]["properties"]
        assert props["strike"]["description"] == "Strike price of the contract."
        assert (
            props["underlying_price"]["description"] == "Price of the underlying stock."
        )

    def test_json_schema_extra_propagates_to_row_schema(self):
        """``json_schema_extra`` (e.g. ``x-unit_measurement``) survives."""
        schema = OptionsChainsData.model_json_schema()
        props = schema["items"]["properties"]
        assert props["strike"]["x-unit_measurement"] == "currency"
        assert props["underlying_price"]["x-unit_measurement"] == "currency"
        assert props["change_percent"]["x-unit_measurement"] == "percent"
        assert props["change_percent"]["x-frontend_multiply"] == 100

    def test_datetime_fields_become_string_in_schema(self):
        """Datetime fields are stringified by the serializer; schema must agree."""
        schema = OptionsChainsData.model_json_schema()
        props = schema["items"]["properties"]
        # ``last_trade_time`` is ``list[datetime | None]`` on the model.
        types = {entry.get("type") for entry in props["last_trade_time"]["anyOf"]}
        assert "string" in types

    def test_fastapi_openapi_advertises_array_response(self):
        """Mounted on a FastAPI route, the OpenAPI doc reports ``type: array``.

        This is the user-visible contract: every API consumer that reads
        ``openapi.json`` will see the row-oriented shape that matches the
        actual JSON response, not the column-oriented internal storage.
        """
        from fastapi import FastAPI

        app = FastAPI()

        @app.get("/chains")
        def chains() -> OBBject[OptionsChainsData]:  # pragma: no cover - schema-only
            ...

        schema = app.openapi()
        components = schema["components"]["schemas"]
        assert "OptionsChainsData" in components
        component = components["OptionsChainsData"]

        assert component["type"] == "array"
        assert component["items"]["type"] == "object"

        # Drill into the response content schema for completeness.
        path = schema["paths"]["/chains"]["get"]
        response_schema = path["responses"]["200"]["content"]["application/json"][
            "schema"
        ]
        # The response is wrapped in ``OBBject`` whose ``results`` field
        # references ``OptionsChainsData``. Resolve that ref and verify.
        ref = response_schema["$ref"]
        wrapper_name = ref.rsplit("/", 1)[-1]
        wrapper = components[wrapper_name]
        results_schema = wrapper["properties"]["results"]
        # ``results`` is ``OBBject[T]``'s ``T | None`` — anyOf {ref, null}.
        refs = [
            entry.get("$ref")
            for entry in results_schema.get("anyOf", [results_schema])
            if entry.get("$ref")
        ]
        assert any(r and r.endswith("OptionsChainsData") for r in refs)

    def test_row_schema_field_set_pins_serializer_contract(self):
        """Snapshot guard: every model field appears in the row schema.

        If a future field is added to ``OptionsChainsData`` without being
        considered by the serializer / schema override, this regression
        guard fires.
        """
        schema = OptionsChainsData.model_json_schema()
        row_props = set(schema["items"]["properties"].keys())
        model_fields = set(OptionsChainsData.model_fields.keys())
        assert row_props == model_fields, (
            f"Row schema fields drifted from model fields. "
            f"Missing from row: {model_fields - row_props}; "
            f"Extra in row: {row_props - model_fields}"
        )


def test_options_chains_data_constructs_without_pandas(monkeypatch):
    """The model must be importable and constructible with pandas absent.

    Only the ``dataframe`` analytics surface requires the ``[pandas]`` extra —
    the model itself, its serializer, and its JSON schema must work in core.
    """
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pandas" or name.startswith("pandas."):
            raise ImportError("No module named 'pandas'")
        if name == "numpy" or name.startswith("numpy."):
            raise ImportError("No module named 'numpy'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    data = OptionsChainsData(
        contract_symbol=["FAKE"],
        expiration=[date(2030, 1, 17)],
        strike=[100.0],
        option_type=["call"],
    )
    dumped = data.model_dump()
    # ``date`` (not ``datetime``) values pass through unchanged — only the
    # ``isinstance(value[0], datetime)`` branch in ``model_serialize``
    # stringifies, so plain dates remain as ``date`` objects in the dict.
    assert dumped == [
        {
            "contract_symbol": "FAKE",
            "expiration": date(2030, 1, 17),
            "strike": 100.0,
            "option_type": "call",
        }
    ]

    # Schema generation must also work with no pandas installed.
    schema = OptionsChainsData.model_json_schema()
    assert schema["type"] == "array"

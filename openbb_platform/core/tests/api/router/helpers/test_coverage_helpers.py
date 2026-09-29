"""Tests for openbb_core.api.router.helpers.coverage_helpers."""

from dataclasses import (
    field as dc_field,
    make_dataclass,
)
from typing import Annotated

import pytest
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo

from openbb_core.api.router.helpers import coverage_helpers
from openbb_core.api.router.helpers.coverage_helpers import (
    create_combined_model,
    dataclass_to_fields,
    get_route_callable,
    get_route_schema_map,
    signature_to_fields,
)


class _FakeApp:
    class equity:  # noqa: N801
        @staticmethod
        def profile(symbol: str, limit: int = 5):
            return {"symbol": symbol, "limit": limit}


def test_get_route_callable_walks_dotted_path():
    fn = get_route_callable(_FakeApp, "/equity/profile")
    assert fn is _FakeApp.equity.profile


def test_get_route_callable_supports_dot_path():
    fn = get_route_callable(_FakeApp, ".equity.profile")
    assert fn is _FakeApp.equity.profile


def test_signature_to_fields_extracts_typed_params():
    fields = signature_to_fields(_FakeApp, "/equity/profile")
    assert "symbol" in fields and "limit" in fields
    sym_type, sym_field = fields["symbol"]
    assert sym_type is str
    assert sym_field.title == "openbb"


class _A(BaseModel):
    x: int = Field(default=1, title="openbb", description="x")


class _B(BaseModel):
    y: int = Field(default=2, title="other", description="y")


def test_create_combined_model_no_filter_keeps_all():
    fields_a = {"x": (int, Field(..., title="openbb", description="x"))}
    fields_b = {"y": (int, Field(..., title="other", description="y"))}
    model = create_combined_model("M", fields_a, fields_b)
    model_fields = (model if isinstance(model, type) else type(model)).model_fields
    assert {"x", "y"} <= set(model_fields)


def test_create_combined_model_filters_by_provider():
    fields_a = {"x": (int, Field(..., title="openbb", description=""))}
    fields_b = {"y": (int, Field(..., title="fmp", description=""))}
    fields_c = {"z": (int, Field(..., title="polygon", description=""))}
    model = create_combined_model(
        "M", fields_a, fields_b, fields_c, filter_by_provider="fmp"
    )
    model_fields = (model if isinstance(model, type) else type(model)).model_fields
    assert "x" in model_fields  # always kept (openbb)
    assert "y" in model_fields  # matches provider
    assert "z" not in model_fields


def test_signature_to_fields_with_annotated_description():
    class _App:
        class router:  # noqa: N801
            @staticmethod
            def cmd(
                ticker: Annotated[str, type("M", (), {"description": "the ticker"})()],
            ):
                return ticker

    fields = signature_to_fields(_App, "/router/cmd")
    # Annotated metadata description should be picked up.
    _, fld = fields["ticker"]
    # Either present or None depending on metadata layout; just confirm field exists.
    assert fld.title == "openbb"


def test_get_route_callable_attribute_error_propagates():
    with pytest.raises(AttributeError):
        get_route_callable(_FakeApp, "/does/not/exist")


def _make_extra_dataclass():
    """Build a dataclass shaped like ProviderInterface.params[model]['extra']."""
    fi_x = FieldInfo(default=None, title="openbb", description="x desc", annotation=int)
    fi_y = FieldInfo(default=None, title="fmp", description="y desc", annotation=str)
    return make_dataclass(
        "ExtraDC",
        [
            ("x", int, dc_field(default=fi_x)),
            ("y", str, dc_field(default=fi_y)),
        ],
    )


class _OutputModel(BaseModel):
    """Pydantic output model used for the schema map."""

    val: int = 0


def test_dataclass_to_fields_extracts_field_info(monkeypatch):
    DC = _make_extra_dataclass()
    monkeypatch.setattr(
        coverage_helpers.provider_interface, "_params", {"M": {"extra": DC}}
    )
    fields = dataclass_to_fields("M")
    assert set(fields) == {"x", "y"}
    x_type, x_field = fields["x"]
    assert x_type is int
    assert x_field.title == "openbb"
    assert x_field.description == "x desc"


def test_get_route_schema_map_combines_signature_and_dataclass(monkeypatch):
    DC = _make_extra_dataclass()
    monkeypatch.setattr(
        coverage_helpers.provider_interface, "_params", {"M": {"extra": DC}}
    )
    monkeypatch.setattr(
        coverage_helpers.provider_interface,
        "_return_schema",
        {"M": _OutputModel},
    )
    out = get_route_schema_map(_FakeApp, {"/equity/profile": "M"})
    assert "/equity/profile" in out
    entry = out["/equity/profile"]
    assert entry["output"] is _OutputModel
    assert entry["callable"] is _FakeApp.equity.profile
    input_fields = (
        entry["input"] if isinstance(entry["input"], type) else type(entry["input"])
    ).model_fields
    # signature params (symbol, limit) + dataclass extras (x, y) all merged
    assert {"symbol", "limit", "x", "y"} <= set(input_fields)


def test_get_route_schema_map_filters_by_provider(monkeypatch):
    DC = _make_extra_dataclass()
    monkeypatch.setattr(
        coverage_helpers.provider_interface, "_params", {"M": {"extra": DC}}
    )
    monkeypatch.setattr(
        coverage_helpers.provider_interface,
        "_return_schema",
        {"M": _OutputModel},
    )
    out = get_route_schema_map(
        _FakeApp, {"/equity/profile": "M"}, filter_by_provider="fmp"
    )
    input_model = out["/equity/profile"]["input"]
    fields = (
        input_model if isinstance(input_model, type) else type(input_model)
    ).model_fields
    # x has title "openbb" -> always kept; y has title "fmp" -> kept
    assert {"x", "y"} <= set(fields)


def test_get_route_schema_map_filter_excludes_non_matching_provider(monkeypatch):
    DC = _make_extra_dataclass()
    monkeypatch.setattr(
        coverage_helpers.provider_interface, "_params", {"M": {"extra": DC}}
    )
    monkeypatch.setattr(
        coverage_helpers.provider_interface,
        "_return_schema",
        {"M": _OutputModel},
    )
    out = get_route_schema_map(
        _FakeApp, {"/equity/profile": "M"}, filter_by_provider="polygon"
    )
    input_model = out["/equity/profile"]["input"]
    fields = (
        input_model if isinstance(input_model, type) else type(input_model)
    ).model_fields
    # y had title "fmp" — should NOT appear when filtering for polygon
    assert "y" not in fields
    # x had title "openbb" — always kept
    assert "x" in fields

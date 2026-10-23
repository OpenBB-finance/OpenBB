"""Tests for AgGrid SSRM request/response models."""

import pytest
from pydantic import BaseModel, ValidationError

from openbb_core.app.model.aggrid import (
    AgFilterModel,
    AgGridRowsRequest,
    AgGridRowsResponse,
    AgGroupingModel,
    AgSortColumn,
)


def test_ag_sort_column_round_trips():
    """``colId``/``sort`` are mandatory; both directions accepted."""
    asc = AgSortColumn(colId="symbol", sort="asc")
    desc = AgSortColumn(colId="market_cap", sort="desc")
    assert asc.colId == "symbol"
    assert desc.sort == "desc"


def test_ag_sort_column_rejects_invalid_direction():
    """``sort`` is constrained to ``Literal["asc", "desc"]``."""
    with pytest.raises(ValidationError):
        AgSortColumn(colId="x", sort="ascending")  # type: ignore[arg-type]


def test_ag_sort_column_rejects_extra_keys():
    """``extra="forbid"`` so the wire format stays tight."""
    with pytest.raises(ValidationError):
        AgSortColumn(colId="x", sort="asc", whoops=True)  # type: ignore[call-arg]


def test_ag_filter_model_allows_extras_for_operator_vocab():
    """ag-grid keeps adding fields like ``filterTo``/``dateFrom``;
    ``extra="allow"`` keeps the model forward-compatible.
    """
    f = AgFilterModel.model_validate(
        {
            "filterType": "number",
            "type": "greaterThan",
            "filter": 100,
            "dateFrom": "2024-01-01",  # extra; should pass through
        }
    )
    assert f.filterType == "number"
    assert f.filter == 100
    # ``extra="allow"`` exposes unknown keys via model_dump
    assert f.model_dump()["dateFrom"] == "2024-01-01"


def test_ag_filter_model_filter_type_constrained():
    """``filterType`` is a Literal — anything outside the set is
    rejected even though we allow extra top-level keys.
    """
    with pytest.raises(ValidationError):
        AgFilterModel(filterType="weird")  # type: ignore[arg-type]


def test_ag_grouping_model_defaults():
    """All collection fields default to empty; ``pivotMode`` defaults
    to False — that's the "no grouping yet" baseline.
    """
    g = AgGroupingModel()
    assert g.rowGroupCols == []
    assert g.valueCols == []
    assert g.pivotCols == []
    assert g.pivotMode is False
    assert g.groupKeys == []


def test_ag_grouping_model_rejects_extras():
    """Tight schema — typos shouldn't silently pass."""
    with pytest.raises(ValidationError):
        AgGroupingModel(typo=True)  # type: ignore[call-arg]


def test_ag_grid_rows_request_minimum_payload():
    """Just ``startRow``/``endRow`` is enough — the rest defaults."""
    r = AgGridRowsRequest(startRow=0, endRow=100)
    assert r.startRow == 0
    assert r.endRow == 100
    assert r.sortModel == []
    assert r.filterModel == {}
    assert r.grouping is None


def test_ag_grid_rows_request_full_payload():
    """A populated payload deserializes nested models correctly."""
    r = AgGridRowsRequest.model_validate(
        {
            "startRow": 0,
            "endRow": 50,
            "sortModel": [{"colId": "date", "sort": "desc"}],
            "filterModel": {
                "symbol": {
                    "filterType": "text",
                    "type": "contains",
                    "filter": "AAPL",
                }
            },
            "grouping": {"groupKeys": ["technology"]},
        }
    )
    assert isinstance(r.sortModel[0], AgSortColumn)
    assert r.sortModel[0].colId == "date"
    assert isinstance(r.filterModel["symbol"], AgFilterModel)
    assert r.filterModel["symbol"].filter == "AAPL"
    assert r.grouping is not None
    assert r.grouping.groupKeys == ["technology"]


def test_ag_grid_rows_request_negative_indices_rejected():
    """``startRow``/``endRow`` are non-negative — ag-grid never sends
    negatives, and a negative would crash slicing on the server.
    """
    with pytest.raises(ValidationError):
        AgGridRowsRequest(startRow=-1, endRow=10)


def test_ag_grid_rows_request_extras_allowed_for_subclass_pattern():
    """``extra="allow"`` lets a subclass add provider-specific filters
    without a schema-level merge step. Direct extras also pass through.
    """
    r = AgGridRowsRequest.model_validate(
        {"startRow": 0, "endRow": 10, "providerToken": "abc"}
    )
    assert r.model_dump()["providerToken"] == "abc"


class _FooRow(BaseModel):
    symbol: str
    price: float


def test_ag_grid_rows_response_generic_parametrization():
    """Generic ``Row`` resolves to the parametrized model and validates
    the items list against it.
    """
    resp = AgGridRowsResponse[_FooRow](
        rowData=[_FooRow(symbol="AAPL", price=150.0)],
        rowCount=1,
    )
    assert resp.rowCount == 1
    assert resp.rowData[0].symbol == "AAPL"


def test_ag_grid_rows_response_rejects_extras():
    """``extra="forbid"`` keeps the wire format predictable for the
    ag-grid client.
    """
    with pytest.raises(ValidationError):
        AgGridRowsResponse[_FooRow](
            rowData=[],
            rowCount=0,
            extra="nope",  # type: ignore[call-arg]
        )


def test_ag_grid_rows_response_negative_count_rejected():
    """``rowCount`` must be non-negative."""
    with pytest.raises(ValidationError):
        AgGridRowsResponse[_FooRow](rowData=[], rowCount=-1)

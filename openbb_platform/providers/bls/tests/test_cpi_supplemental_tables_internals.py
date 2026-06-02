"""Internal-branch tests for ``openbb_bls.models.cpi_supplemental_tables``."""

from __future__ import annotations

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.cpi_supplemental_tables as cst_mod


def test_hdr_helper_returns_widget_config():
    """``_hdr`` returns the bare-headerName widget block."""
    assert cst_mod._hdr("My Col") == {"x-widget_config": {"headerName": "My Col"}}


def test_label_serializer_packs_footnote_when_both_present():
    """``_serialize_label_with_footnote`` returns a dict when both fields exist."""
    record = cst_mod.BlsCpiSupplementalTablesData(
        date=date(2026, 1, 1),
        label="Food",
        footnote="Excludes alcoholic beverages.",
        snapshot_date=date(2026, 1, 1),
        table_key="cpi-u-us",
        table_id="tid",
        table_name="Table",
        sheet="Sheet",
        row_index=1,
    )
    packed = record._serialize_label_with_footnote("Food")
    assert packed == {"value": "Food", "footnote": "Excludes alcoholic beverages."}


def test_label_serializer_returns_bare_value_when_footnote_missing():
    """Without a footnote, the serializer passes the label through unchanged."""
    record = cst_mod.BlsCpiSupplementalTablesData(
        date=date(2026, 1, 1),
        label="Energy",
        snapshot_date=date(2026, 1, 1),
        table_key="cpi-u-us",
        table_id="tid",
        table_name="Table",
        sheet="Sheet",
        row_index=1,
    )
    assert record._serialize_label_with_footnote("Energy") == "Energy"


def test_extract_data_raises_when_explicit_date_yields_no_xlsx(monkeypatch):
    """Explicit ``date`` whose XLSX URL 404s triggers ``OpenBBError``."""
    monkeypatch.setattr(cst_mod, "fetch_xlsx", lambda _stem, _y, _m: None)
    query = cst_mod.BlsCpiSupplementalTablesQueryParams(
        table="cpi-u-us", date=date(2099, 1, 1)
    )
    with pytest.raises(OpenBBError, match="does not publish"):
        cst_mod.BlsCpiSupplementalTablesFetcher.extract_data(query, None)


def test_transform_data_raises_when_rows_empty():
    """``transform_data`` raises ``EmptyDataError`` for empty results."""
    query = cst_mod.BlsCpiSupplementalTablesQueryParams(table="cpi-u-us")
    with pytest.raises(EmptyDataError, match="No rows parsed"):
        cst_mod.BlsCpiSupplementalTablesFetcher.transform_data(query, [])

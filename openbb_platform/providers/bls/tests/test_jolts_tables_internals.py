"""Internal-branch tests for ``openbb_bls.models.jolts_tables``."""

from __future__ import annotations

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.jolts_tables as jt_mod


def test_extract_data_raises_for_unknown_table_number(monkeypatch):
    """``extract_data`` raises ``OpenBBError`` when the table_number is out of range."""
    monkeypatch.setattr(
        jt_mod,
        "_NATIONAL_TABLE_MEASURES",
        {1: ("Hires", "over-the-month")},
    )
    query = jt_mod.BlsJoltsChangeAnalysisQueryParams(scope="national", table_number=2)
    with pytest.raises(OpenBBError, match="does not"):
        jt_mod.BlsJoltsChangeAnalysisFetcher.extract_data(query, None)


def test_transform_data_raises_when_rows_empty():
    """``transform_data`` raises ``EmptyDataError`` when the parser returned no rows."""
    query = jt_mod.BlsJoltsChangeAnalysisQueryParams(scope="national", table_number=1)
    with pytest.raises(EmptyDataError, match="No rows parsed"):
        jt_mod.BlsJoltsChangeAnalysisFetcher.transform_data(query, {"rows": []})

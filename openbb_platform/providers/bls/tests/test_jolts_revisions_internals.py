"""Internal-branch tests for ``openbb_bls.models.jolts_revisions``."""

from __future__ import annotations

import openbb_bls.models.jolts_revisions as jr_mod


def test_extract_data_returns_unfiltered_when_no_filters(monkeypatch):
    """``extract_data`` short-circuits to all rows when both filters are None."""
    rows = [{"industry_code": "00", "measure": "Hires"}]
    monkeypatch.setattr(jr_mod, "fetch_revision_xlsx", lambda _sa: b"")
    monkeypatch.setattr(jr_mod, "parse_revision_xlsx", lambda _b, _sa: rows)
    query = jr_mod.BlsJoltsRevisionsQueryParams(
        seasonally_adjusted=True, industry_code=None, measure=None
    )
    assert jr_mod.BlsJoltsRevisionsFetcher.extract_data(query, None) is rows

"""Empty-data branch tests for the SEC filing-section fetchers."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_sec.models.sec_as_filed_statements import SecAsFiledStatementsFetcher
from openbb_sec.models.sec_company_overview import SecCompanyOverviewFetcher
from openbb_sec.models.sec_disclosures import SecDisclosuresFetcher
from openbb_sec.models.sec_exhibit import SecExhibitFetcher
from openbb_sec.models.sec_legal_proceedings import SecLegalProceedingsFetcher
from openbb_sec.models.sec_risk_factors import SecRiskFactorsFetcher
from openbb_sec.models.sec_segment_revenue import SecSegmentRevenueFetcher

_EMPTY_FS = {
    SecCompanyOverviewFetcher: SimpleNamespace(business=lambda: None),
    SecRiskFactorsFetcher: SimpleNamespace(risk_factors=lambda: []),
    SecDisclosuresFetcher: SimpleNamespace(
        disclosures={"not_a_dict": "skip", "empty": {"text": ""}}
    ),
    SecSegmentRevenueFetcher: SimpleNamespace(segment_revenue=lambda: []),
    SecLegalProceedingsFetcher: SimpleNamespace(legal_proceedings=lambda: None),
    SecAsFiledStatementsFetcher: SimpleNamespace(get_statement=lambda _: (None, None)),
    SecExhibitFetcher: SimpleNamespace(exhibit_choices=lambda: []),
}


def test_exhibit_success_and_transform():
    query = SecExhibitFetcher.transform_query({"symbol": "AAPL", "exhibit": "EX-21"})
    fake = SimpleNamespace(
        exhibit_choices=lambda: [{"value": "EX-21", "label": "x"}],
        get_exhibit=lambda _id: "Exhibit body.",
    )
    with (
        patch(
            "openbb_sec.models.sec_financials.resolve_section_url",
            AsyncMock(return_value="u"),
        ),
        patch(
            "openbb_sec.models.sec_financials.FinancialStatements.from_url",
            return_value=fake,
        ),
    ):
        raw = asyncio.run(SecExhibitFetcher.aextract_data(query, None))
        data = SecExhibitFetcher.transform_data(query, raw)
    assert data.content == "Exhibit body."


def test_exhibit_missing_content_raises():
    query = SecExhibitFetcher.transform_query({"symbol": "AAPL", "exhibit": ""})
    assert query.exhibit is None
    fake = SimpleNamespace(
        exhibit_choices=lambda: [{"value": "EX-21", "label": "x"}],
        get_exhibit=lambda _id: None,
    )
    with (
        patch(
            "openbb_sec.models.sec_financials.resolve_section_url",
            AsyncMock(return_value="u"),
        ),
        patch(
            "openbb_sec.models.sec_financials.FinancialStatements.from_url",
            return_value=fake,
        ),
    ):
        with pytest.raises(EmptyDataError):
            asyncio.run(SecExhibitFetcher.aextract_data(query, None))


def _query(fetcher):
    params = {"symbol": "AAPL"}
    if fetcher is SecAsFiledStatementsFetcher:
        params["statement_type"] = "balance"
    return fetcher.transform_query(params)


@pytest.mark.parametrize("fetcher", list(_EMPTY_FS))
def test_no_filing_raises_empty_data(fetcher):
    """A symbol that resolves to no filing raises EmptyDataError."""
    with patch(
        "openbb_sec.models.sec_financials.resolve_section_url",
        AsyncMock(return_value=""),
    ):
        with pytest.raises(EmptyDataError):
            asyncio.run(fetcher.aextract_data(_query(fetcher), None))


@pytest.mark.parametrize("fetcher", list(_EMPTY_FS))
def test_no_section_data_raises_empty_data(fetcher):
    """A filing with no section data raises EmptyDataError."""
    fake = _EMPTY_FS[fetcher]
    with (
        patch(
            "openbb_sec.models.sec_financials.resolve_section_url",
            AsyncMock(return_value="https://sec.gov/filing.htm"),
        ),
        patch(
            "openbb_sec.models.sec_financials.FinancialStatements.from_url",
            return_value=fake,
        ),
    ):
        with pytest.raises(EmptyDataError):
            asyncio.run(fetcher.aextract_data(_query(fetcher), None))


def test_company_overview_falls_back_to_latest_10k():
    query = SecCompanyOverviewFetcher.transform_query(
        {"symbol": "AAPL", "calendar_year": 2099}
    )
    fake = SimpleNamespace(business=lambda: "Business text.")
    with (
        patch(
            "openbb_sec.models.sec_financials.resolve_section_url",
            new=AsyncMock(side_effect=["", "https://sec.gov/10k.htm"]),
        ),
        patch(
            "openbb_sec.models.sec_financials.FinancialStatements.from_url",
            return_value=fake,
        ),
    ):
        result = asyncio.run(SecCompanyOverviewFetcher.aextract_data(query, None))
    assert result == {"content": "Business text."}

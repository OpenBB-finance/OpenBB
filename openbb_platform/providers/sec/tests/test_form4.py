"""Test the Form 4 parsing utilities."""

# pylint: disable=W0613,W0621
# flake8: noqa: D102,D103

from datetime import date
from unittest.mock import patch

import pytest
from openbb_sec.utils.form4 import (
    get_form_4_urls,
    parse_form_4_data,
    resolve_footnotes,
)


class _Filing:
    """Stand-in for a SecCompanyFilingsData record."""

    def __init__(self, filing_date, report_date, accession):
        self.filing_date = filing_date
        self.report_date = report_date
        self.primary_doc = f"{accession}/form4_{accession}.xml"
        self.report_url = (
            "https://www.sec.gov/Archives/edgar/data/320193/"
            f"{accession}/form4_{accession}.xml"
        )


FILINGS = [
    _Filing(date(2026, 1, 15), date(2026, 1, 13), "000123"),
    _Filing(date(2026, 4, 15), date(2026, 4, 13), "000124"),
    _Filing(date(2026, 7, 15), date(2026, 7, 13), "000125"),
]


@pytest.fixture
def mock_filings():
    """Patch the company-filings fetcher so no network access is required."""

    class _Fetcher:
        async def fetch_data(self, *args, **kwargs):
            return FILINGS

    with patch(
        "openbb_sec.models.company_filings.SecCompanyFilingsFetcher",
        _Fetcher,
    ):
        yield


def _accessions(urls):
    """Recover the accession number from the returned document URLs."""
    return [
        url.split("/")[-1].removeprefix("form4_").removesuffix(".xml") for url in urls
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "start_date,end_date,expected",
    [
        # Both bounds supplied - the previously working path, unchanged.
        (date(2026, 3, 1), date(2026, 12, 31), ["000124", "000125"]),
        # Only a lower bound: filings on or after start_date.
        (date(2026, 3, 1), None, ["000124", "000125"]),
        # Only an upper bound: filings on or before end_date.
        (None, date(2026, 5, 1), ["000123", "000124"]),
        # No bounds: no filtering at all.
        (None, None, ["000123", "000124", "000125"]),
    ],
)
async def test_get_form_4_urls_date_bounds(
    mock_filings, start_date, end_date, expected
):
    """An unbounded side must not filter everything out."""
    urls = await get_form_4_urls(
        "AAPL", start_date=start_date, end_date=end_date, use_cache=False
    )
    assert _accessions(urls) == expected


@pytest.mark.asyncio
async def test_get_form_4_urls_accepts_iso_strings(mock_filings):
    """Date bounds passed as ISO strings are coerced before comparison."""
    urls = await get_form_4_urls(
        "AAPL", start_date="2026-03-01", end_date=None, use_cache=False
    )
    assert _accessions(urls) == ["000124", "000125"]


FOOTNOTE_MAP = {
    "F1": "Sale under a Rule 10b5-1 trading plan.",
    "F2": "Weighted average price.",
    "F3": "Shares held by a family trust.",
}


@pytest.mark.parametrize(
    "ref,expected",
    [
        ({"@id": "F1"}, "Sale under a Rule 10b5-1 trading plan."),
        (
            [{"@id": "F1"}, {"@id": "F2"}],
            "Sale under a Rule 10b5-1 trading plan.; Weighted average price.",
        ),
        ({"@id": "F9"}, None),
        (None, None),
    ],
)
def test_resolve_footnotes(ref, expected):
    """Footnote references resolve to text without mutating the map."""
    assert resolve_footnotes(ref, FOOTNOTE_MAP) == expected
    assert FOOTNOTE_MAP["F1"] == "Sale under a Rule 10b5-1 trading plan."


def test_resolve_footnotes_without_map():
    """A filing with no footnotes section resolves to None."""
    assert resolve_footnotes({"@id": "F1"}, {}) is None


def _transaction(day, shares, footnote_ids):
    """Build one nonDerivativeTransaction with the given footnote references."""
    refs = [{"@id": fid} for fid in footnote_ids]
    return {
        "securityTitle": {"value": "Common Stock"},
        "transactionDate": {"value": f"2026-04-{day}"},
        "transactionCoding": {"transactionFormType": "4", "transactionCode": "S"},
        "transactionAmounts": {
            "transactionShares": {
                "value": shares,
                "footnoteId": refs if len(refs) > 1 else refs[0],
            },
            "transactionPricePerShare": {"value": "200.00"},
            "transactionAcquiredDisposedCode": {"value": "D"},
        },
    }


OWNERSHIP_DOCUMENT = {
    "documentType": "4",
    "periodOfReport": "2026-05-01",
    "issuer": {
        "issuerCik": "0000320193",
        "issuerName": "APPLE INC",
        "issuerTradingSymbol": "AAPL",
    },
    "reportingOwner": {
        "reportingOwnerId": {"rptOwnerCik": "0001214156", "rptOwnerName": "DOE JANE"},
        "reportingOwnerRelationship": {"isDirector": "1"},
    },
    "nonDerivativeTable": {
        "nonDerivativeTransaction": [
            _transaction("28", "1000", ["F1", "F2"]),
            _transaction("29", "2000", ["F3"]),
            _transaction("30", "500", ["F4"]),
        ]
    },
    "footnotes": {
        "footnote": [
            {"@id": "F1", "#text": "Sale under a Rule 10b5-1 trading plan."},
            {"@id": "F2", "#text": "Weighted average price."},
            {"@id": "F3", "#text": "Shares held by a family trust."},
            {"@id": "F4", "#text": "Shares withheld to satisfy tax withholding."},
        ]
    },
}


@pytest.mark.asyncio
async def test_parse_form_4_data_footnotes_are_per_row():
    """Each transaction keeps its own footnote text."""
    rows = await parse_form_4_data(OWNERSHIP_DOCUMENT)

    assert len(rows) == 3
    assert rows[0]["footnote"] == (
        "Sale under a Rule 10b5-1 trading plan.; Weighted average price."
    )
    assert rows[1]["footnote"] == "Shares held by a family trust."
    assert rows[2]["footnote"] == "Shares withheld to satisfy tax withholding."


@pytest.mark.asyncio
async def test_parse_form_4_data_handles_empty_footnote_element():
    """A `<footnote id="F1"/>` element with no text does not raise."""
    document = {
        **OWNERSHIP_DOCUMENT,
        "footnotes": {"footnote": {"@id": "F1"}},
        "nonDerivativeTable": {
            "nonDerivativeTransaction": [_transaction("28", "1000", ["F1"])]
        },
    }
    rows = await parse_form_4_data(document)

    assert len(rows) == 1
    assert rows[0]["footnote"] is None

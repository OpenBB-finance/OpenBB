"""Regression tests for optional shares data in SEC filing covers."""

from pathlib import Path

import pandas as pd
import pytest
from openbb_sec.models.sec_filing import SecBaseFiling, SecFilingFetcher

FIXTURES = Path(__file__).parent / "record" / "nbis_2025_cover"
FILING_URL = (
    "https://www.sec.gov/Archives/edgar/data/1513845/"
    "000110465926052948/nbis-20251231x20f.htm"
)


@pytest.mark.asyncio
async def test_nbis_cover_with_missing_comparative_shares(monkeypatch):
    """A real cover with empty comparative shares still yields verified headers."""
    downloads = []

    async def download(url, use_cache=True):
        assert use_cache is False
        downloads.append(url)
        filename = url.rsplit("/", 1)[-1]
        assert filename in {"R1.htm", "0001104659-26-052948-index-headers.htm"}
        return (FIXTURES / filename).read_text(encoding="utf-8")

    monkeypatch.setattr(SecBaseFiling, "_adownload_file", staticmethod(download))
    query = SecFilingFetcher.transform_query({"url": FILING_URL, "use_cache": False})
    data = await SecFilingFetcher.aextract_data(query, None)
    result = SecFilingFetcher.transform_data(query, data)
    assert result.document_type == "20-F"
    assert result.cik == "0001513845"
    assert str(result.period_ending) == "2025-12-31"
    assert result.trading_symbols == ["NBIS"]
    assert result.cover_page["Document Fiscal Year Focus"] == "2025"
    assert result.cover_page["Document Fiscal Period Focus"] == "FY"
    assert result.cover_page["12(b) Securities"]
    assert len(downloads) == 2


@pytest.mark.parametrize(
    "shares, expected",
    [
        (None, None),
        (float("nan"), None),
        (pd.NA, None),
        (float("inf"), None),
        (float("-inf"), None),
        (0, 0),
        (12, 12000),
        (12.5, 12500),
    ],
)
def test_optional_shares_preserve_other_cover_fields(monkeypatch, shares, expected):
    """Missing/non-finite shares stay unknown; finite shares include zero."""
    table = pd.DataFrame(
        [
            ["Document Fiscal Year Focus", "2025", None],
            ["Document Fiscal Period Focus", "FY", None],
            ["Entity Common Stock, Shares Outstanding", None, shares],
            ["Trading Symbol", "TEST", None],
            ["Title of 12(b) Security", "Common stock", None],
            ["Security Exchange Name", "NASDAQ", None],
        ],
        columns=[
            "Document and Entity Information - shares in thousands",
            "Dec. 31, 2025",
            "Dec. 31, 2024",
        ],
    )
    monkeypatch.setattr(
        SecBaseFiling, "download_file", staticmethod(lambda *args: [table])
    )
    filing = SecBaseFiling.model_construct()
    filing._download_cover_page()  # pylint: disable=protected-access
    assert filing.cover_page["Document Fiscal Year Focus"] == "2025"
    assert filing.cover_page["Document Fiscal Period Focus"] == "FY"
    assert filing.trading_symbols == ["TEST"]
    if expected is None:
        assert not hasattr(filing, "_shares_outstanding")
    else:
        assert filing._shares_outstanding == {  # pylint: disable=protected-access
            "2024-12-31": expected
        }

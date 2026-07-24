"""Unit tests for proxy-statement helpers and the DEF 14A-based fetchers."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bs4 import BeautifulSoup
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_sec.models.sec_beneficial_ownership import SecBeneficialOwnershipFetcher
from openbb_sec.models.sec_executive_compensation import (
    SecExecutiveCompensationFetcher,
)
from openbb_sec.models.sec_management_ownership import SecManagementOwnershipFetcher
from openbb_sec.models.sec_pay_versus_performance import (
    SecPayVersusPerformanceFetcher,
)
from openbb_sec.utils import proxy_statement as ps


def _ix_tag(html):
    """Parse a single inline-XBRL element and return its tag."""
    return BeautifulSoup(html, "html.parser").find(True)


def _filing(filing_date, report_url):
    """Build a stand-in filing row with the attributes resolve reads."""
    return SimpleNamespace(filing_date=filing_date, report_url=report_url)


def _patch_filings(rows):
    """Patch SecCompanyFilingsFetcher to return ``rows`` from fetch_data."""
    fetcher_cls = MagicMock()
    fetcher_cls.return_value.fetch_data = AsyncMock(return_value=rows)
    return patch(
        "openbb_sec.models.company_filings.SecCompanyFilingsFetcher", fetcher_cls
    )


class TestAttr:
    """proxy_statement._attr attribute coercion."""

    def test_string_attr(self):
        tag = BeautifulSoup('<x id="c1"></x>', "html.parser").find(True)
        assert ps._attr(tag, "id") == "c1"

    def test_list_attr_joined(self):
        tag = BeautifulSoup('<x class="a b"></x>', "html.parser").find(True)
        assert ps._attr(tag, "class") == "a b"

    def test_missing_attr(self):
        tag = BeautifulSoup("<x></x>", "html.parser").find(True)
        assert ps._attr(tag, "id") == ""


class TestResolveProxyUrl:
    """proxy_statement.resolve_proxy_url branches."""

    def test_defaults_to_newest(self):
        rows = [
            _filing("2024-04-01", "http://new"),
            _filing("2023-04-01", "http://old"),
        ]
        with _patch_filings(rows):
            url = asyncio.run(ps.resolve_proxy_url("AAPL", None, False))
        assert url == "http://new"

    def test_calendar_year_match(self):
        rows = [
            _filing("2024-04-01", "http://new"),
            _filing("2023-04-01", "http://old"),
        ]
        with _patch_filings(rows):
            url = asyncio.run(ps.resolve_proxy_url("AAPL", 2023, False))
        assert url == "http://old"

    def test_calendar_year_no_match_falls_back(self):
        rows = [_filing("2024-04-01", "http://new")]
        with _patch_filings(rows):
            url = asyncio.run(ps.resolve_proxy_url("AAPL", 2010, False))
        assert url == "http://new"

    def test_no_rows_returns_none(self):
        rows = [_filing("2024-04-01", None), _filing("2023-04-01", "")]
        with _patch_filings(rows):
            url = asyncio.run(ps.resolve_proxy_url("AAPL", None, False))
        assert url is None


class TestTableMarkdown:
    """The keyword-predicate table extractors."""

    def test_summary_compensation_table(self):
        html = (
            "<table><tr><td>Name and Principal Position</td><td>Year</td>"
            "<td>Salary</td><td>Stock Awards</td><td>Total</td></tr>"
            "<tr><td>CEO</td><td>2024</td><td>1</td><td>2</td><td>3</td></tr></table>"
        )
        out = ps.summary_compensation_table(html)
        assert "CEO" in out

    def test_beneficial_owners_table(self):
        html = (
            "<table><tr><td>Name and Address of Beneficial Owner</td>"
            "<td>Percent of Class</td></tr>"
            "<tr><td>Fund X</td><td>5%</td></tr></table>"
        )
        out = ps.beneficial_owners_table(html)
        assert "Fund X" in out

    def test_beneficial_owners_table_foreign_style(self):
        html = (
            "<table><tr><td>Directors and Executive Officers (1):</td>"
            "<td>Percentage of Beneficial Ownership</td></tr>"
            "<tr><td>All directors and executive officers as a group</td><td>11.2</td></tr>"
            "<tr><td>5% Shareholders:</td><td>Global Clean Energy Limited</td></tr>"
            "<tr><td>Percentage of Aggregate Voting Power</td><td>86.4</td></tr></table>"
        )
        out = ps.beneficial_owners_table(html)
        assert "Global Clean Energy Limited" in out

    def test_beneficial_owners_table_from_share_ownership_section(self):
        html = (
            "<div>E. Share Ownership</div>"
            "<p>text</p>"
            "<table><tr><td>Directors and Executive Officers</td><td>Voting Power</td></tr>"
            "<tr><td>5% Shareholders:</td><td>Global Clean Energy Limited</td></tr></table>"
            "<table><tr><td>* Represents beneficial ownership.</td></tr></table>"
            "<div>F. Related Party Transactions</div>"
        )
        out = ps.beneficial_owners_table(html)
        assert "Global Clean Energy Limited" in out
        assert "Represents beneficial ownership" in out

    def test_management_ownership_table(self):
        html = (
            "<table><tr><td>Directors and Executive Officers as a Group</td>"
            "<td>10%</td></tr></table>"
        )
        out = ps.management_ownership_table(html)
        assert "10%" in out

    def test_no_match_returns_empty(self):
        html = "<table><tr><td>Unrelated</td><td>Data</td></tr></table>"
        assert ps.beneficial_owners_table(html) == ""


class TestIxNumber:
    """proxy_statement._ix_number parsing branches."""

    def test_scale_and_sign(self):
        assert ps._ix_number(_ix_tag('<x scale="3" sign="-">1,234.5</x>')) == -1234500.0

    def test_plain_currency(self):
        assert ps._ix_number(_ix_tag("<x>$1,000</x>")) == 1000.0

    def test_emdash_is_none(self):
        assert ps._ix_number(_ix_tag("<x>—</x>")) is None

    def test_na_is_none(self):
        assert ps._ix_number(_ix_tag("<x>N/A</x>")) is None

    def test_non_numeric_is_none(self):
        assert ps._ix_number(_ix_tag("<x>abc</x>")) is None


class TestPayVersusPerformance:
    """proxy_statement.pay_versus_performance XBRL parsing."""

    def test_parses_facts_by_year(self):
        html = (
            '<xbrli:context id="c1"><xbrli:period>'
            "<xbrli:enddate>2024-12-31</xbrli:enddate>"
            "</xbrli:period></xbrli:context>"
            '<ix:nonfraction name="ecd:NetIncomeLoss" contextref="c1" scale="6">'
            "100</ix:nonfraction>"
            '<ix:nonfraction name="ecd:PeoTotalCompAmt" contextref="c1">5</ix:nonfraction>'
            '<ix:nonnumeric name="ecd:CoSelectedMeasureName">Revenue</ix:nonnumeric>'
        )
        rows = ps.pay_versus_performance(html)
        assert rows == [
            {
                "year": 2024,
                "net_income": 100000000.0,
                "peo_total_compensation": 5.0,
                "company_selected_measure_name": "Revenue",
            }
        ]

    def test_dimensioned_and_periodless_contexts_skipped(self):
        html = (
            '<xbrli:context id="dim">'
            "<xbrli:explicitmember>x</xbrli:explicitmember>"
            "</xbrli:context>"
            '<xbrli:context id="noperiod"></xbrli:context>'
            '<ix:nonfraction name="ecd:NetIncomeLoss" contextref="dim">9'
            "</ix:nonfraction>"
        )
        assert ps.pay_versus_performance(html) == []

    def test_non_digit_date_ignored(self):
        html = (
            '<xbrli:context id="c1"><xbrli:period>'
            "<xbrli:instant>n/a</xbrli:instant>"
            "</xbrli:period></xbrli:context>"
            '<ix:nonfraction name="ecd:NetIncomeLoss" contextref="c1">1</ix:nonfraction>'
        )
        assert ps.pay_versus_performance(html) == []

    def test_net_income_only_is_not_pvp(self):
        html = (
            '<xbrli:context id="c1"><xbrli:period>'
            "<xbrli:enddate>2024-12-31</xbrli:enddate>"
            "</xbrli:period></xbrli:context>"
            '<ix:nonfraction name="ecd:NetIncomeLoss" contextref="c1">100</ix:nonfraction>'
        )
        assert ps.pay_versus_performance(html) == []


_CONTENT_MODELS = [
    (SecBeneficialOwnershipFetcher, "beneficial_owners_table"),
    (SecExecutiveCompensationFetcher, "summary_compensation_table"),
]


def _adownload(value):
    """Patch Filing._adownload_file to return ``value``."""
    return patch(
        "openbb_sec.models.sec_filing.Filing._adownload_file",
        new=AsyncMock(return_value=value),
    )


@pytest.mark.parametrize("fetcher,extractor", _CONTENT_MODELS)
class TestContentFetchers:
    """The three markdown-table DEF 14A fetchers (shared structure)."""

    def test_query_validators(self, fetcher, extractor):
        q = fetcher.transform_query({"symbol": "aapl", "calendar_year": ""})
        assert q.symbol == "AAPL"
        assert q.calendar_year is None

    def test_success_and_transform(self, fetcher, extractor):
        q = fetcher.transform_query({"symbol": "AAPL"})
        with (
            patch.object(
                ps, "resolve_proxy_url", new=AsyncMock(return_value="http://u")
            ),
            patch.object(ps, extractor, return_value="| table |"),
            _adownload("<html/>"),
        ):
            out = asyncio.run(fetcher.aextract_data(q, None))
        assert out == {"content": "| table |"}
        assert fetcher.transform_data(q, out).content == "| table |"

    def test_retry_without_calendar_year(self, fetcher, extractor):
        q = fetcher.transform_query({"symbol": "AAPL", "calendar_year": 1990})
        with (
            patch.object(
                ps, "resolve_proxy_url", new=AsyncMock(side_effect=["", "http://u"])
            ),
            patch.object(ps, extractor, return_value="| t |"),
            _adownload("<html/>"),
        ):
            out = asyncio.run(fetcher.aextract_data(q, None))
        assert out == {"content": "| t |"}

    def test_no_proxy_raises(self, fetcher, extractor):
        q = fetcher.transform_query({"symbol": "AAPL"})
        with (
            patch.object(ps, "resolve_proxy_url", new=AsyncMock(return_value="")),
            pytest.raises(EmptyDataError, match="No proxy statement"),
        ):
            asyncio.run(fetcher.aextract_data(q, None))

    def test_empty_table_raises(self, fetcher, extractor):
        q = fetcher.transform_query({"symbol": "AAPL"})
        with (
            patch.object(
                ps, "resolve_proxy_url", new=AsyncMock(return_value="http://u")
            ),
            patch.object(ps, extractor, return_value=""),
            _adownload("<html/>"),
            pytest.raises(EmptyDataError),
        ):
            asyncio.run(fetcher.aextract_data(q, None))


class TestPayVersusPerformanceFetcher:
    """SecPayVersusPerformanceFetcher branches (list output)."""

    def test_query_validators(self):
        q = SecPayVersusPerformanceFetcher.transform_query(
            {"symbol": "aapl", "calendar_year": ""}
        )
        assert q.symbol == "AAPL"
        assert q.calendar_year is None

    def test_success_and_transform(self):
        q = SecPayVersusPerformanceFetcher.transform_query({"symbol": "AAPL"})
        rows = [{"year": 2024, "net_income": 1.0}]
        with (
            patch.object(
                ps, "resolve_proxy_url", new=AsyncMock(return_value="http://u")
            ),
            patch.object(ps, "pay_versus_performance", return_value=rows),
            _adownload("<html/>"),
        ):
            out = asyncio.run(SecPayVersusPerformanceFetcher.aextract_data(q, None))
        assert out == rows
        data = SecPayVersusPerformanceFetcher.transform_data(q, out)
        assert data[0].year == 2024

    def test_retry_without_calendar_year(self):
        q = SecPayVersusPerformanceFetcher.transform_query(
            {"symbol": "AAPL", "calendar_year": 1990}
        )
        with (
            patch.object(
                ps, "resolve_proxy_url", new=AsyncMock(side_effect=["", "http://u"])
            ),
            patch.object(ps, "pay_versus_performance", return_value=[{"year": 2024}]),
            _adownload("<html/>"),
        ):
            out = asyncio.run(SecPayVersusPerformanceFetcher.aextract_data(q, None))
        assert out == [{"year": 2024}]

    def test_no_proxy_raises(self):
        q = SecPayVersusPerformanceFetcher.transform_query({"symbol": "AAPL"})
        with (
            patch.object(ps, "resolve_proxy_url", new=AsyncMock(return_value="")),
            pytest.raises(EmptyDataError, match="No proxy statement"),
        ):
            asyncio.run(SecPayVersusPerformanceFetcher.aextract_data(q, None))

    def test_empty_rows_raises(self):
        q = SecPayVersusPerformanceFetcher.transform_query({"symbol": "AAPL"})
        with (
            patch.object(
                ps, "resolve_proxy_url", new=AsyncMock(return_value="http://u")
            ),
            patch.object(ps, "pay_versus_performance", return_value=[]),
            _adownload("<html/>"),
            pytest.raises(EmptyDataError, match="Pay Versus Performance"),
        ):
            asyncio.run(SecPayVersusPerformanceFetcher.aextract_data(q, None))


class TestManagementSectionFetcher:
    def test_uses_item_10_for_10k(self):
        q = SecManagementOwnershipFetcher.transform_query({"symbol": "AAPL"})
        stub = SimpleNamespace(
            document_type="10-K", get_item=MagicMock(return_value={"text": "Item 10"})
        )
        with (
            patch(
                "openbb_sec.models.sec_financials.resolve_filing_url",
                new=AsyncMock(return_value="http://f"),
            ),
            patch(
                "openbb_sec.models.sec_financials.FinancialStatements.from_url",
                return_value=stub,
            ),
        ):
            out = asyncio.run(SecManagementOwnershipFetcher.aextract_data(q, None))
        assert out == {"content": "Item 10"}

    def test_uses_item_6_for_20f_and_slices_before_compensation(self):
        q = SecManagementOwnershipFetcher.transform_query({"symbol": "CNEY"})
        text = (
            "Preface\n"
            "A. Directors and Senior Management\n"
            "Profile A\n"
            "B. Compensation\n"
            "Comp section"
        )
        stub = SimpleNamespace(
            document_type="20-F", get_item=MagicMock(return_value={"text": text})
        )
        with (
            patch(
                "openbb_sec.models.sec_financials.resolve_filing_url",
                new=AsyncMock(return_value="http://f"),
            ),
            patch(
                "openbb_sec.models.sec_financials.FinancialStatements.from_url",
                return_value=stub,
            ),
        ):
            out = asyncio.run(SecManagementOwnershipFetcher.aextract_data(q, None))
        assert "Profile A" in out["content"]
        assert "B. Compensation" not in out["content"]

    def test_no_filing_raises(self):
        q = SecManagementOwnershipFetcher.transform_query({"symbol": "AAPL"})
        with (
            patch(
                "openbb_sec.models.sec_financials.resolve_filing_url",
                new=AsyncMock(return_value=""),
            ),
            pytest.raises(EmptyDataError),
        ):
            asyncio.run(SecManagementOwnershipFetcher.aextract_data(q, None))

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
from openbb_sec.models.sec_management_profiles import SecManagementProfilesFetcher
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

    def test_falls_back_to_foreign_when_no_proxy(self):
        rows = [
            SimpleNamespace(
                filing_date="2024-03-01",
                report_url="http://foreign",
                report_type="20-F",
            )
        ]
        with _patch_filings(rows):
            url = asyncio.run(ps.resolve_proxy_url("CNEY", None, False))
        assert url == "http://foreign"

    def test_unknown_report_type_returns_none(self):
        rows = [
            SimpleNamespace(
                filing_date="2024-03-01",
                report_url="http://other",
                report_type="8-K",
            )
        ]
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

    def test_management_profiles_table(self):
        html = (
            "<table><tr><td>Directors and Executive Officers as a Group</td>"
            "<td>10%</td></tr></table>"
        )
        out = ps.management_profiles_table(html)
        assert "10%" in out

    def test_management_information_from_proxy(self):
        html = (
            "<table><tr><td>Nominee and Principal Occupation</td><td>Independent</td><td>Age</td></tr>"
            "<tr><td>Jane Doe</td><td>Yes</td><td>62</td></tr></table>"
        )
        out = ps.management_information_from_proxy(html)
        assert "Jane Doe" in out

    def test_management_information_from_proxy_uses_fallback_table(self):
        html = (
            "<table><tr><td>Name</td><td>Age</td><td>Position</td></tr>"
            "<tr><td>John Doe</td><td>51</td><td>Director</td></tr></table>"
        )
        out = ps.management_information_from_proxy(html)
        assert "John Doe" in out

    def test_management_information_from_proxy_no_section_returns_empty(self):
        html = "<div><p>Narrative section</p></div>"
        out = ps.management_information_from_proxy(html)
        assert out == ""

    def test_management_information_from_proxy_empty_table_skipped(self):
        html = (
            "<table></table>"
            "<table><tr><td>Name</td><td>Age</td><td>Position</td></tr>"
            "<tr><td>John Doe</td><td>51</td><td>Director</td></tr></table>"
        )
        out = ps.management_information_from_proxy(html)
        assert "John Doe" in out

    def test_management_information_from_proxy_returns_empty_when_converter_empty(self):
        html = "<div><p>Narrative section</p></div>"
        with patch("openbb_sec.utils.html2markdown.html_to_markdown", return_value=""):
            out = ps.management_information_from_proxy(html)
        assert out == ""

    def test_management_information_from_proxy_skips_toc_and_uses_nominee_section(self):
        html = (
            "<table><tr><td>Notice of Annual Meeting of Shareholders</td><td>3</td></tr>"
            "<tr><td>Proxy Statement Summary</td><td>7</td></tr>"
            "<tr><td>Corporate Governance</td><td>13</td></tr>"
            "<tr><td>Board Meetings and Attendance</td><td>20</td></tr>"
            "<tr><td>Related Party Policy and Transactions</td><td>20</td></tr>"
            "<tr><td>Shareholder Engagement</td><td>9</td></tr></table>"
            "<h2>Nominees to Apple's Board of Directors</h2>"
            "<p>Jane Doe has served as director since 2020.</p>"
        )
        out = ps.management_information_from_proxy(html)
        assert "Nominees to Apple's Board of Directors" in out
        assert "Proxy Statement Summary" not in out

    def test_management_information_from_proxy_returns_full_section_not_single_table(
        self,
    ):
        html = (
            "<h2>Nominees to Apple's Board of Directors</h2>"
            "<p>Director profiles appear below.</p>"
            "<table><tr><td>Name</td><td>Age</td><td>Position</td></tr>"
            "<tr><td>Jane Doe</td><td>62</td><td>Director</td></tr></table>"
            "<p>Additional narrative about committee service.</p>"
            "<h2>Executive Compensation</h2>"
            "<p>Comp section starts here.</p>"
        )
        out = ps.management_information_from_proxy(html)
        assert "Nominees to Apple's Board of Directors" in out
        assert "Director profiles appear below." in out
        assert "Jane Doe" in out
        assert "Additional narrative about committee service." in out
        assert "Comp section starts here." not in out

    def test_management_information_from_proxy_skips_front_matter_and_toc(self):
        html = (
            "<h1>UNITED STATES SECURITIES AND EXCHANGE COMMISSION</h1>"
            "<p>SCHEDULE 14A</p>"
            "<table><tr><td>Notice of 2026 Annual Meeting of Shareholders</td><td>3</td></tr>"
            "<tr><td>Proxy Statement Summary</td><td>7</td></tr>"
            "<tr><td>Nominees to Apple's Board of Directors</td><td>10</td></tr></table>"
            "<h2>Nominees to Apple's Board of Directors</h2>"
            "<p>Jane Doe has served as director since 2020.</p>"
            "<p>John Doe is chief executive officer.</p>"
            "<h2>Executive Compensation</h2>"
            "<p>Comp section starts here.</p>"
        )
        out = ps.management_information_from_proxy(html)
        assert "UNITED STATES SECURITIES" not in out
        assert "Proxy Statement Summary" not in out
        assert "Nominees to Apple's Board of Directors" in out
        assert "Jane Doe has served as director since 2020." in out
        assert "Comp section starts here." not in out

    def test_management_information_from_proxy_ignores_intro_paragraph_mentions(self):
        html = (
            "<p>In the Proxy Statement, references to our directors and executive officers are informational only.</p>"
            "<h2>Nominees to Apple's Board of Directors</h2>"
            "<p>Jane Doe has served as director since 2020.</p>"
            "<h2>Executive Compensation</h2>"
            "<p>Comp section starts here.</p>"
        )
        out = ps.management_information_from_proxy(html)
        assert "references to our directors and executive officers" not in out
        assert "Nominees to Apple's Board of Directors" in out
        assert "Jane Doe has served as director since 2020." in out

    def test_management_information_from_proxy_uses_toc_boundaries(self):
        html = (
            "<table>"
            "<tr><td>Proxy Statement Summary</td><td>7</td></tr>"
            "<tr><td>Nominees for Election as Directors</td><td>10</td></tr>"
            "<tr><td>Executive Compensation</td><td>20</td></tr>"
            "</table>"
            "<p>In the Proxy Statement, references to our directors and executive officers are informational only.</p>"
            "<div>Nominees for Election as Directors</div>"
            "<p>Jane Doe biography.</p>"
            "<div>Executive Compensation</div>"
            "<p>Compensation content should not be included.</p>"
        )
        out = ps.management_information_from_proxy(html)
        assert "Nominees for Election as Directors" in out
        assert "Jane Doe biography." in out
        assert "Compensation content should not be included." not in out
        assert "references to our directors and executive officers" not in out

    def test_management_information_from_proxy_toc_exact_heading_match(self):
        html = (
            "<table>"
            "<tr><td>Executive Officers</td><td>33</td></tr>"
            "<tr><td>Executive Compensation</td><td>35</td></tr>"
            "</table>"
            "<p>In the Proxy Statement, references to our directors and executive officers are informational only.</p>"
            "<h2>Executive Officers</h2>"
            "<p>Tim Cook serves as chief executive officer.</p>"
            "<h2>Executive Compensation</h2>"
            "<p>Compensation content should not be included.</p>"
        )
        out = ps.management_information_from_proxy(html)
        assert "references to our directors and executive officers" not in out
        assert "Executive Officers" in out
        assert "Tim Cook serves as chief executive officer." in out
        assert "Compensation content should not be included." not in out

    def test_no_match_returns_empty(self):
        html = "<table><tr><td>Unrelated</td><td>Data</td></tr></table>"
        assert ps.beneficial_owners_table(html) == ""

    def test_table_from_section_returns_first_table_when_no_predicate(self):
        html = (
            "<div>Item 10. Directors</div>"
            "<table><tr><td>A</td></tr></table>"
            "<div>Item 11. Executive Compensation</div>"
        )
        out = ps._table_from_section(html, r"item\s+10")
        assert "A" in out

    def test_table_from_section_returns_matching_predicate(self):
        html = (
            "<div>Item 10. Directors</div>"
            "<table><tr><td>other table</td></tr></table>"
            "<table><tr><td>target table</td></tr></table>"
            "<div>Item 11. Executive Compensation</div>"
        )
        out = ps._table_from_section(
            html,
            r"item\s+10",
            table_predicate=lambda t: "target table" in t,
        )
        assert "target table" in out

    def test_table_from_section_returns_fallback_first_table(self):
        html = (
            "<div>Item 10. Directors</div>"
            "<table><tr><td>first table</td></tr></table>"
            "<table><tr><td>second table</td></tr></table>"
            "<div>Item 11. Executive Compensation</div>"
        )
        out = ps._table_from_section(
            html,
            r"item\s+10",
            table_predicate=lambda t: "never present" in t,
        )
        assert "first table" in out

    def test_table_from_section_skips_node_without_parent(self):
        fake_soup = MagicMock()
        fake_soup.find_all.return_value = [SimpleNamespace(parent=None)]
        with patch("bs4.BeautifulSoup", return_value=fake_soup):
            out = ps._table_from_section("<div/>", r"item\s+10")
        assert out == ""

    def test_ownership_section_with_no_table_returns_empty(self):
        html = "<div>E. Share Ownership</div><div>F. Related Party Transactions</div>"
        out = ps._ownership_table_from_share_section(html)
        assert out == ""

    def test_ownership_section_skips_non_main_then_uses_main_table(self):
        html = (
            "<div>E. Share Ownership</div>"
            "<table><tr><td>Other disclosure</td></tr></table>"
            "<table><tr><td>5% Shareholders</td><td>Voting Power</td></tr>"
            "<tr><td>Fund X</td><td>7%</td></tr></table>"
            "<div>F. Related Party Transactions</div>"
        )
        out = ps._ownership_table_from_share_section(html)
        assert "Fund X" in out

    def test_ownership_section_skips_node_without_parent(self):
        fake_soup = MagicMock()
        fake_soup.find_all.return_value = [SimpleNamespace(parent=None)]
        with patch("bs4.BeautifulSoup", return_value=fake_soup):
            out = ps._ownership_table_from_share_section("<div/>")
        assert out == ""


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
    def test_query_validator_calendar_year_passthrough(self):
        q = SecManagementProfilesFetcher.transform_query(
            {"symbol": "AAPL", "calendar_year": 2024}
        )
        assert q.calendar_year == 2024

    def test_uses_item_10_for_10k(self):
        q = SecManagementProfilesFetcher.transform_query({"symbol": "AAPL"})
        stub = SimpleNamespace(
            document_type="10-K", get_item=MagicMock(return_value={"text": "Item 10"})
        )
        with (
            patch(
                "openbb_sec.models.sec_financials.resolve_section_url",
                new=AsyncMock(return_value="http://f"),
            ),
            patch(
                "openbb_sec.models.sec_financials.FinancialStatements.from_url",
                return_value=stub,
            ),
        ):
            out = asyncio.run(SecManagementProfilesFetcher.aextract_data(q, None))
        assert out == {"content": "Item 10"}

    def test_uses_item_6_for_20f_and_slices_before_compensation(self):
        q = SecManagementProfilesFetcher.transform_query({"symbol": "CNEY"})
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
                "openbb_sec.models.sec_financials.resolve_section_url",
                new=AsyncMock(return_value="http://f"),
            ),
            patch(
                "openbb_sec.models.sec_financials.FinancialStatements.from_url",
                return_value=stub,
            ),
        ):
            out = asyncio.run(SecManagementProfilesFetcher.aextract_data(q, None))
        assert "Profile A" in out["content"]
        assert "B. Compensation" not in out["content"]

    def test_incorporated_by_reference_uses_proxy(self):
        q = SecManagementProfilesFetcher.transform_query({"symbol": "CAT"})
        stub = SimpleNamespace(
            document_type="10-K",
            get_item=MagicMock(
                return_value={
                    "text": "Information required by this Item is incorporated by reference from the 2026 Proxy Statement."
                }
            ),
        )
        proxy_html = (
            "<table><tr><td>Nominee and Principal Occupation</td><td>Independent</td><td>Age</td></tr>"
            "<tr><td>Jane Doe</td><td>Yes</td><td>62</td></tr></table>"
        )
        with (
            patch(
                "openbb_sec.models.sec_financials.resolve_section_url",
                new=AsyncMock(return_value="http://f"),
            ),
            patch(
                "openbb_sec.models.sec_financials.FinancialStatements.from_url",
                return_value=stub,
            ),
            patch.object(
                ps,
                "resolve_proxy_url",
                new=AsyncMock(return_value="http://proxy"),
            ),
            _adownload(proxy_html),
        ):
            out = asyncio.run(SecManagementProfilesFetcher.aextract_data(q, None))
        assert "Jane Doe" in out["content"]

    def test_no_filing_raises(self):
        q = SecManagementProfilesFetcher.transform_query({"symbol": "AAPL"})
        with (
            patch(
                "openbb_sec.models.sec_financials.resolve_section_url",
                new=AsyncMock(return_value=""),
            ),
            pytest.raises(EmptyDataError),
        ):
            asyncio.run(SecManagementProfilesFetcher.aextract_data(q, None))

    def test_no_filing_retries_without_calendar_year(self):
        q = SecManagementProfilesFetcher.transform_query(
            {"symbol": "AAPL", "calendar_year": 1999}
        )
        stub = SimpleNamespace(
            document_type="10-K", get_item=MagicMock(return_value={"text": "Item 10"})
        )
        with (
            patch(
                "openbb_sec.models.sec_financials.resolve_section_url",
                new=AsyncMock(side_effect=["", "http://fallback"]),
            ),
            patch(
                "openbb_sec.models.sec_financials.FinancialStatements.from_url",
                return_value=stub,
            ),
        ):
            out = asyncio.run(SecManagementProfilesFetcher.aextract_data(q, None))
        assert out == {"content": "Item 10"}

    def test_item_name_fallback_chain_uses_director(self):
        q = SecManagementProfilesFetcher.transform_query({"symbol": "AAPL"})
        stub = SimpleNamespace(document_type="", get_item=MagicMock(return_value=None))

        def _item_by_name(name):
            if name == "director":
                return {"text": "Director section"}
            return None

        stub._item_by_name = MagicMock(side_effect=_item_by_name)
        with (
            patch(
                "openbb_sec.models.sec_financials.resolve_section_url",
                new=AsyncMock(return_value="http://f"),
            ),
            patch(
                "openbb_sec.models.sec_financials.FinancialStatements.from_url",
                return_value=stub,
            ),
        ):
            out = asyncio.run(SecManagementProfilesFetcher.aextract_data(q, None))
        assert out == {"content": "Director section"}
        assert [call.args[0] for call in stub._item_by_name.call_args_list] == [
            "senior management",
            "executive officer",
            "director",
        ]

    def test_proxy_retry_without_calendar_year(self):
        q = SecManagementProfilesFetcher.transform_query(
            {"symbol": "AAPL", "calendar_year": 1999}
        )
        stub = SimpleNamespace(
            document_type="10-K",
            get_item=MagicMock(return_value={"text": "See Proxy Statement"}),
        )
        with (
            patch(
                "openbb_sec.models.sec_financials.resolve_section_url",
                new=AsyncMock(return_value="http://f"),
            ),
            patch(
                "openbb_sec.models.sec_financials.FinancialStatements.from_url",
                return_value=stub,
            ),
            patch.object(
                ps,
                "resolve_proxy_url",
                new=AsyncMock(side_effect=["", "http://proxy"]),
            ) as patch_proxy,
            patch.object(
                ps,
                "management_information_from_proxy",
                return_value="proxy content",
            ) as patch_mgmt,
            _adownload("<html></html>"),
        ):
            out = asyncio.run(SecManagementProfilesFetcher.aextract_data(q, None))
        assert out == {"content": "See Proxy Statement"}
        assert patch_proxy.call_count == 2
        assert patch_mgmt.call_count == 1

    def test_proxy_retry_without_calendar_year_replaces_for_incorporated_by_reference(
        self,
    ):
        q = SecManagementProfilesFetcher.transform_query(
            {"symbol": "AAPL", "calendar_year": 1999}
        )
        stub = SimpleNamespace(
            document_type="10-K",
            get_item=MagicMock(
                return_value={"text": "Incorporated by reference to Proxy Statement"}
            ),
        )
        with (
            patch(
                "openbb_sec.models.sec_financials.resolve_section_url",
                new=AsyncMock(return_value="http://f"),
            ),
            patch(
                "openbb_sec.models.sec_financials.FinancialStatements.from_url",
                return_value=stub,
            ),
            patch.object(
                ps,
                "resolve_proxy_url",
                new=AsyncMock(side_effect=["", "http://proxy"]),
            ) as patch_proxy,
            patch.object(
                ps,
                "management_information_from_proxy",
                return_value="proxy content",
            ) as patch_mgmt,
            _adownload("<html></html>"),
        ):
            out = asyncio.run(SecManagementProfilesFetcher.aextract_data(q, None))
        assert out == {"content": "proxy content"}
        assert patch_proxy.call_count == 2
        assert patch_mgmt.call_count == 1

    def test_raises_when_no_management_content(self):
        q = SecManagementProfilesFetcher.transform_query({"symbol": "AAPL"})
        stub = SimpleNamespace(
            document_type="10-K",
            get_item=MagicMock(return_value={"text": ""}),
            _item_by_name=MagicMock(return_value=None),
        )
        with (
            patch(
                "openbb_sec.models.sec_financials.resolve_section_url",
                new=AsyncMock(return_value="http://f"),
            ),
            patch(
                "openbb_sec.models.sec_financials.FinancialStatements.from_url",
                return_value=stub,
            ),
            pytest.raises(EmptyDataError, match="No management section"),
        ):
            asyncio.run(SecManagementProfilesFetcher.aextract_data(q, None))

    def test_transform_data(self):
        q = SecManagementProfilesFetcher.transform_query({"symbol": "AAPL"})
        data = SecManagementProfilesFetcher.transform_data(q, {"content": "abc"})
        assert data.content == "abc"

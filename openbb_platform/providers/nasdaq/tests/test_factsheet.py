"""Tests for openbb_nasdaq.utils.factsheet."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_nasdaq.utils import factsheet


def word(text: str, x0: float, x1: float, top: float = 0.0) -> dict:
    """Build a positioned word the way pdfplumber emits one."""
    return {"text": text, "x0": x0, "x1": x1, "top": top}


class TestFactsheetUrl:
    """Cover the fact sheet URL construction."""

    def test_maps_the_nordic_prefix(self):
        """A Nasdaq Nordic prefix is mapped to its MIC."""
        url = factsheet.build_factsheet_url("SE0011337708", "sek", "STO")

        assert "EX%24%24%24%24XSTO" in url
        assert "BaseCurrencyId=SEK" in url
        assert "externalid=SE0011337708" in url

    def test_passes_a_mic_through(self):
        """A MIC that is already resolved is used as given."""
        assert "XCSE" in factsheet.build_factsheet_url("DK000", "DKK", "XCSE")


class TestFetchFactsheet:
    """Cover the fact sheet download."""

    def test_returns_the_pdf(self, monkeypatch, factsheet_pdf):
        """A PDF response is returned verbatim."""

        async def _request(url, **kwargs):
            return factsheet_pdf

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", _request
        )
        payload = asyncio.run(factsheet.fetch_factsheet("SE1", "SEK", "STO"))

        assert payload.startswith(b"%PDF")

    def test_rejects_a_non_pdf(self, monkeypatch):
        """An HTML error page is reported rather than parsed."""

        async def _request(url, **kwargs):
            return b"<html>not found</html>"

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", _request
        )

        with pytest.raises(OpenBBError, match="No fact sheet"):
            asyncio.run(factsheet.fetch_factsheet("SE2", "SEK", "STO"))


class TestColumnAssignment:
    """Cover the right-edge column assignment."""

    def test_assigns_whole_tokens(self):
        """Tokens that sit inside one column are kept intact."""
        cells = [word("2024", 0, 20), word("2025", 30, 50)]
        values = factsheet._values([word("1,000", 2, 20), word("2,000", 32, 50)], cells)

        assert values == ["1,000", "2,000"]

    def test_leaves_absent_columns_empty(self):
        """A row with fewer values than periods leaves the tail unset."""
        cells = [word("2024", 0, 20), word("2025", 30, 50)]
        values = factsheet._values([word("1,000", 2, 20)], cells)

        assert values == ["1,000", None]

    def test_splits_a_straddling_token(self):
        """A token spanning two columns is broken apart on glyph positions."""
        cells = [word("2025", 0, 20), word("2026-06", 22, 46)]
        values = factsheet._values([word("17.254.06", 4, 46)], cells)

        assert values == ["17.2", "54.06"]

    def test_no_cells_yields_nothing(self):
        """A block without a header produces no values."""
        assert factsheet._values([word("1", 0, 5)], []) == []


class TestHeaderDetection:
    """Cover period-header recognition."""

    def test_year_header(self):
        """Two or more calendar years form a header."""
        line = [word("2024", 0, 20), word("2025", 30, 50)]

        assert len(factsheet._year_header(line)) == 2

    def test_single_year_is_not_a_header(self):
        """One year alone is a data row, not a header."""
        assert factsheet._year_header([word("2024", 0, 20)]) == []

    def test_horizon_header(self):
        """Trailing-return horizons form a header."""
        line = [
            word("1", 0, 4),
            word("Week", 5, 25),
            word("1", 40, 44),
            word("Month", 45, 70),
        ]

        assert len(factsheet._horizon_header(line)) == 2

    def test_quarter_header(self):
        """Quarter labels form a header."""
        line = [word("Q3", 0, 12), word("Q4", 30, 42)]

        assert len(factsheet._period_header(line)) == 2

    def test_prose_is_not_a_header(self):
        """Ordinary text is not mistaken for a header."""
        assert factsheet._period_header([word("Revenue", 0, 30)]) == []


class TestSectionName:
    """Cover section naming."""

    @pytest.mark.parametrize("raw", ["(SEK)", "USD", "(USD)"])
    def test_bare_currency_becomes_market_summary(self, raw):
        """A block labelled only with a currency is named for its content."""
        assert factsheet._section_name(raw) == "Market Summary"

    def test_named_section_is_kept(self):
        """A real section name passes through."""
        assert factsheet._section_name("Financials (USD)") == "Financials (USD)"

    def test_empty_section_is_none(self):
        """An unnamed block carries no section."""
        assert factsheet._section_name("") is None


class TestParseFactsheet:
    """Cover the end-to-end parse of the bundled fact sheet."""

    def test_sections(self, factsheet):
        """Every section of the sheet is represented."""
        sections = {row["section"] for row in factsheet["series"]}

        assert sections == {
            "Yearly Performance",
            "Trailing Returns",
            "Financials",
            "Profitability and Valuation",
            "Compound Annual Growth Rates",
            "Financial Position",
            "Quarterly Results",
            "Market Summary",
            "Financials (USD)",
            "Profitability",
            "Financial Health (USD)",
            "Profitability Analysis",
            "Valuation Analysis",
            "Industry Peers",
        }

    def test_nine_year_financials(self, factsheet):
        """The nine-year income statement is read in full."""
        revenue = {
            row["period"]: row["value"]
            for row in factsheet["series"]
            if row["section"] == "Financials (USD)" and row["label"] == "Revenue (Mil)"
        }

        assert revenue["2017"] == "34,312"
        assert revenue["2025"] == "33,220"
        assert len(revenue) == 9

    def test_market_cap_columns_are_not_smeared(self, factsheet):
        """Run-together market cap figures land in the right periods."""
        values = {
            row["period"]: row["value"]
            for row in factsheet["series"]
            if row["label"] == "Market Cap ( SEK , Mil)"
        }

        assert values["2023"] == "813,999"
        assert values["2024"] == "1,101,488"
        assert values["2025"] == "1,251,098"

    def test_zero_gap_columns_are_split(self, factsheet):
        """Adjacent figures rendered without a gap are separated."""
        equity = {
            row["period"]: row["value"]
            for row in factsheet["series"]
            if row["section"] == "Market Summary" and row["label"] == "Equity"
        }

        assert equity["2025"] == "17.2"
        assert equity["2026-06"] == "54.06"

    def test_average_blocks(self, factsheet):
        """The Current / 3 Yr / 5 Yr / 10 Yr blocks are read."""
        roe = {
            row["period"]: row["value"]
            for row in factsheet["series"]
            if row["section"] == "Profitability Analysis"
            and row["label"] == "Return on Equity %"
        }

        assert roe == {
            "Current": "33.60",
            "3 Yr Avg": "29.26",
            "5 Yr Avg": "26.86",
            "10 Yr Avg": "22.44",
        }

    def test_header_rows_are_not_data(self, factsheet):
        """The wrapped average header is not mistaken for a line item."""
        labels = {row["label"] for row in factsheet["series"]}

        assert not any("Yr Avg" in label for label in labels)

    def test_current_labels_survive(self, factsheet):
        """Balance sheet lines beginning with 'Current' are kept."""
        labels = {
            row["label"]
            for row in factsheet["series"]
            if row["section"] == "Financial Position"
        }

        assert {"Current Assets", "Current Debt", "Current Liabilities"} <= labels

    def test_quarterly_subsections(self, factsheet):
        """Each quarterly sub-table is labelled distinctly."""
        labels = {
            row["label"]
            for row in factsheet["series"]
            if row["section"] == "Quarterly Results"
        }

        assert "Revenue Mil: Most Recent" in labels
        assert "Earnings Per Share: Prior Year" in labels

    def test_unlabelled_rows_take_the_section(self, factsheet):
        """Rows whose section title is their only label are kept."""
        returns = {
            row["period"]: row["value"]
            for row in factsheet["series"]
            if row["section"] == "Trailing Returns"
        }

        assert returns["1 Week"] == "0.6"
        assert returns["YTD"] == "39.8"

    def test_peers(self, factsheet):
        """The industry peer table is read with all three metrics."""
        peers = {
            row["label"]
            for row in factsheet["series"]
            if row["section"] == "Industry Peers"
        }

        assert "AQ Group AB" in peers
        assert len(peers) == 7

    def test_dividends(self, factsheet):
        """Declared distributions are read with both dates."""
        first = factsheet["dividends"][0]

        assert first == {
            "ex_date": "23/03/2026",
            "payment_date": "25/03/2026",
            "type": "Cash",
            "currency": "CHF",
            "amount": "0.94",
        }
        assert len(factsheet["dividends"]) == 5

    def test_profile(self, factsheet):
        """The key stats, description, and derivative flags are read."""
        profile = {row["label"]: row["value"] for row in factsheet["profile"]}

        assert profile["Employees"] == "110,100"
        assert profile["Morningstar Sector"] == "Industrials"
        assert profile["Options"] == "Yes"
        assert profile["Description"].startswith("ABB supplies electrical equipment")

    def test_series_are_deduplicated(self, factsheet):
        """No section, label, and period appears twice."""
        keys = [
            (row["section"], row["label"], row["period"]) for row in factsheet["series"]
        ]

        assert len(keys) == len(set(keys))


class TestGetInstrumentFactsheet:
    """Cover the resolve, download, and parse chain."""

    def test_resolves_and_parses(self, monkeypatch, factsheet_pdf):
        """A resolved instrument yields its parsed fact sheet."""

        async def _resolve(symbol, asset_class=None):
            return {"orderbook_id": "TX1", "asset_class": "SHARES", "isin": "SE1"}

        async def _info(path, **kwargs):
            return {"qdHeader": {"exchange": "Nasdaq Stockholm", "currency": "SEK"}}

        async def _fetch(isin, currency, exchange):
            assert (isin, currency, exchange) == ("SE1", "SEK", "XSTO")

            return factsheet_pdf

        monkeypatch.setattr(
            "openbb_nasdaq.utils.nordic.resolve_nordic_instrument", _resolve
        )
        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _info)
        monkeypatch.setattr(factsheet, "fetch_factsheet", _fetch)
        sheet = asyncio.run(factsheet.get_instrument_factsheet("ABB"))

        assert sheet["series"]

    def test_no_isin_returns_empty(self, monkeypatch):
        """An instrument without an ISIN has no fact sheet."""

        async def _resolve(symbol, asset_class=None):
            return {"orderbook_id": "TX1", "asset_class": "CORPORATE_BONDS"}

        monkeypatch.setattr(
            "openbb_nasdaq.utils.nordic.resolve_nordic_instrument", _resolve
        )
        sheet = asyncio.run(factsheet.get_instrument_factsheet("CATME_HO1"))

        assert sheet == {"profile": [], "series": [], "dividends": []}

    def test_download_failure_returns_empty(self, monkeypatch):
        """A listing Morningstar does not cover degrades to empty sections."""

        async def _resolve(symbol, asset_class=None):
            return {"orderbook_id": "TX1", "asset_class": "SHARES", "isin": "SE1"}

        async def _info(path, **kwargs):
            return {"qdHeader": {"exchange": "Nasdaq Helsinki", "currency": "EUR"}}

        async def _fetch(isin, currency, exchange):
            raise OpenBBError("no fact sheet")

        monkeypatch.setattr(
            "openbb_nasdaq.utils.nordic.resolve_nordic_instrument", _resolve
        )
        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _info)
        monkeypatch.setattr(factsheet, "fetch_factsheet", _fetch)

        assert asyncio.run(factsheet.get_instrument_factsheet("X"))["series"] == []


class _StubPage:
    """A pdfplumber page stand-in built from positioned words."""

    def __init__(self, words: list[dict]):
        self._words = words

    def extract_words(self, **kwargs) -> list[dict]:
        """Return the canned words."""
        return self._words


class TestParserGuards:
    """Cover the guards for blocks a fact sheet does not carry."""

    def test_fetch_reads_through_the_callback(self, monkeypatch, factsheet_pdf):
        """The download callback returns the raw body."""

        class _Response:
            async def read(self):
                """Return the raw body."""
                return factsheet_pdf

        async def _request(url, **kwargs):
            return await kwargs["response_callback"](_Response(), None)

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", _request
        )

        assert asyncio.run(factsheet.fetch_factsheet("SE9", "SEK", "STO")).startswith(
            b"%PDF"
        )

    def test_anchor_edges_without_a_full_row(self):
        """A block with no complete data row yields no columns."""
        assert factsheet._anchor_edges([[word("1", 0, 5)]], 4) == []

    def test_fixed_table_without_columns(self):
        """A block whose columns cannot be derived yields no rows."""
        assert factsheet._parse_fixed_table([[word("x", 0, 5)]], ("a", "b"), "S") == []

    def test_averages_without_the_section(self):
        """A sheet without the block yields no rows."""
        page = _StubPage([word("Something Else", 0, 40, 10)])

        assert factsheet._parse_averages(page, "Valuation Analysis", 0, 999) == []

    def test_description_without_the_heading(self):
        """A sheet without a company profile yields no description."""
        page = _StubPage([word("Key", 400, 415, 10), word("Stats", 416, 440, 10)])

        assert factsheet._parse_description(page) == []

    def test_description_with_no_prose(self):
        """A profile heading with no body yields no description."""
        page = _StubPage(
            [
                word("Company", 400, 430, 10),
                word("Profile", 431, 460, 10),
                word("Key", 400, 415, 30),
                word("Stats", 416, 440, 30),
            ]
        )

        assert factsheet._parse_description(page) == []

    def test_dividends_without_the_table(self):
        """A sheet with no dividend table yields no distributions."""
        page = _StubPage([word("Dividends", 400, 440, 10)])

        assert factsheet._parse_dividends(page) == []

    def test_dividends_stop_at_a_non_date_row(self):
        """Parsing stops at the first row that is not a distribution."""
        rows = [
            word("Ex", 364, 372, 10),
            word("Date", 373, 392, 10),
            word("Payment", 407, 440, 10),
            word("Type", 449, 466, 10),
            word("Currency", 480, 512, 10),
            word("Amount", 526, 552, 10),
            word("Footnote", 364, 400, 30),
        ]

        assert factsheet._parse_dividends(_StubPage(rows)) == []

    def test_duplicate_series_rows_are_dropped(self, monkeypatch, factsheet_pdf):
        """A section, label, and period is emitted only once."""
        duplicate = {
            "section": "Financials",
            "label": "Revenue (Mil)",
            "period": "2025",
            "value": "1",
        }
        monkeypatch.setattr(
            factsheet, "_parse_peers", lambda page: [duplicate, duplicate]
        )
        parsed = factsheet.parse_factsheet(factsheet_pdf)
        matches = [
            row
            for row in parsed["series"]
            if (row["section"], row["label"], row["period"])
            == ("Financials", "Revenue (Mil)", "2025")
        ]

        assert len(matches) == 1

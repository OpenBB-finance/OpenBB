"""Tests for the Nasdaq Nordic reference and schedule models."""

import asyncio
from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_nasdaq.models.nordic_bond_yields import NasdaqNordicBondYieldsFetcher
from openbb_nasdaq.models.nordic_holidays import NasdaqNordicHolidaysFetcher
from openbb_nasdaq.models.nordic_index_factors import NasdaqNordicIndexFactorsFetcher
from openbb_nasdaq.models.nordic_knocked_out import NasdaqNordicKnockedOutFetcher
from openbb_nasdaq.models.nordic_mortgage_rates import (
    NasdaqNordicMortgageRatesFetcher,
)
from openbb_nasdaq.models.nordic_trading_hours import NasdaqNordicTradingHoursFetcher
from openbb_nasdaq.utils import schedule

from .conftest import patch_data

MARKUP = """
<h2>Nasdaq European Markets Trading Hours</h2>
<table>
  <tr><th>Markets - Main Market</th><th>Copenhagen</th><th>Stockholm</th></tr>
  <tr><td>Equities</td><td>09:00-17:00</td><td>09:00-17:30</td></tr>
  <tr><td>Bonds</td><td>&nbsp;</td><td>---</td></tr>
  <tr><td></td><td>09:00-17:00</td><td>09:00-17:30</td></tr>
</table>
<h2>Exchange Holiday Schedule 2026</h2>
<table>
  <tr><th>&nbsp;</th><th>Equity/Equity derivatives</th><th>Fixed Income</th></tr>
  <tr><td>Copenhagen</td><td>Closed Jan 1, 2026; Dec 25, 2026</td><td>Closed Jan 1, 2026</td></tr>
  <tr><td></td><td>Closed Jan 1, 2026</td><td>Closed Jan 1, 2026</td></tr>
</table>
<h2>Exchange Holiday Schedule 2025</h2>
<table>
  <tr><th>&nbsp;</th><th>Equity/Equity derivatives</th></tr>
  <tr><td>Stockholm</td><td>Closed Jan 1, 2025; Feb 30, 2025</td></tr>
</table>
"""


class TestScheduleParsing:
    """Cover the trading-hours page parsing."""

    def test_fetches_the_page(self, monkeypatch):
        """The page markup is returned as text."""

        class _Response:
            async def text(self):
                """Return the page body."""
                return MARKUP

        async def _request(url, **kwargs):
            return await kwargs["response_callback"](_Response(), None)

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", _request
        )

        assert "Trading Hours" in asyncio.run(schedule.fetch_trading_hours())

    def test_non_text_response(self, monkeypatch):
        """A response that is not markup yields an empty page."""

        async def _request(url, **kwargs):
            return {"unexpected": True}

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", _request
        )

        assert asyncio.run(schedule.fetch_trading_hours()) == ""

    def test_parses_the_session_grid(self):
        """Each segment and market pair becomes a record."""
        rows = schedule.parse_trading_hours(MARKUP)

        assert {(r["segment"], r["market"]) for r in rows} == {
            ("Equities", "Copenhagen"),
            ("Equities", "Stockholm"),
        }
        assert rows[0]["section"] == "Markets - Main Market"

    def test_parses_the_holiday_calendar(self):
        """Every closed date is expanded into its own record."""
        rows = schedule.parse_holidays(MARKUP)
        copenhagen = [r for r in rows if r["market"] == "Copenhagen"]

        assert date(2026, 1, 1) in {r["date"] for r in copenhagen}
        assert date(2026, 12, 25) in {r["date"] for r in copenhagen}

    def test_skips_an_impossible_date(self):
        """A date the calendar cannot carry is dropped."""
        stockholm = [
            r for r in schedule.parse_holidays(MARKUP) if r["market"] == "Stockholm"
        ]

        assert [r["date"] for r in stockholm] == [date(2025, 1, 1)]

    def test_ignores_tables_without_rows(self):
        """A table with no body contributes nothing."""
        assert schedule.parse_trading_hours("<table></table>") == []
        assert schedule.parse_holidays("<table></table>") == []

    def test_table_without_a_heading(self):
        """A table with no heading above it still parses its grid."""
        rows = schedule.parse_trading_hours(
            "<table><tr><th>Fixed Income</th><th>Stockholm</th></tr>"
            "<tr><td>Bonds</td><td>09:00-16:15</td></tr></table>"
        )

        assert rows[0]["section"] == "Fixed Income"

    def test_unnamed_section_is_skipped(self):
        """A grid whose first header cell is blank carries no section."""
        assert (
            schedule.parse_trading_hours(
                "<table><tr><th>&nbsp;</th><th>Stockholm</th></tr>"
                "<tr><td>Bonds</td><td>09:00</td></tr></table>"
            )
            == []
        )


class TestTradingHours:
    """Cover the trading hours model."""

    def test_transforms_the_grid(self, monkeypatch):
        """The page is fetched and flattened."""

        async def _fetch():
            return MARKUP

        monkeypatch.setattr(schedule, "fetch_trading_hours", _fetch)
        query = NasdaqNordicTradingHoursFetcher.transform_query({})
        raw = asyncio.run(NasdaqNordicTradingHoursFetcher.aextract_data(query, None))
        rows = NasdaqNordicTradingHoursFetcher.transform_data(query, raw)

        assert len(rows) == 2
        assert rows[0].hours == "09:00-17:00"

    def test_empty_raises(self):
        """A page with no session tables is reported."""
        query = NasdaqNordicTradingHoursFetcher.transform_query({})

        with pytest.raises(EmptyDataError, match="No trading hours"):
            NasdaqNordicTradingHoursFetcher.transform_data(query, "")


class TestHolidays:
    """Cover the exchange holiday model."""

    def test_filters_by_year(self, monkeypatch):
        """The year narrows the calendar and rows sort by date."""

        async def _fetch():
            return MARKUP

        monkeypatch.setattr(schedule, "fetch_trading_hours", _fetch)
        query = NasdaqNordicHolidaysFetcher.transform_query({"year": 2026})
        raw = asyncio.run(NasdaqNordicHolidaysFetcher.aextract_data(query, None))
        rows = NasdaqNordicHolidaysFetcher.transform_data(query, raw)

        assert {r.date.year for r in rows} == {2026}
        assert rows == sorted(rows, key=lambda r: r.date)

    def test_every_year(self):
        """Without a year the whole calendar is returned."""
        query = NasdaqNordicHolidaysFetcher.transform_query({})
        rows = NasdaqNordicHolidaysFetcher.transform_data(query, MARKUP)

        assert {r.date.year for r in rows} == {2025, 2026}

    def test_empty_raises(self):
        """A year with no closures is reported."""
        query = NasdaqNordicHolidaysFetcher.transform_query({"year": 1999})

        with pytest.raises(EmptyDataError, match="No exchange holidays"):
            NasdaqNordicHolidaysFetcher.transform_data(query, MARKUP)


class TestBondYields:
    """Cover the average bond yield model."""

    @staticmethod
    def _payload():
        """Return a one-section yield grid."""
        return {
            "date": "2026-07-24",
            "beforeTax": {
                "headers": {"attribute": "Rente", "under3": "0-3", "total": "Total"},
                "sections": [
                    {
                        "name": "Stat",
                        "rows": [
                            {
                                "attribute": "Effektiv rente",
                                "under3": "2.37",
                                "total": "2.86",
                            }
                        ],
                    }
                ],
            },
            "afterTax": {"headers": {}, "sections": []},
        }

    def test_flattens_the_grid(self, monkeypatch):
        """Each segment, attribute, and maturity bucket becomes a record."""
        patch_data(monkeypatch, self._payload())
        query = NasdaqNordicBondYieldsFetcher.transform_query({})
        raw = asyncio.run(NasdaqNordicBondYieldsFetcher.aextract_data(query, None))
        rows = NasdaqNordicBondYieldsFetcher.transform_data(query, raw)

        assert len(rows) == 2
        assert rows[0].segment == "Stat"
        assert rows[0].maturity == "0-3"
        assert rows[0].value == pytest.approx(2.37)
        assert rows[0].date == date(2026, 7, 24)

    def test_after_tax_basis(self):
        """The after-tax basis reads its own block."""
        query = NasdaqNordicBondYieldsFetcher.transform_query({"basis": "after_tax"})

        with pytest.raises(EmptyDataError, match="after_tax"):
            NasdaqNordicBondYieldsFetcher.transform_data(query, self._payload())

    def test_missing_payload(self, monkeypatch):
        """An empty response yields an empty payload."""
        patch_data(monkeypatch, None)
        query = NasdaqNordicBondYieldsFetcher.transform_query({})

        assert (
            asyncio.run(NasdaqNordicBondYieldsFetcher.aextract_data(query, None)) == {}
        )


class TestIndexFactors:
    """Cover the index factors model."""

    def test_flattens_by_effective_date(self, monkeypatch):
        """Each dated column becomes its own record, sorted by date."""
        patch_data(
            monkeypatch,
            {
                "indexFactors": {
                    "default": {
                        "rows": [
                            {
                                "attribute": "Kreditor",
                                "2026-07-27": "327.733000",
                                "2026-06-30": "327.216000",
                                "2026-12-31": "--",
                            }
                        ]
                    },
                    "other": "not a block",
                }
            },
        )
        query = NasdaqNordicIndexFactorsFetcher.transform_query({})
        raw = asyncio.run(NasdaqNordicIndexFactorsFetcher.aextract_data(query, None))
        rows = NasdaqNordicIndexFactorsFetcher.transform_data(query, raw)

        assert [r.date for r in rows] == [date(2026, 6, 30), date(2026, 7, 27)]
        assert rows[0].value == pytest.approx(327.216)

    def test_empty_raises(self):
        """A payload with no factors is reported."""
        query = NasdaqNordicIndexFactorsFetcher.transform_query({})

        with pytest.raises(EmptyDataError, match="No index factors"):
            NasdaqNordicIndexFactorsFetcher.transform_data(query, {})


class TestMortgageRates:
    """Cover the mortgage rates model."""

    def test_flattens_by_term(self, monkeypatch):
        """Each quoted term becomes a record and blanks are dropped."""
        patch_data(
            monkeypatch,
            {
                "mortgageRates": {
                    "headers": {"fullName": "Name", "3m": "3M", "1y": "1Y"},
                    "rows": [
                        {
                            "fullName": "Danske Bolan",
                            "3m": "3.84",
                            "1y": "---",
                            "url": "https://danske",
                        }
                    ],
                }
            },
        )
        query = NasdaqNordicMortgageRatesFetcher.transform_query({})
        raw = asyncio.run(NasdaqNordicMortgageRatesFetcher.aextract_data(query, None))
        rows = NasdaqNordicMortgageRatesFetcher.transform_data(query, raw)

        assert len(rows) == 1
        assert rows[0].term == "3M"
        assert rows[0].rate == pytest.approx(0.0384)
        assert rows[0].url == "https://danske"

    def test_empty_raises(self):
        """A payload with no rates is reported."""
        query = NasdaqNordicMortgageRatesFetcher.transform_query({})

        with pytest.raises(EmptyDataError, match="No mortgage rates"):
            NasdaqNordicMortgageRatesFetcher.transform_data(query, {})


class TestKnockedOut:
    """Cover the knocked-out instruments model."""

    def test_sends_the_state(self, monkeypatch):
        """The requested state is sent as the category."""
        seen: list[str] = []
        patch_data(
            monkeypatch,
            {
                "instrumentListing": {
                    "rows": [
                        {
                            "isin": "DE000JY513N7",
                            "fullName": "MINI L AMD",
                            "noteDescription": "Knock-out Buy-back",
                            "assetClass": "WARRANTS",
                            "orderbookId": "TX7444224",
                            "exchangeSymbol": "",
                        }
                    ]
                }
            },
            seen,
        )
        query = NasdaqNordicKnockedOutFetcher.transform_query({"state": "trading_halt"})
        raw = asyncio.run(NasdaqNordicKnockedOutFetcher.aextract_data(query, None))
        rows = NasdaqNordicKnockedOutFetcher.transform_data(query, raw)

        assert "category=TRADING_HALT" in seen[0]
        assert rows[0].isin == "DE000JY513N7"
        assert rows[0].exchange_symbol is None

    def test_missing_payload(self, monkeypatch):
        """An empty response yields no rows."""
        patch_data(monkeypatch, None)
        query = NasdaqNordicKnockedOutFetcher.transform_query({})

        assert (
            asyncio.run(NasdaqNordicKnockedOutFetcher.aextract_data(query, None)) == []
        )

    def test_empty_raises(self):
        """No instrument in the requested state is reported."""
        query = NasdaqNordicKnockedOutFetcher.transform_query({})

        with pytest.raises(EmptyDataError, match="buyback"):
            NasdaqNordicKnockedOutFetcher.transform_data(query, [])


class TestTranslations:
    """Cover the Danish label translations."""

    @pytest.mark.parametrize(
        ("danish", "english"),
        [
            ("Effektiv rente", "Effective yield"),
            ("Antal papirer", "Number of securities"),
            ("Vægt i %", "Weight in %"),
            ("Stat, fiskeri & Færøerne", "Government, fisheries & Faroe Islands"),
            ("Særlige institutter", "Special institutions"),
            ("Enhedsprioritet", "Unit priority mortgage"),
            ("Alm & Særl. realkredit", "Ordinary & special mortgage credit"),
            (
                "Kreditor indeksfaktorer: Restgæld/obligationer",
                "Creditor index factors: Outstanding debt/bonds",
            ),
            ("Referenceindeks:", "Reference index"),
            ("Rederiindeks 1 1/2 pct", "Shipping index 1.5 pct"),
        ],
    )
    def test_translates_known_labels(self, danish, english):
        """Every published Danish label maps to English."""
        from openbb_nasdaq.utils.translations import translate

        assert translate(danish) == english

    def test_passes_english_through(self):
        """A label that needs no translation is returned as given."""
        from openbb_nasdaq.utils.translations import translate

        assert translate("Total") == "Total"

    def test_handles_no_label(self):
        """A missing label stays missing."""
        from openbb_nasdaq.utils.translations import translate

        assert translate(None) is None

    def test_translates_the_after_tax_header(self):
        """The after-tax header has its own translation."""
        from openbb_nasdaq.utils.translations import translate

        assert (
            translate("Rente efter skat - restløbetid (år)")
            == "Yield after tax - residual maturity (years)"
        )

    def test_applied_to_the_models(self):
        """The models render their labels in English."""
        query = NasdaqNordicBondYieldsFetcher.transform_query({})
        rows = NasdaqNordicBondYieldsFetcher.transform_data(
            query,
            {
                "date": "2026-07-24",
                "beforeTax": {
                    "headers": {"attribute": "x", "under3": "0-3"},
                    "sections": [
                        {
                            "name": "Særlige institutter",
                            "rows": [{"attribute": "Effektiv rente", "under3": "2.4"}],
                        }
                    ],
                },
            },
        )

        assert rows[0].segment == "Special institutions"
        assert rows[0].attribute == "Effective yield"

        factors = NasdaqNordicIndexFactorsFetcher.transform_data(
            NasdaqNordicIndexFactorsFetcher.transform_query({}),
            {
                "indexFactors": {
                    "default": {
                        "rows": [
                            {
                                "attribute": "Støttet byggeri, hovedstol",
                                "2026-06-30": "1.5",
                            }
                        ]
                    }
                }
            },
        )

        assert factors[0].attribute == "Subsidised construction, principal"

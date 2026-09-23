"""Tests for the USDA ERS FATUS trade update utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.us_agricultural_trade import (
    TABLE_OPTIONS,
    UsAgriculturalTradeData,
    UsAgriculturalTradeFetcher,
    UsAgriculturalTradeQueryParams,
    _column_label,
    _resolve_commodity,
)
from openbb_government_us.usda.utils import ers_fatus_trade
from openbb_government_us.usda.utils.ers_fatus_trade import (
    DIRECTION_LABELS,
    MEASURE_LABELS,
    MEDIA_PATH,
    MONTH_INDEX,
    PRODUCT_PAGE,
    SPREAD_DIMENSION,
    TABLE_ALIASES,
    TABLE_MEASURES,
    TRADE_TABLES,
    build_url,
    classify_period,
    filter_latest,
    parse_rows,
    period_rank,
    table_period_bases,
    vintage_order,
    within_year_rank,
)

HEADER = (
    "Commodity,Country,Time_period,Year,US_Trade,Value_type,Units,Value,"
    "Update_version,Source_table ,Data_source,Notes\n"
)
SUMMARY_TABLE = (
    '"U.S. agricultural trade, fiscal years, calendar years, year-to-date,'
    ' and current month"'
)
MONTHLY_TABLE = '"Total value of U.S. agricultural trade and trade balance, monthly "'
EXPORTS_TABLE = '"U.S. agricultural exports, year-to-date and current months"'
TOP_EXPORTS_TABLE = (
    '"Top 10 U.S. export markets for soybeans, corn, wheat, and cotton, by volume"'
)
SAMPLE_CSV = HEADER + (
    "Agricultural total,World total ,Fiscal year, October-September".replace(
        "Fiscal year, October-September", '"Fiscal year, October-September"'
    )
    + f",2025,Exports,Customs value,Billion U.S. dollars,176.253,NA,"
    f"{SUMMARY_TABLE},"
    '"Compiled by USDA, Economic Research Service using data from U.S.'
    ' Department of Commerce, Bureau of the Census.",NA\n'
    f"Agricultural total,World total,October,1975,Exports,Customs value,"
    f"U.S. dollars,2107269698,NA,{MONTHLY_TABLE},NA,NA\n"
    f'Agricultural total,World total,May,2026,"Trade balance (exports minus'
    f' imports)",Customs value,U.S. dollars,-2841946673,NA,{MONTHLY_TABLE},NA,NA\n'
    f"Soybeans,World total,April,2026,Exports,Volume,Thousand metric tons,"
    f"3000.274,June update of April data,{EXPORTS_TABLE},NA,NA\n"
    f"Soybeans,World total,May,2026,Exports,Volume,Thousand metric tons,"
    f"2569.822,July update of May data,{EXPORTS_TABLE},NA,NA\n"
    f'Coffee and products,World total,"Change, 2025-26",2025-26,Imports,'
    f'"Cost, insurance, and freight (c.i.f.)",Percent,-1.374,'
    f'July update of May data,"U.S. agricultural imports, year-to-date and'
    f' current months",NA,NA\n'
    f'"Cotton, ex linters","Korea, South",May,2026,Exports,Volume,Metric tons,'
    f"64998,July update of May data,{TOP_EXPORTS_TABLE},NA,Excludes pulses\n"
    f"Corn,World total,May,2026,Exports,Volume,Metric tons,,"
    f"July update of May data,{TOP_EXPORTS_TABLE},NA,NA\n"
)


def make_row(**overrides) -> dict:
    """Build a parsed row record with overridable defaults."""
    table = overrides.get("table", "monthly")
    row = {
        "table": table,
        "source_table": TRADE_TABLES[table],
        "commodity": "Agricultural total",
        "country": "World total",
        "time_period": "May",
        "year": "2026",
        "direction": "exports",
        "value_type": "value",
        "units": "U.S. dollars",
        "value": 1.0,
        "update_version": None,
        "notes": None,
        "data_source": None,
    }
    row.update(overrides)
    return row


class TestErsFatusTradeUtils:
    """Tests for the ers_fatus_trade utils module."""

    def test_catalog_contents(self):
        """The catalog maps 6 table slugs to unique published titles."""
        assert sorted(TRADE_TABLES) == [
            "exports_ytd",
            "imports_ytd",
            "monthly",
            "summary",
            "top_export_markets",
            "top_import_sources",
        ]
        assert len(TABLE_ALIASES) == 6
        assert TABLE_ALIASES[TRADE_TABLES["monthly"]] == "monthly"
        assert PRODUCT_PAGE == (
            "data-products/foreign-agricultural-trade-of-the-united-states-fatus"
            "/us-agricultural-trade-data-update"
        )

    def test_pivot_metadata_tables(self):
        """Measures, labels, spread dimensions, and directions align by table."""
        assert TABLE_MEASURES == {
            "summary": ["value"],
            "monthly": ["value"],
            "exports_ytd": ["value", "volume"],
            "imports_ytd": ["value", "volume", "cif"],
            "top_export_markets": ["volume"],
            "top_import_sources": ["value"],
        }
        assert set(MEASURE_LABELS) == {"value", "volume", "cif"}
        assert set(SPREAD_DIMENSION) == set(TRADE_TABLES)
        assert list(DIRECTION_LABELS) == ["exports", "imports", "balance"]
        assert MONTH_INDEX["January"] == 1 and MONTH_INDEX["December"] == 12

    def test_build_url(self):
        """The URL points at the /media/5029 all-data CSV."""
        assert build_url() == (
            "https://www.ers.usda.gov/media/5029"
            "/csv-comma-separated-values-format-of-all-data.csv"
        )
        assert build_url() == f"https://www.ers.usda.gov{MEDIA_PATH}"

    def test_vintage_order(self):
        """Vintages rank by their data month in October-September order."""
        assert vintage_order("January update of October data") == 1
        assert vintage_order("February update of December data") == 3
        assert vintage_order("July update of May data") == 8
        assert vintage_order(None) == 0
        assert vintage_order("Annual revision") == 0
        assert vintage_order("July update of Smarch data") == 0

    def test_period_rank_orders_within_a_year(self):
        """Bare months rank before calendar YTD, fiscal YTD, then annual totals."""
        assert period_rank("May") == 5
        assert period_rank("December") == 12
        assert period_rank("January-May") == 105
        assert period_rank("January-December") == 112
        assert period_rank("October-May") == 205
        assert period_rank("October-January") == 201
        assert period_rank("Fiscal year, October-September") == 900
        assert period_rank("Calendar year, January-December") == 901
        assert period_rank("Change, 2025-26") == 500
        assert period_rank("Marketing year") == 500

    def test_classify_period(self):
        """Each published period maps to its reporting basis, else None."""
        assert classify_period("Fiscal year, October-September") == "Fiscal year"
        assert classify_period("Calendar year, January-December") == "Calendar year"
        assert classify_period("May") == "Monthly"
        assert classify_period("January-May") == "Calendar year-to-date"
        assert classify_period("October-May") == "Fiscal year-to-date"
        assert classify_period("Change, 2025-26") is None
        assert classify_period("Marketing year") is None

    def test_within_year_rank(self):
        """Within-year rank orders months and year-to-date spans by their basis."""
        assert within_year_rank("Monthly", "May") == 5
        assert within_year_rank("Calendar year-to-date", "January-May") == 5
        assert within_year_rank("Fiscal year-to-date", "October-January") == 4
        assert within_year_rank("Fiscal year-to-date", "October-October") == 1
        assert within_year_rank("Fiscal year", "Fiscal year, October-September") == 0

    def test_table_period_bases(self, monkeypatch):
        """table_period_bases lists a table's bases coarse-to-fine, annual first."""

        async def fake_afetch(**kwargs):
            return [
                make_row(table="summary", time_period="May"),
                make_row(table="summary", time_period="Fiscal year, October-September"),
                make_row(table="summary", time_period="October-May"),
                make_row(table="monthly", time_period="January"),
            ]

        monkeypatch.setattr(ers_fatus_trade, "afetch_trade_data", fake_afetch)
        assert asyncio.run(table_period_bases("summary")) == [
            "Fiscal year",
            "Fiscal year-to-date",
            "Monthly",
        ]

    def test_parse_rows_tidies_labels(self):
        """Header and cell whitespace strip, labels normalize, NA maps to None."""
        rows = parse_rows(SAMPLE_CSV)
        assert len(rows) == 7
        summary = rows[0]
        assert summary["table"] == "summary"
        assert summary["source_table"] == TRADE_TABLES["summary"]
        assert summary["country"] == "World total"
        assert summary["year"] == "2025"
        assert summary["value"] == 176.253
        assert summary["update_version"] is None
        assert summary["notes"] is None
        assert summary["data_source"].startswith("Compiled by USDA")
        monthly = rows[1]
        assert monthly["table"] == "monthly"
        assert monthly["value"] == 2107269698
        assert rows[2]["direction"] == "balance"
        assert rows[3]["update_version"] == "June update of April data"
        change = rows[5]
        assert change["table"] == "imports_ytd"
        assert change["value_type"] == "cif"
        assert change["year"] == "2025-26"
        assert change["units"] == "Percent"
        top = rows[6]
        assert top["commodity"] == "Cotton, excluding linters"
        assert top["country"] == "South Korea"
        assert top["notes"] == "Excludes pulses"

    def test_parse_rows_skips_empty_values(self):
        """Rows with an empty Value are dropped."""
        rows = parse_rows(SAMPLE_CSV)
        assert not any(row["commodity"] == "Corn" for row in rows)

    def test_parse_rows_empty_text(self):
        """Empty text parses to no rows."""
        assert parse_rows("") == []

    def test_parse_rows_unknown_source_table_raises(self):
        """An unrecognized source table raises OpenBBError."""
        text = HEADER + (
            "Corn,World total,May,2026,Exports,Volume,Metric tons,1.0,NA,"
            "Mystery table,NA,NA\n"
        )
        with pytest.raises(OpenBBError, match="Unrecognized source table"):
            parse_rows(text)

    def test_parse_rows_unknown_direction_raises(self):
        """An unrecognized US_Trade value raises OpenBBError."""
        text = HEADER + (
            f"Corn,World total,May,2026,Re-exports,Volume,Metric tons,1.0,NA,"
            f"{TOP_EXPORTS_TABLE},NA,NA\n"
        )
        with pytest.raises(OpenBBError, match="Unrecognized trade direction"):
            parse_rows(text)

    def test_parse_rows_unknown_value_type_raises(self):
        """An unrecognized Value_type raises OpenBBError."""
        text = HEADER + (
            f"Corn,World total,May,2026,Exports,Weight,Metric tons,1.0,NA,"
            f"{TOP_EXPORTS_TABLE},NA,NA\n"
        )
        with pytest.raises(OpenBBError, match="Unrecognized value type"):
            parse_rows(text)

    def test_filter_latest_keeps_max_vintage_per_table(self):
        """Only each table's newest vintage survives; None rows pass through."""
        records = [
            make_row(),
            make_row(
                table="exports_ytd",
                update_version="June update of April data",
            ),
            make_row(
                table="exports_ytd",
                update_version="July update of May data",
            ),
            make_row(
                table="imports_ytd",
                update_version="March update of January data",
            ),
        ]
        kept = filter_latest(records)
        assert [record["update_version"] for record in kept] == [
            None,
            "July update of May data",
            "March update of January data",
        ]

    def test_filter_latest_keeps_unrecognized_vintages(self):
        """Tables whose vintages never parse keep all their rows."""
        records = [make_row(update_version="Annual revision")]
        assert filter_latest(records) == records

    def test_afetch_trade_data(self, monkeypatch):
        """afetch_trade_data fetches through the ERS cache client and parses."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return SAMPLE_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        rows = asyncio.run(ers_fatus_trade.afetch_trade_data())
        assert calls == [(MEDIA_PATH, PRODUCT_PAGE)]
        assert len(rows) == 7
        assert rows[0]["table"] == "summary"

    def test_distinct_field_scopes_by_table(self, monkeypatch):
        """distinct_field returns first-seen values, scoped to the given table."""

        async def fake_afetch():
            return [
                make_row(table="monthly", commodity="Soybeans"),
                make_row(table="monthly", commodity="Corn"),
                make_row(table="monthly", commodity="Soybeans"),
                make_row(table="summary", commodity="Cotton"),
                {**make_row(table="monthly"), "commodity": ""},
            ]

        monkeypatch.setattr(ers_fatus_trade, "afetch_trade_data", fake_afetch)
        assert asyncio.run(ers_fatus_trade.distinct_field("commodity", "monthly")) == [
            "Soybeans",
            "Corn",
        ]
        assert asyncio.run(ers_fatus_trade.distinct_field("commodity")) == [
            "Soybeans",
            "Corn",
            "Cotton",
        ]


def _summary_records() -> list[dict]:
    """Direction-spread summary records across two years and several periods."""
    return [
        make_row(
            table="summary",
            direction="exports",
            units="Billion U.S. dollars",
            value=174.148,
            time_period="Fiscal year, October-September",
            year="2024",
        ),
        make_row(
            table="summary",
            direction="imports",
            units="Billion U.S. dollars",
            value=206.016,
            time_period="Fiscal year, October-September",
            year="2024",
        ),
        make_row(
            table="summary",
            direction="balance",
            units="Billion U.S. dollars",
            value=-31.869,
            time_period="Fiscal year, October-September",
            year="2024",
        ),
        make_row(
            table="summary",
            direction="exports",
            units="Billion U.S. dollars",
            value=176.512,
            time_period="Calendar year, January-December",
            year="2024",
        ),
        make_row(
            table="summary",
            direction="exports",
            units="Billion U.S. dollars",
            value=15.18,
            time_period="May",
            year="2026",
        ),
        make_row(
            table="summary",
            direction="exports",
            units="Billion U.S. dollars",
            value=122.4,
            time_period="October-May",
            year="2026",
        ),
        make_row(
            table="summary",
            direction="exports",
            units="Billion U.S. dollars",
            value=75.0,
            time_period="January-May",
            year="2026",
        ),
    ]


def _exports_records() -> list[dict]:
    """Commodity-spread exports records with vintages, a change row, and volume."""
    return [
        make_row(
            table="exports_ytd",
            commodity="Agricultural total",
            value_type="value",
            units="Million U.S. dollars",
            value=100.0,
            time_period="October",
            year="2025",
            update_version="January update of October data",
        ),
        make_row(
            table="exports_ytd",
            commodity="Agricultural total",
            value_type="value",
            units="Million U.S. dollars",
            value=105.0,
            time_period="October",
            year="2025",
            update_version="February update of December data",
        ),
        make_row(
            table="exports_ytd",
            commodity="Soybeans",
            value_type="value",
            units="Million U.S. dollars",
            value=40.0,
            time_period="October",
            year="2025",
            update_version="January update of October data",
        ),
        make_row(
            table="exports_ytd",
            commodity="Agricultural total",
            value_type="value",
            units="Million U.S. dollars",
            value=200.0,
            time_period="October-May",
            year="2026",
            update_version="July update of May data",
        ),
        make_row(
            table="exports_ytd",
            commodity="Agricultural total",
            value_type="value",
            units="Percent",
            value=5.0,
            time_period="Change, 2025-26",
            year="2025-26",
            update_version="July update of May data",
        ),
        make_row(
            table="exports_ytd",
            commodity="Soybeans",
            value_type="volume",
            units="Thousand metric tons",
            value=3000.0,
            time_period="October",
            year="2025",
            update_version="January update of October data",
        ),
        make_row(
            table="exports_ytd",
            commodity="Ethanol (non-beverage)",
            value_type="volume",
            units="Thousand kiloliters",
            value=500.0,
            time_period="October",
            year="2025",
            update_version="January update of October data",
        ),
    ]


def _top_records() -> list[dict]:
    """Partner-spread top-market records for two commodities, one sparse period."""
    return [
        make_row(
            table="top_export_markets",
            commodity="Soybeans",
            country="China",
            value_type="volume",
            units="Metric tons",
            value=5918201.4,
            time_period="October",
            year="2025",
        ),
        make_row(
            table="top_export_markets",
            commodity="Soybeans",
            country="Mexico",
            value_type="volume",
            units="Metric tons",
            value=572648.0,
            time_period="October",
            year="2025",
        ),
        make_row(
            table="top_export_markets",
            commodity="Soybeans",
            country="China",
            value_type="volume",
            units="Metric tons",
            value=6115680.6,
            time_period="November",
            year="2025",
        ),
        make_row(
            table="top_export_markets",
            commodity="Corn",
            country="Japan",
            value_type="volume",
            units="Metric tons",
            value=1056136.0,
            time_period="October",
            year="2025",
        ),
    ]


class TestUsAgriculturalTrade:
    """Tests for the UsAgriculturalTrade model."""

    def test_transform_query_defaults(self):
        """transform_query builds the query params with the exports default table."""
        query = UsAgriculturalTradeFetcher.transform_query({"start_year": 2020})
        assert isinstance(query, UsAgriculturalTradeQueryParams)
        assert query.table == "exports_ytd"
        assert query.value_type is None
        assert query.commodity is None
        assert query.start_year == 2020
        assert query.latest is False

    def test_table_validation(self):
        """Table coerces blanks and lists, defaults, and rejects unknown slugs."""
        assert UsAgriculturalTradeQueryParams(table=None).table == "exports_ytd"
        assert UsAgriculturalTradeQueryParams(table="").table == "exports_ytd"
        assert UsAgriculturalTradeQueryParams(table="  ").table == "exports_ytd"
        assert UsAgriculturalTradeQueryParams(table=[]).table == "exports_ytd"
        assert UsAgriculturalTradeQueryParams(table=["monthly"]).table == "monthly"
        assert UsAgriculturalTradeQueryParams(table=" summary ").table == "summary"
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            UsAgriculturalTradeQueryParams(table="bogus")

    def test_label_normalization(self):
        """value_type and commodity normalize to a single stripped name or None."""
        query = UsAgriculturalTradeQueryParams(
            value_type=["volume"], commodity="  Soybeans  "
        )
        assert query.value_type == "volume"
        assert query.commodity == "Soybeans"
        assert UsAgriculturalTradeQueryParams(value_type="").value_type is None
        assert UsAgriculturalTradeQueryParams(commodity="  ").commodity is None

    def test_column_label_branches(self):
        """The column-label helper appends the source unit for each spread dim."""
        direction = make_row(direction="balance", units="Billion U.S. dollars")
        assert _column_label("direction", direction) == "Balance (Billion U.S. dollars)"
        commodity = make_row(commodity="Soybeans", units="Thousand metric tons")
        assert _column_label("commodity", commodity) == (
            "Soybeans (Thousand metric tons)"
        )
        country = make_row(country="China", units="Metric tons")
        assert _column_label("country", country) == "China (Metric tons)"
        no_unit = make_row(country="China", units="")
        assert _column_label("country", no_unit) == "China"

    def test_period_label_bare_year_for_annual_bases(self):
        """Annual bases label the row with the bare year; sub-annual add the span."""
        label = UsAgriculturalTradeFetcher._period_label
        assert label("Monthly", 2026, "May") == "2026 May"
        assert label("Fiscal year-to-date", 2026, "October-May") == "2026 October-May"
        assert label("Calendar year-to-date", 2026, "January-May") == "2026 January-May"
        assert label("Fiscal year", 2024, "Fiscal year, October-September") == "2024"
        assert label("Calendar year", 2024, "Calendar year, January-December") == "2024"

    def test_period_basis_filters_to_one_basis(self):
        """The period-basis param keeps one aligned series and labels it cleanly."""
        records = _summary_records()
        fiscal = UsAgriculturalTradeFetcher.transform_data(
            UsAgriculturalTradeFetcher.transform_query(
                {"table": "summary", "period_basis": "Fiscal year"}
            ),
            records,
        )
        assert [row.period for row in fiscal] == ["2024"]
        monthly = UsAgriculturalTradeFetcher.transform_data(
            UsAgriculturalTradeFetcher.transform_query(
                {"table": "summary", "period_basis": "Monthly"}
            ),
            records,
        )
        assert [row.period for row in monthly] == ["2026 May"]
        fiscal_ytd = UsAgriculturalTradeFetcher.transform_data(
            UsAgriculturalTradeFetcher.transform_query(
                {"table": "summary", "period_basis": "Fiscal year-to-date"}
            ),
            records,
        )
        assert [row.period for row in fiscal_ytd] == ["2026 October-May"]

    def test_resolve_commodity(self):
        """The commodity resolver honors a valid request and defaults to first."""
        records = [make_row(commodity="Soybeans"), make_row(commodity="Corn")]
        assert _resolve_commodity("Corn", records) == "Corn"
        assert _resolve_commodity(None, records) == "Soybeans"
        assert _resolve_commodity("Wheat", records) == "Soybeans"
        assert _resolve_commodity(None, []) is None

    def test_aextract_filters_to_the_table(self, monkeypatch):
        """aextract_data keeps only the selected table's rows."""

        async def fake_afetch(**kwargs):
            return [
                make_row(table="monthly"),
                make_row(table="summary"),
                make_row(table="exports_ytd"),
            ]

        monkeypatch.setattr(ers_fatus_trade, "afetch_trade_data", fake_afetch)
        query = UsAgriculturalTradeFetcher.transform_query({"table": "summary"})
        records = asyncio.run(UsAgriculturalTradeFetcher.aextract_data(query, None))
        assert [record["table"] for record in records] == ["summary"]

    def test_summary_spreads_direction_into_columns(self):
        """The summary table's default fiscal-year basis spreads directions."""
        query = UsAgriculturalTradeFetcher.transform_query({"table": "summary"})
        data = UsAgriculturalTradeFetcher.transform_data(query, _summary_records())
        assert [row.period for row in data] == ["2024"]
        first = data[0].model_dump(by_alias=True)
        assert list(first) == [
            "period",
            "Exports (Billion U.S. dollars)",
            "Imports (Billion U.S. dollars)",
            "Balance (Billion U.S. dollars)",
        ]
        assert first["Exports (Billion U.S. dollars)"] == 174.148
        assert first["Imports (Billion U.S. dollars)"] == 206.016
        assert first["Balance (Billion U.S. dollars)"] == -31.869
        assert set(UsAgriculturalTradeData.model_fields) == {"period"}

    def test_direction_columns_drop_absent_directions(self):
        """Only directions present in the data become columns."""
        records = [
            make_row(table="monthly", direction="exports", value=10.0),
            make_row(table="monthly", direction="imports", value=6.0),
        ]
        query = UsAgriculturalTradeFetcher.transform_query({"table": "monthly"})
        data = UsAgriculturalTradeFetcher.transform_data(query, records)
        assert list(data[0].model_dump(by_alias=True))[1:] == [
            "Exports (U.S. dollars)",
            "Imports (U.S. dollars)",
        ]

    def test_exports_value_pivot_collapses_vintages_and_drops_change(self):
        """The exports monthly default spreads commodities, newest vintage winning."""
        query = UsAgriculturalTradeFetcher.transform_query({"table": "exports_ytd"})
        data = UsAgriculturalTradeFetcher.transform_data(query, _exports_records())
        assert [row.period for row in data] == ["2025 October"]
        october = data[0].model_dump(by_alias=True)
        assert list(october)[1:] == [
            "Agricultural total (Million U.S. dollars)",
            "Soybeans (Million U.S. dollars)",
        ]
        assert october["Agricultural total (Million U.S. dollars)"] == 105.0
        assert october["Soybeans (Million U.S. dollars)"] == 40.0

    def test_exports_fiscal_ytd_basis_selects_the_span_row(self):
        """Selecting the fiscal year-to-date basis keeps the October-May span row."""
        query = UsAgriculturalTradeFetcher.transform_query(
            {"table": "exports_ytd", "period_basis": "Fiscal year-to-date"}
        )
        data = UsAgriculturalTradeFetcher.transform_data(query, _exports_records())
        assert [row.period for row in data] == ["2026 October-May"]
        assert (
            data[0].model_dump(by_alias=True)[
                "Agricultural total (Million U.S. dollars)"
            ]
            == 200.0
        )

    def test_exports_volume_embeds_varying_units_in_headers(self):
        """Volume columns embed each commodity's own unit and serve only period."""
        query = UsAgriculturalTradeFetcher.transform_query(
            {"table": "exports_ytd", "value_type": "volume"}
        )
        data = UsAgriculturalTradeFetcher.transform_data(query, _exports_records())
        row = data[0].model_dump(by_alias=True)
        assert row["Soybeans (Thousand metric tons)"] == 3000.0
        assert row["Ethanol (non-beverage) (Thousand kiloliters)"] == 500.0
        assert set(UsAgriculturalTradeData.model_fields) == {"period"}

    def test_invalid_measure_falls_back_to_first(self):
        """A measure invalid for the table resolves to the table's first measure."""
        query = UsAgriculturalTradeFetcher.transform_query(
            {"table": "exports_ytd", "value_type": "cif"}
        )
        data = UsAgriculturalTradeFetcher.transform_data(query, _exports_records())
        assert "Agricultural total (Million U.S. dollars)" in data[0].model_dump(
            by_alias=True
        )

    def test_top_markets_spread_partners_for_the_first_commodity(self):
        """With no commodity, the top-market table spreads the first commodity."""
        query = UsAgriculturalTradeFetcher.transform_query(
            {"table": "top_export_markets"}
        )
        data = UsAgriculturalTradeFetcher.transform_data(query, _top_records())
        assert [row.period for row in data] == [
            "2025 November",
            "2025 October",
        ]
        october = data[1].model_dump(by_alias=True)
        assert list(october)[1:] == ["China (Metric tons)", "Mexico (Metric tons)"]
        assert october["China (Metric tons)"] == 5918201.4
        assert october["Mexico (Metric tons)"] == 572648.0
        november = data[0].model_dump(by_alias=True)
        assert november["China (Metric tons)"] == 6115680.6
        assert november["Mexico (Metric tons)"] is None

    def test_top_markets_row_selects_the_named_commodity(self):
        """A named commodity restricts the partner spread to that commodity."""
        query = UsAgriculturalTradeFetcher.transform_query(
            {"table": "top_export_markets", "commodity": "Corn"}
        )
        data = UsAgriculturalTradeFetcher.transform_data(query, _top_records())
        row = data[0].model_dump(by_alias=True)
        assert list(row)[1:] == ["Japan (Metric tons)"]
        assert row["Japan (Metric tons)"] == 1056136.0

    def test_year_filters_and_empty_result(self):
        """Year filters bound the rows and an out-of-range filter yields nothing."""
        query = UsAgriculturalTradeFetcher.transform_query(
            {"table": "summary", "end_year": 2024}
        )
        data = UsAgriculturalTradeFetcher.transform_data(query, _summary_records())
        assert data and all(row.period == "2024" for row in data)
        query = UsAgriculturalTradeFetcher.transform_query(
            {"table": "summary", "start_year": 2030}
        )
        assert (
            UsAgriculturalTradeFetcher.transform_data(query, _summary_records()) == []
        )

    def test_end_year_drops_the_later_years_of_one_basis(self):
        """An end year bounds the rows within the resolved period basis."""
        records = [
            make_row(
                table="summary",
                direction="exports",
                units="Billion U.S. dollars",
                value=value,
                time_period="Fiscal year, October-September",
                year=year,
            )
            for year, value in (("2023", 178.0), ("2024", 174.148))
        ]
        query = UsAgriculturalTradeFetcher.transform_query(
            {"table": "summary", "period_basis": "Fiscal year", "end_year": 2023}
        )
        data = UsAgriculturalTradeFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2023"]
        assert (
            data[0].model_dump(by_alias=True)["Exports (Billion U.S. dollars)"] == 178.0
        )

    def test_latest_keeps_only_the_newest_vintage(self):
        """latest=True keeps only the newest update vintage before pivoting."""
        records = [
            make_row(
                table="exports_ytd",
                commodity="Agricultural total",
                value_type="value",
                units="Million U.S. dollars",
                value=100.0,
                time_period="October",
                year="2025",
                update_version="January update of October data",
            ),
            make_row(
                table="exports_ytd",
                commodity="Agricultural total",
                value_type="value",
                units="Million U.S. dollars",
                value=200.0,
                time_period="October-May",
                year="2026",
                update_version="July update of May data",
            ),
        ]
        query = UsAgriculturalTradeFetcher.transform_query(
            {"table": "exports_ytd", "latest": True}
        )
        data = UsAgriculturalTradeFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2026 October-May"]

    def test_period_is_the_only_served_field(self):
        """Only period is a declared field; value columns arrive as extras."""
        declared = set(UsAgriculturalTradeData.model_fields)
        query = UsAgriculturalTradeFetcher.transform_query({"table": "exports_ytd"})
        data = UsAgriculturalTradeFetcher.transform_data(query, _exports_records())
        served: set = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        assert declared == {"period"}
        assert declared < served
        labels = [row.period for row in data]
        assert len(labels) == len(set(labels))

    def test_param_scoping_options(self):
        """Choice params are single-select with real labels and scoped endpoints."""
        extra = UsAgriculturalTradeQueryParams.__json_schema_extra__
        table = extra["table"]["x-widget_config"]
        assert table["label"] == "Table" and table["multiSelect"] is False
        assert {opt["value"] for opt in table["options"]} == set(TRADE_TABLES)
        assert table["value"] == "exports_ytd"
        value_type = extra["value_type"]["x-widget_config"]
        assert value_type["type"] == "endpoint"
        assert value_type["label"] == "Measure"
        assert value_type["optionsParams"] == {"table": "$table"}
        assert value_type["optionsEndpoint"].endswith(
            "/usda/agricultural_trade_measures"
        )
        commodity = extra["commodity"]["x-widget_config"]
        assert commodity["type"] == "endpoint"
        assert commodity["label"] == "Commodity (partner tables)"
        assert commodity["optionsEndpoint"].endswith(
            "/usda/agricultural_trade_commodities"
        )
        assert {opt["value"] for opt in TABLE_OPTIONS} == set(TRADE_TABLES)

    def test_widget_config_and_column_headers(self):
        """The whole-widget config and the single pinned period column persist."""
        widget = UsAgriculturalTradeData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert widget["$.name"] == "USDA ERS U.S. Agricultural Trade"
        assert widget["$.category"] == "Economy"
        assert widget["$.subCategory"] == "Agriculture"
        assert widget["$.source"] == ["USDA", "ERS"]
        fields = UsAgriculturalTradeData.model_fields
        assert set(fields) == {"period"}
        period_config = fields["period"].json_schema_extra["x-widget_config"]
        assert period_config["headerName"] == "Period"
        assert period_config["pinned"] == "left"
        assert period_config["maxWidth"] == 240

    def test_null_token_mixin_coerces_placeholder(self):
        """The Data model coerces placeholder tokens to None but keeps columns."""
        row = UsAgriculturalTradeData.model_validate(
            {
                "period": "2026 May",
                "China (Metric tons)": "--",
                "Mexico (Metric tons)": 5.0,
            }
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["China (Metric tons)"] is None
        assert dumped["Mexico (Metric tons)"] == 5.0


class TestAgriculturalTradeMeasures:
    """Tests for the table-scoped measures options endpoint."""

    def test_measures_scope_to_the_table(self):
        """The measures endpoint returns each table's ordered, labeled measures."""
        from openbb_government_us.usda.usda_router import agricultural_trade_measures

        imports = asyncio.run(agricultural_trade_measures("imports_ytd"))
        assert imports == [
            {"label": "Value", "value": "value"},
            {"label": "Volume", "value": "volume"},
            {"label": "CIF value", "value": "cif"},
        ]
        top = asyncio.run(agricultural_trade_measures("top_export_markets"))
        assert top == [{"label": "Volume", "value": "volume"}]

    def test_measures_default_to_exports_for_unknown_table(self):
        """An unknown or missing table falls back to the exports measures."""
        from openbb_government_us.usda.usda_router import agricultural_trade_measures

        assert asyncio.run(agricultural_trade_measures(None)) == [
            {"label": "Value", "value": "value"},
            {"label": "Volume", "value": "volume"},
        ]
        assert asyncio.run(agricultural_trade_measures("bogus")) == [
            {"label": "Value", "value": "value"},
            {"label": "Volume", "value": "volume"},
        ]


class TestAgriculturalTradePeriods:
    """Tests for the table-scoped period-basis options endpoint."""

    def test_periods_scope_to_the_table(self, monkeypatch):
        """The endpoint returns each table's ordered, labeled reporting bases."""
        from openbb_government_us.usda.usda_router import agricultural_trade_periods

        async def fake_afetch(**kwargs):
            return [
                make_row(table="summary", time_period="Fiscal year, October-September"),
                make_row(table="summary", time_period="May"),
                make_row(table="monthly", time_period="January"),
            ]

        monkeypatch.setattr(ers_fatus_trade, "afetch_trade_data", fake_afetch)
        result = asyncio.run(agricultural_trade_periods("summary"))
        assert result == [
            {"label": "Fiscal year", "value": "Fiscal year"},
            {"label": "Monthly", "value": "Monthly"},
        ]

    def test_periods_default_to_exports_for_unknown_table(self, monkeypatch):
        """An unknown table falls back to the year-to-date exports table."""
        from openbb_government_us.usda.usda_router import agricultural_trade_periods

        async def fake_afetch(**kwargs):
            return [make_row(table="exports_ytd", time_period="October")]

        monkeypatch.setattr(ers_fatus_trade, "afetch_trade_data", fake_afetch)
        result = asyncio.run(agricultural_trade_periods("bogus"))
        assert result == [{"label": "Monthly", "value": "Monthly"}]

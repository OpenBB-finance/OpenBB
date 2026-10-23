"""Tests for the USDA ERS farm income and wealth statistics utils and model."""

import asyncio
import csv
import io
import zipfile
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.farm_income_and_wealth_statistics import (
    FarmIncomeAndWealthStatisticsData,
    FarmIncomeAndWealthStatisticsFetcher,
    FarmIncomeAndWealthStatisticsQueryParams,
)
from openbb_government_us.usda.utils import ers_farm_income_and_wealth_statistics as fiw
from openbb_government_us.usda.utils.ers_farm_income_and_wealth_statistics import (
    RELEASE_ZIP,
    STATE_LABELS,
    TABLE_LABELS,
    TABLE_PREFIXES,
    US_ONLY_TABLES,
    allowed_states,
    clean_unit,
    extract_csv_text,
    extract_release_zip,
    parse_amount,
    parse_rows,
    state_options,
)

CSV_HEADER = [
    "Year",
    "State",
    "artificialKey",
    "VariableDescriptionTotal",
    "VariableDescriptionPart1",
    "VariableDescriptionPart2",
    "Amount",
    "unit_desc",
    "PublicationDate",
    "Source",
    "ChainType_GDP_Deflator",
]

DIRTY_UNIT = "$1,000���"

SAMPLE_ROWS = [
    ["2023", "US", "FIAUSGCI", "Gross cash income", "All", "", "580000", DIRTY_UNIT],
    ["2024", "US", "FIAUSGCI", "Gross cash income", "All", "", "572008", DIRTY_UNIT],
    ["2025", "US", "FIAUSGCI", "Gross cash income", "All", "", "602726", DIRTY_UNIT],
    ["2023", "US", "FIAUSNFI", "Net farm income", "All", "", "147084", DIRTY_UNIT],
    ["2024", "US", "FIAUSNFI", "Net farm income", "All", "", "127542", DIRTY_UNIT],
    ["2025", "US", "FIAUSNFI", "Net farm income", "All", "", "154537", DIRTY_UNIT],
    ["2023", "IA", "FIAIAGCI", "Gross cash income", "All", "", "40000", DIRTY_UNIT],
    ["2024", "IA", "FIAIAGCI", "Gross cash income", "All", "", "41000", DIRTY_UNIT],
    [
        "2024",
        "US",
        "EXAUSTOT",
        "Total production expenses",
        "Total",
        "",
        "",
        DIRTY_UNIT,
    ],
    ["2024", "US", "FEAUSEQ", "Farm equity", "Equity", "", "3400000", DIRTY_UNIT],
    ["2024", "US", "FAAUSAST", "Farm assets", "Assets", "", "4200000", DIRTY_UNIT],
    ["2024", "US", "FDAUSDBT", "Farm debt", "Debt", "", "800000", DIRTY_UNIT],
    ["2023", "US", "RTAUSATR", "Asset turnover ratio", "", "", "0.16", "Ratio"],
    ["2024", "US", "RTAUSATR", "Asset turnover ratio", "", "", "0.14", "Ratio"],
    ["2024", "US", "RTAUSROR", "Rate of return", "", "", "7.28", "Percent"],
    [
        "2024",
        "US",
        "CRAUSBEET",
        "Sugar beets area",
        "Sugar beets",
        "",
        "1100",
        "1,000 acres",
    ],
]


def build_csv(rows: list[list[str]]) -> str:
    """Build CSV text from header and partial rows padded to full width."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_HEADER)
    for row in rows:
        padded = row + [""] * (len(CSV_HEADER) - len(row))
        writer.writerow(padded)
    return buffer.getvalue()


def build_zip(
    csv_text: str,
    member: str = "FarmIncome_WealthStatisticsData_February2026.csv",
) -> bytes:
    """Zip one CSV member into raw archive bytes."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member, csv_text.encode("utf-8-sig"))
    return buffer.getvalue()


SAMPLE_CSV = build_csv(SAMPLE_ROWS)
SAMPLE_ZIP = build_zip(SAMPLE_CSV)

SAMPLE_HTML = (
    "<h2>Charts and Maps Data Visualizations</h2>"
    '<ul><li><a href="/media/999/ignore-me.zip">chart</a></li></ul>'
    "<h2>Download All Data in CSV File Format (ZIP)</h2>"
    "<ul>"
    '<li><a href="/media/20808/february-5-2026-release.zip" class="usa-link">'
    "February 5, 2026 release</a></li>"
    '<li><a href="/media/4866/september-3-2025-release.zip" class="usa-link">'
    "September 3, 2025 release</a></li>"
    "</ul>"
    "<h2>Archive of Suspended Tables</h2>"
)


def make_record(**overrides) -> dict:
    """Build a parsed row record with optional field overrides."""
    record = {
        "prefix": "FI",
        "order": 0,
        "year": 2024,
        "state": "US",
        "line_item": "Gross cash income",
        "part_1": "All",
        "part_2": None,
        "unit": "$1,000",
        "amount": 572008.0,
    }
    record.update(overrides)
    return record


class TestErsFarmIncomeAndWealthStatisticsUtils:
    """Tests for the ers_farm_income_and_wealth_statistics utils module."""

    def test_table_catalog(self):
        """The catalog holds ten tables, each mapped to a label and prefixes."""
        assert len(TABLE_PREFIXES) == 10
        assert set(TABLE_PREFIXES) == set(TABLE_LABELS)
        assert TABLE_PREFIXES["income_statement"] == ("FI",)
        assert TABLE_PREFIXES["balance_sheet"] == ("FA", "FD", "FE")
        assert {
            "balance_sheet",
            "financial_ratios",
            "farm_business_income",
        } == US_ONLY_TABLES

    def test_state_catalog(self):
        """The state map covers the U.S. aggregate plus the fifty states."""
        assert len(STATE_LABELS) == 51
        assert STATE_LABELS["US"] == "United States"
        assert STATE_LABELS["IA"] == "Iowa"

    def test_allowed_states(self):
        """State tables allow all codes; U.S.-only tables allow only 'US'."""
        assert allowed_states("balance_sheet") == ("US",)
        assert allowed_states("financial_ratios") == ("US",)
        assert allowed_states("income_statement") == tuple(STATE_LABELS)
        assert len(allowed_states("cash_receipts")) == 51

    def test_state_options(self):
        """State options are label/value pairs scoped to the table."""
        assert state_options("balance_sheet") == [
            {"label": "United States", "value": "US"}
        ]
        options = state_options("income_statement")
        assert len(options) == 51
        assert options[0] == {"label": "United States", "value": "US"}
        assert {"label": "Iowa", "value": "IA"} in options

    def test_extract_release_zip(self):
        """The first zip under the download heading is the latest release."""
        assert (
            extract_release_zip(SAMPLE_HTML)
            == "/media/20808/february-5-2026-release.zip"
        )

    def test_extract_release_zip_missing_heading(self):
        """A page without the download heading returns None."""
        assert extract_release_zip("<h2>Something else</h2>") is None

    def test_extract_release_zip_no_zip(self):
        """The download heading with no zip link returns None."""
        html = "<h2>Download All Data in CSV File Format (ZIP)</h2><ul></ul>"
        assert extract_release_zip(html) is None

    def test_extract_release_zip_relative_path(self):
        """A relative zip href is normalized to a leading slash."""
        html = (
            "<h2>Download All Data in CSV File Format (ZIP)</h2>"
            '<ul><li><a href="media/1/x.zip">x</a></li></ul>'
        )
        assert extract_release_zip(html) == "/media/1/x.zip"

    def test_clean_unit(self):
        """Mis-decoded no-break-space bytes are stripped from units."""
        assert clean_unit(DIRTY_UNIT) == "$1,000"
        assert clean_unit("$1,000 per farm\xa0") == "$1,000 per farm"
        assert clean_unit("Ratio") == "Ratio"

    def test_parse_amount(self):
        """Amounts parse to floats, keeping sign and precision, blanks to None."""
        assert parse_amount("572008") == 572008.0
        assert parse_amount("-7744461") == -7744461.0
        assert parse_amount("133246036.87") == 133246036.87
        assert parse_amount("") is None
        assert parse_amount(None) is None
        assert parse_amount("n/a") is None

    def test_parse_rows_filters_prefix_and_state(self):
        """Only rows of the table's prefixes and the chosen state are kept."""
        rows = parse_rows(SAMPLE_CSV, ("FI",), "US")
        assert {row["line_item"] for row in rows} == {
            "Gross cash income",
            "Net farm income",
        }
        assert all(row["state"] == "US" for row in rows)
        assert all(row["prefix"] == "FI" for row in rows)

    def test_parse_rows_keeps_state_slice(self):
        """A state slice keeps only that state's rows."""
        rows = parse_rows(SAMPLE_CSV, ("FI",), "IA")
        assert {row["year"] for row in rows} == {2023, 2024}
        assert all(row["state"] == "IA" for row in rows)

    def test_parse_rows_cleans_unit_and_amount(self):
        """Rows clean the unit and coerce the amount to a float or None."""
        rows = parse_rows(SAMPLE_CSV, ("FI",), "US")
        assert all(row["unit"] == "$1,000" for row in rows)
        assert all(isinstance(row["year"], int) for row in rows)
        expenses = parse_rows(SAMPLE_CSV, ("EX",), "US")
        assert expenses[0]["amount"] is None

    def test_parse_rows_order_and_parts(self):
        """Records carry file order and the component description parts."""
        rows = parse_rows(SAMPLE_CSV, ("CR",), "US")
        assert len(rows) == 1
        assert rows[0]["part_1"] == "Sugar beets"
        assert rows[0]["part_2"] is None
        assert rows[0]["unit"] == "1,000 acres"
        assert rows[0]["order"] == 0

    def test_extract_csv_text(self):
        """The single CSV member is extracted and decoded from the zip."""
        text = extract_csv_text(SAMPLE_ZIP)
        assert text.splitlines()[0].startswith("Year,State,artificialKey")
        assert "Gross cash income" in text

    def test_aresolve_release_zip(self, monkeypatch, tmp_path):
        """The resolver extracts the latest release zip from the subpage."""
        monkeypatch.setenv("OPENBB_USDA_CACHE_DIR", str(tmp_path))

        async def fake_download(url):
            return SAMPLE_HTML.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client._download", fake_download
        )
        path = asyncio.run(fiw.aresolve_release_zip())
        assert path == "/media/20808/february-5-2026-release.zip"

    def test_aresolve_release_zip_falls_back(self, monkeypatch, tmp_path):
        """An unparseable subpage falls back to the hardcoded release zip."""
        monkeypatch.setenv("OPENBB_USDA_CACHE_DIR", str(tmp_path))

        async def fake_download(url):
            return b"<h2>No download section here</h2>"

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client._download", fake_download
        )
        assert asyncio.run(fiw.aresolve_release_zip()) == RELEASE_ZIP

    def test_aresolve_release_zip_uses_cache(self, monkeypatch, tmp_path):
        """The resolved path is cached, so the subpage is fetched once."""
        monkeypatch.setenv("OPENBB_USDA_CACHE_DIR", str(tmp_path))
        calls = []

        async def fake_download(url):
            calls.append(url)
            return SAMPLE_HTML.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client._download", fake_download
        )
        first = asyncio.run(fiw.aresolve_release_zip())
        second = asyncio.run(fiw.aresolve_release_zip())
        assert first == second == "/media/20808/february-5-2026-release.zip"
        assert len(calls) == 1

    def test_afetch_dataset(self, monkeypatch):
        """afetch_dataset resolves the zip, fetches it, and decodes the CSV."""

        async def fake_resolve():
            return "/media/20808/february-5-2026-release.zip"

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            assert media_path == "/media/20808/february-5-2026-release.zip"
            return SAMPLE_ZIP

        monkeypatch.setattr(fiw, "aresolve_release_zip", fake_resolve)
        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        text = asyncio.run(fiw.afetch_dataset())
        assert "Net farm income" in text

    def test_afetch_table(self, monkeypatch):
        """afetch_table parses only the requested table and state."""

        async def fake_dataset():
            return SAMPLE_CSV

        monkeypatch.setattr(fiw, "afetch_dataset", fake_dataset)
        rows = asyncio.run(fiw.afetch_table("income_statement", "US"))
        assert {row["line_item"] for row in rows} == {
            "Gross cash income",
            "Net farm income",
        }


class TestFarmIncomeAndWealthStatistics:
    """Tests for the FarmIncomeAndWealthStatistics model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = FarmIncomeAndWealthStatisticsFetcher.transform_query(
            {"table": "cash_receipts", "state": "IA", "start_year": 2020}
        )
        assert isinstance(query, FarmIncomeAndWealthStatisticsQueryParams)
        assert query.table == "cash_receipts"
        assert query.state == "IA"
        assert query.start_year == 2020

    def test_table_defaults_and_blank(self):
        """The table defaults to the income statement and blanks fall back."""
        assert FarmIncomeAndWealthStatisticsQueryParams().table == "income_statement"
        assert (
            FarmIncomeAndWealthStatisticsQueryParams(table="").table
            == "income_statement"
        )
        assert (
            FarmIncomeAndWealthStatisticsQueryParams(table=["balance_sheet"]).table
            == "balance_sheet"
        )

    def test_unknown_table_raises(self):
        """Unknown tables raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus.*income_statement"):
            FarmIncomeAndWealthStatisticsQueryParams(table="bogus")

    def test_state_defaults_and_normalizes(self):
        """State defaults to US, uppercases, and takes the first of a list."""
        assert FarmIncomeAndWealthStatisticsQueryParams().state == "US"
        assert FarmIncomeAndWealthStatisticsQueryParams(state="").state == "US"
        assert FarmIncomeAndWealthStatisticsQueryParams(state="ia").state == "IA"
        assert FarmIncomeAndWealthStatisticsQueryParams(state=["ny"]).state == "NY"

    def test_unknown_state_raises(self):
        """An unknown state code raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid state: ZZ"):
            FarmIncomeAndWealthStatisticsQueryParams(state="ZZ")

    def test_state_scoped_to_table(self):
        """A state outside a U.S.-only table's scope raises OpenBBError."""
        with pytest.raises(
            OpenBBError, match="Invalid state 'IA' for table 'balance_sheet'"
        ):
            FarmIncomeAndWealthStatisticsQueryParams(table="balance_sheet", state="IA")
        query = FarmIncomeAndWealthStatisticsQueryParams(
            table="income_statement", state="IA"
        )
        assert query.state == "IA"

    def test_aextract_data_passes_table_and_state(self, monkeypatch):
        """aextract_data forwards the table and state to afetch_table."""
        calls = []

        async def fake_afetch_table(table, state):
            calls.append((table, state))
            return parse_rows(SAMPLE_CSV, TABLE_PREFIXES[table], state)

        monkeypatch.setattr(fiw, "afetch_table", fake_afetch_table)
        query = FarmIncomeAndWealthStatisticsFetcher.transform_query(
            {"table": "income_statement", "state": "IA"}
        )
        records = asyncio.run(
            FarmIncomeAndWealthStatisticsFetcher.aextract_data(query, None)
        )
        assert calls == [("income_statement", "IA")]
        assert all(record["state"] == "IA" for record in records)

    def test_transform_data_pivots_years_into_columns(self):
        """Each line item is one row with a value column per year."""
        records = [
            make_record(year=2023, amount=580000.0, order=0),
            make_record(year=2024, amount=572008.0, order=1),
            make_record(year=2025, amount=602726.0, order=2),
        ]
        query = FarmIncomeAndWealthStatisticsFetcher.transform_query({})
        data = FarmIncomeAndWealthStatisticsFetcher.transform_data(query, records)
        assert len(data) == 1
        dumped = data[0].model_dump(by_alias=True)
        assert dumped["2023"] == 580000.0
        assert dumped["2025"] == 602726.0
        assert dumped["line_item"] == "Gross cash income"
        assert dumped["state"] == "United States"
        assert not any(key.startswith("_") for key in dumped)

    def test_transform_data_year_columns_chronological(self):
        """Year columns are emitted oldest-first regardless of input order."""
        records = [
            make_record(year=2025, amount=3.0, order=2),
            make_record(year=2023, amount=1.0, order=0),
            make_record(year=2024, amount=2.0, order=1),
        ]
        query = FarmIncomeAndWealthStatisticsFetcher.transform_query({})
        data = FarmIncomeAndWealthStatisticsFetcher.transform_data(query, records)
        dumped = data[0].model_dump(by_alias=True)
        assert [k for k in dumped if k.isdigit()] == ["2023", "2024", "2025"]

    def test_transform_data_orders_balance_sheet_assets_debt_equity(self):
        """Balance-sheet rows sort assets, then debt, then equity by prefix."""
        records = [
            make_record(prefix="FE", line_item="Farm equity", amount=3.0, order=0),
            make_record(prefix="FA", line_item="Farm assets", amount=1.0, order=1),
            make_record(prefix="FD", line_item="Farm debt", amount=2.0, order=2),
        ]
        query = FarmIncomeAndWealthStatisticsFetcher.transform_query(
            {"table": "balance_sheet"}
        )
        data = FarmIncomeAndWealthStatisticsFetcher.transform_data(query, records)
        assert [row.line_item for row in data] == [
            "Farm assets",
            "Farm debt",
            "Farm equity",
        ]

    def test_transform_data_single_table_file_order(self):
        """A single-prefix table keeps line items in source file order."""
        records = [
            make_record(line_item="Gross cash income", order=0, amount=1.0),
            make_record(line_item="Net farm income", order=1, amount=2.0),
        ]
        query = FarmIncomeAndWealthStatisticsFetcher.transform_query({})
        data = FarmIncomeAndWealthStatisticsFetcher.transform_data(query, records)
        assert [row.line_item for row in data] == [
            "Gross cash income",
            "Net farm income",
        ]

    def test_transform_data_filters_years(self):
        """start_year and end_year select which year columns appear."""
        records = [make_record(year=year, order=year) for year in (2022, 2023, 2024)]
        query = FarmIncomeAndWealthStatisticsFetcher.transform_query(
            {"start_year": 2023, "end_year": 2023}
        )
        data = FarmIncomeAndWealthStatisticsFetcher.transform_data(query, records)
        dumped = data[0].model_dump(by_alias=True)
        assert [k for k in dumped if k.isdigit()] == ["2023"]

    def test_transform_data_mixed_units_are_separate_rows(self):
        """Same-name items with different units stay distinct rows."""
        records = [
            make_record(line_item="X", unit="Ratio", amount=0.1, order=0),
            make_record(line_item="X", unit="Percent", amount=7.0, order=1),
        ]
        query = FarmIncomeAndWealthStatisticsFetcher.transform_query(
            {"table": "financial_ratios"}
        )
        data = FarmIncomeAndWealthStatisticsFetcher.transform_data(query, records)
        assert {row.unit for row in data} == {"Ratio", "Percent"}

    def test_transform_data_empty_raises(self):
        """No records surviving the filters raises EmptyDataError."""
        query = FarmIncomeAndWealthStatisticsFetcher.transform_query(
            {"start_year": 2100}
        )
        with pytest.raises(EmptyDataError, match="No records match"):
            FarmIncomeAndWealthStatisticsFetcher.transform_data(
                query, [make_record(year=2024)]
            )

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served row key."""
        records = [make_record(year=2024, order=0)]
        query = FarmIncomeAndWealthStatisticsFetcher.transform_query({})
        data = FarmIncomeAndWealthStatisticsFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        schema = FarmIncomeAndWealthStatisticsData.model_json_schema(
            by_alias=True, mode="serialization"
        )
        column_fields = [to_snake(key) for key in schema["properties"]]
        assert column_fields, "no column definitions generated"
        for field in column_fields:
            assert field in served, field
        non_year_served = {key for key in served if not key.isdigit()}
        assert non_year_served == set(column_fields)

    def test_widget_config_metadata(self):
        """The whole-widget config carries the ERS category and source."""
        config = FarmIncomeAndWealthStatisticsData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]

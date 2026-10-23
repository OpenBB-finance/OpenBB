"""Tests for the USDA ERS food expenditure series utils and model."""

import asyncio
import csv as _csv
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.helpers import to_snake_case

from openbb_government_us.usda.models.food_expenditure_series import (
    DEFAULT_TABLE,
    FoodExpenditureSeriesData,
    FoodExpenditureSeriesFetcher,
    FoodExpenditureSeriesQueryParams,
)
from openbb_government_us.usda.utils import ers_food_expenditure_series
from openbb_government_us.usda.utils.ers_food_expenditure_series import (
    FOOD_AND_ALCOHOL_LABELS,
    FOOD_EXPENDITURE_FILES,
    PRODUCT_PAGE,
    STATES,
    afetch_table,
    clean_header,
    parse_table,
    resolve_media_path,
)


def _csv_text(header: list[str], rows: list[list]) -> str:
    """Render a header and rows as CSV text."""
    buffer = StringIO()
    writer = _csv.writer(buffer)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


FOOD_ALCOHOL_HEADER = ["Year", *[f"value {i}" for i in range(26)]]
FOOD_ALCOHOL_CSV = _csv_text(
    FOOD_ALCOHOL_HEADER,
    [
        ["2024", *[str(float(i)) for i in range(26)]],
        ["2025", *[str(float(i) + 100) for i in range(26)]],
        ["", *["1.0" for _ in range(26)]],
        ["notayear", *["2.0" for _ in range(26)]],
    ],
)

PURCHASER_HEADER = [
    "Year",
    "Household purchases of food at home (millions of nominal U.S. dollars)",
    "Government purchases of food at home (millions of nominal U.S. dollars)",
    "Home production of food at home (millions of nominal U.S. dollars)",
    "Household purchases of food at home (millions of constant U.S. dollars (2025=100))",
    "Government purchases of food at home (millions of constant U.S. dollars (2025=100))",
    "Home production of food at home (millions of constant U.S. dollars (2025=100))",
    "Household purchases of food away from home (millions of nominal U.S. dollars)",
    "Government purchases of food away from home (millions of nominal U.S. dollars)",
    "Businesses purchases of food away from home (millions of nominal U.S. dollars)",
    "Household purchases of food away from home (millions of constant U.S. dollars (2025=100))",
    "Government purchases of food away from home (millions of constant U.S. dollars (2025=100))",
    "Businesses purchases of food away from home (millions of constant U.S. dollars (2025=100))",
]
PURCHASER_CSV = _csv_text(
    PURCHASER_HEADER,
    [
        [
            "2025",
            "10",
            "11",
            "12",
            "110",
            "111",
            "112",
            "20",
            "21",
            "22",
            "120",
            "121",
            "122",
        ],
    ],
)

NORMALIZED_HEADER = [
    "Year",
    "Food-at-home nominal food expenditure share of disposable personal income, household final users (percentage)",
    "Food-away-from-home nominal food expenditure share of disposable personal income, household final users (percentage)",
    "Total nominal food expenditure share of disposable personal income, household final users (percentage)",
    "Food-at-home share of nominal food expenditures, household final users (percentage)",
    "Food-away-from-home share of nominal food expenditures, household final users (percentage)",
    "Food-at-home expenditures per household, household final users (nominal U.S. dollars)",
    "Food-away-from-home expenditures per household, household final users (nominal U.S. dollars)",
    "Total food expenditures per household, household final users (nominal U.S. dollars)",
    "Food-at-home expenditures per household, household final users (constant U.S. dollars (2025=100))",
    "Food-away-from-home expenditures per household, household final users (constant U.S. dollars (2025=100))",
    "Total food expenditures per household, household final users (constant U.S. dollars (2025=100))",
    "Food-at-home share of nominal food expenditures, all purchasers (percentage)",
    "Food-away-from-home share of nominal food expenditures, all purchasers (percentage)",
    "Food-at-home expenditures per capita, all purchasers (nominal U.S. dollars)",
    "Food-away-from-home expenditures per capita, all purchasers (nominal U.S. dollars)",
    "Total food expenditures per capita, all purchasers (nominal U.S. dollars)",
    "Food-at-home expenditures per capita, all purchasers (constant U.S. dollars (2025=100))",
    "Food-away-from-home expenditures per capita, all purchasers (constant U.S. dollars (2025=100))",
    "Total food expenditures per capita, all purchasers (constant U.S. dollars (2025=100))",
]
NORMALIZED_CSV = _csv_text(
    NORMALIZED_HEADER,
    [["2025", *[str(float(i)) for i in range(1, 20)]]],
)

MONTHLY_HEADER = [
    "Year",
    "Month",
    "Food-at-home sales with taxes and tips (millions of nominal U.S. dollars)",
    "Food-away-from-home sales with taxes and tips (millions of nominal U.S. dollars)",
    "Total food sales with taxes and tips (millions of nominal U.S. dollars)",
    "Food-at-home sales with taxes and tips (millions of constant U.S. dollars (2025=100))",
    "Food-away-from-home sales with taxes and tips (millions of constant U.S. dollars (2025=100))",
    "Total food sales with taxes and tips (millions of constant U.S. dollars (2025=100))",
]
MONTHLY_CSV = _csv_text(
    MONTHLY_HEADER,
    [
        ["2025", "March", "3", "3.5", "6.5", "30", "35", "65"],
        ["2025", "January", "1", "1.5", "2.5", "10", "15", "25"],
        ["2024", "December", "9", "9.5", "18.5", "90", "95", "185"],
        ["2025", "February", "", "", "", "", "", ""],
    ],
)

STATE_HEADER = [
    "Year",
    "State",
    "Food-at-home sales with taxes and tips (millions of nominal U.S. dollars)",
    "Food-away-from-home sales with taxes and tips (millions of nominal U.S. dollars)",
    "Total food sales with taxes and tips (millions of nominal U.S. dollars)",
    "Food-at-home sales with taxes and tips (millions of constant U.S. dollars (2025=100))",
    "Food-away-from-home sales with taxes and tips (millions of constant U.S. dollars (2025=100))",
    "Total food sales with taxes and tips (millions of constant U.S. dollars (2025=100))",
]
STATE_CSV = _csv_text(
    STATE_HEADER,
    [
        ["2025", "California", "100", "200", "300", "90", "190", "280"],
        ["2025", "Alabama", "10", "20", "30", "9", "19", "28"],
        ["2024", "California", "95", "195", "290", "85", "185", "270"],
    ],
)


class TestErsFoodExpenditureSeriesUtils:
    """Tests for the ers_food_expenditure_series utils module."""

    def test_catalog_contents(self):
        """The catalog holds the seven current tables and their file maps."""
        assert list(FOOD_EXPENDITURE_FILES) == [
            "food_and_alcohol",
            "by_final_purchaser",
            "normalized",
            "monthly",
            "monthly_by_outlet",
            "state",
            "state_per_capita",
        ]
        for config in FOOD_EXPENDITURE_FILES.values():
            assert config["label"]
            assert config["dims"][0] == "year"
            assert config["files"]
            for path in config["files"].values():
                assert path.startswith("/media/") and path.endswith(".csv")
        assert len(FOOD_AND_ALCOHOL_LABELS) == 26
        assert len(STATES) == 51

    def test_resolve_media_path_measure_and_taxes(self):
        """food_and_alcohol keys the file on both measure and taxes."""
        assert (
            resolve_media_path("food_and_alcohol", "nominal", "with")
            == "/media/5188/nominal-food-and-alcohol-expenditures-with-taxes-and-tips-for-all-purchasers.csv"
        )
        assert (
            resolve_media_path("food_and_alcohol", "constant", "without")
            == "/media/5194/constant-dollar-food-and-alcohol-expenditures-without-taxes-and-tips-for-all-purchasers.csv"
        )

    def test_resolve_media_path_taxes_only(self):
        """state keys the file on taxes alone, ignoring measure."""
        with_path = resolve_media_path("state", "nominal", "with")
        also_with = resolve_media_path("state", "constant", "with")
        without_path = resolve_media_path("state_per_capita", "nominal", "without")
        assert with_path == also_with
        assert with_path.endswith(
            "state-food-sales-with-taxes-and-tips-for-all-purchasers.csv"
        )
        assert without_path.endswith(
            "state-food-sales-per-capita-without-taxes-and-tips-for-all-purchasers.csv"
        )

    def test_resolve_media_path_single_file(self):
        """monthly ignores both selectors and returns its one file."""
        assert resolve_media_path("monthly", "nominal", "with") == resolve_media_path(
            "monthly", "constant", "without"
        )

    def test_clean_header_strips_taxes_and_reads_measure(self):
        """clean_header removes the tax phrase and unit and reads the measure."""
        assert clean_header(
            "Food-at-home sales with taxes and tips (millions of nominal U.S. dollars)"
        ) == ("Food-at-home sales", "nominal")
        assert clean_header(
            "Total food sales without taxes and tips (millions of constant U.S. dollars (2025=100))"
        ) == ("Total food sales", "constant")

    def test_clean_header_percentage_and_bare(self):
        """A percentage unit yields no measure; a bare header passes through."""
        label, measure = clean_header(
            "Total nominal food expenditure share of disposable personal income, household final users (percentage)"
        )
        assert measure is None
        assert label.endswith("household final users")
        assert clean_header("Year") == ("Year", None)

    def test_parse_food_and_alcohol_uses_canonical_labels(self):
        """The food_and_alcohol table labels its 26 columns by position."""
        records = parse_table(FOOD_ALCOHOL_CSV, "food_and_alcohol")
        assert len(records) == 52
        year_2024 = [r for r in records if r["year"] == 2024]
        assert [r["category"] for r in year_2024] == list(FOOD_AND_ALCOHOL_LABELS)
        assert all(r["measure"] is None for r in year_2024)
        grocery = next(
            r for r in year_2024 if r["category"] == "Food sales at grocery stores"
        )
        assert grocery["value"] == 0.0
        assert year_2024[0]["month"] is None
        assert year_2024[0]["state"] is None

    def test_parse_skips_blank_and_nonnumeric_years(self):
        """Rows with a blank or non-numeric year are dropped."""
        records = parse_table(FOOD_ALCOHOL_CSV, "food_and_alcohol")
        assert {r["year"] for r in records} == {2024, 2025}

    def test_parse_purchaser_reads_measure_per_column(self):
        """by_final_purchaser tags each column's measure from its unit."""
        records = parse_table(PURCHASER_CSV, "by_final_purchaser")
        nominal = {
            r["category"]: r["value"] for r in records if r["measure"] == "nominal"
        }
        constant = {
            r["category"]: r["value"] for r in records if r["measure"] == "constant"
        }
        assert nominal["Household purchases of food at home"] == 10.0
        assert constant["Household purchases of food at home"] == 110.0
        assert nominal["Businesses purchases of food away from home"] == 22.0

    def test_parse_normalized_percentage_always_untagged(self):
        """normalized percentage columns carry no measure tag."""
        records = parse_table(NORMALIZED_CSV, "normalized")
        untagged = [r for r in records if r["measure"] is None]
        assert len(untagged) == 7
        assert all("share" in r["category"] for r in untagged)

    def test_parse_monthly_reads_month_dimension(self):
        """monthly carries the month dimension and skips blank value cells."""
        records = parse_table(MONTHLY_CSV, "monthly")
        assert {r["month"] for r in records} == {"March", "January", "December"}
        assert all(r["state"] is None for r in records)
        february = [r for r in records if r["month"] == "February"]
        assert february == []

    def test_parse_state_reads_state_dimension(self):
        """state carries the state dimension."""
        records = parse_table(STATE_CSV, "state")
        assert {r["state"] for r in records} == {"California", "Alabama"}
        assert all(r["month"] is None for r in records)

    def test_parse_empty_text(self):
        """Empty CSV text yields no records."""
        assert parse_table("", "monthly") == []

    def test_afetch_table(self, monkeypatch):
        """afetch_table resolves the path and parses the fetched content."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return STATE_CSV.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(afetch_table("state", "nominal", "without"))
        assert calls == [
            (
                "/media/5206/state-food-sales-without-taxes-and-tips-for-all-purchasers.csv",
                PRODUCT_PAGE,
            )
        ]
        assert {r["state"] for r in records} == {"California", "Alabama"}


class TestFoodExpenditureSeries:
    """Tests for the FoodExpenditureSeries model."""

    def test_transform_query_default_table(self):
        """transform_query defaults the table, measure, and taxes."""
        query = FoodExpenditureSeriesFetcher.transform_query({"start_year": 2000})
        assert isinstance(query, FoodExpenditureSeriesQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.measure == "nominal"
        assert query.taxes == "with"
        assert query.start_year == 2000

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert FoodExpenditureSeriesQueryParams(table=None).table == DEFAULT_TABLE  # ty: ignore[invalid-argument-type]
        assert FoodExpenditureSeriesQueryParams(table="").table == DEFAULT_TABLE

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        assert FoodExpenditureSeriesQueryParams(table="  monthly  ").table == "monthly"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            FoodExpenditureSeriesQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            FoodExpenditureSeriesQueryParams(table=123)  # ty: ignore[invalid-argument-type]

    def test_aextract_data_passes_selectors(self, monkeypatch):
        """aextract_data forwards the table, measure, and taxes selectors."""
        captured = {}

        async def fake_afetch_table(table, measure, taxes):
            captured["args"] = (table, measure, taxes)
            return [{"year": 2025}]

        monkeypatch.setattr(
            ers_food_expenditure_series, "afetch_table", fake_afetch_table
        )
        query = FoodExpenditureSeriesFetcher.transform_query(
            {"table": "state", "measure": "constant", "taxes": "without"}
        )
        records = asyncio.run(FoodExpenditureSeriesFetcher.aextract_data(query, None))
        assert captured["args"] == ("state", "constant", "without")
        assert records == [{"year": 2025}]

    def test_period_is_the_only_static_field(self):
        """The Data model exposes a single static 'period' field."""
        assert set(FoodExpenditureSeriesData.model_fields) == {"period"}

    def test_transform_data_pivots_food_and_alcohol(self):
        """food_and_alcohol pivots its categories into columns keyed by an annual period."""
        records = parse_table(FOOD_ALCOHOL_CSV, "food_and_alcohol")
        query = FoodExpenditureSeriesFetcher.transform_query({})
        data = FoodExpenditureSeriesFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2024", "2025"]
        dumped = data[0].model_dump(by_alias=True)
        assert dumped["period"] == "2024"
        assert dumped["Food sales at grocery stores"] == 0.0
        assert dumped["Total alcohol-away-from-home sales"] == 25.0

    def test_transform_data_folds_single_unit_into_columns(self):
        """A single-unit table folds its unit into each value column header."""
        records = parse_table(PURCHASER_CSV, "by_final_purchaser")
        nominal = FoodExpenditureSeriesFetcher.transform_data(
            FoodExpenditureSeriesFetcher.transform_query({"measure": "nominal"}),
            records,
        )[0].model_dump(by_alias=True)
        constant = FoodExpenditureSeriesFetcher.transform_data(
            FoodExpenditureSeriesFetcher.transform_query({"measure": "constant"}),
            records,
        )[0].model_dump(by_alias=True)
        assert nominal["period"] == "2025"
        assert (
            nominal[
                "Household purchases of food at home (millions of nominal U.S. dollars)"
            ]
            == 10.0
        )
        assert (
            constant[
                "Household purchases of food at home (millions of constant U.S. dollars (2025=100))"
            ]
            == 110.0
        )

    def test_transform_data_multi_unit_table_stays_unfolded(self):
        """The multi-unit normalized table keeps bare share columns under either measure."""
        records = parse_table(NORMALIZED_CSV, "normalized")
        for measure in ("nominal", "constant"):
            row = FoodExpenditureSeriesFetcher.transform_data(
                FoodExpenditureSeriesFetcher.transform_query({"measure": measure}),
                records,
            )[0].model_dump(by_alias=True)
            shares = [k for k in row if "share" in k]
            assert len(shares) == 7
            assert row["period"] == "2025"
            assert not any("(percentage)" in k for k in row)

    def test_transform_data_folds_month_into_period(self):
        """monthly folds the month into the period and sorts chronologically."""
        records = parse_table(MONTHLY_CSV, "monthly")
        data = FoodExpenditureSeriesFetcher.transform_data(
            FoodExpenditureSeriesFetcher.transform_query({}), records
        )
        assert [row.period for row in data] == [
            "2024 December",
            "2025 January",
            "2025 March",
        ]

    def test_transform_data_filters_years(self):
        """start_year and end_year filter rows on the integer year."""
        records = parse_table(MONTHLY_CSV, "monthly")
        start = FoodExpenditureSeriesFetcher.transform_data(
            FoodExpenditureSeriesFetcher.transform_query({"start_year": 2025}), records
        )
        assert [row.period for row in start] == ["2025 January", "2025 March"]
        end = FoodExpenditureSeriesFetcher.transform_data(
            FoodExpenditureSeriesFetcher.transform_query({"end_year": 2024}), records
        )
        assert [row.period for row in end] == ["2024 December"]

    def test_transform_data_folds_varying_state_into_period(self):
        """state prefixes the varying state into the period label."""
        records = parse_table(STATE_CSV, "state")
        data = FoodExpenditureSeriesFetcher.transform_data(
            FoodExpenditureSeriesFetcher.transform_query({"table": "state"}), records
        )
        assert [row.period for row in data] == [
            "Alabama — 2025",
            "California — 2024",
            "California — 2025",
        ]

    def test_transform_data_state_filter_drops_constant_state(self):
        """Filtering to a single state leaves the period as the bare year."""
        records = parse_table(STATE_CSV, "state")
        data = FoodExpenditureSeriesFetcher.transform_data(
            FoodExpenditureSeriesFetcher.transform_query(
                {"table": "state", "state": "califor"}
            ),
            records,
        )
        assert [row.period for row in data] == ["2024", "2025"]

    def test_transform_data_state_filter_ignored_off_table(self):
        """A state filter does not empty a table without a state dimension."""
        records = parse_table(FOOD_ALCOHOL_CSV, "food_and_alcohol")
        data = FoodExpenditureSeriesFetcher.transform_data(
            FoodExpenditureSeriesFetcher.transform_query({"state": "california"}),
            records,
        )
        assert [row.period for row in data] == ["2024", "2025"]

    def test_transform_data_rows_unique_with_no_empty_columns(self):
        """Every served row is unique and no value column is entirely None."""
        records = parse_table(STATE_CSV, "state")
        data = FoodExpenditureSeriesFetcher.transform_data(
            FoodExpenditureSeriesFetcher.transform_query({"table": "state"}), records
        )
        dumped = [row.model_dump(by_alias=True) for row in data]
        periods = [row["period"] for row in dumped]
        assert len(periods) == len(set(periods))
        serialized = [tuple(sorted(row.items())) for row in dumped]
        assert len(serialized) == len(set(serialized))
        value_columns = [key for key in dumped[0] if key != "period"]
        assert value_columns
        for column in value_columns:
            assert any(row.get(column) is not None for row in dumped)

    def test_data_model_keeps_dynamic_columns_and_precision(self):
        """The Data model preserves dynamic value columns at full precision."""
        row = FoodExpenditureSeriesData.model_validate(
            {"period": "2025", "Total food sales": 190569.69123}
        )
        assert row.model_dump(by_alias=True)["Total food sales"] == 190569.69123

    def test_columns_defs_bind_to_served_keys(self):
        """Every generated column definition binds to a served row key."""
        records = parse_table(STATE_CSV, "state")
        data = FoodExpenditureSeriesFetcher.transform_data(
            FoodExpenditureSeriesFetcher.transform_query({"table": "state"}), records
        )
        served = set(data[0].model_dump(by_alias=True))
        schema = FoodExpenditureSeriesData.model_json_schema()
        column_fields = [
            to_snake_case(key)
            for key, prop in schema["properties"].items()
            if not prop.get("x-widget_config", {}).get("exclude")
        ]
        assert column_fields == ["period"]
        for field in column_fields:
            assert field in served
        assert "period" in served

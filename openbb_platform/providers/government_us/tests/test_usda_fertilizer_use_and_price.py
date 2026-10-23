"""Tests for the USDA ERS fertilizer use and price utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.usda.models.fertilizer_use_and_price import (
    DEFAULT_TABLE,
    FertilizerUseAndPriceData,
    FertilizerUseAndPriceFetcher,
    FertilizerUseAndPriceQueryParams,
)
from openbb_government_us.usda.utils import ers_fertilizer_use_and_price
from openbb_government_us.usda.utils.ers_fertilizer_use_and_price import (
    FERTILIZER_TABLES,
    PRODUCT_PAGE,
    WORKBOOK_MEDIA,
    _numeric,
    _sheet_rows,
    _year_of,
    afetch_table,
    parse_group_a,
    parse_group_b,
    parse_sheet,
)

TABLE1_ROWS = [
    ["Table 1. U.S. consumption of plant nutrients", "", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", "", ""],
    ["", "Primary nutrient content 1/", "", "", "", "", "Share of total", "", ""],
    [
        "Year ending June 30",
        "Nitrogen (N)",
        "Phosphate (P2O5)",
        "Potash (K2O)",
        "Total",
        "",
        "Nitrogen",
        "Phosphate",
        "Potash",
    ],
    ["", "", "", "", "", "", "", "", ""],
    ["", "----1,000 nutrient short tons----", "", "", "", "", "--Percent--", "", ""],
    [1960.0, 2738.0, 2572.4, 2153.3, 7463.7, "", 36.68421828315715, 34.4, 28.8],
    ["   1961", 3030.8, 2645.1, 2168.5, 7844.4, "", 38.6, 33.7, 27.6],
    [1962.0, "NA", 2807.0, 2270.5, 8447.5, "", 39.8, 33.2, 26.8],
    [1963.0, 1.0],
    ["1/ Includes Puerto Rico.", "", "", "", "", "", "", "", ""],
    [],
]

TABLE7_ROWS = [
    ["Table 7. Average U.S. farm prices of selected fertilizers", "", "", "", "", ""],
    ["", "", "", "", "", ""],
    [" Year", "Month", "Anhydrous ammonia", "Nitrogen solutions (30%)", "Urea", "AN"],
    ["", "", "", "", "", ""],
    ["", "", "Dollars per material short ton", "", "", ""],
    [1960.0, "  Apr.", 141.0, "NA", 117.0, 81.6],
    [1960.0, "  Sept.", 140.0, "NA", 117.0, 80.9],
    [1961.0],
    ["NA = Not available.", "", "", "", "", ""],
]

TABLE9_ROWS = [
    ["Table 9. Percent of corn acreage receiving nitrogen fertilizer", "", "", "", ""],
    ["", "", "", "", ""],
    ["State", 1964.0, 1965.0, 1966.0, 1967.0],
    ["", "", "", "", ""],
    ["", "    Percent", "", "", ""],
    ["Alabama", 99.0, 99.0, 100.0, 99.0],
    ["Colorado", "NA", "NA", "NA", "NA"],
    ["", "", "", "", ""],
    ["Illinois", 89.0, 90.0, 96.0, 93.0],
    ["Iowa", 80.0],
    ["U.S. average 1/", 85.0, 88.0, 91.0, 92.0],
    ["NA = Not available. Source data cover selected States.", "", "", "", ""],
    ["1/  U.S. average is an average of State application rates.", "", "", "", ""],
    ["Source: Taylor and USDA NASS.", "", "", "", ""],
    [],
]


class _FakeSheet:
    """Minimal xlrd worksheet stand-in backed by a grid of rows."""

    def __init__(self, grid: list[list]) -> None:
        self._grid = grid
        self.nrows = len(grid)
        self.ncols = max((len(row) for row in grid), default=0)

    def cell_value(self, r: int, c: int):
        """Return the cell at row r, column c, padding short rows with blanks."""
        row = self._grid[r]
        return row[c] if c < len(row) else ""


class _FakeWorkbook:
    """Minimal xlrd workbook stand-in indexing a list of _FakeSheet objects."""

    def __init__(self, sheets: list["_FakeSheet"]) -> None:
        self._sheets = sheets

    def sheet_by_index(self, index: int) -> "_FakeSheet":
        """Return the sheet at the given zero-based index."""
        return self._sheets[index]


class TestErsFertilizerUseAndPriceUtils:
    """Tests for the ers_fertilizer_use_and_price utils module."""

    def test_catalog_contents(self):
        """The catalog holds 32 tables, 8 national and 24 crop-by-State."""
        assert len(FERTILIZER_TABLES) == 32
        group_a = [k for k, c in FERTILIZER_TABLES.items() if c["group"] == "A"]
        group_b = [k for k, c in FERTILIZER_TABLES.items() if c["group"] == "B"]
        assert len(group_a) == 8
        assert len(group_b) == 24
        assert [FERTILIZER_TABLES[k]["sheet"] for k in FERTILIZER_TABLES] == list(
            range(1, 33)
        )
        for config in FERTILIZER_TABLES.values():
            assert config["label"].startswith("Table ")
            if config["group"] == "A":
                assert config["columns"]
            else:
                assert config["unit"] in ("Percent", "Pounds/acre")

    def test_catalog_farm_prices_has_month_column(self):
        """Only the farm-prices table carries a month sub-key column."""
        month_cols = {
            k: c["month_col"] for k, c in FERTILIZER_TABLES.items() if c["group"] == "A"
        }
        assert month_cols["farm_prices"] == 1
        assert all(v is None for k, v in month_cols.items() if k != "farm_prices")

    def test_year_of_variants(self):
        """_year_of reads floats, ints, and padded strings, else None."""
        assert _year_of(1960.0) == 1960
        assert _year_of(1980) == 1980
        assert _year_of("   1961") == 1961
        assert _year_of("Year ending June 30") is None
        assert _year_of("1/ Includes Puerto Rico.") is None
        assert _year_of(True) is None
        assert _year_of(None) is None
        assert _year_of(1899.0) is None
        assert _year_of(3000.0) is None

    def test_numeric_variants(self):
        """_numeric parses numbers and floatable strings, else None."""
        assert _numeric(5) == 5.0
        assert _numeric("5.5") == 5.5
        assert _numeric("NA") is None
        assert _numeric("") is None
        assert _numeric(None) is None

    def test_parse_group_a_pivots_series_and_skips_spacer(self):
        """Group A parse emits one record per mapped column, skipping spacers."""
        records = parse_group_a(TABLE1_ROWS, "us_plant_nutrient_consumption")
        years = {r["year"] for r in records}
        assert years == {1960, 1961, 1962, 1963}
        assert all(r["period"] is None for r in records)
        assert all(r["table"] == "us_plant_nutrient_consumption" for r in records)
        assert all(r["series"] != "" for r in records)
        row_1960 = {r["series"]: r["value"] for r in records if r["year"] == 1960}
        assert row_1960["Nitrogen (N)"] == 2738.0
        assert row_1960["Nitrogen share"] == 36.68421828315715
        assert "Total" in row_1960
        assert len(row_1960) == 7

    def test_parse_group_a_string_year_row(self):
        """A padded string year contributes records like a numeric year."""
        records = parse_group_a(TABLE1_ROWS, "us_plant_nutrient_consumption")
        row_1961 = {r["series"]: r["value"] for r in records if r["year"] == 1961}
        assert row_1961["Phosphate (P2O5)"] == 2645.1

    def test_parse_group_a_skips_na_cell(self):
        """A non-numeric cell drops just that series for the year."""
        records = parse_group_a(TABLE1_ROWS, "us_plant_nutrient_consumption")
        row_1962 = {r["series"]: r["value"] for r in records if r["year"] == 1962}
        assert "Nitrogen (N)" not in row_1962
        assert row_1962["Phosphate (P2O5)"] == 2807.0

    def test_parse_group_a_short_row_guard(self):
        """A truncated data row only emits the columns it actually has."""
        records = parse_group_a(TABLE1_ROWS, "us_plant_nutrient_consumption")
        row_1963 = {r["series"]: r["value"] for r in records if r["year"] == 1963}
        assert row_1963 == {"Nitrogen (N)": 1.0}

    def test_parse_group_a_month_key(self):
        """The farm-prices table populates the month period from column 1."""
        records = parse_group_a(TABLE7_ROWS, "farm_prices")
        periods = {r["period"] for r in records}
        assert periods == {"Apr.", "Sept."}
        apr = {r["series"]: r["value"] for r in records if r["period"] == "Apr."}
        assert apr["Anhydrous ammonia"] == 141.0
        assert "Nitrogen solutions (30%)" not in apr

    def test_parse_group_b_transposes_states(self):
        """Group B parse emits one record per State and year, renaming U.S. row."""
        records = parse_group_b(TABLE9_ROWS, "corn_nitrogen_share")
        states = {r["series"] for r in records}
        assert states == {"Alabama", "Illinois", "Iowa", "U.S. average"}
        assert all(r["period"] is None for r in records)
        alabama = {r["year"]: r["value"] for r in records if r["series"] == "Alabama"}
        assert alabama == {1964: 99.0, 1965: 99.0, 1966: 100.0, 1967: 99.0}

    def test_parse_group_b_skips_all_na_state(self):
        """A State with only 'NA' cells contributes no records."""
        records = parse_group_b(TABLE9_ROWS, "corn_nitrogen_share")
        assert "Colorado" not in {r["series"] for r in records}

    def test_parse_group_b_short_row_guard(self):
        """A truncated State row only emits its present year cells."""
        records = parse_group_b(TABLE9_ROWS, "corn_nitrogen_share")
        iowa = {r["year"]: r["value"] for r in records if r["series"] == "Iowa"}
        assert iowa == {1964: 80.0}

    def test_parse_group_b_no_header_returns_empty(self):
        """A sheet without a 'State' header row yields no records."""
        assert parse_group_b([["Nothing here"], ["", ""]], "corn_nitrogen_share") == []

    def test_parse_sheet_dispatches_by_group(self):
        """parse_sheet routes to the group-appropriate parser."""
        a_records = parse_sheet(TABLE1_ROWS, "us_plant_nutrient_consumption")
        b_records = parse_sheet(TABLE9_ROWS, "corn_nitrogen_share")
        assert a_records[0]["series"] == "Nitrogen (N)"
        assert b_records[0]["series"] == "Alabama"

    def test_sheet_rows_reads_workbook(self, monkeypatch):
        """_sheet_rows materializes a worksheet into padded row lists."""
        monkeypatch.setattr(
            "xlrd.open_workbook",
            lambda file_contents: _FakeWorkbook(
                [_FakeSheet([["a", "b"]]), _FakeSheet(TABLE9_ROWS)]
            ),
        )
        rows = _sheet_rows(b"binary", 1)
        assert rows[2][0] == "State"
        assert rows[9] == ["Iowa", 80.0, "", "", ""]

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches the workbook and parses the selected sheet."""
        calls: list = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return b"binary"

        sheets = [_FakeSheet([["toc"]])] + [
            _FakeSheet(TABLE1_ROWS if i == 1 else [["x"]]) for i in range(1, 33)
        ]
        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        monkeypatch.setattr(
            "xlrd.open_workbook", lambda file_contents: _FakeWorkbook(sheets)
        )
        records = asyncio.run(afetch_table("us_plant_nutrient_consumption"))
        assert calls == [(WORKBOOK_MEDIA, PRODUCT_PAGE)]
        assert {r["year"] for r in records} == {1960, 1961, 1962, 1963}


class TestFertilizerUseAndPrice:
    """Tests for the FertilizerUseAndPrice model."""

    def test_transform_query_default_table(self):
        """transform_query defaults the table and keeps year filters."""
        query = FertilizerUseAndPriceFetcher.transform_query({"start_year": 1990})
        assert isinstance(query, FertilizerUseAndPriceQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.start_year == 1990

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert FertilizerUseAndPriceQueryParams(table=None).table == DEFAULT_TABLE  # ty: ignore[invalid-argument-type]
        assert FertilizerUseAndPriceQueryParams(table="").table == DEFAULT_TABLE

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        query = FertilizerUseAndPriceQueryParams(table="  farm_prices  ")
        assert query.table == "farm_prices"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            FertilizerUseAndPriceQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            FertilizerUseAndPriceQueryParams(table=123)  # ty: ignore[invalid-argument-type]

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched: list = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(
            ers_fertilizer_use_and_price, "afetch_table", fake_afetch_table
        )
        query = FertilizerUseAndPriceFetcher.transform_query({"table": "farm_prices"})
        records = asyncio.run(FertilizerUseAndPriceFetcher.aextract_data(query, None))
        assert fetched == ["farm_prices"]
        assert records == [{"table": "farm_prices"}]

    def test_data_model_single_period_field(self):
        """The only statically served field is the pinned period label."""
        assert set(FertilizerUseAndPriceData.model_fields) == {"period"}

    def test_transform_data_pivots_group_a(self):
        """Group A series become columns, one period row per year, full precision."""
        records = parse_group_a(TABLE1_ROWS, "us_plant_nutrient_consumption")
        query = FertilizerUseAndPriceFetcher.transform_query({})
        data = FertilizerUseAndPriceFetcher.transform_data(query, records)
        dumped = [row.model_dump(by_alias=True) for row in data]
        row_1960 = next(row for row in dumped if row["period"] == "1960")
        assert row_1960["Nitrogen (N)"] == 2738.0
        assert row_1960["Nitrogen share"] == 36.68421828315715
        assert [row["period"] for row in dumped] == ["1960", "1961", "1962", "1963"]

    def test_transform_data_year_rows_chronological(self):
        """Year rows are emitted in ascending order regardless of input order."""
        records = [
            {"table": "t", "year": year, "period": None, "series": "x", "value": 1.0}
            for year in (1962, 1960, 1961)
        ]
        query = FertilizerUseAndPriceFetcher.transform_query({})
        data = FertilizerUseAndPriceFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["1960", "1961", "1962"]

    def test_transform_data_farm_prices_folds_month_into_period(self):
        """The farm-prices month is folded into the period label, chronological."""
        records = parse_group_a(TABLE7_ROWS, "farm_prices")
        query = FertilizerUseAndPriceFetcher.transform_query({"table": "farm_prices"})
        data = FertilizerUseAndPriceFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["1960 Apr.", "1960 Sept."]
        assert data[0].model_dump(by_alias=True)["Anhydrous ammonia"] == 141.0

    def test_transform_data_farm_prices_month_order_and_no_dupes(self):
        """Months sort chronologically and never collapse to a duplicate row."""
        records = [
            {
                "table": "farm_prices",
                "year": 1977,
                "period": m,
                "series": "X",
                "value": v,
            }
            for m, v in (("Dec.", 1.0), ("Mar.", 2.0), ("Oct.", 3.0), ("May", 4.0))
        ]
        query = FertilizerUseAndPriceFetcher.transform_query({"table": "farm_prices"})
        data = FertilizerUseAndPriceFetcher.transform_data(query, records)
        periods = [row.period for row in data]
        assert periods == ["1977 Mar.", "1977 May", "1977 Oct.", "1977 Dec."]
        assert len(periods) == len(set(periods))

    def test_transform_data_pivots_group_b_folds_unit(self):
        """Group B States become columns with the table's single unit folded in."""
        records = parse_group_b(TABLE9_ROWS, "corn_nitrogen_share")
        query = FertilizerUseAndPriceFetcher.transform_query(
            {"table": "corn_nitrogen_share"}
        )
        data = FertilizerUseAndPriceFetcher.transform_data(query, records)
        dumped = [row.model_dump(by_alias=True) for row in data]
        assert [row["period"] for row in dumped] == ["1964", "1965", "1966", "1967"]
        assert dumped[0]["Alabama (Percent)"] == 99.0
        assert dumped[0]["U.S. average (Percent)"] == 85.0
        assert dumped[0]["Illinois (Percent)"] == 89.0

    def test_transform_data_uniform_value_columns(self):
        """Every row carries the identical union of value columns, None-filled."""
        records = parse_group_b(TABLE9_ROWS, "corn_nitrogen_share")
        query = FertilizerUseAndPriceFetcher.transform_query(
            {"table": "corn_nitrogen_share"}
        )
        data = FertilizerUseAndPriceFetcher.transform_data(query, records)
        keysets = [set(row.model_dump(by_alias=True)) for row in data]
        assert all(keys == keysets[0] for keys in keysets)
        row_1966 = next(
            row.model_dump(by_alias=True) for row in data if row.period == "1966"
        )
        assert row_1966["Iowa (Percent)"] is None

    def test_transform_data_filters_years(self):
        """start_year and end_year filter rows on the integer year."""
        records = parse_group_a(TABLE1_ROWS, "us_plant_nutrient_consumption")
        start = FertilizerUseAndPriceFetcher.transform_data(
            FertilizerUseAndPriceFetcher.transform_query({"start_year": 1962}), records
        )
        assert {row.period for row in start} == {"1962", "1963"}
        end = FertilizerUseAndPriceFetcher.transform_data(
            FertilizerUseAndPriceFetcher.transform_query({"end_year": 1961}), records
        )
        assert {row.period for row in end} == {"1960", "1961"}
        window = FertilizerUseAndPriceFetcher.transform_data(
            FertilizerUseAndPriceFetcher.transform_query(
                {"start_year": 1961, "end_year": 1962}
            ),
            records,
        )
        assert {row.period for row in window} == {"1961", "1962"}

    def test_transform_data_empty_raises(self):
        """No matching rows raises EmptyDataError."""
        records = parse_group_a(TABLE1_ROWS, "us_plant_nutrient_consumption")
        with pytest.raises(EmptyDataError):
            FertilizerUseAndPriceFetcher.transform_data(
                FertilizerUseAndPriceFetcher.transform_query({"start_year": 2100}),
                records,
            )

    def test_data_model_dynamic_columns_and_precision(self):
        """The Data model preserves dynamic columns at full precision."""
        row = FertilizerUseAndPriceData.model_validate(
            {"period": "2014", "Nitrogen share": 57.1981723844188}
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["Nitrogen share"] == 57.1981723844188
        assert dumped["period"] == "2014"

    def test_data_model_coerces_null_tokens(self):
        """Placeholder tokens in value columns coerce to None via NullTokenMixin."""
        row = FertilizerUseAndPriceData.model_validate(
            {"period": "1960 Apr.", "Anhydrous ammonia": "--"}
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["period"] == "1960 Apr."
        assert dumped["Anhydrous ammonia"] is None

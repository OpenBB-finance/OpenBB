"""Tests for the USDA ERS fruit and tree nuts data utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.fruit_and_tree_nuts_data import (
    DEFAULT_CATEGORY,
    DEFAULT_TABLE,
    FruitAndTreeNutsData,
    FruitAndTreeNutsDataFetcher,
    FruitAndTreeNutsDataQueryParams,
    column_label,
)
from openbb_government_us.usda.utils import ers_fruit_and_tree_nuts_data
from openbb_government_us.usda.utils.ers_fruit_and_tree_nuts_data import (
    CATEGORY_LABELS,
    PRODUCT_PAGE,
    TABLE_TITLES,
    YEARBOOK_MEDIA,
    category_tables,
    parse_records,
    table_category,
)

HEADER = (
    "table_name,year_value,year_unit,year_start_month,month,variable,"
    "commodity_element,market_segment,geographic_extent,value,unit\n"
)


def _row(**kwargs) -> str:
    """Build one CSV data row from column keyword arguments."""
    cols = [
        "table_name",
        "year_value",
        "year_unit",
        "year_start_month",
        "month",
        "variable",
        "commodity_element",
        "market_segment",
        "geographic_extent",
        "value",
        "unit",
    ]
    defaults = {
        "year_unit": "Calendar year",
        "year_start_month": "NA",
        "month": "NA",
        "market_segment": "All",
        "geographic_extent": "United States",
    }
    values = []
    for col in cols:
        raw = str(kwargs.get(col, defaults.get(col, "")))
        values.append(f'"{raw}"' if "," in raw else raw)
    return ",".join(values) + "\n"


A1_ROWS = (
    _row(
        table_name="Table A-1--Fruit and tree nuts: Per capita availability",
        year_value="1976",
        variable="Per capita availability",
        commodity_element="Apples",
        market_segment="All",
        value="29.85728",
        unit="pounds, farm weight",
    )
    + _row(
        table_name="Table A-1--Fruit and tree nuts: Per capita availability",
        year_value="1976",
        variable="Per capita availability",
        commodity_element="Apples",
        market_segment="Fresh",
        value="17.08102",
        unit="pounds, farm weight",
    )
    + _row(
        table_name="Table A-1--Fruit and tree nuts: Per capita availability",
        year_value="1976",
        variable="Per capita availability",
        commodity_element="Cherries",
        market_segment="All",
        value="1.70954",
        unit="pounds, farm weight",
    )
    + _row(
        table_name="Table A-1--Fruit and tree nuts: Per capita availability",
        year_value="1977",
        variable="Per capita availability",
        commodity_element="Apples",
        market_segment="All",
        value="30.0",
        unit="pounds, farm weight",
    )
    + _row(
        table_name="Table A-1--Fruit and tree nuts: Per capita availability",
        year_value="1977",
        variable="Per capita availability",
        commodity_element="Apples",
        market_segment="Fresh",
        value="NA",
        unit="pounds, farm weight",
    )
    + _row(
        table_name="Table A-1--Fruit and tree nuts: Per capita availability",
        year_value="abcd",
        variable="Per capita availability",
        commodity_element="Apples",
        market_segment="All",
        value="99.0",
        unit="pounds, farm weight",
    )
)

B3_ROWS = (
    _row(
        table_name="Table B-3--Apples: Production, utilization, price",
        year_value="1980",
        variable="Production",
        commodity_element="Apples",
        market_segment="All",
        value="8818.4",
        unit="million pounds",
    )
    + _row(
        table_name="Table B-3--Apples: Production, utilization, price",
        year_value="1980",
        variable="Price received by growers",
        commodity_element="Apples",
        market_segment="Fresh",
        value="12.1",
        unit="cents per pound",
    )
    + _row(
        table_name="Table B-3--Apples: Production, utilization, price",
        year_value="1981",
        variable="Production",
        commodity_element="Apples",
        market_segment="All",
        value="7739.6",
        unit="million pounds",
    )
)

F1_ROWS = (
    _row(
        table_name="Table F-1--Tree nuts: Area bearing",
        year_value="1980/81",
        year_unit="Marketing year",
        variable="Area bearing",
        commodity_element="Almonds",
        value="326800",
        unit="acres",
    )
    + _row(
        table_name="Table F-1--Tree nuts: Area bearing",
        year_value="1980/81",
        year_unit="Marketing year",
        variable="Area bearing",
        commodity_element="Walnuts",
        value="179900",
        unit="acres",
    )
    + _row(
        table_name="Table F-1--Tree nuts: Area bearing",
        year_value="1981/82",
        year_unit="Marketing year",
        variable="Area bearing",
        commodity_element="Almonds",
        value="326200",
        unit="acres",
    )
)

B4_ROWS = (
    _row(
        table_name="Table B-4--Apples, fresh: Price received by growers, monthly",
        year_value="1981",
        month="January",
        variable="Price received by growers",
        commodity_element="Apples",
        market_segment="Fresh",
        value="0.15",
        unit="dollars per pound",
    )
    + _row(
        table_name="Table B-4--Apples, fresh: Price received by growers, monthly",
        year_value="1980",
        month="February",
        variable="Price received by growers",
        commodity_element="Apples",
        market_segment="Fresh",
        value="0.149",
        unit="dollars per pound",
    )
    + _row(
        table_name="Table B-4--Apples, fresh: Price received by growers, monthly",
        year_value="1980",
        month="January",
        variable="Price received by growers",
        commodity_element="Apples",
        market_segment="Fresh",
        value="0.141",
        unit="dollars per pound",
    )
)

G45_ROWS = _row(
    table_name="Table G-45--U.S. population",
    year_value="1980",
    month="January",
    variable="U.S. population",
    commodity_element="NA",
    market_segment="All",
    value="227.0",
    unit="million people",
)

FIXTURE_CSV = HEADER + A1_ROWS + B3_ROWS + F1_ROWS + B4_ROWS + G45_ROWS


class TestErsFruitAndTreeNutsDataUtils:
    """Tests for the ers_fruit_and_tree_nuts_data utils module."""

    def test_catalog_counts(self):
        """The catalog holds all 152 tables with the published letter split."""
        assert len(TABLE_TITLES) == 152
        counts = {letter: 0 for letter in CATEGORY_LABELS}
        for code in TABLE_TITLES:
            counts[table_category(code)] += 1
        assert counts == {
            "A": 15,
            "B": 29,
            "C": 20,
            "D": 10,
            "E": 10,
            "F": 18,
            "G": 45,
            "H": 5,
        }

    def test_table_category(self):
        """table_category returns the leading letter of a code."""
        assert table_category("A-1") == "A"
        assert table_category("G-45") == "G"

    def test_category_tables_filters_by_letter(self):
        """category_tables narrows to the requested letter, ordered."""
        assert category_tables("H") == ["H-1", "H-2", "H-3", "H-4", "H-5"]
        assert category_tables("h") == ["H-1", "H-2", "H-3", "H-4", "H-5"]
        assert category_tables()[0] == "A-1"
        assert len(category_tables()) == 152

    def test_parse_records_filters_to_requested_table(self):
        """parse_records keeps only the requested table's rows."""
        records = parse_records(FIXTURE_CSV, "B-3")
        assert {record["table"] for record in records} == {"B-3"}
        assert len(records) == 3

    def test_parse_records_skips_uncoded_table_name(self):
        """A row whose table_name has no code is skipped."""
        junk = _row(
            table_name="Source: USDA, Economic Research Service",
            year_value="1980",
            variable="Note",
            commodity_element="Apples",
            value="1.0",
            unit="pounds",
        )
        records = parse_records(HEADER + junk + B3_ROWS, "B-3")
        assert len(records) == 3
        assert all(record["table"] == "B-3" for record in records)

    def test_parse_records_fields_and_year(self):
        """A parsed record carries the dimensions, unit, and integer year."""
        records = parse_records(FIXTURE_CSV, "F-1")
        first = records[0]
        assert first == {
            "table": "F-1",
            "year_label": "1980/81",
            "year": 1980,
            "year_unit": "Marketing year",
            "month": None,
            "variable": "Area bearing",
            "commodity": "Almonds",
            "market_segment": "All",
            "geography": "United States",
            "unit": "acres",
            "value": 326800.0,
        }

    def test_parse_records_skips_na_and_bad_year(self):
        """Rows with a non-numeric value or unparseable year are dropped."""
        records = parse_records(FIXTURE_CSV, "A-1")
        assert len(records) == 4
        assert all(record["year"] in (1976, 1977) for record in records)
        assert 99.0 not in [record["value"] for record in records]

    def test_parse_records_month_only_for_monthly(self):
        """A month name is kept for monthly rows and dropped otherwise."""
        monthly = parse_records(FIXTURE_CSV, "B-4")
        assert {record["month"] for record in monthly} == {"January", "February"}
        annual = parse_records(FIXTURE_CSV, "A-1")
        assert all(record["month"] is None for record in annual)

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches the yearbook file and parses one table."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return FIXTURE_CSV.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ers_fruit_and_tree_nuts_data.afetch_table("G-45"))
        assert calls == [(YEARBOOK_MEDIA, PRODUCT_PAGE)]
        assert len(records) == 1
        assert records[0]["commodity"] == "NA"


class TestColumnLabel:
    """Tests for the column_label helper."""

    def test_commodity_is_column(self):
        """When commodity is the column axis, the header is the commodity."""
        record = {"commodity": "Almonds", "unit": "acres", "variable": "Area bearing"}
        assert column_label(record, [], True) == "Almonds (acres)"

    def test_composite_series(self):
        """Varying measure dimensions join in order with the unit appended."""
        record = {
            "variable": "Production",
            "market_segment": "All",
            "geography": "United States",
            "commodity": "Apples",
            "unit": "million pounds",
        }
        label = column_label(record, ["variable", "market_segment"], False)
        assert label == "Production, All (million pounds)"

    def test_single_variable_fallback(self):
        """With no varying measure dimension, the single variable is the header."""
        record = {
            "variable": "Price received by growers",
            "market_segment": "Fresh",
            "geography": "United States",
            "commodity": "Apples",
            "unit": "dollars per pound",
        }
        label = column_label(record, [], False)
        assert label == "Price received by growers (dollars per pound)"


class TestFruitAndTreeNutsDataQueryParams:
    """Tests for the query parameters."""

    def test_defaults(self):
        """The defaults select category A and table A-1."""
        query = FruitAndTreeNutsDataFetcher.transform_query({})
        assert isinstance(query, FruitAndTreeNutsDataQueryParams)
        assert query.category == DEFAULT_CATEGORY
        assert query.table == DEFAULT_TABLE

    def test_category_none_and_list_and_case(self):
        """Category normalizes blank to None and a list or lowercase input."""
        assert FruitAndTreeNutsDataQueryParams(category=None).category is None
        assert FruitAndTreeNutsDataQueryParams(category="").category is None
        assert FruitAndTreeNutsDataQueryParams(category=["b"]).category == "B"
        assert FruitAndTreeNutsDataQueryParams(category="g").category == "G"

    def test_invalid_category_raises(self):
        """An unknown category raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid category: Z"):
            FruitAndTreeNutsDataQueryParams(category="Z")

    def test_table_blank_returns_default(self):
        """A blank table normalizes to the default table."""
        assert FruitAndTreeNutsDataQueryParams(table=None).table == DEFAULT_TABLE
        assert FruitAndTreeNutsDataQueryParams(table="").table == DEFAULT_TABLE

    def test_table_list_and_case_and_strip(self):
        """A list or padded lowercase table value is normalized."""
        assert FruitAndTreeNutsDataQueryParams(table=["g-45"]).table == "G-45"
        assert FruitAndTreeNutsDataQueryParams(table="  b-3 ").table == "B-3"

    def test_invalid_table_raises(self):
        """An unknown table raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table: Z-9"):
            FruitAndTreeNutsDataQueryParams(table="Z-9")


class TestFruitAndTreeNutsData:
    """Tests for the FruitAndTreeNutsData model and pivot."""

    @staticmethod
    def _pivot(table: str, **params):
        records = parse_records(FIXTURE_CSV, table)
        query = FruitAndTreeNutsDataFetcher.transform_query({"table": table, **params})
        return FruitAndTreeNutsDataFetcher.transform_data(query, records)

    def test_commodity_row_market_columns(self):
        """A-1 folds the commodity into the period label and spreads segments."""
        rows = [row.model_dump() for row in self._pivot("A-1")]
        apples_1976 = next(
            row
            for row in rows
            if row["commodity"] == "Apples" and row["year"] == "Apples — 1976"
        )
        assert apples_1976["All (pounds, farm weight)"] == 29.85728
        assert apples_1976["Fresh (pounds, farm weight)"] == 17.08102
        cherries = next(row for row in rows if row["commodity"] == "Cherries")
        assert cherries["All (pounds, farm weight)"] == 1.70954
        assert cherries["Fresh (pounds, farm weight)"] is None

    def test_commodity_row_sorted_commodity_then_year(self):
        """A-1 rows group by commodity source order, then chronological year."""
        rows = self._pivot("A-1")
        keys = [(row.commodity, row.year) for row in rows]
        assert keys == [
            ("Apples", "Apples — 1976"),
            ("Apples", "Apples — 1977"),
            ("Cherries", "Cherries — 1976"),
        ]

    def test_variable_and_market_columns(self):
        """B-3 spreads the variable and market segment into composite columns."""
        rows = [row.model_dump() for row in self._pivot("B-3")]
        row_1980 = next(row for row in rows if row["year"] == "1980")
        assert row_1980["Production, All (million pounds)"] == 8818.4
        assert row_1980["Price received by growers, Fresh (cents per pound)"] == 12.1
        assert row_1980["commodity"] is None

    def test_commodity_as_columns(self):
        """F-1 turns the sole varying commodity dimension into the columns."""
        rows = [row.model_dump() for row in self._pivot("F-1")]
        row_1980 = next(row for row in rows if row["year"] == "1980/81")
        assert row_1980["Almonds (acres)"] == 326800.0
        assert row_1980["Walnuts (acres)"] == 179900.0
        assert row_1980["commodity"] is None

    def test_monthly_rows_single_value_column_chronological(self):
        """B-4 keeps year and month in the rows, emitted chronologically."""
        rows = self._pivot("B-4")
        keys = [(row.year, row.month) for row in rows]
        assert keys == [("1980", "January"), ("1980", "February"), ("1981", "January")]
        dumped = rows[0].model_dump()
        assert dumped["Price received by growers (dollars per pound)"] == 0.141

    def test_population_commodity_na_coerced(self):
        """G-45 carries a null commodity and pivots the single population column."""
        rows = self._pivot("G-45")
        assert len(rows) == 1
        dumped = rows[0].model_dump()
        assert dumped["commodity"] is None
        assert dumped["U.S. population (million people)"] == 227.0

    def test_year_filters(self):
        """start_year and end_year filter rows on the integer year."""
        start = self._pivot("A-1", start_year=1977)
        assert {row.year for row in start} == {"Apples — 1977"}
        end = self._pivot("A-1", end_year=1976)
        assert {row.year for row in end} == {"Apples — 1976", "Cherries — 1976"}

    def test_pivot_excludes_sort_keys(self):
        """Internal sort keys never leak into the validated records."""
        dumped = self._pivot("B-3")[0].model_dump()
        for hidden in ("_order", "_year", "_month", "_commodity_index"):
            assert hidden not in dumped

    def test_model_keeps_dynamic_columns_and_precision(self):
        """The Data model preserves dynamic columns at full precision."""
        row = FruitAndTreeNutsData.model_validate(
            {
                "table": "F-6",
                "year": "1980/81",
                "commodity": "NA",
                "Per capita availability (pounds, shelled basis)": 1.8231000001,
            }
        )
        dumped = row.model_dump()
        assert dumped["commodity"] is None
        assert dumped["Per capita availability (pounds, shelled basis)"] == 1.8231000001

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(
            ers_fruit_and_tree_nuts_data, "afetch_table", fake_afetch_table
        )
        query = FruitAndTreeNutsDataFetcher.transform_query({"table": "G-1"})
        records = asyncio.run(FruitAndTreeNutsDataFetcher.aextract_data(query, None))
        assert fetched == ["G-1"]
        assert records == [{"table": "G-1"}]

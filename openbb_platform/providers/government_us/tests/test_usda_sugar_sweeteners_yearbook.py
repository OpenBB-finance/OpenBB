"""Tests for the USDA ERS sugar and sweeteners yearbook utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.usda.models.sugar_sweeteners_yearbook import (
    DEFAULT_TABLE,
    MAX_WIDE_COLUMNS,
    SugarSweetenersYearbookData,
    SugarSweetenersYearbookFetcher,
    SugarSweetenersYearbookQueryParams,
)
from openbb_government_us.usda.utils import ers_sugar_sweeteners_yearbook
from openbb_government_us.usda.utils.ers_sugar_sweeteners_yearbook import (
    PRODUCT_PAGE,
    SUGAR_SWEETENERS_FILES,
    frequency_rank,
    parse_table,
    period_sort_num,
    period_sort_rank,
    table_frequencies,
    within_year_label,
)

PRICE_CSV = (
    "Table_number,Commodity_desc,Commodity_desc2,Geographic_extent,"
    "Geographic_extent2,Year,Year_cat,Year_desc,Period,Period_cat,Period_desc,"
    "Attribute_desc,Unit,Value\n"
    "2,Sugar,World white (Number 5),World,NA,1980,Calendar,"
    "Calendar year (Jan-Dec),1980,Calendar year,Calendar year (Jan-Dec),"
    "Price,U.S. cents per pound,25.0\n"
    "2,Sugar,World white (Number 5),World,NA,1980,Calendar,"
    "Calendar year (Jan-Dec),1,Calendar year quarter,Q1 (Jan-Mar),"
    "Price,U.S. cents per pound,28.0\n"
    "2,Sugar,World white (Number 5),World,NA,1980,Calendar,"
    "Calendar year (Jan-Dec),2,Month,Feb,Price,U.S. cents per pound,26.13\n"
    "2,Sugar,World white (Number 5),World,NA,1980,Calendar,"
    "Calendar year (Jan-Dec),1,Month,Jan,Price,U.S. cents per pound,20.06\n"
    "2,Sugar,World white (Number 5),World,NA,1981,Calendar,"
    "Calendar year (Jan-Dec),1,Month,Jan,Price,U.S. cents per pound,30.0\n"
    "3a,Sugar,World raw,World,NA,1980,Calendar,Calendar year (Jan-Dec),"
    "1,Month,Jan,Price,U.S. cents per pound,99.0\n"
    "2,Sugar,World white (Number 5),World,NA,1982,Calendar,"
    "Calendar year (Jan-Dec),1,Month,Jan,Price,U.S. cents per pound,\n"
    "2,Sugar,World white (Number 5),World,NA,1982,Calendar,"
    "Calendar year (Jan-Dec),2,Month,Feb,Price,U.S. cents per pound,n/a\n"
    "2,Sugar,World white (Number 5),World,NA,abcd,Calendar,"
    "Calendar year (Jan-Dec),1,Month,Jan,Price,U.S. cents per pound,40.0\n"
)

MULTI_UNIT_CSV = (
    "Table_number,Commodity_desc,Commodity_desc2,Geographic_extent,"
    "Geographic_extent2,Year,Year_cat,Year_desc,Period,Period_cat,Period_desc,"
    "Attribute_desc,Unit,Value\n"
    "54,Sugar,Estandar,Mexico,Mexico City,2024,Calendar,"
    "Calendar year (Jan-Dec),1,Month,Jan,Wholesale price,"
    "Mexican pesos per 50 kilogram,1119.319\n"
    "54,Sugar,Estandar,Mexico,Mexico City,2024,Calendar,"
    "Calendar year (Jan-Dec),1,Month,Jan,Wholesale price,"
    "U.S. cents per pound,59.405\n"
)

GROUP_CSV = (
    "Table_number,Commodity_desc,Commodity_desc2,Geographic_extent,"
    "Geographic_extent2,Year,Year_cat,Year_desc,Period,Period_cat,Period_desc,"
    "Attribute_desc,Unit,Forecast_yearmonth,Value\n"
    "24a,Sugar,Beet sugar,United States,United States,2024,Fiscal,"
    "Fiscal year (Oct-Sep),2024,Fiscal year,Fiscal year (Oct-Sep),"
    'Production,"1,000 short tons, raw value",NA,5172.462\n'
    "24a,Sugar,Sugar,United States,United States,2024,Fiscal,"
    "Fiscal year (Oct-Sep),2024,Fiscal year,Fiscal year (Oct-Sep),"
    'Beginning stocks,"1,000 short tons, raw value",NA,1780.032\n'
    "24a,Sugar,Sugar,United States,United States,2024,Fiscal,"
    "Fiscal year (Oct-Sep),2024,Fiscal year,Fiscal year (Oct-Sep),"
    'Total supply,"1,000 short tons, raw value",NA,14932.57\n'
    "24a,Sugar,Sugar,United States,United States,2024,Fiscal,"
    "Fiscal year (Oct-Sep),2024,Fiscal year,Fiscal year (Oct-Sep),"
    "Stocks-to-use ratio,Percent,NA,16.7\n"
    "24a,Sugar,Sugar,United States,United States,2023,Fiscal,"
    "Fiscal year (Oct-Sep),2023,Fiscal year,Fiscal year (Oct-Sep),"
    'Beginning stocks,"1,000 short tons, raw value",NA,1769.525\n'
)

SOURCE_CSV = (
    "Table_number,Commodity_desc,Commodity_desc2,Geographic_extent,"
    "Geographic_extent2,Source_or_destination,Year,Year_cat,Year_desc,Period,"
    "Period_cat,Period_desc,Attribute_desc,Unit,Value\n"
    "48a,Honey,NA,United States,United States,Argentina,1989,Calendar,"
    "Calendar year (Jan-Dec),1989,Calendar year,Calendar year (Jan-Dec),"
    "U.S. imports by sources,Metric tons,4746.354\n"
    "48a,Honey,NA,United States,United States,Canada,1989,Calendar,"
    "Calendar year (Jan-Dec),1989,Calendar year,Calendar year (Jan-Dec),"
    "U.S. imports by sources,Metric tons,12421.565\n"
)


class TestErsSugarSweetenersYearbookUtils:
    """Tests for the ers_sugar_sweeteners_yearbook utils module."""

    def test_catalog_contents(self):
        """The catalog holds the 67 tables mapped to their seven files."""
        assert len(SUGAR_SWEETENERS_FILES) == 67
        assert DEFAULT_TABLE in SUGAR_SWEETENERS_FILES
        medias = {config["media"] for config in SUGAR_SWEETENERS_FILES.values()}
        assert len(medias) == 7
        numbers = [config["number"] for config in SUGAR_SWEETENERS_FILES.values()]
        assert len(numbers) == len(set(numbers))
        for key, config in SUGAR_SWEETENERS_FILES.items():
            assert key.startswith("table_")
            assert config["media"].startswith("/media/")
            assert config["label"].startswith("Table ")
            assert config["number"]

    def test_period_sort_rank(self):
        """Annual, quarter, and month categories rank from summary to detail."""
        assert period_sort_rank("Fiscal year") == 0
        assert period_sort_rank("Calendar year") == 0
        assert period_sort_rank("Calendar year quarter") == 1
        assert period_sort_rank("Month") == 2
        assert period_sort_rank("Month and day") == 2
        assert period_sort_rank(None) == 0

    def test_period_sort_num(self):
        """A numeric period yields its integer, a non-numeric one yields zero."""
        assert period_sort_num("7") == 7
        assert period_sort_num("1231") == 1231
        assert period_sort_num("Jan") == 0
        assert period_sort_num(None) == 0

    def test_frequency_rank(self):
        """Annual bases rank 0, quarters 1, months 2."""
        assert frequency_rank("Fiscal year") == 0
        assert frequency_rank("Calendar year") == 0
        assert frequency_rank("Calendar year quarter") == 1
        assert frequency_rank("Month") == 2
        assert frequency_rank("Month and day") == 2
        assert frequency_rank(None) == 0

    def test_within_year_label(self):
        """The within-year label is empty annually and short sub-annually."""
        assert within_year_label("Calendar year", "Calendar year (Jan-Dec)") == ""
        assert within_year_label("Month", "Jan") == "Jan"
        assert within_year_label("Calendar year quarter", "Q1 (Jan-Mar)") == "Q1"
        assert within_year_label("Month and day", "Dec_31") == "Dec_31"

    def test_table_frequencies_orders_annual_first(self, monkeypatch):
        """table_frequencies lists distinct period bases, annual first."""

        async def fake_afetch_table(table, **kwargs):
            return [
                {"period_cat": "Month"},
                {"period_cat": "Calendar year"},
                {"period_cat": "Calendar year quarter"},
                {"period_cat": None},
            ]

        monkeypatch.setattr(
            ers_sugar_sweeteners_yearbook, "afetch_table", fake_afetch_table
        )
        assert asyncio.run(table_frequencies("table_2")) == [
            "Calendar year",
            "Calendar year quarter",
            "Month",
        ]

    def test_parse_table_filters_and_records(self):
        """Only the selected table's rows parse, with dimensions and value."""
        records = parse_table(PRICE_CSV, "table_2")
        assert {record["number"] for record in records} == {"2"}
        first = records[0]
        assert first["table"] == "table_2"
        assert first["year"] == 1980
        assert first["year_cat"] == "Calendar"
        assert first["period"] == "1980"
        assert first["period_cat"] == "Calendar year"
        assert first["period_desc"] == "Calendar year (Jan-Dec)"
        assert first["attribute"] == "Price"
        assert first["unit"] == "U.S. cents per pound"
        assert first["value"] == 25.0
        assert first["commodity_desc"] == "Sugar"
        assert first["geographic_extent"] == "World"
        assert first["geographic_extent2"] == "NA"
        assert first["source_or_destination"] is None

    def test_parse_table_skips_blank_and_nonnumeric_values(self):
        """Blank and non-numeric values, and other tables, are dropped."""
        records = parse_table(PRICE_CSV, "table_2")
        assert all(record["value"] not in (None,) for record in records)
        assert 99.0 not in [record["value"] for record in records]
        assert {record["year"] for record in records} == {1980, 1981}

    def test_parse_table_skips_nonnumeric_year(self):
        """A non-numeric year label drops the row."""
        records = parse_table(PRICE_CSV, "table_2")
        assert 40.0 not in [record["value"] for record in records]

    def test_parse_table_source_dimension(self):
        """A table with a source column populates source_or_destination."""
        records = parse_table(SOURCE_CSV, "table_48a")
        assert {record["source_or_destination"] for record in records} == {
            "Argentina",
            "Canada",
        }

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches the file through the ERS cache and parses it."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return PRICE_CSV.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ers_sugar_sweeteners_yearbook.afetch_table("table_2"))
        assert calls == [(SUGAR_SWEETENERS_FILES["table_2"]["media"], PRODUCT_PAGE)]
        assert {record["number"] for record in records} == {"2"}


def make_record(**overrides) -> dict:
    """Build a long-format record in the parse_table shape."""
    record = {
        "table": "table_24a",
        "number": "24a",
        "year": 2024,
        "year_cat": "Fiscal",
        "year_desc": "Fiscal year (Oct-Sep)",
        "period": "2024",
        "period_cat": "Fiscal year",
        "period_desc": "Fiscal year (Oct-Sep)",
        "attribute": "Production",
        "unit": "1,000 short tons, raw value",
        "value": 1.0,
        "commodity_desc": "Sugar",
        "commodity_desc2": None,
        "geographic_extent": "United States",
        "geographic_extent2": None,
        "source_or_destination": None,
        "fiscal_year_entered": None,
        "fiscal_year_quota": None,
        "forecast_yearmonth": None,
    }
    record.update(overrides)
    return record


class TestSugarSweetenersYearbook:
    """Tests for the SugarSweetenersYearbook model."""

    def test_classify_dims_never_spreads_an_unpopulated_dim(self):
        """A dim no record populates cannot partition the attributes into columns."""
        rows = [
            make_record(attribute="Production", geographic_extent="United States"),
            make_record(attribute="Imports", geographic_extent="World"),
        ]
        assert all(record["source_or_destination"] is None for record in rows)
        assert SugarSweetenersYearbookFetcher._classify_dims(
            rows, ["source_or_destination", "geographic_extent"]
        ) == (["geographic_extent"], [])

    def test_transform_data_drops_a_dim_another_dim_already_fixes(self):
        """Two dims moving together label a column once, not twice."""
        records = [
            make_record(
                attribute="Price",
                commodity_desc2="World white",
                geographic_extent="World",
                unit="U.S. cents per pound",
                value=25.0,
            ),
            make_record(
                attribute="Price",
                commodity_desc2="World raw",
                geographic_extent="Raw world",
                unit="U.S. cents per pound",
                value=20.0,
            ),
        ]
        query = SugarSweetenersYearbookFetcher.transform_query({"table": "table_24a"})
        data = SugarSweetenersYearbookFetcher.transform_data(query, records)
        assert [row.model_dump() for row in data] == [
            {
                "period": "2024",
                "World — Price": 25.0,
                "Raw world — Price": 20.0,
            }
        ]

    def test_transform_query_default_table(self):
        """transform_query defaults the table and keeps year filters."""
        query = SugarSweetenersYearbookFetcher.transform_query({"start_year": 2000})
        assert isinstance(query, SugarSweetenersYearbookQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.start_year == 2000

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert SugarSweetenersYearbookQueryParams(table=None).table == DEFAULT_TABLE
        assert SugarSweetenersYearbookQueryParams(table="").table == DEFAULT_TABLE

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        query = SugarSweetenersYearbookQueryParams(table="  table_2  ")
        assert query.table == "table_2"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            SugarSweetenersYearbookQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            SugarSweetenersYearbookQueryParams(table=123)

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(
            ers_sugar_sweeteners_yearbook, "afetch_table", fake_afetch_table
        )
        query = SugarSweetenersYearbookFetcher.transform_query({"table": "table_48a"})
        records = asyncio.run(SugarSweetenersYearbookFetcher.aextract_data(query, None))
        assert fetched == ["table_48a"]
        assert records == [{"table": "table_48a"}]

    def test_frequency_blank_returns_none(self):
        """A blank or None frequency normalizes to None."""
        assert SugarSweetenersYearbookQueryParams(frequency=None).frequency is None
        assert SugarSweetenersYearbookQueryParams(frequency="").frequency is None

    def test_frequency_strips_whitespace(self):
        """A padded frequency value is stripped."""
        assert (
            SugarSweetenersYearbookQueryParams(frequency="  Month  ").frequency
            == "Month"
        )

    def test_resolve_frequency_defaults_to_first_annual_basis(self):
        """With no frequency the first annual basis is chosen."""
        records = parse_table(PRICE_CSV, "table_2")
        query = SugarSweetenersYearbookFetcher.transform_query({"table": "table_2"})
        freq, available = SugarSweetenersYearbookFetcher._resolve_frequency(
            query, records
        )
        assert available == ["Calendar year", "Calendar year quarter", "Month"]
        assert freq == "Calendar year"

    def test_transform_data_single_unit_columns(self):
        """A single-unit monthly table names the column by the attribute alone."""
        records = parse_table(PRICE_CSV, "table_2")
        query = SugarSweetenersYearbookFetcher.transform_query(
            {"table": "table_2", "frequency": "Month"}
        )
        data = SugarSweetenersYearbookFetcher.transform_data(query, records)
        jan_1980 = next(row for row in data if row.period == "1980 Jan")
        dumped = jan_1980.model_dump()
        assert dumped["Price"] == 20.06
        assert "Price (U.S. cents per pound)" not in dumped

    def test_transform_data_monthly_period_labels(self):
        """The monthly basis labels each row with the year and month name."""
        records = parse_table(PRICE_CSV, "table_2")
        query = SugarSweetenersYearbookFetcher.transform_query(
            {"table": "table_2", "frequency": "Month"}
        )
        data = SugarSweetenersYearbookFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["1981 Jan", "1980 Feb", "1980 Jan"]

    def test_transform_data_annual_basis_labels_year_only(self):
        """The annual basis labels each row with the plain year."""
        records = parse_table(PRICE_CSV, "table_2")
        query = SugarSweetenersYearbookFetcher.transform_query(
            {"table": "table_2", "frequency": "Calendar year"}
        )
        data = SugarSweetenersYearbookFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["1980"]
        assert data[0].model_dump()["Price"] == 25.0

    def test_transform_data_quarter_basis_labels(self):
        """The quarterly basis labels each row with the year and quarter code."""
        records = parse_table(PRICE_CSV, "table_2")
        query = SugarSweetenersYearbookFetcher.transform_query(
            {"table": "table_2", "frequency": "Calendar year quarter"}
        )
        data = SugarSweetenersYearbookFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["1980 Q1"]

    def test_transform_data_multi_unit_suffix(self):
        """A multi-unit table suffixes every wide column with its unit."""
        records = parse_table(MULTI_UNIT_CSV, "table_54")
        query = SugarSweetenersYearbookFetcher.transform_query(
            {"table": "table_54", "frequency": "Month"}
        )
        data = SugarSweetenersYearbookFetcher.transform_data(query, records)
        dumped = data[0].model_dump()
        assert dumped["Wholesale price (Mexican pesos per 50 kilogram)"] == 1119.319
        assert dumped["Wholesale price (U.S. cents per pound)"] == 59.405
        assert "Wholesale price" not in dumped

    def test_transform_data_folds_partitioning_commodity_into_columns(self):
        """A supply-use table folds an attribute-partitioning commodity into the column headers, keeping one dense row per year."""
        records = parse_table(GROUP_CSV, "table_24a")
        query = SugarSweetenersYearbookFetcher.transform_query({"table": "table_24a"})
        data = SugarSweetenersYearbookFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2024", "2023"]
        y2024 = next(row for row in data if row.period == "2024").model_dump()
        assert (
            y2024["Beet sugar — Production (1,000 short tons, raw value)"] == 5172.462
        )
        assert (
            y2024["Sugar — Beginning stocks (1,000 short tons, raw value)"] == 1780.032
        )
        assert y2024["Sugar — Total supply (1,000 short tons, raw value)"] == 14932.57
        assert y2024["Sugar — Stocks-to-use ratio (Percent)"] == 16.7
        y2023 = next(row for row in data if row.period == "2023").model_dump()
        assert (
            y2023["Sugar — Beginning stocks (1,000 short tons, raw value)"] == 1769.525
        )
        assert y2023["Beet sugar — Production (1,000 short tons, raw value)"] is None

    def test_transform_data_folds_compact_source_into_columns(self):
        """A by-source table spreads a compact source dim across the columns."""
        records = parse_table(SOURCE_CSV, "table_48a")
        query = SugarSweetenersYearbookFetcher.transform_query({"table": "table_48a"})
        data = SugarSweetenersYearbookFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["1989"]
        dumped = data[0].model_dump()
        assert dumped["Argentina — U.S. imports by sources"] == 4746.354
        assert dumped["Canada — U.S. imports by sources"] == 12421.565

    def test_transform_data_keeps_wide_source_in_the_row_label(self):
        """A source dim too wide to spread stays folded into the row label."""
        records = [
            {
                "table": "table_48a",
                "year": year,
                "year_cat": "Calendar",
                "period": str(year),
                "period_cat": "Calendar year",
                "period_desc": "Calendar year (Jan-Dec)",
                "commodity_desc": "Honey",
                "commodity_desc2": None,
                "geographic_extent": "United States",
                "geographic_extent2": "United States",
                "source_or_destination": f"Country {index:02d}",
                "fiscal_year_entered": None,
                "fiscal_year_quota": None,
                "attribute": "U.S. imports by sources",
                "unit": "Metric tons",
                "forecast_yearmonth": None,
                "value": float(index + year),
            }
            for year in (1989, 1990)
            for index in range(MAX_WIDE_COLUMNS + 1)
        ]
        query = SugarSweetenersYearbookFetcher.transform_query({"table": "table_48a"})
        data = SugarSweetenersYearbookFetcher.transform_data(query, records)
        assert len(data) == 2 * (MAX_WIDE_COLUMNS + 1)
        assert data[0].period == "Country 00 — 1990"
        assert data[0].model_dump()["U.S. imports by sources"] == 1990.0

    def test_transform_data_keeps_latest_forecast_vintage(self):
        """When forecast vintages vary only the latest survives."""
        records = [
            {
                "table": "table_25",
                "year": 2020,
                "year_cat": "Fiscal",
                "period": "2020",
                "period_cat": "Fiscal year",
                "period_desc": "Fiscal year (Oct-Sep)",
                "attribute": "Total supply",
                "unit": "1,000 short tons, raw value",
                "forecast_yearmonth": vintage,
                "commodity_desc": "Sugar",
                "commodity_desc2": "Sugar",
                "geographic_extent": "United States",
                "geographic_extent2": "United States",
                "source_or_destination": None,
                "fiscal_year_entered": None,
                "fiscal_year_quota": None,
                "value": value,
            }
            for vintage, value in [("2019-05", 100.0), ("2019-07", 130.0)]
        ]
        query = SugarSweetenersYearbookFetcher.transform_query({"table": "table_25"})
        data = SugarSweetenersYearbookFetcher.transform_data(query, records)
        assert len(data) == 1
        assert data[0].model_dump()["Total supply"] == 130.0

    def test_transform_data_filters_years(self):
        """start_year and end_year filter rows on the integer year."""
        records = parse_table(PRICE_CSV, "table_2")
        start = SugarSweetenersYearbookFetcher.transform_data(
            SugarSweetenersYearbookFetcher.transform_query(
                {"table": "table_2", "frequency": "Month", "start_year": 1981}
            ),
            records,
        )
        assert {row.period for row in start} == {"1981 Jan"}

    def test_transform_data_empty_raises(self):
        """A filter that excludes every row raises EmptyDataError."""
        records = parse_table(PRICE_CSV, "table_2")
        query = SugarSweetenersYearbookFetcher.transform_query(
            {"table": "table_2", "start_year": 2100}
        )
        with pytest.raises(EmptyDataError):
            SugarSweetenersYearbookFetcher.transform_data(query, records)

    def test_transform_data_empty_input(self):
        """Empty extracted data returns an empty result."""
        query = SugarSweetenersYearbookFetcher.transform_query({"table": "table_2"})
        assert SugarSweetenersYearbookFetcher.transform_data(query, []) == []

    def test_transform_data_excludes_sort_keys(self):
        """Internal sort keys never leak into the validated records."""
        records = parse_table(PRICE_CSV, "table_2")
        query = SugarSweetenersYearbookFetcher.transform_query(
            {"table": "table_2", "frequency": "Month"}
        )
        data = SugarSweetenersYearbookFetcher.transform_data(query, records)
        dumped = data[0].model_dump()
        assert "_order" not in dumped
        assert "_dims" not in dumped

    def test_data_model_only_period_is_static(self):
        """The only static served field is the pinned period label."""
        assert set(SugarSweetenersYearbookData.model_fields) == {"period"}

    def test_data_model_keeps_dynamic_columns_and_precision(self):
        """The Data model preserves dynamic columns at full precision."""
        row = SugarSweetenersYearbookData.model_validate(
            {
                "period": "Sugar — 2020",
                "Total supply (1,000 short tons, raw value)": 13977.835,
            }
        )
        dumped = row.model_dump()
        assert dumped["Total supply (1,000 short tons, raw value)"] == 13977.835

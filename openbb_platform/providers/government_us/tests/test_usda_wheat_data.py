"""Tests for the USDA ERS wheat data utils and model."""

import asyncio
import zipfile
from io import BytesIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.wheat_data import (
    DEFAULT_TABLE,
    WheatDataData,
    WheatDataFetcher,
    WheatDataQueryParams,
)
from openbb_government_us.usda.utils import ers_wheat_data
from openbb_government_us.usda.utils.ers_wheat_data import (
    ALL_YEARS_ZIP,
    PRODUCT_PAGE,
    QUARTERLY_ZIP,
    WHEAT_DATA_FILES,
    normalize_class,
    parse_table,
)

US_SUPPLY_CSV = (
    "Commodity_Desc,Commodity_Desc2,Attribute_Desc,Geography_Desc,Unit_Desc,"
    "Marketing_Year,Timeperiod_Desc,Amount\n"
    "Wheat,All wheat,Beginning stocks,United States,Million bushels,"
    "2024/25,MY Jun-May,696.434\n"
    "Wheat,All wheat,Production,United States,Million bushels,"
    "2024/25,MY Jun-May,1978.697\n"
    "Wheat,Durum,Production,United States,Million bushels,"
    "2024/25,MY Jun-May,80.051\n"
    "Wheat,,Production,United States,Million bushels,"
    ",MY Jun-May,12.0\n"
    "Wheat,,Production,United States,Million bushels,"
    "abcd,MY Jun-May,13.0\n"
    "Wheat,All wheat,Production,United States,Million bushels,"
    "2023/24,,50.0\n"
)

DESTINATIONS_CSV = (
    "Commodity_Desc,Attribute_Desc,Geography_Desc,Unit_Desc,"
    "Marketing_Year,Timeperiod_Desc,Amount\n"
    'Total wheat grain,"Exports, Qty",Sudan,"1,000 metric tons ",'
    "2011/12,MY Jun-May,0.017\n"
    'Total wheat grain,"Exports, Qty",Sudan,"1,000 metric tons ",'
    "2011/12,MY Jun-May,0.1225\n"
    'Total wheat grain,"Exports, Qty",Japan,"1,000 metric tons ",'
    "2011/12,MY Jun-May,3000.0\n"
    'Total wheat grain,"Exports, Qty",Japan,"1,000 metric tons ",'
    "2011/12,MY Jun-May,\n"
)

PLACEHOLDER_DESTINATION_CSV = (
    "Commodity_Desc,Attribute_Desc,Geography_Desc,Unit_Desc,"
    "Marketing_Year,Timeperiod_Desc,Amount\n"
    'Total wheat grain,"Exports, Qty",Japan,"1,000 metric tons ",'
    "2011/12,MY Jun-May,3000.0\n"
    'Total wheat grain,"Exports, Qty",NA,"1,000 metric tons ",'
    "2010/11,MY Jun-May,2500.0\n"
)

WORLD_CSV = (
    "Commodity_Desc,Attribute_Desc,Geography_Desc,Unit_Desc,Marketing_Year,Amount\n"
    "Wheat,World Production Million Metric Tons,World,Million Metric Tons,"
    "2024/25,798.5\n"
    "Wheat,United States Exports Million Bushels,United States,Million Bushels,"
    "2024/25,820.0\n"
)

BY_CLASS_TRADE_CSV = (
    "Commodity_Desc,Attribute_Desc,Unit_Desc,Marketing_Year,Timeperiod_Desc,Amount\n"
    'All Wheat,Export estimates,"1,000 bushels",2024/25,MY Jun-May,100.0\n'
    'All wheat,Import estimates,"1,000 bushels",2024/25,MY Jun-May,5.0\n'
)

QUARTERLY_CSV = (
    "MarketingYear,TimePeriod,Commodity,Class,Attribute,GeographicalLevel,"
    "Location,Value,Unit\n"
    "2024-25,Marketing year: Jun-May,Wheat,All wheat,Beginning stocks,Country,"
    "United States,696.434,Bushels (million)\n"
    "2024-25,Marketing year: Jun-May,Wheat,All wheat,Imports,Country,"
    "United States,149.630228133494,Bushels (million)\n"
    "2024-25,Marketing year: Jun-May,Wheat,All wheat,Ending stocks,Country,"
    "United States,NA,Bushels (million)\n"
)


class TestErsWheatDataUtils:
    """Tests for the ers_wheat_data utils module."""

    def test_catalog_contents(self):
        """The catalog holds the 16 tables mapped to their two zip archives."""
        assert len(WHEAT_DATA_FILES) == 16
        all_years = [
            key
            for key, config in WHEAT_DATA_FILES.items()
            if config["media"] == ALL_YEARS_ZIP
        ]
        assert len(all_years) == 15
        assert WHEAT_DATA_FILES["by_class_quarterly"]["media"] == QUARTERLY_ZIP
        assert (
            WHEAT_DATA_FILES["by_class_inspections"]["member"]
            == "26_By_class_inspections _data.csv"
        )
        for config in WHEAT_DATA_FILES.values():
            assert config["label"]
            assert config["value_col"] in ("Amount", "Value")
            if config["series_col"] is None:
                assert config["value_name"]

    def test_normalize_class_canonicalizes_known_labels(self):
        """Known class labels normalize to canonical casing."""
        assert normalize_class("All Wheat") == "All wheat"
        assert normalize_class("all wheat") == "All wheat"
        assert normalize_class(" HARD RED WINTER ") == "Hard red winter"

    def test_normalize_class_passes_through_unknown(self):
        """Unknown class labels pass through, stripped."""
        assert normalize_class("  Triticale  ") == "Triticale"

    def test_parse_table_series_measures_and_class(self):
        """A series-column table emits one record per class, measure, and year."""
        records = parse_table(US_SUPPLY_CSV, "us_supply_and_disappearance")
        assert len(records) == 4
        assert records[0] == {
            "table": "us_supply_and_disappearance",
            "marketing_year": "2024/25",
            "year": 2024,
            "period": "MY Jun-May",
            "wheat_class": "All wheat",
            "commodity_group": None,
            "product": None,
            "geography": None,
            "unit": None,
            "series": "Beginning stocks",
            "amount": 696.434,
        }
        assert records[2]["wheat_class"] == "Durum"
        assert records[2]["amount"] == 80.051

    def test_parse_table_skips_blank_and_nonnumeric_years(self):
        """Rows with a blank or non-numeric year label are dropped."""
        records = parse_table(US_SUPPLY_CSV, "us_supply_and_disappearance")
        assert all(record["year"] in (2024, 2023) for record in records)
        assert 12.0 not in [record["amount"] for record in records]
        assert 13.0 not in [record["amount"] for record in records]

    def test_parse_table_empty_period_becomes_none(self):
        """An empty Timeperiod cell yields a None period."""
        records = parse_table(US_SUPPLY_CSV, "us_supply_and_disappearance")
        year_2023 = [record for record in records if record["year"] == 2023]
        assert len(year_2023) == 1
        assert year_2023[0]["period"] is None

    def test_parse_table_no_series_column_uses_value_name(self):
        """The destination table has no series column, so it uses value_name."""
        records = parse_table(DESTINATIONS_CSV, "all_wheat_destination_exports")
        assert len(records) == 3
        assert {record["series"] for record in records} == {"Exports"}
        assert records[0]["geography"] == "Sudan"
        assert records[2]["geography"] == "Japan"

    def test_parse_table_skips_blank_amount(self):
        """A blank Amount cell drops the row."""
        records = parse_table(DESTINATIONS_CSV, "all_wheat_destination_exports")
        assert len(records) == 3

    def test_parse_table_period_column_absent(self):
        """A table without a period column yields None periods."""
        records = parse_table(WORLD_CSV, "world_supply_and_disappearance")
        assert len(records) == 2
        assert all(record["period"] is None for record in records)
        assert records[0]["series"] == "World Production Million Metric Tons"

    def test_parse_table_normalizes_wheat_class(self):
        """The by-class trade table normalizes 'All Wheat' to 'All wheat'."""
        records = parse_table(BY_CLASS_TRADE_CSV, "by_class_trade_data")
        assert {record["wheat_class"] for record in records} == {"All wheat"}

    def test_parse_table_quarterly_value_column_and_na(self):
        """The quarterly table reads the Value column and skips 'NA'."""
        records = parse_table(QUARTERLY_CSV, "by_class_quarterly")
        assert len(records) == 2
        assert records[0] == {
            "table": "by_class_quarterly",
            "marketing_year": "2024-25",
            "year": 2024,
            "period": "Marketing year: Jun-May",
            "wheat_class": "All wheat",
            "commodity_group": None,
            "product": None,
            "geography": None,
            "unit": "Bushels (million)",
            "series": "Beginning stocks",
            "amount": 696.434,
        }

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches the zip through the ERS cache and reads the member."""
        calls = []
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(
                WHEAT_DATA_FILES["us_supply_and_disappearance"]["member"],
                US_SUPPLY_CSV,
            )
            archive.writestr("Wheat Data.txt", "readme")
        content = buffer.getvalue()

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return content

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_wheat_data.afetch_table("us_supply_and_disappearance")
        )
        assert calls == [(ALL_YEARS_ZIP, PRODUCT_PAGE)]
        assert len(records) == 4
        assert records[0]["series"] == "Beginning stocks"


class TestWheatData:
    """Tests for the WheatData model."""

    def test_transform_query_default_table(self):
        """transform_query defaults the table and keeps year filters."""
        query = WheatDataFetcher.transform_query({"start_year": 2000})
        assert isinstance(query, WheatDataQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.start_year == 2000

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert WheatDataQueryParams(table=None).table == DEFAULT_TABLE  # ty: ignore[invalid-argument-type]
        assert WheatDataQueryParams(table="").table == DEFAULT_TABLE

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        query = WheatDataQueryParams(table="  by_class_quarterly  ")
        assert query.table == "by_class_quarterly"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            WheatDataQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            WheatDataQueryParams(table=123)  # ty: ignore[invalid-argument-type]

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(ers_wheat_data, "afetch_table", fake_afetch_table)
        query = WheatDataFetcher.transform_query(
            {"table": "world_supply_and_disappearance"}
        )
        records = asyncio.run(WheatDataFetcher.aextract_data(query, None))
        assert fetched == ["world_supply_and_disappearance"]
        assert records == [{"table": "world_supply_and_disappearance"}]

    def test_data_model_exposes_only_period_field(self):
        """The served Data model carries a single pinned period field."""
        assert set(WheatDataData.model_fields) == {"period"}

    def test_transform_data_folds_class_into_period_label(self):
        """A varying wheat class is folded into the pinned period label."""
        records = parse_table(US_SUPPLY_CSV, "us_supply_and_disappearance")
        data = WheatDataFetcher.transform_data(
            WheatDataFetcher.transform_query({}), records
        )
        by_period = {row.period: row.model_dump(by_alias=True) for row in data}
        assert set(by_period) == {
            "All wheat — 2023/24",
            "All wheat — 2024/25 MY Jun-May",
            "Durum — 2024/25 MY Jun-May",
        }
        all_wheat = by_period["All wheat — 2024/25 MY Jun-May"]
        assert all_wheat["Beginning stocks"] == 696.434
        assert all_wheat["Production"] == 1978.697
        durum = by_period["Durum — 2024/25 MY Jun-May"]
        assert durum["Production"] == 80.051
        assert durum["Beginning stocks"] is None

    def test_transform_data_period_omits_absent_within_year_period(self):
        """A row without a within-year period keeps only the year in the label."""
        records = parse_table(US_SUPPLY_CSV, "us_supply_and_disappearance")
        data = WheatDataFetcher.transform_data(
            WheatDataFetcher.transform_query({}), records
        )
        assert "All wheat — 2023/24" in {row.period for row in data}

    def test_transform_data_folds_geography_and_sums_cells(self):
        """A hidden destination surfaces in the label and duplicate cells sum."""
        records = parse_table(DESTINATIONS_CSV, "all_wheat_destination_exports")
        data = WheatDataFetcher.transform_data(
            WheatDataFetcher.transform_query({}), records
        )
        by_period = {row.period: row.model_dump(by_alias=True) for row in data}
        assert set(by_period) == {
            "Japan — 2011/12 MY Jun-May",
            "Sudan — 2011/12 MY Jun-May",
        }
        assert by_period["Sudan — 2011/12 MY Jun-May"]["Exports"] == pytest.approx(
            0.017 + 0.1225
        )
        assert by_period["Japan — 2011/12 MY Jun-May"]["Exports"] == 3000.0

    def test_transform_data_ignores_a_placeholder_dimension(self):
        """A 'NA' destination is read as absent, so it never labels a row."""
        records = parse_table(
            PLACEHOLDER_DESTINATION_CSV, "all_wheat_destination_exports"
        )
        assert [record["geography"] for record in records] == ["Japan", "NA"]
        data = WheatDataFetcher.transform_data(
            WheatDataFetcher.transform_query({}), records
        )
        assert {row.period for row in data} == {
            "2011/12 MY Jun-May",
            "2010/11 MY Jun-May",
        }

    def test_transform_data_labels_are_unique(self):
        """No two rows share a period label after folding the destination."""
        records = parse_table(DESTINATIONS_CSV, "all_wheat_destination_exports")
        data = WheatDataFetcher.transform_data(
            WheatDataFetcher.transform_query({}), records
        )
        labels = [row.period for row in data]
        assert len(labels) == len(set(labels))

    def test_transform_data_filters_years(self):
        """start_year and end_year filter rows on the integer year."""
        records = parse_table(US_SUPPLY_CSV, "us_supply_and_disappearance")
        start = WheatDataFetcher.transform_data(
            WheatDataFetcher.transform_query({"start_year": 2024}), records
        )
        assert all("2024/25" in row.period for row in start)
        assert start
        end = WheatDataFetcher.transform_data(
            WheatDataFetcher.transform_query({"end_year": 2023}), records
        )
        assert all("2023/24" in row.period for row in end)
        assert end
        window = WheatDataFetcher.transform_data(
            WheatDataFetcher.transform_query({"start_year": 2024, "end_year": 2024}),
            records,
        )
        assert all("2024/25" in row.period for row in window)
        assert window

    def test_transform_data_empty_after_filter_returns_empty(self):
        """A year filter that excludes every row yields no rows."""
        records = parse_table(US_SUPPLY_CSV, "us_supply_and_disappearance")
        data = WheatDataFetcher.transform_data(
            WheatDataFetcher.transform_query({"start_year": 3000}), records
        )
        assert data == []

    def test_transform_data_merges_class_and_omits_constant_dim(self):
        """Case-variant classes merge and a constant class stays out of the label."""
        records = parse_table(BY_CLASS_TRADE_CSV, "by_class_trade_data")
        data = WheatDataFetcher.transform_data(
            WheatDataFetcher.transform_query({}), records
        )
        assert len(data) == 1
        dumped = data[0].model_dump(by_alias=True)
        assert dumped["period"] == "2024/25 MY Jun-May"
        assert dumped["Export estimates"] == 100.0
        assert dumped["Import estimates"] == 5.0

    def test_transform_data_no_dims_no_period_labels_by_year(self):
        """A table with no dimension and no period labels each row by year alone."""
        records = parse_table(WORLD_CSV, "world_supply_and_disappearance")
        data = WheatDataFetcher.transform_data(
            WheatDataFetcher.transform_query({}), records
        )
        assert len(data) == 1
        dumped = data[0].model_dump(by_alias=True)
        assert dumped["period"] == "2024/25"
        assert dumped["World Production Million Metric Tons"] == 798.5
        assert dumped["United States Exports Million Bushels"] == 820.0

    def test_transform_data_excludes_internal_sort_keys(self):
        """Internal sort keys never leak into the served records."""
        records = parse_table(WORLD_CSV, "world_supply_and_disappearance")
        data = WheatDataFetcher.transform_data(
            WheatDataFetcher.transform_query({}), records
        )
        dumped = data[0].model_dump(by_alias=True)
        assert "_order" not in dumped
        assert "_year" not in dumped
        assert "_sort" not in dumped

    def test_transform_data_folds_constant_unit_into_column_header(self):
        """A single-unit table folds its unit into each value-column header."""
        records = parse_table(QUARTERLY_CSV, "by_class_quarterly")
        data = WheatDataFetcher.transform_data(
            WheatDataFetcher.transform_query({}), records
        )
        assert len(data) == 1
        dumped = data[0].model_dump(by_alias=True)
        assert dumped["period"] == "2024-25 Marketing year: Jun-May"
        assert dumped["Beginning stocks (Bushels (million))"] == 696.434
        assert dumped["Imports (Bushels (million))"] == 149.630228133494

    def test_data_model_keeps_dynamic_columns_and_precision(self):
        """The Data model preserves dynamic value columns at full precision."""
        row = WheatDataData.model_validate(
            {
                "period": "2024-25 Marketing year: Jun-May",
                "Imports": 149.630228133494,
            }
        )
        assert row.model_dump()["Imports"] == 149.630228133494

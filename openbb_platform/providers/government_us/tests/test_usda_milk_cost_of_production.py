"""Tests for the USDA ERS milk cost of production utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.usda.models.milk_cost_of_production import (
    MilkCostOfProductionFetcher,
    MilkCostOfProductionQueryParams,
)
from openbb_government_us.usda.utils import ers_milk_cost_of_production
from openbb_government_us.usda.utils.ers_milk_cost_of_production import (
    CATEGORY_CHOICES,
    ITEM_CHOICES,
    MILK_COST_FILES,
    SIZE_CHOICES,
    STATE_CHOICES,
    build_url,
    clean_item,
    decode_csv,
    media_path,
    parse_rows,
)

SAMPLE_STATE_CSV = (
    "Commodity,Category,Item,Units,Size,Region,Country,Year,Value,"
    "Survey base year\n"
    "Milk,Gross value of production,Milk sold,dollars per hundredweight sold,"
    "No specific size,Wisconsin,United States,2024,22.02,Base survey of 2021\n"
    "Milk,Supporting information,Milk cows,head per farm,No specific size,"
    "U.S. total,United States,2025,283,Base survey of 2021\n"
    'Milk,Operating costs,"Other, operating costs  ",'
    "dollars per hundredweight sold,No specific size,U.S. total,United States,"
    "2025,0.01,Base survey of 2021\n"
    "Milk,Net value,Value of production less operating costs,"
    "dollars per hundredweight sold,No specific size,California,United States,"
    "2023,,Base survey of 2021\n"
)

SAMPLE_SIZE_CSV = (
    "Commodity,Category,Item,Item2,Units,Size,Region,Country,Year,Value,"
    "Survey base year\n"
    "Milk,Gross value of production,Cattle,Cattle,"
    "dollars per hundredweight sold,50–99 cows,U.S. total,United States,2025,"
    "2.92,Base survey of 2021\n"
    "Milk,Supporting information,Milk cows,Milk cows (head per farm),"
    'head per farm,"1,000–1,999 cows",U.S. total,United States,2025,1411,'
    "Base survey of 2021\n"
    'Milk,Operating costs,"Other, operating costs ² ",'
    '"Other, operating costs ² ",dollars per hundredweight sold,'
    "Fewer than 50 cows,U.S. total,United States,2021,0.03,Base survey of 2021\n"
)


def make_state_record(**overrides) -> dict:
    """Build a by-state row record with optional field overrides."""
    record = {
        "category": "Gross value of production",
        "item": "Milk sold",
        "unit": "dollars per hundredweight sold",
        "state": "U.S. total",
        "size_of_operation": None,
        "year": 2024,
        "value": 22.02,
        "survey_base_year": "Base survey of 2021",
    }
    record.update(overrides)
    return record


def make_size_record(**overrides) -> dict:
    """Build a by-size row record with optional field overrides."""
    record = {
        "category": "Gross value of production",
        "item": "Milk sold",
        "unit": "dollars per hundredweight sold",
        "state": None,
        "size_of_operation": "All sizes",
        "year": 2024,
        "value": 22.02,
        "survey_base_year": "Base survey of 2021",
    }
    record.update(overrides)
    return record


class TestErsMilkCostOfProductionUtils:
    """Tests for the ers_milk_cost_of_production utils module."""

    def test_catalog_contents(self):
        """The catalog holds the two 2021-base reports with unique paths."""
        assert sorted(MILK_COST_FILES) == ["by_size_of_operation", "by_state"]
        media_ids = [entry["media_id"] for entry in MILK_COST_FILES.values()]
        assert len(set(media_ids)) == 2
        slugs = [entry["slug"] for entry in MILK_COST_FILES.values()]
        assert len(set(slugs)) == 2
        dimensions = {entry["dimension"] for entry in MILK_COST_FILES.values()}
        assert dimensions == {"state", "size_of_operation"}

    def test_choice_maps(self):
        """Choice maps cover the published dimension and label values."""
        assert len(STATE_CHOICES) == 11
        assert STATE_CHOICES["us_total"] == "U.S. total"
        assert len(SIZE_CHOICES) == 8
        assert SIZE_CHOICES["1000_1999_cows"] == "1,000–1,999 cows"
        assert len(CATEGORY_CHOICES) == 6
        assert len(ITEM_CHOICES) == 29
        assert len(set(ITEM_CHOICES.values())) == 29

    def test_media_path(self):
        """media_path builds the report's media path."""
        assert media_path("by_state") == "/media/5057/by-state.csv"
        assert (
            media_path("by_size_of_operation") == "/media/5059/by-size-of-operation.csv"
        )

    def test_build_url(self):
        """URLs follow the /media/{media_id}/{slug}.csv pattern."""
        assert build_url("by_state") == (
            "https://www.ers.usda.gov/media/5057/by-state.csv"
        )
        assert build_url("by_size_of_operation") == (
            "https://www.ers.usda.gov/media/5059/by-size-of-operation.csv"
        )

    def test_clean_item(self):
        """Footnote superscripts and stray whitespace are stripped."""
        assert clean_item("Other, operating costs ² ") == "Other, operating costs"
        assert clean_item("Other income  ") == "Other income"
        assert (
            clean_item("Capital recovery of machinery and equipment ³ ")
            == "Capital recovery of machinery and equipment"
        )
        assert clean_item("Milk sold") == "Milk sold"

    def test_clean_item_matches_choices(self):
        """Cleaned footnoted labels match the ITEM_CHOICES catalog values."""
        assert clean_item("Other income ¹ ") == ITEM_CHOICES["other_income"]
        assert (
            clean_item("Other, operating costs  ")
            == ITEM_CHOICES["other_operating_costs"]
        )

    def test_decode_csv_utf8(self):
        """UTF-8 content decodes directly, dropping any BOM."""
        assert decode_csv("Year,Value\n2024,1.5\n".encode("utf-8-sig")) == (
            "Year,Value\n2024,1.5\n"
        )

    def test_decode_csv_cp1252_fallback(self):
        """cp1252 bytes fall back from the UTF-8 decode attempt."""
        text = "50–99 cows ¹"
        assert decode_csv(text.encode("cp1252")) == text

    def test_parse_rows_by_state(self):
        """By-state rows carry state, a None size, and skip empty values."""
        rows = parse_rows(SAMPLE_STATE_CSV, "by_state")
        assert rows == [
            {
                "category": "Gross value of production",
                "item": "Milk sold",
                "unit": "dollars per hundredweight sold",
                "state": "Wisconsin",
                "size_of_operation": None,
                "year": 2024,
                "value": 22.02,
                "survey_base_year": "Base survey of 2021",
            },
            {
                "category": "Supporting information",
                "item": "Milk cows",
                "unit": "head per farm",
                "state": "U.S. total",
                "size_of_operation": None,
                "year": 2025,
                "value": 283.0,
                "survey_base_year": "Base survey of 2021",
            },
            {
                "category": "Operating costs",
                "item": "Other, operating costs",
                "unit": "dollars per hundredweight sold",
                "state": "U.S. total",
                "size_of_operation": None,
                "year": 2025,
                "value": 0.01,
                "survey_base_year": "Base survey of 2021",
            },
        ]

    def test_parse_rows_by_size(self):
        """By-size rows carry the size class, a None state, and clean items."""
        rows = parse_rows(SAMPLE_SIZE_CSV, "by_size_of_operation")
        assert [row["size_of_operation"] for row in rows] == [
            "50–99 cows",
            "1,000–1,999 cows",
            "Fewer than 50 cows",
        ]
        assert all(row["state"] is None for row in rows)
        assert rows[2]["item"] == "Other, operating costs"
        assert rows[1]["value"] == 1411.0
        assert rows[0]["year"] == 2025

    def test_afetch_report_by_state(self, monkeypatch):
        """afetch_report fetches through the ERS cache client and parses."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return SAMPLE_STATE_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        rows = asyncio.run(ers_milk_cost_of_production.afetch_report("by_state"))
        assert calls == [
            ("/media/5057/by-state.csv", ers_milk_cost_of_production.PRODUCT_PAGE)
        ]
        assert len(rows) == 3
        assert rows[0]["state"] == "Wisconsin"

    def test_afetch_report_by_size_decodes_cp1252(self, monkeypatch):
        """afetch_report decodes the cp1252 by-size CSV via the fallback."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return SAMPLE_SIZE_CSV.encode("cp1252")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        rows = asyncio.run(
            ers_milk_cost_of_production.afetch_report("by_size_of_operation")
        )
        assert calls == [
            (
                "/media/5059/by-size-of-operation.csv",
                ers_milk_cost_of_production.PRODUCT_PAGE,
            )
        ]
        assert [row["size_of_operation"] for row in rows] == [
            "50–99 cows",
            "1,000–1,999 cows",
            "Fewer than 50 cows",
        ]
        assert rows[2]["item"] == "Other, operating costs"


class TestMilkCostOfProduction:
    """Tests for the MilkCostOfProduction model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = MilkCostOfProductionFetcher.transform_query(
            {"report": "by_state", "state": "wisconsin", "start_year": 2022}
        )
        assert isinstance(query, MilkCostOfProductionQueryParams)
        assert query.report == "by_state"
        assert query.state == "wisconsin"
        assert query.start_year == 2022

    def test_report_defaults_to_by_state(self):
        """The report defaults to the by-state table."""
        assert MilkCostOfProductionQueryParams().report == "by_state"

    def test_selection_accepts_list_and_comma_string(self):
        """Selections accept a list or a comma-separated string."""
        query = MilkCostOfProductionQueryParams(state=["us_total", "wisconsin"])
        assert query.state == "us_total,wisconsin"
        query = MilkCostOfProductionQueryParams(state=" us_total , wisconsin ")
        assert query.state == "us_total,wisconsin"
        query = MilkCostOfProductionQueryParams(
            report="by_size_of_operation", size="all_sizes,50_99_cows"
        )
        assert query.size == "all_sizes,50_99_cows"
        query = MilkCostOfProductionQueryParams(
            category=["net_value"], item="milk_sold,total_costs_listed"
        )
        assert query.category == "net_value"
        assert query.item == "milk_sold,total_costs_listed"

    def test_blank_selection_returns_none(self):
        """Empty or whitespace-only selections normalize to None."""
        assert MilkCostOfProductionQueryParams(state=None).state is None
        assert MilkCostOfProductionQueryParams(state="").state is None
        assert MilkCostOfProductionQueryParams(state=" , ").state is None

    def test_unknown_state_raises(self):
        """Unknown states raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid state.*texas.*wisconsin"):
            MilkCostOfProductionQueryParams(state="wisconsin,texas")

    def test_unknown_size_raises(self):
        """Unknown sizes raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid size.*bogus.*all_sizes"):
            MilkCostOfProductionQueryParams(report="by_size_of_operation", size="bogus")

    def test_unknown_category_raises(self):
        """Unknown categories raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid category.*bogus.*net_value"):
            MilkCostOfProductionQueryParams(category="bogus")

    def test_unknown_item_raises(self):
        """Unknown items raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid item.*bogus.*milk_sold"):
            MilkCostOfProductionQueryParams(item="milk_sold,bogus")

    def test_size_filter_requires_size_report(self):
        """A size filter with the by-state report raises OpenBBError."""
        with pytest.raises(OpenBBError, match="'size' filter applies only"):
            MilkCostOfProductionQueryParams(report="by_state", size="all_sizes")

    def test_state_filter_requires_state_report(self):
        """A state filter with the by-size report raises OpenBBError."""
        with pytest.raises(OpenBBError, match="'state' filter applies only"):
            MilkCostOfProductionQueryParams(
                report="by_size_of_operation", state="wisconsin"
            )

    def test_aextract_fetches_selected_report(self, monkeypatch):
        """aextract_data fetches only the selected report's CSV."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return SAMPLE_SIZE_CSV.encode("cp1252")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        query = MilkCostOfProductionFetcher.transform_query(
            {"report": "by_size_of_operation"}
        )
        records = asyncio.run(MilkCostOfProductionFetcher.aextract_data(query, None))
        assert calls == [
            (
                "/media/5059/by-size-of-operation.csv",
                ers_milk_cost_of_production.PRODUCT_PAGE,
            )
        ]
        assert len(records) == 3
        assert records[0]["size_of_operation"] == "50–99 cows"

    def test_transform_data_filters_states(self):
        """The state filter keeps only the selected published labels."""
        records = [
            make_state_record(state="Wisconsin"),
            make_state_record(state="U.S. total"),
            make_state_record(state="California"),
        ]
        query = MilkCostOfProductionFetcher.transform_query(
            {"state": "us_total,california"}
        )
        data = MilkCostOfProductionFetcher.transform_data(query, records)
        assert [row.group for row in data] == ["U.S. total", "California"]

    def test_transform_data_filters_sizes(self):
        """The size filter keeps only the selected published labels."""
        records = [
            make_size_record(size_of_operation="All sizes"),
            make_size_record(size_of_operation="50–99 cows"),
            make_size_record(size_of_operation="1,000–1,999 cows"),
        ]
        query = MilkCostOfProductionFetcher.transform_query(
            {"report": "by_size_of_operation", "size": "1000_1999_cows"}
        )
        data = MilkCostOfProductionFetcher.transform_data(query, records)
        assert [row.group for row in data] == ["1,000–1,999 cows"]

    def test_transform_data_filters_categories_and_items(self):
        """Category and item filters intersect on the published labels."""
        records = [
            make_state_record(category="Net value", item="Milk sold"),
            make_state_record(
                category="Net value",
                item="Value of production less operating costs",
            ),
            make_state_record(category="Operating costs", item="Milk sold"),
        ]
        query = MilkCostOfProductionFetcher.transform_query(
            {"category": "net_value", "item": "milk_sold"}
        )
        data = MilkCostOfProductionFetcher.transform_data(query, records)
        assert [(row.category, row.item) for row in data] == [
            ("Net value", "Milk sold")
        ]

    def test_transform_data_filters_years(self):
        """start_year and end_year select which year columns appear."""
        records = [make_state_record(year=year) for year in (2021, 2022, 2023, 2024)]
        query = MilkCostOfProductionFetcher.transform_query(
            {"start_year": 2022, "end_year": 2023}
        )
        data = MilkCostOfProductionFetcher.transform_data(query, records)
        assert len(data) == 1
        dumped = data[0].model_dump()
        assert sorted(k for k in dumped if k.isdigit()) == ["2022", "2023"]

    def test_transform_data_pivots_years_into_columns(self):
        """Each item and dimension is one row with a value column per year."""
        records = [
            make_state_record(year=2022, state="California", item="Cattle", value=5.0),
            make_state_record(year=2023, state="California", item="Cattle", value=6.0),
            make_state_record(
                year=2022, state="Wisconsin", item="Milk sold", value=22.02
            ),
        ]
        query = MilkCostOfProductionFetcher.transform_query({})
        data = MilkCostOfProductionFetcher.transform_data(query, records)
        assert [(row.group, row.item) for row in data] == [
            ("California", "Cattle"),
            ("Wisconsin", "Milk sold"),
        ]
        cattle = data[0].model_dump()
        assert cattle["2022"] == 5.0
        assert cattle["2023"] == 6.0
        assert "survey_base_year" not in cattle

    def test_transform_data_groups_rows_by_dimension_then_category(self):
        """Rows group by the published dimension order, then category order."""
        records = [
            make_state_record(state="Wisconsin", category="Net value", item="Cattle"),
            make_state_record(
                state="U.S. total", category="Operating costs", item="Repairs"
            ),
            make_state_record(
                state="U.S. total",
                category="Gross value of production",
                item="Milk sold",
            ),
            make_state_record(
                state="U.S. total",
                category="Gross value of production",
                item="Total, gross value of production",
            ),
            make_state_record(
                state="U.S. total",
                category="Gross value of production",
                item="Cattle",
            ),
        ]
        query = MilkCostOfProductionFetcher.transform_query({})
        data = MilkCostOfProductionFetcher.transform_data(query, records)
        assert [(row.group, row.category, row.item) for row in data] == [
            ("U.S. total", "Gross value of production", "Cattle"),
            ("U.S. total", "Gross value of production", "Milk sold"),
            (
                "U.S. total",
                "Gross value of production",
                "Total, gross value of production",
            ),
            ("U.S. total", "Operating costs", "Repairs"),
            ("Wisconsin", "Net value", "Cattle"),
        ]

    def test_transform_data_serves_one_dimension_column(self):
        """Both reports carry the row dimension in the single group column."""
        query = MilkCostOfProductionFetcher.transform_query({})
        state_row = MilkCostOfProductionFetcher.transform_data(
            query, [make_state_record(state="Wisconsin")]
        )[0].model_dump()
        assert state_row["group"] == "Wisconsin"
        query = MilkCostOfProductionFetcher.transform_query(
            {"report": "by_size_of_operation"}
        )
        size_row = MilkCostOfProductionFetcher.transform_data(
            query, [make_size_record(size_of_operation="500–999 cows")]
        )[0].model_dump()
        assert size_row["group"] == "500–999 cows"
        assert "state" not in size_row
        assert "size_of_operation" not in state_row

    def test_transform_data_orders_year_columns_ascending(self):
        """Year columns are ordered oldest to newest regardless of source order."""
        records = [
            make_state_record(year=year, item="Milk sold", value=float(year))
            for year in (2025, 2021, 2023, 2022, 2024)
        ]
        query = MilkCostOfProductionFetcher.transform_query({})
        data = MilkCostOfProductionFetcher.transform_data(query, records)
        dumped = data[0].model_dump()
        assert [key for key in dumped if key.isdigit()] == [
            "2021",
            "2022",
            "2023",
            "2024",
            "2025",
        ]

    def test_transform_data_pads_missing_year_cells(self):
        """A row missing a year still carries that year's column as None."""
        records = [
            make_state_record(year=2021, item="Milk sold", value=1.0),
            make_state_record(year=2022, item="Milk sold", value=2.0),
            make_state_record(year=2021, item="Cattle", value=3.0),
        ]
        query = MilkCostOfProductionFetcher.transform_query({})
        data = MilkCostOfProductionFetcher.transform_data(query, records)
        cattle = next(row for row in data if row.item == "Cattle").model_dump()
        assert cattle["2021"] == 3.0
        assert cattle["2022"] is None

    def test_transform_data_empty_raises(self):
        """No records surviving the filters raises EmptyDataError."""
        query = MilkCostOfProductionFetcher.transform_query({"start_year": 2030})
        with pytest.raises(EmptyDataError, match="No records match"):
            MilkCostOfProductionFetcher.transform_data(
                query, [make_state_record(year=2024)]
            )

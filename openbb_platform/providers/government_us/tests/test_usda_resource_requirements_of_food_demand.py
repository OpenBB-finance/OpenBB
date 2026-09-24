"""Tests for the USDA ERS Resource Requirements of Food Demand utils and model."""

import asyncio
import csv
import io
import zipfile
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.resource_requirements_of_food_demand import (
    DEFAULT_TABLE,
    ResourceRequirementsOfFoodDemandData,
    ResourceRequirementsOfFoodDemandFetcher,
    ResourceRequirementsOfFoodDemandQueryParams,
    _number,
)
from openbb_government_us.usda.utils import ers_resource_requirements_of_food_demand
from openbb_government_us.usda.utils.ers_resource_requirements_of_food_demand import (
    CSV_MEMBER,
    ENERGY_SOURCE_COLUMNS,
    MEASURE_COLUMNS,
    MEDIA_PATH,
    PRODUCT_PAGE,
    TABLES,
    measure_column,
    parse_table,
)

HEADER = [
    "Year",
    "Resource",
    "ResourceDescription",
    "SourceCode",
    "SourceDescription",
    "Unit",
    "TableNumber",
    "TableDescription",
    "TableDescriptionShort",
    "SupplyChainStageNumber",
    "SupplyChainStageDescription",
    "Release",
    "Data",
]

VISIBLE_MEASURES = {"employment", "water", "energy_total"}
HIDDEN_MEASURES = {
    "energy_pa",
    "energy_ng",
    "energy_es",
    "energy_cl",
    "energy_lo",
    "energy_bf",
    "energy_ww",
    "energy_wd",
    "energy_hy",
    "energy_ge",
    "energy_so",
    "energy_wy",
    "energy_cc",
    "energy_sf",
}


def _row(
    year,
    resource,
    source_code,
    data,
    table="Xf1103",
    stage_num="1",
    stage_desc="Total",
):
    """Build one CSV row in HEADER order."""
    return [
        str(year),
        resource,
        f"{resource} desc",
        source_code,
        f"{source_code} desc",
        "unit",
        table,
        f"{table} long",
        "short",
        str(stage_num),
        stage_desc,
        "2026-03-17",
        str(data),
    ]


def _make_csv(rows):
    """Serialize header and rows to CSV text."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(HEADER)
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


BEEF_CSV = _make_csv(
    [
        _row(2011, "Employment", "TOTAL", "100.0"),
        _row(2011, "Water", "TOTAL", "200.0"),
        _row(2011, "Energy", "TOTAL", "300.0"),
        _row(2011, "Energy", "PA", "50.123456789"),
        _row(2011, "Energy", "NG", "40.0"),
        _row(2010, "Employment", "TOTAL", "90.0"),
        _row(2010, "Energy", "TOTAL", "280.0"),
        _row(2010, "Water", "TOTAL", "500.0", stage_num="3", stage_desc="Crops"),
        _row(2010, "Energy", "TOTAL", "28.0", stage_num="3", stage_desc="Crops"),
        _row("NA", "Employment", "TOTAL", "999.0"),
        _row(2010, "Employment", "TOTAL", ""),
        _row(2010, "Other", "ZZ", "7.0"),
        _row(2010, "Energy", "ZZ", "8.0"),
        _row(2012, "Employment", "TOTAL", "5.0", stage_num="X", stage_desc="Weird"),
        _row(2010, "Employment", "TOTAL", "7.0", table="Xf0000"),
    ]
)


def _zip_bytes(text):
    """Wrap the CSV text in a single-member ZIP like the source file."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(CSV_MEMBER, text)
    return buffer.getvalue()


class TestErsResourceRequirementsOfFoodDemandUtils:
    """Tests for the ers_resource_requirements_of_food_demand utils module."""

    def test_catalog_contents(self):
        """The catalog holds the 49 Xf tables and the fixed measure columns."""
        assert len(TABLES) == 49
        assert DEFAULT_TABLE in TABLES
        assert TABLES[DEFAULT_TABLE] == "Food and food-related"
        assert TABLES["Xf1103"] == "Beef"
        assert TABLES["Xf3000"] == "Households"
        assert all(code.startswith("Xf") for code in TABLES)
        assert all(label for label in TABLES.values())
        assert len(MEASURE_COLUMNS) == 17
        assert len(ENERGY_SOURCE_COLUMNS) == 15
        assert set(ENERGY_SOURCE_COLUMNS.values()) <= set(MEASURE_COLUMNS)

    def test_measure_column_employment_and_water(self):
        """Employment and Water map to their single total columns."""
        assert measure_column("Employment", "TOTAL") == "employment"
        assert measure_column("Water", "TOTAL") == "water"

    def test_measure_column_energy_total_and_sources(self):
        """Energy TOTAL maps to energy_total and codes map to energy_<code>."""
        assert measure_column("Energy", "TOTAL") == "energy_total"
        assert measure_column("Energy", "PA") == "energy_pa"
        assert measure_column("Energy", "sf") == "energy_sf"

    def test_measure_column_unknown_resource(self):
        """An unrecognized resource yields no column."""
        assert measure_column("Land", "TOTAL") is None
        assert measure_column("", "TOTAL") is None

    def test_measure_column_unknown_energy_source(self):
        """An unrecognized energy source code yields no column."""
        assert measure_column("Energy", "ZZ") is None

    def test_parse_table_filters_to_selected_table(self):
        """Only rows of the selected table survive; other tables are dropped."""
        records = parse_table(BEEF_CSV, "Xf1103")
        assert len(records) == 10
        assert all(record["table"] == "Xf1103" for record in records)
        other = parse_table(BEEF_CSV, "Xf0000")
        assert len(other) == 1
        assert other[0]["column"] == "employment"

    def test_parse_table_builds_long_records(self):
        """A parsed record carries the year, stage, column, and value."""
        records = parse_table(BEEF_CSV, "Xf1103")
        assert records[0] == {
            "table": "Xf1103",
            "year": 2011,
            "stage": "Total",
            "stage_ord": 1,
            "column": "employment",
            "value": 100.0,
        }
        assert records[3]["column"] == "energy_pa"
        assert records[3]["value"] == 50.123456789

    def test_parse_table_skips_unmapped_blank_and_bad_year(self):
        """Unmapped resources, blank values, and bad years are all dropped."""
        records = parse_table(BEEF_CSV, "Xf1103")
        assert 999.0 not in [record["value"] for record in records]
        assert 7.0 not in [record["value"] for record in records]
        assert 8.0 not in [record["value"] for record in records]
        assert all(record["value"] != "" for record in records)

    def test_parse_table_stage_ordinal_fallback(self):
        """A non-numeric supply-chain stage number yields a zero ordinal."""
        records = parse_table(BEEF_CSV, "Xf1103")
        weird = next(record for record in records if record["stage"] == "Weird")
        assert weird["stage_ord"] == 0

    def test_afetch_table(self, monkeypatch):
        """afetch_table pulls the ZIP through the cache and parses the CSV."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return _zip_bytes(BEEF_CSV)

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_resource_requirements_of_food_demand.afetch_table("Xf1103")
        )
        assert calls == [(MEDIA_PATH, PRODUCT_PAGE)]
        assert len(records) == 10


class TestResourceRequirementsOfFoodDemand:
    """Tests for the ResourceRequirementsOfFoodDemand model."""

    def test_number_helper(self):
        """The numeric column helper adds hide only when requested."""
        assert _number("Header") == {
            "x-widget_config": {"headerName": "Header", "cellDataType": "number"}
        }
        assert _number("Header", hide=True)["x-widget_config"]["hide"] is True

    def test_transform_query_default_table(self):
        """transform_query defaults the table and keeps year filters."""
        query = ResourceRequirementsOfFoodDemandFetcher.transform_query(
            {"start_year": 2015}
        )
        assert isinstance(query, ResourceRequirementsOfFoodDemandQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.start_year == 2015

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert (
            ResourceRequirementsOfFoodDemandQueryParams(table=None).table
            == DEFAULT_TABLE
        )
        assert (
            ResourceRequirementsOfFoodDemandQueryParams(table="").table == DEFAULT_TABLE
        )

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        query = ResourceRequirementsOfFoodDemandQueryParams(table="  Xf1103  ")
        assert query.table == "Xf1103"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            ResourceRequirementsOfFoodDemandQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            ResourceRequirementsOfFoodDemandQueryParams(table=123)

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(
            ers_resource_requirements_of_food_demand,
            "afetch_table",
            fake_afetch_table,
        )
        query = ResourceRequirementsOfFoodDemandFetcher.transform_query(
            {"table": "Xf3000"}
        )
        records = asyncio.run(
            ResourceRequirementsOfFoodDemandFetcher.aextract_data(query, None)
        )
        assert fetched == ["Xf3000"]
        assert records == [{"table": "Xf3000"}]

    def test_transform_data_pivots_measures_into_columns(self):
        """Each resource-and-source measure becomes its own value column."""
        records = parse_table(BEEF_CSV, "Xf1103")
        query = ResourceRequirementsOfFoodDemandFetcher.transform_query(
            {"table": "Xf1103"}
        )
        data = ResourceRequirementsOfFoodDemandFetcher.transform_data(query, records)
        total_2011 = next(
            row for row in data if row.year == 2011 and row.stage == "Total"
        )
        dumped = total_2011.model_dump()
        assert dumped["employment"] == 100.0
        assert dumped["water"] == 200.0
        assert dumped["energy_total"] == 300.0
        assert dumped["energy_pa"] == 50.123456789
        assert dumped["energy_ng"] == 40.0
        assert dumped["energy_es"] is None

    def test_transform_data_orders_chronologically(self):
        """Rows sort by year then stage ordinal, oldest year first."""
        records = parse_table(BEEF_CSV, "Xf1103")
        query = ResourceRequirementsOfFoodDemandFetcher.transform_query(
            {"table": "Xf1103"}
        )
        data = ResourceRequirementsOfFoodDemandFetcher.transform_data(query, records)
        order = [(row.year, row.stage) for row in data]
        assert order == [
            (2010, "Total"),
            (2010, "Crops"),
            (2011, "Total"),
            (2012, "Weird"),
        ]

    def test_transform_data_filters_years(self):
        """start_year and end_year filter rows on the integer year."""
        records = parse_table(BEEF_CSV, "Xf1103")
        start = ResourceRequirementsOfFoodDemandFetcher.transform_data(
            ResourceRequirementsOfFoodDemandFetcher.transform_query(
                {"table": "Xf1103", "start_year": 2011}
            ),
            records,
        )
        assert {row.year for row in start} == {2011, 2012}
        end = ResourceRequirementsOfFoodDemandFetcher.transform_data(
            ResourceRequirementsOfFoodDemandFetcher.transform_query(
                {"table": "Xf1103", "end_year": 2010}
            ),
            records,
        )
        assert {row.year for row in end} == {2010}

    def test_transform_data_excludes_temp_keys(self):
        """Internal sort keys never leak into the validated records."""
        records = parse_table(BEEF_CSV, "Xf1103")
        query = ResourceRequirementsOfFoodDemandFetcher.transform_query(
            {"table": "Xf1103"}
        )
        data = ResourceRequirementsOfFoodDemandFetcher.transform_data(query, records)
        dumped = data[0].model_dump()
        assert "_order" not in dumped
        assert "_stage_ord" not in dumped
        assert "_table" not in dumped
        assert "table" not in dumped

    def test_query_params_widget_options(self):
        """The table param exposes all 49 tables as a single-select filter."""
        config = ResourceRequirementsOfFoodDemandQueryParams.__json_schema_extra__[
            "table"
        ]["x-widget_config"]
        assert config["multiSelect"] is False
        assert config["multiple"] is False
        assert config["value"] == DEFAULT_TABLE
        assert len(config["options"]) == 49
        assert config["options"][0]["value"] == "Xf0000"

    def test_widget_model_config(self):
        """The whole-widget config carries the name, category, and source."""
        config = ResourceRequirementsOfFoodDemandData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.name"] == "USDA ERS Resource Requirements of Food Demand"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]

    def test_visible_and_hidden_measure_columns(self):
        """Totals stay visible while the by-source energy breakdown is hidden."""
        fields = ResourceRequirementsOfFoodDemandData.model_fields
        for name in VISIBLE_MEASURES:
            extra = fields[name].json_schema_extra["x-widget_config"]
            assert "hide" not in extra
        for name in HIDDEN_MEASURES:
            extra = fields[name].json_schema_extra["x-widget_config"]
            assert extra["hide"] is True

    def test_columns_defs_bind_to_served_keys(self):
        """Every served key is a declared field with a column definition."""
        records = parse_table(BEEF_CSV, "Xf1103")
        query = ResourceRequirementsOfFoodDemandFetcher.transform_query(
            {"table": "Xf1103"}
        )
        data = ResourceRequirementsOfFoodDemandFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        fields = ResourceRequirementsOfFoodDemandData.model_fields
        assert served == set(fields)
        for name, field in fields.items():
            extra = (field.json_schema_extra or {}).get("x-widget_config", {})
            assert extra.get("headerName")
            assert name in served
        assert "table" not in served
        assert "_table" not in served

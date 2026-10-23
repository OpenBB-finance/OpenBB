"""Tests for the USDA ERS agricultural trade multipliers utils and model."""

import asyncio

from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.agricultural_trade_multipliers import (
    AgriculturalTradeMultipliersData,
    AgriculturalTradeMultipliersFetcher,
    AgriculturalTradeMultipliersQueryParams,
)
from openbb_government_us.usda.utils import ers_agricultural_trade_multipliers
from openbb_government_us.usda.utils.ers_agricultural_trade_multipliers import (
    AGGREGATE_COMMODITY,
    AGRICULTURAL_TRADE_MULTIPLIERS_FILES,
    VARIABLE_FIELDS,
    build_url,
    media_path,
    parse_commodity_id,
    parse_rows,
    parse_value,
)

OUTPUT_UNIT = "Total U.S. dollar economic output per U.S. dollar of export value"
JOBS_UNIT = "Jobs per 1 billion U.S. dollars of export value"

SAMPLE_CSV = (
    '"COMMID","CommodityName","Variable","Unit","Value","Year"\n'
    '1,"Soybeans","Producer Employment Multiplier","' + JOBS_UNIT + '",'
    "3390.86642305398,2024\n"
    '1,"Soybeans","Producer Output Multiplier","' + OUTPUT_UNIT + '",'
    "1.86409505658884,2024\n"
    '1,"Soybeans","Port Employment Multiplier","' + JOBS_UNIT + '",'
    "3802.09037046935,2024\n"
    '1,"Soybeans","Port Output Multiplier","' + OUTPUT_UNIT + '",'
    "1.81566021784644,2024\n"
    '1,"Soybeans","Export Value","1,000 U.S. dollars",24469752.842,2024\n'
    '3,"Corn ","Producer Employment Multiplier","' + JOBS_UNIT + '",'
    "7968.25317130076,2024\n"
    '3,"Corn ","Producer Output Multiplier","' + OUTPUT_UNIT + '",'
    "2.26589964268361,2024\n"
    '3,"Corn ","Port Employment Multiplier","' + JOBS_UNIT + '",'
    "6312.73273919219,2024\n"
    '3,"Corn ","Port Output Multiplier","' + OUTPUT_UNIT + '",'
    "2.02471964081607,2024\n"
    '3,"Corn ","Export Value","1,000 U.S. dollars",13695938.759,2024\n'
    '3,"Corn ","Bogus Measure","Unknown",99.0,2024\n'
    'NA,NA,"Producer Employment Multiplier","' + JOBS_UNIT + '",NA,2024\n'
    'NA,NA,"Producer Output Multiplier","' + OUTPUT_UNIT + '",NA,2024\n'
    'NA,NA,"Port Employment Multiplier","' + JOBS_UNIT + '",NA,2024\n'
    'NA,NA,"Port Output Multiplier","' + OUTPUT_UNIT + '",NA,2024\n'
    'NA,NA,"Export Value","1,000 U.S. dollars",177208605.317,2024\n'
)


def _long_records():
    """Return long records for the sample CSV."""
    return parse_rows(SAMPLE_CSV)


class TestErsAgriculturalTradeMultipliersUtils:
    """Tests for the ers_agricultural_trade_multipliers utils module."""

    def test_catalog_contents(self):
        """The catalog holds the single table with its media path."""
        assert AGRICULTURAL_TRADE_MULTIPLIERS_FILES == {
            "agricultural_trade_multipliers": (
                "/media/6492/agricultural-trade-multipliers.csv"
            )
        }

    def test_variable_field_mapping(self):
        """The five source variables map to the five wide value fields."""
        assert VARIABLE_FIELDS == {
            "Producer Output Multiplier": "producer_output_multiplier",
            "Producer Employment Multiplier": "producer_employment_multiplier",
            "Port Output Multiplier": "port_output_multiplier",
            "Port Employment Multiplier": "port_employment_multiplier",
            "Export Value": "export_value",
        }

    def test_media_path(self):
        """media_path returns the table's media path."""
        assert media_path() == "/media/6492/agricultural-trade-multipliers.csv"
        assert media_path("agricultural_trade_multipliers") == media_path()

    def test_build_url(self):
        """build_url joins the base URL and the media path."""
        assert build_url() == (
            "https://www.ers.usda.gov/media/6492/agricultural-trade-multipliers.csv"
        )

    def test_parse_value_handles_commas_and_null_tokens(self):
        """Values parse to floats, stripping commas and null tokens to None."""
        assert parse_value("24469752.842") == 24469752.842
        assert parse_value("1,000.5") == 1000.5
        assert parse_value("") is None
        assert parse_value(None) is None
        assert parse_value("NA") is None

    def test_parse_commodity_id_handles_null_tokens(self):
        """Commodity ids parse to ints, coercing null tokens to None."""
        assert parse_commodity_id("3") == 3
        assert parse_commodity_id(" 84 ") == 84
        assert parse_commodity_id("") is None
        assert parse_commodity_id(None) is None
        assert parse_commodity_id("NA") is None

    def test_parse_rows_maps_variables_and_strips_names(self):
        """Rows map each variable to a field and strip trailing name whitespace."""
        rows = _long_records()
        soybeans = [row for row in rows if row["commodity"] == "Soybeans"]
        assert {row["field"] for row in soybeans} == set(VARIABLE_FIELDS.values())
        corn = [row for row in rows if row["commodity_id"] == 3]
        assert {row["commodity"] for row in corn} == {"Corn"}
        export = next(row for row in soybeans if row["field"] == "export_value")
        assert export["value"] == 24469752.842
        assert export["unit"] == "1,000 U.S. dollars"
        assert export["year"] == 2024

    def test_parse_rows_skips_unknown_variable(self):
        """Rows with a variable outside the fixed set are dropped."""
        rows = _long_records()
        assert all(row["field"] in set(VARIABLE_FIELDS.values()) for row in rows)
        assert not any(row["value"] == 99.0 for row in rows)

    def test_parse_rows_relabels_aggregate_row(self):
        """The null-token aggregate row is relabeled with a null commodity id."""
        rows = _long_records()
        aggregate = [row for row in rows if row["commodity"] == AGGREGATE_COMMODITY]
        assert len(aggregate) == 5
        assert all(row["commodity_id"] is None for row in aggregate)
        export = next(row for row in aggregate if row["field"] == "export_value")
        assert export["value"] == 177208605.317
        multipliers = [row for row in aggregate if row["field"] != "export_value"]
        assert all(row["value"] is None for row in multipliers)

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches through the ERS cache client and parses the CSV."""
        calls = []

        async def fake_afetch_ers_file(path, product=None, ttl=None):
            calls.append((path, product))
            return SAMPLE_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        rows = asyncio.run(ers_agricultural_trade_multipliers.afetch_table())
        assert calls == [
            (
                "/media/6492/agricultural-trade-multipliers.csv",
                ers_agricultural_trade_multipliers.PRODUCT_PAGE,
            )
        ]
        assert {row["commodity"] for row in rows} == {
            "Soybeans",
            "Corn",
            AGGREGATE_COMMODITY,
        }


class TestAgriculturalTradeMultipliers:
    """Tests for the AgriculturalTradeMultipliers model."""

    def test_transform_query(self):
        """transform_query builds the parameter-free query params model."""
        query = AgriculturalTradeMultipliersFetcher.transform_query({})
        assert isinstance(query, AgriculturalTradeMultipliersQueryParams)

    def test_aextract_data(self, monkeypatch):
        """aextract_data returns the util's long records."""

        async def fake_afetch_table(**kwargs):
            return _long_records()

        monkeypatch.setattr(
            ers_agricultural_trade_multipliers, "afetch_table", fake_afetch_table
        )
        query = AgriculturalTradeMultipliersFetcher.transform_query({})
        records = asyncio.run(
            AgriculturalTradeMultipliersFetcher.aextract_data(query, None)
        )
        assert {row["commodity"] for row in records} == {
            "Soybeans",
            "Corn",
            AGGREGATE_COMMODITY,
        }

    def test_transform_data_pivots_variables_into_columns(self):
        """Each variable becomes a column, one wide row per commodity."""
        query = AgriculturalTradeMultipliersFetcher.transform_query({})
        data = AgriculturalTradeMultipliersFetcher.transform_data(
            query, _long_records()
        )
        assert [row.commodity for row in data] == [
            "Soybeans",
            "Corn",
            AGGREGATE_COMMODITY,
        ]
        soybeans = data[0]
        assert isinstance(soybeans, AgriculturalTradeMultipliersData)
        assert soybeans.commodity_id == 1
        assert soybeans.year == 2024
        assert soybeans.producer_output_multiplier == 1.86409505658884
        assert soybeans.producer_employment_multiplier == 3390.86642305398
        assert soybeans.port_output_multiplier == 1.81566021784644
        assert soybeans.port_employment_multiplier == 3802.09037046935
        assert soybeans.export_value == 24469752.842

    def test_transform_data_aggregate_row(self):
        """The aggregate row carries only the export value, multipliers null."""
        query = AgriculturalTradeMultipliersFetcher.transform_query({})
        data = AgriculturalTradeMultipliersFetcher.transform_data(
            query, _long_records()
        )
        aggregate = next(row for row in data if row.commodity == AGGREGATE_COMMODITY)
        assert aggregate.commodity_id is None
        assert aggregate.export_value == 177208605.317
        assert aggregate.producer_output_multiplier is None
        assert aggregate.producer_employment_multiplier is None
        assert aggregate.port_output_multiplier is None
        assert aggregate.port_employment_multiplier is None

    def test_transform_data_preserves_source_order(self):
        """Rows keep the CSV's export-value-descending source order."""
        records = list(reversed(_long_records()))
        query = AgriculturalTradeMultipliersFetcher.transform_query({})
        data = AgriculturalTradeMultipliersFetcher.transform_data(query, records)
        assert [row.commodity for row in data] == [
            AGGREGATE_COMMODITY,
            "Corn",
            "Soybeans",
        ]

    def test_columns_defs_bind_to_served_keys(self):
        """Every columnsDefs field binds to a served key, and vice versa."""
        query = AgriculturalTradeMultipliersFetcher.transform_query({})
        data = AgriculturalTradeMultipliersFetcher.transform_data(
            query, _long_records()
        )
        column_fields = set()
        for name, info in AgriculturalTradeMultipliersData.model_fields.items():
            extra = info.json_schema_extra or {}
            config = extra.get("x-widget_config", {})
            assert "headerName" in config
            column_fields.add(to_snake(info.serialization_alias or name))
        for row in data:
            served = set(row.model_dump(by_alias=True))
            assert served == column_fields

    def test_widget_config_metadata(self):
        """The whole-widget config sets the name, category, and source."""
        config = AgriculturalTradeMultipliersData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]
        assert config["$.name"] == "USDA ERS Agricultural Trade Multipliers"

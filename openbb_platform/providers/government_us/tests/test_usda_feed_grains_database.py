"""Tests for the USDA ERS feed grains database utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.feed_grains_database import (
    DEFAULT_TABLE,
    FeedGrainsDatabaseData,
    FeedGrainsDatabaseFetcher,
    FeedGrainsDatabaseQueryParams,
)
from openbb_government_us.usda.utils import ers_feed_grains
from openbb_government_us.usda.utils.ers_feed_grains import (
    FEED_GRAINS_TABLES,
    MEDIA_PATH,
    PRODUCT_PAGE,
    build_url,
    parse_rows,
    table_key,
)

HEADER = (
    "table_group,table_name,commodity_group,commodity,attribute,geography,"
    "year,frequency,timeperiod,unit,amount\n"
)

CORN_NAME = "Table 4--Corn: Supply and disappearance, million bushels"
FARM_PRICE_NAME = "Table 9--Corn and sorghum: Prices received by farmers, United States"
EXPORTS_NAME = "Table 22--U.S. corn and sorghum exports by selected destinations"
WHITE_CORN_NAME = "Table 26--U.S. white corn exports by selected destinations"
ANIMAL_NAME = "Table 30--Indexes of feed consuming animal units, millions"

YEARBOOK_CSV = HEADER + (
    f'supply_and_use,"{CORN_NAME}",Corn,Corn,Beginning stocks,United States,'
    "1975,Annual,Marketing year Sep-Aug,Million bushels,558.0\n"
    f'supply_and_use,"{CORN_NAME}",Corn,Corn,Production,United States,'
    "1975,Annual,Marketing year Sep-Aug,Million bushels,5840.757\n"
    f'supply_and_use,"{CORN_NAME}",Corn,Corn,Ending stocks,United States,'
    "1975,Annual,Marketing year Sep-Aug,Million bushels,\n"
    f'supply_and_use,"{CORN_NAME}",Corn,Corn,Beginning stocks,United States,'
    "1976,Annual,Marketing year Sep-Aug,Million bushels,633.2\n"
    f'supply_and_use,"{CORN_NAME}",Corn,Corn,Production,United States,'
    "1976,Annual,Marketing year Sep-Aug,Million bushels,6289.169\n"
    f'prices,"{FARM_PRICE_NAME}",Corn,Corn,Prices received by farmers,'
    "United States,1975,Annual,Marketing year Sep-Aug,Dollars per bushel,2.5\n"
    f'prices,"{FARM_PRICE_NAME}",Sorghum,Sorghum,Prices received by farmers,'
    "United States,1975,Annual,Marketing year Sep-Aug,Dollars per bushel,2.3\n"
    f'prices,"{FARM_PRICE_NAME}",Sorghum,Sorghum,Prices received by farmers,'
    "United States,1975,Annual,Marketing year Sep-Aug,"
    "Dollars per hundredweight,4.1\n"
    f"trade,{EXPORTS_NAME},Corn,Corn,Exports,Algeria,"
    '1989,Annual,Marketing year Sep-Aug,"1,000 metric tons",1.1747\n'
    f"trade,{EXPORTS_NAME},Sorghum,Sorghum,Exports,Algeria,"
    '1989,Annual,Marketing year Sep-Aug,"1,000 metric tons",24.517\n'
    f"trade,{EXPORTS_NAME},Corn,Corn,Exports,Mexico,"
    '1989,Annual,Marketing year Sep-Aug,"1,000 metric tons",100.0\n'
    f"trade,{WHITE_CORN_NAME},White corn,White corn,Exports,Japan,"
    '1990,Annual,Marketing year Sep-Aug,"1,000 metric tons",5.5\n'
    f"trade,{WHITE_CORN_NAME},White corn,White corn,Exports,Mexico,"
    '1990,Annual,Marketing year Sep-Aug,"1,000 metric tons",10.2\n'
    f'animal_units,"{ANIMAL_NAME}",Grain and roughage-consuming animal units '
    "(GRCAU),Dairy,Index,United States,1976,Annual,Marketing year Sep-Aug,"
    "Million animal units,13.6346\n"
    f'animal_units,"{ANIMAL_NAME}",Grain and roughage-consuming animal units '
    "(GRCAU),Hogs,Index,United States,1976,Annual,Marketing year Sep-Aug,"
    "Million animal units,9.0463\n"
    f'animal_units,"{ANIMAL_NAME}",Grain-consuming animal units (GCAU),Dairy,'
    "Index,United States,1976,Annual,Marketing year Sep-Aug,"
    "Million animal units,12.0\n"
)


REDUNDANT_GEOGRAPHY_CSV = HEADER + (
    f'supply_and_use,"{CORN_NAME}",Corn,Corn,Beginning stocks,United States,'
    "1975,Annual,Marketing year Sep-Aug,Million bushels,558.0\n"
    f'supply_and_use,"{CORN_NAME}",Corn,Corn,Exports,World,'
    "1975,Annual,Marketing year Sep-Aug,Million bushels,1695.0\n"
)


def _records_for(table: str) -> list[dict]:
    """Return parsed rows for one table slug."""
    return [record for record in parse_rows(YEARBOOK_CSV) if record["table"] == table]


class TestErsFeedGrainsUtils:
    """Tests for the ers_feed_grains utils module."""

    def test_catalog_contents(self):
        """The catalog holds the 35 yearbook tables with number, name, group."""
        assert len(FEED_GRAINS_TABLES) == 35
        assert FEED_GRAINS_TABLES["corn_supply_and_use"]["number"] == 4
        for config in FEED_GRAINS_TABLES.values():
            assert config["name"].startswith("Table ")
            assert config["group"]

    def test_build_url_joins_base_and_media_path(self):
        """build_url joins the base URL and the media path."""
        assert build_url() == f"https://www.ers.usda.gov{MEDIA_PATH}"

    def test_table_key_resolves_known_name(self):
        """A published table name resolves to its slug and number."""
        assert table_key(CORN_NAME) == ("corn_supply_and_use", 4)
        assert table_key(ANIMAL_NAME) == ("animal_unit_indexes", 30)

    def test_table_key_falls_back_to_number(self):
        """An uncataloged 'Table N--' name falls back to a numbered slug."""
        assert table_key("Table 99--Some new experimental table") == ("table_99", 99)

    def test_table_key_raises_without_prefix(self):
        """A name without a 'Table N--' prefix raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Unrecognized table name"):
            table_key("Corn balance sheet")

    def test_parse_rows_types_and_skips_blank_amount(self):
        """parse_rows coerces year and value, and drops blank-amount rows."""
        records = _records_for("corn_supply_and_use")
        assert len(records) == 4
        assert records[0] == {
            "table": "corn_supply_and_use",
            "table_number": 4,
            "table_name": CORN_NAME,
            "table_group": "supply_and_use",
            "commodity_group": "Corn",
            "commodity": "Corn",
            "attribute": "Beginning stocks",
            "geography": "United States",
            "year": 1975,
            "frequency": "Annual",
            "timeperiod": "Marketing year Sep-Aug",
            "unit": "Million bushels",
            "value": 558.0,
        }
        assert "Ending stocks" not in {record["attribute"] for record in records}

    def test_parse_rows_covers_all_tables(self):
        """Every synthetic table slug is recovered from the tidy CSV."""
        slugs = {record["table"] for record in parse_rows(YEARBOOK_CSV)}
        assert slugs == {
            "corn_supply_and_use",
            "corn_and_sorghum_farm_prices",
            "corn_and_sorghum_exports_by_destination",
            "white_corn_exports_by_destination",
            "animal_unit_indexes",
        }

    def test_afetch_yearbook(self, monkeypatch):
        """afetch_yearbook fetches the CSV through the ERS cache and parses it."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return YEARBOOK_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ers_feed_grains.afetch_yearbook())
        assert calls == [(MEDIA_PATH, PRODUCT_PAGE)]
        assert len(records) == 15
        assert records[0]["table"] == "corn_supply_and_use"


class TestFeedGrainsDatabase:
    """Tests for the FeedGrainsDatabase model."""

    def test_transform_query_default_table(self):
        """transform_query defaults the table and keeps year filters."""
        query = FeedGrainsDatabaseFetcher.transform_query({"start_year": 2000})
        assert isinstance(query, FeedGrainsDatabaseQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.start_year == 2000

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert (
            FeedGrainsDatabaseQueryParams.model_validate({"table": None}).table
            == DEFAULT_TABLE
        )
        assert FeedGrainsDatabaseQueryParams(table="").table == DEFAULT_TABLE

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        query = FeedGrainsDatabaseQueryParams(table="  barley_supply_and_use  ")
        assert query.table == "barley_supply_and_use"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            FeedGrainsDatabaseQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            FeedGrainsDatabaseQueryParams.model_validate({"table": 123})

    def test_aextract_data_filters_selected_table(self, monkeypatch):
        """aextract_data returns only the selected table's rows."""

        async def fake_afetch_yearbook(**kwargs):
            return parse_rows(YEARBOOK_CSV)

        monkeypatch.setattr(ers_feed_grains, "afetch_yearbook", fake_afetch_yearbook)
        query = FeedGrainsDatabaseFetcher.transform_query(
            {"table": "corn_and_sorghum_farm_prices"}
        )
        records = asyncio.run(FeedGrainsDatabaseFetcher.aextract_data(query, None))
        assert {record["table"] for record in records} == {
            "corn_and_sorghum_farm_prices"
        }
        assert len(records) == 3

    def test_data_model_only_serves_period_field(self):
        """The static served schema is a single pinned period string."""
        assert set(FeedGrainsDatabaseData.model_fields) == {"period"}

    def test_transform_data_series_attribute_folds_unit_into_columns(self):
        """Attribute-varying tables spread attributes into unit-tagged columns."""
        query = FeedGrainsDatabaseFetcher.transform_query(
            {"table": "corn_supply_and_use"}
        )
        data = FeedGrainsDatabaseFetcher.transform_data(
            query, _records_for("corn_supply_and_use")
        )
        dumped = [row.model_dump() for row in data]
        assert [row["period"] for row in dumped] == [
            "1975 Marketing year Sep-Aug",
            "1976 Marketing year Sep-Aug",
        ]
        first = dumped[0]
        assert first["Beginning stocks (Million bushels)"] == 558.0
        assert first["Production (Million bushels)"] == 5840.757

    def test_transform_data_multi_unit_series_split_into_columns(self):
        """A commodity published in two units yields one column per unit."""
        query = FeedGrainsDatabaseFetcher.transform_query(
            {"table": "corn_and_sorghum_farm_prices"}
        )
        data = FeedGrainsDatabaseFetcher.transform_data(
            query, _records_for("corn_and_sorghum_farm_prices")
        )
        dumped = [row.model_dump() for row in data]
        assert len(dumped) == 1
        row = dumped[0]
        assert row["period"] == "1975 Marketing year Sep-Aug"
        assert row["Corn (Dollars per bushel)"] == 2.5
        assert row["Sorghum (Dollars per bushel)"] == 2.3
        assert row["Sorghum (Dollars per hundredweight)"] == 4.1

    def test_transform_data_folds_geography_into_period(self):
        """Commodity-varying trade tables fold geography into the period label."""
        query = FeedGrainsDatabaseFetcher.transform_query(
            {"table": "corn_and_sorghum_exports_by_destination"}
        )
        data = FeedGrainsDatabaseFetcher.transform_data(
            query, _records_for("corn_and_sorghum_exports_by_destination")
        )
        dumped = [row.model_dump() for row in data]
        assert {row["period"] for row in dumped} == {
            "Algeria — 1989 Marketing year Sep-Aug",
            "Mexico — 1989 Marketing year Sep-Aug",
        }
        algeria = next(row for row in dumped if row["period"].startswith("Algeria"))
        assert algeria["Corn (1,000 metric tons)"] == 1.1747
        assert algeria["Sorghum (1,000 metric tons)"] == 24.517
        mexico = next(row for row in dumped if row["period"].startswith("Mexico"))
        assert mexico["Corn (1,000 metric tons)"] == 100.0
        assert mexico["Sorghum (1,000 metric tons)"] is None

    def test_transform_data_single_value_column(self):
        """A single-attribute single-commodity table yields one value column."""
        query = FeedGrainsDatabaseFetcher.transform_query(
            {"table": "white_corn_exports_by_destination"}
        )
        data = FeedGrainsDatabaseFetcher.transform_data(
            query, _records_for("white_corn_exports_by_destination")
        )
        dumped = [row.model_dump() for row in data]
        assert {row["period"] for row in dumped} == {
            "Japan — 1990 Marketing year Sep-Aug",
            "Mexico — 1990 Marketing year Sep-Aug",
        }
        japan = next(row for row in dumped if row["period"].startswith("Japan"))
        assert japan["Exports (1,000 metric tons)"] == 5.5

    def test_transform_data_folds_commodity_group_into_period(self):
        """An animal-unit table folds the commodity group into the period."""
        query = FeedGrainsDatabaseFetcher.transform_query(
            {"table": "animal_unit_indexes"}
        )
        data = FeedGrainsDatabaseFetcher.transform_data(
            query, _records_for("animal_unit_indexes")
        )
        dumped = [row.model_dump() for row in data]
        grcau = next(
            row
            for row in dumped
            if row["period"].startswith(
                "Grain and roughage-consuming animal units (GRCAU)"
            )
        )
        assert grcau["Dairy (Million animal units)"] == 13.6346
        assert grcau["Hogs (Million animal units)"] == 9.0463
        gcau = next(
            row
            for row in dumped
            if row["period"].startswith("Grain-consuming animal units (GCAU)")
        )
        assert gcau["Dairy (Million animal units)"] == 12.0
        assert gcau["Hogs (Million animal units)"] is None

    def test_transform_data_skips_a_geography_that_restates_the_series(self):
        """A geography holding one value per series is not folded into the period."""
        records = [
            record
            for record in parse_rows(REDUNDANT_GEOGRAPHY_CSV)
            if record["table"] == "corn_supply_and_use"
        ]
        query = FeedGrainsDatabaseFetcher.transform_query(
            {"table": "corn_supply_and_use"}
        )
        data = FeedGrainsDatabaseFetcher.transform_data(query, records)
        assert [row.model_dump() for row in data] == [
            {
                "period": "1975 Marketing year Sep-Aug",
                "Beginning stocks (Million bushels)": 558.0,
                "Exports (Million bushels)": 1695.0,
            }
        ]

    def test_transform_data_no_duplicate_rows(self):
        """No two served rows share a period label or identical content."""
        for table in (
            "corn_supply_and_use",
            "corn_and_sorghum_farm_prices",
            "corn_and_sorghum_exports_by_destination",
            "white_corn_exports_by_destination",
            "animal_unit_indexes",
        ):
            query = FeedGrainsDatabaseFetcher.transform_query({"table": table})
            data = FeedGrainsDatabaseFetcher.transform_data(query, _records_for(table))
            dumped = [row.model_dump() for row in data]
            periods = [row["period"] for row in dumped]
            assert len(periods) == len(set(periods))
            for row in dumped:
                assert set(FeedGrainsDatabaseData.model_fields) == {"period"}

    def test_transform_data_filters_years(self):
        """start_year and end_year filter rows on the integer year."""
        records = _records_for("corn_supply_and_use")
        start = FeedGrainsDatabaseFetcher.transform_data(
            FeedGrainsDatabaseFetcher.transform_query(
                {"table": "corn_supply_and_use", "start_year": 1976}
            ),
            records,
        )
        assert {row.period for row in start} == {"1976 Marketing year Sep-Aug"}
        end = FeedGrainsDatabaseFetcher.transform_data(
            FeedGrainsDatabaseFetcher.transform_query(
                {"table": "corn_supply_and_use", "end_year": 1975}
            ),
            records,
        )
        assert {row.period for row in end} == {"1975 Marketing year Sep-Aug"}

    def test_transform_data_empty_slice_returns_empty(self):
        """A year window that excludes every row returns no records."""
        records = _records_for("corn_supply_and_use")
        result = FeedGrainsDatabaseFetcher.transform_data(
            FeedGrainsDatabaseFetcher.transform_query(
                {"table": "corn_supply_and_use", "start_year": 3000}
            ),
            records,
        )
        assert result == []

    def test_transform_data_no_rows_returns_empty(self):
        """An empty input returns no records."""
        query = FeedGrainsDatabaseFetcher.transform_query(
            {"table": "corn_supply_and_use"}
        )
        assert FeedGrainsDatabaseFetcher.transform_data(query, []) == []

    def test_transform_data_collapses_duplicate_records(self):
        """A duplicated row-key and series cell collapses to a single row."""
        records = [
            {
                "table": "corn_supply_and_use",
                "commodity_group": "Corn",
                "commodity": "Corn",
                "attribute": "Production",
                "geography": "United States",
                "year": 1975,
                "timeperiod": "Marketing year Sep-Aug",
                "unit": "Million bushels",
                "value": 5840.757,
            },
            {
                "table": "corn_supply_and_use",
                "commodity_group": "Corn",
                "commodity": "Corn",
                "attribute": "Production",
                "geography": "United States",
                "year": 1975,
                "timeperiod": "Marketing year Sep-Aug",
                "unit": "Million bushels",
                "value": 5840.757,
            },
        ]
        query = FeedGrainsDatabaseFetcher.transform_query(
            {"table": "corn_supply_and_use"}
        )
        data = FeedGrainsDatabaseFetcher.transform_data(query, records)
        assert len(data) == 1
        assert data[0].period == "1975 Marketing year Sep-Aug"
        assert data[0].model_dump()["Production (Million bushels)"] == 5840.757

    def test_transform_data_excludes_sort_keys(self):
        """Internal sort keys never leak into the validated records."""
        query = FeedGrainsDatabaseFetcher.transform_query(
            {"table": "corn_supply_and_use"}
        )
        data = FeedGrainsDatabaseFetcher.transform_data(
            query, _records_for("corn_supply_and_use")
        )
        dumped = data[0].model_dump()
        assert not any(key.startswith("_") for key in dumped)

    def test_data_model_keeps_dynamic_columns_and_precision(self):
        """The Data model preserves dynamic columns at full precision."""
        row = FeedGrainsDatabaseData.model_validate(
            {
                "period": "1975 Marketing year Sep-Aug",
                "Feed and residual use (Million bushels)": 3581.7600000001,
            }
        )
        assert (
            row.model_dump()["Feed and residual use (Million bushels)"]
            == 3581.7600000001
        )

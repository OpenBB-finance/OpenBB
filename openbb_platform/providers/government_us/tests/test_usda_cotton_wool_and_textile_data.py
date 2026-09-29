"""Tests for the USDA ERS cotton, wool, and textile data utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.cotton_wool_and_textile_data import (
    DEFAULT_TABLE,
    CottonWoolAndTextileDataData,
    CottonWoolAndTextileDataFetcher,
    CottonWoolAndTextileDataQueryParams,
)
from openbb_government_us.usda.utils import ers_cotton_wool_and_textile_data
from openbb_government_us.usda.utils.ers_cotton_wool_and_textile_data import (
    CWT_TABLES,
    M_RFE_IMPORTS_BY_ORIGIN,
    M_US_COTTON,
    RFE_PRODUCT,
    ROW_DIM_FIELDS,
    YEARBOOK_PRODUCT,
    _table_number,
    afetch_table,
    classify_frequency,
    parse_table,
    table_frequencies,
)

SUPPLY_CSV = (
    "table_number,table_name,month,period,period_name,geography,Type,category,"
    "value,units\n"
    "1,US cotton,annual,1975,marketing year,US,Area,area_planted,9478,acres\n"
    "1,US cotton,annual,1975,marketing year,US,Supply,production,8302,bales\n"
    "1,US cotton,annual,1975,marketing year,US,farm_price,farm_price,51.3,cents\n"
    "1,US cotton,annual,1976,marketing year,US,Area,area_planted,11636,acres\n"
    "1,US cotton,annual,,marketing year,US,Supply,production,12,bales\n"
    "1,US cotton,annual,abcd,marketing year,US,Supply,production,13,bales\n"
    "1,US cotton,annual,1976,marketing year,US,Supply,production,,bales\n"
    "2,US upland,annual,1975,marketing year,US,Area,area_planted,9000,acres\n"
)

BY_STATE_CSV = (
    "table_number,table_name,month,period,period_name,geography,Type,category,"
    "value,units\n"
    "4,Upland acreage,annual,1975,marketing year,US,National,"
    "upland_cotton_planted_acreage,9478,acres\n"
    "4,Upland acreage,annual,1975,marketing year,TX,State,"
    "upland_cotton_planted_acreage,4200,acres\n"
    "4,Upland acreage,annual,1976,marketing year,US,National,"
    "upland_cotton_planted_acreage,11636,acres\n"
)

ELS_CSV = (
    "table_number,table_name,month,period,period_name,geography,Type,category,"
    "value,units\n"
    "8,ELS acreage,annual,2024,marketing year,US,National,"
    "extra_long_Staple_cotton_planted_acreage,207,acres\n"
    "8,ELS acreage,annual,2024,marketing year,CA,State,"
    "extra_long_staple_cotton_planted_acreage,145,acres\n"
    "8,ELS acreage,annual,2024,marketing year,US,National,"
    "extra_long_Staple_cotton_harvested_acreage,201,acres\n"
)

MONTHLY_CSV = (
    "table_number,table_name,month,period,period_name,geography,Type,category,"
    "value,units\n"
    "10,Monthly,8,2024,marketing year,,Supply,total_supply,3628,bales\n"
    "10,Monthly,9,2024,marketing year,,Supply,total_supply,3449,bales\n"
    "10,Monthly,8,2024,marketing year,,Disappearance,exports,721,bales\n"
)

PRICES_CSV = (
    "table_number,table_name,time_period,period,period_name,category,value,units,\n"
    "13,Quotes,1,2024,marketing year,far_east_a_index,90.5,cents,\n"
    "13,Quotes,2,2024,marketing year,far_east_a_index,91.0,cents,\n"
)

TEXTILE_CSV = (
    "table_number,table_name,month,period,period_name,trade_category,fiber,"
    "textile_group,textile_category,value,units\n"
    "35,RFE,annual,1989,calendar year,imports,cotton,All,All,100,pounds\n"
    "35,RFE,annual,1989,calendar year,imports,wool,All,All,50,pounds\n"
    "35,RFE,annual,1989,calendar year,exports,cotton,All,All,30,pounds\n"
)

TEXTILE_CATEGORY_CSV = (
    "table_number,table_name,month,period,period_name,trade_category,fiber,"
    "textile_group,textile_category,value,units\n"
    "36,Cotton imports,1,2024,calendar year,imports,cotton,Apparel,tops,232,pounds\n"
    "36,Cotton imports,1,2024,calendar year,imports,cotton,Apparel,bottoms,143,pounds\n"
    "36,Cotton imports,1,2024,calendar year,imports,cotton,Floor coverings,tufted,"
    "12,pounds\n"
)

RFE_FIBER_CSV = (
    "table_num,table_name,Item,fiber,period,period_name,value,unit\n"
    "1,Textile imports,Apparel,Cotton,1989,calendar year,1435,pounds\n"
    "1,Textile imports,Apparel,Wool,1989,calendar year,131,pounds\n"
    "1,Textile imports,Apparel,Cotton,1990,calendar year,1508,pounds\n"
)

RFE_ORIGIN_CSV = (
    "table_num,table_name,Region/country,year,period_name,value,unit\n"
    "3,Cotton imports by origin,World,2022,calendar year,100,pounds\n"
    "3,Cotton imports by origin,World,2023,calendar year,110,pounds\n"
    "3,Cotton imports by origin,Canada,2022,calendar year,20,pounds\n"
    "3,Cotton imports by origin,Canada,2023,calendar year,NA,pounds\n"
)


class TestErsCottonWoolTextileUtils:
    """Tests for the ers_cotton_wool_and_textile_data utils module."""

    def test_catalog_contents(self):
        """The catalog holds the 49 tables mapped to their source files."""
        assert len(CWT_TABLES) == 49
        assert CWT_TABLES[DEFAULT_TABLE]["media"] == M_US_COTTON
        assert CWT_TABLES[DEFAULT_TABLE]["product"] == YEARBOOK_PRODUCT
        years_pivot = [
            key for key, cfg in CWT_TABLES.items() if cfg["pivot"] == "years"
        ]
        assert years_pivot == [
            "rfe_cotton_textile_imports_by_origin",
            "rfe_cotton_textile_exports_by_destination",
        ]
        rfe = CWT_TABLES["rfe_cotton_textile_imports_by_origin"]
        assert rfe["media"] == M_RFE_IMPORTS_BY_ORIGIN
        assert rfe["product"] == RFE_PRODUCT
        assert rfe["year_col"] == "year"
        assert rfe["series_col"] is None
        for cfg in CWT_TABLES.values():
            assert cfg["label"]
            assert cfg["number"]
            assert cfg["unit_col"] in ("units", "unit")

    def test_table_number_reads_both_column_names(self):
        """The table-number helper reads either source column name."""
        assert _table_number({"table_number": " 5 "}) == "5"
        assert _table_number({"table_num": "3"}) == "3"
        assert _table_number({}) == ""

    def test_parse_table_series_pivot_and_geography_dim(self):
        """A category-series table emits one record per measure and year."""
        records = parse_table(SUPPLY_CSV, "cotton_supply_and_use")
        assert len(records) == 4
        assert records[0] == {
            "table": "cotton_supply_and_use",
            "year": 1975,
            "period": None,
            "geography": None,
            "measure": None,
            "trade_category": None,
            "textile_group": None,
            "item": None,
            "unit": "acres",
            "series": "area_planted",
            "value": 9478.0,
        }
        assert {record["series"] for record in records} == {
            "area_planted",
            "production",
            "farm_price",
        }

    def test_parse_table_filters_to_requested_table_number(self):
        """Rows for other tables in the same file are skipped."""
        records = parse_table(SUPPLY_CSV, "cotton_supply_and_use")
        assert all(record["table"] == "cotton_supply_and_use" for record in records)
        assert all(record["value"] != 9000.0 for record in records)

    def test_parse_table_skips_blank_and_nonnumeric_years(self):
        """Rows with a blank or non-numeric year label are dropped."""
        records = parse_table(SUPPLY_CSV, "cotton_supply_and_use")
        assert all(record["year"] in (1975, 1976) for record in records)
        assert 12.0 not in [record["value"] for record in records]
        assert 13.0 not in [record["value"] for record in records]

    def test_parse_table_skips_blank_value(self):
        """A blank value cell drops the row."""
        records = parse_table(SUPPLY_CSV, "cotton_supply_and_use")
        year_1976 = [record for record in records if record["year"] == 1976]
        assert len(year_1976) == 1
        assert year_1976[0]["series"] == "area_planted"

    def test_parse_table_series_geography(self):
        """A by-State table uses geography as the series column."""
        records = parse_table(BY_STATE_CSV, "upland_planted_acreage_by_state")
        assert {record["series"] for record in records} == {"US", "TX"}
        assert records[0]["geography"] is None

    def test_parse_table_normalizes_measure(self):
        """The ELS by-State table casefolds its measure dimension."""
        records = parse_table(ELS_CSV, "els_acreage_by_state")
        assert {record["measure"] for record in records} == {
            "extra_long_staple_cotton_planted_acreage",
            "extra_long_staple_cotton_harvested_acreage",
        }
        assert {record["series"] for record in records} == {"US", "CA"}

    def test_parse_table_month_period(self):
        """The monthly table reads the month column as the period."""
        records = parse_table(MONTHLY_CSV, "cotton_supply_and_disappearance_monthly")
        assert {record["period"] for record in records} == {"8", "9"}
        assert records[0]["geography"] is None

    def test_parse_table_time_period_column(self):
        """The monthly price table reads time_period as the period."""
        records = parse_table(PRICES_CSV, "cotton_price_quotes_monthly")
        assert {record["period"] for record in records} == {"1", "2"}
        assert {record["series"] for record in records} == {"far_east_a_index"}

    def test_parse_table_textile_trade_category_dim(self):
        """The raw-fiber manufactures table carries the trade-category dim."""
        records = parse_table(TEXTILE_CSV, "raw_fiber_equivalent_textile_manufactures")
        assert {record["series"] for record in records} == {"cotton", "wool"}
        assert {record["trade_category"] for record in records} == {
            "imports",
            "exports",
        }

    def test_parse_table_textile_category_group_dim(self):
        """The by-category textile table carries the textile-group dim."""
        records = parse_table(TEXTILE_CATEGORY_CSV, "raw_cotton_equivalent_imports")
        assert {record["series"] for record in records} == {
            "tops",
            "bottoms",
            "tufted",
        }
        assert {record["textile_group"] for record in records} == {
            "Apparel",
            "Floor coverings",
        }

    def test_parse_table_rfe_item_dim_and_table_num_column(self):
        """The by-fiber table reads table_num and carries the item dim."""
        records = parse_table(RFE_FIBER_CSV, "rfe_textile_imports_by_fiber")
        assert {record["series"] for record in records} == {"Cotton", "Wool"}
        assert {record["item"] for record in records} == {"Apparel"}
        assert records[0]["unit"] == "pounds"

    def test_parse_table_years_pivot_series_none_and_skips_na(self):
        """A years-pivot table has no series and skips NA values."""
        records = parse_table(RFE_ORIGIN_CSV, "rfe_cotton_textile_imports_by_origin")
        assert len(records) == 3
        assert all(record["series"] is None for record in records)
        assert {record["geography"] for record in records} == {"World", "Canada"}
        assert all(record["value"] != 0.0 for record in records)

    def test_afetch_table_yearbook(self, monkeypatch):
        """afetch_table fetches the yearbook file through the ERS cache."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return SUPPLY_CSV.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(afetch_table("cotton_supply_and_use"))
        assert calls == [(M_US_COTTON, YEARBOOK_PRODUCT)]
        assert len(records) == 4

    def test_afetch_table_rfe_product(self, monkeypatch):
        """afetch_table passes the raw-fiber product page for TTL resolution."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return RFE_ORIGIN_CSV.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(afetch_table("rfe_cotton_textile_imports_by_origin"))
        assert calls == [(M_RFE_IMPORTS_BY_ORIGIN, RFE_PRODUCT)]
        assert len(records) == 3

    def test_classify_frequency(self):
        """The period token classifies into Annual, Quarterly, or Monthly."""
        assert classify_frequency(None) == "Annual"
        assert classify_frequency("annual") == "Annual"
        assert classify_frequency("Season") == "Annual"
        assert classify_frequency("1") == "Monthly"
        assert classify_frequency("12") == "Monthly"
        assert classify_frequency("Q3") == "Quarterly"

    def test_table_frequencies_orders_coarse_to_fine(self, monkeypatch):
        """table_frequencies lists the distinct frequencies, Annual first."""

        async def fake_afetch_table(table, **kwargs):
            return [
                {"period": "1"},
                {"period": "Season"},
                {"period": "2"},
            ]

        monkeypatch.setattr(
            ers_cotton_wool_and_textile_data, "afetch_table", fake_afetch_table
        )
        assert asyncio.run(table_frequencies("cotton_supply_and_use")) == [
            "Annual",
            "Monthly",
        ]


class TestCottonWoolAndTextileData:
    """Tests for the CottonWoolAndTextileData model."""

    def test_transform_query_default_table(self):
        """transform_query defaults the table and keeps year filters."""
        query = CottonWoolAndTextileDataFetcher.transform_query({"start_year": 2000})
        assert isinstance(query, CottonWoolAndTextileDataQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.start_year == 2000

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert CottonWoolAndTextileDataQueryParams(table=None).table == DEFAULT_TABLE
        assert CottonWoolAndTextileDataQueryParams(table="").table == DEFAULT_TABLE

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        query = CottonWoolAndTextileDataQueryParams(table="  fiber_prices  ")
        assert query.table == "fiber_prices"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            CottonWoolAndTextileDataQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            CottonWoolAndTextileDataQueryParams(table=123)

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(
            ers_cotton_wool_and_textile_data, "afetch_table", fake_afetch_table
        )
        query = CottonWoolAndTextileDataFetcher.transform_query(
            {"table": "world_cotton_supply_and_use"}
        )
        records = asyncio.run(
            CottonWoolAndTextileDataFetcher.aextract_data(query, None)
        )
        assert fetched == ["world_cotton_supply_and_use"]
        assert records == [{"table": "world_cotton_supply_and_use"}]

    def test_transform_data_empty(self):
        """Empty extracted data returns an empty result."""
        query = CottonWoolAndTextileDataFetcher.transform_query({})
        assert CottonWoolAndTextileDataFetcher.transform_data(query, []) == []

    def test_in_range(self):
        """The year-window helper honors each bound and open ends."""
        query = CottonWoolAndTextileDataFetcher.transform_query(
            {"start_year": 2000, "end_year": 2010}
        )
        assert CottonWoolAndTextileDataFetcher._in_range(2005, query) is True
        assert CottonWoolAndTextileDataFetcher._in_range(1999, query) is False
        assert CottonWoolAndTextileDataFetcher._in_range(2011, query) is False
        open_query = CottonWoolAndTextileDataFetcher.transform_query({})
        assert CottonWoolAndTextileDataFetcher._in_range(1800, open_query) is True

    def test_frequency_blank_returns_none(self):
        """A blank or None frequency normalizes to None."""
        assert CottonWoolAndTextileDataQueryParams(frequency=None).frequency is None
        assert CottonWoolAndTextileDataQueryParams(frequency="").frequency is None

    def test_frequency_title_cased(self):
        """A frequency value is title-cased for a canonical label."""
        assert (
            CottonWoolAndTextileDataQueryParams(frequency="monthly").frequency
            == "Monthly"
        )
        assert (
            CottonWoolAndTextileDataQueryParams(frequency=["annual"]).frequency
            == "Annual"
        )

    def test_resolve_frequency_falls_back_to_finest(self):
        """A requested frequency absent from the table falls back to the finest."""
        query = CottonWoolAndTextileDataFetcher.transform_query(
            {"frequency": "Monthly"}
        )
        data = parse_table(SUPPLY_CSV, "cotton_supply_and_use")
        freq, available = CottonWoolAndTextileDataFetcher._resolve_frequency(
            query, data
        )
        assert available == ["Annual"]
        assert freq == "Annual"

    def test_transform_data_series_into_columns(self):
        """Each series becomes a unit-tagged column with the year in the period."""
        records = parse_table(SUPPLY_CSV, "cotton_supply_and_use")
        query = CottonWoolAndTextileDataFetcher.transform_query({})
        data = CottonWoolAndTextileDataFetcher.transform_data(query, records)
        dumped = [row.model_dump() for row in data]
        row_1975 = next(row for row in dumped if row["period"] == "1975")
        assert row_1975["area planted (acres)"] == 9478.0
        assert row_1975["production (bales)"] == 8302.0
        assert row_1975["farm price (cents)"] == 51.3
        row_1976 = next(row for row in dumped if row["period"] == "1976")
        assert row_1976["area planted (acres)"] == 11636.0
        assert row_1976["production (bales)"] is None

    def test_transform_data_geography_series_columns(self):
        """A by-State table spreads each State into a unit-tagged column."""
        records = parse_table(BY_STATE_CSV, "upland_planted_acreage_by_state")
        query = CottonWoolAndTextileDataFetcher.transform_query({})
        data = CottonWoolAndTextileDataFetcher.transform_data(query, records)
        row_1975 = next(row for row in data if row.period == "1975")
        dumped = row_1975.model_dump()
        assert dumped["US (acres)"] == 9478.0
        assert dumped["TX (acres)"] == 4200.0

    def test_transform_data_rows_sorted_chronologically(self):
        """Series-pivot rows carry the year as the period, newest first."""
        records = parse_table(SUPPLY_CSV, "cotton_supply_and_use")
        query = CottonWoolAndTextileDataFetcher.transform_query({})
        data = CottonWoolAndTextileDataFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["1976", "1975"]

    def test_transform_data_filters_years(self):
        """start_year and end_year filter rows on the integer year."""
        records = parse_table(SUPPLY_CSV, "cotton_supply_and_use")
        start = CottonWoolAndTextileDataFetcher.transform_data(
            CottonWoolAndTextileDataFetcher.transform_query({"start_year": 1976}),
            records,
        )
        assert {row.period for row in start} == {"1976"}
        end = CottonWoolAndTextileDataFetcher.transform_data(
            CottonWoolAndTextileDataFetcher.transform_query({"end_year": 1975}),
            records,
        )
        assert {row.period for row in end} == {"1975"}

    def test_transform_data_year_window_outside_the_series(self):
        """A year window past the published series serves nothing at all."""
        records = parse_table(SUPPLY_CSV, "cotton_supply_and_use")
        assert records
        data = CottonWoolAndTextileDataFetcher.transform_data(
            CottonWoolAndTextileDataFetcher.transform_query({"start_year": 2050}),
            records,
        )
        assert data == []

    def test_transform_data_monthly_period_labels(self):
        """A monthly table labels each row with the year and month name."""
        records = parse_table(PRICES_CSV, "cotton_price_quotes_monthly")
        query = CottonWoolAndTextileDataFetcher.transform_query(
            {"table": "cotton_price_quotes_monthly"}
        )
        data = CottonWoolAndTextileDataFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2024 Feb", "2024 Jan"]
        assert data[1].model_dump()["far east a index (cents)"] == 90.5

    def test_transform_data_folds_measure_into_columns(self):
        """The ELS by-State table folds measure and State into one dense row."""
        records = parse_table(ELS_CSV, "els_acreage_by_state")
        query = CottonWoolAndTextileDataFetcher.transform_query(
            {"table": "els_acreage_by_state"}
        )
        data = CottonWoolAndTextileDataFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2024"]
        dumped = data[0].model_dump()
        assert dumped["extra long staple cotton planted acreage · US (acres)"] == 207.0
        assert dumped["extra long staple cotton planted acreage · CA (acres)"] == 145.0
        assert (
            dumped["extra long staple cotton harvested acreage · US (acres)"] == 201.0
        )

    def test_transform_data_folds_textile_group_into_columns(self):
        """A textile-category table folds the textile group into the header."""
        records = parse_table(TEXTILE_CATEGORY_CSV, "raw_cotton_equivalent_imports")
        query = CottonWoolAndTextileDataFetcher.transform_query(
            {"table": "raw_cotton_equivalent_imports", "frequency": "Monthly"}
        )
        data = CottonWoolAndTextileDataFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2024 Jan"]
        dumped = data[0].model_dump()
        assert dumped["Apparel · tops (pounds)"] == 232.0
        assert dumped["Floor coverings · tufted (pounds)"] == 12.0

    def test_transform_data_sums_duplicate_cells(self):
        """A duplicated series cell within a row sums."""
        records = [
            {
                "table": "raw_fiber_equivalent_textile_manufactures",
                "year": 1989,
                "period": None,
                "geography": None,
                "measure": None,
                "trade_category": "imports",
                "textile_group": None,
                "item": None,
                "unit": "pounds",
                "series": "cotton",
                "value": 40.0,
            },
            {
                "table": "raw_fiber_equivalent_textile_manufactures",
                "year": 1989,
                "period": None,
                "geography": None,
                "measure": None,
                "trade_category": "imports",
                "textile_group": None,
                "item": None,
                "unit": "pounds",
                "series": "cotton",
                "value": 60.0,
            },
        ]
        query = CottonWoolAndTextileDataFetcher.transform_query(
            {"table": "raw_fiber_equivalent_textile_manufactures"}
        )
        data = CottonWoolAndTextileDataFetcher.transform_data(query, records)
        assert data[0].model_dump()["imports · cotton (pounds)"] == 100.0

    def test_transform_data_years_pivot_chronological(self):
        """A years-pivot table keeps the country in the period, years in columns."""
        records = parse_table(RFE_ORIGIN_CSV, "rfe_cotton_textile_imports_by_origin")
        query = CottonWoolAndTextileDataFetcher.transform_query(
            {"table": "rfe_cotton_textile_imports_by_origin"}
        )
        data = CottonWoolAndTextileDataFetcher.transform_data(query, records)
        world = next(row for row in data if row.period == "World")
        dumped = world.model_dump()
        year_keys = [key for key in dumped if key.isdigit()]
        assert year_keys == ["2022", "2023"]
        assert dumped["2022"] == 100.0
        assert dumped["2023"] == 110.0
        canada = next(row for row in data if row.period == "Canada")
        assert canada.model_dump()["2022"] == 20.0
        assert canada.model_dump()["2023"] is None

    def test_transform_data_years_pivot_row_order(self):
        """Years-pivot rows keep the source order of the country rows."""
        records = parse_table(RFE_ORIGIN_CSV, "rfe_cotton_textile_imports_by_origin")
        query = CottonWoolAndTextileDataFetcher.transform_query(
            {"table": "rfe_cotton_textile_imports_by_origin"}
        )
        data = CottonWoolAndTextileDataFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["World", "Canada"]

    def test_data_model_keeps_dynamic_columns_and_precision(self):
        """The Data model preserves dynamic columns at full precision."""
        row = CottonWoolAndTextileDataData.model_validate(
            {
                "period": "2024 Jan",
                "Apparel · tops (pounds)": 232495.9736,
            }
        )
        assert row.model_dump()["Apparel · tops (pounds)"] == 232495.9736

    def test_data_model_only_period_is_static(self):
        """The only static served field is the pinned period label."""
        assert set(CottonWoolAndTextileDataData.model_fields) == {"period"}

    def test_row_dim_fields_exposed(self):
        """The row-dimension field tuple matches the parser's dims."""
        assert ROW_DIM_FIELDS == (
            "geography",
            "measure",
            "trade_category",
            "textile_group",
            "item",
        )

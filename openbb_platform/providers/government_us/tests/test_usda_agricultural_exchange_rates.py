"""Tests for the USDA ERS agricultural exchange rates utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import to_snake_case

from openbb_government_us.usda.models.agricultural_exchange_rates import (
    DEFAULT_TABLE,
    AgriculturalExchangeRatesData,
    AgriculturalExchangeRatesFetcher,
    AgriculturalExchangeRatesQueryParams,
)
from openbb_government_us.usda.utils import ers_agricultural_exchange_rates
from openbb_government_us.usda.utils.ers_agricultural_exchange_rates import (
    BILATERAL_REGIONS,
    EXCHANGE_RATE_FILES,
    INDEX_WEIGHTS,
    MONTH_ORDER,
    build_url,
    media_path,
    parse_table,
)

MARKETS = "U.S. markets (U.S. export weights)"
COMPETITORS = "U.S. competitors (country export weights)"

INDEX_ANNUAL_CSV = (
    "Commodity,Weights,Year,Value\n"
    f"Corn,{MARKETS},2024,121.2180\n"
    f"Corn,{MARKETS},2025,122.1123\n"
    f"Cotton,{MARKETS},2024,129.1817\n"
    f"Corn,{COMPETITORS},2024,100.0\n"
    f"Corn,{MARKETS},,999.0\n"
    f"Corn,{MARKETS},abcd,999.0\n"
    f"Corn,{MARKETS},2026,\n"
)

INDEX_MONTHLY_CSV = (
    "Commodity,Weights,Month,Year,Value\n"
    f"Corn,{MARKETS},January,2025,120.0\n"
    f"Corn,{MARKETS},December,2025,116.0\n"
    f"Corn,{MARKETS},June,2025,118.0\n"
)

BILATERAL_ANNUAL_CSV = (
    "Region,Country,Countrycode,Year,Value\n"
    "North America,Canada,(1220),2024,1.426067948\n"
    "North America,Mexico,(2010),2024,15.68008804\n"
    "Europe,France,(4273),2024,1.021022081\n"
    "North America,Canada,(1220),2025,1.464753151\n"
)

BILATERAL_MONTHLY_CSV = (
    "Region,Country,Countrycode,Month,Year,Value\n"
    "North America,Canada,(1220),January,2025,1.42\n"
    "North America,Canada,(1220),December,2025,1.46\n"
)


def _column_def_fields(model) -> list[str]:
    """Replicate the widget generator's columnsDefs field derivation."""
    props = model.model_json_schema(by_alias=True).get("properties", {})
    fields: list[str] = []
    for key, prop in props.items():
        if prop.get("x-widget_config", {}).get("exclude"):
            continue
        fields.append(to_snake_case(key))
    return fields


class TestErsAgriculturalExchangeRatesUtils:
    """Tests for the ers_agricultural_exchange_rates utils module."""

    def test_catalog_contents(self):
        """The catalog holds the six dated tables with kind and frequency."""
        assert len(EXCHANGE_RATE_FILES) == 6
        assert set(EXCHANGE_RATE_FILES) == {
            "real_index_annual",
            "real_index_monthly",
            "real_bilateral_annual",
            "real_bilateral_monthly",
            "nominal_bilateral_annual",
            "nominal_bilateral_monthly",
        }
        medias = [config["media"] for config in EXCHANGE_RATE_FILES.values()]
        assert len(set(medias)) == 6
        for config in EXCHANGE_RATE_FILES.values():
            assert config["media"].startswith("/media/")
            assert config["media"].endswith(".csv")
            assert config["kind"] in ("index", "bilateral")
            assert config["frequency"] in ("annual", "monthly")
            assert config["label"]
        assert EXCHANGE_RATE_FILES["real_index_annual"]["kind"] == "index"
        assert EXCHANGE_RATE_FILES["nominal_bilateral_monthly"]["kind"] == "bilateral"
        assert EXCHANGE_RATE_FILES["real_index_monthly"]["frequency"] == "monthly"

    def test_static_dimension_sets(self):
        """The index weight schemes and bilateral regions are fixed sets."""
        assert len(INDEX_WEIGHTS) == 3
        assert MARKETS in INDEX_WEIGHTS
        assert len(BILATERAL_REGIONS) == 12
        assert "North America" in BILATERAL_REGIONS
        assert list(MONTH_ORDER.values()) == list(range(1, 13))
        assert MONTH_ORDER["January"] == 1
        assert MONTH_ORDER["December"] == 12

    def test_media_path_and_build_url(self):
        """media_path and build_url resolve a table's CSV location."""
        assert media_path("real_bilateral_annual") == (
            "/media/5457/annual-real-exchange-rates-local-currency-per-usd.csv"
        )
        assert build_url("real_bilateral_annual") == (
            "https://www.ers.usda.gov/media/5457/"
            "annual-real-exchange-rates-local-currency-per-usd.csv"
        )

    def test_parse_index_annual(self):
        """Index annual rows parse with weights, commodity series, and no month."""
        records = parse_table(INDEX_ANNUAL_CSV, "real_index_annual")
        assert len(records) == 4
        assert records[0] == {
            "table": "real_index_annual",
            "kind": "index",
            "year": 2024,
            "month": None,
            "month_order": None,
            "value": 121.218,
            "weights": MARKETS,
            "region": None,
            "series": "Corn",
        }
        assert records[2]["series"] == "Cotton"
        assert records[3]["weights"] == COMPETITORS

    def test_parse_index_annual_skips_blank_and_nonnumeric(self):
        """Blank years, non-numeric years, and blank values are dropped."""
        records = parse_table(INDEX_ANNUAL_CSV, "real_index_annual")
        assert {record["year"] for record in records} == {2024, 2025}
        assert 999.0 not in {record["value"] for record in records}

    def test_parse_index_monthly_month_order(self):
        """Index monthly rows carry the month label and calendar order."""
        records = parse_table(INDEX_MONTHLY_CSV, "real_index_monthly")
        assert len(records) == 3
        by_month = {record["month"]: record["month_order"] for record in records}
        assert by_month == {"January": 1, "December": 12, "June": 6}
        assert all(record["kind"] == "index" for record in records)

    def test_parse_bilateral_annual(self):
        """Bilateral annual rows parse with region and country series."""
        records = parse_table(BILATERAL_ANNUAL_CSV, "real_bilateral_annual")
        assert len(records) == 4
        assert records[0] == {
            "table": "real_bilateral_annual",
            "kind": "bilateral",
            "year": 2024,
            "month": None,
            "month_order": None,
            "value": 1.426067948,
            "weights": None,
            "region": "North America",
            "series": "Canada",
        }
        assert records[2]["region"] == "Europe"
        assert records[2]["series"] == "France"

    def test_parse_bilateral_monthly(self):
        """Bilateral monthly rows carry region, country, month, and order."""
        records = parse_table(BILATERAL_MONTHLY_CSV, "nominal_bilateral_monthly")
        assert {record["month"] for record in records} == {"January", "December"}
        assert records[0]["region"] == "North America"
        assert records[0]["series"] == "Canada"
        assert records[0]["weights"] is None

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches through the ERS cache client and parses."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return INDEX_ANNUAL_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_agricultural_exchange_rates.afetch_table("real_index_annual")
        )
        assert calls == [
            (
                media_path("real_index_annual"),
                ers_agricultural_exchange_rates.PRODUCT_PAGE,
            )
        ]
        assert len(records) == 4
        assert records[0]["series"] == "Corn"


class TestAgriculturalExchangeRates:
    """Tests for the AgriculturalExchangeRates model."""

    def test_transform_query_default_table(self):
        """transform_query defaults the table and keeps the year filters."""
        query = AgriculturalExchangeRatesFetcher.transform_query({"start_year": 2000})
        assert isinstance(query, AgriculturalExchangeRatesQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.start_year == 2000

    def test_table_blank_list_and_strip(self):
        """Blank tables fall back to the default, lists take the first, strips."""
        assert AgriculturalExchangeRatesQueryParams(table="").table == DEFAULT_TABLE
        assert AgriculturalExchangeRatesQueryParams(table=None).table == DEFAULT_TABLE
        assert (
            AgriculturalExchangeRatesQueryParams(table=["real_bilateral_annual"]).table
            == "real_bilateral_annual"
        )
        assert (
            AgriculturalExchangeRatesQueryParams(table="  real_index_monthly  ").table
            == "real_index_monthly"
        )

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            AgriculturalExchangeRatesQueryParams(table="bogus")

    def test_optional_filters_normalize(self):
        """Blank weights and region normalize to None; lists take the first."""
        query = AgriculturalExchangeRatesQueryParams(weights="  ", region="")
        assert query.weights is None
        assert query.region is None
        query = AgriculturalExchangeRatesQueryParams(
            table="real_bilateral_annual", region=["North America"]
        )
        assert query.region == "North America"

    def test_invalid_weights_on_index_raises(self):
        """An invalid weight scheme on an index table raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid weight scheme: bogus"):
            AgriculturalExchangeRatesQueryParams(
                table="real_index_annual", weights="bogus"
            )

    def test_invalid_region_on_bilateral_raises(self):
        """An invalid region on a bilateral table raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid region: Mars"):
            AgriculturalExchangeRatesQueryParams(
                table="real_bilateral_annual", region="Mars"
            )

    def test_inapplicable_filters_ignored(self):
        """A stale weights on a bilateral table, or region on index, is tolerated."""
        query = AgriculturalExchangeRatesQueryParams(
            table="real_bilateral_annual", weights="bogus"
        )
        assert query.weights == "bogus"
        query = AgriculturalExchangeRatesQueryParams(
            table="real_index_annual", region="Mars"
        )
        assert query.region == "Mars"

    def test_valid_weights_on_index(self):
        """A valid weight scheme on an index table validates cleanly."""
        query = AgriculturalExchangeRatesQueryParams(
            table="real_index_annual", weights=MARKETS
        )
        assert query.weights == MARKETS

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(
            ers_agricultural_exchange_rates, "afetch_table", fake_afetch_table
        )
        query = AgriculturalExchangeRatesFetcher.transform_query(
            {"table": "real_bilateral_annual"}
        )
        records = asyncio.run(
            AgriculturalExchangeRatesFetcher.aextract_data(query, None)
        )
        assert fetched == ["real_bilateral_annual"]
        assert records == [{"table": "real_bilateral_annual"}]

    def test_transform_data_stacks_all_schemes_when_weights_none(self):
        """weights=None stacks every scheme, folding it into the period label."""
        records = parse_table(INDEX_ANNUAL_CSV, "real_index_annual")
        query = AgriculturalExchangeRatesFetcher.transform_query({"weights": None})
        data = AgriculturalExchangeRatesFetcher.transform_data(query, records)
        dumped = [row.model_dump(by_alias=True) for row in data]
        assert dumped[0]["period"] == f"{COMPETITORS} — 2024"
        assert dumped[0]["Corn"] == 100.0
        markets_2024 = next(
            row for row in dumped if row["period"] == f"{MARKETS} — 2024"
        )
        assert markets_2024["Corn"] == 121.218
        assert markets_2024["Cotton"] == 129.1817

    def test_transform_data_default_keeps_single_weight_scheme(self):
        """The default query keeps one scheme, so the period is the bare year."""
        records = parse_table(INDEX_ANNUAL_CSV, "real_index_annual")
        query = AgriculturalExchangeRatesFetcher.transform_query({})
        assert query.weights == MARKETS
        data = AgriculturalExchangeRatesFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2025", "2024"]

    def test_transform_data_weights_filter(self):
        """The weights filter keeps only the selected scheme's rows."""
        records = parse_table(INDEX_ANNUAL_CSV, "real_index_annual")
        query = AgriculturalExchangeRatesFetcher.transform_query({"weights": MARKETS})
        data = AgriculturalExchangeRatesFetcher.transform_data(query, records)
        assert {row.period for row in data} == {"2024", "2025"}

    def test_transform_data_pivots_countries_into_columns(self):
        """Each country becomes a column for a bilateral table, newest first."""
        records = parse_table(BILATERAL_ANNUAL_CSV, "real_bilateral_annual")
        query = AgriculturalExchangeRatesFetcher.transform_query(
            {"table": "real_bilateral_annual"}
        )
        data = AgriculturalExchangeRatesFetcher.transform_data(query, records)
        dumped = [row.model_dump(by_alias=True) for row in data]
        assert [row["period"] for row in dumped] == ["2025", "2024"]
        assert dumped[1]["Canada"] == 1.426067948
        assert dumped[1]["Mexico"] == 15.68008804
        assert dumped[1]["France"] == 1.021022081

    def test_transform_data_region_filter(self):
        """The region filter drops partner countries outside the region."""
        records = parse_table(BILATERAL_ANNUAL_CSV, "real_bilateral_annual")
        query = AgriculturalExchangeRatesFetcher.transform_query(
            {"table": "real_bilateral_annual", "region": "North America"}
        )
        data = AgriculturalExchangeRatesFetcher.transform_data(query, records)
        row_2024 = next(
            row.model_dump(by_alias=True) for row in data if row.period == "2024"
        )
        assert "Canada" in row_2024
        assert "Mexico" in row_2024
        assert "France" not in row_2024

    def test_transform_data_monthly_folds_month_into_period(self):
        """Monthly rows carry the year and month, newest month first."""
        records = parse_table(INDEX_MONTHLY_CSV, "real_index_monthly")
        query = AgriculturalExchangeRatesFetcher.transform_query(
            {"table": "real_index_monthly"}
        )
        data = AgriculturalExchangeRatesFetcher.transform_data(query, records)
        assert [row.period for row in data] == [
            "2025 December",
            "2025 June",
            "2025 January",
        ]

    def test_transform_data_filters_years(self):
        """start_year and end_year filter the pivoted rows on the year."""
        records = parse_table(INDEX_ANNUAL_CSV, "real_index_annual")
        start = AgriculturalExchangeRatesFetcher.transform_data(
            AgriculturalExchangeRatesFetcher.transform_query({"start_year": 2025}),
            records,
        )
        assert {row.period for row in start} == {"2025"}
        end = AgriculturalExchangeRatesFetcher.transform_data(
            AgriculturalExchangeRatesFetcher.transform_query({"end_year": 2024}),
            records,
        )
        assert {row.period for row in end} == {"2024"}

    def test_transform_data_empty_raises(self):
        """No records surviving the filters raises EmptyDataError."""
        records = parse_table(INDEX_ANNUAL_CSV, "real_index_annual")
        query = AgriculturalExchangeRatesFetcher.transform_query({"start_year": 2100})
        with pytest.raises(EmptyDataError, match="No records match"):
            AgriculturalExchangeRatesFetcher.transform_data(query, records)

    def test_transform_data_excludes_sort_keys(self):
        """Internal sort keys never leak into the validated records."""
        records = parse_table(INDEX_ANNUAL_CSV, "real_index_annual")
        query = AgriculturalExchangeRatesFetcher.transform_query({})
        data = AgriculturalExchangeRatesFetcher.transform_data(query, records)
        dumped = data[0].model_dump(by_alias=True)
        assert not any(key.startswith("_") for key in dumped)

    def test_data_model_preserves_dynamic_columns_and_precision(self):
        """Dynamic value columns survive at full precision as extras."""
        row = AgriculturalExchangeRatesData.model_validate(
            {"period": "2026", "Japan": 188.9905243}
        )
        assert row.model_dump(by_alias=True)["Japan"] == 188.9905243


class TestAgriculturalExchangeRatesWidget:
    """Tests for the widget configuration and columnsDefs binding."""

    def test_whole_widget_config(self):
        """The model carries the whole-widget category, subcategory, and source."""
        config = AgriculturalExchangeRatesData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]
        assert config["$.name"] == "USDA ERS Agricultural Exchange Rates"

    def test_period_is_the_only_static_field(self):
        """The pinned period label is the only fixed served column."""
        assert set(AgriculturalExchangeRatesData.model_fields) == {"period"}
        props = AgriculturalExchangeRatesData.model_json_schema(by_alias=True)[
            "properties"
        ]
        assert props["period"]["x-widget_config"]["pinned"] == "left"

    def test_param_options_are_single_select(self):
        """Each choice param is a real single-select with labeled options."""
        extra = AgriculturalExchangeRatesQueryParams.__json_schema_extra__
        for name in ("table", "weights", "region"):
            config = extra[name]["x-widget_config"]
            assert config["multiSelect"] is False
            assert config["multiple"] is False
            assert config["label"]
            assert config["options"]
        assert len(extra["table"]["x-widget_config"]["options"]) == 6
        assert len(extra["weights"]["x-widget_config"]["options"]) == 3
        assert len(extra["region"]["x-widget_config"]["options"]) == 12

    def test_columns_defs_bind_to_served_keys_index(self):
        """Every declared columnDef field is a served key for an index row."""
        records = parse_table(INDEX_ANNUAL_CSV, "real_index_annual")
        query = AgriculturalExchangeRatesFetcher.transform_query({"weights": MARKETS})
        data = AgriculturalExchangeRatesFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        for field in _column_def_fields(AgriculturalExchangeRatesData):
            assert field in served
        assert served >= {"period", "Corn"}

    def test_columns_defs_bind_to_served_keys_bilateral(self):
        """Every declared columnDef field is a served key for a bilateral row."""
        records = parse_table(BILATERAL_ANNUAL_CSV, "real_bilateral_annual")
        query = AgriculturalExchangeRatesFetcher.transform_query(
            {"table": "real_bilateral_annual"}
        )
        data = AgriculturalExchangeRatesFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        for field in _column_def_fields(AgriculturalExchangeRatesData):
            assert field in served
        assert served >= {"period", "Canada"}

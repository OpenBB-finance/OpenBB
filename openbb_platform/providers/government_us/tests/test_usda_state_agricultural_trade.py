"""Tests for the USDA ERS state agricultural trade utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.state_agricultural_trade import (
    StateAgriculturalTradeData,
    StateAgriculturalTradeFetcher,
    StateAgriculturalTradeQueryParams,
)
from openbb_government_us.usda.utils import ers_state_agricultural_trade
from openbb_government_us.usda.utils.ers_state_agricultural_trade import (
    ALL_DATA_CSV,
    COMMODITIES,
    DATASET_A_STATE_NAMES,
    DATASET_B_STATE_NAMES,
    DEFAULT_COMMODITY,
    DEFAULT_STATE,
    DEFAULT_TABLE,
    PRODUCT_PAGE,
    STATE_AG_TRADE_FILES,
    STATE_CODE_TO_NAME,
    TABLE_LABELS,
    TOP_EXPORTS_CSV,
    TOP_IMPORTS_CSV,
    allowed_state_names,
    commodity_options,
    parse_dataset_a,
    parse_dataset_b,
    parse_value,
    state_options,
)

FIXTURE_A = (
    "Commodity,State,Units,Year,Value\n"
    "Total agricultural exports,California,Million dollars,2000,6800.4433\n"
    "Total agricultural exports,California,Million dollars,2012,19005.118\n"
    "Total agricultural exports,California,Million dollars,2024,26345.5221\n"
    "Tree nuts,California,Million dollars,2000,894.1047\n"
    "Tree nuts,California,Million dollars,2012,5968.6765\n"
    "Tree nuts,California,Million dollars,2024,9153.3596\n"
    "Cotton,California,Million dollars,2000,379.8393\n"
    "Cotton,California,Million dollars,2012,\n"
    "Cotton,California,Million dollars,2024,249.5516\n"
    "Other commodity,California,Million dollars,2024,1.5\n"
    "Total agricultural exports,Iowa,Million dollars,2000,3479.41\n"
    "Total agricultural exports,Iowa,Million dollars,2024,13673.33\n"
    "Total agricultural exports,United States,Million dollars,2000,55010.669\n"
    "Total agricultural exports,United States,Million dollars,2024,168084.576\n"
    "Tree nuts,United States,Million dollars,2024,9200.0\n"
    "Cotton,California,Million dollars,badyear,9.9\n"
)

FIXTURE_B = (
    "State,Fiscal year,Country,Commodity name,Dollar value,Fiscal quarter,"
    "Trade type,Fiscal quarter description\n"
    "CA,2019,World,Tree nuts,8030094410,0,Exports,Fiscal year total\n"
    "CA,2019,World,Dairy products,1659409767,0,Exports,Fiscal year total\n"
    "CA,2024,World,Tree nuts,8514278662,0,Exports,Fiscal year total\n"
    "CA,2024,World,Dairy products,2182484826,0,Exports,Fiscal year total\n"
    "CA,2019,Canada,Tree nuts,100,0,Exports,Fiscal year total\n"
    "CA,2019,World,Tree nuts,2000,1,Exports,Fiscal quarter 1\n"
    "CA,notayear,World,Tree nuts,3000,0,Exports,Fiscal year total\n"
    "US,2019,World,Tree nuts,9000000000,0,Exports,Fiscal year total\n"
    "PR,2019,World,Coffee,5000,0,Exports,Fiscal year total\n"
)


class TestErsStateAgriculturalTradeUtils:
    """Tests for the ers_state_agricultural_trade utils module."""

    def test_catalog(self):
        """The catalog maps every table to its media path and product page."""
        assert set(STATE_AG_TRADE_FILES) == set(TABLE_LABELS)
        assert STATE_AG_TRADE_FILES["exports_by_commodity"] == (
            ALL_DATA_CSV,
            PRODUCT_PAGE,
        )
        assert STATE_AG_TRADE_FILES["exports_by_state"] == (ALL_DATA_CSV, PRODUCT_PAGE)
        assert STATE_AG_TRADE_FILES["top_exports"] == (TOP_EXPORTS_CSV, PRODUCT_PAGE)
        assert STATE_AG_TRADE_FILES["top_imports"] == (TOP_IMPORTS_CSV, PRODUCT_PAGE)
        assert ALL_DATA_CSV.startswith("/media/5420/")
        assert TOP_EXPORTS_CSV.startswith("/media/5422/")
        assert TOP_IMPORTS_CSV.startswith("/media/5424/")

    def test_state_maps(self):
        """The code-to-name map covers 54 codes and the name map inverts it."""
        assert len(STATE_CODE_TO_NAME) == 54
        assert STATE_CODE_TO_NAME["US"] == "United States"
        assert STATE_CODE_TO_NAME["CA"] == "California"
        assert STATE_CODE_TO_NAME["PR"] == "Puerto Rico"
        assert STATE_CODE_TO_NAME["DC"] == "District of Columbia"
        assert STATE_CODE_TO_NAME["VI"] == "Virgin Islands"

    def test_dataset_state_orderings(self):
        """State orderings lead with the national total, then run alphabetically."""
        assert DATASET_A_STATE_NAMES[0] == "United States"
        assert len(DATASET_A_STATE_NAMES) == 51
        assert list(DATASET_A_STATE_NAMES[1:]) == sorted(DATASET_A_STATE_NAMES[1:])
        assert "Puerto Rico" not in DATASET_A_STATE_NAMES
        assert DATASET_B_STATE_NAMES[0] == "United States"
        assert len(DATASET_B_STATE_NAMES) == 54
        assert "Puerto Rico" in DATASET_B_STATE_NAMES

    def test_allowed_state_names_by_table(self):
        """The all-data tables use 51 states, the top tables use 54."""
        assert allowed_state_names("exports_by_commodity") == DATASET_A_STATE_NAMES
        assert allowed_state_names("exports_by_state") == DATASET_A_STATE_NAMES
        assert allowed_state_names("top_exports") == DATASET_B_STATE_NAMES
        assert allowed_state_names("top_imports") == DATASET_B_STATE_NAMES

    def test_state_options_labels(self):
        """State options carry the full name as both label and value."""
        options = state_options("exports_by_commodity")
        assert options[0] == {"label": "United States", "value": "United States"}
        assert {opt["value"] for opt in options} == set(DATASET_A_STATE_NAMES)
        top = state_options("top_exports")
        assert any(opt["value"] == "Puerto Rico" for opt in top)

    def test_commodity_options(self):
        """Commodity options list every commodity as label and value."""
        options = commodity_options()
        assert len(options) == 27
        assert options[0] == {
            "label": "Total agricultural exports",
            "value": "Total agricultural exports",
        }
        assert {opt["value"] for opt in options} == set(COMMODITIES)

    def test_parse_value(self):
        """Numeric cells parse to floats; blank and non-numeric cells to None."""
        assert parse_value("6800.4433") == 6800.4433
        assert parse_value("8030094410") == 8030094410.0
        assert parse_value("") is None
        assert parse_value(None) is None
        assert parse_value("n/a") is None

    def test_parse_dataset_a(self):
        """The all-data parser keeps full names, ints, and floats, skipping bad years."""
        records = parse_dataset_a(FIXTURE_A)
        years = {record["year"] for record in records}
        assert "badyear" not in {str(record["year"]) for record in records}
        assert years == {2000, 2012, 2024}
        first = records[0]
        assert first == {
            "commodity": "Total agricultural exports",
            "state": "California",
            "year": 2000,
            "unit": "Million dollars",
            "value": 6800.4433,
        }
        blank = next(
            record
            for record in records
            if record["commodity"] == "Cotton" and record["year"] == 2012
        )
        assert blank["value"] is None

    def test_parse_dataset_b(self):
        """The top parser keeps only World, fiscal-year-total, numeric-year rows."""
        records = parse_dataset_b(FIXTURE_B)
        assert len(records) == 6
        assert all(record["value"] is not None for record in records)
        ca = [record for record in records if record["state"] == "CA"]
        assert {record["year"] for record in ca} == {2019, 2024}
        assert {record["commodity"] for record in ca} == {"Tree nuts", "Dairy products"}
        tree_2019 = next(
            record
            for record in ca
            if record["commodity"] == "Tree nuts" and record["year"] == 2019
        )
        assert tree_2019["value"] == 8030094410.0
        assert any(record["state"] == "PR" for record in records)

    def test_afetch_table_dataset_a(self, monkeypatch):
        """afetch_table fetches and parses the all-data CSV for the A tables."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return FIXTURE_A.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_state_agricultural_trade.afetch_table("exports_by_commodity")
        )
        assert calls == [(ALL_DATA_CSV, PRODUCT_PAGE)]
        assert any(record["state"] == "United States" for record in records)

    def test_afetch_table_dataset_b(self, monkeypatch):
        """afetch_table fetches and parses the top-import CSV for the B tables."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return FIXTURE_B.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ers_state_agricultural_trade.afetch_table("top_imports"))
        assert calls == [(TOP_IMPORTS_CSV, PRODUCT_PAGE)]
        assert all(record["commodity"] for record in records)


class TestStateAgriculturalTrade:
    """Tests for the StateAgriculturalTrade model."""

    def _records_a(self):
        """Parse the calendar-year fixture into long records."""
        return parse_dataset_a(FIXTURE_A)

    def _records_b(self):
        """Parse the fiscal-year fixture into long records."""
        return parse_dataset_b(FIXTURE_B)

    def test_transform_query_defaults(self):
        """transform_query applies the table, state, and commodity defaults."""
        query = StateAgriculturalTradeFetcher.transform_query({})
        assert isinstance(query, StateAgriculturalTradeQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.state == DEFAULT_STATE
        assert query.commodity == DEFAULT_COMMODITY
        assert query.start_year is None
        assert query.end_year is None

    def test_blank_values_fall_back_to_defaults(self):
        """Blank table, state, and commodity normalize to their defaults."""
        query = StateAgriculturalTradeQueryParams(table="", state="", commodity="")
        assert query.table == DEFAULT_TABLE
        assert query.state == DEFAULT_STATE
        assert query.commodity == DEFAULT_COMMODITY

    def test_invalid_table_state_commodity_raise(self):
        """Unknown table, state, or commodity raise OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            StateAgriculturalTradeQueryParams(table="bogus")
        with pytest.raises(OpenBBError, match="Invalid state: Atlantis"):
            StateAgriculturalTradeQueryParams(state="Atlantis")
        with pytest.raises(OpenBBError, match="Invalid commodity: bogus"):
            StateAgriculturalTradeQueryParams(commodity="bogus")

    def test_state_accepts_name_and_code(self):
        """The state param accepts a full name or a two-letter code."""
        assert (
            StateAgriculturalTradeQueryParams(state="California").state == "California"
        )
        assert StateAgriculturalTradeQueryParams(state="ca").state == "California"
        assert StateAgriculturalTradeQueryParams(state=["TX"]).state == "Texas"

    def test_state_for_table_validation(self):
        """A fiscal-year-only state is rejected for a calendar-year table."""
        assert (
            StateAgriculturalTradeQueryParams(
                table="top_exports", state="Puerto Rico"
            ).state
            == "Puerto Rico"
        )
        with pytest.raises(OpenBBError, match="Invalid state 'Puerto Rico'"):
            StateAgriculturalTradeQueryParams(
                table="exports_by_commodity", state="Puerto Rico"
            )

    def test_exports_by_state_ignores_state(self):
        """The exports-by-state table does not enforce the state selection."""
        query = StateAgriculturalTradeQueryParams(
            table="exports_by_state", state="Puerto Rico"
        )
        assert query.table == "exports_by_state"

    def test_aextract_data(self, monkeypatch):
        """aextract_data returns the selected table's parsed records."""

        async def fake_afetch_table(table):
            return parse_dataset_a(FIXTURE_A)

        monkeypatch.setattr(
            ers_state_agricultural_trade, "afetch_table", fake_afetch_table
        )
        query = StateAgriculturalTradeFetcher.transform_query({})
        records = asyncio.run(StateAgriculturalTradeFetcher.aextract_data(query, None))
        assert any(record["commodity"] == "Tree nuts" for record in records)

    def test_exports_by_commodity_pivot(self):
        """The commodity table spreads a state's commodities into columns by year."""
        query = StateAgriculturalTradeFetcher.transform_query({"state": "California"})
        data = StateAgriculturalTradeFetcher.transform_data(query, self._records_a())
        assert [row.year for row in data] == [2000, 2012, 2024]
        first = data[0].model_dump(by_alias=True)
        assert list(first)[:4] == ["year", "state", "commodity", "unit"]
        assert list(first)[4:] == [
            "Total agricultural exports",
            "Cotton",
            "Tree nuts",
            "Other commodity",
        ]
        assert first["Total agricultural exports"] == 6800.4433
        assert first["Cotton"] == 379.8393
        assert first["Tree nuts"] == 894.1047
        assert first["Other commodity"] is None
        assert first["state"] == "California"
        assert first["commodity"] is None
        assert first["unit"] == "Million dollars"

    def test_exports_by_commodity_blank_value_is_none(self):
        """A blank source value surfaces as None on the pivoted row."""
        query = StateAgriculturalTradeFetcher.transform_query({"state": "California"})
        data = StateAgriculturalTradeFetcher.transform_data(query, self._records_a())
        row_2012 = next(row for row in data if row.year == 2012)
        assert row_2012.model_dump(by_alias=True)["Cotton"] is None

    def test_exports_by_state_pivot(self):
        """The state table spreads states into columns, national total first."""
        query = StateAgriculturalTradeFetcher.transform_query(
            {"table": "exports_by_state", "commodity": "Total agricultural exports"}
        )
        data = StateAgriculturalTradeFetcher.transform_data(query, self._records_a())
        assert [row.year for row in data] == [2000, 2012, 2024]
        first = data[0].model_dump(by_alias=True)
        assert list(first)[4:] == ["United States", "California", "Iowa"]
        assert first["United States"] == 55010.669
        assert first["California"] == 6800.4433
        assert first["Iowa"] == 3479.41
        assert first["commodity"] == "Total agricultural exports"
        assert first["state"] is None

    def test_top_exports_pivot(self):
        """The top-export table spreads a state's commodities by fiscal year."""
        query = StateAgriculturalTradeFetcher.transform_query(
            {"table": "top_exports", "state": "California"}
        )
        data = StateAgriculturalTradeFetcher.transform_data(query, self._records_b())
        assert [row.year for row in data] == [2019, 2024]
        first = data[0].model_dump(by_alias=True)
        assert list(first)[4:] == ["Dairy products", "Tree nuts"]
        assert first["Tree nuts"] == 8030094410.0
        assert first["Dairy products"] == 1659409767.0
        assert first["state"] == "California"
        assert first["unit"] == "Dollars"

    def test_top_imports_pivot_with_code_state(self):
        """The top-import table resolves a code state and pivots its commodities."""
        query = StateAgriculturalTradeFetcher.transform_query(
            {"table": "top_imports", "state": "PR"}
        )
        data = StateAgriculturalTradeFetcher.transform_data(query, self._records_b())
        assert [row.year for row in data] == [2019]
        row = data[0].model_dump(by_alias=True)
        assert row["Coffee"] == 5000.0
        assert row["state"] == "Puerto Rico"
        assert row["unit"] == "Dollars"

    def test_year_filters(self):
        """start_year and end_year bound the emitted year rows."""
        start = StateAgriculturalTradeFetcher.transform_data(
            StateAgriculturalTradeFetcher.transform_query(
                {"state": "California", "start_year": 2012}
            ),
            self._records_a(),
        )
        assert [row.year for row in start] == [2012, 2024]
        end = StateAgriculturalTradeFetcher.transform_data(
            StateAgriculturalTradeFetcher.transform_query(
                {"state": "California", "end_year": 2000}
            ),
            self._records_a(),
        )
        assert [row.year for row in end] == [2000]

    def test_empty_slice_raises(self):
        """A filter that matches no rows raises EmptyDataError."""
        query = StateAgriculturalTradeFetcher.transform_query(
            {"state": "California", "start_year": 3000}
        )
        with pytest.raises(EmptyDataError):
            StateAgriculturalTradeFetcher.transform_data(query, self._records_a())

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served record key."""
        declared = set()
        for name, field in StateAgriculturalTradeData.model_fields.items():
            alias = field.serialization_alias or name
            extra = field.json_schema_extra
            config = extra.get("x-widget_config", {}) if isinstance(extra, dict) else {}
            if config.get("exclude"):
                continue
            declared.add(to_snake(alias))
        query = StateAgriculturalTradeFetcher.transform_query({"state": "California"})
        data = StateAgriculturalTradeFetcher.transform_data(query, self._records_a())
        served = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        assert declared <= served

    def test_dynamic_columns_are_not_constant(self):
        """Served keys without a column definition vary across the rows."""
        declared = set()
        for name, field in StateAgriculturalTradeData.model_fields.items():
            alias = field.serialization_alias or name
            declared.add(to_snake(alias))
        query = StateAgriculturalTradeFetcher.transform_query({"state": "California"})
        data = StateAgriculturalTradeFetcher.transform_data(query, self._records_a())
        rows = [row.model_dump(by_alias=True) for row in data]
        served = set().union(*rows)
        for key in served - declared:
            values = [row.get(key) for row in rows]
            assert len(set(values)) > 1

    def test_param_scoping_options(self):
        """Choice params are single-select with real labels and options."""
        extra = StateAgriculturalTradeQueryParams.__json_schema_extra__
        table = extra["table"]["x-widget_config"]
        assert table["label"] == "Table" and table["multiSelect"] is False
        assert {opt["value"] for opt in table["options"]} == set(TABLE_LABELS)
        state = extra["state"]["x-widget_config"]
        assert state["type"] == "endpoint"
        assert state["optionsEndpoint"].endswith("/usda/state_ag_trade_states")
        assert state["optionsParams"] == {"table": "$table"}
        assert state["value"] == DEFAULT_STATE
        commodity = extra["commodity"]["x-widget_config"]
        assert commodity["multiSelect"] is False
        assert commodity["value"] == DEFAULT_COMMODITY
        assert {opt["value"] for opt in commodity["options"]} == set(COMMODITIES)

    def test_widget_config_and_column_headers(self):
        """The whole-widget config and per-field headers are populated."""
        widget = StateAgriculturalTradeData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert widget["$.name"] == "USDA ERS State Agricultural Trade"
        assert widget["$.category"] == "Economy"
        assert widget["$.subCategory"] == "Agriculture"
        assert widget["$.source"] == ["USDA", "ERS"]
        fields = StateAgriculturalTradeData.model_fields
        assert fields["year"].json_schema_extra["x-widget_config"]["pinned"] == "left"
        assert fields["state"].json_schema_extra["x-widget_config"]["hide"] is True
        assert fields["commodity"].json_schema_extra["x-widget_config"]["hide"] is True
        assert fields["unit"].json_schema_extra["x-widget_config"]["hide"] is True

    def test_null_token_mixin_coerces_placeholder(self):
        """The Data model coerces placeholder tokens to None but keeps columns."""
        row = StateAgriculturalTradeData.model_validate(
            {"year": 2024, "state": "--", "Tree nuts": 9153.3596}
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["state"] is None
        assert dumped["Tree nuts"] == 9153.3596

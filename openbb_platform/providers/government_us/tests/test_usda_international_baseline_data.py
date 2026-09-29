"""Tests for the USDA ERS international baseline data utils and model."""

import asyncio
import zipfile
from io import BytesIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.international_baseline_data import (
    InternationalBaselineDataData,
    InternationalBaselineDataFetcher,
    InternationalBaselineDataQueryParams,
)
from openbb_government_us.usda.utils import ers_international_baseline_data
from openbb_government_us.usda.utils.ers_international_baseline_data import (
    COMMODITIES,
    DEFAULT_ATTRIBUTE,
    DEFAULT_COMMODITY,
    INTERNATIONAL_BASELINE_FILES,
    MEDIA_PATH,
    PRODUCT_PAGE,
    attributes_for_commodity,
    build_url,
    countries_for_commodity,
    parse_amount,
    parse_rows,
    select_csv_member,
)

FIXTURE_CSV = (
    "Data_Release_Year,Country,Topic,Commodity,Attribute,Amount,Unit,Year,Year_type\n"
    "2025,United States,Crops,Wheat,Production,100,Thousand metric tons,2023/24,Crop year\n"
    "2025,United States,Crops,Wheat,Production,110,Thousand metric tons,2024/25,Crop year\n"
    "2025,China,Crops,Wheat,Production,500,Thousand metric tons,2023/24,Crop year\n"
    '2025,China,Crops,Wheat,Production,"1,200",Thousand metric tons,2024/25,Crop year\n'
    "2025,Argentina,Crops,Wheat,Production,50,Thousand metric tons, 2023/24,Crop year\n"
    "2025,Argentina,Crops,Wheat,Production,No data,Thousand metric tons,2024/25,Crop year\n"
    "2025,Hong Kong,Crops,Wheat,Production,No data,Thousand metric tons,2023/24,Crop year\n"
    "2025,Hong Kong,Crops,Wheat,Production,No data,Thousand metric tons,2024/25,Crop year\n"
    "2025,United States,Crops,Wheat,Exports,30,Thousand metric tons,2023/24,Crop year\n"
    "2025,Argentina,Livestock,Beef and veal,Production,2720,Thousand metric tons,2023,Calendar year\n"
    "2025,Argentina,Livestock,Beef and veal,Production,2650,Thousand metric tons,2024,Calendar year\n"
    "2025,Argentina,Crops,Wheat,Production,999,Thousand metric tons,notayear,Crop year\n"
)


def _records():
    """Parse the fixture into long records."""
    return parse_rows(FIXTURE_CSV)


class TestErsInternationalBaselineDataUtils:
    """Tests for the ers_international_baseline_data utils module."""

    def test_catalog_and_url(self):
        """The catalog is the single baseline ZIP and build_url points at it."""
        assert INTERNATIONAL_BASELINE_FILES == {
            "international_baseline": (MEDIA_PATH, PRODUCT_PAGE)
        }
        assert MEDIA_PATH.startswith("/media/5324/")
        assert build_url().endswith(MEDIA_PATH)
        assert len(COMMODITIES) == 12
        assert DEFAULT_COMMODITY == "Wheat"
        assert DEFAULT_ATTRIBUTE == "Production"

    def test_select_csv_member_by_extension(self):
        """The sole CSV member is resolved by extension, ignoring the vintages."""
        names = [
            "2024 International Long-Term Projections to 2033.xlsx",
            "2025 International Long-Term Projections to 2034.csv",
            "2025 International Long-Term Projections to 2034.xlsx",
        ]
        assert (
            select_csv_member(names)
            == "2025 International Long-Term Projections to 2034.csv"
        )

    def test_select_csv_member_raises_without_csv(self):
        """An archive with no CSV member raises OpenBBError."""
        with pytest.raises(OpenBBError, match="No CSV member"):
            select_csv_member(["2024.xlsx", "2025.xlsx"])

    def test_parse_amount_handles_tokens_commas_and_blanks(self):
        """Amounts strip commas; 'No data' and blanks become None."""
        assert parse_amount("100") == 100.0
        assert parse_amount("1,200") == 1200.0
        assert parse_amount(" 53650 ") == 53650.0
        assert parse_amount("No data") is None
        assert parse_amount("") is None

    def test_parse_rows_strips_and_coerces(self):
        """Rows strip the leading-space year and coerce the null token to None."""
        records = _records()
        argentina = next(
            record
            for record in records
            if record["commodity"] == "Wheat"
            and record["country"] == "Argentina"
            and record["year"] == "2023/24"
        )
        assert argentina == {
            "country": "Argentina",
            "topic": "Crops",
            "commodity": "Wheat",
            "attribute": "Production",
            "unit": "Thousand metric tons",
            "year": "2023/24",
            "year_type": "Crop year",
            "amount": 50.0,
        }
        china_2024 = next(
            record
            for record in records
            if record["country"] == "China" and record["year"] == "2024/25"
        )
        assert china_2024["amount"] == 1200.0
        no_data = [record for record in records if record["amount"] is None]
        assert {record["country"] for record in no_data} == {"Argentina", "Hong Kong"}

    def test_attributes_for_commodity_first_seen_order(self):
        """Attributes list in first-seen source order for the commodity."""
        assert attributes_for_commodity(_records(), "Wheat") == [
            "Production",
            "Exports",
        ]
        assert attributes_for_commodity(_records(), "Beef and veal") == ["Production"]

    def test_countries_for_commodity_includes_all(self):
        """Countries list every distinct area, even all-'No data' ones."""
        assert countries_for_commodity(_records(), "Wheat") == [
            "United States",
            "China",
            "Argentina",
            "Hong Kong",
        ]

    def test_afetch_records(self, monkeypatch):
        """afetch_records unzips, picks the CSV, and parses through the cache."""
        calls = []
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("2020 International Long-Term Projections.xlsx", b"junk")
            archive.writestr(
                "2025 International Long-Term Projections to 2034.csv", FIXTURE_CSV
            )
        zip_bytes = buffer.getvalue()

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return zip_bytes

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ers_international_baseline_data.afetch_records())
        assert calls == [(MEDIA_PATH, PRODUCT_PAGE)]
        assert any(record["commodity"] == "Wheat" for record in records)


class TestInternationalBaselineData:
    """Tests for the InternationalBaselineData model."""

    def test_transform_query_defaults(self):
        """transform_query applies the commodity and attribute defaults."""
        query = InternationalBaselineDataFetcher.transform_query({})
        assert isinstance(query, InternationalBaselineDataQueryParams)
        assert query.commodity == DEFAULT_COMMODITY
        assert query.attribute == DEFAULT_ATTRIBUTE
        assert query.country is None

    def test_blank_values_fall_back_to_defaults(self):
        """Blank commodity and attribute normalize to their defaults."""
        query = InternationalBaselineDataQueryParams(commodity="", attribute="")
        assert query.commodity == DEFAULT_COMMODITY
        assert query.attribute == DEFAULT_ATTRIBUTE

    def test_invalid_commodity_raises(self):
        """An unknown commodity raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid commodity: bogus"):
            InternationalBaselineDataQueryParams(commodity="bogus")

    def test_attribute_and_country_accept_lists(self):
        """List-valued attribute and country collapse to their first element."""
        assert (
            InternationalBaselineDataQueryParams(attribute=["Exports"]).attribute
            == "Exports"
        )
        assert (
            InternationalBaselineDataQueryParams(country=["  China "]).country
            == "China"
        )
        assert InternationalBaselineDataQueryParams(country="").country is None

    def test_aextract_data_returns_records(self, monkeypatch):
        """aextract_data returns the parsed projection records."""

        async def fake_afetch_records():
            return _records()

        monkeypatch.setattr(
            ers_international_baseline_data, "afetch_records", fake_afetch_records
        )
        query = InternationalBaselineDataFetcher.transform_query({})
        records = asyncio.run(
            InternationalBaselineDataFetcher.aextract_data(query, None)
        )
        assert any(record["commodity"] == "Wheat" for record in records)

    def test_default_pivot_country_columns_by_year(self):
        """Wheat production spreads countries into columns with years as rows."""
        query = InternationalBaselineDataFetcher.transform_query({})
        data = InternationalBaselineDataFetcher.transform_data(query, _records())
        assert [row.year for row in data] == ["2023/24", "2024/25"]
        first = data[0].model_dump(by_alias=True)
        assert list(first)[:6] == [
            "year",
            "commodity",
            "attribute",
            "unit",
            "year_type",
            "topic",
        ]
        assert list(first)[6:] == ["United States", "China", "Argentina"]
        assert first["United States"] == 100.0
        assert first["China"] == 500.0
        assert first["Argentina"] == 50.0
        assert first["commodity"] == "Wheat"
        assert first["attribute"] == "Production"
        assert first["unit"] == "Thousand metric tons"
        assert first["year_type"] == "Crop year"
        assert first["topic"] == "Crops"

    def test_all_none_country_column_dropped(self):
        """A country whose values are all None never becomes a column."""
        query = InternationalBaselineDataFetcher.transform_query({})
        data = InternationalBaselineDataFetcher.transform_data(query, _records())
        served = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        assert "Hong Kong" not in served

    def test_partial_none_country_kept_with_none_cell(self):
        """A country with one 'No data' year keeps its column and a None cell."""
        query = InternationalBaselineDataFetcher.transform_query({})
        data = InternationalBaselineDataFetcher.transform_data(query, _records())
        second = data[1].model_dump(by_alias=True)
        assert second["year"] == "2024/25"
        assert second["China"] == 1200.0
        assert second["Argentina"] is None

    def test_country_filter_single_column(self):
        """The country filter narrows the columns to one area."""
        query = InternationalBaselineDataFetcher.transform_query({"country": "China"})
        data = InternationalBaselineDataFetcher.transform_data(query, _records())
        rows = [row.model_dump(by_alias=True) for row in data]
        assert [row["year"] for row in rows] == ["2023/24", "2024/25"]
        for row in rows:
            assert "United States" not in row
        assert rows[0]["China"] == 500.0
        assert rows[1]["China"] == 1200.0

    def test_year_filters(self):
        """start_year and end_year filter the emitted year rows."""
        start = InternationalBaselineDataFetcher.transform_data(
            InternationalBaselineDataFetcher.transform_query({"start_year": 2024}),
            _records(),
        )
        assert [row.year for row in start] == ["2024/25"]
        end = InternationalBaselineDataFetcher.transform_data(
            InternationalBaselineDataFetcher.transform_query({"end_year": 2023}),
            _records(),
        )
        assert [row.year for row in end] == ["2023/24"]

    def test_livestock_calendar_year_pivot(self):
        """A livestock commodity pivots on calendar years with its topic."""
        query = InternationalBaselineDataFetcher.transform_query(
            {"commodity": "Beef and veal"}
        )
        data = InternationalBaselineDataFetcher.transform_data(query, _records())
        assert [row.year for row in data] == ["2023", "2024"]
        first = data[0].model_dump(by_alias=True)
        assert first["year_type"] == "Calendar year"
        assert first["topic"] == "Livestock"
        assert first["Argentina"] == 2720.0

    def test_other_attribute_selects_its_rows(self):
        """Selecting another measure restricts the pivot to that attribute."""
        query = InternationalBaselineDataFetcher.transform_query(
            {"attribute": "Exports"}
        )
        data = InternationalBaselineDataFetcher.transform_data(query, _records())
        assert [row.year for row in data] == ["2023/24"]
        assert data[0].model_dump(by_alias=True)["United States"] == 30.0

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served record key."""
        declared = set()
        for name, field in InternationalBaselineDataData.model_fields.items():
            alias = field.serialization_alias or name
            extra = field.json_schema_extra
            config = extra.get("x-widget_config", {}) if isinstance(extra, dict) else {}
            if config.get("exclude"):
                continue
            declared.add(to_snake(alias))
        query = InternationalBaselineDataFetcher.transform_query({})
        data = InternationalBaselineDataFetcher.transform_data(query, _records())
        served = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        assert declared <= served

    def test_no_dead_constant_column(self):
        """Served keys lacking a columnDef are the varying country extras."""
        declared = set()
        for name, field in InternationalBaselineDataData.model_fields.items():
            alias = field.serialization_alias or name
            declared.add(to_snake(alias))
        query = InternationalBaselineDataFetcher.transform_query({})
        data = InternationalBaselineDataFetcher.transform_data(query, _records())
        rows = [row.model_dump(by_alias=True) for row in data]
        served = set()
        for row in rows:
            served.update(row)
        for key in served - declared:
            values = [row.get(key) for row in rows]
            assert len(set(values)) > 1

    def test_param_scoping_options(self):
        """Choice params are single-select with real labels and endpoints."""
        extra = InternationalBaselineDataQueryParams.__json_schema_extra__
        commodity = extra["commodity"]["x-widget_config"]
        assert commodity["label"] == "Commodity"
        assert commodity["multiSelect"] is False
        assert {opt["value"] for opt in commodity["options"]} == set(COMMODITIES)
        attribute = extra["attribute"]["x-widget_config"]
        assert attribute["type"] == "endpoint"
        assert attribute["optionsParams"] == {"commodity": "$commodity"}
        assert attribute["value"] == DEFAULT_ATTRIBUTE
        country = extra["country"]["x-widget_config"]
        assert country["type"] == "endpoint"
        assert country["optionsParams"] == {"commodity": "$commodity"}
        assert "value" not in country

    def test_widget_config_and_column_headers(self):
        """The whole-widget config and per-field headers are populated."""
        widget = InternationalBaselineDataData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert widget["$.name"] == "USDA ERS International Baseline Data"
        assert widget["$.category"] == "Economy"
        assert widget["$.subCategory"] == "Agriculture"
        assert widget["$.source"] == ["USDA", "ERS"]
        fields = InternationalBaselineDataData.model_fields
        assert fields["year"].json_schema_extra["x-widget_config"]["pinned"] == "left"
        assert fields["attribute"].json_schema_extra["x-widget_config"]["hide"] is True
        assert (
            fields["attribute"].json_schema_extra["x-widget_config"]["headerName"]
            == "Measure"
        )

    def test_null_token_mixin_coerces_placeholder(self):
        """The Data model coerces placeholder tokens to None but keeps columns."""
        row = InternationalBaselineDataData.model_validate(
            {"year": "2024/25", "unit": "--", "United States": 110.0}
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["unit"] is None
        assert dumped["United States"] == 110.0

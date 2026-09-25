"""Tests for the USDA ERS global food assessment utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.global_food_assessment import (
    GlobalFoodAssessmentData,
    GlobalFoodAssessmentFetcher,
    GlobalFoodAssessmentQueryParams,
)
from openbb_government_us.usda.utils import ers_global_food_assessment
from openbb_government_us.usda.utils.ers_global_food_assessment import (
    DEFAULT_ELEMENT,
    ELEMENTS,
    GLOBAL_FOOD_ASSESSMENT_FILES,
    MEDIA_PATH,
    PRODUCT_PAGE,
    REGIONS,
    UNIT,
    build_url,
    parse_amount,
    parse_rows,
)

FIXTURE_CSV = (
    "Dataset,Element,Region,Subregion,Year,Millions of metric tons\n"
    "Global Food Assessment,Total grain demand,Asia,East Asia,2025,6.9\n"
    "Global Food Assessment,Total grain demand,Asia,South Asia,2025,473.3\n"
    "Global Food Assessment,Total grain demand,Asia,Southeast Asia,2025,\n"
    "Global Food Assessment,Total grain demand,Sub-Saharan Africa,Central Africa,2025,17.9\n"
    "Global Food Assessment,Total grain demand,Sub-Saharan Africa,East Africa,2025,78.1\n"
    "Global Food Assessment,Total grain demand,Former Soviet Union,Former Soviet Union,2025,48.6\n"
    "Global Food Assessment,Total grain demand,Latin America and the Caribbean,Central America,2025,\n"
    '"Global Food Assessment",Total grain demand,Asia,"Asia, total",2025,687.1\n'
    '"Global Food Assessment",Total grain demand,Sub-Saharan Africa,"Sub-Saharan Africa, total",2025,213.9\n'
    '"Global Food Assessment",Total grain demand,Former Soviet Union,"Former Soviet Union, total",2025,48.6\n'
    '"Global Food Assessment",Total grain demand,GFA countries,"GFA countries, total",2025,"1,138.4"\n'
    "Global Food Assessment,Total grain demand,Asia,East Asia,2035,8.1\n"
    "Global Food Assessment,Total grain demand,Asia,South Asia,2035,590.9\n"
    "Global Food Assessment,Total grain demand,Asia,Southeast Asia,2035,\n"
    "Global Food Assessment,Total grain demand,Sub-Saharan Africa,Central Africa,2035,25.0\n"
    "Global Food Assessment,Total grain demand,Sub-Saharan Africa,East Africa,2035,110.1\n"
    "Global Food Assessment,Total grain demand,Former Soviet Union,Former Soviet Union,2035,58.2\n"
    "Global Food Assessment,Total grain demand,Latin America and the Caribbean,Central America,2035,14.7\n"
    '"Global Food Assessment",Total grain demand,Asia,"Asia, total",2035,841.2\n'
    '"Global Food Assessment",Total grain demand,Sub-Saharan Africa,"Sub-Saharan Africa, total",2035,297.8\n'
    '"Global Food Assessment",Total grain demand,Former Soviet Union,"Former Soviet Union, total",2035,58.2\n'
    '"Global Food Assessment",Total grain demand,GFA countries,"GFA countries, total",2035,1413.4\n'
    "Global Food Assessment,Total grain demand,Asia,East Asia,notayear,99\n"
    "Global Food Assessment,Implied additional supply required,Former Soviet Union,Former Soviet Union,2025,-23.5\n"
    "Global Food Assessment,Implied additional supply required,Sub-Saharan Africa,Central Africa,2025,7.9\n"
    "Global Food Assessment,Implied additional supply required,Sub-Saharan Africa,East Africa,2025,21.9\n"
    '"Global Food Assessment",Implied additional supply required,Sub-Saharan Africa,"Sub-Saharan Africa, total",2025,69.1\n'
    "Global Food Assessment,Implied additional supply required,Former Soviet Union,Former Soviet Union,2035,-21.2\n"
    "Global Food Assessment,Implied additional supply required,Sub-Saharan Africa,Central Africa,2035,11.7\n"
    "Global Food Assessment,Implied additional supply required,Sub-Saharan Africa,East Africa,2035,45.2\n"
    '"Global Food Assessment",Implied additional supply required,Sub-Saharan Africa,"Sub-Saharan Africa, total",2035,106.4\n'
    "Global Food Assessment,Grain production,Middle East and North Africa,Middle East,2025,24.6\n"
    "Global Food Assessment,Grain production,Middle East and North Africa,North Africa,2025,29.8\n"
    '"Global Food Assessment",Grain production,Middle East and North Africa,"Middle East and North Africa, total",2025,54.4\n'
    "Global Food Assessment,Grain production,Middle East and North Africa,Middle East,2035,31.8\n"
    "Global Food Assessment,Grain production,Middle East and North Africa,North Africa,2035,34.1\n"
    '"Global Food Assessment",Grain production,Middle East and North Africa,"Middle East and North Africa, total",2035,65.9\n'
)

DEFAULT_COLUMNS = [
    "East Asia",
    "South Asia",
    "Central Africa",
    "East Africa",
    "Former Soviet Union",
    "Asia, total",
    "Sub-Saharan Africa, total",
    "Former Soviet Union, total",
    "GFA countries, total",
    "Central America",
]


def _records():
    """Parse the fixture into long records."""
    return parse_rows(FIXTURE_CSV)


class TestErsGlobalFoodAssessmentUtils:
    """Tests for the ers_global_food_assessment utils module."""

    def test_catalog_and_url(self):
        """The catalog is the single CSV and build_url points at it."""
        assert GLOBAL_FOOD_ASSESSMENT_FILES == {
            "global_food_assessment": (MEDIA_PATH, PRODUCT_PAGE)
        }
        assert MEDIA_PATH.startswith("/media/6171/")
        assert MEDIA_PATH.endswith(".csv")
        assert PRODUCT_PAGE == "data-products/global-food-assessment"
        assert build_url().endswith(MEDIA_PATH)
        assert len(ELEMENTS) == 5
        assert len(REGIONS) == 6
        assert DEFAULT_ELEMENT == "Total grain demand"
        assert DEFAULT_ELEMENT in ELEMENTS
        assert UNIT == "Millions of metric tons"

    def test_parse_amount_handles_commas_blanks_and_negatives(self):
        """Amounts strip commas; blanks become None; negatives pass through."""
        assert parse_amount("6.9") == 6.9
        assert parse_amount("1,138.4") == 1138.4
        assert parse_amount(" 213.9 ") == 213.9
        assert parse_amount("-23.5") == -23.5
        assert parse_amount("") is None
        assert parse_amount("No data") is None

    def test_parse_rows_structure_and_drops_dataset(self):
        """Rows carry the five dimensions; the constant Dataset is dropped."""
        records = _records()
        row = next(
            record
            for record in records
            if record["element"] == "Total grain demand"
            and record["subregion"] == "Asia, total"
            and record["year"] == "2025"
        )
        assert row == {
            "element": "Total grain demand",
            "region": "Asia",
            "subregion": "Asia, total",
            "year": "2025",
            "amount": 687.1,
        }
        assert "Dataset" not in row
        blank = next(
            record
            for record in records
            if record["subregion"] == "Southeast Asia" and record["year"] == "2025"
        )
        assert blank["amount"] is None
        negative = next(
            record
            for record in records
            if record["element"] == "Implied additional supply required"
            and record["subregion"] == "Former Soviet Union"
            and record["year"] == "2025"
        )
        assert negative["amount"] == -23.5

    def test_afetch_records(self, monkeypatch):
        """afetch_records decodes and parses through the cache."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return FIXTURE_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ers_global_food_assessment.afetch_records())
        assert calls == [(MEDIA_PATH, PRODUCT_PAGE)]
        assert any(record["element"] == "Total grain demand" for record in records)


class TestGlobalFoodAssessment:
    """Tests for the GlobalFoodAssessment model."""

    def test_transform_query_defaults(self):
        """transform_query applies the measure default and a null region."""
        query = GlobalFoodAssessmentFetcher.transform_query({})
        assert isinstance(query, GlobalFoodAssessmentQueryParams)
        assert query.element == DEFAULT_ELEMENT
        assert query.region is None
        assert query.start_year is None
        assert query.end_year is None

    def test_blank_element_falls_back_to_default(self):
        """A blank measure normalizes to the default."""
        assert GlobalFoodAssessmentQueryParams(element="").element == DEFAULT_ELEMENT

    def test_invalid_element_raises(self):
        """An unknown measure raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid measure: bogus"):
            GlobalFoodAssessmentQueryParams(element="bogus")

    def test_invalid_region_raises(self):
        """An unknown region raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid region: bogus"):
            GlobalFoodAssessmentQueryParams(region="bogus")

    def test_element_and_region_accept_lists(self):
        """List-valued measure and region collapse to their first element."""
        assert (
            GlobalFoodAssessmentQueryParams(element=["Grain production"]).element
            == "Grain production"
        )
        assert (
            GlobalFoodAssessmentQueryParams(region=["  Sub-Saharan Africa "]).region
            == "Sub-Saharan Africa"
        )
        assert GlobalFoodAssessmentQueryParams(region="").region is None
        assert GlobalFoodAssessmentQueryParams(region="   ").region is None

    def test_aextract_data_returns_records(self, monkeypatch):
        """aextract_data returns the parsed records."""

        async def fake_afetch_records():
            return _records()

        monkeypatch.setattr(
            ers_global_food_assessment, "afetch_records", fake_afetch_records
        )
        query = GlobalFoodAssessmentFetcher.transform_query({})
        records = asyncio.run(GlobalFoodAssessmentFetcher.aextract_data(query, None))
        assert any(record["element"] == "Total grain demand" for record in records)

    def test_default_pivot_subregion_columns_by_year(self):
        """The default measure spreads subregions into columns, years as rows."""
        query = GlobalFoodAssessmentFetcher.transform_query({})
        data = GlobalFoodAssessmentFetcher.transform_data(query, _records())
        assert [row.year for row in data] == ["2025", "2035"]
        first = data[0].model_dump(by_alias=True)
        assert list(first)[:3] == ["year", "element", "unit"]
        assert list(first)[3:] == DEFAULT_COLUMNS
        assert first["element"] == "Total grain demand"
        assert first["unit"] == "Millions of metric tons"
        assert first["East Asia"] == 6.9
        assert first["South Asia"] == 473.3
        assert first["Asia, total"] == 687.1
        assert first["GFA countries, total"] == 1138.4

    def test_all_none_subregion_column_dropped(self):
        """A subregion whose values are all blank never becomes a column."""
        query = GlobalFoodAssessmentFetcher.transform_query({})
        data = GlobalFoodAssessmentFetcher.transform_data(query, _records())
        served = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        assert "Southeast Asia" not in served

    def test_partial_none_subregion_kept_with_none_cell(self):
        """A subregion with one blank year keeps its column and a None cell."""
        query = GlobalFoodAssessmentFetcher.transform_query({})
        data = GlobalFoodAssessmentFetcher.transform_data(query, _records())
        first = data[0].model_dump(by_alias=True)
        second = data[1].model_dump(by_alias=True)
        assert first["Central America"] is None
        assert second["Central America"] == 14.7

    def test_region_filter_narrows_columns(self):
        """The region filter narrows the columns to that region's subregions."""
        query = GlobalFoodAssessmentFetcher.transform_query(
            {
                "element": "Implied additional supply required",
                "region": "Sub-Saharan Africa",
            }
        )
        data = GlobalFoodAssessmentFetcher.transform_data(query, _records())
        rows = [row.model_dump(by_alias=True) for row in data]
        assert [row["year"] for row in rows] == ["2025", "2035"]
        assert list(rows[0])[3:] == [
            "Central Africa",
            "East Africa",
            "Sub-Saharan Africa, total",
        ]
        assert "Former Soviet Union" not in rows[0]
        assert rows[0]["Sub-Saharan Africa, total"] == 69.1
        assert rows[1]["Sub-Saharan Africa, total"] == 106.4

    def test_negative_gap_passes_through_raw(self):
        """The implied additional supply gap keeps its negative surplus values."""
        query = GlobalFoodAssessmentFetcher.transform_query(
            {
                "element": "Implied additional supply required",
                "region": "Former Soviet Union",
            }
        )
        data = GlobalFoodAssessmentFetcher.transform_data(query, _records())
        rows = [row.model_dump(by_alias=True) for row in data]
        assert [row["year"] for row in rows] == ["2025", "2035"]
        assert rows[0]["Former Soviet Union"] == -23.5
        assert rows[1]["Former Soviet Union"] == -21.2

    def test_other_element_selects_its_rows(self):
        """Selecting another measure restricts the pivot to that measure."""
        query = GlobalFoodAssessmentFetcher.transform_query(
            {"element": "Grain production", "region": "Middle East and North Africa"}
        )
        data = GlobalFoodAssessmentFetcher.transform_data(query, _records())
        first = data[0].model_dump(by_alias=True)
        assert first["element"] == "Grain production"
        assert list(first)[3:] == [
            "Middle East",
            "North Africa",
            "Middle East and North Africa, total",
        ]
        assert first["Middle East and North Africa, total"] == 54.4

    def test_year_filters(self):
        """start_year and end_year filter the emitted year rows."""
        start = GlobalFoodAssessmentFetcher.transform_data(
            GlobalFoodAssessmentFetcher.transform_query({"start_year": 2035}),
            _records(),
        )
        assert [row.year for row in start] == ["2035"]
        end = GlobalFoodAssessmentFetcher.transform_data(
            GlobalFoodAssessmentFetcher.transform_query({"end_year": 2025}),
            _records(),
        )
        assert [row.year for row in end] == ["2025"]

    def test_non_digit_year_skipped(self):
        """A non-digit year is skipped rather than emitted as a row."""
        query = GlobalFoodAssessmentFetcher.transform_query({})
        data = GlobalFoodAssessmentFetcher.transform_data(query, _records())
        assert all(row.year in {"2025", "2035"} for row in data)

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served record key."""
        declared = set()
        for name, field in GlobalFoodAssessmentData.model_fields.items():
            alias = field.serialization_alias or name
            extra = field.json_schema_extra
            config = extra.get("x-widget_config", {}) if isinstance(extra, dict) else {}
            if config.get("exclude"):
                continue
            declared.add(to_snake(alias))
        query = GlobalFoodAssessmentFetcher.transform_query({})
        data = GlobalFoodAssessmentFetcher.transform_data(query, _records())
        served = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        assert declared <= served

    def test_no_dead_constant_column(self):
        """Served keys lacking a columnDef are the varying subregion extras."""
        declared = set()
        for name, field in GlobalFoodAssessmentData.model_fields.items():
            alias = field.serialization_alias or name
            declared.add(to_snake(alias))
        query = GlobalFoodAssessmentFetcher.transform_query({})
        data = GlobalFoodAssessmentFetcher.transform_data(query, _records())
        rows = [row.model_dump(by_alias=True) for row in data]
        served = set()
        for row in rows:
            served.update(row)
        for key in served - declared:
            values = [row.get(key) for row in rows]
            assert len(set(values)) > 1

    def test_param_scoping_options(self):
        """Choice params are single-select with real labels and static options."""
        extra = GlobalFoodAssessmentQueryParams.__json_schema_extra__
        element = extra["element"]["x-widget_config"]
        assert element["label"] == "Measure"
        assert element["multiSelect"] is False
        assert element["multiple"] is False
        assert element["value"] == DEFAULT_ELEMENT
        assert {opt["value"] for opt in element["options"]} == set(ELEMENTS)
        assert "optionsEndpoint" not in element
        region = extra["region"]["x-widget_config"]
        assert region["label"] == "Region"
        assert region["multiSelect"] is False
        assert region["multiple"] is False
        assert {opt["value"] for opt in region["options"]} == set(REGIONS)
        assert "optionsEndpoint" not in region
        assert "value" not in region

    def test_widget_config_and_column_headers(self):
        """The whole-widget config and per-field headers are populated."""
        widget = GlobalFoodAssessmentData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert widget["$.name"] == "USDA ERS Global Food Assessment"
        assert widget["$.category"] == "Economy"
        assert widget["$.subCategory"] == "Agriculture"
        assert widget["$.source"] == ["USDA", "ERS"]
        fields = GlobalFoodAssessmentData.model_fields
        assert fields["year"].json_schema_extra["x-widget_config"]["pinned"] == "left"
        assert fields["element"].json_schema_extra["x-widget_config"]["hide"] is True
        assert (
            fields["element"].json_schema_extra["x-widget_config"]["headerName"]
            == "Measure"
        )
        assert fields["unit"].json_schema_extra["x-widget_config"]["hide"] is True

    def test_null_token_mixin_coerces_placeholder(self):
        """The Data model coerces placeholder tokens to None but keeps columns."""
        row = GlobalFoodAssessmentData.model_validate(
            {"year": "2025", "unit": "--", "East Asia": 6.9}
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["unit"] is None
        assert dumped["East Asia"] == 6.9

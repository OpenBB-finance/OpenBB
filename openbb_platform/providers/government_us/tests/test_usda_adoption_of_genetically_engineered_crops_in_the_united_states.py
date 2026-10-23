"""Tests for the USDA ERS adoption of genetically engineered crops utils and model."""

import asyncio
import io

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.adoption_of_genetically_engineered_crops_in_the_united_states import (
    AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesData as GeCropsData,
    AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesFetcher as GeCropsFetcher,
    AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesQueryParams as GeCropsQuery,
)
from openbb_government_us.usda.utils import (
    ers_adoption_of_genetically_engineered_crops_in_the_united_states as ers,
)
from openbb_government_us.usda.utils.ers_adoption_of_genetically_engineered_crops_in_the_united_states import (
    CROP_STATES,
    CROPS,
    MEDIA_PATH,
    PRODUCT_PAGE,
    STATES_ALL,
    _clean_state,
    _coerce_value,
    _is_footnote,
    _match_trait,
    _year_columns,
    crop_options,
    parse_sheet,
    state_options,
)

CORN_ROWS: list[list] = [
    ["Genetically engineered (GE) corn varieties by State and United States, 2000–25"],
    ["Insect-resistant (Bt) only (percent of all corn planted) "],
    ["State/Year", "2000", "2001", "2004", "2005", "2025"],
    ["Illinois", 13, 12, 26, 25, 2],
    ["North Dakota 2/", ".", ".", ".", 21, 4],
    ["Other States 1/", 10, 11, 19, 19, 4],
    ["United States", 18, 18, 27, 26, 3],
    ["Herbicide-tolerant (HT) only (percent of all corn planted) "],
    ["State/Year", "2000", "2001", "2004", "2005", "2025"],
    ["Illinois", 3, 3, 5, 6, 4],
    ["North Dakota 2/", ".", ".", ".", 39, 9],
    ["Other States 1/", 6, 8, 21, 19, 13],
    ["United States", 6, 7, 14, 17, 8],
    ["Stacked gene varieties (percent of all corn planted)"],
    ["State/Year", "2000", "2001", "2004", "2005", "2025"],
    ["Illinois", 1, 1, 2, 5, 88],
    ["Indiana", "*", "*", 2, 4, 79],
    ["North Dakota 2/", ".", ".", ".", 15, 80],
    ["Other States 1/", 1, 1, 6, 6, 76],
    ["United States", 1, 1, 6, 9, 84],
    ["All GE varieties (percent of all corn planted) 3/"],
    ["State/Year", "2000", "2001", "2004", "2005", "2025"],
    ["Illinois", 17, 16, 33, 36, 94],
    ["North Dakota 2/", ".", ".", ".", 75, 93],
    ["Other States 1/", 17, 20, 46, 44, 92],
    ["United States", 25, 26, 47, 52, 94],
    [
        "Note: HT indicates herbicide-tolerant varieties; Bt indicates insect resistance."
    ],
    ["* Data rounds to less than 0.5 percent."],
    ["1/ Includes all other States in the corn estimating program."],
    ["2/ Estimates published individually beginning in 2005.        "],
    ["3/ The sum of biotech varieties may not add to total all GE varieties."],
    ["Source: USDA, Economic Research Service using data from USDA, NASS."],
    [None],
]

SOYBEAN_ROWS: list[list] = [
    [
        "Genetically engineered (GE) soybean varieties by State and United States, 2000–25"
    ],
    ["Herbicide-tolerant (HT) only (percent of all soybeans planted)"],
    ["State/Year", "2000", "2012", "2025"],
    ["Arkansas", 43, 94, 97],
    ["North Dakota", 22, 98, 96],
    ["Other States 1/", 54, 93, 95],
    ["United States", 54, 93, 96],
    ["All GE varieties (percent of all soybeans planted)"],
    ["State/Year", "2000", "2012", "2025"],
    ["Arkansas", 43, 94, 97],
    ["North Dakota", 22, 98, 96],
    ["Other States 1/", 54, 93, 95],
    ["United States", 54, 93, 96],
    ["Note: Only HT soybean varieties have data presented."],
    ["1/ Includes all other States in the soybean estimating program."],
    ["Source: USDA, Economic Research Service using data from USDA, NASS."],
]


def _build_workbook(sheet_name: str, rows: list[list]) -> bytes:
    """Build in-memory XLSX bytes with one named sheet holding the given rows."""
    import openpyxl

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    for row in rows:
        sheet.append(["" if cell is None else cell for cell in row])
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


class TestErsAdoptionUtils:
    """Tests for the ers adoption of genetically engineered crops utils module."""

    def test_catalog(self):
        """The hardcoded catalog points at the full-history XLSX and three crops."""
        assert MEDIA_PATH.startswith("/media/5685/")
        assert MEDIA_PATH.endswith(".xlsx")
        assert PRODUCT_PAGE.endswith(
            "adoption-of-genetically-engineered-crops-in-the-united-states"
        )
        assert set(CROPS) == {"corn", "cotton", "soybeans"}
        assert CROPS["corn"]["traits"] == ("Bt only", "HT only", "Stacked", "All GE")
        assert CROPS["soybeans"]["traits"] == ("HT only", "All GE")

    def test_crop_options(self):
        """The crop options are labeled and single-valued per crop."""
        options = crop_options()
        assert {opt["value"] for opt in options} == {"corn", "cotton", "soybeans"}
        assert {opt["label"] for opt in options} == {
            "Corn",
            "Upland cotton",
            "Soybeans",
        }

    def test_state_options(self):
        """State options are the published states, unknown crops falling back to corn."""
        corn = state_options("corn")
        assert [opt["value"] for opt in corn] == list(CROP_STATES["corn"])
        assert corn[-1] == {"label": "United States", "value": "United States"}
        assert state_options("bogus") == state_options("corn")
        assert len(CROP_STATES["cotton"]) == 12
        assert len(CROP_STATES["soybeans"]) == 16

    def test_states_all_is_sorted_union(self):
        """STATES_ALL is the sorted, de-duplicated union across crops."""
        union = {state for states in CROP_STATES.values() for state in states}
        assert set(STATES_ALL) == union
        assert list(STATES_ALL) == sorted(union)

    def test_match_trait(self):
        """Trait block titles map to their short names; other labels do not match."""
        assert (
            _match_trait("Insect-resistant (Bt) only (percent of all corn planted)")
            == "Bt only"
        )
        assert _match_trait("Herbicide-tolerant (HT) only (percent)") == "HT only"
        assert _match_trait("Stacked gene varieties (percent)") == "Stacked"
        assert _match_trait("All GE varieties (percent) 3/") == "All GE"
        assert _match_trait("Illinois") is None

    def test_is_footnote(self):
        """Note, source, asterisk, and numbered-slash lines are footnotes."""
        assert _is_footnote("Note: HT indicates herbicide-tolerant varieties.")
        assert _is_footnote("Source: USDA, Economic Research Service.")
        assert _is_footnote("* Data rounds to less than 0.5 percent.")
        assert _is_footnote("1/ Includes all other States.")
        assert _is_footnote("2/ Estimates published individually beginning in 2005.")
        assert not _is_footnote("Other States 1/")
        assert not _is_footnote("United States")

    def test_clean_state(self):
        """State footnote suffixes are stripped."""
        assert _clean_state("North Dakota 2/") == "North Dakota"
        assert _clean_state("Other States 1/") == "Other States"
        assert _clean_state("United States") == "United States"
        assert _clean_state("Texas 2/ ") == "Texas"

    def test_year_columns(self):
        """Only four-digit numeric cells past the first column become year columns."""
        header = ["State/Year", "2000", "2001", None, "abc", "2025", 42]
        assert _year_columns(header) == [(1, 2000), (2, 2001), (5, 2025)]

    def test_coerce_value(self):
        """Cell coercion maps tokens to floats, None, 0.0, or the skip sentinel."""
        assert _coerce_value(18) == 18.0
        assert _coerce_value(0) == 0.0
        assert _coerce_value("52") == 52.0
        assert _coerce_value(".") is None
        assert _coerce_value("*") == 0.0
        assert _coerce_value(None) is ers._MISSING
        assert _coerce_value("") is ers._MISSING
        assert _coerce_value("  ") is ers._MISSING
        assert _coerce_value("n/a") is ers._MISSING
        assert _coerce_value(True) is ers._MISSING

    def test_parse_sheet_corn_traits_and_tokens(self):
        """Corn parsing captures four traits, strips suffixes, and coerces tokens."""
        records = parse_sheet(CORN_ROWS, "corn")
        traits = {record["trait"] for record in records}
        assert traits == {"Bt only", "HT only", "Stacked", "All GE"}
        states = {record["state"] for record in records}
        assert states == {
            "Illinois",
            "Indiana",
            "North Dakota",
            "Other States",
            "United States",
        }
        us_bt_2000 = next(
            r
            for r in records
            if r["state"] == "United States"
            and r["trait"] == "Bt only"
            and r["year"] == 2000
        )
        assert us_bt_2000["value"] == 18.0
        indiana_star = next(
            r
            for r in records
            if r["state"] == "Indiana" and r["trait"] == "Stacked" and r["year"] == 2000
        )
        assert indiana_star["value"] == 0.0
        nd_na = next(
            r
            for r in records
            if r["state"] == "North Dakota"
            and r["trait"] == "Bt only"
            and r["year"] == 2000
        )
        assert nd_na["value"] is None

    def test_parse_sheet_skips_missing_and_blank_cells(self):
        """Year columns past a short row, and blank cells, emit no record."""
        rows = [
            ["Insect-resistant (Bt) only (percent of all corn planted)"],
            ["State/Year", "2000", "2001", "2002", "2003"],
            ["Illinois", 10, "", 12],
        ]
        records = parse_sheet(rows, "corn")
        assert {record["year"] for record in records} == {2000, 2002}

    def test_parse_sheet_skips_footnotes_and_titles(self):
        """No record carries a footnote, source, or block-title as its state."""
        records = parse_sheet(CORN_ROWS, "corn")
        for record in records:
            assert not record["state"].startswith("Note")
            assert not record["state"].startswith("Source")
            assert not record["state"].startswith("*")
            assert "varieties" not in record["state"].casefold()

    def test_parse_sheet_soybeans_two_traits(self):
        """Soybean parsing captures only the HT-only and All-GE traits."""
        records = parse_sheet(SOYBEAN_ROWS, "soybeans")
        assert {record["trait"] for record in records} == {"HT only", "All GE"}

    def test_parse_sheet_ignores_traits_outside_crop_vocabulary(self):
        """Parsing corn rows as soybeans keeps only the soybean trait vocabulary."""
        records = parse_sheet(CORN_ROWS, "soybeans")
        assert {record["trait"] for record in records} == {"HT only", "All GE"}
        assert all(record["crop"] == "soybeans" for record in records)

    def test_afetch_crop(self, monkeypatch):
        """afetch_crop fetches the workbook through the cache and parses one sheet."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return _build_workbook("Corn", CORN_ROWS)

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ers.afetch_crop("corn"))
        assert calls == [(MEDIA_PATH, PRODUCT_PAGE)]
        assert any(
            r["state"] == "United States"
            and r["trait"] == "All GE"
            and r["year"] == 2025
            for r in records
        )


class TestAdoptionOfGeneticallyEngineeredCropsInTheUnitedStates:
    """Tests for the AdoptionOfGeneticallyEngineeredCrops model."""

    def _corn(self):
        """Parse the corn fixture into long records."""
        return parse_sheet(CORN_ROWS, "corn")

    def _soybeans(self):
        """Parse the soybean fixture into long records."""
        return parse_sheet(SOYBEAN_ROWS, "soybeans")

    def test_transform_query_defaults(self):
        """transform_query applies the crop and state defaults."""
        query = GeCropsFetcher.transform_query({})
        assert isinstance(query, GeCropsQuery)
        assert query.crop == "corn"
        assert query.state == "United States"
        assert query.start_year is None
        assert query.end_year is None

    def test_blank_values_fall_back_to_defaults(self):
        """Blank crop and state normalize to their defaults."""
        query = GeCropsQuery(crop="", state="")
        assert query.crop == "corn"
        assert query.state == "United States"

    def test_invalid_crop_raises(self):
        """An unknown crop raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid crop: bogus"):
            GeCropsQuery(crop="bogus")

    def test_invalid_state_raises(self):
        """An unknown state raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid state\\(s\\): Atlantis"):
            GeCropsQuery(state="Atlantis")

    def test_state_canonicalizes_case_and_list(self):
        """State input canonicalizes casing and accepts comma lists or sequences."""
        assert GeCropsQuery(state="united states").state == "United States"
        assert GeCropsQuery(state="iowa, ohio").state == "Iowa,Ohio"
        assert GeCropsQuery(state=["Texas", "Iowa"]).state == "Texas,Iowa"
        assert GeCropsQuery(state=" , ").state == "United States"

    def test_aextract_data_returns_records(self, monkeypatch):
        """aextract_data returns the selected crop's parsed records."""

        async def fake_afetch_crop(crop):
            return parse_sheet(CORN_ROWS, crop)

        monkeypatch.setattr(ers, "afetch_crop", fake_afetch_crop)
        query = GeCropsFetcher.transform_query({})
        records = asyncio.run(GeCropsFetcher.aextract_data(query, None))
        assert any(record["trait"] == "Stacked" for record in records)

    def test_corn_pivot_four_columns_chronological(self):
        """The corn pivot spreads four traits into columns with year rows ascending."""
        query = GeCropsFetcher.transform_query(
            {"crop": "corn", "state": "United States"}
        )
        data = GeCropsFetcher.transform_data(query, self._corn())
        assert [row.year for row in data] == [2000, 2001, 2004, 2005, 2025]
        first = data[0].model_dump(by_alias=True)
        assert list(first) == [
            "state",
            "year",
            "Bt only",
            "HT only",
            "Stacked",
            "All GE",
        ]
        assert first["state"] == "United States"
        assert first["Bt only"] == 18.0
        assert first["HT only"] == 6.0
        assert first["Stacked"] == 1.0
        assert first["All GE"] == 25.0
        last = data[-1].model_dump(by_alias=True)
        assert (last["Bt only"], last["HT only"], last["Stacked"], last["All GE"]) == (
            3.0,
            8.0,
            84.0,
            94.0,
        )

    def test_soybeans_pivot_two_columns_only(self):
        """The soybean pivot renders only the two soybean traits, never empty columns."""
        query = GeCropsFetcher.transform_query(
            {"crop": "soybeans", "state": "United States"}
        )
        data = GeCropsFetcher.transform_data(query, self._soybeans())
        keys = list(data[0].model_dump(by_alias=True))
        assert keys == ["state", "year", "HT only", "All GE"]
        assert "Bt only" not in keys
        assert "Stacked" not in keys
        row = data[0].model_dump(by_alias=True)
        assert row["HT only"] == row["All GE"] == 54.0

    def test_north_dakota_not_available_tokens_blank_rows(self):
        """North Dakota's '.' tokens emit blank pre-2005 rows that still appear."""
        query = GeCropsFetcher.transform_query(
            {"crop": "corn", "state": "North Dakota"}
        )
        data = GeCropsFetcher.transform_data(query, self._corn())
        assert [row.year for row in data] == [2000, 2001, 2004, 2005, 2025]
        blank = data[0].model_dump(by_alias=True)
        assert blank["Bt only"] is None
        assert blank["All GE"] is None
        populated = next(row for row in data if row.year == 2005).model_dump(
            by_alias=True
        )
        assert populated["Bt only"] == 21.0
        assert populated["All GE"] == 75.0

    def test_state_filter_selects_only_requested_state(self):
        """Only rows for the selected state are emitted."""
        query = GeCropsFetcher.transform_query({"crop": "corn", "state": "Illinois"})
        data = GeCropsFetcher.transform_data(query, self._corn())
        assert {row.state for row in data} == {"Illinois"}

    def test_multiple_states_pivot(self):
        """Multiple selected states each yield their own rows, sorted by state then year."""
        query = GeCropsFetcher.transform_query(
            {"crop": "corn", "state": "United States,Illinois"}
        )
        data = GeCropsFetcher.transform_data(query, self._corn())
        states = [row.state for row in data]
        assert set(states) == {"Illinois", "United States"}
        assert states == sorted(states)

    def test_year_filters(self):
        """start_year and end_year bound the emitted year rows."""
        start = GeCropsFetcher.transform_data(
            GeCropsFetcher.transform_query({"crop": "corn", "start_year": 2005}),
            self._corn(),
        )
        assert [row.year for row in start] == [2005, 2025]
        end = GeCropsFetcher.transform_data(
            GeCropsFetcher.transform_query({"crop": "corn", "end_year": 2001}),
            self._corn(),
        )
        assert [row.year for row in end] == [2000, 2001]

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served record key."""
        declared = set()
        for name, field in GeCropsData.model_fields.items():
            alias = field.serialization_alias or name
            extra = field.json_schema_extra
            config = extra.get("x-widget_config", {}) if isinstance(extra, dict) else {}
            if config.get("exclude"):
                continue
            declared.add(to_snake(alias))
        assert declared == {"state", "year"}
        query = GeCropsFetcher.transform_query({"crop": "corn"})
        data = GeCropsFetcher.transform_data(query, self._corn())
        served = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        assert declared <= served

    def test_no_dead_constant_column(self):
        """Served keys lacking a column definition vary across rows, never constant."""
        query = GeCropsFetcher.transform_query(
            {"crop": "corn", "state": "United States"}
        )
        data = GeCropsFetcher.transform_data(query, self._corn())
        declared = {"state", "year"}
        per_key: dict[str, set] = {}
        for row in data:
            for key, value in row.model_dump(by_alias=True).items():
                per_key.setdefault(key, set()).add(value)
        for key, values in per_key.items():
            if to_snake(key) not in declared:
                assert len(values) > 1

    def test_param_scoping_options(self):
        """Choice params are single-select with real labels and dependent options."""
        extra = GeCropsQuery.__json_schema_extra__
        crop = extra["crop"]["x-widget_config"]
        assert crop["label"] == "Crop"
        assert crop["multiSelect"] is False and crop["multiple"] is False
        assert {opt["value"] for opt in crop["options"]} == {
            "corn",
            "cotton",
            "soybeans",
        }
        state = extra["state"]["x-widget_config"]
        assert state["label"] == "State"
        assert state["multiSelect"] is False and state["multiple"] is False
        assert state["type"] == "endpoint"
        assert state["value"] == "United States"
        assert state["optionsEndpoint"].endswith("/usda/ge_crop_states")
        assert state["optionsParams"] == {"crop": "$crop"}
        assert extra["state"]["multiple_items_allowed"] is True

    def test_widget_config_and_column_headers(self):
        """The whole-widget config and per-field headers are populated."""
        widget = GeCropsData.model_config["json_schema_extra"]["x-widget_config"]
        assert widget["$.name"] == "USDA ERS Adoption of Genetically Engineered Crops"
        assert widget["$.category"] == "Economy"
        assert widget["$.subCategory"] == "Agriculture"
        assert widget["$.source"] == ["USDA", "ERS"]
        fields = GeCropsData.model_fields
        assert fields["state"].json_schema_extra["x-widget_config"]["pinned"] == "left"
        assert fields["year"].json_schema_extra["x-widget_config"]["pinned"] == "left"
        assert fields["year"].json_schema_extra["x-widget_config"]["maxWidth"] == 90

    def test_null_token_mixin_coerces_placeholder(self):
        """The Data model coerces placeholder tokens to None but keeps columns."""
        row = GeCropsData.model_validate(
            {"state": "United States", "year": 2025, "All GE": "--"}
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["state"] == "United States"
        assert dumped["All GE"] is None

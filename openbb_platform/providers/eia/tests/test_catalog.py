"""Tests for the EIA dataset catalog runtime module."""

from datetime import date, datetime

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_us_eia.utils import catalog

GROUPS = [
    "aeo",
    "coal",
    "crude_oil_imports",
    "densified_biomass",
    "electricity",
    "electricity_grid",
    "ieo",
    "international",
    "natural_gas",
    "nuclear_outages",
    "petroleum",
    "seds",
    "state_electricity_profiles",
    "total_energy",
]


class TestCatalogIntegrity:
    """The packaged catalog asset is complete and well-formed."""

    def test_all_groups_present(self):
        assert sorted(catalog.load_catalog()) == GROUPS

    @pytest.mark.parametrize("group", GROUPS)
    def test_dataset_specs_well_formed(self, group):
        datasets = catalog.get_group(group)["datasets"]
        assert datasets
        for slug, spec in datasets.items():
            assert len(slug) <= 60
            if group not in ("aeo", "ieo"):
                assert slug == catalog.snake_case(slug)
            assert spec["path"]
            assert spec["name"]
            assert spec["frequencies"]
            assert spec["default_frequency"] in spec["frequencies"]
            for freq in spec["frequencies"].values():
                assert freq["path"]
                catalog.parse_period("2020-01-01T00", 'YYYY-MM-DD"T"HH24')
                assert freq["format"]
            assert spec["data_columns"]
            for column, detail in spec["data_columns"].items():
                assert column == catalog.snake_case(column)
                assert detail["id"]
            for facet, detail in spec["facets"].items():
                assert facet == catalog.snake_case(facet)
                assert detail["id"]

    @pytest.mark.parametrize("group", GROUPS)
    def test_period_formats_supported(self, group):
        for spec in catalog.get_group(group)["datasets"].values():
            for freq in spec["frequencies"].values():
                catalog.format_period(date(2024, 5, 15), freq["format"])

    def test_grid_group_merges_daily_routes(self):
        spec = catalog.get_dataset("electricity_grid", "demand")
        assert spec["frequencies"]["daily"]["path"].startswith("electricity/rto/daily")
        assert spec["frequencies"]["hourly"]["path"] == "electricity/rto/region-data"
        assert spec["facets"]["timezone"]["frequencies"] == ["daily"]

    def test_petroleum_duplicates_dropped(self):
        paths = {
            spec["path"] for spec in catalog.get_group("petroleum")["datasets"].values()
        }
        assert "petroleum/move/imc1" not in paths
        assert "petroleum/pri/imc1" in paths


class TestCatalogLookups:
    """Lookup helpers resolve entries and raise on unknown keys."""

    def test_get_group_unknown_raises(self):
        with pytest.raises(OpenBBError, match="Unknown EIA group"):
            catalog.get_group("wind")

    def test_get_dataset_unknown_raises(self):
        with pytest.raises(OpenBBError, match="Unknown dataset"):
            catalog.get_dataset("coal", "not_a_dataset")

    def test_dataset_choices(self):
        assert "receipts" in catalog.dataset_choices("coal")

    def test_facet_choices_embedded(self):
        choices = catalog.facet_choices("coal", "coal_rank")
        assert {"value", "label", "param"} == set(choices[0])

    def test_facet_choices_too_large_is_empty(self):
        assert catalog.facet_choices("petroleum", "region") == []

    def test_facet_schema_with_choices(self):
        schema = catalog.facet_schema("coal", "coal_rank")
        assert schema["multiple_items_allowed"] is True
        assert "metallurgical" in schema["choices"]

    def test_facet_schema_without_choices(self):
        assert catalog.facet_schema("petroleum", "series") == {
            "multiple_items_allowed": True
        }

    def test_facet_description_lists_applicability(self):
        text = catalog.facet_description("coal", "country")
        assert "comma-separated" in text
        assert "exports_imports_quantity_price" in text

    def test_facet_description_single_select(self):
        text = catalog.facet_description("coal", "market_type", multiple=False)
        assert "comma-separated" not in text

    def test_facet_description_uncatalogued_values(self):
        text = catalog.facet_description("petroleum", "series")
        assert "facet_options" in text

    def test_snake_case(self):
        assert catalog.snake_case("percentOutage") == "percent_outage"
        assert catalog.snake_case("heat-content") == "heat_content"
        assert catalog.snake_case("stateID") == "state_id"


class TestResolveFrequency:
    """Frequency resolution validates against the dataset."""

    def test_default_frequency(self):
        spec = catalog.get_dataset("coal", "consumption_and_quality")
        frequency, freq_spec = catalog.resolve_frequency(spec, None)
        assert frequency == spec["default_frequency"]
        assert freq_spec["path"] == spec["path"]

    def test_explicit_frequency(self):
        spec = catalog.get_dataset("coal", "consumption_and_quality")
        frequency, _ = catalog.resolve_frequency(spec, "annual")
        assert frequency == "annual"

    def test_invalid_frequency_raises(self):
        spec = catalog.get_dataset("coal", "consumption_and_quality")
        with pytest.raises(OpenBBError, match="not available"):
            catalog.resolve_frequency(spec, "hourly")

    def test_missing_default_falls_back_to_first(self):
        spec = {"path": "x", "frequencies": {"annual": {}}, "default_frequency": None}
        frequency, _ = catalog.resolve_frequency(spec, None)
        assert frequency == "annual"


class TestResolveDataColumns:
    """Data column resolution maps snake names onto API ids."""

    def test_default_returns_all(self):
        spec = catalog.get_dataset("nuclear_outages", "us_nuclear_outages")
        assert catalog.resolve_data_columns(spec, None) == [
            "capacity",
            "outage",
            "percentOutage",
        ]

    def test_subset_and_normalization(self):
        spec = catalog.get_dataset("nuclear_outages", "us_nuclear_outages")
        assert catalog.resolve_data_columns(spec, "percent_outage, capacity") == [
            "percentOutage",
            "capacity",
        ]

    def test_invalid_raises(self):
        spec = catalog.get_dataset("nuclear_outages", "us_nuclear_outages")
        with pytest.raises(OpenBBError, match="Invalid data_type"):
            catalog.resolve_data_columns(spec, "megawatts")


class TestResolveFacets:
    """Facet resolution maps canonical parameters onto API facet ids."""

    def test_maps_and_splits_values(self):
        spec = catalog.get_dataset("coal", "exports_imports_quantity_price")
        query = catalog.resolve_facets(
            spec, "quarterly", {"coal_rank": "MET, STM", "country": "CA"}
        )
        assert query == {"coalRankId": ["MET", "STM"], "countryId": ["CA"]}

    def test_none_and_empty_skipped(self):
        spec = catalog.get_dataset("coal", "exports_imports_quantity_price")
        assert (
            catalog.resolve_facets(spec, "annual", {"coal_rank": None, "country": ""})
            == {}
        )

    def test_inapplicable_facet_raises(self):
        spec = catalog.get_dataset("coal", "exports_imports_quantity_price")
        with pytest.raises(OpenBBError, match="does not apply"):
            catalog.resolve_facets(spec, "annual", {"mine_state": "PA"})

    def test_frequency_restricted_facet(self):
        spec = catalog.get_dataset("electricity_grid", "demand")
        assert catalog.resolve_facets(spec, "daily", {"timezone": "Eastern"}) == {
            "timezone": ["Eastern"]
        }
        with pytest.raises(OpenBBError, match="only applies"):
            catalog.resolve_facets(spec, "hourly", {"timezone": "Eastern"})

    def test_embedded_choices_correct_casing(self):
        spec = catalog.get_dataset("coal", "exports_imports_quantity_price")
        query = catalog.resolve_facets(spec, "quarterly", {"coal_rank": "met,stm"})
        assert query == {"coalRankId": ["MET", "STM"]}

    def test_embedded_choices_map_param_slugs_to_codes(self):
        spec = catalog.get_dataset("coal", "exports_imports_quantity_price")
        query = catalog.resolve_facets(
            spec, "quarterly", {"coal_rank": "metallurgical,steam_coal"}
        )
        assert query == {"coalRankId": ["MET", "STM"]}

    def test_embedded_choices_invalid_value_lists_choices(self):
        spec = catalog.get_dataset("coal", "exports_imports_quantity_price")
        with pytest.raises(OpenBBError, match="metallurgical") as excinfo:
            catalog.resolve_facets(spec, "quarterly", {"coal_rank": "ANTHRACITE"})
        assert "Invalid coal_rank value(s): ANTHRACITE" in str(excinfo.value)
        assert "steam_coal" in str(excinfo.value)

    def test_invalid_value_on_large_vocabulary_caps_choices(self):
        spec = catalog.get_dataset("seds", "seds")
        with pytest.raises(OpenBBError, match=r"plus \d+ more") as excinfo:
            catalog.resolve_facets(spec, "annual", {"series": "NOT_A_SERIES"})
        assert "facet_options" in str(excinfo.value)


class TestLabelSlugs:
    """Readable parameter slugs derived from display labels."""

    @pytest.mark.parametrize(
        ("label", "slug"),
        [
            ("Battery storage", "battery_storage"),
            ("Spot Price FOB", "spot_price_fob"),
            (
                "U.S. Gulf Coast Kerosene-Type Jet Fuel",
                "us_gulf_coast_kerosene_type_jet_fuel",
            ),
            (
                "Alcoa Power Generating, Inc. - Yadkin Division",
                "alcoa_power_generating_yadkin_division",
            ),
            ("Table 73.  Hydrogen Market Projections", "hydrogen_market_projections"),
            ("Wind & Solar (test)", "wind_and_solar"),
            ("", "value"),
        ],
    )
    def test_label_slug(self, label, slug):
        assert catalog.label_slug(label) == slug

    def test_label_slug_caps_length_at_word_boundary(self):
        slug = catalog.label_slug("word " * 30)
        assert len(slug) <= 60
        assert not slug.endswith("_")

    def test_attach_params_identical_labels_share_one_slug(self):
        choices = catalog.attach_params(
            [
                {"value": "5-0", "label": "United States"},
                {"value": "1-0", "label": "United States"},
            ]
        )
        assert [choice["param"] for choice in choices] == [
            "united_states",
            "united_states",
        ]

    def test_attach_params_distinct_labels_keep_parenthetical(self):
        choices = catalog.attach_params(
            [
                {"value": "8023", "label": "Columbia (WI)"},
                {"value": "2123", "label": "Columbia (SC)"},
            ]
        )
        assert [choice["param"] for choice in choices] == [
            "columbia_wi",
            "columbia_sc",
        ]

    def test_attach_params_code_suffix_is_last_resort(self):
        choices = catalog.attach_params(
            [
                {"value": "A1", "label": "Columbia (WI)"},
                {"value": "A2", "label": "Columbia ( WI )"},
            ]
        )
        params = [choice["param"] for choice in choices]
        assert params[0] == "columbia_wi"
        assert params[1] == "columbia_wi_a2"

    def test_shared_slug_resolves_to_every_code(self):
        spec = catalog.get_dataset("aeo", "2025")
        query = catalog.resolve_facets(spec, "annual", {"region": "united_states"})
        assert sorted(query["regionId"]) == ["1-0", "5-0"]


class TestFormatChoiceList:
    """Choice list rendering for error messages."""

    def test_renders_sorted_by_label(self):
        text = catalog.format_choice_list({"B": "beta", "A": "alpha"}, "fuel")
        assert text.index("A = alpha") < text.index("B = beta")

    def test_caps_and_hints_overflow(self):
        vocabulary = {f"V{i:03d}": f"Label {i:03d}" for i in range(60)}
        text = catalog.format_choice_list(vocabulary, "series")
        assert "V049" in text
        assert "V051" not in text
        assert "... 10 more" in text
        assert "facet_options" in text


class TestPeriodConversion:
    """Period strings round-trip through format and parse helpers."""

    @pytest.mark.parametrize(
        ("fmt", "value", "expected"),
        [
            ("YYYY", date(2024, 5, 15), "2024"),
            ("YYYY-MM", date(2024, 5, 15), "2024-05"),
            ('YYYY-"Q"Q', date(2024, 5, 15), "2024-Q2"),
            ("YYYY-MM-DD", date(2024, 5, 15), "2024-05-15"),
            ('YYYY-MM-DD"T"HH24', date(2024, 5, 15), "2024-05-15T00"),
            (
                'YYYY-MM-DD"T"HH24',
                datetime(2024, 5, 15, 7, 30),
                "2024-05-15T07",
            ),
            ('YYYY-MM-DD"T"HH24TZH', date(2024, 5, 15), "2024-05-15T00"),
        ],
    )
    def test_format_period(self, fmt, value, expected):
        assert catalog.format_period(value, fmt) == expected

    def test_format_period_unknown_raises(self):
        with pytest.raises(OpenBBError, match="Unsupported"):
            catalog.format_period(date(2024, 1, 1), "WW")

    @pytest.mark.parametrize(
        ("fmt", "value", "expected"),
        [
            ("YYYY", "2024", date(2024, 1, 1)),
            ("YYYY-MM", "2024-05", date(2024, 5, 1)),
            ('YYYY-"Q"Q', "2024-Q3", date(2024, 7, 1)),
            ("YYYY-MM-DD", "2024-05-15", date(2024, 5, 15)),
            ('YYYY-MM-DD"T"HH24', "2024-05-15T07", datetime(2024, 5, 15, 7)),
            (
                'YYYY-MM-DD"T"HH24TZH',
                "2024-05-15T07-04",
                datetime.fromisoformat("2024-05-15T07:00-04:00"),
            ),
        ],
    )
    def test_parse_period(self, fmt, value, expected):
        assert catalog.parse_period(value, fmt) == expected

    def test_parse_period_unknown_raises(self):
        with pytest.raises(OpenBBError, match="Unsupported"):
            catalog.parse_period("2024", "WW")

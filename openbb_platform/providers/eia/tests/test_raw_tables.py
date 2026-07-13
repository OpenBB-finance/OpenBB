"""Tests for the ``raw`` pivot: every EIA browser payload shape becomes rows.

The ``raw`` button must answer for whatever view is on screen, so each shape the
browsers return -- classic tables, series lists, rankings, state maps, the
International series and overview payloads -- has to pivot into the same
``category / units / source_key / <periods>`` row form.
"""

import json

import pytest

from openbb_us_eia import browsers

TABLEDATA = {
    "UNITS": "million kilowatthours",
    "ROWS": [
        {
            "SERIES_ID": "ELEC.GEN.ALL-US-99.M",
            "CHART_NAME": "All fuels",
            "DATA": {"202401": "1000.5", "202402": "900"},
        },
        {
            "SERIES_ID": "ELEC.GEN.COW-US-99.M",
            "DESCRIPTION": "Coal",
            "UNITS": "thousand tons",
            "DATA": {"202401": "500", "202402": ""},
        },
    ],
}

SERIES_PAYLOAD = {
    "series": [
        {
            "series_id": "SEDS.TETCB.CA.A",
            "name": "Total energy consumed",
            "units": "billion Btu",
            "data": [["2022", 7000.0], ["2023", 7100.0]],
        }
    ]
}

RANKING_PAYLOAD = {
    "series": [
        {
            "stateName": "Texas",
            "stateId": "TX",
            "seriesId": "SEDS.TETCB.TX.A",
            "displayName": "Total energy consumed",
            "rank": 1,
            "period": "2023",
            "value": "12000.5",
        },
        {
            "stateName": "California",
            "seriesId": "SEDS.TETCB.CA.A",
            "displayName": "Total energy consumed",
            "rank": "2",
            "period": "2023",
            "value": 7100.0,
        },
    ]
}

STATE_MAP_PAYLOAD = {
    "year": 2023,
    "series": {
        "TETCB": {"TX": "12000", "CA": "7100"},
        "PATCB": {"TX": "4000", "CA": "2000"},
    },
}

INTL_SERIES_PAYLOAD = {
    "data": {
        "INTL.44-1-USA-QBTU.A": {"2022": [95.0, 95.12], "2023": [96.0, 96.34]},
        "INTL.44-1-CHN-QBTU.A": {"2022": [130.0, 130.5], "2023": [131.0, 131.7]},
    }
}

INTL_OVERVIEW_PAYLOAD = {
    "data": [
        {
            "series_id": "INTL.44-1-USA-QBTU.A",
            "name": "United States",
            "iso": "USA",
            "unit": "QBTU",
            "frequency": "A",
            "data": [
                {"date": 1672531200000, "value": 96.34},
                {"date": 1704067200000, "value": 97.5},
            ],
        }
    ]
}

BIOFUELS_PAYLOAD = {
    "data": {
        "INTL.79-1-ABW-TBPD.A": {"2024": ["--"]},
        "INTL.80-1-ABW-TBPD.A": {"2024": [0.0, 0.0]},
        "INTL.81-1-ABW-TBPD.A": {"2024": [0.0, 0.0]},
    }
}

LABELS = {
    "region": {"USA": "United States", "CHN": "China", "ABW": "Aruba"},
    "unit": {"QBTU": "quad Btu", "TBPD": "Mb/d"},
    "product": {
        "44": "primary energy",
        "79": "biofuels",
        "80": "fuel ethanol",
        "81": "biomass-based diesel",
    },
    "activity": {"1": "production", "2": "consumption"},
    "parent": {"44": None, "79": None, "80": 79, "81": 79},
}


class TestNum:
    """A measurement cell is a number or it is missing -- never text.

    EIA marks withheld or negligible values with text inside an otherwise
    numeric column. Those markers must not survive into the table, or the
    column stops being numeric and cannot be sorted or charted.
    """

    @pytest.mark.parametrize("value", [None, ""])
    def test_missing_becomes_none(self, value):
        assert browsers._num(value) is None

    @pytest.mark.parametrize(
        ("value", "expected"), [("1.5", 1.5), (2, 2.0), ("-3", -3.0), (4.25, 4.25)]
    )
    def test_numeric_becomes_float(self, value, expected):
        assert browsers._num(value) == expected

    @pytest.mark.parametrize("marker", ["(s)", "--", "NA", "W", "(*)", "NM"])
    def test_eia_suppression_markers_become_none(self, marker):
        assert browsers._num(marker) is None

    def test_non_scalar_becomes_none(self):
        assert browsers._num(["a"]) is None


class TestSuppressionMarkers:
    """Every International pivot drops EIA's text markers.

    ``series_data/data`` returns ``["(s)", 0.000102]`` and ``["--"]``;
    ``series_data/infographic`` returns the marker as a bare ``value``. Both
    must land as null, not as the string ``(s)`` in a numeric column.
    """

    def test_series_marker_with_an_underlying_value_keeps_the_value(self):
        rows = browsers._intl_series_rows(
            {"INTL.44-1-ABW-QBTU.A": {"2009": ["(s)", 0.0001023642489938382]}}
        )
        assert rows[0]["2009 "] == 0.0001023642489938382

    def test_series_marker_without_a_value_is_null(self):
        rows = browsers._intl_series_rows({"INTL.44-1-ABW-QBTU.A": {"1980": ["--"]}})
        assert rows[0]["1980 "] is None

    @pytest.mark.parametrize("marker", ["(s)", "--"])
    def test_infographic_marker_is_null(self, marker):
        rows = browsers._intl_infographic_rows(
            [
                {
                    "series_id": "INTL.44-1-ASM-QBTU.A",
                    "iso": "ASM",
                    "unit": "QBTU",
                    "frequency": "A",
                    "data": [{"date": 1704067200000, "value": marker}],
                }
            ]
        )
        assert rows[0]["2024 "] is None

    def test_classic_table_marker_is_null(self):
        rows = browsers._table_rows(
            {"ROWS": [{"SERIES_ID": "S", "CHART_NAME": "C", "DATA": {"2024": "(s)"}}]}
        )
        assert rows[0]["2024 "] is None

    def test_no_period_column_holds_text(self):
        payload = {
            "data": {
                "INTL.44-1-ASM-QBTU.A": {"2023": ["(s)"], "2024": ["(s)", 1.7e-05]},
                "INTL.44-1-CSK-QBTU.A": {"2023": ["--"], "2024": ["--"]},
            }
        }
        for row in browsers.rows_from_payload(payload):
            for key, value in row.items():
                if key in ("category", "country", "units", "source_key"):
                    continue
                assert value is None or isinstance(value, float)


class TestFormatPeriod:
    """EIA period codes render as ISO-style strings."""

    def test_six_digits_is_year_month(self):
        assert browsers._format_period("202401") == "2024-01"

    def test_eight_digits_is_a_date(self):
        assert browsers._format_period("20240105") == "2024-01-05"

    def test_bare_year_unchanged(self):
        assert browsers._format_period("2024") == "2024"

    def test_non_numeric_unchanged(self):
        assert browsers._format_period("2024-Q1") == "2024-Q1"


class TestPeriodColumns:
    """Identifiers first, then periods ascending -- matching EIA's CSV export.

    JS ``Object.keys`` floats canonical integer-string keys ahead of text keys,
    so a bare year must not be a canonical integer key or the year columns jump
    in front of the identifier columns in the rendered table.
    """

    def test_bare_years_are_not_canonical_integer_keys(self):
        columns = browsers._period_columns({"2024", "2023"})
        assert columns == [("2023 ", "2023"), ("2024 ", "2024")]
        for label, _ in columns:
            assert str(int(label)) != label

    def test_periods_are_ascending(self):
        columns = browsers._period_columns({"2024", "2022", "2023"})
        assert [raw for _, raw in columns] == ["2022", "2023", "2024"]

    def test_month_and_day_periods_are_not_integer_keys(self):
        assert browsers._period_columns({"202401"}) == [("2024-01", "202401")]
        assert browsers._period_columns({"20240105"}) == [("2024-01-05", "20240105")]

    def test_empty_period_set(self):
        assert browsers._period_columns(set()) == []


class TestFlattenCases:
    """STEO/AEO payloads nest periods under a case id."""

    def test_case_keyed_series_are_merged(self):
        flat = browsers._flatten_cases(
            {"REF2025": {"2024": 1.0}, "HIGH": {"2025": 2.0}}
        )
        assert flat == {"2024": 1.0, "2025": 2.0}

    def test_plain_period_map_passes_through(self):
        assert browsers._flatten_cases({"2024": 1.0}) == {"2024": 1.0}

    def test_empty_passes_through(self):
        assert browsers._flatten_cases({}) == {}


class TestTableRows:
    """The classic TABLEDATA shape used by electricity, coal, STEO and imports."""

    def test_identifier_columns_then_periods(self):
        rows = browsers._table_rows(TABLEDATA)
        assert list(rows[0]) == [
            "category",
            "units",
            "source_key",
            "2024-01",
            "2024-02",
        ]

    def test_labels_units_and_values(self):
        first, second = browsers._table_rows(TABLEDATA)
        assert first["category"] == "All fuels"
        assert first["units"] == "million kilowatthours"
        assert first["source_key"] == "ELEC.GEN.ALL-US-99.M"
        assert first["2024-01"] == 1000.5
        assert second["category"] == "Coal"
        assert second["units"] == "thousand tons"
        assert second["2024-02"] is None

    def test_lowercase_keys_are_accepted(self):
        rows = browsers._table_rows(
            {
                "units": "u",
                "rows": [
                    {"rowId": "R1", "chart_name": "Low", "data": {"2024": "1"}},
                ],
            }
        )
        assert rows == [
            {"category": "Low", "units": "u", "source_key": "R1", "2024 ": 1.0}
        ]

    def test_rows_given_as_a_mapping(self):
        rows = browsers._table_rows(
            {"ROWS": {"a": {"MSN": "TETCB", "DESCRIPTION": "T", "DATA": {"2024": 1}}}}
        )
        assert rows[0]["source_key"] == "TETCB"

    def test_case_nested_data_is_flattened(self):
        rows = browsers._table_rows(
            {
                "ROWS": [
                    {
                        "SERIES_ID": "S",
                        "CHART_NAME": "C",
                        "DATA": {"REF": {"2024": 1.0}},
                    }
                ]
            }
        )
        assert rows[0]["2024 "] == 1.0

    def test_non_dict_entries_skipped(self):
        assert browsers._table_rows({"ROWS": ["junk", None]}) == []

    def test_missing_data_yields_no_period_columns(self):
        rows = browsers._table_rows({"ROWS": [{"SERIES_ID": "S", "CHART_NAME": "C"}]})
        assert rows == [{"category": "C", "units": "", "source_key": "S"}]

    def test_pinned_name_used_as_a_last_resort_label(self):
        rows = browsers._table_rows(
            {"ROWS": [{"SERIES_ID": "S", "PINNED_NAME": "Pinned", "DATA": {}}]}
        )
        assert rows[0]["category"] == "Pinned"


class TestSeriesRows:
    """The ``{series_id, data}`` shape used by SEDS and the state profiles."""

    def test_pairs_data_becomes_period_columns(self):
        rows = browsers._series_rows(SERIES_PAYLOAD["series"])
        assert rows == [
            {
                "category": "Total energy consumed",
                "units": "billion Btu",
                "source_key": "SEDS.TETCB.CA.A",
                "2022 ": 7000.0,
                "2023 ": 7100.0,
            }
        ]

    def test_mapping_data_is_accepted(self):
        rows = browsers._series_rows(
            [{"seriesID": "S", "description": "D", "unit": "u", "data": {"2024": "3"}}]
        )
        assert rows[0]["2024 "] == 3.0
        assert rows[0]["units"] == "u"

    def test_series_id_is_the_fallback_label(self):
        rows = browsers._series_rows([{"id": "S1", "data": {"2024": 1}}])
        assert rows[0]["category"] == "S1"

    def test_series_without_data_is_skipped(self):
        assert browsers._series_rows([{"series_id": "S"}]) == []

    def test_malformed_points_are_skipped(self):
        rows = browsers._series_rows([{"series_id": "S", "data": [["2024"], 5]}])
        assert rows == [{"category": "S", "units": "", "source_key": "S"}]

    def test_non_dict_entries_skipped(self):
        assert browsers._series_rows(["junk"]) == []


class TestRankingRows:
    """State Energy Profiles rankings are one row per state."""

    def test_rank_period_and_value(self):
        rows = browsers._ranking_rows(RANKING_PAYLOAD["series"])
        assert rows[0] == {
            "category": "Texas",
            "units": "Total energy consumed",
            "source_key": "SEDS.TETCB.TX.A",
            "rank": 1.0,
            "period": "2023",
            "value": 12000.5,
        }
        assert rows[1]["rank"] == 2.0

    def test_state_id_is_the_fallback_label(self):
        rows = browsers._ranking_rows([{"stateId": "TX"}])
        assert rows[0]["category"] == "TX"

    def test_non_dict_entries_skipped(self):
        assert browsers._ranking_rows([None]) == []


class TestStateMapRows:
    """A US map payload is ``{code: {state: value}}`` and pivots to one row per state."""

    def test_state_and_series_codes_are_named_from_the_catalog(self):
        rows = browsers._state_map_rows(STATE_MAP_PAYLOAD["series"])
        assert rows == [
            {
                "category": "Texas",
                "state": "TX",
                "Total energy consumption": 12000.0,
                "All petroleum products total consumption": 4000.0,
            },
            {
                "category": "California",
                "state": "CA",
                "Total energy consumption": 7100.0,
                "All petroleum products total consumption": 2000.0,
            },
        ]

    def test_unknown_codes_fall_back_to_themselves(self):
        rows = browsers._state_map_rows({"A": {"TX": 1}, "B": {"ZZ": 2}})
        assert rows == [
            {"category": "Texas", "state": "TX", "A": 1.0, "B": None},
            {"category": "ZZ", "state": "ZZ", "A": None, "B": 2.0},
        ]

    def test_non_mapping_codes_ignored(self):
        assert browsers._state_map_rows({"year": 2023}) == []


class TestInternationalHelpers:
    """International encodes region and unit in the series id, values in pairs."""

    def test_value_takes_the_unrounded_element(self):
        assert browsers._intl_value([96.0, 96.34]) == 96.34

    def test_string_marker_is_missing(self):
        assert browsers._intl_value([96.0, "--"]) is None

    def test_scalar_passes_through(self):
        assert browsers._intl_value(5) == 5

    def test_empty_point_is_missing(self):
        assert browsers._intl_value([]) is None

    def test_series_id_splits_into_product_activity_region_and_unit(self):
        assert browsers._parse_intl_id("INTL.44-1-USA-QBTU.A") == (
            "44",
            "1",
            "USA",
            "QBTU",
        )

    def test_series_id_without_the_prefix(self):
        assert browsers._parse_intl_id("44-1-CHN-QBTU.A") == ("44", "1", "CHN", "QBTU")

    def test_series_id_without_a_product(self):
        assert browsers._parse_intl_id("USA-QBTU.A") == ("", "", "USA", "QBTU")

    def test_unparseable_series_id(self):
        assert browsers._parse_intl_id("INTL.X") == ("", "", "", "")

    @pytest.mark.parametrize(
        ("frequency", "expected"),
        [("A", "2023"), ("M", "202301"), ("D", "20230101"), ("Q", "2023-Q1")],
    )
    def test_epoch_renders_per_frequency(self, frequency, expected):
        assert browsers._epoch_period(1672531200000, frequency) == expected

    @pytest.mark.parametrize("stamp", [None, "abc", 10**20])
    def test_bad_epoch_yields_no_period(self, stamp):
        assert browsers._epoch_period(stamp, "A") == ""

    def test_infographic_shape_detected(self):
        assert browsers._is_intl_infographic(INTL_OVERVIEW_PAYLOAD["data"]) is True

    @pytest.mark.parametrize(
        "data", [[], [{"series_id": "S"}], [{"data": []}], {"a": 1}, None]
    )
    def test_other_shapes_are_not_infographic(self, data):
        assert browsers._is_intl_infographic(data) is False


class TestInternationalRows:
    """International rows must read like the table: one row per product per country.

    The table lists three rows under each country -- ``Production`` for the
    top-level product, then each child product by name -- so the row label is
    the product (or the activity it totals) and the country is its own column.
    """

    def test_row_label_is_the_product_and_country_is_its_own_column(self):
        rows = browsers._intl_series_rows(BIOFUELS_PAYLOAD["data"], LABELS)
        assert [(row["category"], row["country"]) for row in rows] == [
            ("Production", "Aruba"),
            ("Fuel ethanol", "Aruba"),
            ("Biomass-based diesel", "Aruba"),
        ]
        assert {row["units"] for row in rows} == {"Mb/d"}

    def test_top_level_product_is_labelled_by_its_activity(self):
        rows = browsers._intl_series_rows(
            {"INTL.44-2-USA-QBTU.A": {"2023": [96.0, 96.34]}}, LABELS
        )
        assert rows[0]["category"] == "Consumption"

    def test_series_rows_are_labelled_with_country_and_unit_names(self):
        rows = browsers._intl_series_rows(INTL_SERIES_PAYLOAD["data"], LABELS)
        assert rows[0] == {
            "category": "Production",
            "country": "United States",
            "units": "quad Btu",
            "source_key": "INTL.44-1-USA-QBTU.A",
            "2022 ": 95.12,
            "2023 ": 96.34,
        }
        assert rows[1]["country"] == "China"

    def test_series_rows_fall_back_to_codes_without_label_maps(self):
        rows = browsers._intl_series_rows(INTL_SERIES_PAYLOAD["data"])
        assert rows[0]["country"] == "USA"
        assert rows[0]["units"] == "QBTU"
        assert rows[0]["category"] == "INTL.44-1-USA-QBTU.A"

    def test_series_rows_skip_non_mapping_entries(self):
        assert browsers._intl_series_rows({"INTL.X": "junk"}) == []

    def test_overview_rows_are_labelled_and_keyed_by_period(self):
        rows = browsers._intl_infographic_rows(INTL_OVERVIEW_PAYLOAD["data"], LABELS)
        assert rows == [
            {
                "category": "Production",
                "country": "United States",
                "units": "quad Btu",
                "source_key": "INTL.44-1-USA-QBTU.A",
                "2023 ": 96.34,
                "2024 ": 97.5,
            }
        ]

    def test_overview_rows_fall_back_to_the_entry_name(self):
        rows = browsers._intl_infographic_rows(
            [{"series_id": "S", "name": "Kuwait", "data": [], "frequency": "A"}]
        )
        assert rows[0]["country"] == "Kuwait"
        assert rows[0]["category"] == "S"

    def test_overview_rows_skip_malformed_entries(self):
        rows = browsers._intl_infographic_rows(
            ["junk", {"series_id": "S", "data": [1]}]
        )
        assert rows == [
            {"category": "S", "country": "", "units": "", "source_key": "S"}
        ]


class TestRowsFromPayload:
    """Every browser payload shape dispatches to the right pivot."""

    def test_tabledata(self):
        rows = browsers.rows_from_payload({"TABLEDATA": TABLEDATA})
        assert rows[0]["category"] == "All fuels"

    def test_lowercase_tabledata(self):
        rows = browsers.rows_from_payload({"tabledata": TABLEDATA})
        assert rows[0]["category"] == "All fuels"

    def test_seriesdata(self):
        rows = browsers.rows_from_payload({"SERIESDATA": TABLEDATA})
        assert rows[0]["category"] == "All fuels"

    def test_viewsdata(self):
        rows = browsers.rows_from_payload({"VIEWSDATA": TABLEDATA})
        assert rows[0]["category"] == "All fuels"

    def test_seriesdata_without_rows_is_ignored(self):
        assert browsers.rows_from_payload({"SERIESDATA": {"ROWS": []}}) == []

    def test_table_data_list(self):
        rows = browsers.rows_from_payload(
            {"TABLE_DATA": [{"seriesID": "S", "data": {"2024": 1}}]}
        )
        assert rows[0]["source_key"] == "S"

    def test_series_list_of_series(self):
        rows = browsers.rows_from_payload(SERIES_PAYLOAD)
        assert rows[0]["category"] == "Total energy consumed"

    def test_series_list_of_rankings(self):
        rows = browsers.rows_from_payload(RANKING_PAYLOAD)
        assert rows[0]["rank"] == 1.0

    def test_series_mapping_is_a_state_map(self):
        rows = browsers.rows_from_payload(STATE_MAP_PAYLOAD)
        assert rows[0]["category"] == "Texas"
        assert rows[0]["state"] == "TX"

    def test_international_series(self):
        rows = browsers.rows_from_payload(INTL_SERIES_PAYLOAD)
        assert rows[0]["source_key"] == "INTL.44-1-USA-QBTU.A"

    def test_international_overview(self):
        rows = browsers.rows_from_payload(INTL_OVERVIEW_PAYLOAD)
        assert rows[0]["country"] == "USA"
        assert rows[0]["source_key"] == "INTL.44-1-USA-QBTU.A"

    def test_plain_list_of_records(self):
        assert browsers.rows_from_payload({"data": [{"a": 1}, "junk"]}) == [{"a": 1}]

    def test_bare_list_of_records(self):
        assert browsers.rows_from_payload([{"a": 1}]) == [{"a": 1}]

    def test_list_of_payloads_is_flattened(self):
        rows = browsers.rows_from_payload([{"TABLEDATA": TABLEDATA}])
        assert rows[0]["category"] == "All fuels"

    def test_unrecognised_payload_is_empty(self):
        assert browsers.rows_from_payload("nope") == []
        assert browsers.rows_from_payload({}) == []
        assert browsers.rows_from_payload({"data": None}) == []


class TestSteoTable:
    """STEO has no TABLEDATA: its table is VIEWSDATA, not the pinned SERIESDATA."""

    PAYLOAD = {
        "VIEWSDATA": {
            "ROWS": [
                {"CHART_NAME": "Energy Production", "HAS_DATA": 0, "LEVEL": 1},
                {
                    "CHART_NAME": "U.S. Crude Oil Production",
                    "SERIES_ID": "COPRPUS",
                    "UNITS": "million barrels per day",
                    "DATA": {"2025": "13.6"},
                },
            ]
        },
        "SERIESDATA": {
            "ROWS": [
                {
                    "CHART_NAME": "Biodiesel Net Imports",
                    "SERIES_ID": "BDNIPUS",
                    "UNITS": "million barrels per day",
                    "DATA": {"2025": "0.1"},
                }
            ]
        },
    }

    def test_the_view_is_the_table_not_the_pinned_series(self):
        rows = browsers.rows_from_payload(self.PAYLOAD)
        assert [row["source_key"] for row in rows] == ["", "COPRPUS"]

    def test_pinned_series_are_the_table_when_no_view_is_selected(self):
        payload = {"VIEWSDATA": {"ROWS": []}, "SERIESDATA": self.PAYLOAD["SERIESDATA"]}
        rows = browsers.rows_from_payload(payload)
        assert [row["source_key"] for row in rows] == ["BDNIPUS"]


class TestImportsRows:
    """Imports ships only series ids; the browser builds every label from config."""

    LABELS = {
        "origin": {
            "REG": {"WORLD": "World"},
            "OPN": {"Y": "OPEC", "N": "Non-OPEC"},
            "CTY": {},
        },
        "destination": {"RP": {"3": "PADD3 (Gulf Coast)"}, "RS": {"US": "Total U.S."}},
        "grade": {"LSO": "Light Sour", "LSW": "Light Sweet"},
    }
    RECORDS = [
        {"seriesID": "PET_IMPORTS.WORLD-RP_3-LSO.M", "data": {"200901": 9091}},
        {"seriesID": "PET_IMPORTS.OPN_Y-RP_3-LSW.M", "data": {"200901": 20089}},
    ]

    def test_rows_are_named_the_way_the_table_names_them(self):
        rows = browsers._imports_rows(self.RECORDS, self.LABELS)
        assert rows[0]["category"] == (
            "Imports of Light Sour from World to PADD3 (Gulf Coast), monthly"
        )
        assert rows[0]["origin"] == "World"
        assert rows[0]["destination"] == "PADD3 (Gulf Coast)"
        assert rows[0]["grade"] == "Light Sour"
        assert rows[0]["units"] == "thousand barrels"
        assert rows[0]["2009-01"] == 9091.0

    def test_typed_origin_prefix_is_resolved(self):
        rows = browsers._imports_rows(self.RECORDS, self.LABELS)
        assert rows[1]["origin"] == "OPEC"
        assert rows[1]["grade"] == "Light Sweet"

    def test_annual_series_says_annual(self):
        rows = browsers._imports_rows(
            [{"seriesID": "PET_IMPORTS.WORLD-RS_US-ALL.A", "data": {"2024": 1}}],
            self.LABELS,
        )
        assert rows[0]["category"] == (
            "Imports of all grades from World to Total U.S., annual"
        )

    def test_unknown_codes_fall_back_to_themselves(self):
        rows = browsers._imports_rows(
            [{"seriesID": "PET_IMPORTS.ZZ-YY_9-QQ.M", "data": {}}], self.LABELS
        )
        assert rows[0]["origin"] == "ZZ"
        assert rows[0]["destination"] == "YY_9"
        assert rows[0]["grade"] == "QQ"

    def test_unparseable_series_id_still_yields_a_row(self):
        rows = browsers._imports_rows([{"seriesID": "BROKEN"}], self.LABELS)
        assert rows[0]["category"] == "BROKEN"
        assert rows[0]["source_key"] == "BROKEN"

    def test_non_dict_entries_skipped(self):
        assert browsers._imports_rows(["junk"], self.LABELS) == []


class TestNgqsRows:
    """NGQS records are keyed by short grid field ids; the payload names them."""

    PAYLOAD = {
        "columns": [
            {"headerName": "Area", "field": "a"},
            {"headerName": "Company", "field": "b"},
            {"headerName": "Item", "field": "c"},
            {"headerName": 2023, "field": "y2023", "numeric": True},
            {"width": 10},
        ],
        "data": [
            {
                "a": " U.S. Total",
                "b": " Total of All Companies",
                "c": "Production Volume",
                "y2023": 2389716115,
            },
            "junk",
        ],
    }

    def test_grid_headers_become_the_columns(self):
        rows = browsers._ngqs_rows(self.PAYLOAD)
        assert rows == [
            {
                "Area": " U.S. Total",
                "Company": " Total of All Companies",
                "Item": "Production Volume",
                "2023 ": 2389716115.0,
            }
        ]

    def test_year_headers_are_not_canonical_integer_keys(self):
        assert "2023 " in browsers._ngqs_rows(self.PAYLOAD)[0]

    def test_missing_columns_yield_nothing(self):
        assert browsers._ngqs_rows({"data": []}) == []
        assert browsers._ngqs_rows({"columns": []}) == []


class TestStatesTableRows:
    """The State Profiles table keeps its values outside the series metadata."""

    PAYLOAD = {
        "request": "SEDS.TETCB.TX.A",
        "series": [
            {
                "series_id": "SEDS.TETCB.TX.A",
                "name": "SEDS.TETCB.TX.A, annual",
                "units": "Billion Btu",
                "column_index": "column_0",
            }
        ],
        "data": [
            {"time": "2024", "column_0": 14536890},
            {"time": "2023", "column_0": 14149656},
            {"time": "", "column_0": 1},
        ],
    }

    def test_values_are_joined_to_their_series_by_column_index(self):
        rows = browsers.rows_from_payload(self.PAYLOAD)
        assert rows == [
            {
                "category": "SEDS.TETCB.TX.A, annual",
                "units": "Billion Btu",
                "source_key": "SEDS.TETCB.TX.A",
                "2023 ": 14149656.0,
                "2024 ": 14536890.0,
            }
        ]

    def test_series_without_values_is_not_mistaken_for_a_ranking(self):
        rows = browsers.rows_from_payload(self.PAYLOAD)
        assert "rank" not in rows[0]

    def test_series_metadata_without_a_column_index_is_skipped(self):
        payload = dict(self.PAYLOAD, series=[{"column_index": "column_0"}, "junk"])
        rows = browsers._states_table_rows(payload["series"], payload["data"])
        assert len(rows) == 1
        assert rows[0]["category"] == ""

    def test_non_dict_records_are_skipped(self):
        rows = browsers._states_table_rows(
            self.PAYLOAD["series"], ["junk", {"time": "2024", "column_0": 1}]
        )
        assert rows[0]["2024 "] == 1.0


class TestParseInlineTable:
    """Total Energy ships its table inline as ``sampleData``."""

    def test_extracts_and_pivots(self):
        html = f"<script>var sampleData = {json.dumps(TABLEDATA)};</script>"
        rows = browsers.parse_inline_table(html)
        assert rows[0]["category"] == "All fuels"

    def test_absent_marker_yields_nothing(self):
        assert browsers.parse_inline_table("<html></html>") == []

    def test_malformed_json_yields_nothing(self):
        assert browsers.parse_inline_table("sampleData = {not json") == []

    def test_non_object_payload_yields_nothing(self):
        assert browsers.parse_inline_table('sampleData = "x" {}') == []


class TestTableParamsFromHash:
    """Classic browsers encode the current view in the URL fragment."""

    def test_builds_aggregate_params(self):
        params = browsers.table_params_from_hash(
            "#/topic/0?agg=0,1&geo=g&freq=A&ctype=linechart&linechart=ELEC.X&rtype=s"
        )
        assert params["method"] == browsers._TABLE_METHOD
        assert params["topic"] == "0"
        assert params["agg"] == "0,1"
        assert params["geo"] == "g"
        assert params["freq"] == "A"
        assert params["rtype"] == "s"
        assert params["ids"] == "ELEC.X"

    def test_pin_wins_over_the_chart_selection(self):
        params = browsers.table_params_from_hash(
            "#/topic/0?pin=PINNED&ctype=linechart&linechart=OTHER"
        )
        assert params["ids"] == "PINNED"

    def test_defaults_applied_when_absent(self):
        params = browsers.table_params_from_hash("#/topic/2?geo=g")
        assert params["freq"] == "M"
        assert params["rtype"] == "s"
        assert params["ids"] == ""

    def test_chart_keys_are_not_forwarded_as_filters(self):
        params = browsers.table_params_from_hash("#/topic/0?ctype=map&map=X")
        assert "map" not in params
        assert "ctype" not in params

    @pytest.mark.parametrize(
        "fragment", ["", "no-hash", "#/nowhere?x=1", "#/topic/0", "#/topic/0?"]
    )
    def test_unusable_fragments_yield_none(self, fragment):
        assert browsers.table_params_from_hash(fragment) is None

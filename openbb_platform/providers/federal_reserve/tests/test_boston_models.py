"""Tests for the Boston Fed regional models."""

import base64
import json
from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.boston_economic_indicators import (
    FederalReserveBostonEconomicIndicatorsData,
    FederalReserveBostonEconomicIndicatorsFetcher,
)
from openbb_federal_reserve.utils import boston


def _series(
    name: str,
    description: str | None,
    frequency: int | None,
    func: str | None,
    points: list[tuple[str, float]],
    geography: str | None = None,
    data_type: str | None = None,
) -> dict:
    """Build a single NEEI geography series dict."""
    return {
        "name": name,
        "description": description,
        "geography": geography,
        "dataType": data_type,
        "originalFrequency": frequency,
        "func": func,
        "sourceName": "Bureau of Labor Statistics/Haver Analytics",
        "dataPoints": [{"date": d, "nSeriesData": v} for d, v in points],
    }


def _island(label: str, series: list[dict]) -> str:
    """Build a chart island: a tab anchor plus its base64 series-data div."""
    encoded = base64.b64encode(json.dumps(series).encode("utf-8")).decode("utf-8")
    return (
        f'<a tabindex="1" href="#">{label}</a>'
        f'<div class="hidden series-data">{encoded}</div>'
    )


_PAGE = (
    "<html><body>"
    + "".join(
        [
            _island(
                "Payroll Employment",
                [
                    _series(
                        "USLNAGRA",
                        "All Employees: Total Nonfarm, United States (SA, Thous)",
                        40,
                        "YRYR%",
                        [("2026-04-01", 0.18), ("2026-05-01", 0.23)],
                    ),
                    _series(
                        "C1LNAGRA",
                        "All Employees: Total Nonfarm, New England (SA, Thous)",
                        40,
                        "YRYR%",
                        [("2026-04-01", -0.05), ("2026-05-01", -0.08)],
                    ),
                ],
            ),
            _island(
                "Consumer Price Index",
                [
                    _series(
                        "UIN",
                        "CPI-U: All Items (NSA, 1982-84=100)",
                        40,
                        "YRYR%",
                        [("2026-05-01", 4.25)],
                    ),
                    _series(
                        "UIC1N",
                        "CPI-U: New England: All Items (NSA, Dec-17=100)",
                        40,
                        "YRYR%",
                        [("2026-05-01", 4.64)],
                    ),
                ],
            ),
            _island(
                "Home Price Index",
                [
                    _series(
                        "C1HPI",
                        "FHFA House Price Index: New England (Q1-80=100)",
                        30,
                        "YRYR%",
                        [("2026-01-01", 4.97)],
                    ),
                ],
            ),
            _island(
                "Unemployment Rates",
                [
                    _series(
                        "URMA",
                        "Unemployment Rate, Massachusetts (SA, %)",
                        40,
                        None,
                        [("2026-05-01", 4.3)],
                        data_type="%",
                    ),
                    _series(
                        "URUS",
                        "Unemployment Rate, United States (SA, %)",
                        40,
                        None,
                        [("2026-05-01", 4.2)],
                        data_type="%",
                    ),
                ],
            ),
            _island(
                "Initial Claims",
                [
                    _series(
                        "USLIC",
                        "Unemploy Ins: Initial Claims, State Prog Wkly Avg,"
                        " United States (SA, Persons)",
                        40,
                        "index",
                        [("2026-05-01", 59.45)],
                        geography="111",
                        data_type="Units",
                    ),
                    _series(
                        "MALIC",
                        "Unemploy Ins: Initial Claims, State Prog Wkly Avg,"
                        " Massachusetts (SA, Persons)",
                        40,
                        "index",
                        [("2026-05-01", 79.43)],
                        geography="25",
                        data_type="Units",
                    ),
                ],
            ),
            _island(
                "Construction Contracts (Dodge)",
                [
                    _series(
                        "US",
                        None,
                        None,
                        None,
                        [("2026-02-01", 474.1)],
                        data_type="INDEX",
                    ),
                    _series(
                        "MA",
                        None,
                        None,
                        None,
                        [("2026-02-01", 88.2)],
                        data_type="INDEX",
                    ),
                ],
            ),
        ]
    )
    + "</body></html>"
)


class TestEconomicIndicators:
    """Tests for the NEEI economic indicators fetcher."""

    def test_default_returns_all_geographies(self, monkeypatch):
        """The default indicator pivots every geography into one row per date."""
        monkeypatch.setattr(boston, "fetch_page", lambda: _PAGE)
        query = FederalReserveBostonEconomicIndicatorsFetcher.transform_query(
            {"indicator": "payroll_employment"}
        )
        rows = FederalReserveBostonEconomicIndicatorsFetcher.extract_data(query, None)
        result = FederalReserveBostonEconomicIndicatorsFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveBostonEconomicIndicatorsData) for r in result
        )
        assert [r.date for r in result] == [date(2026, 4, 1), date(2026, 5, 1)]
        national = "United States (Y/Y %)"
        regional = "New England (Y/Y %)"
        first = result[0].model_dump()
        assert set(first) == {"date", national, regional}
        assert first[national] == 0.18
        assert first[regional] == -0.05

    def test_start_date_filter(self, monkeypatch):
        """The start_date filter narrows the pivot to the bounded observations."""
        monkeypatch.setattr(boston, "fetch_page", lambda: _PAGE)
        query = FederalReserveBostonEconomicIndicatorsFetcher.transform_query(
            {"indicator": "payroll_employment", "start_date": "2026-05-01"}
        )
        rows = FederalReserveBostonEconomicIndicatorsFetcher.extract_data(query, None)
        result = FederalReserveBostonEconomicIndicatorsFetcher.transform_data(
            query, rows
        )
        regional = "New England (Y/Y %)"
        assert len(result) == 1
        assert result[0].date == date(2026, 5, 1)
        assert result[0].model_dump()[regional] == -0.08

    def test_level_series_pivots_into_geography_column(self, monkeypatch):
        """A one-per-geography level series carries its value under its geography."""
        monkeypatch.setattr(boston, "fetch_page", lambda: _PAGE)
        query = FederalReserveBostonEconomicIndicatorsFetcher.transform_query(
            {"indicator": "unemployment_rates"}
        )
        rows = FederalReserveBostonEconomicIndicatorsFetcher.extract_data(query, None)
        result = FederalReserveBostonEconomicIndicatorsFetcher.transform_data(
            query, rows
        )
        assert len(result) == 1
        assert result[0].model_dump()["Massachusetts (SA, %)"] == 4.3

    def test_description_less_series_pivot_by_geography(self, monkeypatch):
        """Description-less Construction Contracts pivot under their geography name."""
        monkeypatch.setattr(boston, "fetch_page", lambda: _PAGE)
        query = FederalReserveBostonEconomicIndicatorsFetcher.transform_query(
            {"indicator": "construction_contracts_dodge"}
        )
        rows = FederalReserveBostonEconomicIndicatorsFetcher.extract_data(query, None)
        result = FederalReserveBostonEconomicIndicatorsFetcher.transform_data(
            query, rows
        )
        assert len(result) == 1
        row = result[0].model_dump()
        assert row["date"] == date(2026, 2, 1)
        assert row["United States"] == 474.1
        assert row["Massachusetts"] == 88.2

    def test_index_series_label_marks_index_and_drops_unit(self, monkeypatch):
        """An index series drops the raw unit parenthetical for an ``(Index)`` mark."""
        monkeypatch.setattr(boston, "fetch_page", lambda: _PAGE)
        query = FederalReserveBostonEconomicIndicatorsFetcher.transform_query(
            {"indicator": "initial_claims"}
        )
        rows = FederalReserveBostonEconomicIndicatorsFetcher.extract_data(query, None)
        assert {r["geography"] for r in rows} == {"ma", "us"}
        assert all(r["transform"] == "index" and r["unit"] == "index" for r in rows)
        result = FederalReserveBostonEconomicIndicatorsFetcher.transform_data(
            query, rows
        )
        columns = set(result[0].model_dump())
        national = "United States (Index)"
        regional = "Massachusetts (Index)"
        assert columns == {"date", national, regional}
        assert "Persons" not in national
        assert result[0].model_dump()[national] == 59.45
        assert result[0].model_dump()[regional] == 79.43

    def test_end_date_filter(self, monkeypatch):
        """The end_date filter drops observations after the bound."""
        monkeypatch.setattr(boston, "fetch_page", lambda: _PAGE)
        query = FederalReserveBostonEconomicIndicatorsFetcher.transform_query(
            {"indicator": "payroll_employment", "end_date": "2026-04-30"}
        )
        rows = FederalReserveBostonEconomicIndicatorsFetcher.extract_data(query, None)
        result = FederalReserveBostonEconomicIndicatorsFetcher.transform_data(
            query, rows
        )
        assert [r.date for r in result] == [date(2026, 4, 1)]

    def test_empty_page_raises(self, monkeypatch):
        """A page with no matching island raises ``EmptyDataError``."""
        monkeypatch.setattr(boston, "fetch_page", lambda: "<html></html>")
        query = FederalReserveBostonEconomicIndicatorsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveBostonEconomicIndicatorsFetcher.extract_data(query, None)


class TestResolveGeography:
    """Tests for the geography resolver's identification order."""

    def test_numeric_code_takes_priority(self):
        """A known numeric geography code resolves before description or name."""
        series = {"geography": "25", "description": "ignored", "name": "ignored"}
        assert boston._resolve_geography(series) == "ma"

    def test_unresolvable_series_returns_none(self):
        """A series with no known code, US marker, or name prefix resolves to None."""
        series = {"geography": "9999", "description": "mystery measure", "name": "zzz"}
        assert boston._resolve_geography(series) is None


class TestBostonHelpers:
    """Tests for the NEEI page-decoding and series helper functions."""

    def test_fetch_page_returns_html(self, monkeypatch):
        """``fetch_page`` returns the body of a successful request."""

        class _Response:
            text = "<html>page</html>"

            def raise_for_status(self):
                return None

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda url: _Response(),
        )
        assert boston.fetch_page() == "<html>page</html>"

    def test_parse_islands_skips_unlabeled_and_undecodable(self):
        """Blocks without a preceding label or with bad base64 are skipped."""
        html = (
            '<div class="hidden series-data">not-base64!!</div>'
            '<a href="#">Payroll Employment</a>'
            '<div class="hidden series-data">@@@</div>'
        )
        assert boston.parse_islands(html) == {}

    def test_frequency_quarterly(self):
        """A frequency code of 30 maps to quarterly."""
        assert boston._frequency_for({"originalFrequency": 30}) == "quarterly"

    def test_unit_for_index_func_overrides_datatype(self):
        """An index transform reports an ``index`` unit, not the source datatype."""
        assert boston._unit_for({"func": "index", "dataType": "Units"}) == "index"

    def test_unit_for_yoy_func_is_percent(self):
        """A year-over-year transform reports a ``percent`` unit."""
        assert boston._unit_for({"func": "YRYR%", "dataType": "Units"}) == "percent"

    def test_unit_for_level_uses_datatype(self):
        """A level series reports the source datatype's unit."""
        assert boston._unit_for({"func": None, "dataType": "US$"}) == "dollars"

    def test_unit_for_missing_datatype_is_none(self):
        """A level series without a datatype reports no unit."""
        assert boston._unit_for({"func": None}) is None

    def test_column_label_marks_transform_and_strips_unit(self):
        """A transformed series drops its unit parenthetical for a transform mark."""
        label = boston._column_label(
            "Permits: New Privately Owned Housing Units, U.S. (SA, Units)",
            "USHP",
            "index",
        )
        assert label == "Permits: New Privately Owned Housing Units, U.S. (Index)"

    def test_column_label_level_keeps_description(self):
        """A level series keeps its description unchanged as the column label."""
        label = boston._column_label("Unemployment Rate, US (SA, %)", "URUS", "level")
        assert label == "Unemployment Rate, US (SA, %)"

    def test_column_label_falls_back_to_name(self):
        """A description-less series falls back to its short name code."""
        assert boston._column_label(None, "USTOTHER", "level") == "USTOTHER"

    def test_clean_description_strips_leading_units_and_boilerplate(self):
        """A stray ``Units`` token and the measure-class prefix are both removed."""
        assert (
            boston._clean_description(
                "Units All Employees: Total Nonagricultural, New Hampshire (SA, Thous.)"
            )
            == "Total Nonagricultural, New Hampshire (SA, Thous.)"
        )
        assert (
            boston._clean_description(
                "Exp Value: CT Total Exports to Belgium (Thous.$)"
            )
            == "CT Total Exports to Belgium (Thous.$)"
        )
        assert (
            boston._clean_description("All Employ: Finance, Insurance, Massachusetts")
            == "Finance, Insurance, Massachusetts"
        )

    def test_geography_label_transform_uses_geography_and_marker(self):
        """A transformed one-per-geography series labels by geography plus marker."""
        label = boston._geography_label(
            "ma",
            "All Employees: Total Nonagricultural, Massachusetts (SA, Thous)",
            "MALNAGRA",
            "year_over_year_percent",
        )
        assert label == "Massachusetts (Y/Y %)"

    def test_geography_label_level_keeps_unit_parenthetical(self):
        """A level one-per-geography series keeps the description's unit suffix."""
        label = boston._geography_label(
            "us", "Unemployment Rate, United States (SA, %)", "USRA", "level"
        )
        assert label == "United States (SA, %)"

    def test_geography_label_level_without_unit_is_bare_geography(self):
        """A description-less level series labels by the bare geography name."""
        assert boston._geography_label("us", None, "US", "level") == "United States"

    def test_geography_label_unresolved_falls_back_to_description(self):
        """An unresolved geography falls back to the cleaned description label."""
        label = boston._geography_label(
            None, "Some Measure, Region X (SA, %)", "XYZ", "year_over_year_percent"
        )
        assert label == "Some Measure, Region X (Y/Y %)"

    def test_strip_shared_label_prefix_drops_redundant_measure(self):
        """A measure prefix shared by every column is removed in place."""
        records = [
            {"label": "JOLTS: Job Openings Rate: Construction (EOP, SA, %)"},
            {"label": "JOLTS: Job Openings Rate: Government (EOP, SA, %)"},
        ]
        boston._strip_shared_label_prefix(records)
        assert [record["label"] for record in records] == [
            "Construction (EOP, SA, %)",
            "Government (EOP, SA, %)",
        ]

    def test_strip_shared_label_prefix_keeps_distinct_geographies(self):
        """Columns sharing no ``": "`` prefix (one geography each) are unchanged."""
        records = [{"label": "Connecticut (Y/Y %)"}, {"label": "Maine (Y/Y %)"}]
        boston._strip_shared_label_prefix(records)
        assert [record["label"] for record in records] == [
            "Connecticut (Y/Y %)",
            "Maine (Y/Y %)",
        ]

    def test_strip_shared_label_prefix_single_column_unchanged(self):
        """A single distinct label has no shared prefix to strip."""
        records = [{"label": "Total (EOP, SA, %)"}, {"label": "Total (EOP, SA, %)"}]
        boston._strip_shared_label_prefix(records)
        assert {record["label"] for record in records} == {"Total (EOP, SA, %)"}

    def test_strip_shared_label_prefix_preserves_prefix_only_column(self):
        """A column equal to the shared prefix is preserved, not emptied."""
        records = [
            {"label": "JOLTS: Job Openings Rate: "},
            {"label": "JOLTS: Job Openings Rate: Total (EOP, SA, %)"},
        ]
        boston._strip_shared_label_prefix(records)
        assert {record["label"] for record in records} == {
            "JOLTS: Job Openings Rate: ",
            "Total (EOP, SA, %)",
        }

    def test_is_geography_mode_true_for_one_per_geography(self):
        """One resolvable series per geography selects geography mode."""
        series_list = [
            {"geography": "25", "func": "YRYR%"},
            {"geography": "33", "func": "YRYR%"},
        ]
        assert boston._is_geography_mode(series_list) is True

    def test_is_geography_mode_false_for_multiple_per_geography(self):
        """Several series in one geography selects description mode."""
        series_list = [
            {"geography": "25", "func": None},
            {"geography": "25", "func": None},
        ]
        assert boston._is_geography_mode(series_list) is False

    def test_is_geography_mode_ignores_unresolvable_series(self):
        """Unresolvable series do not collide, so geography mode is kept."""
        series_list = [
            {"geography": "9999", "description": "mystery", "name": "zzz"},
            {"geography": "9999", "description": "other", "name": "yyy"},
        ]
        assert boston._is_geography_mode(series_list) is True

    def test_unknown_indicator_raises(self):
        """An unknown indicator key raises ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError

        with pytest.raises(OpenBBError):
            boston.fetch_indicator("not_a_chart")

    def test_unknown_geography_raises(self):
        """An unknown geography filter raises ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError

        with pytest.raises(OpenBBError):
            boston.fetch_indicator("payroll_employment", "atlantis")

    def test_fetch_indicator_filters_geography(self, monkeypatch):
        """A geography argument narrows the cached records to the match."""
        from openbb_federal_reserve.utils import cache

        monkeypatch.setattr(boston, "fetch_page", lambda: _PAGE)
        monkeypatch.setattr(cache, "cached", lambda _key, _ttl, producer: producer())
        records = boston.fetch_indicator("payroll_employment", "new_england")
        assert records
        assert {r["geography"] for r in records} == {"new_england"}

    def test_labels_recomputed_from_cached_page(self, monkeypatch):
        """The cache stores the raw page, so label-code changes surface at once."""
        from openbb_federal_reserve.utils import cache

        cached_page = {"html": None}

        def _cached(key, _ttl, producer):
            """Cache only the raw HTML payload, mimicking the page cache."""
            assert key == "boston_neei_page"
            if cached_page["html"] is None:
                cached_page["html"] = producer()
            return cached_page["html"]

        fetch_calls = {"n": 0}

        def _fetch_page():
            """Count upstream fetches to prove the second call hits the cache."""
            fetch_calls["n"] += 1
            return _PAGE

        monkeypatch.setattr(boston, "fetch_page", _fetch_page)
        monkeypatch.setattr(cache, "cached", _cached)

        records = boston.fetch_indicator("payroll_employment")
        assert {r["label"] for r in records} == {
            "United States (Y/Y %)",
            "New England (Y/Y %)",
        }
        assert fetch_calls["n"] == 1

        monkeypatch.setattr(
            boston, "_geography_label", lambda *_args, **_kwargs: "RELABELED"
        )
        records = boston.fetch_indicator("payroll_employment")
        assert {r["label"] for r in records} == {"RELABELED"}
        assert fetch_calls["n"] == 1

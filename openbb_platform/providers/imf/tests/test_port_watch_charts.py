"""Tests for the IMF port-watch chart builders and view wrappers."""

# ruff: noqa: I001

from openbb_imf.views.port_watch_charts import (
    _empty_figure,
    _source_annotation,
    _theme,
    build_activity_chart,
    build_container_metric_chart,
    build_disruption_sankey,
    build_disruptions_map,
    build_monthly_trade_chart,
    clean_records,
    figure_to_json,
    plot_container_metrics,
    plot_country_activity,
    plot_disruption_sankey,
    plot_disruptions_map,
    plot_monthly_trade,
)


class TestThemeAndHelpers:
    """Tests for the theme and small helper functions."""

    def test_theme_dark(self):
        """Dark theme returns the dark color tokens."""
        th = _theme("dark")
        assert th["paper_bgcolor"].startswith("rgba(21")
        assert th["font_color"] == "#ffffff"

    def test_theme_light(self):
        """Anything other than ``dark`` returns the light palette."""
        th = _theme("light")
        assert th["font_color"] == "#000000"

    def test_source_annotation_carries_color(self):
        """The source annotation borrows the theme's annotation color."""
        ann = _source_annotation(_theme("dark"))
        assert ann["font"]["color"] == "#aaaaaa"
        assert "Source: IMF Port Watch" in ann["text"]

    def test_figure_to_json_sets_config(self):
        """``figure_to_json`` wraps the figure with a ``displayModeBar=False`` config."""
        fig = _empty_figure("test")
        payload = figure_to_json(fig)
        assert payload["config"] == {"displayModeBar": False}
        assert "data" in payload and "layout" in payload

    def test_empty_figure_has_no_traces(self):
        """The empty figure carries only the centered annotation."""
        fig = _empty_figure("no data")
        assert fig.data == ()
        assert any("no data" in a.text for a in fig.layout.annotations)

    def test_clean_records_replaces_nan_with_none(self):
        """NaN floats are normalised to ``None``."""
        records = [{"a": float("nan"), "b": 1}]
        assert clean_records(records) == [{"a": None, "b": 1}]


class TestBuildActivityChart:
    """Tests for ``build_activity_chart``."""

    def _sample_rows(self):
        """Two rows with all five vessel-type columns set."""
        return [
            {
                "date": "2024-01-01",
                "portcalls": 30,
                "portcalls_container": 10,
                "portcalls_dry_bulk": 5,
                "portcalls_general_cargo": 4,
                "portcalls_roro": 3,
                "portcalls_tanker": 8,
            },
            {
                "date": "2024-01-02",
                "portcalls": 32,
                "portcalls_container": 11,
                "portcalls_dry_bulk": 5,
                "portcalls_general_cargo": 5,
                "portcalls_roro": 3,
                "portcalls_tanker": 8,
            },
        ]

    def test_full_chart_has_six_traces(self):
        """5 vessel-type stacks plus a 30-day MA overlay."""
        fig = build_activity_chart(self._sample_rows(), "USA", "portcalls")
        assert len(fig.data) == 6
        assert {t.name for t in fig.data[:5]} == {
            "Container",
            "Dry Bulk",
            "General Cargo",
            "Ro-Ro",
            "Tanker",
        }

    def test_empty_rows_returns_empty_figure(self):
        """An empty input produces the empty-state figure."""
        fig = build_activity_chart([], "USA", "portcalls")
        assert fig.data == ()
        assert any("No activity data" in (a.text or "") for a in fig.layout.annotations)

    def test_unknown_metric_falls_back_to_first(self):
        """An unknown metric label falls back to the default ``portcalls``."""
        fig = build_activity_chart(self._sample_rows(), "USA", "not-real")
        assert "Port Calls" in fig.layout.title.text

    def test_missing_date_field_short_circuits(self):
        """Rows without a ``date`` field surface as an empty figure."""
        fig = build_activity_chart([{"portcalls": 1}], "USA", "portcalls")
        assert any("missing a 'date'" in (a.text or "") for a in fig.layout.annotations)

    def test_no_vessel_breakdown_columns_short_circuits(self):
        """If none of the vessel-type breakdown columns exist, return empty."""
        fig = build_activity_chart([{"date": "2024-01-01"}], "USA", "portcalls")
        assert any(
            "breakdown columns" in (a.text or "") for a in fig.layout.annotations
        )


class TestBuildMonthlyTradeChart:
    """Tests for ``build_monthly_trade_chart``."""

    def test_trade_value_line_chart(self):
        """Trade-value metric produces an Imports + Exports line chart."""
        rows = [
            {
                "date": "2024-01-01",
                "value_import_total": 100,
                "value_export_total": 95,
            },
            {
                "date": "2024-02-01",
                "value_import_total": 105,
                "value_export_total": 100,
            },
        ]
        fig = build_monthly_trade_chart(rows, "USA", "trade_value")
        assert len(fig.data) == 2
        assert {t.name for t in fig.data} == {"Imports", "Exports"}

    def test_portcalls_stacked_area(self):
        """The portcalls metric produces five stacked vessel-type traces."""
        rows = [
            {
                "date": "2024-01-01",
                "ais_portcalls_container": 1,
                "ais_portcalls_dry_bulk": 2,
                "ais_portcalls_general_cargo": 3,
                "ais_portcalls_roro": 1,
                "ais_portcalls_tanker": 4,
            }
        ]
        fig = build_monthly_trade_chart(rows, "USA", "portcalls")
        assert len(fig.data) == 5

    def test_invalid_metric_falls_back_to_trade_value(self):
        """Unknown metrics fall back to ``trade_value``."""
        rows = [
            {"date": "2024-01-01", "value_import_total": 1, "value_export_total": 2}
        ]
        fig = build_monthly_trade_chart(rows, "USA", "junk")
        assert "Trade Value" in fig.layout.title.text

    def test_empty_rows_returns_empty_figure(self):
        """No data produces the empty-state figure."""
        fig = build_monthly_trade_chart([], "USA", "trade_value")
        assert fig.data == ()

    def test_missing_date_returns_empty_figure(self):
        """A missing ``date`` field surfaces as an empty figure."""
        fig = build_monthly_trade_chart([{"trade_value": 1}], "USA", "trade_value")
        assert any("missing a 'date'" in (a.text or "") for a in fig.layout.annotations)

    def test_no_matching_columns_returns_empty(self):
        """When no metric columns are present, the empty path triggers."""
        fig = build_monthly_trade_chart([{"date": "2024-01-01"}], "USA", "trade_value")
        assert any(
            "No 'trade_value' columns" in (a.text or "") for a in fig.layout.annotations
        )


class TestBuildContainerMetricChart:
    """Tests for ``build_container_metric_chart``."""

    def test_one_trace_per_port(self):
        """One Scatter trace is emitted per port id with non-empty rows."""
        series = {
            "PORT1": [
                {"date": "2024-01-01", "value": 10},
                {"date": "2024-02-01", "value": 12},
            ],
            "PORT2": [
                {"date": "2024-01-01", "value": 7},
            ],
        }
        fig = build_container_metric_chart(series, {"PORT1": "Shanghai"}, "Port Calls")
        names = {t.name for t in fig.data}
        assert "Shanghai" in names
        assert "PORT2" in names
        assert len(fig.data) == 2

    def test_empty_series_returns_empty_figure(self):
        """An empty series payload yields the empty figure."""
        fig = build_container_metric_chart({}, {}, "Port Calls")
        assert any(
            "No container metric" in (a.text or "") for a in fig.layout.annotations
        )

    def test_series_with_all_empty_returns_empty_figure(self):
        """A dict whose every value is empty also short-circuits."""
        fig = build_container_metric_chart({"PORT1": []}, {}, "Port Calls")
        assert any(
            "No container metric" in (a.text or "") for a in fig.layout.annotations
        )


class TestBuildDisruptionSankey:
    """Tests for ``build_disruption_sankey``."""

    def test_basic_sankey(self):
        """A valid edge list returns a single Sankey trace."""
        rows = [
            {
                "source": 0,
                "target": 1,
                "from_": "A",
                "to_": "B",
                "perc_disaster_capacity": 25.0,
            }
        ]
        fig = build_disruption_sankey(rows, "Event 1")
        assert len(fig.data) == 1
        assert fig.data[0].type == "sankey"

    def test_empty_rows(self):
        """Empty input yields the empty-state figure."""
        fig = build_disruption_sankey([], "Event 1")
        assert fig.data == ()

    def test_malformed_rows_filtered(self):
        """Rows missing required keys are skipped."""
        rows = [{"source": "junk"}, {"perc_disaster_capacity": "n/a"}]
        fig = build_disruption_sankey(rows, "Event")
        assert any(
            "No usable sankey edges" in (a.text or "") for a in fig.layout.annotations
        )


class TestBuildDisruptionsMap:
    """Tests for ``build_disruptions_map``."""

    def test_traces_grouped_by_alert_level(self):
        """One Scattergeo trace per non-empty alert level."""
        rows = [
            {"lat": 1.0, "long": 2.0, "alertlevel": "RED", "n_affectedports": 3},
            {"lat": 3.0, "long": 4.0, "alertlevel": "ORANGE", "n_affectedports": 1},
            {"lat": 5.0, "long": 6.0, "alertlevel": "GREEN", "n_affectedports": 2},
        ]
        fig = build_disruptions_map(rows)
        names = {t.name for t in fig.data}
        assert names == {"Red", "Orange", "Green"}

    def test_other_alert_levels_grouped(self):
        """Rows with non-standard alert levels go into an ``Other`` trace."""
        rows = [{"lat": 1.0, "long": 2.0, "alertlevel": "PURPLE", "n_affectedports": 1}]
        fig = build_disruptions_map(rows)
        assert any(t.name == "Other" for t in fig.data)

    def test_empty_rows(self):
        """Empty input yields the empty figure."""
        fig = build_disruptions_map([])
        assert fig.data == ()

    def test_missing_lat_long_returns_empty(self):
        """If no row has lat/long, the helper falls back to the empty state."""
        fig = build_disruptions_map([{"alertlevel": "RED"}])
        assert any(
            "No georeferenced disruptions" in (a.text or "")
            for a in fig.layout.annotations
        )

    def test_lat_long_all_nan_returns_empty(self):
        """Rows with present-but-NaN lat/long collapse to the empty state."""
        rows = [{"lat": None, "long": None, "alertlevel": "RED"}]
        fig = build_disruptions_map(rows)
        assert any(
            "No georeferenced disruptions" in (a.text or "")
            for a in fig.layout.annotations
        )

    def test_unknown_alertlevel_column_missing(self):
        """When the ``alertlevel`` column is absent, rows still render."""
        rows = [
            {"lat": 1.0, "long": 2.0, "n_affectedports": 2},
            {"lat": 3.0, "long": 4.0, "n_affectedports": 1},
        ]
        fig = build_disruptions_map(rows)
        assert any(t.name == "Other" for t in fig.data)

    def test_no_n_affectedports_column(self):
        """A missing ``n_affectedports`` column falls back to uniform markers."""
        rows = [{"lat": 1.0, "long": 2.0, "alertlevel": "RED"}]
        fig = build_disruptions_map(rows)
        assert any(t.name == "Red" for t in fig.data)

    def test_hover_includes_optional_fields(self):
        """Hover text includes type/from/to/country when present."""
        from openbb_imf.views.port_watch_charts import _disruption_hover_html

        row = {
            "lat": 1.0,
            "long": 2.0,
            "alertlevel": "RED",
            "eventtype": "Cyclone",
            "fromdate": "2024-01-01",
            "todate": "2024-01-05",
            "n_affectedports": 3,
            "country": "USA",
        }
        html = _disruption_hover_html(row)
        assert "Type: Cyclone" in html
        assert "From: 2024-01-01" in html
        assert "To: 2024-01-05" in html
        assert "Affected ports: 3" in html
        assert "Country: USA" in html


class TestBuildMonthlyTradePortcalls:
    """Edge tests for the ``portcalls`` branch of ``build_monthly_trade_chart``."""

    def test_portcalls_metric_skips_missing_columns(self):
        """A ``portcalls`` metric with no matching column collapses to empty."""
        rows = [{"date": "2024-01-01"}]
        fig = build_monthly_trade_chart(rows, "USA", "portcalls")
        assert any("columns present" in (a.text or "") for a in fig.layout.annotations)


class TestBuildContainerMetricSkipBranches:
    """Edge tests for ``build_container_metric_chart``."""

    def test_empty_inner_series_skipped(self):
        """A port whose series is empty is skipped without producing a trace."""
        series = {"P1": [{"date": "2024-01-01", "value": 5}], "P2": []}
        fig = build_container_metric_chart(series, {"P1": "Port 1"}, "Calls")
        assert len(fig.data) == 1
        assert fig.data[0].name == "Port 1"


class TestPlotWrappers:
    """Tests for the ``plot_*`` ``OpenBBFigure`` wrappers."""

    def test_plot_country_activity_returns_openbb_figure(self):
        """The wrapper coerces the result to ``OpenBBFigure``."""
        from openbb_charting.core.openbb_figure import OpenBBFigure

        rows = [
            {
                "date": "2024-01-01",
                "portcalls_container": 1,
                "portcalls_dry_bulk": 1,
                "portcalls_general_cargo": 1,
                "portcalls_roro": 1,
                "portcalls_tanker": 1,
                "portcalls": 5,
            }
        ]
        fig = plot_country_activity(rows, "USA", "portcalls")
        assert isinstance(fig, OpenBBFigure)

    def test_plot_monthly_trade_returns_openbb_figure(self):
        """The monthly-trade plot returns ``OpenBBFigure``."""
        from openbb_charting.core.openbb_figure import OpenBBFigure

        rows = [
            {
                "date": "2024-01-01",
                "value_import_total": 100,
                "value_export_total": 95,
            }
        ]
        assert isinstance(plot_monthly_trade(rows, "USA", "trade_value"), OpenBBFigure)

    def test_plot_container_metrics_groups_by_portid(self):
        """The container-metrics wrapper groups long-format rows by port id."""
        from openbb_charting.core.openbb_figure import OpenBBFigure

        rows = [
            {"portid": "PORT1", "date": "2024-01-01", "value": 5},
            {"portid": "PORT1", "date": "2024-02-01", "value": 7},
            {"portid": "PORT2", "date": "2024-01-01", "value": 1},
        ]
        fig = plot_container_metrics(rows, "Container Port Calls")
        assert isinstance(fig, OpenBBFigure)

    def test_plot_container_metrics_ignores_missing_portid(self):
        """Rows without a port id are dropped before grouping."""
        from openbb_charting.core.openbb_figure import OpenBBFigure

        rows = [{"date": "2024-01-01", "value": 1}]
        fig = plot_container_metrics(rows, "Container Port Calls")
        assert isinstance(fig, OpenBBFigure)

    def test_plot_disruption_sankey(self):
        """The Sankey wrapper produces an ``OpenBBFigure``."""
        from openbb_charting.core.openbb_figure import OpenBBFigure

        rows = [
            {
                "source": 0,
                "target": 1,
                "from_": "A",
                "to_": "B",
                "perc_disaster_capacity": 10.0,
            }
        ]
        assert isinstance(plot_disruption_sankey(rows, "Event 1"), OpenBBFigure)

    def test_plot_disruptions_map(self):
        """The Scattergeo wrapper produces an ``OpenBBFigure``."""
        from openbb_charting.core.openbb_figure import OpenBBFigure

        rows = [{"lat": 1.0, "long": 2.0, "alertlevel": "RED", "n_affectedports": 2}]
        assert isinstance(plot_disruptions_map(rows), OpenBBFigure)

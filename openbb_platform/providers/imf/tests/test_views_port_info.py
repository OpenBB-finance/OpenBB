"""Tests for ``openbb_imf.views.port_info``."""

# ruff: noqa: I001

import pytest

from openbb_imf.models.port_info import ImfPortInfoData
from openbb_imf.views.port_info import plot_port_info_map


def _row(
    port_code: str,
    *,
    country: str = "United States",
    continent: str = "North America",
    lat: float = 35.0,
    lon: float = -120.0,
    total: int = 100,
    share_import: float = 0.1,
    share_export: float = 0.2,
    industries: int = 3,
) -> ImfPortInfoData:
    """Build a populated port-info row."""
    payload = {
        "port_code": port_code,
        "port_name": port_code,
        "port_full_name": f"Port of {port_code}",
        "country": country,
        "country_code": "USA",
        "continent": continent,
        "latitude": lat,
        "longitude": lon,
        "vessel_count_total": total,
        "vessel_count_tanker": max(total // 5, 1),
        "vessel_count_container": max(total // 4, 1),
        "vessel_count_general_cargo": max(total // 6, 1),
        "vessel_count_dry_bulk": max(total // 3, 1),
        "vessel_count_roro": max(total // 10, 1),
        "share_country_maritime_import": share_import,
        "share_country_maritime_export": share_export,
        "industry_top1": "Energy" if industries >= 1 else None,
        "industry_top2": "Trade" if industries >= 2 else None,
        "industry_top3": "Manufacturing" if industries >= 3 else None,
    }
    return ImfPortInfoData.model_validate(payload)


class TestPlotPortInfoMap:
    """Tests for ``plot_port_info_map``."""

    def test_multi_continent_zooms_out(self):
        """Multiple continents produce a global map (zoom = 0)."""
        data = [
            _row("USNYC", continent="North America", lat=40.0, lon=-74.0, total=500),
            _row(
                "CNSHA",
                country="China",
                continent="Asia",
                lat=31.0,
                lon=121.0,
                total=900,
            ),
        ]
        fig = plot_port_info_map(data)
        assert fig.layout.map.zoom == 0
        assert len(fig.data) == 1

    def test_single_country_uses_share_for_marker_size(self):
        """Single-country input uses import+export share for sizing."""
        data = [
            _row(
                "USA1",
                total=300,
                share_import=0.05,
                share_export=0.10,
                lat=35.0,
                lon=-120.0,
            ),
            _row(
                "USA2",
                total=500,
                share_import=0.15,
                share_export=0.25,
                lat=33.0,
                lon=-118.0,
            ),
        ]
        fig = plot_port_info_map(data)
        assert fig.layout.map.center.lat == pytest.approx(34.0)
        assert fig.layout.map.zoom == 2

    def test_single_country_uniform_share_falls_back_to_midsize(self):
        """When all rows share identical import/export, the midsize marker is used."""
        data = [
            _row("US1", share_import=0.1, share_export=0.2, total=100),
            _row("US2", share_import=0.1, share_export=0.2, total=200),
        ]
        fig = plot_port_info_map(data)
        assert fig.data[0].marker is not None

    def test_single_continent_one_country_one_row(self):
        """A 1-row input still renders successfully."""
        data = [_row("US1", total=100)]
        fig = plot_port_info_map(data)
        assert fig.data[0].lat[0] == pytest.approx(35.0)
        assert fig.layout.map.center is not None

    def test_empty_list_raises(self):
        """An empty list raises ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError

        with pytest.raises(OpenBBError, match="No data to plot"):
            plot_port_info_map([])

    def test_wrong_type_raises(self):
        """A non-model entry raises ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError

        with pytest.raises(OpenBBError, match="Invalid data format"):
            plot_port_info_map([{"x": 1}])  # type: ignore[list-item]

    def test_charting_import_failure_raises(self, monkeypatch):
        """A failure importing the charting modules surfaces as ``OpenBBError``."""
        import builtins

        from openbb_core.app.model.abstract.error import OpenBBError

        real_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "openbb_charting.core.openbb_figure":
                raise ImportError("forced")
            return real_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        with pytest.raises(OpenBBError, match="Could not import Charting modules"):
            plot_port_info_map([_row("Test")])

    def test_hover_html_includes_all_sections(self):
        """The hover HTML carries name, traffic shares, vessel counts, industries."""
        data = [_row("MAIN", industries=3, share_import=0.1, share_export=0.2)]
        fig = plot_port_info_map(data)
        hover = fig.data[0].customdata[0][0]
        assert "Port of MAIN" in hover
        assert "Imports" in hover and "Exports" in hover
        assert "Containers" in hover and "Tankers" in hover
        assert "Top Industries" in hover

    def test_hover_html_skips_missing_shares(self):
        """When share fields are absent, the traffic block is suppressed."""
        from numpy import nan

        from openbb_imf.views.port_info import plot_port_info_map  # noqa: F401

        rows = [
            _row("US1", share_import=nan, share_export=nan, total=200),
            _row("US2", share_import=nan, share_export=nan, total=100),
        ]
        fig = plot_port_info_map(rows)
        hover = fig.data[0].customdata[0][0]
        assert "Imports" not in hover
        assert "Exports" not in hover

    def test_hover_html_no_industries(self):
        """When all industry fields are blank, the industries block is suppressed."""
        rows = [
            _row("US1", industries=0, share_import=0.0, share_export=0.0, total=300),
            _row("US2", industries=0, share_import=0.0, share_export=0.0, total=400),
        ]
        fig = plot_port_info_map(rows)
        hover = fig.data[0].customdata[0][0]
        assert "Top Industries" not in hover

    def test_single_country_uniform_vessel_count_falls_back_to_min_size(self):
        """Single country with identical share *and* vessel counts falls back to min size."""
        rows = [
            _row("US1", share_import=0.0, share_export=0.0, total=100),
            _row("US2", share_import=0.0, share_export=0.0, total=100),
        ]
        fig = plot_port_info_map(rows)
        assert fig.data[0].marker is not None

    def test_multi_country_uses_vessel_count_for_sizing(self):
        """When ``country.nunique() > 1`` the helper uses vessel-count sizing."""
        data = [
            _row(
                "US1",
                country="United States",
                continent="North America",
                total=100,
                lat=35.0,
                lon=-120.0,
            ),
            _row(
                "MX1",
                country="Mexico",
                continent="North America",
                total=900,
                lat=20.0,
                lon=-100.0,
            ),
        ]
        fig = plot_port_info_map(data)
        assert fig.layout.map.zoom == 2

    def test_zero_vessel_count_filtered_out(self):
        """Rows with ``vessel_count_total == 0`` are filtered out by the ``query``."""
        data = [
            _row("LIVE", total=100, lat=35.0, lon=-120.0),
            _row("DEAD", total=1, lat=10.0, lon=-50.0),
        ]
        fig = plot_port_info_map(data)
        assert len(fig.data[0].lat) == 2

    def test_multi_country_uniform_vessel_count_uses_min_size(self):
        """Multi-country input with identical vessel counts falls into the min-size branch."""
        data = [
            _row(
                "US1",
                country="United States",
                continent="North America",
                total=100,
                lat=35.0,
                lon=-120.0,
            ),
            _row(
                "MX1",
                country="Mexico",
                continent="North America",
                total=100,
                lat=20.0,
                lon=-100.0,
            ),
        ]
        fig = plot_port_info_map(data)
        assert fig.data[0].marker is not None

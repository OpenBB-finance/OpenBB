"""Tests for ``openbb_imf.views.maritime_chokepoint_info``."""

# ruff: noqa: I001

import pytest

from openbb_imf.models.maritime_chokepoint_info import ImfMaritimeChokePointInfoData
from openbb_imf.views.maritime_chokepoint_info import plot_chokepoint_annual_avg_vessels


def _row(
    name: str, total: int, lat: float = 0.0, lon: float = 0.0
) -> ImfMaritimeChokePointInfoData:
    """Build a populated chokepoint data row."""
    return ImfMaritimeChokePointInfoData.model_validate(
        {
            "chokepoint_code": name,
            "name": name,
            "latitude": lat,
            "longitude": lon,
            "vessel_count_total": total,
            "vessel_count_tanker": total // 5,
            "vessel_count_container": total // 4,
            "vessel_count_general_cargo": total // 6,
            "vessel_count_dry_bulk": total // 3,
            "vessel_count_roro": total // 10,
            "industry_top1": "Trade",
            "industry_top2": "Energy",
            "industry_top3": "Manufacturing",
        }
    )


class TestPlotChokepointAnnualAvgVessels:
    """Tests for ``plot_chokepoint_annual_avg_vessels``."""

    def test_light_theme_returns_figure_with_two_traces(self):
        """Default light theme builds a 2-trace (Scattergeo + Table) figure."""
        data = [
            _row("Suez", 500, lat=30.0, lon=32.0),
            _row("Panama", 300, lat=9.0, lon=-79.0),
        ]
        fig = plot_chokepoint_annual_avg_vessels(data)
        assert len(fig.data) == 2
        types = {t.type for t in fig.data}
        assert types == {"scattergeo", "table"}
        assert "Annual Average Vessels" in fig.layout.title.text

    def test_dark_theme_changes_paper_color(self):
        """Dark theme switches the paper background to the dark palette."""
        data = [_row("Suez", 500), _row("Hormuz", 250)]
        fig = plot_chokepoint_annual_avg_vessels(data, theme="dark")
        assert fig.layout.paper_bgcolor.startswith("rgba(21")

    def test_odd_number_of_rows_uses_alternating_fill(self):
        """An odd-length df still gets alternating row colors."""
        data = [_row("A", 100), _row("B", 90), _row("C", 80)]
        fig = plot_chokepoint_annual_avg_vessels(data)
        table_trace = next(t for t in fig.data if t.type == "table")
        assert table_trace.cells.fill.color is not None

    def test_source_annotation_is_present(self):
        """An ``IMF Port Watch`` source annotation appears on the layout."""
        data = [_row("Suez", 200)]
        fig = plot_chokepoint_annual_avg_vessels(data)
        annotations = [a.text for a in fig.layout.annotations]
        assert any("IMF Port Watch" in (t or "") for t in annotations)

    def test_empty_data_raises(self):
        """An empty list raises ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError

        with pytest.raises(OpenBBError, match="No data to plot"):
            plot_chokepoint_annual_avg_vessels([])

    def test_wrong_type_raises(self):
        """Non-list/non-model input raises ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError

        with pytest.raises(OpenBBError, match="Invalid data format"):
            plot_chokepoint_annual_avg_vessels([{"not": "a model"}])  # type: ignore[list-item]

    def test_charting_import_failure_raises_openbb_error(self, monkeypatch):
        """A failure importing ``openbb_charting`` is wrapped in ``OpenBBError``."""
        import builtins

        from openbb_core.app.model.abstract.error import OpenBBError

        real_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "openbb_charting.core.openbb_figure":
                raise ImportError("forced")
            return real_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        with pytest.raises(OpenBBError, match="Could not import Charting modules"):
            plot_chokepoint_annual_avg_vessels([_row("Suez", 100)])

"""Unit tests for state mixins.

Tests cover:
- EmittingWidget base class contract
- _normalize_figure helper function
- GridStateMixin: all grid state management methods
- PlotlyStateMixin: all Plotly state management methods
- ToolbarStateMixin: all toolbar state management methods

All tests use mock emitter classes to verify event emission.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from pywry.state_mixins import (
    EmittingWidget,
    GridStateMixin,
    PlotlyStateMixin,
    ToolbarStateMixin,
    _normalize_figure,
)


# =============================================================================
# Fixtures
# =============================================================================


class MockEmitter(EmittingWidget):
    """Mock emitter for testing mixins."""

    def __init__(self) -> None:
        self.emitted_events: list[tuple[str, dict]] = []

    def emit(self, event_type: str, data: dict[str, Any]) -> None:
        """Record emitted events for verification."""
        self.emitted_events.append((event_type, data))

    def get_last_event(self) -> tuple[str, dict[str, Any]] | None:
        """Get the most recently emitted event."""
        return self.emitted_events[-1] if self.emitted_events else None

    def get_events_by_type(self, event_type: str) -> list[dict]:
        """Get all events of a specific type."""
        return [data for evt, data in self.emitted_events if evt == event_type]


class MockGridWidget(MockEmitter, GridStateMixin):
    """Mock widget combining emitter with GridStateMixin."""


class MockPlotlyWidget(MockEmitter, PlotlyStateMixin):
    """Mock widget combining emitter with PlotlyStateMixin."""


class MockToolbarWidget(MockEmitter, ToolbarStateMixin):
    """Mock widget combining emitter with ToolbarStateMixin."""


class MockCombinedWidget(MockEmitter, GridStateMixin, PlotlyStateMixin, ToolbarStateMixin):
    """Mock widget combining all mixins."""


# =============================================================================
# _normalize_figure Tests
# =============================================================================


class TestNormalizeFigure:
    """Test the _normalize_figure helper function."""

    def test_dict_passthrough(self) -> None:
        """Test that dict figures are returned as-is."""
        fig = {"data": [{"x": [1, 2], "y": [3, 4]}], "layout": {"title": "Test"}}
        result = _normalize_figure(fig)
        assert result == fig
        assert result is fig  # Same object, no copy

    def test_object_with_to_dict(self) -> None:
        """Test that objects with to_json() are converted (to_json takes precedence)."""
        mock_figure = MagicMock()
        # _normalize_figure checks to_json first, which should return a JSON string
        mock_figure.to_json.return_value = '{"data": [], "layout": {"title": "Mock"}}'

        result = _normalize_figure(mock_figure)

        mock_figure.to_json.assert_called_once()
        assert result == {"data": [], "layout": {"title": "Mock"}}

    def test_object_without_to_dict_raises(self) -> None:
        """Test that objects without to_dict() raise ValueError."""
        mock_obj = MagicMock(spec=[])  # No to_dict method

        with pytest.raises(ValueError, match="Invalid figure format"):
            _normalize_figure(mock_obj)

    def test_none_raises(self) -> None:
        """Test that None raises ValueError."""
        with pytest.raises(ValueError, match="Invalid figure format"):
            _normalize_figure(None)


# =============================================================================
# GridStateMixin Tests
# =============================================================================


class TestGridStateMixin:
    """Test GridStateMixin event emission."""

    def test_request_grid_state(self) -> None:
        """Test request_grid_state emits correct event."""
        widget = MockGridWidget()

        widget.request_grid_state()

        event, data = widget.get_last_event()
        assert event == "grid:request-state"
        assert data == {}

    def test_request_grid_state_with_id(self) -> None:
        """Test request_grid_state with grid_id."""
        widget = MockGridWidget()

        widget.request_grid_state(grid_id="grid1")

        event, data = widget.get_last_event()
        assert event == "grid:request-state"
        assert data["gridId"] == "grid1"

    def test_request_grid_state_with_context(self) -> None:
        """Test request_grid_state with context for view switching."""
        widget = MockGridWidget()

        widget.request_grid_state({"target_view": "product_pivot"})

        event, data = widget.get_last_event()
        assert event == "grid:request-state"
        assert data["context"] == {"target_view": "product_pivot"}

    def test_restore_state(self) -> None:
        """Test restore_state emits correct event with state data."""
        widget = MockGridWidget()
        state = {
            "columnState": [{"colId": "name", "width": 200}],
            "filterState": {},
            "sortState": [],
        }

        widget.restore_state(state)

        event, data = widget.get_last_event()
        assert event == "grid:restore-state"
        assert data["state"] == state

    def test_reset_state(self) -> None:
        """Test reset_state emits correct event with hard flag."""
        widget = MockGridWidget()

        widget.reset_state()

        event, data = widget.get_last_event()
        assert event == "grid:reset-state"
        assert data["hard"] is False

    def test_reset_state_hard(self) -> None:
        """Test reset_state with hard=True."""
        widget = MockGridWidget()

        widget.reset_state(hard=True)

        event, data = widget.get_last_event()
        assert event == "grid:reset-state"
        assert data["hard"] is True

    def test_update_cell(self) -> None:
        """Test update_cell emits correct event."""
        widget = MockGridWidget()

        widget.update_cell(row_id="row1", col_id="price", value=99.99)

        event, data = widget.get_last_event()
        assert event == "grid:update-cell"
        assert data["rowId"] == "row1"
        assert data["colId"] == "price"
        assert data["value"] == 99.99

    def test_update_data(self) -> None:
        """Test update_data emits correct event."""
        widget = MockGridWidget()
        new_data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

        widget.update_data(new_data)

        event, data = widget.get_last_event()
        assert event == "grid:update-data"
        assert data["data"] == new_data
        assert data["strategy"] == "set"

    def test_update_columns(self) -> None:
        """Test update_columns emits correct event."""
        widget = MockGridWidget()
        columns = [
            {"field": "name", "headerName": "Name"},
            {"field": "age", "headerName": "Age"},
        ]

        widget.update_columns(columns)

        event, data = widget.get_last_event()
        assert event == "grid:update-columns"
        assert data["columnDefs"] == columns

    def test_update_grid(self) -> None:
        """Test update_grid emits correct event with data and columns."""
        widget = MockGridWidget()
        new_data = [{"id": 1, "name": "Alice"}]
        new_columns = [{"field": "id"}, {"field": "name"}]

        widget.update_grid(data=new_data, columns=new_columns)

        event, data = widget.get_last_event()
        assert event == "grid:update-grid"
        assert data["data"] == new_data
        assert data["columnDefs"] == new_columns

    def test_update_grid_with_restore_state(self) -> None:
        """Test update_grid with state restoration."""
        widget = MockGridWidget()
        new_data = [{"id": 1, "name": "Alice"}]
        saved_state = {
            "columnState": [{"colId": "name", "width": 200}],
            "filterModel": {},
        }

        widget.update_grid(data=new_data, restore_state=saved_state)

        event, data = widget.get_last_event()
        assert event == "grid:update-grid"
        assert data["data"] == new_data
        assert data["restoreState"] == saved_state

    def test_request_grid_state_with_context_kwarg(self) -> None:
        """Test request_grid_state with context as keyword arg."""
        widget = MockGridWidget()

        widget.request_grid_state(context={"target_view": "summary"})

        event, data = widget.get_last_event()
        assert event == "grid:request-state"
        assert data["context"] == {"target_view": "summary"}


# =============================================================================
# PlotlyStateMixin Tests
# =============================================================================


class TestPlotlyStateMixin:
    """Test PlotlyStateMixin event emission."""

    def test_update_figure_with_dict(self) -> None:
        """Test update_figure with dict figure."""
        widget = MockPlotlyWidget()
        figure = {"data": [{"x": [1, 2], "y": [3, 4]}], "layout": {"title": "Test"}}

        widget.update_figure(figure)

        event, data = widget.get_last_event()
        assert event == "plotly:update-figure"
        assert data["data"] == [{"x": [1, 2], "y": [3, 4]}]
        assert data["layout"] == {"title": "Test"}
        assert data["animate"] is False

    def test_update_figure_with_plotly_object(self) -> None:
        """Test update_figure with Plotly Figure-like object (to_json takes precedence)."""
        widget = MockPlotlyWidget()
        mock_figure = MagicMock()
        # _normalize_figure checks to_json first, which should return a JSON string
        mock_figure.to_json.return_value = '{"data": [{"x": [1]}], "layout": {"title": "Mock"}}'

        widget.update_figure(mock_figure)

        event, data = widget.get_last_event()
        assert event == "plotly:update-figure"
        assert data["data"] == [{"x": [1]}]
        assert data["layout"] == {"title": "Mock"}

    def test_update_layout(self) -> None:
        """Test update_layout emits correct event."""
        widget = MockPlotlyWidget()
        layout_update = {"title": "New Title", "showlegend": False}

        widget.update_layout(layout_update)

        event, data = widget.get_last_event()
        assert event == "plotly:update-layout"
        assert data["layout"] == layout_update

    def test_update_traces(self) -> None:
        """Test update_traces emits correct event."""
        widget = MockPlotlyWidget()
        trace_update = {"visible": True}

        widget.update_traces(trace_update, indices=[0, 1])

        event, data = widget.get_last_event()
        assert event == "plotly:update-traces"
        assert data["update"] == trace_update
        assert data["indices"] == [0, 1]

    def test_update_traces_default_indices(self) -> None:
        """Test update_traces with no indices specified."""
        widget = MockPlotlyWidget()
        trace_update = {"marker": {"size": 10}}

        widget.update_traces(trace_update)

        event, data = widget.get_last_event()
        assert event == "plotly:update-traces"
        assert data["update"] == trace_update
        assert "indices" not in data  # Not included when None

    def test_request_plotly_state(self) -> None:
        """Test request_plotly_state emits correct event."""
        widget = MockPlotlyWidget()

        widget.request_plotly_state()

        event, data = widget.get_last_event()
        assert event == "plotly:request-state"
        assert data == {}

    def test_reset_zoom(self) -> None:
        """Test reset_zoom emits correct event."""
        widget = MockPlotlyWidget()

        widget.reset_zoom()

        event, data = widget.get_last_event()
        assert event == "plotly:reset-zoom"
        assert data == {}

    def test_set_zoom(self) -> None:
        """Test set_zoom uses update_layout internally."""
        widget = MockPlotlyWidget()

        widget.set_zoom(xaxis_range=[0, 100], yaxis_range=[10, 50])

        # set_zoom calls update_layout internally
        event, data = widget.get_last_event()
        assert event == "plotly:update-layout"
        assert data["layout"]["xaxis.range"] == [0, 100]
        assert data["layout"]["yaxis.range"] == [10, 50]

    def test_set_zoom_x_only(self) -> None:
        """Test set_zoom with only xaxis_range."""
        widget = MockPlotlyWidget()

        widget.set_zoom(xaxis_range=[0, 100])

        event, data = widget.get_last_event()
        assert event == "plotly:update-layout"
        assert data["layout"]["xaxis.range"] == [0, 100]
        assert "yaxis.range" not in data["layout"]

    def test_set_trace_visibility(self) -> None:
        """Test set_trace_visibility uses update_traces internally."""
        widget = MockPlotlyWidget()

        widget.set_trace_visibility(visible=False, indices=[0])

        event, data = widget.get_last_event()
        assert event == "plotly:update-traces"
        assert data["update"] == {"visible": False}
        assert data["indices"] == [0]

    def test_set_trace_visibility_legendonly(self) -> None:
        """Test set_trace_visibility with 'legendonly' value."""
        widget = MockPlotlyWidget()

        widget.set_trace_visibility(visible="legendonly", indices=[2])

        event, data = widget.get_last_event()
        assert event == "plotly:update-traces"
        assert data["update"]["visible"] == "legendonly"
        assert data["indices"] == [2]


# =============================================================================
# ToolbarStateMixin Tests
# =============================================================================


class TestToolbarStateMixin:
    """Test ToolbarStateMixin event emission."""

    def test_request_toolbar_state(self) -> None:
        """Test request_toolbar_state emits correct event."""
        widget = MockToolbarWidget()

        widget.request_toolbar_state()

        event, data = widget.get_last_event()
        assert event == "toolbar:request-state"
        assert data == {}

    def test_set_toolbar_value(self) -> None:
        """Test set_toolbar_value emits correct event."""
        widget = MockToolbarWidget()

        widget.set_toolbar_value(component_id="dropdown_1", value="option_a")

        event, data = widget.get_last_event()
        assert event == "toolbar:set-value"
        assert data["componentId"] == "dropdown_1"
        assert data["value"] == "option_a"

    def test_set_toolbar_value_complex(self) -> None:
        """Test set_toolbar_value with complex value."""
        widget = MockToolbarWidget()

        widget.set_toolbar_value(component_id="multi_select", value=["a", "b", "c"])

        event, data = widget.get_last_event()
        assert event == "toolbar:set-value"
        assert data["componentId"] == "multi_select"
        assert data["value"] == ["a", "b", "c"]

    def test_set_toolbar_values(self) -> None:
        """Test set_toolbar_values emits correct event."""
        widget = MockToolbarWidget()
        values = {"dropdown_1": "option_a", "checkbox_1": True, "slider_1": 50}

        widget.set_toolbar_values(values)

        event, data = widget.get_last_event()
        assert event == "toolbar:set-values"
        assert data["values"] == values


# =============================================================================
# Combined Mixin Tests
# =============================================================================


class TestCombinedMixins:
    """Test widgets combining multiple mixins."""

    def test_combined_widget_has_all_methods(self) -> None:
        """Test that combined widget has methods from all mixins."""
        widget = MockCombinedWidget()

        # Grid methods
        assert hasattr(widget, "request_grid_state")
        assert hasattr(widget, "restore_state")
        assert hasattr(widget, "update_data")

        # Plotly methods
        assert hasattr(widget, "update_figure")
        assert hasattr(widget, "update_layout")
        assert hasattr(widget, "reset_zoom")

        # Toolbar methods
        assert hasattr(widget, "request_toolbar_state")
        assert hasattr(widget, "set_toolbar_value")

    def test_combined_widget_tracks_all_events(self) -> None:
        """Test that combined widget tracks events from all mixins."""
        widget = MockCombinedWidget()

        widget.request_grid_state()
        widget.update_layout({"title": "Test"})
        widget.set_toolbar_value("widget_1", "value_1")

        assert len(widget.emitted_events) == 3

        event_types = [event for event, _ in widget.emitted_events]
        assert "grid:request-state" in event_types
        assert "plotly:update-layout" in event_types
        assert "toolbar:set-value" in event_types


# =============================================================================
# EmittingWidget Contract Tests
# =============================================================================


class TestEmittingWidgetContract:
    """Test EmittingWidget base class."""

    def test_emit_raises_not_implemented(self) -> None:
        """Test that EmittingWidget.emit raises NotImplementedError."""
        widget = EmittingWidget()
        with pytest.raises(NotImplementedError, match="must implement"):
            widget.emit("test:event", {})

    def test_subclass_without_override_raises(self) -> None:
        """Test that subclasses without emit override still raise."""

        class IncompleteWidget(EmittingWidget):  # pylint: disable=abstract-method
            """Test class that doesn't override emit."""

        widget = IncompleteWidget()
        with pytest.raises(NotImplementedError, match="must implement"):
            widget.emit("test:event", {})

    def test_subclass_with_emit_works(self) -> None:
        """Test that subclasses implementing emit() work."""
        widget = MockEmitter()

        widget.emit("test:event", {"key": "value"})

        assert len(widget.emitted_events) == 1
        assert widget.get_last_event() == ("test:event", {"key": "value"})


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_state_restore(self) -> None:
        """Test restoring empty state."""
        widget = MockGridWidget()

        widget.restore_state({})

        result = widget.get_last_event()
        assert result is not None
        event, data = result  # pylint: disable=unpacking-non-sequence
        assert event == "grid:restore-state"
        assert data["state"] == {}

    def test_empty_data_update(self) -> None:
        """Test updating with empty data array."""
        widget = MockGridWidget()

        widget.update_data([])

        result = widget.get_last_event()
        assert result is not None
        event, data = result  # pylint: disable=unpacking-non-sequence
        assert event == "grid:update-data"
        assert data["data"] == []

    def test_empty_layout_update(self) -> None:
        """Test updating with empty layout dict."""
        widget = MockPlotlyWidget()

        widget.update_layout({})

        result = widget.get_last_event()
        assert result is not None
        event, data = result  # pylint: disable=unpacking-non-sequence
        assert event == "plotly:update-layout"
        assert data["layout"] == {}

    def test_none_value_in_toolbar(self) -> None:
        """Test setting None value in toolbar."""
        widget = MockToolbarWidget()

        widget.set_toolbar_value(component_id="widget_1", value=None)

        result = widget.get_last_event()
        assert result is not None
        event, data = result  # pylint: disable=unpacking-non-sequence
        assert event == "toolbar:set-value"
        assert data["value"] is None

    def test_large_data_update(self) -> None:
        """Test updating with large dataset."""
        widget = MockGridWidget()
        large_data = [{"id": i, "value": i * 10} for i in range(10000)]

        widget.update_data(large_data)

        result = widget.get_last_event()
        assert result is not None
        event, data = result  # pylint: disable=unpacking-non-sequence
        assert event == "grid:update-data"
        assert len(data["data"]) == 10000

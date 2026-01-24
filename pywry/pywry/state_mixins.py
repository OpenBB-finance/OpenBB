"""Shared mixins for unified state management across rendering paths.

These mixins provide a consistent API for widget interactions (Grid, Plotly, Toolbar)
regardless of whether the widget is running in a PyTauri window, an inline IFrame,
or a Jupyter widget (anywidget).

All mixins assume the consuming class implements:
    def emit(self, event_type: str, data: dict[str, Any]) -> None: ...
"""

from __future__ import annotations

import json

from typing import Any, Literal


class EmittingWidget:
    """Base class for state mixins, providing the emit interface."""

    def emit(self, event_type: str, data: dict[str, Any]) -> None:
        """Emit an event to the JavaScript side.

        This method must be implemented by the consuming class (e.g., PyWryWidget).
        """
        raise NotImplementedError("Classes mixing in EmittingWidget must implement 'emit'")

    def alert(
        self,
        message: str,
        alert_type: Literal["info", "success", "warning", "error", "confirm"] = "info",
        title: str | None = None,
        duration: int | None = None,
        callback_event: str | None = None,
        position: Literal["top-right", "top-left", "bottom-right", "bottom-left"] = "top-right",
    ) -> None:
        """Show a toast notification.

        Parameters
        ----------
        message : str
            The message to display.
        alert_type : str
            Alert type: 'info', 'success', 'warning', 'error', or 'confirm'.
        title : str, optional
            Optional title for the toast.
        duration : int, optional
            Auto-dismiss duration in ms. Defaults based on type.
        callback_event : str, optional
            Event name to emit when confirm dialog is answered.
        position : str
            Toast position: 'top-right', 'top-left', 'bottom-right', 'bottom-left'.
        """
        payload: dict[str, Any] = {
            "message": message,
            "type": alert_type,
            "position": position,
        }
        if title is not None:
            payload["title"] = title
        if duration is not None:
            payload["duration"] = duration
        if callback_event is not None:
            payload["callback_event"] = callback_event
        self.emit("pywry:alert", payload)


def _normalize_figure(figure: Any) -> dict[str, Any]:
    """Normalize a Plotly Figure or dict into a pure JSON-serializable dictionary.

    Uses Plotly's to_json() when available to ensure numpy arrays are converted
    to lists and all values are JSON-serializable.
    """
    if hasattr(figure, "to_json"):
        # Use to_json for proper numpy array handling, then parse back
        return json.loads(figure.to_json())  # type: ignore[no-any-return]
    if hasattr(figure, "to_dict"):
        return figure.to_dict()  # type: ignore[no-any-return]
    if isinstance(figure, dict):
        return figure
    try:
        # Fallback for JSON strings
        return json.loads(str(figure))  # type: ignore[no-any-return]
    except (ValueError, TypeError) as e:
        raise ValueError("Invalid figure format. Expected Plotly Figure, dict, or JSON.") from e


class GridStateMixin(EmittingWidget):  # pylint: disable=abstract-method
    """Mixin for AG Grid state management."""

    def request_grid_state(
        self,
        context: dict[str, Any] | None = None,
        grid_id: str | None = None,
    ) -> None:
        """Request the current state of the grid (sort, filter, columns, etc.).

        The frontend will respond with a 'grid:state-response' event.

        Parameters
        ----------
        context : dict, optional
            Context data to include in the response. This is echoed back
            unchanged in the state_response event, useful for tracking
            which request triggered the response (e.g., view switching).
        grid_id : str, optional
            The ID of the grid to query.
        """
        payload: dict[str, Any] = {}
        if grid_id:
            payload["gridId"] = grid_id
        if context:
            payload["context"] = context
        self.emit("grid:request-state", payload)

    def restore_state(self, state: dict[str, Any], grid_id: str | None = None) -> None:
        """Restore the grid state from a previous state object."""
        payload: dict[str, Any] = {"state": state}
        if grid_id:
            payload["gridId"] = grid_id
        self.emit("grid:restore-state", payload)

    def reset_state(self, grid_id: str | None = None, hard: bool = False) -> None:
        """Reset the grid state to default values.

        Parameters
        ----------
        grid_id : str | None, optional
            The ID of the grid to reset.
        hard : bool, optional
            If True, completely destroys and recreates the grid instance.
            If False (default), only resets state columns/filters/sort.
        """
        payload: dict[str, Any] = {"hard": hard}
        if grid_id:
            payload["gridId"] = grid_id
        self.emit("grid:reset-state", payload)

    def update_cell(
        self, row_id: str | int, col_id: str, value: Any, grid_id: str | None = None
    ) -> None:
        """Update a single cell value."""
        payload = {
            "rowId": row_id,
            "colId": col_id,
            "value": value,
        }
        if grid_id:
            payload["gridId"] = grid_id
        self.emit("grid:update-cell", payload)

    def update_data(
        self,
        data: list[dict[str, Any]],
        grid_id: str | None = None,
        strategy: str = "set",
    ) -> None:
        """Update grid data rows.

        Parameters
        ----------
        data : list[dict[str, Any]]
            List of row data dictionaries.
        grid_id : str | None, optional
            The ID of the grid.
        strategy : str, optional
            Update strategy ('set', 'append', 'update').
            'set' replaces all data.
        """
        payload: dict[str, Any] = {"data": data, "strategy": strategy}
        if grid_id:
            payload["gridId"] = grid_id
        self.emit("grid:update-data", payload)

    def update_columns(self, column_defs: list[dict[str, Any]], grid_id: str | None = None) -> None:
        """Update column definitions."""
        payload: dict[str, Any] = {"columnDefs": column_defs}
        if grid_id:
            payload["gridId"] = grid_id
        self.emit("grid:update-columns", payload)

    def update_grid(
        self,
        data: list[dict[str, Any]] | Any | None = None,
        columns: list[dict[str, Any]] | None = None,
        restore_state: dict[str, Any] | None = None,
        grid_id: str | None = None,
    ) -> None:
        """Update the grid with new data, columns, and/or restore saved state.

        This is the primary method for switching views or making bulk updates.
        It combines data, column, and state updates into a single operation
        to minimize UI flicker.

        Parameters
        ----------
        data : list[dict] | DataFrame, optional
            New row data. If a DataFrame, it will be converted to records.
        columns : list[dict], optional
            New column definitions.
        restore_state : dict, optional
            Previously saved grid state to restore (from grid:state-response).
            Contains columnState, filterModel, sortModel.
        grid_id : str, optional
            The ID of the grid to update.
        """
        payload: dict[str, Any] = {}

        # Normalize data if it's a DataFrame
        if data is not None:
            if hasattr(data, "to_dict") and hasattr(data, "columns"):
                # It's a DataFrame
                payload["data"] = data.to_dict(orient="records")
            else:
                payload["data"] = data

        if columns is not None:
            payload["columnDefs"] = columns

        if restore_state is not None:
            payload["restoreState"] = restore_state

        if grid_id:
            payload["gridId"] = grid_id

        # Emit combined update event
        self.emit("grid:update-grid", payload)


class PlotlyStateMixin(EmittingWidget):  # pylint: disable=abstract-method
    """Mixin for Plotly chart state management."""

    def update_figure(
        self,
        figure: Any,
        chart_id: str | None = None,
        animate: bool = False,
        config: dict[str, Any] | None = None,
    ) -> None:
        """Update the entire chart figure (data and layout)."""
        fig_dict = _normalize_figure(figure)
        payload = {
            "data": fig_dict.get("data", []),
            "layout": fig_dict.get("layout", {}),
            "animate": animate,
        }
        if chart_id:
            payload["chartId"] = chart_id
        if config:
            payload["config"] = config
        self.emit("plotly:update-figure", payload)

    def update_layout(self, layout: dict[str, Any], chart_id: str | None = None) -> None:
        """Update specific layout properties (Plotly.relayout)."""
        payload: dict[str, Any] = {"layout": layout}
        if chart_id:
            payload["chartId"] = chart_id
        self.emit("plotly:update-layout", payload)

    def update_traces(
        self,
        patch: dict[str, Any],
        indices: list[int] | None = None,
        chart_id: str | None = None,
    ) -> None:
        """Update specific trace properties (Plotly.restyle)."""
        payload: dict[str, Any] = {"update": patch}
        if chart_id:
            payload["chartId"] = chart_id
        if indices is not None:
            payload["indices"] = indices
        self.emit("plotly:update-traces", payload)

    def request_plotly_state(self, chart_id: str | None = None) -> None:
        """Request current chart state (viewport, zoom, selections)."""
        payload = {}
        if chart_id:
            payload["chartId"] = chart_id
        self.emit("plotly:request-state", payload)

    def reset_zoom(self, chart_id: str | None = None) -> None:
        """Reset the chart zoom/pan to default."""
        payload = {}
        if chart_id:
            payload["chartId"] = chart_id
        self.emit("plotly:reset-zoom", payload)

    def set_zoom(
        self,
        xaxis_range: tuple[Any, Any] | None = None,
        yaxis_range: tuple[Any, Any] | None = None,
        chart_id: str | None = None,
    ) -> None:
        """Set specific zoom ranges for axes."""
        update = {}
        if xaxis_range:
            update["xaxis.range"] = xaxis_range
        if yaxis_range:
            update["yaxis.range"] = yaxis_range

        if update:
            self.update_layout(update, chart_id)

    def set_trace_visibility(
        self,
        visible: bool | str | list[bool | str],
        indices: list[int] | None = None,
        chart_id: str | None = None,
    ) -> None:
        """Set visibility for specific traces."""
        self.update_traces({"visible": visible}, indices, chart_id)


class ToolbarStateMixin(EmittingWidget):  # pylint: disable=abstract-method
    """Mixin for Toolbar state interactions."""

    def request_toolbar_state(self, toolbar_id: str | None = None) -> None:
        """Request values of all toolbar inputs."""
        payload: dict[str, Any] = {}
        if toolbar_id:
            payload["toolbarId"] = toolbar_id
        self.emit("toolbar:request-state", payload)

    def set_toolbar_value(
        self, component_id: str, value: Any, toolbar_id: str | None = None
    ) -> None:
        """Set a single toolbar input value."""
        payload: dict[str, Any] = {"componentId": component_id, "value": value}
        if toolbar_id:
            payload["toolbarId"] = toolbar_id
        self.emit("toolbar:set-value", payload)

    def set_toolbar_values(self, values: dict[str, Any], toolbar_id: str | None = None) -> None:
        """Set multiple toolbar input values at once."""
        payload: dict[str, Any] = {"values": values}
        if toolbar_id:
            payload["toolbarId"] = toolbar_id
        self.emit("toolbar:set-values", payload)

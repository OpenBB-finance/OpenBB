"""Abstract contracts an OBBject charting engine and backend must satisfy."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from openbb_core.app.model.charts.chart import Chart


@runtime_checkable
class ChartingExtension(Protocol):
    """Surface a charting engine must expose to the Platform interfaces.

    An engine is the OBBject accessor resolved by
    :class:`~openbb_core.app.charting.manager.ChartingManager`. Implementing
    this contract keeps every interface (Python, API, CLI, MCP) free of any
    hard dependency on a specific charting package.
    """

    @classmethod
    def functions(cls) -> list[str]:
        """Return the route-derived names the engine can chart.

        Names are the command route with slashes replaced by underscores and
        the leading underscore stripped, e.g. ``equity_price_historical``.
        """
        ...  # pragma: no cover - Protocol stub, never executed

    def show(self, render: bool = True, **kwargs: Any) -> Chart | None:
        """Create the chart for the bound OBBject and store it on it."""
        ...  # pragma: no cover - Protocol stub, never executed


@runtime_checkable
class AbstractChartingBackend(Protocol):
    """Surface a rendering backend must expose to charting engines.

    A backend is resolved through the ``openbb_charting_backend`` entry-point
    group (see :mod:`openbb_core.app.charting.backend`) and is constructed with
    a single ``charting_settings`` argument, mirroring the reference engine.
    """

    def __init__(self, charting_settings: Any) -> None:
        """Initialize the backend with the resolved charting settings."""
        ...  # pragma: no cover - Protocol stub, never executed

    def send_table(self, *args: Any, **kwargs: Any) -> Any:
        """Display an interactive table."""
        ...  # pragma: no cover - Protocol stub, never executed

    def send_url(self, *args: Any, **kwargs: Any) -> Any:
        """Display a URL."""
        ...  # pragma: no cover - Protocol stub, never executed

# pylint: disable=c-extension-no-member,protected-access,consider-using-with
# type: ignore
import json
from typing import TYPE_CHECKING, Optional, TypeVar

import plotly.graph_objects as go
from PySide6.QtCore import QSize, Qt, QUrl, Signal
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QDialog, QMainWindow, QSizePolicy, QWidget

from openbb_terminal.core.config.paths import USER_DATA_DIRECTORY
from qt_app.config.qt_settings import QT_PATH, WEB_ENGINE_SETTINGS

if TYPE_CHECKING:
    from .qt_figure import QtFigure


QtFigureType = TypeVar("QtFigureType", bound="QtFigure")


active_windows: list["QtPlotlyFigureWindow"] = []


class PlotlyFigureHTMLWebView(QWebEngineView):
    """Web view widget to display a plotly figure as HTML."""

    def __init__(self, parent: Optional["QtPlotlyFigureWidget"] = None):
        super().__init__(parent=parent)
        self.figure_: QtFigureType = None
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        for attribute in WEB_ENGINE_SETTINGS:
            self.settings().setAttribute(*attribute)

        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setMinimumSize(600, 400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setUrl(QUrl.fromLocalFile(QT_PATH / "core/plotly.html"))
        self.loadFinished.connect(self._on_load_finished)

    def set_figure(self, figure: go.Figure, style: str = "dark"):
        """Set the figure."""
        if (bg_color := "#111111" if style == "dark" else "white") == "#111111":
            figure.update_layout(
                newshape_line_color="gold",
                modebar=dict(
                    orientation="v",
                    bgcolor=bg_color,
                    color="gold",
                    activecolor="#d1030d",
                ),
            )
        self.page().setBackgroundColor(bg_color)

        figure = go.Figure(figure.to_dict())
        figure.update_layout(dragmode="pan")
        self.figure_ = figure

    def _on_load_finished(self):
        """Handle load finished."""
        if self.figure_ is None or self.figure_.data is None:
            return

        fig_json = json.dumps(self.figure_.to_json())

        for trace in self.figure_.data:
            if isinstance(trace, go.Table):
                self.page().runJavaScript(f"window.plotly_table = {fig_json}")
                return

        self.page().runJavaScript(f"window.plotly_figure = {fig_json}")


class QtPlotlyFigureWidget(QWidget):
    """Widget to display a plotly figure."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self.figure_ = None
        self.view_ = PlotlyFigureHTMLWebView(self)

    def set_figure(self, figure: go.Figure):
        """Set the figure to display.

        Parameters
        ----------
        figure : plotly.graph_objects.Figure
            The figure to display.
        """
        self.figure_: QtFigureType = figure
        self.view_.set_figure(figure, figure.layout.template.layout.mapbox.style)


class PlotlyFigureWidget(QtPlotlyFigureWidget):
    """Widget to display a plotly figure.

    Parameters
    ----------
    figure : plotly.graph_objects.Figure
        The figure to display.
    """

    def __init__(self, figure: go.Figure):
        super().__init__()
        self.set_figure(figure)

    def sizeHint(self):
        """Return the size hint for the widget."""
        return QSize(800, 600)


class QtPlotlyFigureWindow(QMainWindow):
    """Window to display a plotly figure.

    Parameters
    ----------
    figure : plotly.graph_objects.Figure
        The figure to display.
    """

    on_open = Signal()
    closing = Signal()

    def __init__(self, figure: go.Figure):
        super().__init__()
        self.widget_ = QtPlotlyFigureWidget(self)
        self.widget_.set_figure(figure)
        self.setCentralWidget(self.widget_.view_)
        self.setMinimumSize(800, 586)
        active_windows.append(self)

        self.closing.connect(lambda: active_windows.remove(self))
        self.on_open.connect(lambda: self.raise_())

        self._download_popup = QDialog(self)
        self.widget_.view_.page().profile().setDownloadPath(
            str(USER_DATA_DIRECTORY / "saved_plots")
        )

    def set_figure(self, figure: go.Figure):
        """Set the figure to display.

        Parameters
        ----------
        figure : plotly.graph_objects.Figure
            The figure to display.
        """
        self.widget_.set_figure(figure)

    def closeEvent(self, event):
        """We override the close event to emit a signal before closing."""
        self.closing.emit()
        super().closeEvent(event)

    def sizeHint(self):
        """Return the size hint for the widget."""
        return QSize(*self.widget_.figure_.get_fig_size())

    def get_popup(self):
        """Return the popup window."""
        return self._download_popup

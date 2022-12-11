# pylint: disable=c-extension-no-member,protected-access,consider-using-with
# type: ignore
import random

import plotly.graph_objects as go
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QGuiApplication
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout

from qt_app.core.figure_window import QtPlotlyFigureWindow


class QtFigure(go.Figure):
    """Plotly figure that can be displayed in a Qt window.

    Parameters
    ----------
    *args
        Positional arguments to pass to ``plotly.graph_objects.Figure``
    **kwargs
        Keyword arguments to pass to ``plotly.graph_objects.Figure``
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._window: QtPlotlyFigureWindow = None

    def show(self):  # pylint: disable=arguments-differ
        """Show the figure in a Qt window."""

        if self._window is None:
            self._window = QtPlotlyFigureWindow(self)

            title = self.layout.title.text if self.layout.title.text else "Plots"
            self._window.setWindowTitle(
                f"OpenBB - {title.replace('<b>', '').replace('</b>', '')}"
            )

            center = QGuiApplication.primaryScreen().availableGeometry().center()
            self._window.move(
                center.x() - self._window.width() / 2 + random.randint(-100, 100),
                center.y() - self._window.height() / 2 + random.randint(-100, 100),
            )

            # Download popup window for saving plots
            download_popup = self._window.get_popup()
            download_popup.setWindowTitle("OpenBB - Plot saved")
            download_popup.resize(300, 100)
            download_popup.setWindowModality(Qt.NonModal)

            download_popup.setLayout(QVBoxLayout(download_popup))
            download_popup.layout().addWidget(
                QLabel("Plot saved.\n\nWould you like to open the directory?")
            )

            # Buttons for opening the directory and closing the popup
            download_popup.layout().addWidget(
                QPushButton("Open", clicked=lambda: self._on_accept_open_directory())
            )
            download_popup.layout().addWidget(
                QPushButton("Close", clicked=lambda: download_popup.close())
            )

            self._window.widget_.view_.page().profile().downloadRequested.connect(
                self._on_download_requested
            )

        self._window.on_open.emit()
        self._window.setWindowState(
            self._window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
        )
        self._window.activateWindow()
        self._window.raise_()
        self._window.show()

    def _on_download_requested(self, download_item: QWebEngineDownloadRequest):
        """Handle download requests."""
        download_item.accept()
        self._on_download_finished(download_item)

    def _on_download_finished(self, download_item: QWebEngineDownloadRequest):
        """Handle download finished."""
        if isinstance(download_item, QWebEngineDownloadRequest):
            # We only want to show the popup if the download was initiated from the
            # figure window
            if download_item.page() == self._window.widget_.view_.page():
                self._window._download_popup.show()

    def _on_accept_open_directory(self):
        """Handle the user accepting to open the directory."""
        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                self._window.widget_.view_.page().profile().downloadPath()
            )
        )
        self._window._download_popup.close()

    def get_fig_size(self):
        """Gets the width and height of the plotly figure."""
        height = 585 if self.layout.height is None else self.layout.height
        width = 800 if self.layout.width is None else self.layout.width
        return int(width), int(height)

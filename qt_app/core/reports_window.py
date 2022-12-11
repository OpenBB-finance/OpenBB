# pylint: disable=c-extension-no-member,protected-access
# type: ignore
import logging
import os
import sys
from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QGuiApplication, QIcon
from PySide6.QtWebEngineCore import (
    QWebEngineDownloadRequest,
    QWebEnginePage,
    QWebEngineUrlRequestInfo,
    QWebEngineUrlRequestInterceptor,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from openbb_terminal.core.config.paths import USER_REPORTS_DIRECTORY
from qt_app.config.qt_settings import ICON_PATH, WEB_ENGINE_SETTINGS
from qt_app.core.figure_window import active_windows

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


class OpenBBRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent: "ReportsWebView" = None):
        super().__init__(parent)
        self._widget: "ReportsWidget" = parent.parent().parent()

    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        """Intercept requests to open links in the default browser."""
        if (
            info.resourceType()
            == QWebEngineUrlRequestInfo.ResourceType.ResourceTypeMainFrame
            and info.requestMethod() == "GET"
            and info.navigationType()
            == QWebEngineUrlRequestInfo.NavigationType.NavigationTypeLink
        ):
            if info.requestUrl().scheme() != "file":
                QDesktopServices.openUrl(info.requestUrl())
                info.block(True)
                self._widget._view.load(self._widget._view.url())
                self._widget._view.reload()


class ReportsSaveFileDialog(QFileDialog):
    def __init__(self, parent: "ReportsWebView" = None):
        super().__init__(parent)
        self._view: "ReportsWebView" = parent
        self.setWindowTitle("Save Report")
        self.setNameFilter("HTML files (*.html)")
        self.setDirectory(str(USER_REPORTS_DIRECTORY))
        self.setFileMode(QFileDialog.FileMode.AnyFile)
        self.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        self.setLabelText(QFileDialog.DialogLabel.LookIn, "Look in:")
        self.setLabelText(QFileDialog.DialogLabel.FileName, "File name:")
        self.setLabelText(QFileDialog.DialogLabel.FileType, "Files of type:")
        self.setLabelText(QFileDialog.DialogLabel.Accept, "Save")
        self.setLabelText(QFileDialog.DialogLabel.Reject, "Cancel")
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        self.setDefaultSuffix("html")

    def accept(self):
        """We override the accept method to make sure the file name ends with .html."""
        if self.selectedFiles()[0].endswith(".html"):
            super().accept()
        else:
            msg = QMessageBox(
                QMessageBox.Warning,
                "OpenBB - Reports",
                "Invalid File Name\n\nThe file name must end with .html",
                QMessageBox.StandardButton.Ok,
                self,
            )
            msg.setDefaultButton(QMessageBox.StandardButton.Ok)
            msg.exec()


class ReportsWebView(QWebEngineView):
    def __init__(self, parent: "ReportsWidget" = None):
        super().__init__(parent)
        self._window: "ReportsWindow" = parent.parent()
        self._filedialog = ReportsSaveFileDialog(self)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        for attribute in WEB_ENGINE_SETTINGS:
            self.settings().setAttribute(*attribute)

        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setMinimumSize(600, 400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAcceptDrops(False)

        # We set up the request interceptor to make sure links are opened in the default browser
        self.interceptor = OpenBBRequestInterceptor(self)
        self.page().profile().setUrlRequestInterceptor(self.interceptor)
        self.page().profile().downloadRequested.connect(self._on_download_requested)

    def _on_download_requested(self, download_item: QWebEngineDownloadRequest):
        """When the Save Changes button is clicked, we intercept the download request and
        open a file dialog to let the user select a file name and location.
        """
        if download_item.downloadFileName().endswith(".html"):
            self._filedialog.selectFile(
                self.url().fileName() if self.url().fileName() else "openbb_report.html"
            )
            self._filedialog.resize(800, 600)
            self._filedialog.show()
            if self._filedialog.exec():
                self._on_file_selected(download_item)
                self.page().triggerAction(QWebEnginePage.WebAction.DownloadImageToDisk)

    def _on_file_selected(self, download_item: QWebEngineDownloadRequest):
        """This method is called when the user selects a file in the file dialog."""
        download_item.setDownloadDirectory(self._filedialog.directory().path())
        download_item.setDownloadFileName(self._filedialog.selectedFiles()[0])
        download_item.accept()

        self._on_download_finished(download_item)

    def _on_download_finished(self, download_item: QWebEngineDownloadRequest):
        """When the download is finished, we open a message box to let the user know the
        report has been saved and give them the option to open the directory containing the
        report."""
        if download_item.page() == self.page():
            msg = QMessageBox(
                QMessageBox.Information,
                "OpenBB - Reports",
                f"The report has been saved to {Path(download_item.downloadDirectory()).name}",
                QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Close,
                self,
            )
            msg.setDefaultButton(QMessageBox.StandardButton.Open)

            msg.buttonClicked.connect(
                lambda x: QDesktopServices.openUrl(
                    QUrl.fromLocalFile(download_item.downloadDirectory())
                )
                if x.text() == "Open"
                else None
            )
            msg.show()


class ReportsWidget(QWidget):
    def __init__(self, parent: "ReportsWindow" = None):
        super().__init__(parent)
        self._view = ReportsWebView(self)
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self._view)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.show()

    def closeEvent(self, event):
        """We override the closeEvent method to emit a signal when the widget is closed."""
        self._view._window.closing.emit()
        event.accept()


class ReportsWindow(QMainWindow):
    closing = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._widget = ReportsWidget(self)
        self.setWindowTitle("OpenBB Reports")
        self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setCentralWidget(self._widget._view)
        self._view = self._widget._view

        # We resize the window to 80% of the screen size
        screen = QGuiApplication.primaryScreen().availableGeometry()
        if screen.width() > 1920:
            self.resize(1920 * 0.8, 1080 * 0.8)
        else:
            self.resize(screen.width() * 0.8, screen.height() * 0.8)

    def _on_new_report(self, report_path: str):
        """Open the most recent report in the webview"""
        self._view.load(QUrl.fromLocalFile(report_path))
        self.show()
        self.raise_()
        self.activateWindow()
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def closeEvent(self, event):
        """Override the close event to emit a signal"""
        self.closing.emit()
        event.accept()


class ReportsFileSystemWatcher(QFileSystemWatcher):
    closing = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addPath(str(USER_REPORTS_DIRECTORY))
        self._last_report: Path = [
            max(USER_REPORTS_DIRECTORY.glob("*.html"), key=lambda x: x.stat().st_ctime)
            if USER_REPORTS_DIRECTORY.glob("*.html")
            else None
        ][0]
        self.directoryChanged.connect(self.on_directory_changed)

    def on_directory_changed(self):
        """Open the most recent report in the webview"""
        if USER_REPORTS_DIRECTORY.iterdir():
            most_recent = max(
                USER_REPORTS_DIRECTORY.glob("*.html"), key=lambda x: x.stat().st_ctime
            )

            # This is a hack to make sure the file is not locked by the OS
            # If it is locked, we wait for the next change
            # e.g. when the report is still being written
            try:
                os.rename(most_recent, most_recent)
            except OSError:
                return
            if most_recent != self._last_report:
                self._last_report = most_recent
                self._on_new_report(most_recent)

    def _create_window(self, report_path: str):
        """Create a new reports window"""
        window = ReportsWindow()
        active_windows.append(window)
        window.closing.connect(lambda: active_windows.remove(window))
        window._on_new_report(report_path)
        window.show()

    def _on_new_report(self, report_path: str):
        """Open the most recent report in the webview"""
        self._create_window(report_path)

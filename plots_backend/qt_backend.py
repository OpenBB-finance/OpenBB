# pylint: disable=c-extension-no-member,protected-access,consider-using-with
# type: ignore
import contextlib
import json
import os
import pickle
import random
import signal
import socket
import sys
from pathlib import Path
from typing import List, Optional

import plotly.graph_objects as go
from PySide6.QtCore import (
    QObject,
    QSize,
    QSocketNotifier,
    Qt,
    QUrl,
    Signal,
)  # QFileSystemWatcher,
from PySide6.QtGui import QDesktopServices, QGuiApplication, QIcon
from PySide6.QtNetwork import QHostAddress
from PySide6.QtWebEngineCore import (  # QWebEngineUrlRequestInfo,; QWebEngineUrlRequestInterceptor,
    QWebEngineDownloadRequest,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebSockets import QWebSocketServer
from PySide6.QtWidgets import (  # QFileDialog,
    QDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from openbb_terminal.core.config.paths import (
    USER_DATA_DIRECTORY,
)  # USER_REPORTS_DIRECTORY,
from plots_backend.app_config import (
    APP_PALETTE,
    STYLE_SHEET,
    WEB_ENGINE_SETTINGS,
    QApplication,
)

qApp: Optional[QApplication] = None
active_windows: List["QtPlotlyFigureWindow"] = []
QT_PATH = Path(__file__).parent.resolve()
ICON_PATH = QT_PATH / "assets/favicon.ico"


websocket_port = 14733
# in case the port is already in use, We try to find a free port
while True:
    try:
        server = QWebSocketServer("openbb", QWebSocketServer.NonSecureMode)
        if not server.listen(QHostAddress.LocalHost, websocket_port):
            websocket_port += 1
            continue
        server.close()
        break
    except RuntimeError:
        websocket_port += 1
        continue

# We save the port and the pid of the this process in pickle file so that the terminal can access it
pickle.dump(websocket_port, open(QT_PATH / "assets/qt_socket", "wb"))
pickle.dump(os.getpid(), open(QT_PATH / "assets/qt_backend_pid", "wb"))


def _create_qApp() -> QApplication:
    global qApp  # pylint: disable=global-statement
    if qApp is None:
        app = QApplication.instance()
        if app is None:
            qApp = QApplication(["openbb"])
            qApp.setPalette(APP_PALETTE)
            qApp.setApplicationName("openbb")
            qApp.setApplicationVersion("2.0.0")
            qApp.setOrganizationName("OpenBB")
            qApp.setOrganizationDomain("https://openbb.co")
            qApp.setWindowIcon(QIcon(str(ICON_PATH)))
            qApp.setStyleSheet(STYLE_SHEET)
            try:
                import ctypes  # pylint: disable=import-outside-toplevel

                # We need to set an app id so that the taskbar icon is correct on Windows
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("openbb")
            except (AttributeError, ImportError):
                pass
            except OSError:
                pass
        else:
            qApp = app
    return qApp


@contextlib.contextmanager
def _maybe_allow_interrupt(qapp: QApplication):
    """
    This manager allows to terminate a plot by sending a SIGINT. It is
    necessary because the running Qt backend prevents Python interpreter to
    run and process signals (i.e., to raise KeyboardInterrupt exception). To
    solve this one needs to somehow wake up the interpreter and make it close
    the plot window. We do this by using the signal.set_wakeup_fd() function
    which organizes a write of the signal number into a socketpair connected
    to the QSocketNotifier (since it is part of the Qt backend, it can react
    to that write event). Afterwards, the Qt handler empties the socketpair
    by a recv() command to re-arm it (we need this if a signal different from
    SIGINT was caught by set_wakeup_fd() and we shall continue waiting). If
    the SIGINT was caught indeed, after exiting the on_signal() function the
    interpreter reacts to the SIGINT according to the handle() function which
    had been set up by a signal.signal() call: it causes the qt_object to
    exit by calling its quit() method. Finally, we call the old SIGINT
    handler with the same arguments that were given to our custom handle()
    handler.

    We do this only if the old handler for SIGINT was not None, which means
    that a non-python handler was installed, i.e. in Julia, and not SIG_IGN
    which means we should ignore the interrupts.
    """
    old_sigint_handler = signal.getsignal(signal.SIGINT)
    handler_args = None
    skip = False
    if old_sigint_handler in (None, signal.SIG_IGN, signal.SIG_DFL):
        skip = True
    else:
        wsock, rsock = socket.socketpair()
        wsock.setblocking(False)
        old_wakeup_fd = signal.set_wakeup_fd(wsock.fileno())
        sn = QSocketNotifier(rsock.fileno(), QSocketNotifier.Type.Read)

        # We do not actually care about this value other than running some
        # Python code to ensure that the interpreter has a chance to handle the
        # signal in Python land.  We also need to drain the socket because it
        # will be written to as part of the wakeup!  There are some cases where
        # this may fire too soon / more than once on Windows so we should be
        # forgiving about reading an empty socket.
        rsock.setblocking(False)

        # Clear the socket to re-arm the notifier.
        @sn.activated.connect
        def _may_clear_sock(*args):  # pylint: disable=unused-argument
            try:
                rsock.recv(1)
            except BlockingIOError:
                pass

        def handle(*args):
            nonlocal handler_args
            handler_args = args
            qapp.quit()

        signal.signal(signal.SIGINT, handle)
    try:
        yield
    finally:
        if not skip:
            wsock.close()
            rsock.close()
            sn.setEnabled(False)
            signal.set_wakeup_fd(old_wakeup_fd)
            signal.signal(signal.SIGINT, old_sigint_handler)
            if handler_args is not None:
                old_sigint_handler(*handler_args)  # pylint: disable=not-an-iterable


class PlotlyFigureHTMLWebView(QWebEngineView):
    """Web view widget to display a plotly figure as HTML."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self.figure_: go.Figure = None
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        for attribute in WEB_ENGINE_SETTINGS:
            self.settings().setAttribute(*attribute)

        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setMinimumSize(600, 400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setUrl(QUrl.fromLocalFile(QT_PATH / "plotly.html"))
        self.loadFinished.connect(self._on_load_finished)

    def set_figure(self, figure: go.Figure):
        """Set the figure."""
        bg_color = (
            "#111111"
            if figure.layout.template.layout.mapbox.style == "dark"
            else "white"
        )
        figure = go.Figure(figure.to_dict())
        figure.update_layout(
            newshape_line_color="gold",
            modebar=dict(
                orientation="v", bgcolor=bg_color, color="gold", activecolor="#d1030d"
            ),
            dragmode="pan",
        )
        self.figure_ = figure

    def _on_load_finished(self):
        """Handle load finished."""
        if self.figure_ is None or self.figure_.data is None:
            return

        for trace in self.figure_.data:
            if isinstance(trace, go.Table):
                self.page().runJavaScript(
                    f"window.plotly_table = {json.dumps(self.figure_.to_json())}"
                )
                print("table")
                return
        self.page().runJavaScript(
            f"window.plotly_figure = {json.dumps(self.figure_.to_json())}"
        )
        print("figure")


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
        self.figure_ = figure
        self.view_.set_figure(figure)


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
        self.closing.emit()
        super().closeEvent(event)

    def sizeHint(self):
        """Return the size hint for the widget."""
        width, height = self.widget_.figure_.get_fig_size()

        return QSize(int(width), int(height))

    def get_popup(self):
        """Return the popup window."""
        return self._download_popup


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
        self._window = None

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

    def _on_download_requested(self, download_item):
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
        return width, height


class WebSocketServer(QObject):
    connected = Signal()
    disconnected = Signal()
    data_received = Signal(str)
    isatty_signal = Signal(bool)
    error = Signal(str)
    to_close = Signal(str)

    def __init__(self, parent: QWebSocketServer):
        super().__init__(parent)
        self.server = QWebSocketServer(parent.serverName(), parent.secureMode(), parent)
        self.figures: List[QtFigure] = []

        if self.server.listen(QHostAddress.LocalHost, websocket_port):
            print(f"Listening on port {self.server.serverPort()}")
        else:
            print("Error listening on port")
            sys.exit(1)

        self.server.acceptError.connect(self.onAcceptError)
        self.server.newConnection.connect(self.onNewConnection)

        # This is needed to prevent the application from closing when the last
        # window is closed.
        # This prevents the application from closing if the following conditions:
        # - The application is started from a users custom script with no running loop (SDK)
        # - The application is started from the command line (SDK)
        # - The application is started from the command line (OpenBB Terminal) and
        #   the user still has figures open
        self.isatty_signal.connect(
            lambda x: QApplication.instance().setQuitOnLastWindowClosed(x)
        )
        # We set the default value to False, so the application will not close
        # when the last window is closed. (OpenBB Terminal)
        self.isatty_signal.emit(False)
        self.clientConnection = None

    def onAcceptError(self, accept_error):
        print(f"Accept Error: {accept_error}")

    def onNewConnection(self):
        print("onNewConnection")
        self.clientConnection = self.server.nextPendingConnection()
        self.clientConnection.textMessageReceived.connect(self.processTextMessage)
        self.clientConnection.disconnected.connect(self.socketDisconnected)

    def processTextMessage(self, message):
        """Process the incoming message."""
        print("onTextMessageReceived")
        try:
            # If the message is "init", we create a figure and close it immediately.
            # This is so the first plot doesn't have to wait for the QtWebEngine to initialize.
            if message == "init":
                window = QtPlotlyFigureWindow(QtFigure())
                window.close()
                del window
                return

            if message in ["isatty", "isterminal"]:
                # We've received isatty, so we can close the application when the last
                # window is closed.
                self.isatty_signal.emit(True)
                if message == "isterminal":
                    if len(active_windows) != 0:
                        # We send a popup to the user asking if they would like to close all
                        # open windows or not.
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Question)
                        msg.setWindowTitle("OpenBB Terminal - Terminal Closed")
                        msg.setText(
                            "OpenBB Terminal has been closed, "
                            "would you like to close all remaining windows?"
                        )
                        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                        msg.resize(400, 100)
                        msg.buttonClicked.connect(self.on_to_close)
                        fig = self.figures[0]
                        fig._window.raise_()
                        fig._window._download_popup = msg

                        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
                        msg.show()
                        msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowStaysOnTopHint)
                        msg.show()
                    else:
                        print("No windows open, killing app")
                        sys.exit(qApp.quit())

                return

            data = json.loads(message)
            fig = QtFigure(data)
            self.figures.append(fig)
            fig.show()
            fig._window.closing.connect(lambda: self.on_figure_closed(fig))
            # This is needed to make sure the window opens on top of the terminal.
            # initially the window is created with the WindowStaysOnTopHint flag set,
            # but this is removed when the window is shown. This is done so the
            # window doesn't stay on top when the user clicks on the window.
            fig._window.setWindowFlags(
                fig._window.windowFlags() | Qt.WindowStaysOnTopHint
            )
            fig._window.show()
            fig._window.setWindowFlags(
                fig._window.windowFlags() & ~Qt.WindowStaysOnTopHint
            )
            fig._window.show()
        except json.JSONDecodeError:
            self.error.emit("Invalid JSON")
            return
        except Exception as e:
            self.error.emit(str(e))
            sys.exit(1)

    def socketDisconnected(self):
        print("socketDisconnected")

    def on_figure_closed(self, fig):
        print("on_figure_closed")
        self.figures.remove(fig)

    def on_to_close(self, message):
        print("on_to_close")
        if message.text() == "&Yes":
            print("Closing all windows")
            for fig in self.figures:
                fig._window.close()
            sys.exit(qApp.quit())

        print("Some figures open, quitting on last window close")


# class OpenBBRequestInterceptor(QWebEngineUrlRequestInterceptor):
#     def __init__(self, parent: "ReportsWebView" = None):
#         super().__init__(parent)
#         self._window: "ReportsWindow" = parent.parent()
#         self._widget: "ReportsWidget" = self._window.parent()

#     def interceptRequest(self, info: QWebEngineUrlRequestInfo):
#         # We make sure to open user clicked links in the default browser
#         if (
#             info.resourceType()
#             == QWebEngineUrlRequestInfo.ResourceType.ResourceTypeMainFrame
#             and info.requestMethod() == "GET"
#             and info.navigationType()
#             == QWebEngineUrlRequestInfo.NavigationType.NavigationTypeLink
#         ):
#             if info.requestUrl().scheme() != "file":
#                 QDesktopServices.openUrl(info.requestUrl())
#                 info.block(True)
#                 self._widget._view.load(self._widget._view.url())
#                 self._widget._view.reload()
#                 return None


# class ReportsWebView(QWebEngineView):
#     def __init__(self, parent: "ReportsWidget" = None):
#         super().__init__(parent)
#         self._window: "ReportsWindow" = parent.parent()
#         self._widget: "ReportsWidget" = parent
#         self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

#         for attribute in WEB_ENGINE_SETTINGS:
#             self.settings().setAttribute(*attribute)

#         self.setContextMenuPolicy(Qt.NoContextMenu)
#         self.setMinimumSize(600, 400)
#         self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         self._reports_folder = USER_REPORTS_DIRECTORY
#         self._reports_folder.mkdir(exist_ok=True)
#         self._file_system_watcher = QFileSystemWatcher()
#         self._file_system_watcher.addPath(str(self._reports_folder))
#         self._file_system_watcher.directoryChanged.connect(self.on_directory_changed)
#         self._last_report: List[Path] = [
#             max(USER_REPORTS_DIRECTORY.glob("*.html"), key=lambda x: x.stat().st_ctime)
#             if USER_REPORTS_DIRECTORY.glob("*.html")
#             else None
#         ]

#         # set download path to user directory so we can save the report
#         self.page().profile().setDownloadPath(str(USER_REPORTS_DIRECTORY / "saved"))

#         # We set up the request interceptor to make sure links are opened in the default browser
#         self.interceptor = OpenBBRequestInterceptor(self)
#         self.page().profile().setUrlRequestInterceptor(self.interceptor)
#         self.page().profile().downloadRequested.connect(self._on_download_requested)

#     def _on_download_requested(self, download_item: QWebEngineDownloadRequest):
#         print("on_download_requested")
#         if download_item.downloadFileName().endswith(".html"):
#             filedialog = QFileDialog()
#             filedialog.setFileMode(QFileDialog.FileMode.AnyFile)
#             filedialog.setNameFilter("HTML files (*.html)")
#             filedialog.setDirectory(str(USER_REPORTS_DIRECTORY))
#             filedialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
#             filedialog.setWindowTitle("Save Report")
#             filedialog.setLabelText(QFileDialog.DialogLabel.LookIn, "Look in:")
#             filedialog.setLabelText(QFileDialog.DialogLabel.FileName, "File name:")
#             filedialog.setLabelText(QFileDialog.DialogLabel.FileType, "Files of type:")
#             filedialog.setLabelText(QFileDialog.DialogLabel.Accept, "Save")
#             filedialog.setLabelText(QFileDialog.DialogLabel.Reject, "Cancel")
#             filedialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
#             filedialog.setDefaultSuffix("html")
#             filedialog.selectFile("report.html")
#             filedialog.exec()
#             self._window._widget._view.load(self._window._widget._view.url())
#             self._window._widget._view.reload()
#             self._window.show()

#             if filedialog.result() == QDialog.DialogCode.Accepted:
#                 download_item.setDownloadDirectory(filedialog.directory().path())
#                 download_item.setDownloadFileName(filedialog.selectedFiles()[0])
#                 download_item.accept()
#                 self._on_download_finished(download_item)
#             else:
#                 download_item.cancel()

#     def _on_download_finished(self, download_item: QWebEngineDownloadRequest):
#         if download_item.page() == self.page():
#             print("on_download_finished")
#             msg = QMessageBox()
#             msg.setIcon(QMessageBox.Information)
#             msg.setText("Report Saved")
#             msg.setInformativeText(
#                 f"The report has been saved to {Path(download_item.downloadDirectory()).name}"
#             )
#             msg.setStandardButtons(
#                 QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Close
#             )
#             msg.setDefaultButton(QMessageBox.StandardButton.Open)

#             msg.buttonClicked.connect(
#                 lambda x: QDesktopServices.openUrl(
#                     QUrl.fromLocalFile(download_item.downloadDirectory())
#                     if x.text() == "Open"
#                     else None
#                 )
#             )
#             msg.setWindowTitle("OpenBB - Reports")
#             msg.exec()
#             self._widget._view.load(self._widget._view.url())
#             self._widget._view.reload()

#     def on_directory_changed(self):
#         """Open the most recent report in the webview"""
#         if not USER_REPORTS_DIRECTORY.exists() or not USER_REPORTS_DIRECTORY.iterdir():
#             return
#         most_recent = max(
#             USER_REPORTS_DIRECTORY.glob("*.html"), key=lambda x: x.stat().st_ctime
#         )
#         try:
#             os.rename(most_recent, most_recent)
#         except OSError:
#             return
#         if most_recent not in self._last_report:
#             self._last_report.pop(0)
#             self._last_report.append(most_recent)
#             self._window.on_new_report.emit(str(most_recent))


# class ReportsWidget(QWidget):
#     def __init__(self, parent: "ReportsWindow" = None):
#         super().__init__(parent)
#         self._view = ReportsWebView(self)
#         self._layout = QVBoxLayout(self)
#         self._layout.addWidget(self._view)
#         self._layout.setContentsMargins(0, 0, 0, 0)
#         self.show()


# class ReportsWindow(QMainWindow):
#     on_new_report = Signal(str)
#     closing = Signal()

#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self._widget = ReportsWidget(self)
#         self.setWindowTitle("OpenBB Reports")
#         self.setWindowIcon(QIcon(str(ICON_PATH)))
#         self.setCentralWidget(self._widget._view)
#         self._view = self._widget._view
#         self.on_new_report.emit(str(self._view._last_report[0]))

#         # We resize the window to 80% of the screen size
#         screen = QGuiApplication.primaryScreen().availableGeometry()
#         if screen.width() > 1920:
#             self.resize(1920 * 0.8, 1080 * 0.8)
#         else:
#             self.resize(screen.width() * 0.8, screen.height() * 0.8)

#         active_windows.append(self)
#         self.on_new_report.connect(self._on_new_report)
#         self.closing.connect(lambda: active_windows.remove(self))

#     def _on_new_report(self, report_path: str):
#         print("on_new_report")
#         self._view.load(QUrl.fromLocalFile(report_path))
#         self.raise_()
#         self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
#         self.show()
#         self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
#         self.show()

#     def closeEvent(self, event):
#         print("closeEvent")
#         self.closing.emit()
#         event.accept()


if __name__ == "__main__":
    _create_qApp()
    serverObject = QWebSocketServer("openbb", QWebSocketServer.NonSecureMode)
    ws = WebSocketServer(serverObject)
    # reports_window = ReportsWindow()

    with _maybe_allow_interrupt(qApp):
        sys.exit(qApp.exec())

# pylint: disable=c-extension-no-member,protected-access
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
from PySide6 import QtCore, QtGui, QtNetwork, QtWebEngineCore, QtWebSockets, QtWidgets
from PySide6.QtWebEngineWidgets import QWebEngineView

from openbb_terminal.core.config.paths import USER_DATA_DIRECTORY

qApp: Optional[QtWidgets.QApplication] = None
active_windows: List["QtPlotlyFigureWindow"] = []
QT_PATH = Path(__file__).parent.resolve()

# Now use a palette to switch to dark colors:
palette = QtGui.QPalette()
palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(53, 53, 53))
palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtCore.Qt.GlobalColor.white)
palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(25, 25, 25))
palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(53, 53, 53))
palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtCore.Qt.GlobalColor.white)
palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtCore.Qt.GlobalColor.white)
palette.setColor(QtGui.QPalette.ColorRole.Text, QtCore.Qt.GlobalColor.white)
palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(53, 53, 53))
palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtCore.Qt.GlobalColor.white)
palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtCore.Qt.GlobalColor.red)
palette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(42, 130, 218))
palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(42, 130, 218))
palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtCore.Qt.GlobalColor.black)


websocket_port = 14733
# in case the port is already in use, We try to find a free port
while True:
    try:
        server = QtWebSockets.QWebSocketServer(
            "openbb", QtWebSockets.QWebSocketServer.NonSecureMode
        )
        if not server.listen(QtNetwork.QHostAddress.LocalHost, websocket_port):
            websocket_port += 1
            continue
        server.close()
        break
    except RuntimeError:
        websocket_port += 1
        continue

# We save the port and the pid of the this process in pickle file so that the frontend can access it
pickle.dump(websocket_port, open(QT_PATH / "assets/qt_socket", "wb"))
pickle.dump(os.getpid(), open(QT_PATH / "assets/qt_backend_pid", "wb"))


def _create_qApp():
    global qApp  # pylint: disable=global-statement
    if qApp is None:
        app = QtWidgets.QApplication.instance()
        if app is None:
            try:
                # AA_ShareOpenGLContexts
                QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
                    QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
                )
            except AttributeError:
                pass
            qApp = QtWidgets.QApplication(["openbb"])
            qApp.setQuitOnLastWindowClosed(True)
            qApp.setPalette(palette)
            qApp.setApplicationName("openbb")
            qApp.setApplicationVersion("2.0.0")
            qApp.setOrganizationName("OpenBB")
            qApp.setOrganizationDomain("https://openbb.co")
            qApp.setWindowIcon(QtGui.QIcon("favicon.ico"))
            try:
                import ctypes  # pylint: disable=import-outside-toplevel

                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("openbb")
            except (AttributeError, ImportError):
                pass
            except OSError:
                pass
        else:
            qApp = app
    return qApp


@contextlib.contextmanager
def _maybe_allow_interrupt(qapp: QtWidgets.QApplication):
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
        sn = QtCore.QSocketNotifier(rsock.fileno(), QtCore.QSocketNotifier.Type.Read)

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

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)
        self.figure_: go.Figure = None
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.NoContextMenu)

        self.settings().setAttribute(
            QtWebEngineCore.QWebEngineSettings.WebAttribute.WebGLEnabled, True
        )
        self.settings().setAttribute(
            QtWebEngineCore.QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,
            True,
        )
        self.settings().setAttribute(
            QtWebEngineCore.QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls,
            True,
        )
        self.settings().setAttribute(
            QtWebEngineCore.QWebEngineSettings.WebAttribute.LocalStorageEnabled, True
        )
        self.settings().setAttribute(
            QtWebEngineCore.QWebEngineSettings.WebAttribute.PluginsEnabled, True
        )

        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.setMinimumSize(600, 400)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.setUrl(QtCore.QUrl.fromLocalFile(QT_PATH / "plotly.html"))
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
            legend=dict(x=0, y=1),
            dragmode="pan",
        )
        self.figure_ = figure

    def _on_load_finished(self):
        """Handle load finished."""
        self.page().runJavaScript(
            f"window.plotly_figure = {json.dumps(self.figure_.to_json())}"
        )


class QtPlotlyFigureWidget(QtWidgets.QWidget):
    """Widget to display a plotly figure."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
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
        return QtCore.QSize(800, 600)


class QtPlotlyFigureWindow(QtWidgets.QMainWindow):
    """Window to display a plotly figure.

    Parameters
    ----------
    figure : plotly.graph_objects.Figure
        The figure to display.
    """

    on_open = QtCore.Signal()
    closing = QtCore.Signal()

    def __init__(self, figure: go.Figure):
        super().__init__()
        self.widget_ = QtPlotlyFigureWidget(self)
        self.widget_.set_figure(figure)
        self.setCentralWidget(self.widget_.view_)
        active_windows.append(self)

        self.closing.connect(lambda: active_windows.remove(self))

        self._download_popup = QtWidgets.QDialog(self)
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

    def show(self):
        """Show the window."""
        super().show()
        self.on_open.emit()
        print("Showing figure window")

    def closeEvent(self, event):
        self.closing.emit()
        super().closeEvent(event)
        self.deleteLater()

    def sizeHint(self):
        """Return the size hint for the widget."""
        height, width = self.widget_.figure_.get_fig_size()

        return QtCore.QSize(int(width), int(height))


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

            center = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
            self._window.move(
                center.x() - self._window.width() / 2 + random.randint(-100, 100),
                center.y() - self._window.height() / 2 + random.randint(-100, 100),
            )
            self._window.setWindowFlags(
                self._window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint
            )

            # Download popup window for saving plots
            download_popup = self._window._download_popup
            download_popup.setWindowTitle("OpenBB - Plot saved")
            download_popup.resize(300, 100)
            download_popup.setStyleSheet(
                "QDialog {background-color: #2d2d30; color: white;}"
                "QLabel {color: white;}"
                "QPushButton {background-color: #3d3d40; color: white;}"
                "QPushButton:hover {background-color: #4d4d50; color: white;}"
            )
            download_popup.setWindowModality(QtCore.Qt.NonModal)

            download_popup.setLayout(QtWidgets.QVBoxLayout(download_popup))
            download_popup.layout().addWidget(
                QtWidgets.QLabel("Plot saved.\n\nWould you like to open the directory?")
            )

            # Buttons for opening the directory and closing the popup
            download_popup.layout().addWidget(
                QtWidgets.QPushButton(
                    "Open", clicked=lambda: self._on_accept_open_directory()
                )
            )
            download_popup.layout().addWidget(
                QtWidgets.QPushButton("Close", clicked=lambda: download_popup.close())
            )

            self._window.widget_.view_.page().profile().downloadRequested.connect(
                self._on_download_requested
            )

        self._window.show()
        self._window.on_open.emit()

    def _on_download_requested(self, download_item):
        """Handle download requests."""
        download_item.accept()
        self._on_download_finished(download_item)

    def _on_download_finished(
        self, download_item: QtWebEngineCore.QWebEngineDownloadRequest
    ):
        """Handle download finished."""
        if isinstance(download_item, QtWebEngineCore.QWebEngineDownloadRequest):
            # We only want to show the popup if the download was initiated from the
            # figure window
            if download_item.page() == self._window.widget_.view_.page():
                self._window._download_popup.show()

    def _on_accept_open_directory(self):
        """Handle the user accepting to open the directory."""
        QtGui.QDesktopServices.openUrl(
            QtCore.QUrl.fromLocalFile(
                self._window.widget_.view_.page().profile().downloadPath()
            )
        )
        self._window._download_popup.close()

    def _on_open(self):
        """Handle the figure window being opened."""
        # Makes sure the figure is shown on top of the main window
        self._window.set_figure(self)

    def get_fig_size(self):
        """Gets the width and height of the plotly figure."""
        height = 565 if self.layout.height is None else self.layout.height
        width = 786 if self.layout.width is None else self.layout.width
        return height + 20, width + 50


class WebSocketServer(QtCore.QObject):
    connected = QtCore.Signal()
    disconnected = QtCore.Signal()
    data_received = QtCore.Signal(str)
    error = QtCore.Signal(str)

    def __init__(self, parent: QtWebSockets.QWebSocketServer):
        super().__init__(parent)
        self.server = QtWebSockets.QWebSocketServer(
            parent.serverName(), parent.secureMode(), parent
        )
        self.figures: List[QtFigure] = []

        if self.server.listen(QtNetwork.QHostAddress.LocalHost, websocket_port):
            print(f"Listening on port {self.server.serverPort()}")
        else:
            print("error")
            sys.exit(1)

        self.server.acceptError.connect(self.onAcceptError)
        self.server.newConnection.connect(self.onNewConnection)
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
        try:
            data = json.loads(message)
            fig = QtFigure(data)
            self.figures.append(fig)
            fig.show()
            fig._window.closing.connect(lambda: self.on_figure_closed(fig))
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


if __name__ == "__main__":
    openbb = _create_qApp()
    serverObject = QtWebSockets.QWebSocketServer(
        "openbb", QtWebSockets.QWebSocketServer.NonSecureMode
    )
    ws = WebSocketServer(serverObject)

    with _maybe_allow_interrupt(openbb):
        openbb.exec()

# pylint: disable=c-extension-no-member,protected-access,consider-using-with
# type: ignore
import os
import pickle
import sys
from typing import Optional

from PySide6.QtGui import QIcon
from PySide6.QtNetwork import QHostAddress
from PySide6.QtWebSockets import QWebSocketServer

from openbb_terminal.qt_app.config.qt_settings import (
    APP_PALETTE,
    ICON_PATH,
    QT_PATH,
    STYLE_SHEET,
    QApplication,
)
from openbb_terminal.qt_app.core.reports_window import ReportsFileSystemWatcher
from openbb_terminal.qt_app.core.socket_server import BackendSocketServer
from openbb_terminal.qt_app.utils import _maybe_allow_interrupt

qApp: Optional[QApplication] = None
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


if __name__ == "__main__":
    _create_qApp()
    serverObject = QWebSocketServer("openbb", QWebSocketServer.NonSecureMode)
    ws = BackendSocketServer(serverObject)
    reports = ReportsFileSystemWatcher()

    with _maybe_allow_interrupt(qApp):
        sys.exit(qApp.exec())

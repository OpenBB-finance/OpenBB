# pylint: disable=c-extension-no-member,protected-access,consider-using-with
# type: ignore
import logging
import os
import socket
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import numpy as np
import psutil
from PySide6.QtCore import Qt, QThread, QUrl, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QMainWindow, QSizePolicy, QWidget

import openbb_terminal.config_terminal as cfg
from openbb_terminal.qt_app.config.qt_settings import WEB_ENGINE_SETTINGS

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


class QtVoila(QWebEngineView):
    on_refresh = Signal()
    on_run = Signal()
    on_close = Signal()
    """
    QtVoila - A Qt for Python extension for Voila!
    """

    def __init__(self, parent=None, notebook=None):
        super().__init__(parent)
        self.widget_: VoilaRendererWidget = parent

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        for attribute in WEB_ENGINE_SETTINGS:
            self.settings().setAttribute(*attribute)

        self.setMinimumSize(600, 400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setHtml(
            "<div style='text-align:center; margin-top: 30%'><h1>Loading</h1></div>"
        )
        self.voilathread = None
        self.nbpath = None
        self.notebook = notebook

    def run_voila(self):
        """Set up notebook and run it with a dedicated Voila thread."""
        self.nbpath = self.notebook

        self.voilathread = VoilaThread(parent=self, nbpath=self.nbpath)
        self.voilathread.finished.connect(
            lambda: self.update_html(url=f"http://localhost:{self.voilathread.port}")
        )
        self.voilathread.start()

    def refresh(self):
        self.reload()

    def update_html(self, url):
        """Loads temporary HTML file and render it."""
        self.load(QUrl(url))
        self.show()

    def close_renderer(self):
        """Close current renderer"""
        if self.voilathread is not None:
            # Stop Voila thread
            self.voilathread.stop()


class VoilaThread(QThread):
    finished = Signal()

    def __init__(self, parent, nbpath):
        super().__init__()
        self.view_: QtVoila = parent
        self.nbpath = nbpath

        self.voila_process = None
        self.port = None
        self.get_free_port()

    def run(self):
        """Starts Voila thread."""
        os.system(f"jupyter trust {self.nbpath}")
        kwargs = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "stdin": subprocess.PIPE,
        }
        if os.environ.get("DEBUG"):
            kwargs = {"stdin": subprocess.PIPE}

        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["preexec_fn"] = os.setsid  # pylint: disable=no-member

        cfg.LOGGING_SUPPRESS = True
        self.voila_process = psutil.Popen(
            f"{sys.executable} -m voila --no-browser --port {self.port} {self.nbpath}",
            shell=True,
            **kwargs,
        )
        cfg.LOGGING_SUPPRESS = True
        while True:
            logger.info("waiting for voila to start")
            self.msleep(100)
            try:
                _ = urlopen(f"http://localhost:{self.port}")
                break
            except HTTPError as e:
                logger.error("Voila HttpError: %s", e)
                break
            except URLError:
                pass
        logger.info("Voila started")
        self.finished.emit()

    def get_free_port(self):
        """Searches for a random free port number."""
        not_free = True
        while not_free:
            port = np.random.randint(7000, 7999)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                res = sock.connect_ex(("localhost", port))
                if res != 0:
                    not_free = False
        self.port = port

    def stop(self):
        try:
            parent = self.voila_process
            if parent is None:
                return
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
            parent.wait()
        except psutil.NoSuchProcess:
            pass


class VoilaRendererWidget(QWidget):
    def __init__(self, parent=None, notebook=None):
        super().__init__(parent)
        self._window: VoilaWindow = parent
        self.notebook = notebook
        self._view = QtVoila(self, notebook=self.notebook)

    def run_voila(self):
        self._view.run_voila()
        self.show()


class VoilaWindow(QMainWindow):
    on_open = Signal()
    closing = Signal()

    def __init__(self, parent=None, notebook=None):
        super().__init__(parent)
        self.notebook = notebook
        self.voila = VoilaRendererWidget(self, notebook=self.notebook)
        self.setCentralWidget(self.voila)
        self.setWindowTitle("OpenBB Dashboards")

        # We resize the window to 80% of the screen size
        screen = QGuiApplication.primaryScreen().availableGeometry()
        if screen.width() > 1920:
            self.resize(1920 * 0.8, 1080 * 0.8)
        else:
            self.resize(screen.width() * 0.8, screen.height() * 0.8)

    def closeEvent(self, event):
        self.voila._view.close_renderer()
        self.closing.emit()
        event.accept()

    def resizeEvent(self, event):
        self.voila._view.resize(self.size())
        event.accept()

    def showEvent(self, event):
        self.voila.run_voila()
        event.accept()

    def reShow(self):
        self.showMinimized()
        self.setWindowState(
            self.windowState() and (not Qt.WindowMinimized or Qt.WindowActive)
        )

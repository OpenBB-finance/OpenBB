# pylint: disable=c-extension-no-member
import asyncio
import atexit
import contextlib
import os
import pickle
import subprocess
import sys
import threading
from pathlib import Path
from typing import List

import plotly.graph_objects as go
import psutil
import requests
from websockets.client import connect

QT_PATH = Path(__file__).parent.resolve()
BACKEND_RUNNING = False


class PlotsBackendError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self):
        self.message = "We've encountered an error while trying to start the Plots backend. Please try again."
        super().__init__(self.message)


def get_qt_backend_pid():
    """Returns the pid of the qt_backend process"""
    try:
        qt_backend_pid = pickle.load(open(QT_PATH / "assets/qt_backend_pid", "rb"))
    except FileNotFoundError:
        qt_backend_pid = None

    return qt_backend_pid


async def get_qt_backend_socket(retry: bool = False, error: bool = False):
    try:
        socket_port = pickle.load(open(QT_PATH / "assets/qt_socket", "rb"))
        if error:
            raise FileNotFoundError  # if there's an error, we need to run the qt_backend again
    except FileNotFoundError:
        # if the socket file is not found, the qt_backend is probably not running
        # or the socket file was deleted by the user
        # in both cases, we need to check if there's a qt_backend_pid file and try to kill the process
        # and then run the qt_backend again
        try:
            await asyncio.sleep(2)
            qt_backend_pid = get_qt_backend_pid()
            process = psutil.Process(qt_backend_pid)
            process.kill()
            run_qt_backend()
            socket_port = pickle.load(open(QT_PATH / "assets/qt_socket", "rb"))
        except FileNotFoundError as file:
            if not retry:
                socket_port = await get_qt_backend_socket(True)
            else:
                raise PlotsBackendError from file
        except psutil.NoSuchProcess as proc:
            raise PlotsBackendError from proc

    return socket_port


def run_qt_backend():
    """Runs the qt_backend.py script in a subprocess"""

    if BACKEND_RUNNING:
        return True

    qt_backend_pid = get_qt_backend_pid()

    def is_running(process_name):
        """Checks if the qt_backend is running and if the process is the same as qt_backend_pid"""
        try:
            process = psutil.Process(qt_backend_pid)
            if len(process.cmdline()) > 1 and process_name in process.cmdline()[1]:
                if process.is_running():
                    global BACKEND_RUNNING  # pylint: disable=global-statement
                    BACKEND_RUNNING = True
                    return True
        except psutil.NoSuchProcess:
            pass

        return False

    if not is_running("qt_backend.py"):
        kwargs = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}

        if os.environ.get("DEBUG", False):
            kwargs = {}

        subprocess.Popen(
            [sys.executable, "qt_backend.py"], shell=True, cwd=QT_PATH, **kwargs
        )
        return True

    return False


class QtBackend:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(QtBackend, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.socket_port: int = None
        self.figures: List[go.Figure] = []
        self.thread = None

    async def connect(self, retry: bool = False):
        """Connects to qt_backend and maintains the connection until the terminal is closed"""
        try:
            global BACKEND_RUNNING  # pylint: disable=global-statement
            if not BACKEND_RUNNING:
                run_qt_backend()
                await asyncio.sleep(1)
                self.socket_port = await get_qt_backend_socket()

            async with connect(
                f"ws://localhost:{self.socket_port}", open_timeout=6, timeout=1
            ) as websocket:
                while True:
                    if self.figures:
                        data = self.figures.pop(0)
                        await websocket.send(data.to_json())
                    await asyncio.sleep(0.1)

        except asyncio.exceptions.TimeoutError as time:
            raise PlotsBackendError from time

        except ConnectionRefusedError as conn:
            await get_qt_backend_socket(error=True)
            if not retry:
                await self.connect(True)
            else:
                BACKEND_RUNNING = False
                raise PlotsBackendError from conn

    def start(self):
        """Connect to qt_backend in a separate thread."""
        thread = threading.Thread(
            target=asyncio.run, args=(self.connect(),), daemon=True
        )
        self.thread = thread
        thread.start()

    def send_fig(self, fig: go.Figure):
        """Send figure to qt_backend."""
        if not BACKEND_RUNNING or not self.thread.is_alive():
            self.start()

        self.figures.append(fig)

    def close(self):
        """Close the connection."""
        self.thread.join()


# To avoid having plotly.js in the repo, we download it if it's not present
if not (Path(__file__).parent.resolve() / "assets/plotly.js").exists():
    download = requests.get("https://cdn.plot.ly/plotly-2.16.1.min.js", stream=True)
    with open(Path(__file__).parent.resolve() / "assets/plotly.js", "wb") as f:
        for chunk in download.iter_content(chunk_size=1024):
            f.write(chunk)


def kill_subprocess():
    """Kills the qt_backend subprocess when the terminal is closed"""
    try:
        qt_backend_pid = get_qt_backend_pid()
        process = psutil.Process(qt_backend_pid)
        process.kill()
    except psutil.NoSuchProcess:
        pass


PLOTLY_BACKEND = QtBackend()

atexit.register(kill_subprocess)

# pylint: disable=c-extension-no-member
import asyncio
import os
import pickle
import subprocess
import sys
import warnings
from pathlib import Path

import plotly.graph_objects as go
import psutil
import requests
from websockets.client import connect

QT_PATH = Path(__file__).parent.resolve()


class PlotsBackendError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self):
        self.message = "We've encountered an error while trying to start the Plots backend. Please try again."
        super().__init__(self.message)


def get_qt_backend_pid():
    try:
        qt_backend_pid = pickle.load(open(QT_PATH / "assets/qt_backend_pid", "rb"))
    except FileNotFoundError:
        qt_backend_pid = None

    return qt_backend_pid


def get_qt_backend_socket(retry: bool = False, error: bool = False):
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
            asyncio.run(asyncio.sleep(2))
            qt_backend_pid = get_qt_backend_pid()
            process = psutil.Process(qt_backend_pid)
            process.kill()
            run_qt_backend()
            socket_port = pickle.load(open(QT_PATH / "assets/qt_socket", "rb"))
        except FileNotFoundError as file:
            if not retry:
                socket_port = get_qt_backend_socket(True)
            else:
                raise PlotsBackendError from file
        except psutil.NoSuchProcess as proc:
            raise PlotsBackendError from proc

    return socket_port


def run_qt_backend():
    qt_backend_pid = get_qt_backend_pid()

    def is_running(process_name):
        """Checks if the qt_backend is running and if the process is the same as qt_backend_pid"""
        try:
            process = psutil.Process(qt_backend_pid)
            if len(process.cmdline()) > 1 and process_name in process.cmdline()[1]:
                if process.is_running():
                    return True
        except psutil.NoSuchProcess:
            pass

        return False

    if not is_running("qt_backend.py"):
        kwargs = {}
        if not os.environ.get("DEBUG", False):
            subprocess.DEVNULL = open(os.devnull, "wb")
            kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}

        subprocess.Popen(
            [sys.executable, "qt_backend.py"], shell=True, cwd=QT_PATH, **kwargs
        )

        return True

    return False


class QtBackend:
    def __init__(self):
        self.socket_port = get_qt_backend_socket()

    async def connect(self, data: dict, retry: bool = False, **kwargs):
        """Connect to server and send data."""
        try:

            async with connect(
                f"ws://localhost:{self.socket_port}", open_timeout=6, **kwargs
            ) as websocket:
                await websocket.send(data)

        except asyncio.exceptions.TimeoutError as time:
            raise PlotsBackendError from time

        except ConnectionRefusedError as conn:
            get_qt_backend_socket(error=True)
            if not retry:
                await self.connect(data, True, **kwargs)
            else:
                raise PlotsBackendError from conn

    def send_fig(self, fig: go.Figure, timeout: int = 1):
        """Connect to server and send data."""
        data = fig.to_json()

        warnings.filterwarnings("ignore", category=DeprecationWarning)
        try:
            asyncio.get_event_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())

        if asyncio.get_event_loop().is_running():
            asyncio.create_task(self.connect(data, timeout=timeout))
        else:
            asyncio.run(self.connect(data, timeout=timeout))


# To avoid having plotly.js in the repo, we download it if it's not present
if not (Path(__file__).parent.resolve() / "assets/plotly.js").exists():
    download = requests.get("https://cdn.plot.ly/plotly-2.16.1.min.js", stream=True)
    with open(
        Path(__file__).parent.resolve() / "assets/plotly.js", "wb", encoding="utf-8"
    ) as f:
        for chunk in download.iter_content(chunk_size=1024):
            f.write(chunk)

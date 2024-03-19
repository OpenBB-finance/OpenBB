import asyncio
import warnings
from queue import Queue
from typing import List

import dotenv
from openbb_core.app.constants import OPENBB_DIRECTORY
from openbb_core.env import Env

SETTINGS_ENV_FILE = OPENBB_DIRECTORY / ".env"

pywry_missing = """
[red]PyWry is not installed or missing required linux dependencies.[/]

[yellow]Install PyWry[/]
[green]pip install pywry --upgrade[/]

[yellow]Platform-specific notes[/]
Here is the underlying web engine each platform uses you might need to install.

[green]Linux[/]
Pywry uses gtk-rs and its related libraries for window creation and Wry also needs WebKitGTK for WebView.
To activate interactive plots/tables in pywry window, please make sure the following packages are installed:

[yellow]Arch Linux / Manjaro:[/]
[green]sudo pacman -S webkit2gtk[/]\n
[yellow]Debian / Ubuntu:[/]
[green]sudo apt install libwebkit2gtk-4.0-dev[/]\n
[yellow]Fedora / CentOS / AlmaLinux:[/]
[green]sudo dnf install gtk3-devel webkit2gtk3-devel[/]\r
"""


class DummyBackend:
    """Dummy class to avoid import errors."""

    __version__ = "0.0.0"

    max_retries = 0
    outgoing: List[str] = []
    init_engine: List[str] = []
    daemon = True
    debug = False
    shell = False
    base = None
    recv: Queue = Queue()

    def __new__(cls, *args, **kwargs):  # pylint: disable=W0613
        """Create a singleton instance of the backend."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)  # pylint: disable=E1120
        return cls.instance

    def __init__(self, daemon: bool = True, max_retries: int = 30):
        """Dummy init to avoid import errors."""
        self.daemon = daemon
        self.max_retries = max_retries
        try:
            self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        if Env().DEBUG_MODE:
            warnings.warn(pywry_missing)
        dotenv.set_key(SETTINGS_ENV_FILE, "PLOT_ENABLE_PYWRY", "0")

    def close(self, reset: bool = False):  # pylint: disable=W0613
        pass

    def start(self, debug: bool = False):  # pylint: disable=W0613
        pass

    def send_outgoing(self, outgoing: dict):
        pass

    async def check_backend(self):
        """Dummy check backend method to avoid errors and revert to browser."""
        raise Exception

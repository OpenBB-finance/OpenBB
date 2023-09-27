"""Backend for Plotly."""
import asyncio
import atexit
import json
import os
import re
import subprocess  # nosec: B404
import sys
from multiprocessing import current_process
from pathlib import Path
from threading import Thread
from typing import Any, Dict, Optional, Union

import aiohttp
import pandas as pd
import plotly.graph_objects as go
from packaging import version
from reportlab.graphics import renderPDF

from openbb_terminal.core.session.constants import BackendEnvironment

# pylint: disable=C0411,C0412,C0415
try:
    from pywry import PyWry
except ImportError as e:
    print(f"\033[91m{e}\033[0m")  # noqa: T201
    # pylint: disable=C0412
    from openbb_terminal.core.plots.no_import import DummyBackend

    class PyWry(DummyBackend):  # type: ignore
        pass


from svglib.svglib import svg2rlg

from openbb_terminal import config_terminal
from openbb_terminal.base_helpers import console
from openbb_terminal.core.session.current_system import get_current_system
from openbb_terminal.core.session.current_user import get_current_user

try:
    from IPython import get_ipython

    if "IPKernelApp" not in get_ipython().config:
        raise ImportError("console")
    if (
        "parent_header"
        in get_ipython().kernel._parent_ident  # pylint: disable=protected-access
    ):
        raise ImportError("notebook")
except (ImportError, AttributeError):
    JUPYTER_NOTEBOOK = False
else:
    JUPYTER_NOTEBOOK = True

PLOTS_CORE_PATH = Path(__file__).parent.resolve()
PLOTLYJS_PATH: Path = PLOTS_CORE_PATH / "assets" / "plotly-2.24.2.min.js"
BACKEND = None


class Backend(PyWry):
    """Custom backend for Plotly."""

    def __new__(cls, *args, **kwargs):  # pylint: disable=W0613
        """Create a singleton instance of the backend."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)  # pylint: disable=E1120
        return cls.instance

    def __init__(
        self,
        daemon: bool = True,
        max_retries: int = 30,
        proc_name: str = "OpenBB Terminal",
    ):
        has_version = hasattr(PyWry, "__version__")
        init_kwargs: Dict[str, Any] = dict(daemon=daemon, max_retries=max_retries)

        if has_version and version.parse(PyWry.__version__) >= version.parse("0.4.8"):
            init_kwargs.update(dict(proc_name=proc_name))

        super().__init__(**init_kwargs)

        self.plotly_html: Path = (PLOTS_CORE_PATH / "plotly.html").resolve()
        self.table_html: Path = (PLOTS_CORE_PATH / "table.html").resolve()
        self.isatty = (
            not JUPYTER_NOTEBOOK
            and sys.stdin.isatty()
            and not get_current_system().TEST_MODE
            and not get_current_user().preferences.ENABLE_QUICK_EXIT
            and current_process().name == "MainProcess"
        )
        if has_version and PyWry.__version__ == "0.0.0":
            self.isatty = False

        self.WIDTH, self.HEIGHT = 1400, 762
        self.logged_in: bool = False

        atexit.register(self.close)

    def set_window_dimensions(self):
        """Set the window dimensions."""
        current_user = get_current_user()
        width = current_user.preferences.PLOT_PYWRY_WIDTH or 1400
        height = current_user.preferences.PLOT_PYWRY_HEIGHT or 762

        self.WIDTH, self.HEIGHT = int(width), int(height)

    def get_pending(self) -> list:
        """Get the pending data that has not been sent to the backend."""
        # pylint: disable=W0201,E0203
        pending = self.outgoing + self.init_engine
        self.outgoing: list = []
        self.init_engine: list = []
        return pending

    def get_plotly_html(self) -> Path:
        """Get the plotly html file."""
        self.set_window_dimensions()
        if self.plotly_html.exists():
            return self.plotly_html

        console.print(
            "[bold red]plotly.html file not found, check the path:[/]"
            f"[green]{PLOTS_CORE_PATH / 'plotly.html'}[/]"
        )
        self.max_retries = 0  # pylint: disable=W0201
        raise FileNotFoundError

    def get_table_html(self) -> Path:
        """Get the table html file."""
        self.set_window_dimensions()
        if self.table_html.exists():
            return self.table_html
        console.print(
            "[bold red]table.html file not found, check the path:[/]"
            f"[green]{PLOTS_CORE_PATH / 'table.html'}[/]"
        )
        self.max_retries = 0  # pylint: disable=W0201
        raise FileNotFoundError

    def get_window_icon(self) -> Optional[Path]:
        """Get the window icon."""
        icon_path = PLOTS_CORE_PATH / "assets" / "Terminal_icon.png"
        if icon_path.exists():
            return icon_path
        return None

    def get_json_update(self, cmd_loc: str, theme: Optional[str] = None) -> dict:
        """Get the json update for the backend."""
        current_user = get_current_user()
        current_system = get_current_system()

        posthog: Dict[str, Any] = dict(collect_logs=current_system.LOG_COLLECT)
        if (
            current_system.LOG_COLLECT
            and current_user.profile.email
            and not self.logged_in
        ):
            self.logged_in = True
            posthog.update(
                dict(
                    user_id=current_user.profile.uuid,
                    email=current_user.profile.email,
                )
            )

        return dict(
            theme=theme or current_user.preferences.CHART_STYLE,
            log_id=current_system.LOGGING_APP_ID,
            pywry_version=self.__version__,
            terminal_version=current_system.VERSION,
            python_version=current_system.PYTHON_VERSION,
            posthog=posthog,
            command_location=cmd_loc,
        )

    def send_figure(
        self, fig: go.Figure, export_image: Optional[Union[Path, str]] = ""
    ):
        """Send a Plotly figure to the backend.

        Parameters
        ----------
        fig : go.Figure
            Plotly figure to send to backend.
        export_image : str, optional
            Path to export image to, by default ""
        """
        self.check_backend()
        # pylint: disable=C0415
        from openbb_terminal.helper_funcs import command_location

        title = "Interactive Chart"

        fig.layout.title.text = re.sub(
            r"<[^>]*>", "", fig.layout.title.text if fig.layout.title.text else title
        )

        fig.layout.height += 69

        if export_image and isinstance(export_image, str):
            export_image = Path(export_image).resolve()

        json_data = json.loads(fig.to_json())

        if config_terminal.COMMAND_ON_CHART:
            json_data.update(self.get_json_update(command_location))
        else:
            json_data.update(self.get_json_update(" "))
        outgoing = dict(
            html=self.get_plotly_html(),
            json_data=json_data,
            export_image=export_image,
            **self.get_kwargs(command_location),
        )
        self.send_outgoing(outgoing)

        if export_image and isinstance(export_image, Path):
            self.loop.run_until_complete(self.process_image(export_image))

    async def process_image(self, export_image: Path):
        """Check if the image has been exported to the path."""
        pdf = export_image.suffix == ".pdf"
        img_path = export_image.resolve()

        checks = 0
        while not img_path.exists():
            await asyncio.sleep(0.2)
            checks += 1
            if checks > 50:
                break

        if pdf:
            img_path = img_path.rename(img_path.with_suffix(".svg"))

        if img_path.exists():
            if pdf:
                drawing = svg2rlg(img_path)
                img_path.unlink(missing_ok=True)
                renderPDF.drawToFile(drawing, str(export_image))

            if get_current_user().preferences.PLOT_OPEN_EXPORT:
                if sys.platform == "win32":
                    os.startfile(export_image)  # noqa: S606  # nosec: B606
                else:
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.check_call(
                        [opener, export_image]  # nosec: B603 # noqa: S603
                    )  # nosec: B603 # noqa: S603

    def send_table(
        self,
        df_table: pd.DataFrame,
        title: str = "",
        source: str = "",
        theme: str = "dark",
    ):
        """Send table data to the backend to be displayed in a table.

        Parameters
        ----------
        df_table : pd.DataFrame
            Dataframe to send to backend.
        title : str, optional
            Title to display in the window, by default ""
        source : str, optional
            Source of the data, by default ""
        theme : light or dark, optional
            Theme of the table, by default "light"
        """
        self.check_backend()

        if title:
            # We remove any html tags and markdown from the title
            title = re.sub(r"<[^>]*>", "", title)
            title = re.sub(r"\[\/?[a-z]+\]", "", title)

        # we get the length of each column using the max length of the column
        # name and the max length of the column values as the column width
        columnwidth = [
            max(
                len(str(df_table[col].name)),
                df_table[col].astype(str).str.len().max(),
            )
            for col in df_table.columns
            if hasattr(df_table[col], "name") and hasattr(df_table[col], "dtype")
        ]

        # we add a percentage of max to the min column width
        columnwidth = [
            int(x + (max(columnwidth) - min(columnwidth)) * 0.2) for x in columnwidth
        ]

        # in case of a very small table we set a min width
        width = max(int(min(sum(columnwidth) * 9.7, self.WIDTH + 100)), 800)

        # pylint: disable=C0415
        from openbb_terminal.helper_funcs import command_location

        json_data = json.loads(df_table.to_json(orient="split", date_format="iso"))
        json_data.update(
            dict(
                title=title,
                source=source or "",
                **self.get_json_update(command_location, theme or "dark"),
            )
        )

        outgoing = dict(
            html=self.get_table_html(),
            json_data=json.dumps(json_data),
            width=width,
            height=self.HEIGHT - 100,
            **self.get_kwargs(command_location),
        )
        self.send_outgoing(outgoing)

    def send_url(
        self,
        url: str,
        title: str = "",
        width: Optional[int] = None,
        height: Optional[int] = None,
    ):
        """Send a URL to the backend to be displayed in a window.

        Parameters
        ----------
        url : str
            URL to display in the window.
        title : str, optional
            Title to display in the window, by default ""
        width : int, optional
            Width of the window, by default 1200
        height : int, optional
            Height of the window, by default 800
        """
        self.check_backend()
        script = f"""
        <script>
            window.location.replace("{url}");
        </script>
        """
        outgoing = dict(
            html=script,
            **self.get_kwargs(title),
            width=width or self.WIDTH,
            height=height or self.HEIGHT,
        )
        self.send_outgoing(outgoing)

    def get_kwargs(self, title: str = "") -> dict:
        """Get the kwargs for the backend."""
        return {
            "title": f"OpenBB - {title}",
            "icon": self.get_window_icon(),
            "download_path": str(get_current_user().preferences.USER_EXPORTS_DIRECTORY),
        }

    def start(self, debug: bool = False):  # pylint: disable=W0221
        """Start the backend WindowManager process."""
        if self.isatty:
            super().start(debug)

    def check_backend(self):
        """Override to check if isatty."""
        if not self.isatty:
            return None

        message = (
            "[bold red]PyWry version 0.5.12 or higher is required to use the "
            "OpenBB Plots backend.[/]\n"
            "[yellow]Please update pywry with 'pip install pywry --upgrade'[/]"
        )
        if not hasattr(PyWry, "__version__"):
            try:
                # pylint: disable=C0415
                from pywry import __version__ as pywry_version
            except ImportError:
                self.max_retries = 0
                return console.print(message)

            PyWry.__version__ = pywry_version  # pylint: disable=W0201

        if version.parse(PyWry.__version__) < version.parse("0.5.12"):
            self.max_retries = 0  # pylint: disable=W0201
            return console.print(message)

        if version.parse(PyWry.__version__) > version.parse("0.5.12"):
            return super().check_backend()

        try:
            return self.loop.run_until_complete(super().check_backend())
        except Exception:
            return None

    def close(self, reset: bool = False):
        """Close the backend."""
        if reset:
            self.max_retries = 50  # pylint: disable=W0201

        super().close()

    async def get_results(self, description: str) -> dict:
        """Wait for completion of interactive task and return the data.

        Parameters
        ----------
        description : str
            Description of the task to console print while waiting.

        Returns
        -------
        dict
            The data returned from pywry backend.
        """
        console.print(
            f"[green]{description}[/]\n\n"
            "[yellow]If the window is closed you can continue by pressing Ctrl+C.[/]"
        )
        while True:
            try:
                data: dict = self.recv.get(block=False) or {}
                if data.get("result", False):
                    return json.loads(data["result"])
            except Exception:  # pylint: disable=W0703 # noqa: S110
                pass

            await asyncio.sleep(1)

    def call_hub(self, login: bool = True) -> Optional[dict]:
        """Call the hub to login or logout.

        Parameters
        ----------
        login : bool, optional
            Whether to login or logout, by default True

        Returns
        -------
        Optional[dict]
            The user data if login was successful, None otherwise.
        """
        self.check_backend()
        endpoint = {True: "login", False: "logout"}[login]

        json_url = f"{BackendEnvironment.HUB_URL}{endpoint}?pywry=true"

        outgoing = dict(
            json_data=dict(url=json_url),
            **self.get_kwargs(endpoint.title()),
            width=900,
            height=800,
        )
        self.send_outgoing(outgoing)

        messages_dict = dict(
            login=dict(
                message="Welcome to OpenBB Terminal! Please login to continue.",
                interrupt="Window closed without authentication. Please proceed below.",
            ),
            logout=dict(
                message="Sending logout request", interrupt="Please login to continue."
            ),
        )

        try:
            return self.loop.run_until_complete(
                self.get_results(messages_dict[endpoint]["message"])
            )
        except KeyboardInterrupt:
            console.print(f"\n[red]{messages_dict[endpoint]['interrupt']}[/red]")
            return None


async def download_plotly_js():
    """Download or updates plotly.js to the assets folder."""
    js_filename = PLOTLYJS_PATH.name
    try:
        # we use aiohttp to download plotly.js
        # this is so we don't have to block the main thread
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session, session.get(f"https://cdn.plot.ly/{js_filename}") as resp:
            with open(str(PLOTLYJS_PATH), "wb") as f:
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)

        # We delete the old version of plotly.js
        for file in (PLOTS_CORE_PATH / "assets").glob("plotly*.js"):
            if file.name != js_filename:
                file.unlink(missing_ok=True)

    except Exception as err:  # pylint: disable=W0703
        console.print(f"Error downloading plotly.js: {err}")


def plots_backend() -> Backend:
    """Get the backend."""
    global BACKEND  # pylint: disable=W0603 # noqa
    if BACKEND is None:
        BACKEND = Backend()
    return BACKEND


# To avoid having plotly.js in the repo, we download it if it's not present
if not PLOTLYJS_PATH.exists() and not JUPYTER_NOTEBOOK:
    # We run this in a thread so we don't block the main thread
    Thread(target=asyncio.run, args=(download_plotly_js(),)).start()

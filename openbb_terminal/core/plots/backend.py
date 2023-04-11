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
from typing import Optional, Union

import aiohttp
import pandas as pd
import plotly.graph_objects as go
from packaging import version
from reportlab.graphics import renderPDF

try:
    from pywry.core import PyWry

    PYWRY_AVAILABLE = True
except ImportError as e:
    print(f"\033[91m{e}\033[0m")
    PYWRY_AVAILABLE = False

from svglib.svglib import svg2rlg

from openbb_terminal.base_helpers import console
from openbb_terminal.core.session.current_system import get_current_system
from openbb_terminal.core.session.current_user import get_current_user

if not PYWRY_AVAILABLE:
    from openbb_terminal.core.plots.no_import import DummyBackend as PyWry  # noqa

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
PLOTLYJS_PATH = PLOTS_CORE_PATH / "assets" / "plotly-2.20.0.min.js"
BACKEND = None


class Backend(PyWry):
    """Custom backend for Plotly."""

    def __new__(cls, *args, **kwargs):  # pylint: disable=W0613
        """Create a singleton instance of the backend."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)  # pylint: disable=E1120
        return cls.instance

    def __init__(self, daemon: bool = True, max_retries: int = 30):
        super().__init__(daemon=daemon, max_retries=max_retries)
        self.plotly_html: Path = (PLOTS_CORE_PATH / "plotly_temp.html").resolve()
        self.table_html: Path = (PLOTS_CORE_PATH / "table.html").resolve()
        self.inject_path_to_html()
        self.isatty = (
            not JUPYTER_NOTEBOOK
            and sys.stdin.isatty()
            and not get_current_system().TEST_MODE
            and not get_current_user().preferences.ENABLE_QUICK_EXIT
            and current_process().name == "MainProcess"
        )
        if hasattr(PyWry, "__version__") and PyWry.__version__ == "0.0.0":
            self.isatty = False

        self.WIDTH, self.HEIGHT = 1400, 762

        atexit.register(self.close)

    def set_window_dimensions(self):
        """Set the window dimensions."""
        current_user = get_current_user()
        width = current_user.preferences.PLOT_PYWRY_WIDTH or 1400
        height = current_user.preferences.PLOT_PYWRY_HEIGHT or 762

        self.WIDTH, self.HEIGHT = int(width), int(height)

    def inject_path_to_html(self):
        """Update the script tag in html with local path."""
        try:
            with open(PLOTS_CORE_PATH / "plotly.html", encoding="utf-8") as file:  # type: ignore
                html = file.read()
                html = html.replace(
                    "{{MAIN_PATH}}", str(PLOTS_CORE_PATH.as_uri())
                ).replace("{{PLOTLYJS_PATH}}", str(PLOTLYJS_PATH.as_uri()))

            # We create a temporary file to inject the path to the script tag
            # This is so we don't have to modify the original file
            # The file is deleted at program exit.
            with open(self.plotly_html, "w", encoding="utf-8") as file:  # type: ignore
                file.write(html)
        except FileNotFoundError as error:
            console.print(
                "[bold red]plotly.html file not found, check the path:[/]"
                f"[green]{PLOTS_CORE_PATH / 'plotly.html'}[/]"
            )
            self.max_retries = 0  # pylint: disable=W0201
            raise error

    def get_pending(self) -> list:
        """Get the pending data that has not been sent to the backend."""
        # pylint: disable=W0201,E0203
        pending = self.outgoing + self.init_engine
        self.outgoing: list = []
        self.init_engine: list = []
        return pending

    def get_plotly_html(self) -> str:
        """Get the plotly html file."""
        self.set_window_dimensions()
        if not self.plotly_html.exists():
            self.inject_path_to_html()
            return self.get_plotly_html()

        return str(self.plotly_html)

    def get_table_html(self) -> str:
        """Get the table html file."""
        self.set_window_dimensions()
        if self.table_html.exists():
            return str(self.table_html)
        console.print(
            "[bold red]table.html file not found, check the path:[/]"
            f"[green]{PLOTS_CORE_PATH / 'table.html'}[/]"
        )
        self.max_retries = 0  # pylint: disable=W0201
        raise FileNotFoundError

    def get_window_icon(self) -> str:
        """Get the window icon."""
        icon_path = PLOTS_CORE_PATH / "assets" / "Terminal_icon.png"
        if icon_path.exists():
            return str(icon_path)
        return ""

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
        self.loop.run_until_complete(self.check_backend())
        title = "Plots"

        # We check if figure is a subplot and has a title annotation
        if not fig.layout.title.text and fig._has_subplots():  # pylint: disable=W0212
            for annotation in fig.select_annotations(
                selector=dict(xref="paper", yref="paper")
            ):
                # Subplots always set the first annotation as the title
                # so we break after the first one
                if annotation.text:
                    title = annotation.text
                break

        title = re.sub(
            r"<[^>]*>", "", fig.layout.title.text if fig.layout.title.text else title
        )
        fig.layout.height += 69

        if export_image and isinstance(export_image, str):
            export_image = Path(export_image).resolve()

        self.outgoing.append(
            json.dumps(
                {
                    "html_path": self.get_plotly_html(),
                    "json_data": json.loads(fig.to_json()),
                    "export_image": str(export_image),
                    **self.get_kwargs(title),
                }
            )
        )
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
                    os.startfile(export_image)  # nosec: B606
                else:
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.check_call([opener, export_image])  # nosec: B603

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
        self.loop.run_until_complete(self.check_backend())

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

        json_data = json.loads(df_table.to_json(orient="split"))
        json_data.update(dict(title=title, source=source or "", theme=theme or "dark"))

        self.outgoing.append(
            json.dumps(
                {
                    "html_path": self.get_table_html(),
                    "json_data": json.dumps(json_data),
                    "width": width,
                    "height": self.HEIGHT - 100,
                    **self.get_kwargs(title),
                }
            )
        )

    def send_html(self, html_str: str = "", html_path: str = "", title: str = ""):
        """Send HTML to the backend to be displayed in a window.

        Parameters
        ----------
        html_str : str
            HTML string to send to backend.
        html_path : str, optional
            Path to html file to send to backend, by default ""
        title : str, optional
            Title to display in the window, by default ""
        """
        self.loop.run_until_complete(self.check_backend())
        message = json.dumps(
            {"html_str": html_str, "html_path": html_path, **self.get_kwargs(title)}
        )
        self.outgoing.append(message)

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
        self.loop.run_until_complete(self.check_backend())
        script = f"""
        <script>
            window.location.replace("{url}");
        </script>
        """
        message = json.dumps(
            {
                "html_str": script,
                **self.get_kwargs(title),
                "width": width or self.WIDTH,
                "height": height or self.HEIGHT,
            }
        )
        self.outgoing.append(message)

    def get_kwargs(self, title: str = "") -> dict:
        """Get the kwargs for the backend."""
        return {
            "title": f"OpenBB - {title}",
            "icon": self.get_window_icon(),
            "download_path": str(get_current_user().preferences.USER_EXPORTS_DIRECTORY),
        }

    def del_temp(self):
        """Delete the temporary html file."""
        self.plotly_html.unlink(missing_ok=True)

    def start(self, debug: bool = False):
        """Start the backend WindowManager process."""
        if self.isatty:
            super().start(debug)

    async def check_backend(self):
        """Override to check if isatty."""
        if self.isatty:
            message = (
                "[bold red]PyWry version 0.3.5 or higher is required to use the "
                "OpenBB Plots backend.[/]\n"
                "[yellow]Please update pywry with 'pip install pywry --upgrade'[/]"
            )
            if not hasattr(PyWry, "__version__"):
                try:
                    # pylint: disable=C0415
                    from pywry import __version__ as pywry_version
                except ImportError:
                    console.print(message)
                    self.max_retries = 0
                    return

                PyWry.__version__ = pywry_version  # pylint: disable=W0201

            if version.parse(PyWry.__version__) < version.parse("0.3.5"):
                console.print(message)
                self.max_retries = 0  # pylint: disable=W0201
                return
            await super().check_backend()

    def close(self, reset: bool = False):
        """Close the backend."""
        if reset:
            self.max_retries = 50  # pylint: disable=W0201
        elif self.isatty:
            self.del_temp()

        super().close(reset)


async def download_plotly_js():
    """Download or updates plotly.js to the assets folder."""
    js_filename = PLOTLYJS_PATH.name
    try:
        # we use aiohttp to download plotly.js
        # this is so we don't have to block the main thread
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            async with session.get(f"https://cdn.plot.ly/{js_filename}") as resp:
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
        print(f"Error downloading plotly.js: {err}")


# To avoid having plotly.js in the repo, we download it if it's not present
if not PLOTLYJS_PATH.exists() and not JUPYTER_NOTEBOOK:
    asyncio.run(download_plotly_js())


def plots_backend() -> Backend:
    """Get the backend."""
    global BACKEND  # pylint: disable=W0603 # noqa
    if BACKEND is None:
        BACKEND = Backend()
    return BACKEND

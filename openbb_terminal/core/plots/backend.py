import asyncio
import atexit
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union

import aiohttp
import pandas as pd
import plotly.graph_objects as go
from pywry import PyWry
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

from openbb_terminal.base_helpers import strtobool

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
PLOTLYJS_PATH = PLOTS_CORE_PATH / "assets" / "plotly-2.18.0.min.js"
BACKEND = None


class Backend(PyWry):
    """Custom backend for Plotly"""

    def __new__(cls, *args, **kwargs):  # pylint: disable=W0613
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)  # pylint: disable=E1120
        return cls.instance

    def __init__(self, daemon: bool = True, max_retries: int = 30):
        super().__init__(daemon=daemon, max_retries=max_retries)
        self.plotly_html: Path = (PLOTS_CORE_PATH / "plotly_temp.html").resolve()
        self.table_html: Path = (PLOTS_CORE_PATH / "table_temp.html").resolve()
        self.inject_path_to_html()
        self.isatty = (
            not JUPYTER_NOTEBOOK
            and sys.stdin.isatty()
            and not strtobool(os.environ.get("TEST_MODE", False))
            and not strtobool(os.environ.get("OPENBB_ENABLE_QUICK_EXIT", False))
        )

        atexit.register(self.close)

    def inject_path_to_html(self):
        """Update the script tag in html with local path"""
        for html_file, temp_file in zip(
            ["plotly.html", "table.html"], [self.plotly_html, self.table_html]
        ):
            with open(PLOTS_CORE_PATH / html_file, encoding="utf-8") as file:  # type: ignore
                html = file.read()
                html = html.replace("{{MAIN_PATH}}", str(PLOTS_CORE_PATH.as_uri()))

            # We create a temporary file to inject the path to the script tag
            # This is so we don't have to modify the original file
            # The file is deleted at program exit.
            with open(temp_file, "w", encoding="utf-8") as file:  # type: ignore
                file.write(html)

    def get_plotly_html(self) -> str:
        """Get the plotly html file"""
        if self.plotly_html and self.plotly_html.exists():
            return str(self.plotly_html)
        return ""

    def get_table_html(self) -> str:
        """Get the table html file"""
        if self.table_html and self.table_html.exists():
            return str(self.table_html)
        return ""

    def get_window_icon(self) -> str:
        """Get the window icon"""
        icon_path = PLOTS_CORE_PATH / "assets" / "icon.png"
        if icon_path.exists():
            return str(icon_path)
        return ""

    def send_figure(
        self, fig: go.Figure, export_image: Optional[Union[Path, str]] = ""
    ):
        """Send a Plotly figure to the backend

        Parameters
        ----------
        fig : go.Figure
            Plotly figure to send to backend.
        export_image : str, optional
            Path to export image to, by default ""
        """

        self.loop.run_until_complete(self.check_backend())
        title = re.sub(
            r"<[^>]*>", "", fig.layout.title.text if fig.layout.title.text else "Plots"
        )

        if export_image and isinstance(export_image, str):
            export_image = Path(export_image).resolve()

        self.outgoing.append(
            json.dumps(
                {
                    "html_path": self.get_plotly_html(),
                    "plotly": json.loads(fig.to_json()),
                    "export_image": str(export_image).replace(".pdf", ".svg"),
                    **self.get_kwargs(title),
                }
            )
        )
        if export_image and isinstance(export_image, Path):
            self.loop.run_until_complete(self.process_image(export_image))

    async def process_image(self, export_image: Path):
        """We check if the image has been exported to the path"""
        pdf = export_image.suffix == ".pdf"
        img_path = export_image.resolve()

        if pdf:
            img_path = img_path.with_suffix(".svg")

        checks = 0
        while not img_path.exists():
            await asyncio.sleep(0.2)
            checks += 1
            if checks > 50:
                break

        if img_path.exists():
            if pdf:
                drawing = svg2rlg(img_path)
                img_path.unlink(missing_ok=True)
                renderPDF.drawToFile(drawing, str(export_image))

            if sys.platform == "win32":
                os.startfile(export_image)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.check_call([opener, export_image])

    def send_table(self, df_table: pd.DataFrame, title: str = ""):
        """Sends table data to the backend to be displayed in a table.

        Parameters
        ----------
        df_table : pd.DataFrame
            Dataframe to send to backend.
        title : str, optional
            Title to display in the window, by default ""
        """
        self.loop.run_until_complete(self.check_backend())

        self.outgoing.append(
            json.dumps(
                {
                    "html_path": self.get_table_html(),
                    "plotly": df_table.to_json(orient="split"),
                    "width": 1200,
                    "height": 800,
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

    def send_url(self, url: str, title: str = "", width: int = 1200, height: int = 800):
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
                "width": width,
                "height": height,
            }
        )
        self.outgoing.append(message)

    def get_kwargs(self, title: str = "") -> dict:
        """Get the kwargs for the backend"""
        return {
            "title": f"OpenBB - {title}",
            "icon": self.get_window_icon(),
        }

    def del_temp(self):
        """Delete the temporary html file"""
        for file in (self.plotly_html, self.table_html):
            file.unlink(missing_ok=True)

    def start(self, debug: bool = False):
        """Starts the backend WindowManager process"""
        if self.isatty:
            super().start(debug)

    async def check_backend(self):
        """We override to check if isatty"""
        if self.isatty:
            await super().check_backend()

    def close(self, reset: bool = False):
        """Close the backend."""
        if reset:
            self.max_retries = 50  # pylint: disable=W0201
        else:
            self.del_temp()

        super().close(reset)


async def download_plotly_js():
    """Downloads or updates plotly.js to the assets folder"""

    js_filename = PLOTLYJS_PATH.name
    try:
        # we use aiohttp to download plotly.js
        # this is so we don't have to block the main thread
        async with aiohttp.ClientSession() as session:
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
if not PLOTLYJS_PATH.exists():
    if not JUPYTER_NOTEBOOK:
        asyncio.run(download_plotly_js())


def plots_backend() -> Backend:
    """Get the backend"""
    global BACKEND  # pylint: disable=W0603
    if BACKEND is None:
        BACKEND = Backend()
    return BACKEND

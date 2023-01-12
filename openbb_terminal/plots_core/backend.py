import atexit
import json
import os
import re
import sys
from pathlib import Path

import plotly.graph_objects as go
import requests
from pywry import PyWry

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
BACKEND = None


class Backend(PyWry):
    """Custom backend for Plotly"""

    def __new__(cls, *args, **kwargs):  # pylint: disable=W0613
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)  # pylint: disable=E1120
        return cls.instance

    def __init__(self, daemon: bool = True, max_retries: int = 30):
        super().__init__(daemon=daemon, max_retries=max_retries)
        self.plotly_html: Path = PLOTS_CORE_PATH / "plotly_temp.html"
        self.inject_path_to_html()
        self.isatty = (
            not JUPYTER_NOTEBOOK
            and sys.stdin.isatty()
            and os.environ.get("TEST_MODE", "False") != "True"
        )
        atexit.register(self.del_temp)

    def inject_path_to_html(self):
        """Update the script tag in html with local path"""
        with open(PLOTS_CORE_PATH / "plotly.html", encoding="utf-8") as file:  # type: ignore
            html = file.read()

        replace = str(PLOTS_CORE_PATH.as_uri())

        html = html.replace("{{MAIN_PATH}}", replace)

        # We create a temporary file to inject the path to the script tag
        # This is so we don't have to modify the original file
        # The file is deleted at program exit.
        with open(self.plotly_html, "w", encoding="utf-8") as file:  # type: ignore
            file.write(html)

    def get_plotly_html(self) -> str:
        """Get the plotly html file"""
        if self.plotly_html and self.plotly_html.exists():
            return str(self.plotly_html)
        return ""

    def get_window_icon(self) -> str:
        """Get the window icon"""
        icon_path = PLOTS_CORE_PATH / "assets" / "icon.png"
        if icon_path.exists():
            return str(icon_path)
        return ""

    def send_figure(self, fig: go.Figure):
        """Send a Plotly figure to the backend

        Parameters
        ----------
        fig : go.Figure
            Plotly figure to send to backend.
        """
        self.check_backend()
        title = re.sub(
            r"<[^>]*>", "", fig.layout.title.text if fig.layout.title.text else "Plots"
        )

        data = json.loads(fig.to_json())
        self.outgoing.append(
            json.dumps(
                {
                    "html_path": self.get_plotly_html(),
                    "plotly": data,
                    "title": f"OpenBB - {title}",
                    "icon": self.get_window_icon(),
                }
            )
        )

    def del_temp(self):
        """Delete the temporary html file"""
        if self.plotly_html:
            self.plotly_html.unlink(missing_ok=True)

    def start(self, debug: bool = False):
        """Starts the backend WindowManager process"""
        if self.isatty:
            super().start(debug)


# To avoid having plotly.js in the repo, we download it if it's not present
if not (PLOTS_CORE_PATH / "assets" / "plotly.js").exists():
    download = requests.get("https://cdn.plot.ly/plotly-2.16.1.min.js", stream=True)

    with open(str(PLOTS_CORE_PATH / "assets" / "plotly.js"), "wb") as f:
        for chunk in download.iter_content(chunk_size=1024):
            f.write(chunk)


def get_backend() -> Backend:
    """Get the backend"""
    global BACKEND  # pylint: disable=W0603
    if BACKEND is None:
        BACKEND = Backend()
    return BACKEND

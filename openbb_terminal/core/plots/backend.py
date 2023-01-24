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

        html = html.replace("{{MAIN_PATH}}", str(PLOTS_CORE_PATH.as_uri()))

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
        self.outgoing.append(
            json.dumps(
                {
                    "html_path": self.get_plotly_html(),
                    "plotly": json.loads(fig.to_json()),
                    **self.get_kwargs(title),
                }
            )
        )

    def send_html(self, html_str: str, html_path: str = "", title: str = ""):
        """Send html to backend.

        Parameters
        ----------
        html_str : str
            HTML string to send to backend.
        html_path : str, optional
            Path to html file to send to backend, by default ""
        title : str, optional
            Title to display in the window, by default ""
        """
        self.check_backend()
        message = json.dumps(
            {"html_str": html_str, "html_path": html_path, **self.get_kwargs(title)}
        )
        self.outgoing.append(message)

    def send_url(self, url: str, title: str = "", width: int = 1200, height: int = 800):
        """Send url to backend.

        Parameters
        ----------
        url : str
            URL to send to backend.
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

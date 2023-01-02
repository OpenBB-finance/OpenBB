import atexit
import json
import re
from pathlib import Path

import plotly.graph_objects as go
import requests
from pywry import PyWry


class Backend(PyWry):
    """Custom backend for Plotly"""

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Backend, cls).__new__(cls)
        return cls.instance

    def __init__(self, daemon: bool = True, max_retries: int = 30):
        super().__init__(daemon=daemon, max_retries=max_retries)
        self.plotly_html = None
        self.inject_path_to_html(Path(__file__).parent.resolve() / "plotly.html")

    def inject_path_to_html(self, path: Path):
        """Update the script tag in html with local path"""
        with open(path, "r", encoding="utf-8") as file:
            html = file.read()

        replace = str(path.parent.resolve().as_posix())

        html = html.replace("{{MAIN_PATH}}", replace)

        # We create a temporary file to inject the path to the script tag
        # This is so we don't have to modify the original file
        # The file is deleted at program exit.
        self.plotly_html = path.parent.resolve() / "plotly_temp.html"
        with open(self.plotly_html, "w", encoding="utf-8") as file:
            file.write(html)

    def get_plotly_html(self) -> str:
        """Get the plotly html file"""
        if self.plotly_html and self.plotly_html.exists():
            return str(self.plotly_html)
        return ""

    def get_window_icon(self) -> str:
        """Get the window icon"""
        icon_path = Path(__file__).parent.resolve() / "assets" / "icon.png"
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
                    "html": self.get_plotly_html(),
                    "plotly": data,
                    "title": f"OpenBB - {title}",
                    "icon": self.get_window_icon(),
                }
            )
        )

    def close(self):
        """Close the backend and delete the temporary html file"""
        if self.plotly_html:
            self.plotly_html.unlink(missing_ok=True)


# To avoid having plotly.js in the repo, we download it if it's not present
if not (Path(__file__).parent.resolve() / "assets" / "plotly.js").exists():
    download = requests.get("https://cdn.plot.ly/plotly-2.16.1.min.js", stream=True)
    with open(
        Path(__file__).parent.resolve() / "assets" / "plotly.js", "wb", encoding="utf-8"
    ) as f:
        for chunk in download.iter_content(chunk_size=1024):
            f.write(chunk)


BACKEND = Backend()


atexit.register(BACKEND.close)

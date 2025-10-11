"""Backend for Plotly."""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from openbb_core.app.model.charts.charting_settings import ChartingSettings
    from pandas import DataFrame
    from plotly.graph_objs import Figure

PLOTS_CORE_PATH = Path(__file__).parent.resolve()
PLOTLYJS_PATH = PLOTS_CORE_PATH / "assets" / "plotly-3.1.0.min.js"
BACKEND = None

try:
    from pywry import PyWry  # pylint: disable=import-outside-toplevel
except ImportError:
    from .dummy_backend import DummyBackend  # pylint: disable=import-outside-toplevel

    class PyWry(DummyBackend):  # type: ignore
        """Dummy backend for charts."""


class Backend(PyWry):
    """Custom backend for Plotly."""

    def __new__(cls, *args, **kwargs):  # pylint: disable=W0613
        """Create a singleton instance of the backend."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)  # pylint: disable=E1120
        return cls.instance

    def __init__(
        self,
        charting_settings: "ChartingSettings",
        daemon: bool = True,
        max_retries: int = 30,
        proc_name: str = "OpenBB Platform",
    ):
        """Create a new instance of the backend."""
        # pylint: disable=import-outside-toplevel
        import atexit  # noqa
        import sys  # noqa
        from multiprocessing import current_process  # noqa
        from packaging import version  # noqa

        self.charting_settings = charting_settings
        has_version = hasattr(PyWry, "__version__")
        init_kwargs: dict[str, Any] = dict(daemon=daemon, max_retries=max_retries)

        if has_version and version.parse(PyWry.__version__) >= version.parse("0.4.8"):
            init_kwargs.update(dict(proc_name=proc_name))

        super().__init__(**init_kwargs)

        try:
            from IPython import get_ipython  # pylint: disable=import-outside-toplevel

            if "IPKernelApp" not in get_ipython().config:
                raise ImportError("console")
            if (
                "parent_header" in get_ipython().kernel._parent_ident
            ):  # pylint: disable=protected-access
                raise ImportError("notebook")
        except (ImportError, AttributeError):
            JUPYTER_NOTEBOOK = False
        else:
            JUPYTER_NOTEBOOK = True

        self.plotly_html: Path = (PLOTS_CORE_PATH / "plotly.html").resolve()
        self.table_html: Path = (PLOTS_CORE_PATH / "table.html").resolve()
        self.isatty = (
            not JUPYTER_NOTEBOOK
            and sys.stdin.isatty()
            and current_process().name == "MainProcess"
        )
        if has_version and PyWry.__version__ == "0.0.0":
            self.isatty = False

        self.WIDTH, self.HEIGHT = 1400, 762

        atexit.register(self.close)

    def set_window_dimensions(self):
        """Set the window dimensions."""
        width = 1400
        height = 762

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
        # pylint: disable=import-outside-toplevel
        import warnings

        self.set_window_dimensions()
        if self.plotly_html.exists():
            return self.plotly_html

        warnings.warn(
            f"[bold red]plotly.html file not found, check the path:[/][green]{PLOTS_CORE_PATH / 'plotly.html'}[/]"
        )
        self.max_retries = 0  # pylint: disable=W0201
        raise FileNotFoundError

    def get_table_html(self) -> Path:
        """Get the table html file."""
        # pylint: disable=import-outside-toplevel
        import warnings

        self.set_window_dimensions()
        if self.table_html.exists():
            return self.table_html
        warnings.warn(
            f"[bold red]table.html file not found, check the path:[/][green]{PLOTS_CORE_PATH / 'table.html'}[/]"
        )
        self.max_retries = 0  # pylint: disable=W0201
        raise FileNotFoundError

    def get_window_icon(self) -> Path | None:
        """Get the window icon."""
        icon_path = PLOTS_CORE_PATH / "assets" / "Terminal_icon.png"
        if icon_path.exists():
            return icon_path
        return None

    def get_json_update(
        self,
        cmd_loc: str | None = None,
        theme: str | None = None,
    ) -> dict:
        """Get the json update for the backend."""

        return dict(
            theme=theme or self.charting_settings.chart_style,
            pywry_version=self.__version__,
            platform_version=self.charting_settings.version,
            python_version=self.charting_settings.python_version,
            command_location=cmd_loc,
        )

    def send_figure(
        self,
        fig: "Figure",
        export_image: Path | str | None = "",
        command_location: str | None = "",
    ):
        """Send a Plotly figure to the backend.

        Parameters
        ----------
        fig : Figure
            Plotly figure to send to backend.
        export_image : str, optional
            Path to export image to, by default ""
        command_location : str, optional
            Location of the command, by default "".
            We can use the route here to display it on the chart title.
        """
        # pylint: disable=import-outside-toplevel
        import asyncio
        import json
        import re

        self.check_backend()
        # pylint: disable=C0415

        paper_bg = (
            "rgba(0,0,0,0)"
            if self.charting_settings.chart_style == "dark"
            else "rgba(255,255,255,0)"
        )
        title = "OpenBB Platform"
        fig.layout.title.text = re.sub(
            r"<[^>]*>", "", fig.layout.title.text if fig.layout.title.text else title
        )
        fig.layout.height += 69

        export_image = Path(export_image).resolve() if export_image else None

        json_data = json.loads(fig.to_json())
        json_data.update(self.get_json_update(command_location))
        json_data["layout"]["paper_bgcolor"] = paper_bg

        outgoing = dict(
            html=self.get_plotly_html(),
            json_data=json_data,
            export_image=export_image,
            **self.get_kwargs(command_location),
        )
        self.send_outgoing(outgoing)

        if export_image:
            if self.loop.is_closed():  # type: ignore[has-type]
                # Create a new event loop
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)

            self.loop.run_until_complete(self.process_image(export_image))

    async def process_image(self, export_image: Path):
        """Check if the image has been exported to the path."""
        # pylint: disable=import-outside-toplevel
        import asyncio
        import subprocess
        import sys

        img_path = export_image.resolve()

        checks = 0
        while not img_path.exists():
            await asyncio.sleep(0.2)
            checks += 1
            if checks > 50:
                break

        if img_path.exists():  # noqa: SIM102
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.check_call([opener, export_image])  # nosec: B603 # noqa: S603

    def send_table(  # pylint: disable=too-many-positional-arguments
        self,
        df_table: "DataFrame",
        title: str = "",
        source: str = "",
        theme: str = "dark",
        command_location: str | None = "",
    ):
        """Send table data to the backend to be displayed in a table.

        Parameters
        ----------
        df_table : DataFrame
            Dataframe to send to backend.
        title : str, optional
            Title to display in the window, by default ""
        source : str, optional
            Source of the data, by default ""
        theme : light or dark, optional
            Theme of the table, by default "light"
        """
        # pylint: disable=import-outside-toplevel
        import json
        import re

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
        width: int | None = None,
        height: int | None = None,
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

    def get_kwargs(self, title: str | None = "") -> dict:
        """Get the kwargs for the backend."""
        return {
            "title": "OpenBB Platform" + (f" - {title}" if title else ""),
            "icon": self.get_window_icon(),
            "download_path": str(self.charting_settings.user_exports_directory),
        }

    def start(self, debug: bool = False, headless: bool = False):
        """Start the backend WindowManager process."""
        if self.isatty:
            super().start(debug, headless)

    def check_backend(self):
        """Override to check if isatty."""
        # pylint: disable=import-outside-toplevel
        import warnings  # noqa
        from packaging import version  # noqa

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
                return warnings.warn(message)

            PyWry.__version__ = pywry_version  # pylint: disable=W0201

        if version.parse(PyWry.__version__) < version.parse("0.5.12"):
            self.max_retries = 0  # pylint: disable=W0201
            return warnings.warn(message)

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


async def download_plotly_js():
    """Download or updates plotly.js to the assets folder."""
    # pylint: disable=import-outside-toplevel
    import aiohttp  # noqa
    import warnings  # noqa

    js_filename = PLOTLYJS_PATH.name
    try:
        # we use aiohttp to download plotly.js
        # this is so we don't have to block the main thread
        async with (
            aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=False), trust_env=True
            ) as session,
            session.get(f"https://cdn.plot.ly/{js_filename}") as resp,
        ):
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
        warnings.warn(f"Error downloading plotly.js: {err}")


def create_backend(charting_settings: Optional["ChartingSettings"] = None):
    """Create the backend."""
    # pylint: disable=import-outside-toplevel
    import importlib

    charting_module = importlib.import_module(
        "openbb_core.app.model.charts.charting_settings", "charting_settings"
    )

    ChartingSettings = charting_module.ChartingSettings
    charting_settings = charting_settings or ChartingSettings()
    global BACKEND  # pylint: disable=W0603 # noqa
    if BACKEND is None:
        BACKEND = Backend(charting_settings)


def get_backend():
    """Get the backend instance."""
    if BACKEND is None:
        create_backend()
    return BACKEND

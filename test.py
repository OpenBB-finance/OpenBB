import asyncio
import atexit
import base64
import io
import json
import sys
from multiprocessing import current_process
from pathlib import Path
from timeit import default_timer as timer

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

# from kaleido.scopes.plotly import PlotlyScope
from PIL import Image
from pywry import PyWry

# from openbb_terminal.core.plots.backend import PLOTLYJS_PATH

# kaleido_scope = PlotlyScope(plotlyjs=PLOTLYJS_PATH)
# kaleido_scope.chromium_args += ("--disable-dev-shm-usage", "--no-sandbox")
# kaleido_scope.default_width = None
# kaleido_scope.default_height = None
BACKEND = None


# We create a custom backend for PyWry that will be used to display the figure in the
# window. This backend is a singleton, so it will only be created once, and will be
# shared across all modules that import it.
class Backend(PyWry):
    """Custom backend for PyWry."""

    def __new__(cls, *args, **kwargs):  # pylint: disable=W0613
        """Create a singleton instance of the backend."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)  # pylint: disable=E1120
        return cls.instance

    def __init__(
        self,
        daemon: bool = True,
        max_retries: int = 30,
        proc_name: str = "PyWry Backend",
    ):
        super().__init__(daemon=daemon, max_retries=max_retries, proc_name=proc_name)
        self.isatty = sys.stdin.isatty() and current_process().name == "MainProcess"
        self.plotly_html = Path(__file__).parent / "main.html"
        atexit.register(self.close)

    def get_plotly_html(self) -> Path:
        """Get the path to the Plotly HTML file."""
        if self.plotly_html.exists():
            return self.plotly_html

        self.max_retries = 0  # pylint: disable=W0201
        raise FileNotFoundError(f"Plotly HTML file not found at {self.plotly_html}.")

    def send_figure(self, fig: go.Figure):
        """Send a Plotly figure to the backend.

        Parameters
        ----------
        fig : go.Figure
            Plotly figure to send to backend.
        """
        self.loop.run_until_complete(self.check_backend())
        title = fig.layout.title.text if fig.layout.title else "Plotly Figure"

        json_data = json.loads(fig.to_json())

        outgoing = dict(
            html_path=self.get_plotly_html(),
            json_data=json_data,
            title=title,
            download_path=Path.cwd(),
        )
        self.send_outgoing(outgoing)

    def figure_write_image(
        self, fig: go.Figure, img_format: str = "png", scale=1
    ) -> dict:
        """Convert a Plotly figure to an image.

        Parameters
        ----------
        fig : go.Figure
            Plotly figure to convert to image.
        format : str, optional
            Image format, by default "png"
        """
        self.loop.run_until_complete(self.check_backend())

        json_data = json.loads(fig.to_json())
        json_data["scale"] = scale

        outgoing = dict(
            json_data=json_data,
            export_image=f"plotly_image.{img_format}",
        )
        self.send_outgoing(outgoing)

        incoming = self.recv.get(timeout=5)
        if incoming.get("result", None):
            return incoming.get("result")
        else:
            raise RuntimeError("Error converting figure to image.")

    def figure_to_image(self, fig: go.Figure, img_format: str = "png", scale=1) -> dict:
        """Convert a Plotly figure to an image.

        Parameters
        ----------
        fig : go.Figure
            Plotly figure to convert to image.
        format : str, optional
            Image format, by default "png"
        """
        self.loop.run_until_complete(self.check_backend())

        json_data = json.loads(fig.to_json())

        outgoing = dict(
            json_data=json_data,
            export_image=f"plotly_image.{img_format}",
        )
        self.send_outgoing(outgoing)

        incoming = self.recv.get(timeout=5)
        if incoming.get("result", None):
            img = incoming.get("result")
            img_kal = Image.open(
                io.BytesIO(base64.b64decode(img)), formats=[img_format]
            )
            img_kal.save(f"plotly_image.{img_format}", img_format)
        else:
            raise RuntimeError("Error converting figure to image.")

    def start(self, debug: bool = False, headless: bool = False):
        """Start the backend WindowManager process.

        Parameters
        ----------
        debug : bool, optional
            Whether to start in debug mode to see the output and
            enable dev tools in the browser, by default False
        headless : bool, optional
            Whether to start in headless mode for ploty static image export, by default False
        """
        if self.isatty:
            super().start(debug=debug, headless=headless)

    async def check_backend(self):
        """Override to check if isatty."""
        if self.isatty:
            await super().check_backend()


pywry_backend = Backend()
pywry_backend.start(False, True)


# We create a custom figure class that inherits from Plotly's Figure class.
# This allows us to add custom show method that will send the figure to the
# backend if running in a TTY terminal.
class PyWryFigure(go.Figure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_layout(
            template="plotly_dark",
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
            dragmode="pan",
            hovermode="closest",
        )

    def show(self, *args, **kwargs):
        if pywry_backend.isatty:
            try:
                # We send the figure to the backend to be displayed
                return pywry_backend.send_figure(self)
            except Exception:
                pass

        return pio.show(self, *args, **kwargs)

    def pywry_write_image(self, img_format="png", scale=1):
        if pywry_backend.isatty:
            try:
                # We send the figure to the backend to be displayed
                return pywry_backend.figure_write_image(
                    self, img_format=img_format, scale=scale
                )
            except Exception:
                pass


class Main:
    async def main_loop(self):
        while True:
            await asyncio.sleep(1)

    def run(self):
        fig = PyWryFigure()
        fig.add_scatter(y=np.random.randn(10_000), mode="markers")
        fig.add_scatter(y=np.random.randn(10_000) + 1, mode="markers")
        fig.add_scatter(y=np.random.randn(10_000) + 2, mode="markers")
        fig.update_layout(title="Plotly Figure", width=1400, height=762)

        pywry_start = timer()
        img = fig.pywry_write_image(scale=1.8, img_format="png")

        if img:
            imgbytes = io.BytesIO(base64.b64decode(img))
            img_kal = Image.open(imgbytes)
            img_kal.save("test_pywry1.png")
        timer()
        print(f"\nPyWry  : {timer() - pywry_start} seconds")

        # kal_start = timer()
        # kal_img = kaleido_scope.transform(
        #     fig, scale=1.8, height=762, width=1400, format="png"
        # )

        # imgbytes = io.BytesIO(kal_img)
        # img_kal = Image.open(imgbytes)
        # img_kal.save("test_kal1.png")
        # kal_end = timer()
        # print(f"Kaleido: {timer() - kal_start} seconds")

        # calculate the difference in time between the two methods
        # faster = kal_end - kal_start < pywry_end - pywry_start
        # gain = (
        #     (pywry_end - pywry_start) / (kal_end - kal_start)
        #     if faster
        #     else (kal_end - kal_start) / (pywry_end - pywry_start)
        # )
        # if faster:
        #     print(f"Kaleido is {gain:.2f}x faster than PyWry\n")
        # else:
        #     print(f"\033[93mPyWry is {gain:.2f}x faster than Kaleido\033[0m\n")
        pywry_start = timer()
        img = fig.pywry_write_image(scale=1.8, img_format="png")

        if img:
            imgbytes = io.BytesIO(base64.b64decode(img))
            img_kal = Image.open(imgbytes)
            img_kal.save("test_pywry2.png")
        timer()
        print(f"PyWry  : {timer() - pywry_start} seconds")

        # kal_start = timer()
        # kal_img = kaleido_scope.transform(
        #     fig, scale=1.8, height=762, width=1400, format="png"
        # )

        # imgbytes = io.BytesIO(kal_img)
        # img_kal = Image.open(imgbytes)
        # img_kal.save("test_kal2.png")
        # kal_end = timer()
        # print(f"Kaleido: {timer() - kal_start} seconds")

        # calculate the difference in time between the two methods
        # faster = kal_end - kal_start < pywry_end - pywry_start
        # gain = (
        #     (pywry_end - pywry_start) / (kal_end - kal_start)
        #     if faster
        #     else (kal_end - kal_start) / (pywry_end - pywry_start)
        # )
        # if faster:
        #     print(f"Kaleido is {gain:.2f}x faster than PyWry\n")
        # else:
        #     print(f"\033[93mPyWry is {gain:.2f}x faster than Kaleido\033[0m\n")

        pywry_start = timer()
        img = fig.pywry_write_image(scale=1.8, img_format="png")

        if img:
            imgbytes = io.BytesIO(base64.b64decode(img))
            img_kal = Image.open(imgbytes)
            img_kal.save("test_pywry3.png")
        timer()
        print(f"PyWry  : {timer() - pywry_start} seconds")

        # kal_start = timer()
        # kal_img = kaleido_scope.transform(
        #     fig, scale=1.8, height=762, width=1400, format="png"
        # )

        # imgbytes = io.BytesIO(kal_img)
        # img_kal = Image.open(imgbytes)
        # img_kal.save("test_kal3.png")
        # kal_end = timer()
        # print(f"Kaleido: {timer() - kal_start} seconds")

        # calculate the difference in time between the two methods
        # faster = kal_end - kal_start < pywry_end - pywry_start
        # gain = (
        #     (pywry_end - pywry_start) / (kal_end - kal_start)
        #     if faster
        #     else (kal_end - kal_start) / (pywry_end - pywry_start)
        # )
        # if faster:
        #     print(f"Kaleido is {gain:.2f}x faster than PyWry\n")
        # else:
        #     print(f"\033[93mPyWry is {gain:.2f}x faster than Kaleido\033[0m\n")

        pywry_backend.loop.run_until_complete(self.main_loop())


if __name__ == "__main__":
    try:
        # PyWry creates a new thread for the backend,
        # so we need to run the main loop in the main thread.
        asyncio.create_task(Main().run())
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
        sys.exit(0)

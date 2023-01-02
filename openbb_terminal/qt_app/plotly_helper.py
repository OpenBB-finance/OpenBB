from io import BytesIO
from pathlib import Path
from typing import List, Union

import plotly.graph_objects as go
import requests
from PIL import Image
from plotly.subplots import make_subplots

# pylint: disable=unused-import
from openbb_terminal.qt_app.config import openbb_styles as theme  # noqa: F401


# pylint: disable=R0913
class OpenBBFigure(go.Figure):
    """Helper class for creating Plotly figures"""

    def __init__(self, is_subplots: bool = False, fig: go.Figure = None, **kwargs):
        super().__init__()
        if fig:
            self.__dict__ = fig.__dict__

        self._is_subplots = is_subplots
        xaxis: dict = kwargs.pop("xaxis", None)
        yaxis: dict = kwargs.pop("yaxis", None)

        if (xaxis := kwargs.pop("xaxis", None)) or (yaxis := kwargs.pop("yaxis", None)):
            self.update_xaxes(xaxis)
            self.update_yaxes(yaxis)

        self.update_layout(
            margin=dict(l=20, r=60, t=40, b=20, autoexpand=True),
            height=762,
            width=1400,
            **kwargs,
        )

    @property
    def is_subplots(self):
        return self._is_subplots

    @is_subplots.setter
    def is_subplots(self, value):
        self._is_subplots = value

    def _set_openbb_overlays(self):
        # pylint: disable=C0415
        from openbb_terminal.helper_funcs import command_location

        if command_location:
            yaxis = self.layout.yaxis
            yaxis2 = self.layout.yaxis2 if hasattr(self.layout, "yaxis2") else None
            xshift = -80 if yaxis.side == "right" else -130

            if yaxis2 and yaxis.side == "right" and yaxis2.overlaying == "y":
                xshift = -110

            self.add_annotation(
                x=0,
                y=0.5,
                yref="paper",
                xref="paper",
                text=command_location,
                textangle=-90,
                font_size=24,
                font_color="gray",
                opacity=0.5,
                yanchor="middle",
                xanchor="left",
                xshift=xshift,
                showarrow=False,
            )

        self.add_annotation(
            yref="y domain" if not self.is_subplots else "paper",
            xref="x domain",
            x=1,
            y=0,
            text="OpenBB Terminal",
            font_size=17,
            font_color="gray",
            opacity=0.5,
            xanchor="right",
            yanchor="bottom",
            showarrow=False,
            yshift=-80,
            xshift=40,
        )

    def set_title(self, title: str, **kwargs):
        """Set the title of the figure"""
        self.update_layout(title=title, **kwargs)

    @classmethod
    def create_subplots(
        cls,
        rows: int = 1,
        cols: int = 1,
        shared_xaxes: bool = True,
        vertical_spacing: float = None,
        horizontal_spacing: float = None,
        subplot_titles: Union[List[str], tuple] = None,
        row_width: List[Union[float, int]] = None,
        specs: List[List[dict]] = None,
        **kwargs,
    ):
        """Create a new Plotly figure with subplots"""
        fig = make_subplots(
            rows=rows,
            cols=cols,
            shared_xaxes=shared_xaxes,
            vertical_spacing=vertical_spacing,
            horizontal_spacing=horizontal_spacing,
            subplot_titles=subplot_titles,
            row_width=row_width,
            specs=specs,
            **kwargs,
        )
        return cls(is_subplots=True, fig=fig)

    def add_text(
        self,
        x: Union[int, float],
        y: Union[int, float],
        text: str,
        xref: str = "x",
        yref: str = "y",
        **kwargs,
    ):
        """Add text to the figure"""
        if "showarrow" not in kwargs:
            kwargs["showarrow"] = False

        self.add_annotation(dict(xref=xref, yref=yref, x=x, y=y, text=text, **kwargs))

    def layout_image(
        self,
        x: Union[int, float],
        y: Union[int, float],
        sizex: Union[int, float],
        sizey: Union[int, float],
        source: str,
        xref: str = "x",
        yref: str = "y",
        **kwargs,
    ):
        """Add an image to the plot"""
        if source.startswith("http"):
            image = Image.open(BytesIO(requests.get(source).content))
        else:
            image = Image.open(Path(source).resolve())

        self.add_layout_image(
            dict(
                source=image,
                xref=xref,
                yref=yref,
                x=x,
                y=y,
                sizex=sizex,
                sizey=sizey,
                **kwargs,
            )
        )
        image.close()

    def show(self, *args, **kwargs):
        """Show the figure"""
        self._set_openbb_overlays()
        super().show(*args, **kwargs)

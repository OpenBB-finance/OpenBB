""" Finviz View """
__docformat__ = "numpy"


import io
import logging

from PIL import Image

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.technical_analysis import finviz_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def view(symbol: str, external_axes: bool = False):
    """View finviz image for ticker

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    external_axes: bool, optional
        Whether to return the figure object or not, by default False
    """

    image_data = finviz_model.get_finviz_image(symbol)
    dataBytesIO = io.BytesIO(image_data)
    im = Image.open(dataBytesIO)
    fig = OpenBBFigure()
    fig.add_layout_image(
        dict(
            source=im,
            xref="x",
            yref="y",
            x=0,
            y=1,
            sizex=im.width,
            sizey=im.height,
            sizing="stretch",
        )
    )
    fig.update_xaxes(visible=False, range=[0, im.width])
    fig.update_yaxes(visible=False, range=[im.height, 0], scaleanchor="y")
    fig.update_layout(height=im.height, width=im.width)

    return fig.show(external=external_axes)

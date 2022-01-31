"""Finviz model"""
__docformat__ = "numpy"

import logging

import requests
from finvizfinance.quote import finvizfinance
from finvizfinance.util import headers

from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_finviz_image(ticker: str) -> bytes:
    """Get finviz image for given ticker

    Parameters
    ----------
    ticker : str
        ticker

    Returns
    -------
    bytes
        Image in byte format
    """
    stock = finvizfinance(ticker)
    image_url = stock.TickerCharts(urlonly=True)

    r = requests.get(image_url, stream=True, headers=headers, timeout=5)
    r.raise_for_status()
    r.raw.decode_content = True
    return r.content

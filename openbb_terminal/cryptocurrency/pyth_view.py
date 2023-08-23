# pylint: disable= C0301

import asyncio
import logging

from openbb_terminal.cryptocurrency.pyth_model import get_price
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_price(symbol: str) -> None:
    """Displays live price from pyth live feed [Source: https://pyth.network/]

    Parameters
    ----------
    symbol : str
        Symbol of the asset to get price for
    """
    try:
        while True:
            price, confidence, previous_price = asyncio.run(get_price(symbol))
            console.print(
                f"{symbol} = {'[red]' if previous_price >= price else '[green]'}"
                f"{price}{'[/red]' if previous_price >= price else '[/green]'} ± {confidence}",
                end="\r",
            )
    except KeyboardInterrupt:
        console.print(f"\n\nStopped watching {symbol} price and confidence interval\n")

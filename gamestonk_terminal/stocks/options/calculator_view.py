import logging
from typing import Dict, Optional, List

from matplotlib import pyplot as plt

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.options import calculator_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def view_calculator(
    strike: float,
    premium: float,
    put: bool,
    sell: bool,
    external_axes: Optional[List[plt.Axes]] = None,
    **kwargs: Dict[str, int],
):
    """

    Parameters
    ----------
    strike: float
        Strike price
    premium: float
        Premium
    put: bool
        Whether option is put
    sell:
        Whether selling option
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    kwargs: Dict[str,int]
    """

    price_at_expiry, pnl, break_even = calculator_model.pnl_calculator(
        strike, premium, put, sell, **kwargs
    )

    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(price_at_expiry, pnl, alpha=0.1, c="k")
    ax.fill_between(
        price_at_expiry, 0, pnl, where=(pnl > 0), facecolor="green", alpha=0.5
    )
    ax.fill_between(
        price_at_expiry, 0, pnl, where=(pnl < 0), facecolor="red", alpha=0.5
    )
    ax.axvline(x=break_even, lw=3, alpha=0.6, label=f"Breakeven: ${break_even}")
    ax.axvline(x=strike, lw=3, alpha=0.6, label=f"Strike: ${strike}")
    if sell:
        ax.axhline(
            y=100 * premium,
            c="seagreen",
            lw=3,
            alpha=0.6,
            label=f"Max Profit: ${100 * premium}",
        )
    else:
        ax.axhline(
            y=-100 * premium,
            c="firebrick",
            lw=3,
            alpha=0.6,
            label=f"Max Loss: ${-100 * premium}",
        )

    ax.set_xlabel("Price at Expiry")

    ax.set_ylabel("Profit")
    ax.set_title(
        f"Profit for {['Buying', 'Selling'][sell]} {['Call', 'Put'][put]} option"
    )
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    print_string = f"""Strike: ${strike}
Premium: ${premium}
Breakeven price: ${break_even}\n"""

    if sell:
        print_string += f"""Max profit: ${100 * premium}
Max loss: Unlimited\n"""

    else:
        print_string += f"""Max profit: Unlimited
Max loss: ${-100 * premium}\n"""

    console.print(print_string)

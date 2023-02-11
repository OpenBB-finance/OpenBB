import logging
from typing import Dict

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import calculator_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def view_calculator(
    strike: float = 10,
    premium: float = 1,
    put: bool = False,
    sell: bool = False,
    external_axes: bool = False,
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    kwargs: Dict[str,int]
    """

    price_at_expiry, pnl, break_even = calculator_model.pnl_calculator(
        strike, premium, put, sell, **kwargs
    )

    fig = OpenBBFigure(xaxis_title="Price at Expiry", yaxis_title="Profit")

    fig.set_title(
        f"Profit for {['Buying', 'Selling'][sell]} {['Call', 'Put'][put]} option"
    )

    fig.add_scatter(
        x=price_at_expiry[pnl > 0],
        y=pnl[pnl > 0],
        fill="tozeroy",
        fillcolor="rgba(0, 255, 0, 0.5)",
        line_color="green",
        name="Profit",
    )
    fig.add_scatter(
        x=price_at_expiry[pnl < 0],
        y=pnl[pnl < 0],
        fill="tozeroy",
        fillcolor="rgba(255, 0, 0, 0.5)",
        line_color="red",
        name="Loss",
    )

    fig.add_vline(x=strike, line_width=6, line_color="white", opacity=0.5)
    fig.add_vline(x=break_even, line_width=6, line_color="white", opacity=0.5)

    if sell:
        fig.add_hline_legend(
            y=100 * premium,
            line=dict(width=5, color="green"),
            name=f"Max Profit: ${100 * premium}",
        )
    else:
        fig.add_hline_legend(
            y=-100 * premium,
            line=dict(width=5, color="red"),
            name=f"Max Loss: ${-100 * premium}",
        )

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

    return fig.show(external=external_axes)

"""Coinbase view"""
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.decorators import log_start_end
from openbb_terminal.decorators import check_api_key
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.portfolio.brokers.coinbase_advanced import coinbase_advanced_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_CB_ADV_KEY", "API_CB_ADV_SECRET"])
def display_account(currency: str = "USD", export: str = "") -> None:
    """Display list of all your trading accounts. [Source: Coinbase]

    Parameters
    ----------
    currency: str
        Currency to show current value in, default 'USD'
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = coinbase_advanced_model.get_accounts(currency=currency, add_current_price=True)

    if df.empty:
        return

    df.available_balance = df["available_balance"].astype(float)
    df = df[df.available_balance > 0]

    df_data = df.copy()
    df = df.drop(columns=["id"])
    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="All Trading Accounts"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "account",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_CB_ADV_KEY", "API_CB_ADV_SECRET"])
def display_orders(
    limit: int = 20,
    sortby: str = "created_time",
    descend: bool = False,
    status: str = "ALL",
    export: str = "",
) -> None:
    """List your current open orders [Source: Coinbase]

    Parameters
    ----------
    limit: int
        Last `limit` of trades. Maximum is 1000.
    sortby: str
        Key to sort by
    descend: bool
        Flag to sort descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = coinbase_advanced_model.get_orders(limit, sortby, descend, status=status)
    df_data = df.copy()
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Current Open Orders",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "orders",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_CB_ADV_KEY", "API_CB_ADV_SECRET"])
def display_create_order(
    product_id: str = "",
    side: str = "",
    order_type: str = "",
    dry_run: bool = False,
    export: str = "",
    **kwargs
) -> None:
    """
    Parameters
    ----------
    See parameters doc string for create_orders in model
    product_id
    side
    order_type
    quote_size
    base_size
    limit_price
    end_time
    post_only
    stop_price
    stop_direction

    Returns
    -------

    """

    quote_size = kwargs.get("quote_size", 0)
    base_size = kwargs.get("base_size", 0)
    limit_price = kwargs.get("limit_price", 0)
    end_time = kwargs.get("end_time", 0)
    post_only = kwargs.get("post_only", True)
    stop_price = kwargs.get("stop_price", 0)
    stop_direction = kwargs.get("stop_direction", "")

    df = coinbase_advanced_model.create_order(
        product_id=product_id,
        side=side,
        order_type=order_type,
        quote_size=quote_size,
        base_size=base_size,
        limit_price=limit_price,
        end_time=end_time,
        post_only=post_only,
        stop_price=stop_price,
        stop_direction=stop_direction,
        dry_run=dry_run,
    )
    df_data = df.copy()
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Order Status",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "orders",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_CB_ADV_KEY", "API_CB_ADV_SECRET"])
def display_cancel_order(
    order_id: str = "",
    export: str = "",
) -> None:
    """Cancel open  order

    Parameters
    ----------
    order_id: str
        Valid Coinbase Advanced order_id
    """
    df = coinbase_advanced_model.cancel_order(order_id=order_id)
    df_data = df.copy()
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Cancel order response",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cancelled orders",
        df_data,
    )

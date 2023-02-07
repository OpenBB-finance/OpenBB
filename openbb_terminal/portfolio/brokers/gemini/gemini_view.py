"""Coinbase view"""
__docformat__ = "numpy"

import logging
import os
from dotenv import get_key
import openbb_terminal.feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.base_helpers import strtobool
from openbb_terminal.decorators import check_api_key
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.portfolio.brokers.gemini import gemini_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_GEMINI_KEY", "API_GEMINI_SECRET"])
def display_accounts(export: str = "") -> None:
    """Display list of all your trading accounts. [Source: Coinbase]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file

    """
    df = gemini_model.get_accounts()

    if df.empty:
        return

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="All Trading Accounts"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "accounts",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_GEMINI_KEY", "API_GEMINI_SECRET"])
def display_orders(
    limit: int = 20,
    sortby: str = "timestamp",
    descend: bool = False,
    status: str = "all",
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
    status: str
        Order status filter: live cancelled, all
    """
    df = gemini_model.get_orders(limit, sortby, descend, status=status)
    df_data = df.copy()
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Orders",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "orders",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_GEMINI_KEY", "API_GEMINI_SECRET"])
def display_create_order(
    symbol: str = "",
    side: str = "",
    amount: float = 0,
    price: float = 0,
    order_type: str = "",
    stop_price: float = 0,
    account: str = "primary",
    options: str = None,
    **kwargs,
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
    export = kwargs.get("export", "")

    df = gemini_model.create_order(
        symbol=symbol,
        side=side,
        amount=amount,
        account=account,
        price=price,
        order_type=order_type,
        stop_price=stop_price,
        options=options,
    )
    dry_run_status = ""
    if strtobool(get_key(obbff.USER_ENV_FILE, "OPENBB_GEMINI_DRYRUN") or "False"):
        dry_run_status = " - DRY RUN"

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title=f"Order Status{dry_run_status}",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "orders",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_GEMINI_KEY", "API_GEMINI_SECRET"])
def display_cancel_orders(
    order_id: str = None,
    all_active: bool = None,
    account: str = "primary",
    export: str = "",
) -> None:
    """Cancel open  order

    Parameters
    ----------
    order_id: str
        Valid Coinbase Advanced order_id
    """
    df = gemini_model.cancel_orders(
        order_id=order_id, all_active=all_active, account=account
    )
    df_data = df.copy()

    dry_run_status = ""
    if strtobool(get_key(obbff.USER_ENV_FILE, "OPENBB_GEMINI_DRYRUN") or "False"):
        dry_run_status = " - DRY RUN"

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title=f"Cancel order response{dry_run_status}",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cancelled orders",
        df_data,
    )

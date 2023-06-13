"""Terra Money FCD view"""
__docformat__ = "numpy"

import logging
import os
import textwrap
from typing import Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_very_long_number_formatter,
    prettify_column_names,
)
from openbb_terminal.cryptocurrency.defi import terramoney_fcd_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_account_staking_info(
    address: str = "",
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing staking info for provided terra account address [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    address: str
        terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg
    limit: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df, report = terramoney_fcd_model.get_staking_account_info(address)
    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title=report,
            export=bool(export),
            limit=limit,
        )
    else:
        console.print(f"[red]No data found for address {address}\n[/red]")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sinfo",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_validators(
    limit: int = 10,
    sortby: str = "votingPower",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing information about terra validators [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. Choose from:
        validatorName, tokensAmount, votingPower, commissionRate, status, uptime
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = terramoney_fcd_model.get_validators(sortby, ascend)
    df_data = df.copy()
    df["tokensAmount"] = df["tokensAmount"].apply(
        lambda x: lambda_very_long_number_formatter(x)
    )
    df.columns = [
        x if x not in ["Voting power", "Commission rate", "Uptime"] else f"{x} %"
        for x in prettify_column_names(df.columns)
    ]

    df["Account address"] = df["Account address"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=20))
    )

    print_rich_table(
        df,
        headers=list(df.columns),
        floatfmt=".2f",
        show_index=False,
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "validators",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_gov_proposals(
    limit: int = 10,
    status: str = "all",
    sortby: str = "id",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    limit: int
        Number of records to display
    status: str
        status of proposal, one from list: ['Voting','Deposit','Passed','Rejected']
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascend
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = terramoney_fcd_model.get_proposals(status, sortby, ascend, limit)

    print_rich_table(
        df,
        headers=list(df.columns),
        floatfmt=".2f",
        show_index=False,
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "govp",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_account_growth(
    kind: str = "total",
    cumulative: bool = False,
    limit: int = 90,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    limit: int
        Number of records to display
    kind: str
        display total account count or active account count. One from list [active, total]
    cumulative: bool
        Flag to show cumulative or discrete values. For active accounts only discrete value are available.
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df = terramoney_fcd_model.get_account_growth(cumulative)
    if kind not in ["active", "total"]:
        kind = "total"
    options = {"total": "Total accounts", "active": "Active accounts"}

    opt = options[kind]
    label = "Cumulative" if cumulative and opt == "total" else "Daily"

    fig = OpenBBFigure(yaxis_title=f"{opt}")

    df = df.sort_values("date", ascending=False).head(limit)
    df = df.set_index("date")

    start, end = df.index[-1], df.index[0]

    if cumulative:
        fig.add_scatter(x=df.index, y=df[opt], mode="lines", name=opt)
    else:
        fig.add_bar(x=df.index, y=df[opt], name=opt)

    fig.set_title(f"{label} number of {opt.lower()} in period from {start} to {end}")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gacc",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_staking_ratio_history(
    limit: int = 90,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots terra blockchain staking ratio history [Source: https://fcd.terra.dev/v1]

    Parameters
    ----------
    limit: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df = terramoney_fcd_model.get_staking_ratio_history(limit)

    start, end = df.index[-1], df.index[0]

    fig = OpenBBFigure(yaxis_title="Staking ratio [%]")
    fig.set_title(f"Staking ratio from {start} to {end}")

    fig.add_scatter(x=df.index, y=df["stakingRatio"], mode="lines", name="stakingRatio")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sratio",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_staking_returns_history(
    limit: int = 90,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots terra blockchain staking returns history [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    limit: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    """

    fig = OpenBBFigure(yaxis_title="Staking returns [%]")

    df = terramoney_fcd_model.get_staking_returns_history(limit)

    start, end = df.index[-1], df.index[0]

    fig.add_scatter(
        x=df.index, y=df["annualizedReturn"], mode="lines", name="annualizedReturn"
    )
    fig.set_title(f"Staking returns from {start} to {end}")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sreturn",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)

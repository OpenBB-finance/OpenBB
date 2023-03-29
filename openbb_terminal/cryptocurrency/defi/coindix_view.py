"""Coindix view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.defi import coindix_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_defi_vaults(
    chain: Optional[str] = None,
    protocol: Optional[str] = None,
    kind: Optional[str] = None,
    limit: int = 10,
    sortby: str = "apy",
    ascend: bool = True,
    link: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing Top DeFi Vaults - pools of funds with an assigned strategy which main goal is to
    maximize returns of its crypto assets. [Source: https://coindix.com/]

    Parameters
    ----------
    chain: str
        Blockchain - one from list [
        'ethereum', 'polygon', 'avalanche', 'bsc', 'terra', 'fantom',
        'moonriver', 'celo', 'heco', 'okex', 'cronos', 'arbitrum', 'eth',
        'harmony', 'fuse', 'defichain', 'solana', 'optimism'
        ]
    protocol: str
        DeFi protocol - one from list: [
        'aave', 'acryptos', 'alpaca', 'anchor', 'autofarm', 'balancer', 'bancor',
        'beefy', 'belt', 'compound', 'convex', 'cream', 'curve', 'defichain', 'geist',
        'lido', 'liquity', 'mirror', 'pancakeswap', 'raydium', 'sushi', 'tarot', 'traderjoe',
        'tulip', 'ubeswap', 'uniswap', 'venus', 'yearn'
        ]
    kind: str
        Kind/type of vault - one from list: ['lp','single','noimploss','stable']
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    link: bool
        Flag to show links
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coindix_model.get_defi_vaults(
        chain=chain, protocol=protocol, kind=kind, sortby=sortby, ascend=ascend
    )
    if df.empty:
        print(
            f"Couldn't find any vaults for "
            f"{'' if not chain else 'chain: ' + chain}"
            f"{'' if not protocol else ', protocol: ' + protocol}"
            f"{'' if not kind else ', kind:' + kind}"
        )
        return

    if link is True:
        df.drop("Link", axis=1, inplace=True)

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Top DeFi Vaults",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "vaults",
        df,
        sheet_name,
    )

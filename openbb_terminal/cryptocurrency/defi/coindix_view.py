"""Coindix view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.defi import coindix_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_defi_vaults(
    chain: Optional[str] = None,
    protocol: Optional[str] = None,
    kind: Optional[str] = None,
    top: int = 10,
    sortby: str = "apy",
    descend: bool = False,
    link: bool = False,
    export: str = "",
) -> None:
    """Display Top DeFi Vaults - pools of funds with an assigned strategy which main goal is to
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
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    link: bool
        Flag to show links
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coindix_model.get_defi_vaults(chain=chain, protocol=protocol, kind=kind)
    df_data = df.copy()
    if df.empty:
        print(
            f"Couldn't find any vaults for "
            f"{'' if not chain else 'chain: ' + chain}{'' if not protocol else ', protocol: ' + protocol}"
            f"{'' if not kind else ', kind:' + kind}"
        )
        return

    df = df.sort_values(by=sortby, ascending=descend)
    df["tvl"] = df["tvl"].apply(lambda x: lambda_long_number_format(x))
    df["apy"] = df["apy"].apply(
        lambda x: f"{str(round(x * 100, 2))} %" if isinstance(x, (int, float)) else x
    )
    df.columns = [x.title() for x in df.columns]
    df.rename(columns={"Apy": "APY (%)", "Tvl": "TVL ($)"}, inplace=True)

    if link is True:
        df.drop("Link", axis=1, inplace=True)

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Top DeFi Vaults",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "vaults",
        df_data,
    )

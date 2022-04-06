"""LoanScan view"""
import logging
import os
from openbb_terminal.cryptocurrency.overview import loanscan_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_crypto_rates(
    cryptos: str,
    platforms: str,
    rate_type: str,
    limit: int = 10,
    export: str = "",
) -> None:
    """Displays crypto {borrow,supply} interest rates for cryptocurrencies across several platforms
    [Source: https://loanscan.io/]

    Parameters
    ----------
    rate_type: str
        Interest rate type: {borrow, supply}. Default: supply
    cryptos: str
        Crypto separated by commas. Default: BTC,ETH,USDT,USDC
    platforms: str
        Platforms separated by commas. Default: BlockFi,Ledn,SwissBorg,Youhodler
    limit: int
        Number of records to show
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = loanscan_model.get_rates(rate_type=rate_type)
    if df.empty:
        console.print("\nError in loanscan request\n")
    else:
        df = df[cryptos.split(",")].loc[platforms.lower().split(",")]
        df = df.applymap(lambda x: str(100 * x) + "%" if x != "N/A" else x)

        print_rich_table(
            df.head(limit),
            headers=list(df.columns),
            index_name="Platform",
            show_index=True,
            title=f"Crypto {rate_type.capitalize()} Interest Rates",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cr",
            df,
        )

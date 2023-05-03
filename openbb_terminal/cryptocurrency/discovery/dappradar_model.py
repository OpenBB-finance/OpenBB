"""DappRadar model"""
__docformat__ = "numpy"

# pylint: disable=C0301,E1137
import logging
from typing import Optional

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

NFT_COLUMNS = [
    "Name",
    "Dapp ID",
    "Logo",
    "Chains",
    "Avg Price [$]",
    "Avg Price Change [%]",
    "Volume [$]",
    "Volume Change [%]",
    "Traders",
    "Traders Change [%]",
]


@log_start_end(log=logger)
def _make_request(url: str, verbose: bool = False) -> Optional[dict]:
    """Helper method handles dappradar api requests. [Source: https://dappradar.com/]

    Parameters
    ----------
    url: str
        endpoint url
    verbose: bool
        whether to print the text from the response

    Returns
    -------
    Optional[dict]:
        dictionary with response data
    """
    current_user = get_current_user()

    headers = {
        "Accept": "application/json",
        "User-Agent": get_user_agent(),
        # "referer": "https://api.dappradar.com/4tsxo4vuhotaojtl/",
        "X-BLOBR-KEY": current_user.credentials.API_DAPPRADAR_KEY,
    }
    response = request(url, headers=headers)
    if not 200 <= response.status_code < 300:
        if verbose:
            console.print(f"[red]dappradar api exception: {response.text}[/red]")
        return None
    try:
        return response.json()
    except Exception as e:  # noqa: F841
        logger.exception("Invalid Response: %s", str(e))
        if verbose:
            console.print(f"[red]Invalid Response:: {response.text}[/red]")
        return None


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def get_nft_marketplaces(
    chain: str = "", sortby: str = "", order: str = "", limit: int = 10
) -> pd.DataFrame:
    """Get top nft collections [Source: https://dappradar.com/]

    Parameters
    ----------
    chain: str
        Name of the chain
    sortby: str
        Key by which to sort data
    order: str
        Order of sorting
    limit: int
        Number of records to display

    Returns
    -------
    pd.DataFrame
        Columns: Name, Dapp ID, Logo, Chains, Avg Price [$], Avg Price Change [%],
        Volume [$], Volume Change [%], Traders, Traders Change [%]
    """

    args = {
        "chain": chain,
        "order": order,
        "sort": sortby,
        "resultsPerPage": limit,
    }
    args = {k: v for k, v in args.items() if v}
    query_string = "&".join([f"{k}={v}" for k, v in args.items()])

    response = _make_request(
        f"https://api.dappradar.com/4tsxo4vuhotaojtl/nfts/marketplaces?{query_string}"
    )
    if response:
        data = response.get("results")

        return pd.DataFrame(
            data,
            columns=[
                "name",
                "dappId",
                "logo",
                "chains",
                "avgPrice",
                "avgPricePercentageChange",
                "volume",
                "volumePercentageChange",
                "traders",
                "tradersPercentageChange",
            ],
        ).rename(
            columns={
                "name": "Name",
                "dappId": "Dapp ID",
                "logo": "Logo",
                "chains": "Chains",
                "avgPrice": "Avg Price [$]",
                "avgPricePercentageChange": "Avg Price Change [%]",
                "volume": "Volume [$]",
                "volumePercentageChange": "Volume Change [%]",
                "traders": "Traders",
                "tradersPercentageChange": "Traders Change [%]",
            }
        )
    return pd.DataFrame()


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def get_nft_marketplace_chains() -> pd.DataFrame:
    """Get nft marketplaces chains [Source: https://dappradar.com/]

    Returns
    -------
    pd.DataFrame
        Columns: Chain
    """

    response = _make_request(
        "https://api.dappradar.com/4tsxo4vuhotaojtl/nfts/marketplaces/chains"
    )
    if response:
        data = response.get("chains")

        return pd.DataFrame(
            data,
            columns=["Chain"],
        )
    return pd.DataFrame()


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def get_dapps(chain: str = "", page: int = 1, resultPerPage: int = 15):
    """Get dapps [Source: https://dappradar.com/]

    Parameters
    ----------
    chain: str
        Name of the chain
    page: int
        Page number
    resultPerPage: int
        Number of records to display

    Returns
    -------
    pd.DataFrame
        Columns: Dapp ID, Name, Description, Full Description, Logo, Link, Website,
        Chains, Categories
    """

    args = {
        "chain": chain,
        "page": page,
    }
    args = {k: v for k, v in args.items() if v}
    query_string = "&".join([f"{k}={v}" for k, v in args.items()])

    response = _make_request(
        f"https://api.dappradar.com/4tsxo4vuhotaojtl/dapps?{query_string}"
    )

    if response:
        data = response.get("results")
        return (
            pd.DataFrame(
                data,
                columns=[
                    "dappId",
                    "name",
                    "description",
                    "fullDescription",
                    "chains",
                    "categories",
                    "logo",
                    "link",
                    "website",
                ],
            )
            .rename(
                columns={
                    "dappId": "Dapp ID",
                    "name": "Name",
                    "description": "Description",
                    "fullDescription": "Full Description",
                    "chains": "Chains",
                    "categories": "Categories",
                    "logo": "Logo",
                    "link": "Link",
                    "website": "Website",
                }
            )
            .head(resultPerPage)  # DappRadar resultsPerPage is broken
        )

    return pd.DataFrame()


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def get_dapp_categories() -> pd.DataFrame:
    """Get dapp categories [Source: https://dappradar.com/]

    Returns
    -------
    pd.DataFrame
        Columns: Category
    """

    response = _make_request(
        "https://api.dappradar.com/4tsxo4vuhotaojtl/dapps/categories"
    )
    if response:
        data = response.get("categories")

        return pd.DataFrame(
            data,
            columns=["Category"],
        )
    return pd.DataFrame()


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def get_dapp_chains() -> pd.DataFrame:
    """Get dapp chains [Source: https://dappradar.com/]

    Returns
    -------
    pd.DataFrame
        Columns: Chain
    """

    response = _make_request("https://api.dappradar.com/4tsxo4vuhotaojtl/dapps/chains")
    if response:
        data = response.get("chains")

        return pd.DataFrame(
            data,
            columns=["Chain"],
        )
    return pd.DataFrame()


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def get_dapp_metrics(
    dappId: int, chain: str = "", time_range: str = ""
) -> pd.DataFrame:
    """Get dapp metrics [Source: https://dappradar.com/]

    Parameters
    ----------
    dappId: int
        Dapp ID
    chain: str
        Name of the chain if the dapp is multi-chain
    range: str
        Time range for the metrics. Can be 24h, 7d, 30d

    Returns
    -------
    pd.DataFrame
        Columns: Transactions, Transactions Change [%], Users, UAW, UAW Change [%],
        Volume [$], Volume Change [%], Balance [$], Balance Change [%]
    """
    if not dappId:
        console.print("[red]Please provide a dappId[/red]")
        return pd.DataFrame()

    query_string = (
        f"range={time_range}" if not chain else f"chain={chain}&range={time_range}"
    )

    response = _make_request(
        f"https://api.dappradar.com/4tsxo4vuhotaojtl/dapps/{dappId}?{query_string}"
    )

    if response:
        data = response["results"].get("metrics")
        return pd.DataFrame(
            data,
            columns=[
                "transactions",
                "transactionsPercentageChange",
                "users",
                "uaw",
                "uawPercentageChange",
                "volume",
                "volumePercentageChange",
                "balance",
                "balancePercentageChange",
            ],
            index=[response["results"]["name"]],
        ).rename(
            columns={
                "transactions": "Transactions",
                "transactionsPercentageChange": "Transactions Change [%]",
                "users": "Users",
                "uaw": "UAW",
                "uawPercentageChange": "UAW Change [%]",
                "volume": "Volume [$]",
                "volumePercentageChange": "Volume Change [%]",
                "balance": "Balance [$]",
                "balancePercentageChange": "Balance Change [%]",
            }
        )

    return pd.DataFrame()


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def get_defi_chains() -> pd.DataFrame:
    """Get defi chains [Source: https://dappradar.com/]

    Returns
    -------
    pd.DataFrame
        Columns: Chains
    """

    response = _make_request("https://api.dappradar.com/4tsxo4vuhotaojtl/defi/chains")
    if response:
        data = response.get("chains")

        return pd.DataFrame(
            data,
            columns=["Chains"],
        )
    return pd.DataFrame()


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def get_token_chains() -> pd.DataFrame:
    """Get chains that support tokens [Source: https://dappradar.com/]

    Returns
    -------
    pd.DataFrame
        Columns: Chains
    """

    response = _make_request("https://api.dappradar.com/4tsxo4vuhotaojtl/tokens/chains")
    if response:
        data = response.get("chains")

        return pd.DataFrame(
            data,
            columns=["Chains"],
        )
    return pd.DataFrame()

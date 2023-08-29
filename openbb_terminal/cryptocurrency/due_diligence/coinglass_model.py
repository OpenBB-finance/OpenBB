import datetime as dt
import json
import logging

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

api_url = "https://open-api.coinglass.com/api/pro/v1/"

# Prompt toolkit does not allow integers, so these items need to be strings
INTERVALS = [0, 1, 2, 4]


@log_start_end(log=logger)
@check_api_key(["API_COINGLASS_KEY"])
def get_liquidations(symbol: str) -> pd.DataFrame:
    """Returns liquidations per day for a certain symbol
    [Source: https://coinglass.github.io/API-Reference/#liquidation-chart]

    Parameters
    ----------
    symbol : str
        Crypto Symbol to search daily liquidations (e.g., BTC)

    Returns
    -------
    pd.DataFrame
        daily liquidations for loaded symbol
    """

    url = api_url + f"futures/liquidation_chart?symbol={symbol.upper()}"

    headers = {"coinglassSecret": get_current_user().credentials.API_COINGLASS_KEY}

    response = request(url, headers=headers)

    df = pd.DataFrame()

    if response.status_code == 200:
        res_json = json.loads(response.text)

        if res_json["success"]:
            if "data" in res_json:
                data = res_json["data"]
                time = data["dateList"]
                time_new = []
                for elem in time:
                    time_actual = dt.datetime.utcfromtimestamp(elem / 1000)
                    time_new.append(time_actual)

                df = pd.DataFrame(
                    data={
                        "date": time_new,
                        "price": data["priceList"],
                        "Shorts": data["buyList"],
                        "Longs": data["sellList"],
                    }
                )
                df = df.set_index("date")
            else:
                console.print(f"No data found for {symbol}.\n")
        elif "secret invalid" in res_json["msg"]:
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(res_json["msg"])

    elif response.status_code == 429:
        console.print("[red]Exceeded number of calls per minute[/red]\n")
    elif response.status_code == 429:
        console.print(
            "[red]IP address autobanned for exceeding calls limit multiple times.[/red]\n"
        )

    return df


@log_start_end(log=logger)
@check_api_key(["API_COINGLASS_KEY"])
def get_funding_rate(symbol: str) -> pd.DataFrame:
    """Returns open interest by exchange for a certain symbol
    [Source: https://coinglass.github.io/API-Reference/]

    Parameters
    ----------
    symbol : str
        Crypto Symbol to search open interest futures (e.g., BTC)

    Returns
    -------
    pd.DataFrame
        funding rate per exchange
    """

    url = api_url + f"futures/funding_rates_chart?symbol={symbol.upper()}&type=C"

    headers = {"coinglassSecret": get_current_user().credentials.API_COINGLASS_KEY}

    response = request(url, headers=headers)

    df = pd.DataFrame()

    if response.status_code == 200:
        res_json = json.loads(response.text)

        if res_json["success"]:
            if "data" in res_json:
                data = res_json["data"]
                time = data["dateList"]
                time_new = []
                for elem in time:
                    time_actual = dt.datetime.utcfromtimestamp(elem / 1000)
                    time_new.append(time_actual)

                df = pd.DataFrame(
                    data={
                        "date": time_new,
                        "price": data["priceList"],
                        **data["dataMap"],
                    }
                )
                df = df.set_index("date")
            else:
                console.print(f"No data found for {symbol}.\n")
        elif "secret invalid" in res_json["msg"]:
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(res_json["msg"])

    elif response.status_code == 429:
        console.print("[red]Exceeded number of calls per minute[/red]\n")
    elif response.status_code == 429:
        console.print(
            "[red]IP address autobanned for exceeding calls limit multiple times.[/red]\n"
        )

    return df


@log_start_end(log=logger)
@check_api_key(["API_COINGLASS_KEY"])
def get_open_interest_per_exchange(symbol: str, interval: int = 0) -> pd.DataFrame:
    """Returns open interest by exchange for a certain symbol
    [Source: https://coinglass.github.io/API-Reference/]

    Parameters
    ----------
    symbol : str
        Crypto Symbol to search open interest futures (e.g., BTC)
    interval : int
        Frequency (possible values are: 0 for ALL, 2 for 1H, 1 for 4H, 4 for 12H), by default 0

    Returns
    -------
    pd.DataFrame
        open interest by exchange and price
    """

    url = (
        api_url
        + f"futures/openInterest/chart?symbol={symbol.upper()}&interval={interval}"
    )

    headers = {"coinglassSecret": get_current_user().credentials.API_COINGLASS_KEY}

    response = request(url, headers=headers)
    df = pd.DataFrame()

    if response.status_code == 200:
        res_json = json.loads(response.text)

        if res_json["success"]:
            if "data" in res_json:
                data = res_json["data"]
                time = data["dateList"]
                time_new = []
                for elem in time:
                    time_actual = dt.datetime.utcfromtimestamp(elem / 1000)
                    time_new.append(time_actual)

                df = pd.DataFrame(
                    data={
                        "date": time_new,
                        "price": data["priceList"],
                        **data["dataMap"],
                    }
                )
                df = df.set_index("date")
            else:
                console.print(f"No data found for {symbol}.\n")
        elif "secret invalid" in res_json["msg"]:
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(res_json["msg"])

    elif response.status_code == 429:
        console.print("[red]Exceeded number of calls per minute[/red]\n")
    elif response.status_code == 429:
        console.print(
            "[red]IP address autobanned for exceeding calls limit multiple times.[/red]\n"
        )

    return df

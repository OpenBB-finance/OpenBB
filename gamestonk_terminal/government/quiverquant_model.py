import requests
import pandas as pd

# Provided by Quiverquant guys to GST users
API_QUIVERQUANT_KEY = "5cd2a65e96d0486efbe926a7cdbc1e8d8ab6c7b3"


def get_government_trading(gov_type: str, ticker: str = "") -> pd.DataFrame:
    """Returns the most recent transactions by members of government

    Parameters
    ----------
    gov_type: str
        Type of government data between: Congress, Senate, House and Contracts
    ticker : str
        Ticker to get congress trading data from

    Returns
    -------
    pd.DataFrame
        Most recent transactions by members of U.S. Congress
    """

    if gov_type == "congress":
        if ticker:
            url = (
                f"https://api.quiverquant.com/beta/historical/congresstrading/{ticker}"
            )
        else:
            url = "https://api.quiverquant.com/beta/live/congresstrading"

    elif gov_type == "senate":
        if ticker:
            url = f"https://api.quiverquant.com/beta/historical/senatetrading/{ticker}"
        else:
            url = "https://api.quiverquant.com/beta/live/senatetrading"

    elif gov_type == "house":
        if ticker:
            url = f"https://api.quiverquant.com/beta/historical/housetrading/{ticker}"
        else:
            url = "https://api.quiverquant.com/beta/live/housetrading"

    elif gov_type == "contracts":
        if ticker:
            url = (
                f"https://api.quiverquant.com/beta/historical/govcontractsall/{ticker}"
            )
        else:
            url = "https://api.quiverquant.com/beta/live/govcontractsall"

    else:
        return pd.DataFrame()

    headers = {
        "accept": "application/json",
        "X-CSRFToken": "TyTJwjuEC7VV7mOqZ622haRaaUr0x0Ng4nrwSRFKQs7vdoBcJlK9qjAS69ghzhFu",
        "Authorization": f"Token {API_QUIVERQUANT_KEY}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        if gov_type in ["congress", "senate", "house"]:
            return pd.DataFrame(response.json()).rename(
                columns={"Date": "TransactionDate", "Senator": "Representative"}
            )
        else:
            return pd.DataFrame(response.json())

    return pd.DataFrame()

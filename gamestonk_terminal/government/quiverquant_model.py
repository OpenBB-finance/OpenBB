import requests
import pandas as pd

# Provided by Quiverquant guys to GST users
API_QUIVERQUANT_KEY = "5cd2a65e96d0486efbe926a7cdbc1e8d8ab6c7b3"


def get_congress_trading(ticker: str = "") -> pd.DataFrame:
    """Returns the most recent transactions by members of U.S. Congress

    Parameters
    ----------
    ticker : str
        Ticker to get congress trading data from

    Returns
    -------
    pd.DataFrame
        Most recent transactions by members of U.S. Congress
    """

    if ticker:
        url = f"https://api.quiverquant.com/beta/historical/congresstrading/{ticker}"
    else:
        url = "https://api.quiverquant.com/beta/live/congresstrading"

    headers = {
        "accept": "application/json",
        "X-CSRFToken": "TyTJwjuEC7VV7mOqZ622haRaaUr0x0Ng4nrwSRFKQs7vdoBcJlK9qjAS69ghzhFu",
        "Authorization": f"Token {API_QUIVERQUANT_KEY}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return pd.DataFrame(response.json())

    return pd.DataFrame()

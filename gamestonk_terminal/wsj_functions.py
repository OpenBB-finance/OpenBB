"""Functions to scrape wsj.com/market-data"""
__docformat__ = "numpy"
import requests
import pandas as pd


def us_indices() -> pd.DataFrame:
    """
    Get the top US indices
    Returns
    -------
    indices: pd.DataFrame
        Dataframe containing name, price, net change and percent change
    """
    data = requests.get(
        "https://www.wsj.com/market-data/stocks?id=%7B%22application%22%3A%22WSJ%22%2C%22instruments%22%3A%5B%7B"
        "%22symbol%22%3A%22INDEX%2FUS%2F%2FDJIA%22%2C%22name%22%3A%22DJIA%22%7D%2C%7B%22symbol%22%3A%22INDEX%2FUS%2F"
        "%2FCOMP%22%2C%22name%22%3A%22Nasdaq%20Composite%22%7D%2C%7B%22symbol%22%3A%22INDEX%2FUS%2F%2FSPX%22%2C%22name"
        "%22%3A%22S%26P%20500%22%7D%2C%7B%22symbol%22%3A%22INDEX%2FUS%2F%2FDWCF%22%2C%22name%22%3A%22DJ%20Total%20Stock"
        "%20Market%22%7D%2C%7B%22symbol%22%3A%22INDEX%2FUS%2F%2FRUT%22%2C%22name%22%3A%22Russell%202000%22%7D%2C%7B"
        "%22symbol%22%3A%22INDEX%2FUS%2F%2FNYA%22%2C%22name%22%3A%22NYSE%20Composite%22%7D%2C%7B%22symbol%22%3A%22INDEX"
        "%2FUS%2F%2FB400%22%2C%22name%22%3A%22Barron%27s%20400%22%7D%2C%7B%22symbol%22%3A%22INDEX%2FUS%2F%2FVIX%22%2C%22"
        "name%22%3A%22CBOE%20Volatility%22%7D%2C%7B%22symbol%22%3A%22FUTURE%2FUS%2F%2FDJIA%20FUTURES%22%2C%22name%22%3A%"
        "22DJIA%20Futures%22%7D%2C%7B%22symbol%22%3A%22FUTURE%2FUS%2F%2FS%26P%20500%20FUTURES%22%2C%22name%22%3A%22S%26P"
        "%20500%20Futures%22%7D%5D%7D&type=mdc_quotes",
        headers={"User-Agent": "Mozilla/5.0"},
    ).json()

    name, last_price, net_change, percent_change = [], [], [], []

    for entry in data["data"]["instruments"]:
        name.append(entry["formattedName"])
        last_price.append(entry["lastPrice"])
        net_change.append(entry["priceChange"])
        percent_change.append(entry["percentChange"])

    indices = pd.DataFrame(
        {" ": name, "Price": last_price, "Chg": net_change, "%Chg": percent_change}
    )

    return indices


def market_overview() -> pd.DataFrame:
    """
    Scrape data for market overview
    Returns
    -------
    overview: pd.DataFrame
        Dataframe containing name, price, net change and percent change
    """
    data = requests.get(
        "https://www.wsj.com/market-data?id=%7B%22application%22%3A%22WSJ%22%2C%22instruments%22%3A%5B%7B%22symbol%22"
        "%3A%22INDEX%2FUS%2F%2FDJIA%22%2C%22name%22%3A%22DJIA%22%7D%2C%7B%22symbol%22%3A%22INDEX%2FUS%2F%2FSPX%22%2C%22"
        "name%22%3A%22S%26P%20500%22%7D%2C%7B%22symbol%22%3A%22INDEX%2FUS%2F%2FCOMP%22%2C%22name%22%3A%22Nasdaq%20"
        "Composite%22%7D%2C%7B%22symbol%22%3A%22INDEX%2FJP%2F%2FNIK%22%2C%22name%22%3A%22Japan%3A%20Nikkei%20225%22%7D%"
        "2C%7B%22symbol%22%3A%22INDEX%2FUK%2F%2FUKX%22%2C%22name%22%3A%22UK%3A%20FTSE%20100%22%7D%2C%7B%22symbol%22%3A%"
        "22FUTURE%2FUS%2F%2FCRUDE%20OIL%20-%20ELECTRONIC%22%2C%22name%22%3A%22Crude%20Oil%20Futures%22%7D%2C%7B%22symbol"
        "%22%3A%22FUTURE%2FUS%2F%2FGOLD%22%2C%22name%22%3A%22Gold%20Futures%22%7D%2C%7B%22symbol%22%3A%22CURRENCY%2FUS%2"
        "F%2FUSDJPY%22%2C%22name%22%3A%22Yen%22%7D%2C%7B%22symbol%22%3A%22CURRENCY%2FUS%2F%2FEURUSD%22%2C%22name%22%3A%"
        "22Euro%22%7D%5D%7D&type=mdc_quotes",
        headers={"User-Agent": "Mozilla/5.0"},
    ).json()
    name, last_price, net_change, percent_change = [], [], [], []

    for entry in data["data"]["instruments"]:
        name.append(entry["formattedName"])
        last_price.append(entry["lastPrice"])
        net_change.append(entry["priceChange"])
        percent_change.append(entry["percentChange"])

    overview = pd.DataFrame(
        {" ": name, "Price": last_price, "Chg": net_change, "%Chg": percent_change}
    )

    return overview


def top_commodities() -> pd.DataFrame:
    """
    Scrape data for top commodities
    Returns
    -------
    commodities: pd.DataFrame
        Dataframe containing name, price, net change and percent change
    """
    data = requests.get(
        "https://www.wsj.com/market-data/commodities?id=%7B%22application%22%3A%22WSJ%22%2C%22instruments%22%3A%5B%7"
        "B%22symbol%22%3A%22FUTURE%2FUS%2F%2FCRUDE%20OIL%20-%20ELECTRONIC%22%2C%22name%22%3A%22Crude%20Oil%20Futures"
        "%22%7D%2C%7B%22symbol%22%3A%22FUTURE%2FUK%2F%2FBRENT%20CRUDE%22%2C%22name%22%3A%22Brent%20Crude%20Futures%22"
        "%7D%2C%7B%22symbol%22%3A%22FUTURE%2FUS%2F%2FGOLD%22%2C%22name%22%3A%22Gold%20Futures%22%7D%2C%7B%22symbol%22%"
        "3A%22FUTURE%2FUS%2F%2FSILVER%22%2C%22name%22%3A%22Silver%20Futures%22%7D%2C%7B%22symbol%22%3A%22FUTURE%2FUS%2F"
        "%2FNATURAL%20GAS%22%2C%22name%22%3A%22Natural%20Gas%20Futures%22%7D%2C%7B%22symbol%22%3A%22FUTURE%2FUS%2F%2"
        "FUNLEADED%20GASOLINE%22%2C%22name%22%3A%22Unleaded%20Gasoline%20Futures%22%7D%2C%7B%22symbol%22%3A%22FUTURE%"
        "2FUS%2F%2FCOPPER%22%2C%22name%22%3A%22Copper%20Futures%22%7D%2C%7B%22symbol%22%3A%22FUTURE%2FUS%2F%2FCORN%22%2"
        "C%22name%22%3A%22Corn%20Futures%22%7D%2C%7B%22symbol%22%3A%22FUTURE%2FUS%2F%2FWHEAT%22%2C%22name%22%3A%22Wheat"
        "%20Futures%22%7D%2C%7B%22symbol%22%3A%22INDEX%2FXX%2F%2FBCOM%22%7D%5D%7D&type=mdc_quotes",
        headers={"User-Agent": "Mozilla/5.0"},
    ).json()
    name, last_price, net_change, percent_change = [], [], [], []

    for entry in data["data"]["instruments"]:
        name.append(entry["formattedName"])
        last_price.append(entry["lastPrice"])
        net_change.append(entry["priceChange"])
        percent_change.append(entry["percentChange"])

    commodities = pd.DataFrame(
        {" ": name, "Price": last_price, "Chg": net_change, "%Chg": percent_change}
    )

    return commodities


def etf_movers(sort_type: str = "gainers") -> pd.DataFrame:
    """
    Scrape data for top etf movers.
    Parameters
    ----------
    sort_type: str
        Data to get.  Can be "gainers", "decliners" or "activity

    Returns
    -------
    etfmovers: pd.DataFrame
        Datafame containing the name, price, change and the volume of the etf
    """

    if sort_type == "gainers":
        url = (
            "https://www.wsj.com/market-data/mutualfunds-etfs/etfmovers?id=%7B%22application"
            "%22%3A%22WSJ%22%2C%22etfMover%22%3A%22leaders%22%2C%22count%22%3A25%7D&type=mdc_etfmovers"
        )
    elif sort_type == "decliners":
        url = (
            "https://www.wsj.com/market-data/mutualfunds-etfs/etfmovers?id=%7B%22application"
            "%22%3A%22WSJ%22%2C%22etfMover%22%3A%22laggards%22%2C%22count%22%3A25%7D&type=mdc_etfmovers"
        )
    elif sort_type == "activity":
        url = (
            "https://www.wsj.com/market-data/mutualfunds-etfs/etfmovers?id=%7B%22application"
            "%22%3A%22WSJ%22%2C%22etfMover%22%3A%22most_active%22%2C%22count%22%3A25%7D&type=mdc_etfmovers"
        )

    data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).json()
    name, last_price, net_change, percent_change, volume = [], [], [], [], []

    for entry in data["data"]["instruments"]:
        name.append(entry["name"])
        last_price.append(entry["lastPrice"])
        net_change.append(entry["priceChange"])
        percent_change.append(entry["percentChange"])
        volume.append(entry["formattedVolume"])

    etfmovers = pd.DataFrame(
        {
            " ": name,
            "Price": last_price,
            "Chg": net_change,
            "%Chg": percent_change,
            "Vol": volume,
        }
    )

    return etfmovers

"""WSJ model"""
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


def us_bonds() -> pd.DataFrame:
    """
    Scrape data for us bonds
    Returns
    -------
    bonds: pd.DataFrame
        Dataframe containing name, coupon rate, yield and change in yield
    """

    data = requests.get(
        "https://www.wsj.com/market-data?id=%7B%22application%22%3A%22WSJ%22%2C%22instruments%22%3A%5B"
        "%7B%22symbol%22%3A%22BOND%2FBX%2F%2FTMUBMUSD30Y%22%2C%22name%22%3A%2230-Year%20Bond%22%7D%2C%7"
        "B%22symbol%22%3A%22BOND%2FBX%2F%2FTMUBMUSD10Y%22%2C%22name%22%3A%2210-Year%20Note%22%7D%2C%7B%2"
        "2symbol%22%3A%22BOND%2FBX%2F%2FTMUBMUSD07Y%22%2C%22name%22%3A%227-Year%20Note%22%7D%2C%7B%22sym"
        "bol%22%3A%22BOND%2FBX%2F%2FTMUBMUSD05Y%22%2C%22name%22%3A%225-Year%20Note%22%7D%2C%7B%22symbol"
        "%22%3A%22BOND%2FBX%2F%2FTMUBMUSD03Y%22%2C%22name%22%3A%223-Year%20Note%22%7D%2C%7B%22symbol%22%"
        "3A%22BOND%2FBX%2F%2FTMUBMUSD02Y%22%2C%22name%22%3A%222-Year%20Note%22%7D%2C%7B%22symbol%22%3A%"
        "22BOND%2FBX%2F%2FTMUBMUSD01Y%22%2C%22name%22%3A%221-Year%20Bill%22%7D%2C%7B%22symbol%22%3A%22"
        "BOND%2FBX%2F%2FTMUBMUSD06M%22%2C%22name%22%3A%226-Month%20Bill%22%7D%2C%7B%22symbol%22%3A%22BON"
        "D%2FBX%2F%2FTMUBMUSD03M%22%2C%22name%22%3A%223-Month%20Bill%22%7D%2C%7B%22symbol%22%3A%22BOND%"
        "2FBX%2F%2FTMUBMUSD01M%22%2C%22name%22%3A%221-Month%20Bill%22%7D%5D%7D&type=mdc_quotes",
        headers={"User-Agent": "Mozilla/5.0"},
    ).json()
    name, yield_pct, rate, yld_chng = [], [], [], []

    for entry in data["data"]["instruments"]:
        name.append(entry["formattedName"])
        yield_pct.append(entry["bond"]["yield"])
        rate.append(entry["bond"]["couponRate"])
        yld_chng.append(entry["bond"]["yieldChange"])

    bonds = pd.DataFrame(
        {" ": name, "Rate (%)": rate, "Yld (%)": yield_pct, "Yld Chg (%)": yld_chng}
    )
    return bonds


def global_bonds() -> pd.DataFrame:
    """
    Scrape data for global bonds
    Returns
    -------
    bonds: pd.DataFrame
        Dataframe containing name, coupon rate, yield and change in yield
    """
    data = requests.get(
        "https://www.wsj.com/market-data?id=%7B%22application%22%3A%22WSJ%22%2C%22bonds%22%3A%5"
        "B%7B%22symbol%22%3A%22TMUBMUSD10Y%22%2C%22name%22%3A%22U.S.%2010%20Year%22%7D%2C%7B%22symbol"
        "%22%3A%22TMBMKDE-10Y%22%2C%22name%22%3A%22Germany%2010%20Year%22%7D%2C%7B%22symbol%22%3A%22TMB"
        "MKGB-10Y%22%2C%22name%22%3A%22U.K.%2010%20Year%22%7D%2C%7B%22symbol%22%3A%22TMBMKJP-10Y%22%2C%"
        "22name%22%3A%22Japan%2010%20Year%22%7D%2C%7B%22symbol%22%3A%22TMBMKAU-10Y%22%2C%22name%22%3A%2"
        "2Australia%2010%20Year%22%7D%2C%7B%22symbol%22%3A%22AMBMKRM-10Y%22%2C%22name%22%3A%22China%2010"
        "%20Year%22%7D%5D%7D&type=mdc_governmentbonds",
        headers={"User-Agent": "Mozilla/5.0"},
    ).json()
    name, yield_pct, rate, yld_chng = [], [], [], []

    for entry in data["data"]["instruments"]:
        name.append(entry["djLegalName"])
        yield_pct.append(entry["yieldPercent"])
        rate.append(entry["couponPercent"])
        yld_chng.append(entry["yieldChange"])

    bonds = pd.DataFrame(
        {" ": name, "Rate (%)": rate, "Yld (%)": yield_pct, "Yld Chg (%)": yld_chng}
    )
    return bonds


def global_currencies() -> pd.DataFrame:
    """
    Scrape data for global currencies
    Returns
    -------
    currencies: pd.DataFrame
        Dataframe containing name, price, net change and percent change
    """
    data = requests.get(
        "https://www.wsj.com/market-data?id=%7B%22application%22%3A%22WSJ%22%2C%22instruments%22%3A%5"
        "B%7B%22symbol%22%3A%22CURRENCY%2FUS%2F%2FEURUSD%22%2C%22name%22%3A%22Euro%20(EUR%2FUSD)%22%7D%"
        "2C%7B%22symbol%22%3A%22CURRENCY%2FUS%2F%2FUSDJPY%22%2C%22name%22%3A%22Japanese%20Yen%20(USD%2F"
        "JPY)%22%7D%2C%7B%22symbol%22%3A%22CURRENCY%2FUS%2F%2FGBPUSD%22%2C%22name%22%3A%22U.K.%20Poun"
        "d%20(GBP%2FUSD)%22%7D%2C%7B%22symbol%22%3A%22CURRENCY%2FUS%2F%2FUSDCHF%22%2C%22name%22%3A%22Sw"
        "iss%20Franc%20(USD%2FCHF)%22%7D%2C%7B%22symbol%22%3A%22CURRENCY%2FUS%2F%2FUSDCNY%22%2C%22name%2"
        "2%3A%22Chinese%20Yuan%20(USD%2FCNY)%22%7D%2C%7B%22symbol%22%3A%22CURRENCY%2FUS%2F%2FUSDCAD%22%2C"
        "%22name%22%3A%22Canadian%20%24%20(USD%2FCAD)%22%7D%2C%7B%22symbol%22%3A%22CURRENCY%2FUS%2F%2F"
        "USDMXN%22%2C%22name%22%3A%22Mexican%20Peso%20(USD%2FMXN)%22%7D%2C%7B%22symbol%22%3A%22CRYPTO"
        "CURRENCY%2FUS%2F%2FBTCUSD%22%2C%22name%22%3A%22Bitcoin%20(BTC%2FUSD)%22%7D%2C%7B%22symbol%22%3A"
        "%22INDEX%2FXX%2F%2FBUXX%22%2C%22name%22%3A%22WSJ%20Dollar%20Index%22%7D%2C%7B%22symbol%22%3A%2"
        "2INDEX%2FUS%2F%2FDXY%22%2C%22name%22%3A%22U.S.%20Dollar%20Index%22%7D%5D%7D&type=mdc_quotes",
        headers={"User-Agent": "Mozilla/5.0"},
    ).json()

    name, last_price, price_change, pct_change = [], [], [], []
    for entry in data["data"]["instruments"]:
        name.append(entry["formattedName"])
        last_price.append(entry["lastPrice"])
        price_change.append(entry["priceChange"])
        pct_change.append(entry["percentChange"])

    currencies = pd.DataFrame(
        {" ": name, "Last": last_price, "Chng": price_change, "%Chng": pct_change}
    )
    return currencies

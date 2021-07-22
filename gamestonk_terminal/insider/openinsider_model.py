from datetime import datetime
from typing import Dict, List
import os
import configparser
import requests
from bs4 import BeautifulSoup
import pandas as pd

presets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")


# pylint: disable=too-many-branches


def check_valid_range(
    category: str, field: str, val: str, min_range: int, max_range: int
):  # -> str
    """Check valid range of data being used

    Parameters
    ----------
    category : str
        category of open insider screener
    field : str
        field from category of open insider screener
    val : str
        value's field of category from open insider screener
    min_range : int
        min value to allow
    max_range : int
        max value to allow

    Returns
    ----------
    error : str
        error message. If empty, no error.
    """
    error = ""
    if val:
        try:
            ival = int(val)

            if ival < min_range or ival > max_range:
                error = (
                    f"Invalid {category}.{field} '{str(ival)}'. "
                    f"Choose value between {min_range} and {max_range}, inclusive."
                )

        except ValueError:
            error = f"Invalid {category}.{field} '{val}'. Not a valid integer.\n"

    return error


def check_dates(d_date: Dict):  # -> str
    """Check valid dates

    Parameters
    ----------
    d_date : Dict
        dictionary with dates from open insider

    Returns
    ----------
    error : str
        error message. If empty, no error.
    """
    possible_dates = [
        "All dates",
        "Custom",
        "Latest Day",
        "Last 3 days",
        "Last 1 week",
        "Last 2 weeks",
        "Last 1 month",
        "Last 2 months",
        "Last 3 months",
        "Last 6 months",
        "Last 1 year",
        "Last 2 years",
        "Last 4 years",
    ]

    error = ""

    if d_date["FilingDate"] not in possible_dates:
        error += (
            f"Invalid FilingDate '{d_date['FilingDate']}'. "
            f"Choose one of the following options: {', '.join(possible_dates)}.\n"
        )
    else:
        if d_date["FilingDate"] == "Custom":
            try:
                datetime.strptime(d_date["FilingDateFrom"], "%d/%m/%Y")
            except ValueError:
                error += f"Invalid FilingDateFrom '{d_date['FilingDateFrom']}' (format: dd/mm/yyyy).\n"
            try:
                datetime.strptime(d_date["FilingDateTo"], "%d/%m/%Y")
            except ValueError:
                error += f"Invalid FilingDateTo '{d_date['FilingDateTo']}' (format: dd/mm/yyyy).\n"

    if d_date["TradingDate"] not in possible_dates:
        error += (
            f"Invalid TradingDate '{d_date['TradingDate']}'. "
            f"Choose one of the following options: {', '.join(possible_dates)}.\n"
        )
    else:
        if d_date["TradingDate"] == "Custom":
            try:
                datetime.strptime(d_date["TradingDateFrom"], "%d/%m/%Y")
            except ValueError:
                error += f"Invalid TradingDateFrom '{d_date['TradingDateFrom']}' (format: dd/mm/yyyy).\n"

            try:
                datetime.strptime(d_date["TradingDateTo"], "%d/%m/%Y")
            except ValueError:
                error += f"Invalid TradingDateTo '{d_date['TradingDateTo']}' (format: dd/mm/yyyy).\n"

    return error


def check_valid_multiple(category: str, field: str, val: str, multiple: int):  # -> str
    """Check valid value being a multiple

    Parameters
    ----------
    category : str
        category of open insider screener
    field : str
        field from category of open insider screener
    val : str
        value's field of category from open insider screener
    multiple : int
        value must be multiple of this number

    Returns
    ----------
    error : str
        error message. If empty, no error.
    """
    error = ""
    if val:
        try:
            ival = int(val)

            if ival % multiple != 0:
                error = f"Invalid {category}.{field} '{str(ival)}'. Choose value multiple of {str(multiple)}.\n"

        except ValueError:
            error = f"Invalid {category}.{field} '{val}'. Not a valid integer.\n"

    return error


def check_boolean_list(category: str, d_data: Dict, l_fields_to_check: List):  # -> str
    """Check list of fields being bools

    Parameters
    ----------
    category : str
        category of open insider screener
    d_data : Dict
        data dictionary
    l_fields_to_check : List[str]
        list of fields from data dictionary to check if they are bool

    Returns
    ----------
    error : str
        error message. If empty, no error.
    """
    error = ""

    for field in l_fields_to_check:
        if d_data[field] not in ["true", ""]:
            error += f"Invalid {category}.{field} '{d_data[field]}'. Needs to be either 'true' or '' (empty).\n"

    return error


def check_in_list(
    category: str, field: str, val: int, l_possible_vals: List[str]
):  # -> str
    """Check value being in possible list

    Parameters
    ----------
    category : str
        category of open insider screener
    field : str
        field from category of open insider screener
    val : str
        value's field of category from open insider screener
    l_possible_vals : List[str]
        list of possible values that should be allowed

    Returns
    ----------
    error : str
        error message. If empty, no error.
    """
    error = ""

    if val:
        if val not in l_possible_vals:
            error += (
                f"Invalid {category}.{field} '{val}'. "
                f"Choose one of the following options: {', '.join(l_possible_vals)}.\n"
            )

    return error


def check_int_in_list(
    category: str, field: str, val: str, l_possible_vals: List[int]
):  # -> str
    """Check int value being in possible list

    Parameters
    ----------
    category : str
        category of open insider screener
    field : str
        field from category of open insider screener
    val : str
        value's field of category from open insider screener
    l_possible_vals : List[str]
        list of possible values that should be allowed

    Returns
    ----------
    error : str
        error message. If empty, no error.
    """
    error = ""

    if val:
        try:
            ival = int(val)

            if ival not in l_possible_vals:
                error += (
                    f"Invalid {category}.{field} '{val}'. "
                    f"Choose one of the following options: {', '.join([str(x) for x in l_possible_vals])}.\n"
                )

        except ValueError:
            error += f"Invalid {category}.{field} '{val}'. Not a valid integer.\n"

    return error


def check_open_insider_general(d_general):  # -> str
    """Check valid open insider general

    Parameters
    ----------
    d_date : Dict
        dictionary of general

    Returns
    ----------
    error : str
        error message. If empty, no error.
    """
    error = check_valid_range(
        "General", "SharePriceMin", d_general["SharePriceMin"], 0, 9999
    )

    error += check_valid_range(
        "General", "SharePriceMax", d_general["SharePriceMax"], 0, 9999
    )

    error += check_valid_range(
        "General", "LiquidityMinM", d_general["LiquidityMinM"], 0, 9999
    )

    error += check_valid_range(
        "General", "LiquidityMaxM", d_general["LiquidityMaxM"], 0, 9999
    )

    return error


def check_open_insider_date(d_date: Dict):  # -> str
    """Check valid open insider date

    Parameters
    ----------
    d_date : Dict
        dictionary of date

    Returns
    ----------
    error : str
        error message. If empty, no error.
    """
    error = check_dates(d_date)
    error += check_valid_range(
        "Date", "FilingDelayMin", d_date["FilingDelayMin"], 0, 99
    )
    error += check_valid_range(
        "Date", "FilingDelayMax", d_date["FilingDelayMax"], 0, 99
    )
    error += check_valid_range("Date", "NDaysAgo", d_date["NDaysAgo"], 0, 99)

    return error


def check_open_insider_transaction_filing(d_transaction_filing: Dict):  # -> str
    """Check valid open insider transaction filing

    Parameters
    ----------
    d_transaction_filing : Dict
        dictionary of transaction filing

    Returns
    ----------
    error : str
        error message. If empty, no error.
    """
    filings_to_check = [
        "P_Purchase",
        "S_Sale",
        "A_Grant",
        "D_SaleToLoss",
        "G_Gift",
        "NoDeriv",
        "F_Tax",
        "M_OptionEx",
        "X_OptionEx",
        "C_CnvDeriv",
        "W_Inherited",
        "MultipleDays",
    ]

    error = check_boolean_list(
        "TransactionFiling", d_transaction_filing, filings_to_check
    )
    error += check_valid_multiple(
        "TransactionFiling", "TradedMinK", d_transaction_filing["TradedMinK"], 5
    )
    error += check_valid_multiple(
        "TransactionFiling", "TradedMaxK", d_transaction_filing["TradedMaxK"], 5
    )
    error += check_valid_range(
        "TransactionFiling",
        "OwnChangeMinPct",
        d_transaction_filing["OwnChangeMinPct"],
        0,
        99,
    )
    error += check_valid_range(
        "TransactionFiling",
        "OwnChangeMaxPct",
        d_transaction_filing["OwnChangeMaxPct"],
        0,
        99,
    )

    return error


def check_open_insider_insider_title(d_insider_title: Dict):  # -> str
    """Check valid open insider title

    Parameters
    ----------
    d_insider_title : Dict
        dictionary of title

    Returns
    ----------
    error : str
        error message. If empty, no error.
    """
    titles_to_check = [
        "COB",
        "CEO",
        "Pres",
        "COO",
        "CFO",
        "GC",
        "VP",
        "Officer",
        "Director",
        "10PctOwn",
        "Other",
    ]

    error = check_boolean_list("InsiderTitle", d_insider_title, titles_to_check)

    return error


def check_open_insider_others(d_others: Dict):  # -> str
    """Check valid open insider others

    Parameters
    ----------
    d_others : Dict
        dictionary of others

    Returns
    ----------
    error : str
        error message. If empty, no error.
    """
    possible_groupby = ["Filing", "Company"]
    error = check_in_list("Others", "GroupBy", d_others["GroupBy"], possible_groupby)

    possible_sortby = ["Filing Date", "Trade Date", "Ticker Symbol", "Trade Value"]
    error = check_in_list("Others", "SortBy", d_others["SortBy"], possible_sortby)

    possible_maxresults = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    error += check_int_in_list(
        "Others", "MaxResults", d_others["MaxResults"], possible_maxresults
    )

    error += check_valid_range("Others", "Page", d_others["Page"], 0, 99)

    return error


def check_open_insider_company_totals(d_company_totals: Dict):  # -> str
    """Check valid open insider company totals

    Parameters
    ----------
    d_company_totals : Dict
        dictionary of company totals

    Returns
    ----------
    error : str
        error message. If empty, no error.
    """
    error = check_valid_range(
        "CompanyTotals", "FilingsMin", d_company_totals["FilingsMin"], 0, 99
    )

    error += check_valid_range(
        "CompanyTotals", "FilingsMax", d_company_totals["FilingsMax"], 0, 99
    )

    error += check_valid_range(
        "CompanyTotals", "InsidersMin", d_company_totals["InsidersMin"], 0, 9
    )

    error += check_valid_range(
        "CompanyTotals", "InsidersMax", d_company_totals["InsidersMax"], 0, 9
    )

    error += check_valid_range(
        "CompanyTotals", "OfficersMin", d_company_totals["OfficersMin"], 0, 9
    )

    error += check_valid_range(
        "CompanyTotals", "OfficersMax", d_company_totals["OfficersMax"], 0, 9
    )

    error += check_valid_multiple(
        "CompanyTotals", "TradedMinK", d_company_totals["TradedMinK"], 5
    )

    error += check_valid_multiple(
        "CompanyTotals", "TradedMaxK", d_company_totals["TradedMaxK"], 5
    )

    error += check_valid_range(
        "CompanyTotals", "OwnChangeMinPct", d_company_totals["OwnChangeMinPct"], 0, 99
    )

    error += check_valid_range(
        "CompanyTotals", "OwnChangeMaxPct", d_company_totals["OwnChangeMaxPct"], 0, 99
    )

    return error


def check_open_insider_screener(
    d_general: Dict,
    d_date: Dict,
    d_transaction_filing: Dict,
    d_industry: Dict,
    d_insider_title: Dict,
    d_others: Dict,
    d_company_totals: Dict,
):
    """Check valid open insider screener

    Parameters
    ----------
    d_general : Dict
        dictionary of general
    d_date : Dict
        dictionary of date
    d_transaction_filing : Dict
        dictionary of transaction filing
    d_industry : Dict
        dictionary of industry
    d_insider_title : Dict
        dictionary of insider title
    d_others : Dict
        dictionary of others
    d_company_totals : Dict
        dictionary of company totals

    Returns
    ----------
    error : str
        error message. If empty, no error.
    """
    error = check_open_insider_general(d_general)
    error += check_open_insider_date(d_date)
    error += check_open_insider_transaction_filing(d_transaction_filing)

    # Missing industry check!
    print(f"Industry check missing: {d_industry} for NOW!!")

    error += check_open_insider_insider_title(d_insider_title)
    error += check_open_insider_others(d_others)
    if d_others["GroupBy"] == "Company":
        error += check_open_insider_company_totals(d_company_totals)

    return error


def get_open_insider_link(preset_loaded: str):  # -> str
    """Get open insider link

    Parameters
    ----------
    preset_loaded: str
        Loaded preset filter

    Returns
    ----------
    link : str
        open insider filtered link
    """
    d_FilingTradingDate = {
        "All dates": "0",
        "Custom": "-1",
        "Latest Day": "1",
        "Last 3 days": "3",
        "Last 1 week": "7",
        "Last 2 weeks": "14",
        "Last 1 month": "30",
        "Last 2 months": "60",
        "Last 3 months": "90",
        "Last 6 months": "180",
        "Last 1 year": "365",
        "Last 2 years": "730",
        "Last 4 years": "1461",
    }
    d_GroupBy = {
        "Filing": "0",
        "Company": "2",
    }
    d_SortBy = {
        "Filing Date": 0,
        "Trade Date": 1,
        "Ticker Symbol": 2,
        "Trade Value": 8,
    }

    preset = configparser.RawConfigParser()
    preset.optionxform = str  # type: ignore
    preset.read(presets_path + preset_loaded + ".ini")

    d_general = dict(preset["General"])
    d_date = dict(preset["Date"])
    d_transaction_filing = dict(preset["TransactionFiling"])
    d_industry = dict(preset["Industry"])
    d_insider_title = dict(preset["InsiderTitle"])
    d_others = dict(preset["Others"])
    d_company_totals = dict(preset["CompanyTotals"])

    result = check_open_insider_screener(
        d_general,
        d_date,
        d_transaction_filing,
        d_industry,
        d_insider_title,
        d_others,
        d_company_totals,
    )

    if result:
        print(result)
        return ""

    link = "http://openinsider.com/screener?"

    # General
    link += f"s={d_general['Tickers'].replace(' ', '+')}&"
    link += f"o={d_general['Insider'].replace(' ', '+')}&"
    link += f"pl={d_general['SharePriceMin']}&"
    link += f"ph={d_general['SharePriceMax']}&"
    link += f"ll={d_general['LiquidityMinM']}&"
    link += f"lh={d_general['LiquidityMaxM']}&"

    # Date
    link += f"fd={d_FilingTradingDate[d_date['FilingDate']]}&"
    if d_date["FilingDate"] == "Custom":
        link += f"fdr={d_date['FilingDateFrom'].replace('/','%2F')}-{d_date['FilingDateTo'].replace('/','%2F')}&"
    else:
        link += "fdr=&"
    link += f"td={d_FilingTradingDate[d_date['TradingDate']]}&"
    if d_date["TradingDate"] == "Custom":
        link += f"tdr={d_date['TradingDateFrom'].replace('/','%2F')}-{d_date['TradingDateTo'].replace('/','%2F')}&"
    else:
        link += "tdr=&"
    link += f"fdlyl={d_date['FilingDelayMin']}&"
    link += f"fdlyh={d_date['FilingDelayMax']}&"
    link += f"daysago={d_date['NDaysAgo']}&"

    # Transaction Filing
    link += f"xp={'1' if d_transaction_filing['P_Purchase'] == 'true' else ''}&"
    link += f"xs={'1' if d_transaction_filing['S_Sale'] == 'true' else ''}&"
    if d_transaction_filing["A_Grant"] == "true":
        link += "xa=1&"
    if d_transaction_filing["D_SaleToLoss"] == "true":
        link += "xd=1&"
    if d_transaction_filing["G_Gift"] == "true":
        link += "xg=1&"
    if d_transaction_filing["NoDeriv"] == "true":
        link += "excludeDerivRelated=1&"
    if d_transaction_filing["F_Tax"] == "true":
        link += "xf=1&"
    if d_transaction_filing["M_OptionEx"] == "true":
        link += "xm=1&"
    if d_transaction_filing["X_OptionEx"] == "true":
        link += "xx=1&"
    if d_transaction_filing["C_CnvDeriv"] == "true":
        link += "xc=1&"
    if d_transaction_filing["W_Inherited"] == "true":
        link += "xw=1&"
    if d_transaction_filing["MultipleDays"] == "true":
        link += "tmult=1&"
    link += f"vl={d_transaction_filing['TradedMinK']}&"
    link += f"vh={d_transaction_filing['TradedMaxK']}&"
    link += f"ocl={d_transaction_filing['OwnChangeMinPct']}&"
    link += f"och={d_transaction_filing['OwnChangeMaxPct']}&"

    # Industry needs to be parsed
    link += "sic1=1&sic2=1&sicl=100&sich=199&"

    # Insider Title
    if d_insider_title["Officer"] == "true":
        link += "isofficer=1&"
    if d_insider_title["COB"] == "true":
        link += "iscob=1&"
    if d_insider_title["CEO"] == "true":
        link += "isceo=1&"
    if d_insider_title["Pres"] == "true":
        link += "ispres=1&"
    if d_insider_title["COO"] == "true":
        link += "iscoo=1&"
    if d_insider_title["CFO"] == "true":
        link += "iscfo=1&"
    if d_insider_title["GC"] == "true":
        link += "isgc=1&"
    if d_insider_title["VP"] == "true":
        link += "isvp=1&"
    if d_insider_title["Director"] == "true":
        link += "isdirector=1&"
    if d_insider_title["10PctOwn"] == "true":
        link += "istenpercent=1&"
    if d_insider_title["Other"] == "true":
        link += "isother=1&"

    # Others
    link += f"grp={d_GroupBy[d_others['GroupBy']]}&"

    # Company Totals
    link += f"nfl={d_company_totals['FilingsMin']}&"
    link += f"nfh={d_company_totals['FilingsMax']}&"
    link += f"nil={d_company_totals['InsidersMin']}&"
    link += f"nih={d_company_totals['InsidersMax']}&"
    link += f"nol={d_company_totals['OfficersMin']}&"
    link += f"noh={d_company_totals['OfficersMax']}&"
    link += f"v2l={d_company_totals['TradedMinK']}&"
    link += f"v2h={d_company_totals['TradedMaxK']}&"
    link += f"oc2l={d_company_totals['OwnChangeMinPct']}&"
    link += f"oc2h={d_company_totals['OwnChangeMaxPct']}&"

    # Others
    link += f"sortcol={d_SortBy[d_others['SortBy']]}&"
    link += f"cnt={d_others['MaxResults']}&"
    link += f"page={d_others['Page']}"

    return link


def get_open_insider_data(url: str):  # -> pd.DataFrame
    """Get open insider link

    Parameters
    ----------
    url: str
        open insider link with filters to retrieve data from

    Returns
    ----------
    data : pd.DataFrame
        open insider filtered data
    """
    text_soup_open_insider = BeautifulSoup(requests.get(url).text, "lxml")

    if len(text_soup_open_insider.find_all("tbody")) == 0:
        print("No insider trading found.")
        return pd.DataFrame()

    l_filing_link = list()
    l_ticker_link = list()
    l_insider_link = list()

    idx = 0
    for val in text_soup_open_insider.find_all("tbody")[1].find_all("a"):
        if idx == 0:
            l_filing_link.append(val["href"])
            idx += 1
        elif idx == 1:
            l_ticker_link.append("http://openinsider.com" + val["href"])
            idx += 1
        elif idx == 2:
            idx += 1
        else:
            l_insider_link.append("http://openinsider.com" + val["href"])
            idx = 0

    l_X = list()
    l_filing_date = list()
    l_trading_date = list()
    l_ticker = list()
    l_company = list()
    l_insider = list()
    l_title = list()
    l_trade_type = list()
    l_price = list()
    l_quantity = list()
    l_owned = list()
    l_delta_own = list()
    l_value = list()

    idx = 0
    for val in text_soup_open_insider.find_all("tbody")[1].find_all("td"):
        if idx == 0:
            l_X.append(val.text)
            idx += 1
        elif idx == 1:
            l_filing_date.append(val.text)
            idx += 1
        elif idx == 2:
            l_trading_date.append(val.text)
            idx += 1
        elif idx == 3:
            l_ticker.append(val.text.strip())
            idx += 1
        elif idx == 4:
            l_company.append(val.text)
            idx += 1
        elif idx == 5:
            l_insider.append(val.text)
            idx += 1
        elif idx == 6:
            l_title.append(val.text)
            idx += 1
        elif idx == 7:
            l_trade_type.append(val.text)
            idx += 1
        elif idx == 8:
            l_price.append(val.text)
            idx += 1
        elif idx == 9:
            l_quantity.append(val.text)
            idx += 1
        elif idx == 10:
            l_owned.append(val.text)
            idx += 1
        elif idx == 11:
            l_delta_own.append(val.text)
            idx += 1
        elif idx == 12:
            l_value.append(val.text)
            idx += 1
        elif idx < 16:
            idx += 1
        else:
            idx = 0

    d_open_insider = {
        "X": l_X,
        "Filing Date": l_filing_date,
        "Trading Date": l_trading_date,
        "Ticker": l_ticker,
        "Company": l_company,
        "Insider": l_insider,
        "Trade Type": l_trade_type,
        "Price": l_price,
        "Quantity": l_quantity,
        "Owned": l_owned,
        "Delta Own": l_delta_own,
        "Value": l_value,
        "Filing Link": l_filing_link,
        "Ticker Link": l_ticker_link,
        "Insider Link": l_insider_link,
    }

    return pd.DataFrame(d_open_insider)

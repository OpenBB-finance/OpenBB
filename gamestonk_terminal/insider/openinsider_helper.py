from datetime import datetime
from typing import Dict, List


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
        "LatestDay",
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
        if d_data[field] not in ["true", "false"]:
            error += f"Invalid {category}.{field} '{d_data[field]}'. Needs to be either 'true' or 'false'.\n"

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
    error = check_open_insider_date(d_date)
    error += check_open_insider_transaction_filing(d_transaction_filing)

    # Missing industry check!
    print(f"Industry check missing: {d_industry}")

    error += check_open_insider_insider_title(d_insider_title)
    error += check_open_insider_others(d_others)
    if d_others["GroupBy"] == "Company":
        error += check_open_insider_company_totals(d_company_totals)

    return error

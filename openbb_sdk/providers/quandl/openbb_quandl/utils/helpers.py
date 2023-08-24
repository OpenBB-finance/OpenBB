"""Quandl Helpers Module"""

from typing import List, Literal, Optional

import pandas as pd
import quandl

from openbb_quandl.utils.series_ids import CFTC, SP500MULTIPLES


def get_sp500_multiples(
    series_name: str = "PE Ratio by Month",
    start_date: Optional[str] = "",
    end_date: Optional[str] = "",
    collapse: Optional[
        Literal["daily", "weekly", "monthly", "quarterly", "annual"]
    ] = "monthly",
    transform: Optional[Literal["diff", "rdiff", "cumul", "normalize"]] = None,
    api_key: Optional[str] = "",
    **kwargs,
) -> pd.DataFrame:
    """Gets historical S&P 500 levels, ratios, and multiples.

    Parameters
    ----------
    series_name : str
        Name of the series. Defaults to "PE Ratio by Month".
    start_date : Optional[dateType]
        The start date of the time series. Defaults to all.
    end_date : Optional[dateType]
        The end date of the time series. Defaults to the most recent data.
    collapse : Optional[Literal["daily", "weekly", "monthly", "quarterly", "annual"]]
        The frequency of the time series. Defaults to "monthly".
    transform : Optional[Literal["diff", "rdiff", "cumul", "normalize"]]
    api_key : Optional[str]
        Quandl API key.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results.
    """

    if series_name not in SP500MULTIPLES:
        print("Invalid series name, choose from: ", list(SP500MULTIPLES.keys()))
        return pd.DataFrame()
    if "Year" in series_name:
        collapse = "annual"
    if "Quarter" in series_name:
        collapse = "quarterly"

    data = (
        quandl.get(
            SP500MULTIPLES[series_name],
            start_date=start_date,
            end_date=end_date,
            collapse=collapse,
            transform=transform,
            api_key=api_key,
            **kwargs,
        )
        .reset_index()
        .rename(columns={"Date": "date", "Value": "value"})
    )

    data["date"] = data["date"].dt.strftime("%Y-%m-%d")

    return data


def search_cot(query: str) -> List[dict]:
    """Search for available CFTC Commitment of Traders Reports.

    Parameters
    ----------
    query: str
        Query string.

    Returns
    -------
    List[Dict]
        List of dictionaries as records.
    """

    available_cot = pd.DataFrame(CFTC).transpose()
    available_cot.columns = available_cot.columns.str.lower()
    return (
        available_cot.query(
            "name.str.contains(@query, case=False)"
            "| category.str.contains(@query, case=False)"
            "| subcategory.str.contains(@query, case=False)"
            "| symbol.str.contains(@query, case=False)"
        )
        .reset_index(drop=True)
        .to_dict("records")
    )


def get_cot(
    code: str = "13874P",
    data_type: Optional[Literal["F", "O", "FO", "CITS"]] = "FO",
    legacy_format: bool = False,
    report_type: Optional[Literal["ALL", "CHG", "OLD", "OTR"]] = "ALL",
    measure: Optional[Literal["CR", "NT", "OI"]] = None,
    start_date: Optional[str] = "",
    end_date: Optional[str] = "",
    transform: Optional[Literal["diff", "rdiff", "cumul", "normalize"]] = None,
    api_key: Optional[str] = "",
    **kwargs,
) -> pd.DataFrame:
    """Get CFTC Commitment of Traders Report. If futures_only and options_only are both False, both will be returned.

    Not all combinations of parameters are valid.

    Parameters
    ----------
    code : str
        CFTC series code.  Use search_cot() to find the code.
        Also accepts certain symbols, such as "ES=F", or exact names.
        Default report is: S&P 500 Consolidated (CME)
    data_type: Optional[Literal["F", "O", "FO", "CITS"]]
        The type of data to reuturn. Default is "FO".

        F = Futures only

        FO = Futures and Options

        CITS = Commodity Index Trader Supplemental. Only valid for commodities.

    report_type: Optional[Literal["ALL", "CHG", "OLD", "OTR"]]
        The type of report to return. Default is "ALL".

            ALL = All

            CHG = Change in Positions

            OLD = Old Crop Years

            OTR = Other Crop Years

    measure : Optional[Literal["CR", "NT", "OI"]]
        The measure to return. Default is None.

            CR = Concentration Ratios

            NT = Number of Traders

            OI = Percent of Open Interest

            CHG = Change in Positions. Only valid when data_type is "CITS".

    start_date : Optional[dateType]
        The start date of the time series. Defaults to all.
    end_date : Optional[dateType]
        The end date of the time series. Defaults to the most recent data.
    transform : Optional[Literal["diff", "rdiff", "cumul", "normalize"]]
        Transform the data as w/w difference, percent change, cumulative, or normalize.
    api_key : Optional[str]
        Quandl API key.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results.
    """
    series_id: str = ""
    series_ids = pd.DataFrame(search_cot(query=""))

    if code in series_ids["code"].values:
        series_id = code

    if code not in series_ids["code"].values:
        if code in series_ids["symbol"].values:
            series_id = series_ids.loc[series_ids["symbol"] == code, "code"].values[0]
        if code in series_ids["name"].values:
            series_id = series_ids.loc[series_ids["name"] == code, "code"].values[0]

        if (
            code not in series_ids["code"].values
            or code not in series_ids["symbol"].values
            or code not in series_ids["name"].values
        ):
            series_id = code

    quandl_code = f"CFTC/{series_id}"

    if data_type == "F":
        quandl_code = f"{quandl_code}_F"

    if data_type == "FO":
        quandl_code = f"{quandl_code}_FO"

    if data_type == "CITS":
        quandl_code = f"{quandl_code}_CITS"

    if legacy_format and data_type != "CITS":
        quandl_code = f"{quandl_code}_L"

    if report_type:
        if report_type == "CHG":
            quandl_code = f"{quandl_code}_CHG"
        if report_type == "OLD":
            quandl_code = f"{quandl_code}_OLD"
        if report_type == "OTR":
            quandl_code = f"{quandl_code}_OTR"
        if report_type == "ALL":
            quandl_code = f"{quandl_code}_ALL"

    if measure is not None:
        if measure == "CR":
            quandl_code = f"{quandl_code}_CR"
        if measure == "NT":
            quandl_code = f"{quandl_code}_NT"
        if measure == "OI":
            quandl_code = f"{quandl_code}_OI"

    try:
        data = quandl.get(
            quandl_code,
            start_date=start_date,
            end_date=end_date,
            transform=transform,
            api_key=api_key,
        )
        return data.reset_index()

    except Exception as e:
        print(e)
        return pd.DataFrame()

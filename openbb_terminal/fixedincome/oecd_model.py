""" OECD model """
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

COUNTRY_TO_CODE_SHORT = {
    "australia": "AUS",
    "austria": "AUT",
    "belgium": "BEL",
    "bulgaria": "BGR",
    "canada": "CAN",
    "switzerland": "CHE",
    "chile": "CHL",
    "china": "CHN",
    "colombia": "COL",
    "costa_rica": "CRI",
    "czech_republic": "CZE",
    "germany": "DEU",
    "denmark": "DNK",
    "euro_area": "EA19",
    "spain": "ESP",
    "estonia": "EST",
    "finland": "FIN",
    "france": "FRA",
    "united_kingdom": "GBR",
    "greece": "GRC",
    "croatia": "HRV",
    "hungary": "HUN",
    "indonesia": "IDN",
    "india": "IND",
    "ireland": "IRL",
    "iceland": "ISL",
    "israel": "ISR",
    "italy": "ITA",
    "japan": "JPN",
    "korea": "KOR",
    "lithuania": "LTU",
    "luxembourg": "LUX",
    "latvia": "LVA",
    "mexico": "MEX",
    "netherlands": "NLD",
    "norway": "NOR",
    "new_zealand": "NZL",
    "poland": "POL",
    "portugal": "PRT",
    "romania": "ROU",
    "russia": "RUS",
    "slovak_republic": "SVK",
    "slovenia": "SVN",
    "sweden": "SWE",
    "united_states": "USA",
    "south_africa": "ZAF",
}


COUNTRY_TO_CODE_LONG = {
    "australia": "AUS",
    "austria": "AUT",
    "belgium": "BEL",
    "bulgaria": "BGR",
    "brazil": "BRA",
    "canada": "CAN",
    "switzerland": "CHE",
    "chile": "CHL",
    "china": "CHN",
    "colombia": "COL",
    "costa_rica": "CRI",
    "czech_republic": "CZE",
    "germany": "DEU",
    "denmark": "DNK",
    "euro_area": "EA19",
    "spain": "ESP",
    "estonia": "EST",
    "finland": "FIN",
    "france": "FRA",
    "united_kingdom": "GBR",
    "greece": "GRC",
    "croatia": "HRV",
    "hungary": "HUN",
    "indonesia": "IDN",
    "india": "IND",
    "ireland": "IRL",
    "iceland": "ISL",
    "israel": "ISR",
    "italy": "ITA",
    "japan": "JPN",
    "korea": "KOR",
    "lithuania": "LTU",
    "luxembourg": "LUX",
    "latvia": "LVA",
    "mexico": "MEX",
    "netherlands": "NLD",
    "norway": "NOR",
    "new_zealand": "NZL",
    "poland": "POL",
    "portugal": "PRT",
    "romania": "ROU",
    "russia": "RUS",
    "slovak_republic": "SVK",
    "slovenia": "SVN",
    "sweden": "SWE",
    "united_states": "USA",
    "south_africa": "ZAF",
}


@log_start_end(log=logger)
def get_interest_rate_data(
    data: str = "short",
    countries: Optional[List[str]] = None,
    start_date: str = "",
    end_date: str = "",
) -> pd.DataFrame:
    """Gets interest rate data from selected countries.

    Long-term interest rates refer to government bonds maturing in ten years. Rates are mainly determined by the
    price charged by the lender, the risk from the borrower and the fall in the capital value. Long-term interest
    rates are generally averages of daily rates, measured as a percentage. These interest rates are implied by the
    prices at which the government bonds are traded on financial markets, not the interest rates at which the loans
    were issued. In all cases, they refer to bonds whose capital repayment is guaranteed by governments. Long-term
    interest rates are one of the determinants of business investment. Low long-term interest rates encourage
    investment in new equipment and high interest rates discourage it. Investment is, in turn, a major source of
    economic growth.

    Short-term interest rates are the rates at which short-term borrowings are effected between financial
    institutions or the rate at which short-term government paper is issued or traded in the market. Short-term
    interest rates are generally averages of daily rates, measured as a percentage. Short-term interest rates are
    based on three-month money market rates where available. Typical standardised names are "money market rate" and
    "treasury bill rate".

    Parameters
    ----------
    data: str
        Type of data to getz, options ['short', 'short_forecast', 'long', 'long_forecast']
    countries: list
        List of countries to get data for
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format

    Returns
    -------
    pd.DataFrame
        Dataframe with the interest rate data
    """
    if data == "short":
        if isinstance(start_date, datetime):
            start_date = start_date.strftime("%Y-%m")
        elif len(start_date) > 8:
            start_date = start_date[:8]
        if isinstance(end_date, datetime):
            end_date = end_date.strftime("%Y-%m")
        elif len(end_date) > 8:
            end_date = end_date[:8]
        df = pd.read_csv(
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.STINT.TOT.PC_PA.M/OECD?contentType=csv&detail=code"
            f"&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
            index_col=5,
        )
        data_name = "3 month"
    elif data == "short_forecast":
        if isinstance(start_date, datetime):
            month = start_date.month
            start_date = start_date.strftime("%Y") + "-Q" + str((month - 1) // 3 + 1)
        elif len(start_date) > 7:
            month = int(start_date[5:7])
            start_date = start_date[:4] + "-Q" + str((month - 1) // 3 + 1)
        if isinstance(end_date, datetime):
            month = end_date.month
            end_date = end_date.strftime("%Y") + "-Q" + str((month - 1) // 3 + 1)
        elif len(end_date) > 7:
            month = int(end_date[5:7])
            end_date = end_date[:4] + "-Q" + str((month - 1) // 3 + 1)
        df = pd.read_csv(
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.STINTFORECAST.TOT.PC_PA.Q/OECD?contentType=csv&detail"
            f"=code&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
            index_col=5,
        )
        data_name = "3 month with forecast"

    elif data == "long":
        if isinstance(start_date, datetime):
            start_date = start_date.strftime("%Y-%m")
        elif len(start_date) > 8:
            start_date = start_date[:8]
        if isinstance(end_date, datetime):
            end_date = end_date.strftime("%Y-%m")
        elif len(end_date) > 8:
            end_date = end_date[:8]
        df = pd.read_csv(
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.LTINT.TOT.PC_PA.M/OECD?contentType=csv&detail=code"
            f"&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
            index_col=5,
        )
        data_name = "10 year"
    elif data == "long_forecast":
        if isinstance(start_date, datetime):
            month = start_date.month
            start_date = start_date.strftime("%Y") + "-Q" + str((month - 1) // 3 + 1)
        elif len(start_date) > 7:
            month = int(start_date[5:7])
            start_date = start_date[:4] + "-Q" + str((month - 1) // 3 + 1)
        if isinstance(end_date, datetime):
            month = end_date.month
            end_date = end_date.strftime("%Y") + "-Q" + str((month - 1) // 3 + 1)
        elif len(end_date) > 7:
            month = int(end_date[5:7])
            end_date = end_date[:4] + "-Q" + str((month - 1) // 3 + 1)
        df = pd.read_csv(
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.LTINTFORECAST.TOT.PC_PA.Q/OECD?contentType=csv&detail"
            f"=code&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
            index_col=5,
        )
        data_name = "10 year with forecast"
    else:
        return pd.DataFrame()
    df = df.iloc[:, [0, 5]]

    result = pd.DataFrame()
    for country in countries:  # type: ignore
        if data in ["short", "short_forecast"]:
            temp = pd.DataFrame(
                df[df["LOCATION"] == COUNTRY_TO_CODE_SHORT[country]]["Value"]
            )
        else:
            temp = pd.DataFrame(
                df[df["LOCATION"] == COUNTRY_TO_CODE_LONG[country]]["Value"]
            )
        temp.columns = [f"{country} ({data_name})"]
        result = pd.concat([result, temp], axis=1)

    result.index = pd.to_datetime(result.index).date
    result.sort_index(inplace=True)

    return result


def get_treasury(
    short_term: Optional[list] = None,
    long_term: Optional[list] = None,
    forecast: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Gets interest rates data from selected countries (3 month and 10 year)

    Short-term interest rates are the rates at which short-term borrowings are effected between financial
    institutions or the rate at which short-term government paper is issued or traded in the market. Short-term
    interest rates are generally averages of daily rates, measured as a percentage. Short-term interest rates are
    based on three-month money market rates where available. Typical standardised names are "money market rate" and
    "treasury bill rate".

    Long-term interest rates refer to government bonds maturing in ten years. Rates are mainly determined by the
    price charged by the lender, the risk from the borrower and the fall in the capital value. Long-term interest
    rates are generally averages of daily rates, measured as a percentage. These interest rates are implied by the
    prices at which the government bonds are traded on financial markets, not the interest rates at which the loans
    were issued. In all cases, they refer to bonds whose capital repayment is guaranteed by governments. Long-term
    interest rates are one of the determinants of business investment. Low long-term interest rates encourage
    investment in new equipment and high interest rates discourage it. Investment is, in turn, a major source of
    economic growth.

    Parameters
    ----------
    short_term: list
        Countries you wish to plot the 3-month interest rate for
    long_term: list
        Countries you wish to plot the 10-year interest rate for
    forecast: bool
        If True, plot forecasts for short term interest rates
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format
    """
    df_short, df_long = pd.DataFrame(), pd.DataFrame()

    if short_term:
        df_short = get_interest_rate_data(
            f"short{'_forecast' if forecast else ''}",
            short_term,
            start_date if start_date is not None else "",
            end_date if end_date is not None else "",
        )
    if long_term:
        df_long = get_interest_rate_data(
            f"long{'_forecast' if forecast else ''}",
            long_term,
            start_date if start_date is not None else "",
            end_date if end_date is not None else "",
        )

    df = pd.concat([df_short, df_long], axis=1)

    return df

""" EconDB Model """
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
import pandas_datareader.data as web

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


TREASURIES: Dict = {
    "frequencies": {
        "annually": 203,
        "monthly": 129,
        "weekly": 21,
        "daily": 9,
    },
    "instruments": {
        "nominal": {
            "identifier": "TCMNOM",
            "maturities": {
                "1m": "1-month",
                "3m": "3-month",
                "6m": "6-month",
                "1y": "1-year",
                "2y": "2-year",
                "3y": "3-year",
                "5y": "5-year",
                "7y": "7-year",
                "10y": "10-year",
                "20y": "20-year",
                "30y": "30-year",
            },
        },
        "inflation": {
            "identifier": "TCMII",
            "maturities": {
                "5y": "5-year",
                "7y": "7-year",
                "10y": "10-year",
                "20y": "20-year",
                "30y": "30-year",
            },
        },
        "average": {
            "identifier": "LTAVG",
            "maturities": {
                "Longer than 10-year": "Longer than 10-year",
            },
        },
        "secondary": {
            "identifier": "TB",
            "maturities": {
                "4w": "4-week",
                "3m": "3-month",
                "6m": "6-month",
                "1y": "1-year",
            },
        },
    },
}


@log_start_end(log=logger)
def get_treasuries(
    instruments: Optional[list] = None,
    maturities: Optional[list] = None,
    frequency: str = "monthly",
    start_date: str = "1900-01-01",
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get U.S. Treasury rates [Source: EconDB]

    Parameters
    ----------
    instruments: list
        Type(s) of treasuries, nominal, inflation-adjusted (long term average) or secondary market.
        Available options can be accessed through economy.treasury_maturities().
    maturities : list
        Treasury maturities to get. Available options can be accessed through economy.treasury_maturities().
    frequency : str
        Frequency of the data, this can be annually, monthly, weekly or daily.
    start_date : str
        Starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : Optional[str]
        End date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.

    Returns
    -------
    treasury_data: pd.Dataframe
        Holds data of the selected types and maturities
    """

    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")

    if instruments is None:
        instruments = ["nominal"]
    if maturities is None:
        maturities = ["10y"]

    treasury_data: Dict[Any, Dict[Any, pd.Series]] = {}

    for instrument in instruments:
        if instrument not in TREASURIES["instruments"]:
            console.print(
                f"{instrument} is not an option. Please choose between: "
                f"{', '.join(TREASURIES['instruments'].keys())}"
            )
        else:
            instrument_identifier = TREASURIES["instruments"][instrument]["identifier"]
            frequency_number = TREASURIES["frequencies"][frequency]
            df = web.DataReader(
                "&".join(
                    [
                        "dataset=FRB_H15",
                        "v=Instrument",
                        "h=TIME",
                        f"instrument=[{instrument_identifier}]",
                        f"from={start_date}",
                        f"to={end_date}",
                        f"freq=[{frequency_number}",
                        "UNIT=[PERCENT:_PER_YEAR]",
                    ]
                ),
                "econdb",
            )

            if instrument == "average":
                maturities_list = ["Longer than 10-year"]
                type_string = "Long-term average"
            else:
                maturities_list = maturities
                type_string = instrument.capitalize()

            treasury_data[type_string] = {}

            for maturity in maturities_list:
                if maturity not in TREASURIES["instruments"][instrument]["maturities"]:
                    console.print(
                        f"The maturity {maturity} is not an option for {instrument}. Please choose between "
                        f"{', '.join(TREASURIES['instruments'][instrument]['maturities'].keys())}"
                    )
                else:
                    maturity_string = TREASURIES["instruments"][instrument][
                        "maturities"
                    ][maturity]

                    for column in df.columns:
                        # check if type inside the name and maturity inside the maturity string
                        if (
                            type_string.lower() in column[2].lower()
                            and maturity_string in column[3]
                        ):
                            treasury_data[type_string][maturity_string] = df[
                                column
                            ].dropna()
                            break

                    if maturity_string not in treasury_data[type_string]:
                        console.print(
                            f"No data found for the combination {instrument} and {maturity}."
                        )

    df = pd.DataFrame.from_dict(treasury_data, orient="index").stack().to_frame()
    df = pd.DataFrame(df[0].values.tolist(), index=df.index).T
    df.columns = ["_".join(column) for column in df.columns]

    return df

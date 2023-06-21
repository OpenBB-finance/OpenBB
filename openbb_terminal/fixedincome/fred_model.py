""" FRED model """
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# IMPORTATION THIRDPARTY
import certifi
import numpy as np
import pandas as pd
from fredapi import Fred
from requests import HTTPError

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.rich_config import console

# pylint: disable=attribute-defined-outside-init,dangerous-default-value
# pylint: disable=C0302

logger = logging.getLogger(__name__)

ice_bofa_path = (Path(__file__).parent / "ice_bofa_indices.csv").resolve()
commercial_paper_path = (Path(__file__).parent / "commercial_paper.csv").resolve()
spot_rates_path = (Path(__file__).parent / "corporate_spot_rates.csv").resolve()

YIELD_CURVE_SERIES_NOMINAL = {
    "1Month": "DGS1MO",
    "3Month": "DGS3MO",
    "6Month": "DGS6MO",
    "1Year": "DGS1",
    "2Year": "DGS2",
    "3Year": "DGS3",
    "5Year": "DGS5",
    "7Year": "DGS7",
    "10Year": "DGS10",
    "20Year": "DGS20",
    "30Year": "DGS30",
}
YIELD_CURVE_SERIES_REAL = {
    "5Year": "DFII5",
    "7Year": "DFII7",
    "10Year": "DFII10",
    "20Year": "DFII20",
    "30Year": "DFII30",
}

YIELD_CURVE_SERIES_CORPORATE_SPOT = {
    "6Month": "HQMCB6MT",
    "1Year": "HQMCB1YR",
    "2Year": "HQMCB2YR",
    "3Year": "HQMCB3YR",
    "5Year": "HQMCB5YR",
    "7Year": "HQMCB7YR",
    "10Year": "HQMCB10YR",
    "20Year": "HQMCB20YR",
    "30Year": "HQMCB30YR",
    "50Year": "HQMCB50YR",
    "75Year": "HQMCB75YR",
    "100Year": "HQMCB100YR",
}
YIELD_CURVE_SERIES_CORPORATE_PAR = {
    "2Year": "HQMCB2YRP",
    "5Year": "HQMCB5YRP",
    "10Year": "HQMCB10YRP",
    "30Year": "HQMCB30YRP",
}

YIELD_CURVE_NOMINAL_RATES = [1 / 12, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]
YIELD_CURVE_SPOT_RATES = [0.5, 1, 2, 3, 5, 7, 10, 20, 30, 50, 75, 100]
YIELD_CURVE_REAL_RATES = [5, 7, 10, 20, 30]
YIELD_CURVE_PAR_RATES = [2, 5, 10, 30]

ice_bofa_path = (Path(__file__).parent / "ice_bofa_indices.csv").resolve()
commercial_paper_path = (Path(__file__).parent / "commercial_paper.csv").resolve()
spot_rates_path = (Path(__file__).parent / "corporate_spot_rates.csv").resolve()


NAME_TO_ID_PROJECTION = {
    "Range High": ["FEDTARRH", "FEDTARRHLR"],
    "Central tendency High": ["FEDTARCTH", "FEDTARCTHLR"],
    "Median": ["FEDTARMD", "FEDTARMDLR"],
    "Range Midpoint": ["FEDTARRM", "FEDTARRMLR"],
    "Central tendency Midpoint": ["FEDTARCTM", "FEDTARCTMLR"],
    "Range Low": ["FEDTARRL", "FEDTARRLLR"],
    "Central tendency Low": ["FEDTARCTL", "FEDTARCTLLR"],
}

NAME_TO_ID_ECB = {"deposit": "ECBDFR", "lending": "ECBMLFR", "refinancing": "ECBMRRFR"}

USARATES_TO_FRED_ID = {
    "4_week": {"tbill": "DTB4WK"},
    "1_month": {"cmn": "DGS1MO"},
    "3_month": {"tbill": "TB3MS", "cmn": "DGS3MO"},
    "6_month": {"tbill": "DTB6", "cmn": "DGS6MO"},
    "1_year": {"tbill": "DTB1YR", "cmn": "DGS1"},
    "2_year": {"cmn": "DGS2"},
    "3_year": {"cmn": "DGS3"},
    "5_year": {"tips": "DFII5", "cmn": "DGS5"},
    "7_year": {"tips": "DFII7", "cmn": "DGS7"},
    "10_year": {"tips": "DFII10", "cmn": "DGS10"},
    "20_year": {"tips": "DFII20", "cmn": "DGS20"},
    "30_year": {"tips": "DFII30", "cmn": "DGS30"},
}

ICE_BOFA_TO_OPTIONS = {
    "Type": ["total_return", "yield", "yield_to_worst"],
    "Category": ["all", "duration", "eur", "usd"],
    "Area": ["asia", "emea", "eu", "ex_g10", "latin_america", "us"],
    "Grade": [
        "a",
        "aa",
        "aaa",
        "b",
        "bb",
        "bbb",
        "ccc",
        "crossover",
        "high_grade",
        "high_yield",
        "non_financial",
        "non_sovereign",
        "private_sector",
        "public_sector",
    ],
}

MOODY_TO_OPTIONS: Dict[str, Dict] = {
    "Type": {
        "aaa": {
            "index": {
                "id": "DAAA",
                "name": "Moody's Seasoned Aaa Corporate Bond Yield",
            },
            "treasury": {
                "id": "AAA10Y",
                "name": "Moody's Seasoned Aaa Corporate Bond Yield Relative to Yield "
                "on 10-Year Treasury Constant Maturity",
            },
            "fed_funds": {
                "id": "AAAFF",
                "name": "Moody's Seasoned Aaa Corporate Bond Minus Federal Funds Rate",
            },
        },
        "baa": {
            "index": {
                "id": "DBAA",
                "name": "Moody's Seasoned Baa Corporate Bond Yield",
            },
            "treasury": {
                "id": "BAA10Y",
                "name": "Moody's Seasoned Baa Corporate Bond Yield Relative "
                "to Yield on 10-Year Treasury Constant Maturity",
            },
            "fed_funds": {
                "id": "BAAFF",
                "name": "Moody's Seasoned Baa Corporate Bond Minus Federal Funds Rate",
            },
        },
    },
    "Spread": ["treasury", "fed_funds"],  # type: ignore
}
SPOT_TO_OPTIONS = {
    "Maturity": [f"{i}y".replace(".0", "") for i in np.arange(1, 100.5, 0.5)],
    "Category": ["spot_rate", "par_yield"],
}
CP_TO_OPTIONS = {
    "Maturity": ["15d", "30d", "60d", "7d", "90d", "overnight"],
    "Category": ["asset_backed", "financial", "non_financial", "spread"],
    "Grade": ["a2_p2", "aa"],
}

ESTR_PARAMETER_TO_ECB_ID = {
    "volume_weighted_trimmed_mean_rate": "ECBESTRVOLWGTTRMDMNRT",
    "number_of_transactions": "ECBESTRNUMTRANS",
    "number_of_active_banks": "ECBESTRNUMACTBANKS",
    "total_volume": "ECBESTRTOTVOL",
    "share_of_volume_of_the_5_largest_active_banks": "ECBESTRSHRVOL5LRGACTBNK",
    "rate_at_75th_percentile_of_volume": "ECBESTRRT75THPCTVOL",
    "rate_at_25th_percentile_of_volume": "ECBESTRRT25THPCTVOL",
}

SOFR_PARAMETER_TO_FRED_ID = {
    "overnight": "SOFR",
    "30_day_average": "SOFR30DAYAVG",
    "90_day_average": "SOFR90DAYAVG",
    "180_day_average": "SOFR180DAYAVG",
    "index": "SOFRINDEX",
}
SONIA_PARAMETER_TO_FRED_ID = {
    "rate": "IUDSOIA",
    "index": "IUDZOS2",
    "10th_percentile": "IUDZLS6",
    "25th_percentile": "IUDZLS7",
    "75th_percentile": "IUDZLS8",
    "90th_percentile": "IUDZLS9",
    "total_nominal_value": "IUDZLT2",
}
AMERIBOR_PARAMETER_TO_FRED_ID = {
    "overnight": "AMERIBOR",
    "term_30": "AMBOR30T",
    "term_90": "AMBOR90T",
    "1_week_term_structure": "AMBOR1W",
    "1_month_term_structure": "AMBOR1M",
    "3_month_term_structure": "AMBOR3M",
    "6_month_term_structure": "AMBOR6M",
    "1_year_term_structure": "AMBOR1Y",
    "2_year_term_structure": "AMBOR2Y",
    "30_day_ma": "AMBOR30",
    "90_day_ma": "AMBOR90",
}

FED_PARAMETER_TO_FRED_ID = {
    "monthly": "FEDFUNDS",
    "daily": "DFF",
    "weekly": "FF",
    "daily_excl_weekend": "RIFSPFFNB",
    "annual": "RIFSPFFNA",
    "biweekly": "RIFSPFFNBWAW",
    "volume": "EFFRVOL",
}

OBFR_PARAMETER_TO_FRED_ID = {
    "daily": "OBFR",
    "volume": "OBFRVOL",
}

DWPCR_PARAMETER_TO_FRED_ID = {
    "daily_excl_weekend": "DPCREDIT",
    "monthly": "MPCREDIT",
    "weekly": "WPCREDIT",
    "daily": "RIFSRPF02ND",
    "annual": "RIFSRPF02NA",
}
TMC_PARAMETER_TO_FRED_ID = {
    "3_month": "T10Y3M",
    "2_year": "T10Y2Y",
}
FFRMC_PARAMETER_TO_FRED_ID = {
    "10_year": "T10YFF",
    "5_year": "T5YFF",
    "1_year": "T1YFF",
    "6_month": "T6MFF",
    "3_month": "T3MFF",
}

TBFFR_PARAMETER_TO_FRED_ID = {
    "3_month": "TB3SMFFM",
    "6_month": "TB6SMFFM",
}


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def get_series_data(
    series_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None
) -> pd.DataFrame:
    """Get Series data. [Source: FRED]

    Parameters
    ----------
    series_id : str
        Series ID to get data from
    start_date : Optional[str]
        Start date to get data from, format yyyy-mm-dd
    end_date : Optional[str]
        End data to get from, format yyyy-mm-dd

    Returns
    -------
    pd.DataFrame
        Series data
    """
    try:
        # Necessary for installer so that it can locate the correct certificates for
        # API calls and https
        # https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error/73270162#73270162
        os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
        os.environ["SSL_CERT_FILE"] = certifi.where()
        fredapi_client = Fred(get_current_user().credentials.API_FRED_KEY)
        df = fredapi_client.get_series(series_id, start_date, end_date)
    # Series does not exist & invalid api keys
    except HTTPError as e:
        console.print(e)

    return df


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def get_yield_curve(
    date: str = "",
    return_date: bool = False,
    inflation_adjusted: bool = False,
    spot_or_par: Optional[str] = None,
) -> Tuple[pd.DataFrame, str]:
    """Gets yield curve data from FRED.

    The graphic depiction of the relationship between the yield on bonds of the same credit quality but different
    maturities is known as the yield curve. In the past, most market participants have constructed yield curves from
    the observations of prices and yields in the Treasury market. Two reasons account for this tendency. First,
    Treasury securities are viewed as free of default risk, and differences in creditworthiness do not affect yield
    estimates. Second, as the most active bond market, the Treasury market offers the fewest problems of illiquidity
    or infrequent trading. The key function of the Treasury yield curve is to serve as a benchmark for pricing bonds
    and setting yields in other sectors of the debt market.

    It is clear that the market’s expectations of future rate changes are one important determinant of the
    yield-curve shape. For example, a steeply upward-sloping curve may indicate market expectations of near-term Fed
    tightening or of rising inflation. However, it may be too restrictive to assume that the yield differences across
    bonds with different maturities only reflect the market’s rate expectations. The well-known pure expectations
    hypothesis has such an extreme implication. The pure expectations hypothesis asserts that all government bonds
    have the same near-term expected return (as the nominally riskless short-term bond) because the return-seeking
    activity of risk-neutral traders removes all expected return differentials across bonds.

    Parameters
    ----------
    date: str
        Date to get curve for. If empty, gets most recent date (format yyyy-mm-dd)
    return_date: bool
        If True, returns date of yield curve

    Returns
    -------
    Tuple[pd.DataFrame, str]
        Dataframe of yields and maturities,
        Date for which the yield curve is obtained

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> ycrv_df = openbb.fixedincome.ycrv()

    Since there is a delay with the data, the most recent date is returned and can be accessed with return_date=True
    >>> ycrv_df, ycrv_date = openbb.fixedincome.ycrv(return_date=True)
    """

    # Necessary for installer so that it can locate the correct certificates for
    # API calls and https
    # https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error/73270162#73270162
    # os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
    # os.environ["SSL_CERT_FILE"] = certifi.where()

    fredapi_client = Fred(get_current_user().credentials.API_FRED_KEY)

    df = pd.DataFrame()

    # Check that the date is in the past
    today = datetime.now().strftime("%Y-%m-%d")
    if date and date >= today:
        console.print("[red]Date cannot be today or in the future[/red]")
        if return_date:
            return pd.DataFrame(), date
        return pd.DataFrame()

    # Add in logic that will get the most recent date
    if date:
        get_last = False
        start_date = (
            datetime.strptime(date, "%Y-%m-%d") - timedelta(days=50)
        ).strftime("%Y-%m-%d")
    else:
        date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=50)).strftime("%Y-%m-%d")
        get_last = True

    if inflation_adjusted:
        fred_series = YIELD_CURVE_SERIES_REAL
        years = YIELD_CURVE_REAL_RATES
    elif spot_or_par:
        if spot_or_par == "spot":
            years = YIELD_CURVE_SPOT_RATES  # type: ignore
            fred_series = YIELD_CURVE_SERIES_CORPORATE_SPOT
        elif spot_or_par == "par":
            years = YIELD_CURVE_PAR_RATES
            fred_series = YIELD_CURVE_SERIES_CORPORATE_PAR
        else:
            console.print("Please select either 'spot' or 'par' rates.")
    else:
        fred_series = YIELD_CURVE_SERIES_NOMINAL
        years = YIELD_CURVE_NOMINAL_RATES  # type: ignore

    for key, s_id in fred_series.items():
        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    fredapi_client.get_series(s_id, start_date), columns=[key]
                ),
            ],
            axis=1,
        )
    if df.empty:
        if return_date:
            return pd.DataFrame(), date
        return pd.DataFrame()
    # Drop rows with NaN -- corresponding to weekends typically
    df = df.dropna()

    if date not in df.index or get_last:
        # If the get_last flag is true, we want the first date, otherwise we want the last date.
        idx = -1 if get_last else 0
        date_of_yield = df.index[idx].strftime("%Y-%m-%d")
        rates = pd.DataFrame(df.iloc[idx, :].values, columns=["Rate"])

        if spot_or_par:
            console.print(
                f"Because {spot_or_par.title()} rates are published monthly, "
                f"the nearest date to {date} is used which is {date_of_yield}."
            )
    else:
        date_of_yield = date
        series = df[df.index == date]
        if series.empty:
            return pd.DataFrame(), date_of_yield
        rates = pd.DataFrame(series.values.T, columns=["Rate"])

    rates.insert(0, "Maturity", years)
    if return_date:
        return rates, date_of_yield
    return rates


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def get_estr(
    parameter: str = "volume_weighted_trimmed_mean_rate",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Obtain data for Euro Short-Term Rate (ESTR)

    Parameters
    ----------
    parameter: str
        The parameter to get data for.
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    series_id = ESTR_PARAMETER_TO_ECB_ID.get(parameter, "")

    return pd.DataFrame(
        get_series_data(series_id=series_id, start_date=start_date, end_date=end_date),
        columns=[series_id],
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def get_sofr(
    parameter: str = "overnight",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Obtain data for Secured Overnight Financing Rate (SOFR)

    Parameters
    ----------
    parameter: str
        The parameter to get data for. Choose from:
            "overnight"
            "30_day_average"
            "90_day_average"
            "180_day_average"
            "index"
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    series_id = SOFR_PARAMETER_TO_FRED_ID.get(parameter, "")

    return pd.DataFrame(
        get_series_data(series_id=series_id, start_date=start_date, end_date=end_date),
        columns=[series_id],
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def get_sonia(
    parameter: str = "rate",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Obtain data for Sterling Overnight Index Average (SONIA)

    Parameters
    ----------
    parameter: str
        The parameter to get data for.
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    series_id = SONIA_PARAMETER_TO_FRED_ID.get(parameter, "")

    return pd.DataFrame(
        get_series_data(series_id=series_id, start_date=start_date, end_date=end_date),
        columns=[series_id],
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def get_ameribor(
    parameter: str = "overnight",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Obtain data for American Interbank Offered Rate (AMERIBOR)

    Parameters
    ----------
    parameter: str
        The parameter to get data for. Choose from:
            "overnight": "AMERIBOR",
            "term_30": "AMBOR30T",
            "term_90": "AMBOR90T",
            "1_week_term_structure": "AMBOR1W",
            "1_month_term_structure": "AMBOR1M",
            "3_month_term_structure": "AMBOR3M",
            "6_month_term_structure": "AMBOR6M",
            "1_year_term_structure": "AMBOR1Y",
            "2_year_term_structure": "AMBOR2Y",
            "30_day_ma": "AMBOR30",
            "90_day_ma": "AMBOR90",
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    series_id = AMERIBOR_PARAMETER_TO_FRED_ID.get(parameter, "")

    return pd.DataFrame(
        get_series_data(series_id=series_id, start_date=start_date, end_date=end_date),
        columns=[series_id],
    )


def get_fed(
    parameter: str = "monthly",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    overnight: bool = False,
    quantiles: bool = False,
    target: bool = False,
) -> pd.DataFrame:
    """Obtain data for Effective Federal Funds Rate.

    Parameters
    ----------
    parameter: str
        The parameter to get data for. Choose from:
            "monthly"
            "daily"
            "weekly"
            "daily_excl_weekend"
            "annual"
            "biweekly"
            "volume"
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    overnight: bool
        Whether you want to plot the Overnight Banking Federal Rate
    quantiles: bool
        Whether you want to see the 1, 25, 75 and 99 percentiles
    target: bool
        Whether you want to see the high and low target range
    """
    series_id = FED_PARAMETER_TO_FRED_ID[parameter]

    if overnight:
        # This piece of code adjusts the series id when the user wants to plot the overnight rate
        if series_id == "DFF":
            series_id = "OBFR"
        elif series_id == "EFFRVOL":
            series_id = "OBFRVOL"
        else:
            console.print(
                "The Overnight Banking Federal Rate only supports Daily data."
            )
            series_id = "OBFR"

    if quantiles or target and not overnight:
        data_series = [series_id if series_id != "EFFRVOL" else "EFFR"]
        series_id = series_id if series_id != "EFFRVOL" else "EFFR"

        if quantiles:
            data_series.extend(["EFFR1", "EFFR25", "EFFR75", "EFFR99"])
        if target:
            data_series.extend(["DFEDTARU", "DFEDTARL"])

        df = pd.DataFrame()

        for series in data_series:
            data = pd.DataFrame(
                get_series_data(
                    series_id=series, start_date=start_date, end_date=end_date
                ),
                columns=[series],
            )
            df = data if series == series_id else pd.concat([df, data], axis=1)

        df = df.dropna()
        return df
    return pd.DataFrame(
        get_series_data(series_id=series_id, start_date=start_date, end_date=end_date),
        columns=[series_id],
    )


def get_iorb(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Obtain data for Interest Rate on Reserve Balances.

    Parameters
    ----------
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    return pd.DataFrame(
        get_series_data(series_id="IORB", start_date=start_date, end_date=end_date),
        columns=["IORB"],
    )


def get_projection(long_run: bool = False):
    """Obtain data for the Federal Reserve's projection of the federal funds rate.

    Parameters
    ----------
    long_run: str
        Whether to obtain data for the long run projection.
    """
    data_series = {}

    for projection, values in NAME_TO_ID_PROJECTION.items():
        data_series[projection] = get_series_data(series_id=values[long_run])

    data_series_df = pd.DataFrame.from_dict(data_series).dropna()
    data_series_df.index = pd.to_datetime(data_series_df.index).date
    data_series_df.index.name = "Date"
    return data_series_df


def get_dwpcr(
    parameter: str = "daily_excl_weekend",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Obtain data for the Discount Window Primary Credit Rate.

    Parameters
    ----------
    parameter: str
        The parameter to get data for. Choose from:
            "daily_excl_weekend"
            "monthly"
            "weekly"
            "daily"
            "annual"
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    series_id = DWPCR_PARAMETER_TO_FRED_ID[parameter]
    return pd.DataFrame(
        get_series_data(series_id=series_id, start_date=start_date, end_date=end_date),
        columns=[series_id],
    )


def get_ecb(
    interest_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Obtain data for ECB interest rates.

    The Governing Council of the ECB sets the key interest rates for the euro area:

    - The interest rate on the main refinancing operations (MRO), which provide
    the bulk of liquidity to the banking system.
    - The rate on the deposit facility, which banks may use to make overnight deposits with the Eurosystem.
    - The rate on the marginal lending facility, which offers overnight credit to banks from the Eurosystem.

    Parameters
    ----------
    interest_type: Optional[str]
        The ability to decide what interest rate to plot. Choose from:
            "deposit"
            "lending"
            "refinancing"
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    if interest_type:
        df = pd.DataFrame(
            get_series_data(
                series_id=NAME_TO_ID_ECB[interest_type],
                start_date=start_date,
                end_date=end_date,
            ),
            columns=[interest_type],
        )

    else:
        series_dictionary = {}

        for interest_name, value in NAME_TO_ID_ECB.items():
            series_dictionary[interest_name.title()] = get_series_data(
                series_id=value, start_date=start_date, end_date=end_date
            )

        df = pd.DataFrame.from_dict(series_dictionary)
        df.index = pd.to_datetime(df.index).date
        df.index.name = "Date"

    return df


def get_usrates(
    parameter: str = "tbills",
    maturity: str = "3_months",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Plot various treasury rates from the United States

    A Treasury Bill (T-Bill) is a short-term U.S. government debt obligation backed by the Treasury Department with a
    maturity of one year or less. Treasury bills are usually sold in denominations of $1,000. However, some can reach
    a maximum denomination of $5 million in non-competitive bids. These securities are widely regarded as low-risk
    and secure investments.

    Yields on Treasury nominal securities at “constant maturity” are interpolated by the U.S. Treasury from the daily
    yield curve for non-inflation-indexed Treasury securities. This curve, which relates the yield on a security to
    its time to maturity, is based on the closing market bid yields on actively traded Treasury securities in the
    over-the-counter market. These market yields are calculated from composites of quotations obtained by the Federal
    Reserve Bank of New York. The constant maturity yield values are read from the yield curve at fixed maturities,
    currently 1, 3, and 6 months and 1, 2, 3, 5, 7, 10, 20, and 30 years. This method provides a yield for a 10-year
    maturity, for example, even if no outstanding security has exactly 10 years remaining to maturity. Similarly,
    yields on inflation-indexed securities at “constant maturity” are interpolated from the daily yield curve for
    Treasury inflation protected securities in the over-the-counter market. The inflation-indexed constant maturity
    yields are read from this yield curve at fixed maturities, currently 5, 7, 10, 20, and 30 years.

    Parameters
    ----------
    parameter: str
        Either "tbills", "cmn", or "tips".
    maturity: str
        Depending on the chosen parameter, a set of maturities is available.
            "4_week": {"tbill": "DTB4WK"},
            "1_month": {"cmn": "DGS1MO"},
            "3_month": {"tbill": "TB3MS", "cmn": "DGS3MO"},
            "6_month": {"tbill": "DTB6", "cmn": "DGS6MO"},
            "1_year": {"tbill": "DTB1YR", "cmn": "DGS1"},
            "2_year": {"cmn": "DGS2"},
            "3_year": {"cmn": "DGS3"},
            "5_year": {"tips": "DFII5", "cmn": "DGS5"},
            "7_year": {"tips": "DFII7", "cmn": "DGS7"},
            "10_year": {"tips": "DFII10", "cmn": "DGS10"},
            "20_year": {"tips": "DFII20", "cmn": "DGS20"},
            "30_year": {"tips": "DFII30", "cmn": "DGS30"},
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    series_id = USARATES_TO_FRED_ID[maturity][parameter]
    return pd.DataFrame(
        get_series_data(series_id=series_id, start_date=start_date, end_date=end_date),
        columns=[series_id],
    )


def get_icebofa(
    data_type: str = "yield",
    category: str = "all",
    area: str = "us",
    grade: str = "non_sovereign",
    options: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get data for ICE BofA US Corporate Bond Indices.

    Find the available options by using the options parameter.

    Parameters
    ----------
    data_type: str
        The type of data you want to see, either "yield", "yield_to_worst", "total_return", or "spread"
    category: str
        The type of category you want to see, either "all", "duration", "eur" or "usd".
    area: str
        The type of area you want to see, either "asia", "emea", "eu", "ex_g10", "latin_america" or "us"
    grade: str
        The type of grade you want to see, either "a", "aa", "aaa", "b", "bb", "bbb", "ccc", "crossover",
        "high_grade", "high_yield", "non_financial", "non_sovereign", "private_sector", "public_sector"
    options: bool
        Set to True to obtain the available options.
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    series = pd.read_csv(ice_bofa_path)

    if options:
        return series.drop(
            ["Frequency", "Units", "Asset Class", "FRED Series ID", "Description"],
            axis=1,
        )[
            series["Type"].isin(
                ["yield", "yield_to_worst", "total_return"]
                if data_type != "spread"
                else ["spread"]
            )
        ]

    if data_type == "total_return":
        units = "index"
    elif data_type in ["yield", "yield_to_worst", "spread"]:
        units = "percent"
    else:
        console.print(
            "Please choose either 'yield', 'yield_to_worst', "
            "'total_return' or 'spread'."
        )
        return pd.DataFrame()

    series = series[
        (series["Type"] == data_type)
        & (series["Units"] == units)
        & (series["Frequency"] == "daily")
        & (series["Asset Class"] == "bonds")
        & (series["Category"] == category)
        & (series["Area"] == area)
        & (series["Grade"] == grade)
    ]

    if series.empty:
        console.print("The combination of parameters does not result in any data.")
        return pd.DataFrame()

    series_dictionary = {}

    for series_id, title in series[["FRED Series ID", "Title"]].values:
        series_dictionary[title] = get_series_data(
            series_id=series_id, start_date=start_date, end_date=end_date
        )

    df = pd.DataFrame.from_dict(series_dictionary)
    df.index = pd.to_datetime(df.index).date
    df.index.name = "Date"
    return df


def get_moody(
    data_type: str = "aaa",
    spread: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get data for Moody Corporate Bond Index

    Parameters
    ----------
    data_type: str
        The type of data you want to see, either "aaa" or "baa"
    spread: Optional[str]
        Whether you want to show the spread for treasury or fed_funds
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    series_id = MOODY_TO_OPTIONS["Type"][data_type][spread if spread else "index"]["id"]

    series = get_series_data(
        series_id=series_id, start_date=start_date, end_date=end_date
    )

    df = pd.DataFrame(series, columns=[f"{data_type}_{spread if spread else 'index'}"])
    df.index = pd.to_datetime(df.index).date
    df.index.name = "Date"
    return df


def get_cp(
    maturity: str = "30d",
    category: str = "financial",
    grade: str = "aa",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Obtain Commercial Paper data

    Parameters
    ----------
    maturity: str
        The maturity you want to see, either "overnight", "7d", "15d", "30d", "60d" or "90d"
    category: str
        The category you want to see, either "asset_backed", "financial" or "non_financial"
    grade: str
        The type of grade you want to see, either "a2_p2" or "aa"
    description: bool
        Whether you wish to obtain a description of the data.
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    if grade == "a2_p2" and category != "non_financial":
        category = "non_financial"
    series = pd.read_csv(commercial_paper_path)
    series = series[
        (series["Maturity"] == maturity)
        & (series["Category"] == category)
        & (series["Grade"] == grade)
    ]

    if series.empty:
        console.print("The combination of parameters does not result in any data.")
        return pd.DataFrame()

    series_dictionary = {}

    for series_id, title in series[["FRED Series ID", "Title"]].values:
        series_dictionary[title] = get_series_data(
            series_id=series_id, start_date=start_date, end_date=end_date
        )

    df = pd.DataFrame.from_dict(series_dictionary)
    df.index = pd.to_datetime(df.index).date
    df.index.name = "Date"
    return df


def get_spot(
    maturity: List = ["10y"],
    category: List = ["spot_rate"],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    The spot rate for any maturity is the yield on a bond that provides
    a single payment at that maturity. This is a zero coupon bond. Because each
    spot rate pertains to a single cashflow, it is the relevant interest rate
    concept for discounting a pension liability at the same maturity.

    Parameters
    ----------
    maturity: str
        The maturity you want to see (ranging from '1y' to '100y' in interval of 0.5, e.g. '50.5y')
    category: list
        The category you want to see ('par_yield' and/or 'spot_rate')
    description: bool
        Whether you wish to obtain a description of the data.
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    series = pd.read_csv(spot_rates_path)

    series = series[
        (series["Maturity"].isin(maturity)) & (series["Category"].isin(category))
    ]

    if "par_yield" in category and "par_yield" not in series["Category"].values:
        console.print(
            "No Par Yield data available for (some of) the selected maturities. "
            "Only 2y, 5y, 10y and 30y is available."
        )

    series_dictionary = {}

    for series_id, title in series[["FRED Series ID", "Title"]].values:
        series_dictionary[title] = get_series_data(
            series_id=series_id, start_date=start_date, end_date=end_date
        )

    df = pd.DataFrame.from_dict(series_dictionary)
    df.index = pd.to_datetime(df.index).date
    df.index.name = "Date"
    return df


def get_hqm(
    date: Optional[str] = None,
    par: bool = False,
) -> Tuple[pd.DataFrame, str]:
    """
    The HQM yield curve represents the high quality corporate bond market, i.e.,
    corporate bonds rated AAA, AA, or A.  The HQM curve contains two regression terms. These
    terms are adjustment factors that blend AAA, AA, and A bonds into a single HQM yield curve
    that is the market-weighted average (MWA) quality of high quality bonds.

    Parameters
    ----------
    date: str
        The date of the yield curve you wish to plot
    par: bool
        Whether you wish to plot the par yield curve as well
    """
    df = pd.DataFrame()
    data_types = ["spot", "par"] if par else ["spot"]

    for types in data_types:
        subset, date_of_yield = get_yield_curve(date, True, spot_or_par=types)
        subset.set_index("Maturity", inplace=True)
        subset.columns = [types]

        df = pd.concat([df, subset], axis=1)

    if par:
        # Drop NaNs because of length mismatch
        df = df.dropna()

    if df.empty:
        console.print(f"[red]Yield data not found at {date_of_yield}.[/red]\n")

    return df, date_of_yield


def get_tbffr(
    parameter: str = "3_month",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get data for Selected Treasury Bill Minus Federal Funds Rate.

    Parameters
    ----------
    parameter: str
        FRED ID of TBFFR data to plot, options: ["3_month", "6_month"]
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    series_id = TBFFR_PARAMETER_TO_FRED_ID[parameter]

    return pd.DataFrame(
        get_series_data(series_id, start_date, end_date), columns=[series_id]
    )


def get_icespread(
    category: str = "all",
    area: str = "us",
    grade: str = "non_sovereign",
    options: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get data for ICE BofA US Corporate Bond Spreads

    Parameters
    ----------
    category: str
        The type of category you want to see, either "all", "duration", "eur" or "usd".
    area: str
        The type of area you want to see, either "asia", "emea", "eu", "ex_g10", "latin_america" or "us"
    grade: str
        The type of grade you want to see, either "a", "aa", "aaa", "b", "bb", "bbb", "ccc", "crossover",
        "high_grade", "high_yield", "non_financial", "non_sovereign", "private_sector", "public_sector"
    """
    return get_icebofa(
        data_type="spread",
        category=category,
        area=area,
        grade=grade,
        options=options,
        start_date=start_date,
        end_date=end_date,
    )


def get_ffrmc(
    parameter: str = "10_year",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get data for Selected Treasury Constant Maturity Minus Federal Funds Rate

    Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
    Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
    yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

    Parameters
    ----------
    parameter: str
        FRED ID of FFRMC data to plot
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    series_id = FFRMC_PARAMETER_TO_FRED_ID[parameter]
    return pd.DataFrame(
        get_series_data(series_id, start_date, end_date), columns=[series_id]
    )


def get_tmc(
    parameter: str = "3_month",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get data for 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity.

    Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
    Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
    yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

    Parameters
    ----------
    parameter: str
        FRED ID of TMC data to plot, options: ["T10Y3M", "T10Y3M"]
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    series_id = TMC_PARAMETER_TO_FRED_ID[parameter]
    return pd.DataFrame(
        get_series_data(series_id, start_date, end_date), columns=[series_id]
    )

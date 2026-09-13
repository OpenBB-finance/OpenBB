"""Helper functions for Quantitative Analysis."""

from datetime import date
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from pandas import DataFrame, Series

FAMA_FRENCH_DATE_COLUMN = "Date"
FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN = "MKT-RF"
FAMA_FRENCH_SMALL_MINUS_BIG_RETURN_COLUMN = "SMB"
FAMA_FRENCH_HIGH_MINUS_LOW_RETURN_COLUMN = "HML"
FAMA_FRENCH_RISK_FREE_RETURN_COLUMN = "RF"
FAMA_FRENCH_MONTHLY_FACTORS_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
FAMA_FRENCH_MONTHLY_FACTORS_FILE = "F-F_Research_Data_Factors.csv"


def prepare_monthly_capm_data(
    data: "DataFrame", factors: "DataFrame", target: str
) -> "DataFrame":
    """Align monthly asset excess returns with Fama-French market excess returns.

    Returns
    -------
    DataFrame
        Monthly observations indexed by calendar month with columns:
        ``excess_return`` for the asset return minus the risk-free return, and
        ``excess_mkt`` for the Fama-French market excess return.
    """
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame, to_datetime, to_numeric

    asset = DataFrame(
        {
            "date": to_datetime(data["date"]),
            target: to_numeric(data[target], errors="raise"),
        }
    ).sort_values("date")
    asset = asset.set_index("date")
    # Use the final available price in each month to calculate monthly returns.
    asset_returns = (
        asset[target].groupby(asset.index.to_period("M")).last().pct_change().dropna()
    )

    monthly_factors = factors[
        [FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN, FAMA_FRENCH_RISK_FREE_RETURN_COLUMN]
    ].copy()
    monthly_factors.index = to_datetime(monthly_factors.index).to_period("M")

    result = DataFrame({"return": asset_returns}).join(monthly_factors, how="inner")
    result["excess_return"] = (
        result["return"] - result[FAMA_FRENCH_RISK_FREE_RETURN_COLUMN]
    )
    result["excess_mkt"] = result[FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN]
    result = result[["excess_return", "excess_mkt"]].dropna()

    if len(result) < 3:
        raise ValueError(
            "CAPM requires at least 3 aligned monthly return observations."
        )
    if result["excess_mkt"].nunique() < 2:
        raise ValueError("CAPM requires variation in market excess returns.")

    return result


def fit_capm(data: "DataFrame") -> tuple[float, float]:
    """Fit CAPM excess returns and return beta and R-squared."""
    # pylint: disable=import-outside-toplevel
    import statsmodels.api as sm

    dependent = data["excess_return"]
    market = sm.add_constant(data["excess_mkt"])
    model = sm.OLS(dependent, market).fit()

    return float(model.params["excess_mkt"]), float(model.rsquared)


# ruff: ignore=S310
def get_fama_raw(
    start_date: date,
    end_date: date,
    url: str = FAMA_FRENCH_MONTHLY_FACTORS_URL,
) -> "DataFrame":
    """Get base Fama French data to calculate risk.

    Parameters
    ----------
    start_date : date
        Start date for the requested factor data.
    end_date : date
        End date for the requested factor data.
    url : str
        URL of the monthly Fama-French factors ZIP archive. This can also be a
        ``file://`` URL for a local archive.

    Returns
    -------
    DataFrame
        A data with fama french model information
    """
    # pylint: disable=import-outside-toplevel
    from io import BytesIO
    from urllib.request import urlopen
    from zipfile import ZipFile

    from pandas import read_csv, to_datetime, to_numeric

    with urlopen(url) as response:  # nosec  # noqa: S310 SIM117
        # Download Zipfile and create pandas DataFrame
        with ZipFile(BytesIO(response.read())) as zipfile:
            with zipfile.open(FAMA_FRENCH_MONTHLY_FACTORS_FILE) as zip_open:
                df = read_csv(
                    zip_open,
                    header=0,
                    names=[
                        FAMA_FRENCH_DATE_COLUMN,
                        FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN,
                        FAMA_FRENCH_SMALL_MINUS_BIG_RETURN_COLUMN,
                        FAMA_FRENCH_HIGH_MINUS_LOW_RETURN_COLUMN,
                        FAMA_FRENCH_RISK_FREE_RETURN_COLUMN,
                    ],
                    skiprows=3,
                )

    df = df[df[FAMA_FRENCH_DATE_COLUMN].apply(lambda x: len(str(x).strip()) == 6)]
    df[FAMA_FRENCH_DATE_COLUMN] = df[FAMA_FRENCH_DATE_COLUMN].astype(str) + "01"
    df[FAMA_FRENCH_DATE_COLUMN] = to_datetime(
        df[FAMA_FRENCH_DATE_COLUMN], format="%Y%m%d"
    )
    df[FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN] = to_numeric(
        df[FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN], downcast="float"
    )
    df[FAMA_FRENCH_SMALL_MINUS_BIG_RETURN_COLUMN] = to_numeric(
        df[FAMA_FRENCH_SMALL_MINUS_BIG_RETURN_COLUMN], downcast="float"
    )
    df[FAMA_FRENCH_HIGH_MINUS_LOW_RETURN_COLUMN] = to_numeric(
        df[FAMA_FRENCH_HIGH_MINUS_LOW_RETURN_COLUMN], downcast="float"
    )
    df[FAMA_FRENCH_RISK_FREE_RETURN_COLUMN] = to_numeric(
        df[FAMA_FRENCH_RISK_FREE_RETURN_COLUMN], downcast="float"
    )
    df[FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN] = (
        df[FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN] / 100
    )
    df[FAMA_FRENCH_SMALL_MINUS_BIG_RETURN_COLUMN] = (
        df[FAMA_FRENCH_SMALL_MINUS_BIG_RETURN_COLUMN] / 100
    )
    df[FAMA_FRENCH_HIGH_MINUS_LOW_RETURN_COLUMN] = (
        df[FAMA_FRENCH_HIGH_MINUS_LOW_RETURN_COLUMN] / 100
    )
    df[FAMA_FRENCH_RISK_FREE_RETURN_COLUMN] = (
        df[FAMA_FRENCH_RISK_FREE_RETURN_COLUMN] / 100
    )
    df = df.set_index(FAMA_FRENCH_DATE_COLUMN)

    dt_start_date = to_datetime(start_date.strftime("%Y-%m-%d"), format="%Y-%m-%d")
    dt_end_date = to_datetime(end_date.strftime("%Y-%m-%d"), format="%Y-%m-%d")
    if dt_start_date > df.index.max():
        raise ValueError(
            f"Start date '{dt_start_date}' is after the last date available for Fama-French '{df.index[-1]}'"
        )

    df = df.loc[dt_start_date:dt_end_date]  # type: ignore

    return df


def validate_window(input_data: Union["Series", "DataFrame"], window: int) -> None:
    """Validate the window input.

    Parameters
    ----------
    input_data : Union[Series, DataFrame]
        The input data to be validated.
    window : int
        The window to be validated.

    Raises
    ------
    ValueError
        If the window is greater than the input data length.
    """
    if window > len(input_data):
        raise ValueError(
            f"Window '{window}' is greater than the input data length '{len(input_data)}'"
        )

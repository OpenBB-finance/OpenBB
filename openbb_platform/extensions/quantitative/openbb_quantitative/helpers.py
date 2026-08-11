"""Helper functions for Quantitative Analysis."""

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from pandas import DataFrame, Series


# ruff: ignore=S310
def get_fama_raw(start_date: str, end_date: str) -> "DataFrame":
    """Get base Fama French data to calculate risk.

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

    with urlopen(  # nosec  # noqa: S310 SIM117
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
    ) as url:
        # Download Zipfile and create pandas DataFrame
        with ZipFile(BytesIO(url.read())) as zipfile:
            with zipfile.open("F-F_Research_Data_Factors.csv") as zip_open:
                df = read_csv(
                    zip_open,
                    header=0,
                    names=["Date", "MKT-RF", "SMB", "HML", "RF"],
                    skiprows=3,
                )

    df = df[df["Date"].apply(lambda x: len(str(x).strip()) == 6)]
    df["Date"] = df["Date"].astype(str) + "01"
    df["Date"] = to_datetime(df["Date"], format="%Y%m%d")
    df["MKT-RF"] = to_numeric(df["MKT-RF"], downcast="float")
    df["SMB"] = to_numeric(df["SMB"], downcast="float")
    df["HML"] = to_numeric(df["HML"], downcast="float")
    df["RF"] = to_numeric(df["RF"], downcast="float")
    df["MKT-RF"] = df["MKT-RF"] / 100
    df["SMB"] = df["SMB"] / 100
    df["HML"] = df["HML"] / 100
    df["RF"] = df["RF"] / 100
    df = df.set_index("Date")

    dt_start_date = to_datetime(start_date, format="%Y-%m-%d")
    if dt_start_date > df.index.max():
        raise ValueError(
            f"Start date '{dt_start_date}' is after the last date available for Fama-French '{df.index[-1]}'"
        )

    df = df.loc[start_date:end_date]  # type: ignore

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


def deflated_sharpe_stats(
    input_data: "Series",
    trials: int,
    rfr: float = 0.0,
    trials_sr_std: Union[float, None] = None,
) -> dict:
    """Compute the deflated Sharpe ratio of a return series.

    The deflated Sharpe ratio (Bailey & Lopez de Prado, 2014) is the
    probability that the true Sharpe exceeds the expected maximum Sharpe of
    `trials` zero-skill strategies — i.e. whether a result selected as the
    best of `trials` attempts reflects skill rather than selection. Adjusts
    for sample length and return skewness/kurtosis.

    Parameters
    ----------
    input_data : Series
        Return series (per-period returns, not prices).
    trials : int
        Number of strategy variants tried before selecting this one.
    rfr : float, optional
        Per-period risk-free rate, by default 0.0.
    trials_sr_std : float, optional
        Standard deviation of the per-period Sharpe estimates across the
        trials. Defaults to the null 1/sqrt(n-1) when unknown.

    Returns
    -------
    dict
        sharpe (per-period), expected_max_sharpe, deflated_sharpe_ratio,
        observations, trials.

    Raises
    ------
    ValueError
        If `trials` < 1 or the series has fewer than 3 observations or zero
        variance.
    """
    # pylint: disable=import-outside-toplevel
    from numpy import asarray, e as np_e, finfo, sqrt
    from scipy.stats import norm

    if trials < 1:
        raise ValueError("trials must be >= 1")
    returns = asarray(input_data, dtype=float)
    n = len(returns)
    if n < 3:
        raise ValueError("need at least 3 observations")
    mu = returns.mean() - rfr
    sd = returns.std()  # population, consistent with the reference implementation
    # `sd == 0` is exact and a constant series does not reach it: its standard
    # deviation is floating-point residue rather than a true zero, so a flat 0.1%
    # series has sd ~1e-19 and divides out to a Sharpe of ~1e16 -- finite, and past
    # every isfinite guard after this one. Deflating that returned 1.0, i.e. certainty
    # of a real edge, for the one input carrying no information about one. Compare
    # against the resolution of a float at the scale of the data instead, so a
    # genuinely low-volatility series still gets a number.
    # The residue grows with the number of terms summed, so the floor is n eps rather
    # than eps: measured at most 1.96 eps x scale over constant series spanning values
    # 1e-7..1e3 and lengths 3..10000, while a real series with sigma=1e-12 sits more
    # than ten orders of magnitude above n eps x scale.
    if not sd > n * finfo(float).eps * abs(returns).max():
        raise ValueError("zero-variance returns")
    sr = mu / sd
    skew_ = (((returns - returns.mean()) / sd) ** 3).mean()
    kurt_ = (((returns - returns.mean()) / sd) ** 4).mean()  # non-excess, normal = 3

    if trials_sr_std is None:
        trials_sr_std = 1.0 / sqrt(n - 1)
    if trials == 1:
        bar = 0.0
    else:
        euler = 0.5772156649015329
        z1 = norm.ppf(1 - 1.0 / trials)
        z2 = norm.ppf(1 - 1.0 / (trials * np_e))
        bar = trials_sr_std * ((1 - euler) * z1 + euler * z2)

    denom = 1 - skew_ * sr + (kurt_ - 1) / 4 * sr**2
    if denom <= 0:
        raise ValueError("degenerate return moments")
    dsr = norm.cdf((sr - bar) * sqrt(n - 1) / sqrt(denom))

    return {
        "sharpe": float(sr),
        "expected_max_sharpe": float(bar),
        "deflated_sharpe_ratio": float(dsr),
        "observations": n,
        "trials": trials,
    }

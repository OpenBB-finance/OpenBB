"""Helper functions for Quantitative Analysis."""

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

import pandas as pd


# ruff: ignore=S310
def get_fama_raw(start_date: str, end_date: str) -> pd.DataFrame:
    """Get base Fama French data to calculate risk.

    Returns
    -------
    pd.DataFrame
        A data with fama french model information
    """
    with urlopen(  # nosec  # noqa: S310 SIM117
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
    ) as url:
        # Download Zipfile and create pandas DataFrame
        with ZipFile(BytesIO(url.read())) as zipfile:
            with zipfile.open("F-F_Research_Data_Factors.CSV") as zip_open:
                df = pd.read_csv(
                    zip_open,
                    header=0,
                    names=["Date", "MKT-RF", "SMB", "HML", "RF"],
                    skiprows=3,
                )

    df = df[df["Date"].apply(lambda x: len(str(x).strip()) == 6)]
    df["Date"] = df["Date"].astype(str) + "01"
    df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d")
    df["MKT-RF"] = pd.to_numeric(df["MKT-RF"], downcast="float")
    df["SMB"] = pd.to_numeric(df["SMB"], downcast="float")
    df["HML"] = pd.to_numeric(df["HML"], downcast="float")
    df["RF"] = pd.to_numeric(df["RF"], downcast="float")
    df["MKT-RF"] = df["MKT-RF"] / 100
    df["SMB"] = df["SMB"] / 100
    df["HML"] = df["HML"] / 100
    df["RF"] = df["RF"] / 100
    df = df.set_index("Date")

    dt_start_date = pd.to_datetime(start_date, format="%Y-%m-%d")
    if dt_start_date > df.index.max():
        raise ValueError(
            f"Start date '{dt_start_date}' is after the last date available for Fama-French '{df.index[-1]}'"
        )

    df = df.loc[start_date:end_date]  # type: ignore

    return df

"""Helper functions for the quantitative extension."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame, Series

_FAMA_FRENCH_FACTORS_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    "F-F_Research_Data_Factors_CSV.zip"
)


def get_fama_raw(start_date: str, end_date: str) -> "DataFrame":
    """Download the Fama-French research factors for a date range.

    Returns a DataFrame indexed by date with the excess market return ('mkt_rf'),
    size ('smb'), value ('hml'), and risk-free ('rf') factors as decimal fractions.
    """
    from io import BytesIO
    from urllib.request import urlopen
    from zipfile import ZipFile

    from pandas import read_csv, to_datetime, to_numeric

    with (
        urlopen(_FAMA_FRENCH_FACTORS_URL) as response,  # noqa: S310
        ZipFile(BytesIO(response.read())) as archive,
        archive.open("F-F_Research_Data_Factors.csv") as handle,
    ):
        df = read_csv(
            handle,
            header=0,
            names=["date", "mkt_rf", "smb", "hml", "rf"],
            skiprows=3,
        )

    df = df[df["date"].apply(lambda value: len(str(value).strip()) == 6)]
    df["date"] = to_datetime(df["date"].astype(str) + "01", format="%Y%m%d")
    for column in ("mkt_rf", "smb", "hml", "rf"):
        df[column] = to_numeric(df[column], downcast="float") / 100
    df = df.set_index("date")

    if to_datetime(start_date) > df.index.max():
        raise ValueError(
            f"Start date '{start_date}' is after the last available Fama-French"
            f" observation '{df.index.max().date()}'."
        )

    return df.loc[start_date:end_date]


def validate_window(input_data: "Series | DataFrame", window: int) -> None:
    """Raise a ValueError when the rolling window exceeds the data length."""
    if window > len(input_data):
        raise ValueError(
            f"Window '{window}' is larger than the data length '{len(input_data)}'."
        )

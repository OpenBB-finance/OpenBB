"""Geek of wall street model"""
__docformat__ = "numpy"

import io
import requests
import pandas as pd


def download_file_from_google_drive(file_id: str) -> bytes:
    """Custom function from rkornmeyer for pulling csv from google drive

    Parameters
    ----------
    file_id : str
        File id to pull from google drive

    Returns
    -------
    bytes
        Content from request response
    """

    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                return value

        return None

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={"id": file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {"id": file_id, "confirm": token}
        response = session.get(URL, params=params, stream=True)

    return response.content


def get_realtime_earnings() -> pd.DataFrame:
    """Pulls realtime earnings from geek of wallstreet

    Returns
    -------
    pd.DataFrame
        Dataframe containing realtime earnings
    """
    data = download_file_from_google_drive("1-TsAuzKs_vvg40r5RuRaG_wyb2Hzxbd5").decode(
        "utf-8"
    )
    return pd.read_csv(io.StringIO(data))

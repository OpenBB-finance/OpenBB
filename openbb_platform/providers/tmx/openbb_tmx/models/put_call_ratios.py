from io import BytesIO

import requests
from pandas import read_csv


def get_pcr(index: bool = False):
    """Gets historical equity and index put-call ratios from TMX."""

    url = (
        "https://www.m-x.ca/files/ratio-sxo.csv"
        if index is True
        else "https://www.m-x.ca/files/ratio-equity.csv"
    )
    r = requests.get(url, timeout=5)

    if r.status_code != 200:
        raise RuntimeError(r.status_code)
    data = read_csv(BytesIO(r.content), delimiter=";").iloc[:, :5]

    data.columns = [d.lower() for d in data.columns.tolist()]

    return data


# Monthly Options Volume and Open Interest Stats
# https://www.m-x.ca/f_stat_en/1907_stats_en.xlsx

""" SEC Model """
__docformat__ = "numpy"

import logging
from datetime import datetime, timedelta
from typing import Optional
from urllib.error import HTTPError

import pandas as pd
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def catching_diff_url_formats(ftd_urls: list) -> list:
    """Catches if URL for SEC data is one of the few URLS that are not in the
    standard format. Catches are for either specific date ranges that have a different
    format or singular URLs that have a different format.

    Parameters
    ----------
    ftd_urls : list
        list of urls of sec data

    Returns
    -------
    list
        list of ftd urls
    """
    feb_mar_apr_catch = ["202002", "202003", "202004"]
    for i, ftd_url in enumerate(ftd_urls):
        # URLs with dates prior to the first half of June 2017 have different formats
        if int(ftd_url[58:64]) < 201706 or "201706a" in ftd_url:
            ftd_urls[i] = ftd_url.replace(
                "fails-deliver-data",
                "frequently-requested-foia-document-fails-deliver-data",
            )
        # URLs between february, march, and april of 2020 have different formats
        elif any(x in ftd_urls[i] for x in feb_mar_apr_catch):
            ftd_urls[i] = ftd_url.replace(
                "data/fails-deliver-data", "node/add/data_distribution"
            )
        # First half of october 2019 has a different format
        elif (
            ftd_url
            == "https://www.sec.gov/files/data/fails-deliver-data/cnsfails201910a.zip"
        ):
            ftd_urls[
                i
            ] = "https://www.sec.gov/files/data/fails-deliver-data/cnsfails201910a_0.zip"

    return ftd_urls


@log_start_end(log=logger)
def get_fails_to_deliver(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 0,
) -> pd.DataFrame:
    """Display fails-to-deliver data for a given ticker. [Source: SEC]

    Parameters
    ----------
    symbol : str
        Stock ticker
    start_date : Optional[str]
        Start of data, in YYYY-MM-DD format
    end_date : Optional[str]
        End of data, in YYYY-MM-DD format
    limit : int
        Number of latest fails-to-deliver being printed

    Returns
    -------
    pd.DataFrame
        Fail to deliver data
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    ftds_data = pd.DataFrame()
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Filter by number of last FTD
    if limit > 0:
        url_ftds = "https://www.sec.gov/data/foiadocsfailsdatahtm"
        text_soup_ftds = BeautifulSoup(
            request(url_ftds, headers={"User-Agent": get_user_agent()}).text,
            "lxml",
        )

        table = text_soup_ftds.find("table", {"class": "list"})
        links = table.findAll("a")
        link_idx = 0

        while len(ftds_data) < limit:
            if link_idx > len(links):
                break
            link = links[link_idx]
            url = "https://www.sec.gov" + link["href"]
            all_ftds = pd.read_csv(
                url,
                compression="zip",
                sep="|",
                engine="python",
                skipfooter=2,
                usecols=[0, 2, 3, 5],
                dtype={"QUANTITY (FAILS)": "int"},
                encoding="iso8859",
            )
            tmp_ftds = all_ftds[all_ftds["SYMBOL"] == symbol]
            del tmp_ftds["PRICE"]
            del tmp_ftds["SYMBOL"]
            # merge the data from this archive
            ftds_data = pd.concat([ftds_data, tmp_ftds], ignore_index=True)
            link_idx += 1

        # clip away extra rows
        ftds_data = ftds_data.sort_values("SETTLEMENT DATE")[-limit:]

        ftds_data["SETTLEMENT DATE"] = ftds_data["SETTLEMENT DATE"].apply(
            lambda x: datetime.strptime(str(x), "%Y%m%d")
        )

    # Filter by start and end dates for FTD
    else:
        base_url = "https://www.sec.gov/files/data/fails-deliver-data/cnsfails"
        ftd_dates = []

        for y in range(start.year, end.year + 1):
            if y < end.year:
                for a_month in range(start.month, 13):
                    formatted_month = f"{a_month:02d}"

                    if a_month == start.month and y == start.year:
                        if start.day < 16:
                            ftd_dates.append(str(y) + formatted_month + "a")
                        ftd_dates.append(str(y) + formatted_month + "b")
                    else:
                        ftd_dates.append(str(y) + formatted_month + "a")
                        ftd_dates.append(str(y) + formatted_month + "b")

            else:
                for a_month in range(1, end.month):
                    formatted_month = f"{a_month:02d}"

                    if a_month == end.month - 1:
                        ftd_dates.append(str(y) + formatted_month + "a")
                        if end.day > 15:
                            ftd_dates.append(str(y) + formatted_month + "b")
                    else:
                        ftd_dates.append(str(y) + formatted_month + "a")
                        ftd_dates.append(str(y) + formatted_month + "b")

        ftd_urls = [base_url + ftd_date + ".zip" for ftd_date in ftd_dates]

        # Calling function that catches a handful of urls that are slightly
        # different than the standard format
        ftd_urls = catching_diff_url_formats(ftd_urls)

        for ftd_link in ftd_urls:
            try:
                all_ftds = pd.read_csv(
                    ftd_link,
                    compression="zip",
                    sep="|",
                    engine="python",
                    skipfooter=2,
                    usecols=[0, 2, 3, 5],
                    dtype={"QUANTITY (FAILS)": "Int64"},
                    encoding="iso8859",
                )
            except HTTPError:
                continue

            tmp_ftds = all_ftds[all_ftds["SYMBOL"] == symbol]
            del tmp_ftds["PRICE"]
            del tmp_ftds["SYMBOL"]
            # merge the data from this archive
            ftds_data = pd.concat([ftds_data, tmp_ftds], ignore_index=True)

        ftds_data["SETTLEMENT DATE"] = ftds_data["SETTLEMENT DATE"].apply(
            lambda x: datetime.strptime(str(x), "%Y%m%d")
        )

        ftds_data = ftds_data[ftds_data["SETTLEMENT DATE"] > start]
        ftds_data = ftds_data[ftds_data["SETTLEMENT DATE"] < end]

    return ftds_data

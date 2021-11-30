""" SEC Model """
__docformat__ = "numpy"

from datetime import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
from gamestonk_terminal.helper_funcs import get_user_agent


def get_fails_to_deliver(
    ticker: str,
    start: datetime,
    end: datetime,
    num: int,
):
    """Display fails-to-deliver data for a given ticker. [Source: SEC]

    Parameters
    ----------
    ticker : str
        Stock ticker
    start : datetime
        Start of data
    end : datetime
        End of data
    num : int
        Number of latest fails-to-deliver being printed
    """
    ftds_data = pd.DataFrame()

    # Filter by number of last FTD
    if num > 0:
        url_ftds = "https://www.sec.gov/data/foiadocsfailsdatahtm"
        text_soup_ftds = BeautifulSoup(
            requests.get(url_ftds, headers={"User-Agent": get_user_agent()}).text,
            "lxml",
        )

        table = text_soup_ftds.find("table", {"class": "list"})
        links = table.findAll("a")
        link_idx = 0

        while len(ftds_data) < num:
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
            tmp_ftds = all_ftds[all_ftds["SYMBOL"] == ticker]
            del tmp_ftds["PRICE"]
            del tmp_ftds["SYMBOL"]
            # merge the data from this archive
            ftds_data = pd.concat([ftds_data, tmp_ftds], ignore_index=True)
            link_idx += 1

        # clip away extra rows
        ftds_data = ftds_data.sort_values("SETTLEMENT DATE")[-num:]

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

        for ftd_link in ftd_urls:
            all_ftds = pd.read_csv(
                ftd_link,
                compression="zip",
                sep="|",
                engine="python",
                skipfooter=2,
                usecols=[0, 2, 3, 5],
                dtype={"QUANTITY (FAILS)": "int"},
                encoding="iso8859",
            )
            tmp_ftds = all_ftds[all_ftds["SYMBOL"] == ticker]
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

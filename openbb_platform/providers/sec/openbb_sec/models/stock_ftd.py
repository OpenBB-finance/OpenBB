""" SEC Stock FTD Model """

import concurrent.futures
from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from io import StringIO
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests_cache
from bs4 import BeautifulSoup
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_ftd import StockFtdData, StockFtdQueryParams
from openbb_sec.utils.helpers import SEC_HEADERS, catching_diff_url_formats
from pydantic import Field

now = datetime.now().date().day
days = 7
if now in (15, 30, 31, 14, 29):
    days = 0

sec_session_ftd = requests_cache.CachedSession(
    "OpenBB_SEC_FTD", expire_after=timedelta(days=days), use_cache_dir=True
)


class SecStockFtdQueryParams(StockFtdQueryParams):
    """SEC Stock FTD Query Params."""

    start_date: Optional[Union[dateType, str]] = Field(
        description="The start date of the data.", default=None
    )
    end_date: Optional[Union[dateType, str]] = Field(
        description="The end date of the data.", default=None
    )
    limit: Optional[int] = Field(description="limit the number of records.", default=0)


class SecStockFtdData(StockFtdData):
    """SEC FTD Data."""


class SecStockFtdFetcher(
    Fetcher[
        SecStockFtdQueryParams,
        List[SecStockFtdData],
    ]
):
    """SEC FTD Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecStockFtdQueryParams:
        """Transform query params."""

        if "start_date" not in params or params["start_date"] is None:
            params["start_date"] = (datetime.now() - timedelta(days=90)).strftime(
                "%Y-%m-%d"
            )

        if "end_date" not in params or params["end_date"] is None:
            params["end_date"] = datetime.now().strftime("%Y-%m-%d")

        return SecStockFtdQueryParams(**params)

    @staticmethod
    def extract_data(
        query: SecStockFtdQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extracts the data from the SEC website."""

        limit = query.limit if query.limit is not None else 0
        start_date = pd.to_datetime(query.start_date)  # type: ignore
        end_date = pd.to_datetime(query.end_date)  # type: ignore
        symbol = query.symbol.upper()
        response = []

        ftds_data = pd.DataFrame()
        start = start_date  # type: ignore
        end = end_date  # type: ignore

        # Filter by number of last FTD
        if limit > 0:  # type: ignore
            url_ftds = "https://www.sec.gov/data/foiadocsfailsdatahtm"
            text_soup_ftds = BeautifulSoup(
                sec_session_ftd.get(url_ftds, headers={SEC_HEADERS}, timeout=5).text,
                "lxml",
            )

            table = text_soup_ftds.find("table", {"class": "list"})
            links = table.findAll("a")  # type: ignore
            link_idx = 0

            while len(ftds_data) < limit:
                all_ftds = pd.DataFrame()
                if link_idx > len(links):
                    break
                link = links[link_idx]
                url = "https://www.sec.gov" + link["href"]
                r = sec_session_ftd.get(url, headers={SEC_HEADERS}, timeout=5)
                all_ftds = pd.read_csv(
                    StringIO(r.text),
                    compression="zip",
                    sep="|",
                    engine="python",
                    skipfooter=2,
                    usecols=[0, 1, 2, 3, 4, 5],
                    dtype={"QUANTITY (FAILS)": "int"},
                    encoding="iso8859",
                )
                tmp_ftds = all_ftds[all_ftds["SYMBOL"] == symbol]
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

            def get_one(ftd_url):
                all_ftds = pd.DataFrame()
                all_ftds = pd.read_csv(
                    ftd_url,
                    compression="zip",
                    sep="|",
                    engine="python",
                    skipfooter=2,
                    usecols=[0, 2, 3, 5],
                    dtype={"QUANTITY (FAILS)": "Int64"},
                    encoding="iso8859",
                )

                tmp_ftds = all_ftds[all_ftds["SYMBOL"] == symbol]
                del tmp_ftds["SYMBOL"]
                # merge the data from this archive
                response.extend(tmp_ftds.to_dict("records"))

            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(get_one, ftd_urls)

            ftds_data = pd.DataFrame.from_records(response)

            ftds_data["SETTLEMENT DATE"] = ftds_data["SETTLEMENT DATE"].apply(
                lambda x: datetime.strptime(str(x), "%Y%m%d")
            )

            ftds_data = ftds_data[ftds_data["SETTLEMENT DATE"] >= pd.to_datetime(start)]
            ftds_data = ftds_data[ftds_data["SETTLEMENT DATE"] <= pd.to_datetime(end)]
            ftds_data = ftds_data.sort_values("SETTLEMENT DATE", ascending=True).rename(
                columns={
                    "QUANTITY (FAILS)": "quantity",
                    "SETTLEMENT DATE": "settlement_date",
                    "PRICE": "price",
                }
            )

        return ftds_data.to_dict("records")

    @staticmethod
    def transform_data(data: List[Dict], **kwargs: Any) -> List[SecStockFtdData]:
        return [SecStockFtdData.model_validate(d) for d in data]

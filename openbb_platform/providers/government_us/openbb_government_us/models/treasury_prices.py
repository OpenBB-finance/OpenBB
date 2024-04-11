"""US Government Treasury Prices."""

# pylint: disable=unused-argument
import asyncio
from datetime import datetime, timedelta
from io import StringIO
from typing import Any, Dict, List, Literal, Optional

import requests
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.treasury_prices import (
    TreasuryPricesData,
    TreasuryPricesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_government_us.utils.helpers import get_random_agent
from pandas import Index, read_csv, to_datetime
from pydantic import Field


class GovernmentUSTreasuryPricesQueryParams(TreasuryPricesQueryParams):
    """US Government Treasury Prices Query."""

    cusip: Optional[str] = Field(description="Filter by CUSIP.", default=None)
    security_type: Literal[None, "bill", "note", "bond", "tips", "frn"] = Field(
        description="Filter by security type.",
        default=None,
    )


class GovernmentUSTreasuryPricesData(TreasuryPricesData):
    """US Government Treasury Prices Data."""


class GovernmentUSTreasuryPricesFetcher(
    Fetcher[
        GovernmentUSTreasuryPricesQueryParams,
        List[GovernmentUSTreasuryPricesData],
    ]
):
    """US Government Treasury Prices Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> GovernmentUSTreasuryPricesQueryParams:
        """Transform query params."""
        if params.get("date") is None:
            _date = datetime.now().date()
        else:
            _date = (
                datetime.strptime(params["date"], "%Y-%m-%d").date()
                if isinstance(params["date"], str)
                else params["date"]
            )
        if _date.weekday() > 4:
            _date = _date - timedelta(days=_date.weekday() - 4)
        params["date"] = _date

        return GovernmentUSTreasuryPricesQueryParams(**params)

    # pylint: disable=unused-argument
    @staticmethod
    async def aextract_data(
        query: GovernmentUSTreasuryPricesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """Extract the raw data from US Treasury website."""
        url = "https://treasurydirect.gov/GA-FI/FedInvest/securityPriceDetail"

        HEADERS = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://treasurydirect.gov/",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://treasurydirect.gov",
            "User-Agent": get_random_agent(),
        }

        payload = (
            f"priceDateDay={query.date.day}"  # type: ignore
            f"&priceDateMonth={query.date.month}"  # type: ignore
            f"&priceDateYear={query.date.year}"  # type: ignore
            "&fileType=csv"
            "&csv=CSV+FORMAT"
        )

        def fetch_data() -> str:
            r = requests.post(url=url, headers=HEADERS, data=payload, timeout=5)

            if r.status_code != 200:
                raise RuntimeError("Error with the request: " + str(r.status_code))

            if r.encoding != "ISO-8859-1":
                raise RuntimeError(
                    f"Expected ISO-8859-1 encoding but got: {r.encoding}"
                )
            return r.content.decode("utf-8")

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, fetch_data)

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: GovernmentUSTreasuryPricesQueryParams,
        data: str,
        **kwargs: Any,
    ) -> List[GovernmentUSTreasuryPricesData]:
        """Transform the data."""
        try:
            if not data:
                raise EmptyDataError("Data not found")
            results = read_csv(StringIO(data), header=0)
            results.columns = Index(
                [
                    "cusip",
                    "security_type",
                    "rate",
                    "maturity_date",
                    "call_date",
                    "bid",
                    "offer",
                    "eod_price",
                ]
            )
            results["date"] = query.date.strftime("%Y-%m-%d")  # type: ignore
            for col in ["maturity_date", "call_date"]:
                results[col] = (
                    (
                        to_datetime(results[col], format="%m/%d/%Y").dt.strftime(
                            "%Y-%m-%d"
                        )
                    )
                    .fillna("-")
                    .replace("-", None)
                )

        except Exception as e:
            raise RuntimeError(e) from e

        if query.security_type is not None:
            results = results[
                results["security_type"].str.contains(query.security_type, case=False)
            ]
        if query.cusip is not None:
            results = results[results["cusip"] == query.cusip]
        return [
            GovernmentUSTreasuryPricesData.model_validate(d)
            for d in results.to_dict("records")
        ]

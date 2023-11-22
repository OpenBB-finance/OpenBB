"""US Government Treasury Prices"""
from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.treasury_prices import (
    USTreasuryPricesData,
    USTreasuryPricesQueryParams,
)
from openbb_provider.utils.helpers import make_request
from pandas import DataFrame, read_csv, to_datetime
from pydantic import Field


class GovernmentUSTreasuryPricesQueryParams(USTreasuryPricesQueryParams):
    """US Government Treasury Prices Query."""

    cusip: Optional[str] = Field(description="Filter by CUSIP.", default=None)
    security_type: Literal[None, "bill", "note", "bond", "tips", "frn"] = Field(
        description="Filter by security type.",
        default=None,
    )


class GovernmentUSTreasuryPricesData(USTreasuryPricesData):
    """US Government Treasury Prices Data."""


class GovernmentUSTreasuryPricesFetcher(
    Fetcher[
        GovernmentUSTreasuryPricesQueryParams,
        List[GovernmentUSTreasuryPricesData],
    ]
):
    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> GovernmentUSTreasuryPricesQueryParams:
        """Transform query params."""

        if "date" not in params or params["date"] is None:
            _date = datetime.now().date()
        if "date" in params and params["date"] is not None:
            _date = (
                datetime.strptime(params["date"], "%Y-%m-%d").date()
                if isinstance(params["date"], str)
                else params["date"]
            )
        if _date.weekday() > 4:
            _date = (
                _date - timedelta(days=_date.weekday() - 4)
                if _date.weekday() > 4
                else _date
            )
        params["date"] = _date

        return GovernmentUSTreasuryPricesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: GovernmentUSTreasuryPricesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from US Treasury website."""

        data: List[Dict] = [{}]

        url = "https://treasurydirect.gov/GA-FI/FedInvest/securityPriceDetail"

        HEADERS = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://treasurydirect.gov/",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://treasurydirect.gov",
        }
        payload = (
            f"priceDateDay={query.date.day}&priceDateMonth={query.date.month}"  # type: ignore
            f"&priceDateYear={query.date.year}&fileType=csv&csv=CSV+FORMAT"
        )

        r = make_request(url=url, headers=HEADERS, method="POST", data=payload)

        if r.status_code != 200:
            raise RuntimeError("Error with the request: " + str(r.status_code))

        if r.encoding == "ISO-8859-1":
            try:
                results = read_csv(BytesIO(r.content), header=0)
                columns = [
                    "cusip",
                    "security_type",
                    "rate",
                    "maturity_date",
                    "call_date",
                    "bid",
                    "offer",
                    "eod_price",
                ]
                results.columns = columns
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

                data = results.to_dict(orient="records")
            except Exception as e:
                raise RuntimeError("Parsing Error: " + str(e))

        return data

    @staticmethod
    def transform_data(
        query: GovernmentUSTreasuryPricesQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[GovernmentUSTreasuryPricesData]:
        """Transform the data."""
        df = DataFrame.from_records(data)
        if query.security_type is not None:
            df = df[df["security_type"].str.contains(query.security_type, case=False)]
        if query.cusip is not None:
            df = df[df["cusip"] == query.cusip]
        return [
            GovernmentUSTreasuryPricesData.model_validate(d)
            for d in df.to_dict("records")
        ]

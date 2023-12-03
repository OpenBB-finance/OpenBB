"""CBOE European Indices Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta
from openbb_cboe.utils.helpers import Europe
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.european_indices import (
    EuropeanIndicesData,
    EuropeanIndicesQueryParams,
)
from openbb_core.provider.utils.helpers import make_request
from pydantic import Field, field_validator


class CboeEuropeanIndicesQueryParams(EuropeanIndicesQueryParams):
    """CBOE European Indices Query.

    Source: https://www.cboe.com/europe/indices/
    """

    interval: Literal["1d", "1m"] = Field(description="Data granularity.", default="1d")


class CboeEuropeanIndicesData(EuropeanIndicesData):
    """CBOE European Indices Data."""

    open: Optional[float] = Field(
        default=None,
        description="Opening price for the interval. Only valid when interval is 1m.",
    )
    high: Optional[float] = Field(
        default=None,
        description="High price for the interval. Only valid when interval is 1m.",
    )
    low: Optional[float] = Field(
        default=None,
        description="Low price for the interval. Only valid when interval is 1m.",
    )
    utc_datetime: Optional[datetime] = Field(
        default=None, description="UTC datetime. Only valid when interval is 1m."
    )

    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        try:
            return datetime.strptime(v, "%Y-%m-%d")
        except Exception:
            return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")


class CboeEuropeanIndicesFetcher(
    Fetcher[
        CboeEuropeanIndicesQueryParams,
        List[CboeEuropeanIndicesData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeEuropeanIndicesQueryParams:
        """Transform the query."""
        now = datetime.now().date()
        transformed_params = params
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return CboeEuropeanIndicesQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: CboeEuropeanIndicesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the CBOE endpoint."""
        data = pd.DataFrame()
        query.symbol = query.symbol.upper()
        SYMBOLS = pd.DataFrame(Europe.list_indices())["symbol"].to_list()

        if query.symbol not in SYMBOLS:
            raise RuntimeError(
                f"The symbol, {query.symbol},"
                "was not found in the CBOE European Indices directory. "
                "Use `available_indices(europe=True)` to see the full list of indices."
            )
        if query.interval == "1d":
            url = f"https://cdn.cboe.com/api/global/european_indices/index_history/{query.symbol}.json"

            r = make_request(url)
            if r.status_code != 200:
                raise RuntimeError(r.status_code)

            r_json = r.json()

            data = pd.DataFrame.from_records(r_json["data"]).set_index("date")

            data.index = pd.to_datetime(data.index, format="%Y-%m-%d")

            if query.start_date is not None:
                query.end_date = (
                    query.end_date if query.end_date else datetime.now().date()
                )

                data = data[
                    (data.index >= pd.to_datetime(query.start_date, format="%Y-%m-%d"))
                    & (data.index <= pd.to_datetime(query.end_date, format="%Y-%m-%d"))
                ]
            data.index = data.index.astype(str)
            data = data.reset_index()

        if query.interval == "1m":
            url = f"https://cdn.cboe.com/api/global/european_indices/intraday_chart_data/{query.symbol}.json"

            r = make_request(url)
            if r.status_code != 200:
                raise RuntimeError(r.status_code)

            r_json = r.json()["data"]

            data = pd.DataFrame.from_records(pd.DataFrame(r_json)["price"])
            data["date"] = pd.DataFrame(r_json)["datetime"]
            data["utc_datetime"] = pd.to_datetime(pd.DataFrame(r_json)["utc_datetime"])

            data = data[["utc_datetime", "date", "open", "high", "low", "close"]].round(
                2
            )

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: CboeEuropeanIndicesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[CboeEuropeanIndicesData]:
        """Transform the data to the standard format."""
        return [CboeEuropeanIndicesData.model_validate(d) for d in data]

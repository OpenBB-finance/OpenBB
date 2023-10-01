"""TMX Company Filings Model"""

import json
from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests
from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.abstract.query_params import QueryParams
from openbb_tmx.utils.gql import GQL
from openbb_tmx.utils.helpers import get_random_agent
from pydantic import Field, NonNegativeInt, validator


class TmxCompanyFilingsQueryParams(QueryParams):
    """TMX Company Filings Query Parameters."""

    symbol: str = Field(description="The ticker symbol to fetch.")
    start_date: Optional[Union[str, dateType]] = Field(
        description="The start date to fetch.",
        default=(datetime.today() - timedelta(weeks=52)).strftime("%Y-%m-%d"),
    )
    end_date: Optional[Union[str, dateType]] = Field(
        description="The end date to fetch.",
        default=datetime.today().strftime("%Y-%m-%d"),
    )
    limit: Optional[NonNegativeInt] = Field(
        description="Limit the number of results to fetch.", default=100
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: str):
        """Convert symbol to uppercase."""
        v = v.upper()
        if ".TO" in v or ".TSX" in v:
            v = v.replace(".TO", "").replace(".TSX", "")
        return v


class TmxCompanyFilingsData(Data):
    """TMX Sedar Filings Data."""

    date: dateType = Field(description="The date of the filing.", alias="filingDate")
    form: str = Field(description="The name of the filing type.", alias="name")
    description: str = Field(description="The description of the filing.")
    url: str = Field(description="The url to the PDF filing.", alias="urlToPdf")
    size: str = Field(description="The file size of the PDF document.")


class TmxCompanyFilingsFetcher(
    Fetcher[TmxCompanyFilingsQueryParams, List[TmxCompanyFilingsData]]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxCompanyFilingsQueryParams:
        """Transform the query."""
        return TmxCompanyFilingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxCompanyFilingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        results = []

        payload = GQL.get_company_filings_payload
        payload["variables"]["symbol"] = query.symbol.upper()
        payload["variables"]["fromDate"] = query.start_date
        payload["variables"]["toDate"] = query.end_date
        payload["variables"]["limit"] = query.limit
        url = "https://app-money.tmx.com/graphql"
        r = requests.post(
            url,
            data=json.dumps(payload),
            headers={
                "authority": "app-money.tmx.com",
                "referer": f"https://money.tmx.com/en/quote/{query.symbol.upper()}",
                "locale": "en",
                "Content-Type": "application/json",
                "User-Agent": get_random_agent(),
                "Accept": "*/*",
            },
            timeout=10,
        )
        try:
            if r.status_code == 403:
                raise RuntimeError(f"HTTP error - > {r.text}")
            else:
                r_data = r.json()
                if len(r_data["data"]["filings"]) == 0:
                    return results
                data = r_data["data"]["filings"]
                results = pd.DataFrame.from_records(data).drop(columns=["__typename"])

                return results.to_dict("records")

        except KeyError as _e:
            raise RuntimeError(_e, query.symbol.upper())

    @staticmethod
    def transform_data(data: List[Dict]) -> List[TmxCompanyFilingsData]:
        """Return the transformed data."""
        return [TmxCompanyFilingsData(**d) for d in data]

"""TMX Company Filings Model"""

import json
from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any, Dict, List, Optional, Union

import requests
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.company_filings import (
    CompanyFilingsData,
    CompanyFilingsQueryParams,
)
from openbb_tmx.utils.gql import GQL
from openbb_tmx.utils.helpers import get_random_agent
from pydantic import Field


class TmxCompanyFilingsQueryParams(CompanyFilingsQueryParams):
    """TMX Company Filings Query Parameters."""

    start_date: Optional[Union[str, dateType]] = Field(
        description="The start date to fetch.",
        default=(datetime.today() - timedelta(weeks=16)).strftime("%Y-%m-%d"),
    )
    end_date: Optional[Union[str, dateType]] = Field(
        description="The end date to fetch.",
        default=datetime.today().strftime("%Y-%m-%d"),
    )


class TmxCompanyFilingsData(CompanyFilingsData):
    """TMX Sedar Filings Data."""

    __alias_dict__ = {
        "date": "filingDate",
        "type": "name",
        "link": "urlToPdf",
    }

    description: str = Field(description="The description of the filing.")
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

        results: List[Dict] = []

        symbol = (
            query.symbol.upper()
            .replace("-", ".")
            .replace(".TO", "")
            .replace(".TSX", "")
        )

        payload = GQL.get_company_filings_payload
        payload["variables"]["symbol"] = symbol
        payload["variables"]["fromDate"] = query.start_date
        payload["variables"]["toDate"] = query.end_date
        payload["variables"]["limit"] = query.limit
        url = "https://app-money.tmx.com/graphql"
        try:
            r = requests.post(
                url,
                data=json.dumps(payload),
                headers={
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json",
                    "Host": "app-money.tmx.com",
                    "Origin": "https://money.tmx.com",
                    "Referer": "https://money.tmx.com/",
                    "locale": "en",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-site",
                    "TE": "trailers",
                    "User-Agent": get_random_agent(),
                },
                timeout=20,
            )
        except requests.exceptions.Timeout as _e:
            raise RuntimeError(
                f"Timeout error - > {_e} - This can be due to a rate limit, or the request being too large. "
                "Please try narrowing the search and try again."
            )
        try:
            if r.status_code == 403:
                raise RuntimeError(f"HTTP error - > {r.text}")
            else:
                try:
                    r_data = r.json()
                except json.decoder.JSONDecodeError as _e:
                    raise RuntimeError(f"JSON decode error - > {_e}")
                if len(r_data["data"]["filings"]) == 0:
                    return results
                results = r_data["data"]["filings"]

                return results

        except KeyError as _e:
            raise RuntimeError(_e, query.symbol.upper())

    @staticmethod
    def transform_data(data: List[Dict]) -> List[TmxCompanyFilingsData]:
        """Return the transformed data."""
        return [TmxCompanyFilingsData(**d) for d in data]

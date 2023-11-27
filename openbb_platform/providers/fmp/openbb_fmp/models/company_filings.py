"""FMP Company Filings Model."""

import math
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_filings import (
    CompanyFilingsData,
    CompanyFilingsQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_fmp.utils.helpers import get_data_many


class FMPCompanyFilingsQueryParams(CompanyFilingsQueryParams):
    """FMP Copmany Filings Query.

    Source: https://site.financialmodelingprep.com/developer/docs/sec-filings-api/
    """

    __alias_dict__ = {"form_type": "type"}


class FMPCompanyFilingsData(CompanyFilingsData):
    """FMP Company Filings Data."""

    __alias_dict__ = {
        "filing_date": "fillingDate",
        "accepted_date": "acceptedDate",
        "report_type": "type",
        "filing_url": "link",
        "report_url": "finalLink",
    }


class FMPCompanyFilingsFetcher(
    Fetcher[
        FMPCompanyFilingsQueryParams,
        List[FMPCompanyFilingsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCompanyFilingsQueryParams:
        """Transform the query params."""
        return FMPCompanyFilingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPCompanyFilingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        data: List[Dict] = []

        base_url = "https://financialmodelingprep.com/api/v3/sec_filings"
        query_str = get_querystring(query.model_dump(by_alias=True), ["symbol"])

        # FMP only allows 1000 results per page
        pages = math.ceil(query.limit / 1000)
        for page in range(pages):
            query_str += f"&page={page}"
            url = f"{base_url}/{query.symbol}?{query_str}&apikey={api_key}"
            response = get_data_many(url, **kwargs)
            data.extend(response)

        return data[: query.limit]

    @staticmethod
    def transform_data(
        query: FMPCompanyFilingsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCompanyFilingsData]:
        """Return the transformed data."""
        return [FMPCompanyFilingsData.model_validate(d) for d in data]

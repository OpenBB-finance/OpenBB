"""Intrinio Filings Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_intrinio.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.filings import (
    FilingsData,
    FilingsQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field


class IntrinioFilingsQueryParams(FilingsQueryParams):
    """Intrinio Filings Query."""

    __alias_dict__ = {
        "form_type": "report_type",
        "limit": "page_size",
    }

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    thea_enabled: Optional[bool] = Field(
        default=True,
        description="Return filings that have been read by Intrinio's Thea NLP.",
    )


class IntrinioFilingsData(FilingsData):
    """Intrinio Filings Data."""

    __alias_dict__ = {
        "url": "filing_url",
        "form_type": "report_type",
    }

    id: str = Field(description="Intrinio ID of the filing.")
    filing_date: dateType = Field(
        description="Date for the SEC filing.",
    )
    period_end_date: Optional[dateType] = Field(
        default=None,
        description="Ending date of the fiscal period for the filing.",
    )
    sec_unique_id: str = Field(
        description="SEC unique ID of the filing.",
    )
    report_url: str = Field(
        description="URL to the actual report on the SEC site.",
    )
    instance_url: Optional[str] = Field(
        default=None,
        description="URL for the XBRL filing for the report.",
    )


class IntrinioFilingsFetcher(
    Fetcher[
        IntrinioFilingsQueryParams,
        List[IntrinioFilingsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioFilingsQueryParams:
        """Transform the query."""
        transformed_params = params

        now = datetime.now().date()
        if "start_date" not in transformed_params:
            transformed_params["start_date"] = now
        if "end_date" not in transformed_params:
            transformed_params["end_date"] = now - relativedelta(years=1)

        return IntrinioFilingsQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: IntrinioFilingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com/companies"
        query_str = get_querystring(query.model_dump(by_alias=True), ["symbol"])
        url = f"{base_url}/{query.symbol}/filings?{query_str}&api_key={api_key}"

        return get_data_many(url, "filings", **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioFilingsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioFilingsData]:
        """Return the transformed data."""
        return [IntrinioFilingsData.model_validate(d) for d in data]

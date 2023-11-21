"""FMP Filings Model."""

import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.filings import (
    FilingsData,
    FilingsQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_fmp.utils.helpers import get_data_many
from pydantic import Field, field_validator


class FMPFilingsQueryParams(FilingsQueryParams):
    """FMP Filings Query."""

    __alias_dict__ = {
        "form_type": "type",
        "is_done": "isDone",
        "start_date": "from",
        "end_date": "to",
    }

    is_done: Optional[Literal["true", "false"]] = Field(
        default=None,
        description="Flag for whether or not the filing is done.",
    )


class FMPFilingsData(FilingsData):
    """FMP Filings Data."""

    __alias_dict__ = {
        "timestamp": "date",
        "symbol": "ticker",
        "url": "link",
    }

    is_done: Optional[Literal["True", "False"]] = Field(
        default=None, description="Whether or not the filing is done."
    )

    @field_validator("timestamp", mode="before")
    def validate_timestamp(cls, v: Any) -> Any:  # pylint: disable=no-self-argument
        """Validate the timestamp."""
        return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class FMPFilingsFetcher(
    Fetcher[
        FMPFilingsQueryParams,
        List[FMPFilingsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPFilingsQueryParams:
        """Transform the query."""
        transformed_params = params
        if "start_date" not in transformed_params:
            transformed_params["start_date"] = datetime.datetime.now().strftime(
                "%Y-%m-%d"
            )
        if "end_date" not in transformed_params:
            transformed_params["end_date"] = datetime.datetime.now().strftime(
                "%Y-%m-%d"
            )
        return FMPFilingsQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: FMPFilingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        response: List[Dict] = [{}]
        exclude = []
        if query.form_type is None:
            exclude.append("formType")
        if not query.is_done:
            exclude.append("isDone")
        base_url = "https://financialmodelingprep.com/api/v4/rss_feed?"
        query_string = get_querystring(query.model_dump(), exclude)
        url = f"{base_url}{query_string}&apikey={api_key}"
        data: List[Dict] = get_data_many(url, **kwargs)

        if len(data) > 0:
            response = data

        return response

    @staticmethod
    def transform_data(
        query: FMPFilingsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPFilingsData]:
        """Return the transformed data."""
        return [FMPFilingsData.model_validate(d) for d in data]

"""Databento Options Chains Model."""

# pylint: disable=unused-argument
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from dateutil import parser
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_databento.utils.helpers import get_options_chain, last_business_day
from pydantic import Field, field_validator


class DatabentoOptionsChainsQueryParams(OptionsChainsQueryParams):
    """Databento Options Chains Query."""

    date: Optional[dateType] = Field(
        default=None, description="The end-of-day date for options chains data."
    )


class DatabentoOptionsChainsData(OptionsChainsData):
    """Databento Options Chains Data."""

    __alias_dict__ = {
        "contract_symbol": "symbol",
        "symbol": "ticker",
        "eod_date": "date",
        "option_type": "type",
    }

    @field_validator(
        "date",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string."""
        # only pass it to the parser if it is not a datetime object
        if isinstance(v, str):
            return parser.parse(v)
        return v


class DatabentoOptionsChainsFetcher(
    Fetcher[DatabentoOptionsChainsQueryParams, List[DatabentoOptionsChainsData]]
):
    """Transform the query, extract and transform the data from the Databento endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> DatabentoOptionsChainsQueryParams:
        """Transform the query."""
        transform_params = params.copy()
        now = datetime.now().date()
        if params.get("date") is None:
            transform_params["date"] = last_business_day(now)
        return DatabentoOptionsChainsQueryParams(**transform_params)

    @staticmethod
    async def aextract_data(
        query: DatabentoOptionsChainsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Databento endpoint."""
        key = credentials.get("databento_api_key") if credentials else ""
        data = get_options_chain(query.symbol, "2024-02-05", key).to_dict(
            orient="records"
        )

        if not data:
            raise EmptyDataError()

        return data

    @staticmethod
    def transform_data(
        query: DatabentoOptionsChainsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[DatabentoOptionsChainsData]:
        """Return the transformed data."""

        return [DatabentoOptionsChainsData.model_validate(d) for d in data]

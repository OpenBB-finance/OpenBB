"""FMP Insider Trading Model."""

# pylint: disable=unused-argument

import math
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.insider_trading import (
    InsiderTradingData,
    InsiderTradingQueryParams,
)
from openbb_core.provider.utils.helpers import amake_requests, get_querystring
from openbb_fmp.utils.definitions import TRANSACTION_TYPES, TRANSACTION_TYPES_DICT
from pydantic import Field, model_validator


class FMPInsiderTradingQueryParams(InsiderTradingQueryParams):
    """FMP Insider Trading Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Insider-Trading
    """

    __json_schema_extra__ = {
        "transaction_type": {
            "multiple_items_allowed": False,
            "choices": list(TRANSACTION_TYPES_DICT),
        }
    }
    __alias_dict__ = {
        "transaction_type": "transactionType",
    }

    transaction_type: Optional[TRANSACTION_TYPES] = Field(
        default=None,
        description="Type of the transaction.",
    )

    @model_validator(mode="after")
    @classmethod
    def validate_transaction_type(cls, values: "FMPInsiderTradingQueryParams"):
        """Validate the transaction type."""
        if isinstance(values.transaction_type, list):
            values.transaction_type = ",".join(values.transaction_type)
        return values


class FMPInsiderTradingData(InsiderTradingData):
    """FMP Insider Trading Data."""

    __alias_dict__ = {
        "owner_cik": "reportingCik",
        "owner_name": "reportingName",
        "owner_title": "typeOfOwner",
        "security_type": "securityName",
        "transaction_price": "price",
        "acquisition_or_disposition": "acquistionOrDisposition",
        "filing_url": "link",
    }

    form_type: str = Field(description="Form type of the insider trading.")


class FMPInsiderTradingFetcher(
    Fetcher[
        FMPInsiderTradingQueryParams,
        List[FMPInsiderTradingData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPInsiderTradingQueryParams:
        """Transform the query params."""
        return FMPInsiderTradingQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPInsiderTradingQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        transaction_type = TRANSACTION_TYPES_DICT.get(query.transaction_type, None)
        query = query.model_copy(update={"transaction_type": transaction_type})

        base_url = "https://financialmodelingprep.com/api/v4/insider-trading"
        query_str = get_querystring(query.model_dump(by_alias=True), ["page"])

        pages = math.ceil(query.limit / 100)
        urls = [
            f"{base_url}?{query_str}&page={page}&apikey={api_key}"
            for page in range(pages)
        ]

        return await amake_requests(urls, raise_for_status=True, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPInsiderTradingQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPInsiderTradingData]:
        """Return the transformed data."""
        data = sorted(data, key=lambda x: x["filingDate"], reverse=True)
        return [FMPInsiderTradingData.model_validate(d) for d in data]

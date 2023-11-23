"""FMP Insider Trading Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.insider_trading import (
    InsiderTradingData,
    InsiderTradingQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_fmp.utils.helpers import get_data_many


class FMPInsiderTradingQueryParams(InsiderTradingQueryParams):
    """FMP Insider Trading Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Insider-Trading
    """

    __alias_dict__ = {"transaction_type": "transactionType"}


class FMPInsiderTradingData(InsiderTradingData):
    """FMP Insider Trading Data."""

    __alias_dict__ = {
        "acquisition_or_disposition": "acquistionOrDisposition",
        "last_number_of_13f_shares": "lastNumberOf13FShares",
        "securities_owned": "securitiesOwned",
    }


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
    def extract_data(
        query: FMPInsiderTradingQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v4/insider-trading"
        query_str = get_querystring(query.model_dump(by_alias=True), ["page"])

        data: List[Dict] = []

        limit_reached = 0
        page = 0

        while limit_reached <= query.limit:
            url = f"{base_url}?{query_str}&page={page}&apikey={api_key}"
            data.extend(get_data_many(url, **kwargs))
            limit_reached += len(data)
            page += 1

        return data[: query.limit]

    @staticmethod
    def transform_data(
        query: FMPInsiderTradingQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPInsiderTradingData]:
        """Return the transformed data."""
        data = sorted(data, key=lambda x: x["filingDate"], reverse=True)
        return [FMPInsiderTradingData.model_validate(d) for d in data]

"""FMP Key Executives Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.key_executives import (
    KeyExecutivesData,
    KeyExecutivesQueryParams,
)
from pydantic import ConfigDict


class FMPKeyExecutivesQueryParams(KeyExecutivesQueryParams):
    """FMP Key Executives Query.

    Source: https://site.financialmodelingprep.com/developer/docs#company-executives
    """


class FMPKeyExecutivesData(KeyExecutivesData):
    """FMP Key Executives Data."""

    model_config = ConfigDict(extra="ignore")


class FMPKeyExecutivesFetcher(
    Fetcher[
        FMPKeyExecutivesQueryParams,
        list[FMPKeyExecutivesData],
    ]
):
    """FMP Key Executives Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPKeyExecutivesQueryParams:
        """Transform the query params."""
        return FMPKeyExecutivesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPKeyExecutivesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        base_url = "https://financialmodelingprep.com/stable"
        url = f"{base_url}/key-executives?symbol={query.symbol}&apikey={api_key}"

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPKeyExecutivesQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPKeyExecutivesData]:
        """Return the transformed data."""
        return [FMPKeyExecutivesData.model_validate(d) for d in data]

"""FMP Crypto Search Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_search import (
    CryptoSearchData,
    CryptoSearchQueryParams,
)
from pydantic import Field, field_validator


class FMPCryptoSearchQueryParams(CryptoSearchQueryParams):
    """FMP Crypto Search Query.

    Source: https://site.financialmodelingprep.com/developer/docs#cryptocurrency-list
    """

    @field_validator("query", mode="after", check_fields=False)
    def validate_query(cls, v: str) -> str:  # pylint: disable=no-self-argument
        """Return the query."""
        if isinstance(v, str):
            return v.replace("-", "") if "-" in v else v
        return None


class FMPCryptoSearchData(CryptoSearchData):
    """FMP Crypto Search Data."""

    exchange: str | None = Field(
        description="The exchange code the crypto trades on.",
        default=None,
    )
    ico_date: dateType | None = Field(
        description="The ICO date of the token.",
        default=None,
    )
    circulating_supply: float | None = Field(
        description="The circulating supply of the token.",
        default=None,
    )
    total_supply: float | None = Field(
        description="The total supply of the token.",
        default=None,
    )


class FMPCryptoSearchFetcher(
    Fetcher[
        FMPCryptoSearchQueryParams,
        list[FMPCryptoSearchData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPCryptoSearchQueryParams:
        """Transform the query."""
        return FMPCryptoSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCryptoSearchQueryParams,  # pylint: disable=unused-argument
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = f"https://financialmodelingprep.com/stable/cryptocurrency-list?apikey={api_key}"

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCryptoSearchQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FMPCryptoSearchData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        cryptos = DataFrame(data)
        if query.query:
            cryptos = cryptos[
                cryptos["symbol"].str.contains(query.query, case=False)
                | cryptos["name"].str.contains(query.query, case=False)
                | cryptos["exchange"].str.contains(query.query, case=False)
            ]
        return [
            FMPCryptoSearchData.model_validate(d) for d in cryptos.to_dict("records")
        ]

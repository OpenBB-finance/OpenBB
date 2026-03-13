"""Intrinio ETF Search Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_intrinio.utils.references import ETF_EXCHANGES
from pydantic import Field


class IntrinioEtfSearchQueryParams(EtfSearchQueryParams):
    """
    Intrinio ETF Search Query Params.

    Source: https://docs.intrinio.com/documentation/web_api/search_etfs_v2
    """

    exchange: None | ETF_EXCHANGES = Field(
        default=None,
        description="Target a specific exchange by providing the MIC code.",
    )


class IntrinioEtfSearchData(EtfSearchData):
    """Intrinio ETF Search Data."""

    __alias_dict__ = {
        "intrinio_id": "id",
        "symbol": "ticker",
        "exchange": "exchange_mic",
    }

    exchange: str | None = Field(
        default=None,
        description="The exchange MIC code.",
    )
    figi_ticker: str | None = Field(
        None,
        description="The OpenFIGI ticker.",
    )
    ric: str | None = Field(
        None,
        description="The Reuters Instrument Code.",
    )
    isin: str | None = Field(
        None,
        description="The International Securities Identification Number.",
    )
    sedol: str | None = Field(
        None,
        description="The Stock Exchange Daily Official List.",
    )
    intrinio_id: str | None = Field(
        None,
        description="The unique Intrinio ID for the security.",
    )


class IntrinioEtfSearchFetcher(
    Fetcher[IntrinioEtfSearchQueryParams, list[IntrinioEtfSearchData]]
):
    """Intrinio ETF Search Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> IntrinioEtfSearchQueryParams:
        """Transform query."""
        return IntrinioEtfSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioEtfSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Intrinio endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import (
            ClientResponse,
            ClientSession,
            amake_request,
        )

        api_key = credentials.get("intrinio_api_key") if credentials else ""
        BASE = "https://api-v2.intrinio.com/etfs"
        if query.exchange is not None:
            url = f"{BASE}?exchange={query.exchange.upper()}&page_size=10000&api_key={api_key}"
        elif query.query:
            url = f"{BASE}/search?query={query.query}&page_size=10000&api_key={api_key}"
        else:
            url = f"{BASE}?page_size=10000&api_key={api_key}"

        data: list = []

        async def response_callback(response: ClientResponse, session: ClientSession):
            """Async response callback."""
            results = await response.json()

            if results.get("messages"):  # type: ignore
                messages = results.get("messages")  # type: ignore
                raise OpenBBError(str(messages))

            if results.get("etfs") and len(results.get("etfs")) > 0:  # type: ignore
                data.extend(results.get("etfs"))  # type: ignore
                while results.get("next_page"):  # type: ignore
                    next_page = results["next_page"]  # type: ignore
                    next_url = f"{url}&next_page={next_page}"
                    results = await amake_request(next_url, session=session, **kwargs)
                    if "etfs" in results and len(results.get("etfs")) > 0:  # type: ignore
                        data.extend(results.get("etfs"))  # type: ignore
            return data

        return await amake_request(url, response_callback=response_callback, **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: IntrinioEtfSearchQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[IntrinioEtfSearchData]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        import re  # noqa
        from pandas import DataFrame  # noqa

        if not data:
            raise EmptyDataError("No data found.")

        results = DataFrame(data)
        if query.query:
            pattern = f".*{re.escape(query.query)}.*"
            results = results[
                results["name"].str.contains(pattern, case=False, regex=True)
            ]

        return [
            IntrinioEtfSearchData.model_validate(d)
            for d in results.to_dict(orient="records")
        ]

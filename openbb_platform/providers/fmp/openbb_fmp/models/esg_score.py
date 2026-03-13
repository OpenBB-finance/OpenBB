"""FMP ESG Score Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.esg_score import (
    EsgScoreData,
    EsgScoreQueryParams,
)


class FMPEsgScoreQueryParams(EsgScoreQueryParams):
    """FMP ESG Score Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class FMPEsgScoreData(EsgScoreData):
    """FMP ESG Score Data."""

    __alias_dict__ = {
        "period_ending": "date",
        "disclosure_date": "acceptedDate",
        "esg_score": "ESGScore",
    }


class FMPEsgScoreFetcher(
    Fetcher[
        FMPEsgScoreQueryParams,
        list[FMPEsgScoreData],
    ]
):
    """FMP ESG Score Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPEsgScoreQueryParams:
        """Transform the query."""
        return FMPEsgScoreQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEsgScoreQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import warnings
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_fmp.utils.helpers import get_data

        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.split(",")
        results: list = []

        async def get_one(symbol):
            """Get data for one symbol."""
            url = f"https://financialmodelingprep.com/stable/esg-disclosures?symbol={symbol}&apikey={api_key}"
            result = await get_data(url, **kwargs)

            if not result:
                warnings.warn(f"Symbol Error: No data found for {symbol}")
            elif result:
                results.extend(result)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No data found for the given symbols.")

        return sorted(results, key=lambda x: x.get("date", ""), reverse=True)

    @staticmethod
    def transform_data(
        query: FMPEsgScoreQueryParams, data: list, **kwargs: Any
    ) -> list[FMPEsgScoreData]:
        """Return the transformed data."""
        return [FMPEsgScoreData.model_validate(d) for d in data]

"""Intrinio Forward PE Estimates Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.forward_pe_estimates import (
    ForwardPeEstimatesData,
    ForwardPeEstimatesQueryParams,
)
from pydantic import Field


class IntrinioForwardPeEstimatesQueryParams(ForwardPeEstimatesQueryParams):
    """Intrinio Forward PE Estimates Query.

    https://api-v2.intrinio.com/zacks/forward_pe?
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class IntrinioForwardPeEstimatesData(ForwardPeEstimatesData):
    """Intrinio Forward PE Estimates Data."""

    __alias_dict__ = {
        "symbol": "ticker",
        "name": "company_name",
        "year1": "forward_pe_year1",
        "year2": "forward_pe_year2",
        "year3": "forward_pe_year3",
        "year4": "forward_pe_year4",
        "year5": "forward_pe_year5",
        "peg_ratio_year1": "forward_peg_ratio_year1",
        "eps_ttm": "latest_ttm_eps",
        "last_updated": "updated_date",
    }

    peg_ratio_year1: Optional[float] = Field(
        default=None,
        description="Estimated Forward PEG ratio for the next fiscal year.",
    )
    eps_ttm: Optional[float] = Field(
        default=None,
        description="The latest trailing twelve months earnings per share.",
    )
    last_updated: Optional[dateType] = Field(
        default=None,
        description="The date the data was last updated.",
    )


class IntrinioForwardPeEstimatesFetcher(
    Fetcher[IntrinioForwardPeEstimatesQueryParams, list[IntrinioForwardPeEstimatesData]]
):
    """Intrinio Forward PE Estimates Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> IntrinioForwardPeEstimatesQueryParams:
        """Transform the query params."""
        return IntrinioForwardPeEstimatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioForwardPeEstimatesQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Intrinio endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_intrinio.utils.helpers import response_callback

        api_key = credentials.get("intrinio_api_key") if credentials else ""
        BASE_URL = "https://api-v2.intrinio.com/zacks/forward_pe"
        symbols = query.symbol.split(",") if query.symbol else None
        results: list[dict] = []

        async def get_one(symbol):
            """Get the data for one symbol."""
            url = f"{BASE_URL}/{symbol}?api_key={api_key}"
            try:
                data = await amake_request(
                    url, response_callback=response_callback, **kwargs
                )
            except Exception as e:
                raise OpenBBError(e) from e

            if data:
                results.append(data)  # type: ignore

        if symbols:
            try:
                gather_results = await asyncio.gather(
                    *[get_one(symbol) for symbol in symbols], return_exceptions=True
                )

                for result in gather_results:
                    if isinstance(result, UnauthorizedError):
                        raise result
                    if isinstance(result, OpenBBError):
                        raise result

                if not results:
                    raise EmptyDataError(
                        f"There were no results found for any of the given symbols. -> {symbols}"
                    )
                return results
            except Exception as e:
                raise OpenBBError(
                    f"Error in Intrinio request -> {e} -> {symbols}"
                ) from e

        async def fetch_callback(response, session):
            """Use callback for pagination."""
            data = await response.json()
            error = data.get("error", None)

            if error:
                message = data.get("message", "")
                if "api key" in message.lower() or "view this data" in error.lower():
                    raise UnauthorizedError(
                        f"Unauthorized Intrinio request -> {message} -> {error}"
                    )
                raise OpenBBError(f"Error: {error} -> {message}")

            forward_pe = data.get("forward_pe")

            if forward_pe and len(forward_pe) > 0:  # type: ignore
                results.extend(forward_pe)  # type: ignore

            return results

        url = f"{BASE_URL}?page_size=10000&api_key={api_key}"
        results = await amake_request(url, response_callback=fetch_callback, **kwargs)  # type: ignore

        if not results:
            raise EmptyDataError("The request was successful but was returned empty.")

        return results

    @staticmethod
    def transform_data(
        query: IntrinioForwardPeEstimatesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[IntrinioForwardPeEstimatesData]:
        """Transform the raw data into the standard format."""
        symbols = query.symbol.split(",") if query.symbol else []
        if symbols:
            data.sort(
                key=lambda item: (
                    symbols.index(item.get("ticker"))  # type: ignore
                    if item.get("ticker") in symbols
                    else len(symbols)
                )
            )
        return [IntrinioForwardPeEstimatesData.model_validate(d) for d in data]

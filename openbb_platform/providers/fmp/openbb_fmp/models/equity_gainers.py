"""FMP Top Gainers Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_performance import (
    EquityPerformanceData,
    EquityPerformanceQueryParams,
)
from pydantic import Field, field_validator


class FMPGainersQueryParams(EquityPerformanceQueryParams):
    """FMP Gainers Query.

    Source: https://site.financialmodelingprep.com/developer/docs#biggest-gainers
    """


class FMPGainersData(EquityPerformanceData):
    """FMP Gainers Data."""

    __alias_dict__ = {
        "percent_change": "changesPercentage",
    }

    exchange: str = Field(
        description="Stock exchange where the security is listed.",
    )

    @field_validator("percent_change", mode="before", check_fields=False)
    @classmethod
    def _normalize_percent(cls, v):
        """Normalize percent change by removing % sign and converting to float."""
        return v / 100 if v else None


class FMPGainersFetcher(Fetcher[FMPGainersQueryParams, list[FMPGainersData]]):
    """FMP Gainers Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPGainersQueryParams:
        """Transform query params."""
        return FMPGainersQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPGainersQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Get the raw data from the FMP API."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = (
            f"https://financialmodelingprep.com/stable/biggest-gainers?apikey={api_key}"
        )

        return await get_data_many(url)

    @staticmethod
    def transform_data(
        query: EquityPerformanceQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FMPGainersData]:
        """Transform data."""
        return [
            FMPGainersData.model_validate(d)
            for d in sorted(
                data,
                key=lambda x: x["changesPercentage"],
                reverse=query.sort == "desc",
            )
        ]

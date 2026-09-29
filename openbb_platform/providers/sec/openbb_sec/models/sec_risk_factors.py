"""SEC Filing Risk Factors Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_sec.models.sec_financials import FilingSectionQueryParams


class SecRiskFactorsQueryParams(FilingSectionQueryParams):
    """SEC Filing Risk Factors Query."""


class SecRiskFactorsData(Data):
    """SEC Filing Risk Factors Data."""

    risk_factor: str | None = Field(
        default=None, description="The individual risk factor heading."
    )
    text: str = Field(description="The text of the risk factor.")


class SecRiskFactorsFetcher(
    Fetcher[SecRiskFactorsQueryParams, list[SecRiskFactorsData]]
):
    """SEC Filing Risk Factors Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecRiskFactorsQueryParams:
        """Transform the query."""
        return SecRiskFactorsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecRiskFactorsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the Risk Factors section from the filing."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_sec.models.sec_financials import (
            FinancialStatements,
            no_filing_message,
            resolve_section_url,
        )

        url = await resolve_section_url(query, annual_default=True)
        if not url:
            raise EmptyDataError(no_filing_message(query.symbol))

        statements = FinancialStatements.from_url(url, query.use_cache)
        factors = statements.risk_factors()

        if not factors:
            raise EmptyDataError(f"No Risk Factors section found for {query.symbol}.")

        return factors

    @staticmethod
    def transform_data(
        query: SecRiskFactorsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[SecRiskFactorsData]:
        """Transform the data."""
        return [SecRiskFactorsData.model_validate(d) for d in data]

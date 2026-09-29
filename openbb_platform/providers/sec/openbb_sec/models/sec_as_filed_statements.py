"""SEC As-Filed Financial Statements Model."""

from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_sec.models.sec_financials import FilingSectionQueryParams


class SecAsFiledStatementsQueryParams(FilingSectionQueryParams):
    """SEC As-Filed Financial Statements Query."""

    statement_type: Literal["income", "balance", "cash", "equity"] = Field(
        default="income",
        description="The financial statement to retrieve, as reported in the filing.",
    )


class SecAsFiledStatementsData(Data):
    """SEC As-Filed Financial Statements Data."""

    order: int | None = Field(
        default=None, description="Presentation order of the line item."
    )
    tag: str | None = Field(default=None, description="XBRL concept tag, if available.")
    parent_tag: str | None = Field(
        default=None, description="Parent concept tag or section."
    )
    preferred_label: str | None = Field(
        default=None, description="Preferred label role."
    )
    balance: str | None = Field(
        default=None, description="Balance type (credit/debit)."
    )
    weight: float | str | None = Field(default=None, description="Calculation weight.")
    decimals: int | str | None = Field(default=None, description="Reported decimals.")
    context_ref: str | None = Field(
        default=None, description="XBRL context reference or period descriptor."
    )
    period_beginning: str | None = Field(
        default=None, description="Start of the reporting period."
    )
    period_ending: str | None = Field(
        default=None, description="End of the reporting period."
    )
    unit: str | None = Field(default=None, description="Unit of measure.")
    label: str | None = Field(default=None, description="Line item label.")
    value: float | int | str | None = Field(default=None, description="Reported value.")


class SecAsFiledStatementsFetcher(
    Fetcher[SecAsFiledStatementsQueryParams, list[SecAsFiledStatementsData]]
):
    """SEC As-Filed Financial Statements Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecAsFiledStatementsQueryParams:
        """Transform the query."""
        return SecAsFiledStatementsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecAsFiledStatementsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the as-filed statement from the filing."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_sec.models.sec_financials import (
            FinancialStatements,
            no_filing_message,
            resolve_section_url,
        )

        url = await resolve_section_url(query, annual_default=False)
        if not url:
            raise EmptyDataError(no_filing_message(query.symbol))

        statements = FinancialStatements.from_url(url, query.use_cache)
        data, _ = statements.get_statement(query.statement_type)

        if data is None or data.empty:
            raise EmptyDataError(
                f"No {query.statement_type} statement found for {query.symbol}."
            )

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: SecAsFiledStatementsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[SecAsFiledStatementsData]:
        """Transform the data."""
        return [SecAsFiledStatementsData.model_validate(d) for d in data]

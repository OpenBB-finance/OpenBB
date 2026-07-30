"""FFIEC Executive Summary Report (ESR) Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveExecutiveSummaryQueryParams(QueryParams):
    """FFIEC Executive Summary Report Query Parameters."""

    symbol: str | None = Field(
        default=None,
        description="The bank's stock ticker, resolved to its parent RSSD identifier.",
    )
    rssd_id: str | None = Field(
        default=None,
        description="The bank's RSSD identifier (the UBPR ID RSSD).",
    )
    all_periods: bool = Field(
        default=False,
        description="Return every reported period instead of only the most recent five.",
    )


class FederalReserveExecutiveSummaryData(Data):
    """FFIEC Executive Summary Report Data."""

    label: str = Field(description="The line item, indented by the report hierarchy.")
    is_header: bool = Field(
        default=False, description="Whether the row is a section or sub-section header."
    )
    narrative: str | None = Field(
        default=None,
        description="The FFIEC Interactive User's Guide definition of the line"
        " item's concept, when available.",
    )


class FederalReserveExecutiveSummaryFetcher(
    Fetcher[
        FederalReserveExecutiveSummaryQueryParams,
        list[FederalReserveExecutiveSummaryData],
    ]
):
    """FFIEC Executive Summary Report Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveExecutiveSummaryQueryParams:
        """Transform the query params."""
        query = FederalReserveExecutiveSummaryQueryParams(**params)
        if not query.rssd_id and not query.symbol:
            raise OpenBBError(
                ValueError("Provide a `symbol` or `rssd_id` to identify the bank.")
            )
        return query

    @staticmethod
    def extract_data(
        query: FederalReserveExecutiveSummaryQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the Executive Summary Report from the FFIEC CDR report router."""
        from openbb_federal_reserve.utils.executive_summary_report import (
            fetch_executive_summary,
        )
        from openbb_federal_reserve.utils.ticker import (
            resolve_rssd_to_bank,
            resolve_ticker_to_rssd,
        )
        from openbb_federal_reserve.utils.ubpr_report import no_bank_report_error

        rssd_id = query.rssd_id
        if not rssd_id and query.symbol:
            rssd_id = resolve_ticker_to_rssd(query.symbol)
            if not rssd_id:
                raise OpenBBError(
                    f"Could not resolve symbol '{query.symbol}' to an RSSD identifier."
                )

        rssd_id, name = resolve_rssd_to_bank(str(rssd_id))
        rows = fetch_executive_summary(rssd_id, all_periods=query.all_periods)
        if not rows:
            raise EmptyDataError("The request was returned empty.")
        structural = {"label", "is_header", "narrative"}
        if not any(
            value is not None
            for row in rows
            for key, value in row.items()
            if key not in structural
        ):
            raise no_bank_report_error(rssd_id, "Executive Summary")
        rows[0] = {"_rssd": rssd_id, "_name": name, **rows[0]}
        return rows

    @staticmethod
    def transform_data(
        query: FederalReserveExecutiveSummaryQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[FederalReserveExecutiveSummaryData]]:
        """Validate the parsed report rows; surface the resolved bank as metadata."""
        head = data[0] if data else {}
        rssd_id = head.pop("_rssd", None)
        name = head.pop("_name", None)
        return AnnotatedResult(
            result=[
                FederalReserveExecutiveSummaryData.model_validate(row) for row in data
            ],
            metadata={
                key: value
                for key, value in {"rssd_id": rssd_id, "name": name}.items()
                if value
            },
        )

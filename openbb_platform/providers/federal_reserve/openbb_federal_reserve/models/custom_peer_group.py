"""FFIEC UBPR Custom Peer Group (CPG) Report Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.custom_peer_group import UBPR_SECTIONS


class FederalReserveCustomPeerGroupQueryParams(QueryParams):
    """FFIEC UBPR Custom Peer Group Report Query Parameters."""

    __json_schema_extra__ = {
        "section": {
            "x-widget_config": {
                "options": [{"label": name, "value": name} for name in UBPR_SECTIONS]
            }
        }
    }

    symbol: str | None = Field(
        default=None,
        description="The target bank's stock ticker, resolved to its parent RSSD"
        " identifier.",
    )
    rssd_id: str | None = Field(
        default=None,
        description="The target bank's RSSD identifier (the UBPR ID RSSD).",
    )
    peers: str | None = Field(
        default=None,
        description="Comma-separated RSSD identifiers forming the custom peer group;"
        " the target bank may be included.",
    )
    section: str = Field(
        default="Summary Ratios",
        description="The UBPR report section (page) to return.",
        json_schema_extra={"choices": UBPR_SECTIONS},
    )
    all_periods: bool = Field(
        default=False,
        description="Return every reported period as the bank's own time series.",
    )


class FederalReserveCustomPeerGroupData(Data):
    """FFIEC UBPR Custom Peer Group Report Data.

    One row per report line item. Each period contributes one
    ``"<ISO> <bank name>"`` column carrying the target bank's value, named by the
    bank's readable name.
    """

    label: str = Field(description="The line item, indented by the report hierarchy.")
    is_header: bool = Field(
        default=False, description="Whether the row is a section or sub-section header."
    )
    narrative: str | None = Field(
        default=None,
        description="The MDRM definition of the line item's concept, where available.",
    )


class FederalReserveCustomPeerGroupFetcher(
    Fetcher[
        FederalReserveCustomPeerGroupQueryParams,
        list[FederalReserveCustomPeerGroupData],
    ]
):
    """FFIEC UBPR Custom Peer Group Report Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveCustomPeerGroupQueryParams:
        """Transform the query params."""
        query = FederalReserveCustomPeerGroupQueryParams(**params)
        if not query.rssd_id and not query.symbol:
            raise OpenBBError(
                ValueError("Provide a `symbol` or `rssd_id` to identify the bank.")
            )
        if not query.peers:
            raise OpenBBError(
                ValueError("Provide `peers` as a comma-separated list of RSSD ids.")
            )
        return query

    @staticmethod
    def extract_data(
        query: FederalReserveCustomPeerGroupQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the requested CPG section from the FFIEC CDR report router.

        A holding-company RSSD carries no UBPR, so the target bank is resolved to
        its lead filing bank; the resolved bank is surfaced through the leading
        row's ``_rssd``/``_name`` metadata keys.
        """
        from openbb_federal_reserve.utils.custom_peer_group import (
            fetch_custom_peer_group,
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
        result = fetch_custom_peer_group(
            rssd_id,
            str(query.peers),
            query.section,
            all_periods=query.all_periods,
        )
        rows = result["rows"]
        if not rows:
            raise EmptyDataError("The request was returned empty.")
        structural = {"label", "is_header", "narrative"}
        if not any(
            value is not None
            for row in rows
            for key, value in row.items()
            if key not in structural
        ):
            raise no_bank_report_error(rssd_id, "UBPR")
        rows[0] = {"_rssd": rssd_id, "_name": name, **rows[0]}
        return rows

    @staticmethod
    def transform_data(
        query: FederalReserveCustomPeerGroupQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[FederalReserveCustomPeerGroupData]]:
        """Validate the parsed section rows; surface the resolved bank as metadata."""
        head = data[0] if data else {}
        rssd_id = head.pop("_rssd", None)
        name = head.pop("_name", None)
        return AnnotatedResult(
            result=[
                FederalReserveCustomPeerGroupData.model_validate(row) for row in data
            ],
            metadata={
                key: value
                for key, value in {
                    "rssd_id": rssd_id,
                    "name": name,
                    "section": query.section,
                }.items()
                if value
            },
        )

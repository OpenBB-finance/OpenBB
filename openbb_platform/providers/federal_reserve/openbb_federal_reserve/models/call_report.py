"""Federal Reserve / FFIEC Bank Call Report Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

_METADATA_FIELDS = {
    "RSSD9017": "name",
    "RSSD9130": "city",
    "RSSD9200": "state",
    "RSSD9220": "zip_code",
    "RSSD9050": "fdic_cert",
    "RCON9224": "lei",
}


def _to_number(value: Any) -> float | None:
    """Coerce a filed value to a number, returning None when non-numeric."""
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    """Coerce an XBRL decimals attribute to an int, returning None otherwise."""
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


class FederalReserveCallReportQueryParams(QueryParams):
    """FFIEC Bank Call Report Query Parameters."""

    symbol: str | None = Field(
        default=None,
        description="The bank's stock ticker; resolved to the subsidiary bank that"
        " files the Call Report (not its parent holding company).",
    )
    rssd_id: str | None = Field(
        default=None,
        description="The bank's RSSD identifier (the Call Report IDRSSD).",
    )
    fdic_cert: str | None = Field(
        default=None,
        description="The bank's FDIC certificate number (alternative to `rssd_id`).",
    )
    date: dateType | None = Field(
        default=None,
        description="The reporting period end date; defaults to the latest filed."
        " Call Reports are filed quarterly.",
    )
    period_type: str | None = Field(
        default=None,
        description="Limit to 'instant' items (balance-sheet, point-in-time) or"
        " 'duration' items (income-statement flows).",
    )


class FederalReserveCallReportData(Data):
    """FFIEC Bank Call Report Data."""

    date: dateType | None = Field(
        default=None, description="The reporting period end date."
    )
    rssd_id: str = Field(description="The bank's RSSD identifier (IDRSSD).")
    name: str | None = Field(default=None, description="The bank's name.")
    order: int | None = Field(
        default=None, description="The line item's position in report order."
    )
    section: str | None = Field(
        default=None, description="The Call Report schedule the item appears on."
    )
    parent: str | None = Field(
        default=None, description="The parent line item in the report hierarchy."
    )
    level: int | None = Field(
        default=None, description="The item's depth in the report hierarchy."
    )
    label: str | None = Field(default=None, description="The line item caption.")
    mdrm: str = Field(description="The MDRM mnemonic for the concept.")
    value: float | None = Field(default=None, description="The reported value.")
    unit: str | None = Field(
        default=None, description="The unit of measure (e.g. USD thousands, rate)."
    )
    decimals: int | None = Field(
        default=None, description="The reported precision, as filed in the XBRL."
    )
    period_type: str | None = Field(
        default=None, description="Whether the concept is an instant or a duration."
    )


class FederalReserveCallReportFetcher(
    Fetcher[
        FederalReserveCallReportQueryParams,
        list[FederalReserveCallReportData],
    ]
):
    """FFIEC Bank Call Report Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveCallReportQueryParams:
        """Transform the query params."""
        query = FederalReserveCallReportQueryParams(**params)
        if not query.rssd_id and not query.fdic_cert and not query.symbol:
            raise OpenBBError(
                ValueError(
                    "Provide a `symbol`, `rssd_id`, or `fdic_cert` to identify"
                    " the bank."
                )
            )
        return query

    @staticmethod
    def extract_data(
        query: FederalReserveCallReportQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Call Report XBRL bulk and parse the bank's instance."""
        from openbb_federal_reserve.utils.cdr import (
            bulk_rssids,
            fetch_bulk,
            parse_xbrl_instance,
            resolve_fdic_cert,
        )
        from openbb_federal_reserve.utils.ticker import (
            lead_subsidiary_bank,
            resolve_ticker_to_bank,
        )

        period = query.date.strftime("%m/%d/%Y") if query.date else None
        content = fetch_bulk("call_single", period, fmt="xbrl")
        if not content[:2] == b"PK":
            raise EmptyDataError("The request was returned empty.")

        filers = bulk_rssids(content)
        rssd_id = query.rssd_id
        if not rssd_id and query.symbol:
            rssd_id = resolve_ticker_to_bank(query.symbol, filers, period)
            if not rssd_id:
                raise OpenBBError(
                    f"Could not resolve symbol '{query.symbol}' to a bank that"
                    " files a Call Report."
                )
        elif not rssd_id and query.fdic_cert:
            rssd_id = resolve_fdic_cert(content, query.fdic_cert)
            if not rssd_id:
                raise OpenBBError(
                    f"Could not resolve FDIC certificate '{query.fdic_cert}'."
                )
        elif rssd_id:
            rssd_id = lead_subsidiary_bank(str(rssd_id), filers, period) or rssd_id

        parsed = parse_xbrl_instance(content, str(rssd_id))
        items = parsed["items"]
        if query.period_type:
            wanted = query.period_type.strip().lower()
            items = [i for i in items if i["period_type"] == wanted]
        if not items:
            raise EmptyDataError("The request was returned empty.")

        out: list[dict] = []
        for item in items:
            period = item.pop("period", None)
            out.append(
                {
                    "date": (
                        datetime.strptime(period, "%Y-%m-%d").date() if period else None
                    ),
                    "rssd_id": str(rssd_id),
                    "name": parsed["name"],
                    "form_type": parsed["form_type"],
                    **item,
                }
            )
        return out

    @staticmethod
    def transform_data(
        query: FederalReserveCallReportQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[FederalReserveCallReportData]]:
        """Split out cover-page metadata; place line items in schedule order."""
        from openbb_federal_reserve.utils.cdr import presentation_map
        from openbb_federal_reserve.utils.ffiec import entity_type
        from openbb_federal_reserve.utils.mdrm import fetch_mdrm_dictionary

        as_of = max((row["date"] for row in data if row.get("date")), default=None)
        form_type = data[0].get("form_type") if data else None
        rssd_id = data[0].get("rssd_id") if data else None
        hierarchy = presentation_map("call_single", form_type)
        schedule_count = max(
            (node.get("section_order", 0) for node in hierarchy.values()), default=0
        )
        dictionary = fetch_mdrm_dictionary(as_of=as_of, prefix="R")

        metadata: dict[str, Any] = {
            "rssd_id": rssd_id,
            "name": data[0].get("name") if data else None,
            "form_type": form_type,
            "entity_type": entity_type(rssd_id) if rssd_id else None,
            "reporting_date": as_of.isoformat() if as_of else None,
        }
        rows: list[dict] = []
        unmapped: list[dict] = []
        for row in data:
            row.pop("form_type", None)
            code = str(row["mdrm"]).upper()
            node = hierarchy.get(code, {})
            section = node.get("section")
            if section and "Demographic" in section:
                key = _METADATA_FIELDS.get(code)
                if key:
                    metadata[key] = str(row["value"]).strip() or None
                continue
            row["section"] = section
            row["parent"] = node.get("parent")
            row["level"] = node.get("level")
            row["label"] = node.get("label") or dictionary.get(code)
            row["value"] = _to_number(row["value"])
            row["decimals"] = _to_int(row["decimals"])
            row["order"] = node.get("order")
            row["_section"] = node.get("section_order")
            rows.append(row)
            if row["_section"] is None:
                unmapped.append(row)

        for position, row in enumerate(
            sorted(unmapped, key=lambda row: str(row["mdrm"])), start=1
        ):
            row["section"] = "Supplemental Information"
            row["parent"] = None
            row["level"] = 1
            row["order"] = position
            row["_section"] = schedule_count + 1

        rows.sort(key=lambda row: (row["_section"], row["order"]))
        for row in rows:
            row.pop("_section", None)
        return AnnotatedResult(
            result=[FederalReserveCallReportData.model_validate(row) for row in rows],
            metadata={key: value for key, value in metadata.items() if value},
        )

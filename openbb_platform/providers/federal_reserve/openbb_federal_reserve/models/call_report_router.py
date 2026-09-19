"""FFIEC Call Report Sectioned Model (UBPR-style section grid)."""

from datetime import datetime
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

_NBSP = "\u00a0"

CALL_REPORT_SECTIONS = [
    "Schedule RI - Income Statement",
    "Schedule RI-A - Changes in Bank Equity Capital",
    "Schedule RI-B Part I - Charge-offs and Recoveries on Loans and Leases",
    "Schedule RI-B Part II - Changes in Allowances for Credit Losses",
    "Schedule RI-C - Disaggregated Data on the Allowances for Credit Losses",
    "Schedule RI-D - Income from Foreign Offices",
    "Schedule RI-E - Explanations",
    "Schedule RC - Balance Sheet",
    "Schedule RC-A - Cash and Balances Due From Depository Institutions",
    "Schedule RC-B - Securities",
    "Schedule RC-C Part I - Loans and Leases",
    "Schedule RC-C Part II - Loans to Small Businesses and Small Farms",
    "Schedule RC-D - Trading Assets and Liabilities",
    "Schedule RC-E - Deposit Liabilities",
    "Schedule RC-E Part I - Deposits in Domestic Offices",
    "Schedule RC-F - Other Assets",
    "Schedule RC-G - Other Liabilities",
    "Schedule RC-H - Selected Balance Sheet Items for Domestic Offices",
    "Schedule RC-I - Assets and Liabilities of IBFs",
    "Schedule RC-K - Quarterly Averages",
    "Schedule RC-L - Derivatives and Off-Balance Sheet Items",
    "Schedule RC-M - Memoranda",
    "Schedule RC-N - Past Due and Nonaccrual Loans Leases and Other Assets",
    "Schedule RC-O - Other Data for Deposit Insurance and FICO Assessments",
    "Schedule RC-P - 1-4 Family Residential Mortgage Banking Activities",
    "Schedule RC-Q - Assets and Liabilities Measured at Fair Value on a"
    " Recurring Basis",
    "Schedule RC-R Part I - Regulatory Capital Components and Ratios",
    "Schedule RC-R Part II - Risk-Weighted Assets",
    "Schedule RC-S - Servicing Securitization and Asset Sale Activities",
    "Schedule RC-T - Fiduciary and Related Services",
    "Schedule RC-V - Variable Interest Entities",
    "Schedule SU - Supplemental Information",
]


def _to_number(value: Any) -> float | None:
    """Coerce a filed value to a number, returning None when non-numeric."""
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _match(section: str, candidate: str | None) -> bool:
    """Match a schedule name to a section, tolerating Part/punctuation drift."""
    if not candidate:
        return False
    norm = lambda text: " ".join(text.replace("-", " ").split()).lower()  # noqa: E731
    return norm(section) == norm(candidate)


class FederalReserveCallReportSectionedQueryParams(QueryParams):
    """FFIEC Call Report Sectioned Query Parameters."""

    __json_schema_extra__ = {
        "section": {
            "x-widget_config": {
                "options": [
                    {"label": name, "value": name} for name in CALL_REPORT_SECTIONS
                ]
            }
        }
    }

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
    section: str = Field(
        default="Schedule RC - Balance Sheet",
        description="The Call Report schedule (section) to return.",
        json_schema_extra={"choices": CALL_REPORT_SECTIONS},
    )
    all_periods: bool = Field(
        default=False,
        description="Return every reported period instead of only the most"
        " recent five.",
    )


class FederalReserveCallReportSectionedData(Data):
    """FFIEC Call Report Sectioned Data."""

    label: str = Field(description="The line item, indented by the report hierarchy.")
    is_header: bool = Field(
        default=False, description="Whether the row is a section or sub-section header."
    )
    narrative: str | None = Field(
        default=None,
        description="The MDRM definition of the line item, shown in a hover card.",
    )


class FederalReserveCallReportSectionedFetcher(
    Fetcher[
        FederalReserveCallReportSectionedQueryParams,
        list[FederalReserveCallReportSectionedData],
    ]
):
    """FFIEC Call Report Sectioned Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveCallReportSectionedQueryParams:
        """Transform the query params."""
        query = FederalReserveCallReportSectionedQueryParams(**params)
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
        query: FederalReserveCallReportSectionedQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Build one schedule as wide line rows across the recent periods."""
        from openbb_federal_reserve.utils.cdr import (
            bulk_rssids,
            fetch_bulk,
            parse_xbrl_instance,
            presentation_map,
            resolve_fdic_cert,
        )
        from openbb_federal_reserve.utils.ticker import (
            lead_subsidiary_bank,
            resolve_ticker_to_bank,
        )

        latest = fetch_bulk("call_single", None, fmt="xbrl")
        if not latest[:2] == b"PK":
            raise EmptyDataError("The request was returned empty.")
        filers = bulk_rssids(latest)

        rssd_id = query.rssd_id
        if not rssd_id and query.symbol:
            rssd_id = resolve_ticker_to_bank(query.symbol, filers, None)
            if not rssd_id:
                raise OpenBBError(
                    f"Could not resolve symbol '{query.symbol}' to a bank that"
                    " files a Call Report."
                )
        elif not rssd_id and query.fdic_cert:
            rssd_id = resolve_fdic_cert(latest, query.fdic_cert)
            if not rssd_id:
                raise OpenBBError(
                    f"Could not resolve FDIC certificate '{query.fdic_cert}'."
                )
        else:
            rssd_id = lead_subsidiary_bank(str(rssd_id), filers, None) or rssd_id

        from openbb_federal_reserve.utils.cdr import list_periods

        available = list_periods("call_single")
        periods = [
            row["date"] for row in (available if query.all_periods else available[:5])
        ]
        facts: dict[str, dict[str, Any]] = {}
        form_type: str | None = None
        name: str | None = None
        isos: list[str] = []
        for period in periods:
            content = (
                latest if period == periods[0] else fetch_bulk("call_single", period)
            )
            parsed = parse_xbrl_instance(content, str(rssd_id))
            form_type = form_type or parsed["form_type"]
            name = name or parsed["name"]
            iso: str | None = None
            for item in parsed["items"]:
                iso = item["period"]
                facts.setdefault(item["mdrm"], {})[iso] = item["value"]
            if iso and iso not in isos:
                isos.append(iso)

        if not facts or not form_type:
            raise EmptyDataError("The request was returned empty.")

        isos.sort(reverse=True)
        hierarchy = presentation_map("call_single", form_type)
        codes = [
            code
            for code in facts
            if _match(query.section, hierarchy.get(code.upper(), {}).get("section"))
        ]
        if not codes:
            raise EmptyDataError(
                f"No data was found for the '{query.section}' schedule."
            )
        codes.sort(key=lambda code: hierarchy.get(code.upper(), {}).get("order") or 0)

        from openbb_federal_reserve.utils.concepts import concept_index, indented_name

        index = concept_index("call_single", form_type)
        rows: list[dict] = [
            {"label": query.section, "is_header": True, "narrative": None}
        ]
        for code in codes:
            meta = index.get(code.upper(), {})
            if meta.get("is_text"):
                continue
            node = hierarchy[code.upper()]
            level = node.get("level") or 1
            indent = _NBSP * 2 * max(level - 1, 0)
            label = node.get("label") or code
            label = (">" + indent + label) if indent else label
            rows.append(
                {
                    "label": indented_name(label, meta.get("name")),
                    "is_header": False,
                    "narrative": meta.get("narrative"),
                    **{iso: _to_number(facts[code].get(iso)) for iso in isos},
                }
            )
        if len(rows) == 1:
            raise EmptyDataError(
                f"No data was found for the '{query.section}' schedule."
            )
        return [
            {
                "_name": (name or "").strip() or None,
                "_rssd": str(rssd_id),
                "_periods": isos,
                **row,
            }
            if index == 0
            else row
            for index, row in enumerate(rows)
        ]

    @staticmethod
    def transform_data(
        query: FederalReserveCallReportSectionedQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[FederalReserveCallReportSectionedData]]:
        """Validate the parsed schedule rows; surface the bank as metadata."""
        from openbb_federal_reserve.utils.call_pages import CALL_PAGE_DESCRIPTIONS
        from openbb_federal_reserve.utils.ubpr_report import rectangularize

        head = data[0] if data else {}
        name = head.pop("_name", None)
        rssd_id = head.pop("_rssd", None)
        periods = head.pop("_periods", None)
        reporting_date = max(periods) if periods else None
        rows = rectangularize(data)
        if rows and rows[0].get("is_header") and not rows[0].get("narrative"):
            rows[0]["narrative"] = CALL_PAGE_DESCRIPTIONS.get(query.section)
        return AnnotatedResult(
            result=[
                FederalReserveCallReportSectionedData.model_validate(row)
                for row in rows
            ],
            metadata={
                key: value
                for key, value in {
                    "rssd_id": rssd_id,
                    "name": name,
                    "section": query.section,
                    "reporting_date": (
                        datetime.strptime(reporting_date, "%Y-%m-%d").date().isoformat()
                        if reporting_date
                        else None
                    ),
                }.items()
                if value
            },
        )

"""FFIEC UBPR Peer Group Bank Report Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

PEER_GROUP_BANK_SECTIONS = [
    "Summary Ratios",
    "Income Statement $",
    "QTR Income Statement $",
    "Noninterest Income and Expenses",
    "Asset Yields and Funding Costs",
    "Balance Sheet $",
    "Off Balance Sheet Items",
    "Derivative Instruments",
    "Derivative Analysis",
    "Balance Sheet %",
    "Allowance & Loan Mix-a",
    "Allowance & Loan Mix-b",
    "Concentrations of Credit",
    "PD, Nonacc & Rest Loans-a",
    "PD, Nonacc & Rest Loans-b",
    "Interest Rate Risk-a",
    "Interest Rate Risk-b",
    "Liquidity & Funding",
    "Liquidity & Inv Portfolio",
    "Capital Analysis-a",
    "Capital Analysis-b",
    "Capital Analysis-c",
    "Income Statement 1-Qtr-Ann",
    "Securitization & Asset Sale-a",
    "Securitization & Asset Sale-b",
    "Securitization & Asset Sale-c",
    "Fiduciary Services-a",
    "Fiduciary Services-b",
]

_REPORT_TYPE_ID = 283

_MONETARY_DATATYPES = {"9", "155"}


def _peer_group_name(rssd_id: str, cycle_id: str) -> tuple[str, str]:
    """Return the bank's peer-group name and description for a reporting cycle."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.ubpr_report import _post

    def _producer() -> list[dict]:
        """Fetch the bank's FFIEC institution attributes."""
        return _post(
            "FiAttributes",
            {"ID_RSSD": str(rssd_id), "ReportingCycleID": cycle_id, "supplemental": ""},
        )

    rows = cached(
        ("pgb_attributes", str(rssd_id), cycle_id),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )
    if not rows:
        raise OpenBBError(
            f"No FFIEC peer group is assigned to RSSD '{rssd_id}' for the period."
        )
    row = rows[0]
    return str(row.get("peergroupname") or ""), str(
        row.get("peergroupdescription") or ""
    )


def _peer_group_banks(peer_group_name: str, cycle_id: str) -> list[dict[str, str]]:
    """Return the peer group's member banks as RSSD/name records, in roster order."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.ubpr_report import _post

    def _producer() -> list[dict[str, str]]:
        """Fetch and trim the peer group's bank roster."""
        rows = _post(
            "LlistOfBanks",
            {
                "ReportingCycleID": cycle_id,
                "PeerGroupName": peer_group_name,
                "MaxRows": 0,
            },
        )
        return [
            {"rssd": str(row["rssd9001"]).strip(), "name": str(row["rssd9017"]).strip()}
            for row in rows
            if isinstance(row, dict) and row.get("rssd9001")
        ]

    return cached(
        ("pgb_roster", peer_group_name, cycle_id),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def _page_id(section: str | None) -> tuple[str, str]:
    """Resolve a section title (or pageid) to its (pageid, title)."""
    from openbb_federal_reserve.utils.ubpr_report import report_sections

    sections = report_sections(_REPORT_TYPE_ID)
    if not sections:
        raise OpenBBError("The report section list could not be retrieved.")
    target = (section or "").strip().lower()
    for row in sections:
        if not target or row["pageid"] == target or row["pagetitle"].lower() == target:
            return row["pageid"], row["pagetitle"]
    raise OpenBBError(f"Unknown report section '{section}'.")


def fetch_peer_group_bank_report(
    rssd_id: str, section: str | None = "Summary Ratios"
) -> dict[str, Any]:
    """Fetch one report section as wide per-bank rows for the bank's peer group.

    Returns ``{section, peer_group, columns, rows}`` where each row is ``{label,
    is_header, <bank cols>}`` and the bank columns are ``"<bank name> (<RSSD>)"``.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.concepts import (
        clean_name,
        concept_index,
        indented_name,
    )
    from openbb_federal_reserve.utils.guide import fetch_guide_concepts
    from openbb_federal_reserve.utils.ubpr_report import (
        _caption,
        _post,
        rectangularize,
        report_cycles,
    )

    page_id, title = _page_id(section)
    cycles = report_cycles()
    if not cycles:
        raise OpenBBError("The reporting-cycle list could not be retrieved.")
    cycle = cycles[0]
    cycle_id = cycle["reportingcycleid"]
    end_date = cycle["enddateformatted"]
    iso_date = f"{end_date[6:]}-{end_date[:2]}-{end_date[3:5]}"

    peer_group_name, peer_group_desc = _peer_group_name(str(rssd_id), cycle_id)
    banks = _peer_group_banks(peer_group_name, cycle_id)
    if not banks:
        return {
            "section": title,
            "peer_group": peer_group_desc,
            "columns": [],
            "rows": [],
        }

    names = {bank["rssd"]: bank["name"] for bank in banks}
    fi_list = ",".join(bank["rssd"] for bank in banks)
    sections = _post("MBReportPageSections", {"ScheduleID": page_id})
    section_ids = [
        str(row["sectionid"])
        for row in sections
        if isinstance(row, dict) and str(row.get("sectionid") or "0") != "0"
    ]

    def _producer() -> list[dict]:
        """Fetch and concatenate the page's sub-section line rows."""
        out: list[dict] = []
        for section_id in section_ids:
            out += _post(
                "MBReportSectionData",
                {
                    "SectionID": section_id,
                    "FIList": fi_list,
                    "ListIsCert": False,
                    "ReportingPeriodEndDate": iso_date,
                    "ShowConfidential": 0,
                    "ID_RSSD": str(rssd_id),
                },
            )
        return out

    raw = cached(
        ("pgb_lines", str(rssd_id), page_id, cycle_id, peer_group_name),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )
    if not raw:
        return {
            "section": title,
            "peer_group": peer_group_desc,
            "columns": [],
            "rows": [],
        }

    bank_cols = [k for k in raw[0] if "_" in k and k[:2].isdigit()]
    headers = {
        key: f"{names.get(key.split('_', 1)[1], 'Bank')} ({key.split('_', 1)[1]})"
        for key in bank_cols
    }
    index = concept_index("ubpr_ratio_single", None)
    concepts = {
        str(line.get("conceptname") or "")
        for line in raw
        if str(line.get("conceptname") or "")
    }
    guide = fetch_guide_concepts(sorted(concepts))
    rows: list[dict] = []
    for line in raw:
        caption = str(line.get("linecaption", ""))
        if caption == "#BlankLine#":
            continue
        values = {key: line.get(key) for key in bank_cols}
        has_value = any(v not in ("", None) for v in values.values())
        is_header = caption.startswith("#SectionTitle#") or not has_value
        code = str(line.get("conceptname") or "")
        meta = index.get(code, {})
        record: dict[str, Any] = {
            "label": _caption(caption),
            "is_header": is_header,
        }
        if is_header:
            record["narrative"] = None
        else:
            g = guide.get(code or "", {})
            label_name = clean_name(g.get("description")) or meta.get("name")
            record["label"] = indented_name(record["label"], label_name)
            record["narrative"] = g.get("narrative") or meta.get("narrative")
            datatype = str(line.get("datatypeid") or "")
            scale = 1000 if datatype in _MONETARY_DATATYPES else 1
            for key in bank_cols:
                raw_value = values[key]
                try:
                    record[headers[key]] = float(raw_value) * scale
                except (TypeError, ValueError):
                    record[headers[key]] = None
        rows.append(record)
    from openbb_federal_reserve.utils.ubpr_pages import UBPR_PAGE_DESCRIPTIONS

    final_rows = rectangularize(rows)
    if final_rows and final_rows[0].get("is_header"):
        final_rows[0]["narrative"] = UBPR_PAGE_DESCRIPTIONS.get(title)
    return {
        "section": title,
        "peer_group": peer_group_desc,
        "columns": [headers[key] for key in bank_cols],
        "rows": final_rows,
    }


class FederalReservePeerGroupBankQueryParams(QueryParams):
    """FFIEC UBPR Peer Group Bank Report Query Parameters."""

    __json_schema_extra__ = {
        "section": {
            "x-widget_config": {
                "options": [
                    {"label": name, "value": name} for name in PEER_GROUP_BANK_SECTIONS
                ]
            }
        }
    }

    symbol: str | None = Field(
        default=None,
        description="The bank's stock ticker, resolved to its parent RSSD identifier.",
    )
    rssd_id: str | None = Field(
        default=None,
        description="The bank's RSSD identifier; its UBPR peer group drives the report.",
    )
    section: str = Field(
        default="Summary Ratios",
        description="The UBPR report section (page) to return.",
        json_schema_extra={"choices": PEER_GROUP_BANK_SECTIONS},
    )


class FederalReservePeerGroupBankData(Data):
    """FFIEC UBPR Peer Group Bank Report Data.

    One row per report line item; each member bank of the subject bank's peer
    group contributes a column (``"<bank name> (<RSSD>)"``) for the latest period,
    in the report's own section layout.
    """

    label: str = Field(description="The line item, indented by the report hierarchy.")
    is_header: bool = Field(
        default=False, description="Whether the row is a section or sub-section header."
    )
    narrative: str | None = Field(
        default=None,
        description="The UBPR User's Guide definition of the line item, shown in a hover card.",
    )


class FederalReservePeerGroupBankFetcher(
    Fetcher[
        FederalReservePeerGroupBankQueryParams,
        list[FederalReservePeerGroupBankData],
    ]
):
    """FFIEC UBPR Peer Group Bank Report Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePeerGroupBankQueryParams:
        """Transform the query params."""
        query = FederalReservePeerGroupBankQueryParams(**params)
        if not query.rssd_id and not query.symbol:
            raise OpenBBError(
                ValueError("Provide a `symbol` or `rssd_id` to identify the bank.")
            )
        return query

    @staticmethod
    def extract_data(
        query: FederalReservePeerGroupBankQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the peer group bank report section from the FFIEC CDR router.

        A holding-company RSSD has no assigned UBPR peer group, so it is resolved
        to its lead filing bank; the resolved bank is surfaced through the leading
        row's ``_rssd``/``_name`` metadata keys.
        """
        from openbb_federal_reserve.models.peer_group_bank import (
            fetch_peer_group_bank_report,
        )
        from openbb_federal_reserve.utils.ticker import (
            resolve_rssd_to_bank,
            resolve_ticker_to_rssd,
        )

        rssd_id = query.rssd_id
        if not rssd_id and query.symbol:
            rssd_id = resolve_ticker_to_rssd(query.symbol)
            if not rssd_id:
                raise OpenBBError(
                    f"Could not resolve symbol '{query.symbol}' to an RSSD identifier."
                )

        rssd_id, name = resolve_rssd_to_bank(str(rssd_id))
        result = fetch_peer_group_bank_report(rssd_id, query.section)
        rows = result["rows"]
        if not rows:
            raise EmptyDataError("The request was returned empty.")
        rows[0] = {"_rssd": rssd_id, "_name": name, **rows[0]}
        return rows

    @staticmethod
    def transform_data(
        query: FederalReservePeerGroupBankQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[FederalReservePeerGroupBankData]]:
        """Validate the parsed section rows; surface the resolved bank as metadata."""
        head = data[0] if data else {}
        rssd_id = head.pop("_rssd", None)
        name = head.pop("_name", None)
        return AnnotatedResult(
            result=[
                FederalReservePeerGroupBankData.model_validate(row) for row in data
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

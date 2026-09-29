"""Federal Reserve Unified FFIEC Financial Report Model."""

import re
from datetime import (
    date as dateType,
    datetime,
)
from functools import cache
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

_NBSP = " "


def _quarter_end(year: int, quarter: int) -> str:
    """Return the ``YYYYMMDD`` quarter-end date for a year and quarter."""
    month_day = {1: "0331", 2: "0630", 3: "0930", 4: "1231"}[quarter]
    return f"{year}{month_day}"


def _default_period() -> tuple[int, int]:
    """Return the most recent (year, quarter) whose filing is likely available."""
    today = datetime.now().date()
    year = today.year
    quarter = (today.month - 1) // 3 + 1
    for _ in range(6):
        available_month = 3 * quarter + 2
        available_year = year + (available_month - 1) // 12
        available_month = (available_month - 1) % 12 + 1
        if (today.year, today.month) >= (available_year, available_month):
            return year, quarter
        quarter -= 1
        if quarter == 0:
            quarter, year = 4, year - 1
    return year, quarter  # pragma: no cover


def _latest_filed_period(rssd_id: str, report_code: str) -> str | None:
    """Return the firm+report's latest filed ``YYYYMMDD`` period, or None."""
    from openbb_federal_reserve.utils.ffiec import fetch_institution_financial_reports

    try:
        reports = fetch_institution_financial_reports(rssd_id)
    except Exception:  # noqa: BLE001
        return None
    periods = reports.get(report_code, {}).get("periods", [])
    if not periods:
        return None
    latest = periods[0]
    return _quarter_end(int(latest["year"]), int(latest["quarter"]))


def _resolve_period(period: str | None, rssd_id: str, report_code: str) -> str:
    """Resolve a ``YYYYMMDD`` period, defaulting to the latest filed period."""
    text = (period or "").strip()
    if text:
        return text
    filed = _latest_filed_period(rssd_id, report_code)
    if filed:
        return filed
    year, quarter = _default_period()
    return _quarter_end(year, quarter)


@cache
def _load_structure(report_type: str) -> dict[str, Any]:
    """Load a committed report structure (schedules and ordered items)."""
    import json
    from pathlib import Path

    from openbb_federal_reserve.utils.ffiec import READY_REPORTS

    report = READY_REPORTS.get(report_type.upper())
    if report is None:
        raise OpenBBError(
            f"Unknown report_type '{report_type}'. Choose one of:"
            f" {', '.join(READY_REPORTS)}."
        )
    asset = (
        Path(__file__).resolve().parent.parent.parent
        / "assets"
        / report["structure"]
        / "structure.json"
    )
    return json.loads(asset.read_text(encoding="utf-8"))


def _to_number(value: Any) -> float | None:
    """Coerce a filed value to a number, returning None when non-numeric."""
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _column_suffixes(columns: list[str], names: dict[str, str]) -> list[str | None]:
    """Derive a per-column distinguishing label from each column's MDRM name."""
    resolved = [names.get(code) for code in columns]
    present = [name for name in resolved if name]
    if len(present) < 2:
        return [None] * len(columns)
    split = [re.split(r"\s+", name.strip()) for name in present]
    common = 0
    shortest = min(len(words) for words in split)
    while common < shortest and len({words[common] for words in split}) == 1:
        common += 1
    suffixes: list[str | None] = []
    for name in resolved:
        if not name:
            suffixes.append(None)
            continue
        tail = re.split(r"\s+", name.strip())[common:]
        suffixes.append(" ".join(tail).strip(" -;:").title() or name.title())
    return suffixes


def _is_cover_item(item: dict[str, Any]) -> bool:
    """Return ``True`` for an administrative cover/contact submission item."""
    if item["schedule"] == "COVER" or item["schedule_name"] == "Cover Page":
        return True
    return str(item.get("caption", "")).strip().lower().startswith("cover page")


def _render_nodes(
    nodes: list[dict[str, Any]],
) -> list["FederalReserveFinancialReportData"]:
    """Collapse repeated schedule headers, prune empties, and emit rows."""
    collapsed: list[dict[str, Any]] = []
    current_schedule: str | None = None
    for node in nodes:
        if node["kind"] == "schedule":
            if node["name"] != current_schedule:
                current_schedule = node["name"]
                collapsed.append({"kind": "header", "label": node["name"], "level": 0})
            continue
        collapsed.append(node)

    keep = [False] * len(collapsed)
    for index, node in enumerate(collapsed):
        if node["kind"] != "item" or node["value"] is None:
            continue
        keep[index] = True
        needed = node["level"]
        for prior in range(index - 1, -1, -1):
            ancestor = collapsed[prior]
            if ancestor["kind"] != "header" or ancestor["level"] >= needed:
                continue
            keep[prior] = True
            needed = ancestor["level"]
            if needed == 0:
                break

    rows: list[FederalReserveFinancialReportData] = []
    for index, node in enumerate(collapsed):
        if not keep[index]:
            continue
        if node["kind"] == "header":
            rows.append(
                FederalReserveFinancialReportData(label=node["label"], is_header=True)
            )
        else:
            rows.append(
                FederalReserveFinancialReportData(
                    label=node["label"],
                    is_header=False,
                    narrative=node["narrative"],
                    value=node["value"],
                )
            )
    return rows


class FederalReserveFinancialReportQueryParams(QueryParams):
    """Federal Reserve Unified FFIEC Financial Report Query Parameters."""

    __json_schema_extra__ = {
        "rssd_id": {"x-widget_config": {"group": "rssd_id"}},
        "report_type": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": "report_types",
                "optionsParams": {"rssd_id": "$rssd_id"},
                "group": "report_type",
            }
        },
        "section": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": "report_sections",
                "optionsParams": {"report_type": "$report_type"},
            }
        },
        "period": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": "report_periods",
                "optionsParams": {
                    "rssd_id": "$rssd_id",
                    "report_type": "$report_type",
                },
            }
        },
    }

    rssd_id: str = Field(
        description="The reporting institution's RSSD identifier.",
    )
    report_type: str | None = Field(
        default=None,
        description="The regulatory report to render, by its FFIEC report code."
        " Defaults to the firm's first filed report. Cascades off `rssd_id`.",
    )
    section: str | None = Field(
        default=None,
        description="The report schedule to return. When omitted, every schedule is"
        " rendered. Cascades off `report_type`.",
    )
    period: str | None = Field(
        default=None,
        description="The reporting period to render, as a `YYYYMMDD` quarter-end."
        " Defaults to the latest available. Cascades off `rssd_id` and"
        " `report_type`.",
    )


class FederalReserveFinancialReportData(Data):
    """Federal Reserve Unified FFIEC Financial Report Data."""

    label: str = Field(
        description="The line item, indented by the report hierarchy.",
    )
    is_header: bool = Field(
        default=False,
        description="Whether the row is a schedule or sub-section header.",
    )
    narrative: str | None = Field(
        default=None,
        description="The MDRM definition of the line item, shown in a hover card.",
    )
    value: int | float | None = Field(
        default=None,
        description="The reported value for the selected period; dollar amounts are"
        " reported in full U.S. dollars, while rates and counts are as filed.",
    )


class FederalReserveFinancialReportFetcher(
    Fetcher[
        FederalReserveFinancialReportQueryParams,
        list[FederalReserveFinancialReportData],
    ]
):
    """Federal Reserve Unified FFIEC Financial Report Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveFinancialReportQueryParams:
        """Transform the query params."""
        return FederalReserveFinancialReportQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveFinancialReportQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Fetch the institution's per-period report CSV for the report type."""
        from openbb_federal_reserve.utils.ffiec import (
            READY_REPORTS,
            fetch_financial_report,
            fetch_institution_financial_reports,
        )

        report_code = (query.report_type or "").upper()
        if report_code and report_code not in READY_REPORTS:
            raise OpenBBError(
                f"Unknown report_type '{query.report_type}'. Choose one of:"
                f" {', '.join(READY_REPORTS)}."
            )

        rssd_id = str(query.rssd_id).strip()
        try:
            filed = fetch_institution_financial_reports(rssd_id)
        except Exception:  # noqa: BLE001
            filed = {}
        firm_ready = [
            code for code in READY_REPORTS if isinstance(filed, dict) and code in filed
        ]
        if report_code not in firm_ready:
            report_code = firm_ready[0] if firm_ready else (report_code or "FRY9C")

        period = _resolve_period(query.period, rssd_id, report_code)
        report = fetch_financial_report(report_code, rssd_id, period)
        if not report.get("facts"):
            raise EmptyDataError("The request was returned empty.")
        report["report_code"] = report_code
        return report

    @staticmethod
    def transform_data(
        query: FederalReserveFinancialReportQueryParams,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> AnnotatedResult[list[FederalReserveFinancialReportData]]:
        """Render the committed structure as grouped header and line-item rows."""
        from openbb_federal_reserve.utils.mdrm import (
            fetch_mdrm_definitions,
            fetch_mdrm_dictionary,
            fetch_mdrm_item_types,
            is_monetary,
        )

        facts = data["facts"]
        raw_date = data.get("report_date")
        report_date: dateType | None = None
        if isinstance(raw_date, str) and len(raw_date) == 8 and raw_date.isdigit():
            report_date = datetime.strptime(raw_date, "%Y%m%d").date()

        definitions = fetch_mdrm_definitions(as_of=report_date)
        item_names = fetch_mdrm_dictionary(as_of=report_date)
        item_types = fetch_mdrm_item_types()

        report_code = data.get("report_code") or query.report_type or "FRY9C"
        structure = _load_structure(report_code)
        section = (query.section or "").strip().lower()

        def _scaled(code: str) -> int | float | None:
            """Scale a code's filed value: dollar amounts x1000, all else as filed."""
            value = _to_number(facts.get(code))
            if value is None:
                return None
            if is_monetary(code, item_types.get(code)):
                value *= 1000
            return int(value) if value.is_integer() else value  # ty: ignore[unresolved-attribute]

        nodes: list[dict[str, Any]] = []
        for item in structure["items"]:
            if _is_cover_item(item):
                continue
            schedule_name = item["schedule_name"]
            if (
                section
                and item["schedule"].lower() != section
                and (schedule_name.lower() != section)
            ):
                continue
            nodes.append(
                {"kind": "schedule", "name": schedule_name, "level": 0, "item": item}
            )

            level = item.get("level") or 1
            indent = _NBSP * 2 * max(level - 1, 0)
            label = item["caption"]
            label = (">" + indent + label) if indent else label

            if item.get("is_header"):
                nodes.append({"kind": "header", "label": label, "level": level})
                continue

            columns = [
                str(code).upper() for code in (item.get("columns") or [item["mdrm"]])
            ]
            if len(columns) == 1:
                code = columns[0]
                nodes.append(
                    {
                        "kind": "item",
                        "label": label,
                        "level": level,
                        "narrative": definitions.get(code),
                        "value": _scaled(code),
                    }
                )
                continue

            nodes.append({"kind": "header", "label": label, "level": level})
            child_level = level + 1
            child_indent = _NBSP * 2 * max(child_level - 1, 0)
            suffixes = _column_suffixes(columns, item_names)
            for code, suffix in zip(columns, suffixes):
                nodes.append(
                    {
                        "kind": "item",
                        "label": ">" + child_indent + (suffix or code),
                        "level": child_level,
                        "narrative": definitions.get(code),
                        "value": _scaled(code),
                    }
                )

        rows = _render_nodes(nodes)

        if not rows:
            raise EmptyDataError("The request was returned empty.")

        return AnnotatedResult(
            result=rows,
            metadata={
                key: value
                for key, value in {
                    "rssd_id": data.get("rssd_id"),
                    "name": data.get("institution_name"),
                    "report_type": report_code.upper(),
                    "section": query.section,
                    "reporting_date": (
                        report_date.isoformat() if report_date else None
                    ),
                }.items()
                if value
            },
        )

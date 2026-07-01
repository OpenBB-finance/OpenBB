"""Federal Reserve BHCPR (Bank Holding Company Performance Report) Data Model."""

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

_NBSP = " "


def _sections() -> list[str]:
    """Return the BHCPR section titles in the report's table-of-contents order."""
    import json
    from pathlib import Path

    asset = Path(__file__).resolve().parents[2] / "assets" / "bhcpr" / "sections.json"
    return [entry["section"] for entry in json.loads(asset.read_text(encoding="utf-8"))]


def _quarter_end(year: int, quarter: int) -> str:
    """Return the ``YYYYMMDD`` quarter-end date for a year and quarter."""
    month_day = {1: "0331", 2: "0630", 3: "0930", 4: "1231"}[quarter]
    return f"{year}{month_day}"


def _default_period() -> tuple[int, int]:
    """Return the most recent (year, quarter) whose BHCPR is likely available."""
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
    # Unreachable: walking back at most six quarters from any month always lands
    # on a filed quarter, so the loop returns before this fallback.
    return year, quarter  # pragma: no cover


def _resolve_period(period: str | None, filed: list[str]) -> str:
    """Resolve a ``YYYYMMDD`` period, defaulting to the firm's latest filed period.

    A firm files on its own cadence, so the default is its most recent filed
    period-end (``filed`` is newest-first). Only when no filed period is known does
    it fall back to the most recent calendar quarter whose BHCPR is likely out.
    """
    text = (period or "").strip()
    if text:
        return text
    if filed:
        return filed[0]
    year, quarter = _default_period()
    return _quarter_end(year, quarter)


def _filed_periods(rssd: str) -> list[str]:
    """Return a firm's filed BHCPR period-ends as ``YYYYMMDD``, newest first."""
    from openbb_federal_reserve.utils.ffiec import fetch_institution_financial_reports

    if not rssd:
        return []
    try:
        reports = fetch_institution_financial_reports(rssd)
    except Exception:  # noqa: BLE001
        return []
    if not isinstance(reports, dict):
        return []
    return [
        _quarter_end(int(period["year"]), int(period["quarter"]))
        for period in reports.get("BHCPR", {}).get("periods", [])
    ]


class FederalReserveBhcprQueryParams(QueryParams):
    """Federal Reserve BHCPR Data Query Parameters."""

    __json_schema_extra__ = {
        "rssd_id": {"x-widget_config": {"group": "rssd_id"}},
        "section": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": "bhcpr_sections",
            }
        },
        "period": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": "bhcpr_periods",
                "optionsParams": {"rssd_id": "$rssd_id"},
            }
        },
    }

    rssd_id: str = Field(
        description="The reporting holding company's RSSD identifier.",
    )
    section: str | None = Field(
        default="Summary Ratios",
        description="The BHCPR report section to return, by its title. When set to"
        " 'All Sections' every section is rendered.",
    )
    period: str | None = Field(
        default=None,
        description="The reporting period to render, as a `YYYYMMDD` quarter-end."
        " Defaults to the latest available. Cascades off `rssd_id`.",
    )


class FederalReserveBhcprData(Data):
    """Federal Reserve BHCPR Data.

    One row per BHCPR line item, grouped by report section. Section and
    sub-header rows are emitted as ``is_header`` rows carrying no values. Each
    metric row carries the current-period holding-company value (``BHC``), the
    peer-group average (``Peer Group``), and the percentile rank (``Percentile``),
    plus the holding-company value for each prior period as an ISO-date-keyed
    column. Those value columns are dynamic (they vary by report and period) and
    are emitted as extra fields rather than a fixed schema, so the Workspace table
    renders every one under ``showAll`` — a fixed numeric column declared here
    would instead collide with ``showAll`` and drop. Dollar amounts are reported in
    full U.S. dollars; ratios, percents, and ranks are as filed.
    """

    label: str = Field(
        description="The line item, indented under its section or sub-header.",
    )
    is_header: bool = Field(
        default=False,
        description="Whether the row is a section or sub-header.",
    )
    narrative: str | None = Field(
        default=None,
        description="The BHCPR User's Guide definition of the line item, where one"
        " is published; shown in the hover card.",
    )


class FederalReserveBhcprFetcher(
    Fetcher[
        FederalReserveBhcprQueryParams,
        list[FederalReserveBhcprData],
    ]
):
    """Federal Reserve BHCPR Data Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FederalReserveBhcprQueryParams:
        """Transform the query params."""
        return FederalReserveBhcprQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveBhcprQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Fetch and parse the holding company's BHCPR PDF for the period.

        The BHCPR is a holding-company report; a bank RSSD is resolved to its
        top-tier holder (the entity whose BHCPR is published) so the shared firm
        selector never lands on an institution with no report. The period defaults
        to the resolved firm's latest filed period.
        """
        from openbb_federal_reserve.utils.ffiec import (
            fetch_bhcpr,
            resolve_bhcpr_holder,
        )

        rssd = resolve_bhcpr_holder(str(query.rssd_id).strip())
        period = _resolve_period(query.period, _filed_periods(rssd))

        data = fetch_bhcpr(rssd, period)
        if not data.get("sections"):
            raise EmptyDataError("The request was returned empty.")
        return data

    @staticmethod
    def transform_data(
        query: FederalReserveBhcprQueryParams,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> AnnotatedResult[list[FederalReserveBhcprData]]:
        """Render the selected section's header and metric rows."""
        from openbb_federal_reserve.utils.bhcpr_guide import (
            bhcpr_narrative,
            fetch_bhcpr_definitions,
        )

        try:
            guide = fetch_bhcpr_definitions()
        except Exception:  # noqa: BLE001
            guide = {}

        section = (query.section or "").strip()
        select_all = not section or section.lower() == "all sections"
        titles = {
            entry["section"].lower(): entry["section"] for entry in data["sections"]
        }
        if not select_all and section.lower() not in titles:
            raise OpenBBError(
                f"Unknown section '{query.section}'. Choose one of:"
                f" {', '.join(entry['section'] for entry in data['sections'])}."
            )

        period_dates: list[str] = data.get("period_dates", [])
        prior_dates = period_dates[1:]

        value_columns = ["BHC", "Peer Group", "Percentile", *prior_dates]

        def _row(
            label: str, is_header: bool, narrative: str | None, values: dict[str, Any]
        ) -> FederalReserveBhcprData:
            """Build a rectangular row carrying every value column.

            The Workspace derives the table's columns from the first row, so header
            rows must declare the same value columns (as ``None``) as metric rows;
            a ragged header would hide every value column under ``showAll``.
            """
            row: dict[str, Any] = {
                "label": label,
                "is_header": is_header,
                "narrative": narrative,
            }
            for column in value_columns:
                row[column] = values.get(column)
            return FederalReserveBhcprData.model_validate(row)

        rows: list[FederalReserveBhcprData] = []
        for entry in data["sections"]:
            if not select_all and entry["section"].lower() != section.lower():
                continue
            rows.append(_row(entry["section"], True, None, {}))
            for record in entry["rows"]:
                if record["is_header"]:
                    rows.append(_row(_NBSP * 2 + record["label"], True, None, {}))
                    continue
                bank = record["bank"]
                values: dict[str, Any] = {
                    "BHC": bank[0] if bank else None,
                    "Peer Group": record.get("peer"),
                    "Percentile": record.get("percentile"),
                }
                for prior_date, value in zip(prior_dates, bank[1:]):
                    values[prior_date] = value
                rows.append(
                    _row(
                        ">" + _NBSP * 2 + record["label"],
                        False,
                        bhcpr_narrative(guide, entry["section"], record["label"]),
                        values,
                    )
                )

        if not rows:  # pragma: no cover
            # Defensive: ``extract_data`` rejects an empty ``sections`` payload and
            # every rendered section emits at least its header, so this guards only
            # a payload mutated between the two stages.
            raise EmptyDataError("The request was returned empty.")

        identity = data.get("identity", {})
        report_date: dateType | None = None
        if period_dates:
            report_date = datetime.strptime(period_dates[0], "%Y-%m-%d").date()

        return AnnotatedResult(
            result=rows,
            metadata={
                key: value
                for key, value in {
                    "rssd_id": identity.get("rssd_id") or str(query.rssd_id).strip(),
                    "name": identity.get("institution_name"),
                    "city_state": identity.get("city_state"),
                    "section": query.section,
                    "reporting_date": (
                        report_date.isoformat() if report_date else None
                    ),
                }.items()
                if value
            },
        )

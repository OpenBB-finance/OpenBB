"""Federal Reserve FFIEC filed financial-report PDF viewer model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

_QUARTER_END = {1: "0331", 2: "0630", 3: "0930", 4: "1231"}


def _pdf_url(base_url: str, code: str, rssd: str, period: dict[str, Any]) -> str:
    """Return the full ``ReturnFinancialReportPDF`` URL for a period."""
    period_end = f"{period['year']}{_QUARTER_END[period['quarter']]}"
    return (
        f"{base_url}/FinancialReport/ReturnFinancialReportPDF"
        f"?rpt={code}&id={rssd}&dt={period_end}"
    )


def _pdf_choices(rssd_id: str, report_type: str | None) -> list[dict[str, Any]]:
    """Build the filed-PDF choices for a firm.

    With a report type, every filed period of that report is offered, newest
    first, labelled ``"YYYY Qn"``. With no report type, the single most recent
    filed PDF of EACH report the firm files is offered (labelled by report and
    period), so the default view surfaces the latest document of each type.
    """
    from openbb_federal_reserve.utils.ffiec import (
        BASE_URL,
        READY_REPORTS,
        fetch_institution_financial_reports,
    )

    rssd = str(rssd_id).strip()
    if not rssd:
        return []
    reports = fetch_institution_financial_reports(rssd)
    if not isinstance(reports, dict):
        return []

    def _choice(code: str, period: dict[str, Any], named: bool) -> dict[str, Any]:
        """One file choice for a report code and period."""
        stamp = f"{period['year']} Q{period['quarter']}"
        name = (reports.get(code) or {}).get("name") or code
        return {
            "label": f"{name} — {stamp}" if named else stamp,
            "value": _pdf_url(BASE_URL, code, rssd, period),
        }

    code = str(report_type or "").strip().upper()
    if code:
        return [
            _choice(code, period, named=False)
            for period in (reports.get(code) or {}).get("periods", [])
        ]
    choices: list[dict[str, Any]] = []
    for candidate in READY_REPORTS:
        periods = (reports.get(candidate) or {}).get("periods", [])
        if periods:
            choices.append(_choice(candidate, periods[0], named=True))
    return choices


class FederalReserveFinancialReportPdfQueryParams(QueryParams):
    """Federal Reserve FFIEC Filed Financial Report PDF Query Parameters."""

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
    }

    rssd_id: str = Field(
        description="The reporting institution's RSSD identifier.",
    )
    report_type: str | None = Field(
        default=None,
        description="The regulatory report whose filed PDFs are listed, by its"
        " FFIEC report code. When omitted, the latest filed PDF of each report"
        " the firm files is listed. Cascades off `rssd_id`.",
    )


class FederalReserveFinancialReportPdfData(Data):
    """Federal Reserve FFIEC Filed Financial Report PDF Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "FFIEC Filed Financial Report PDFs",
                "$.category": "Federal Reserve",
                "$.subCategory": "FFIEC Reports",
                "$.description": "An institution's filed regulatory financial"
                " reports as PDFs. Select a firm and report type, then choose one"
                " or more filed periods to view.",
                "$.gridData": {"w": 50, "h": 25},
                "$.refetchInterval": False,
                "$.endpoint": "financial_report_pdf_download",
                "$.params": [
                    {
                        "paramName": "rssd_id",
                        "group": "rssd_id",
                    },
                    {
                        "type": "endpoint",
                        "paramName": "report_type",
                        "optionsEndpoint": "report_types",
                        "optionsParams": {"rssd_id": "$rssd_id"},
                        "group": "report_type",
                    },
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": "financial_report_pdf_choices",
                        "optionsParams": {
                            "rssd_id": "$rssd_id",
                            "report_type": "$report_type",
                        },
                        "show": False,
                        "multiSelect": True,
                        "roles": ["fileSelector"],
                    },
                ],
                "$.data": {},
            }
        }
    )

    rssd_id: str = Field(description="The reporting institution's RSSD identifier.")
    report_type: str = Field(description="The FFIEC report code.")
    year: int = Field(description="The report year.")
    quarter: int = Field(description="The report quarter, from 1 to 4.")
    label: str = Field(description="The filed-period label.")
    url: str = Field(description="The filed report PDF URL.")


class FederalReserveFinancialReportPdfFetcher(
    Fetcher[
        FederalReserveFinancialReportPdfQueryParams,
        list[FederalReserveFinancialReportPdfData],
    ]
):
    """Federal Reserve FFIEC Filed Financial Report PDF Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveFinancialReportPdfQueryParams:
        """Transform the query parameters."""
        return FederalReserveFinancialReportPdfQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveFinancialReportPdfQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """List the firm's filed PDFs: a report's periods, or the latest of each."""
        from openbb_federal_reserve.utils.ffiec import (
            BASE_URL,
            READY_REPORTS,
            fetch_institution_financial_reports,
        )

        rssd = str(query.rssd_id).strip()
        reports = fetch_institution_financial_reports(rssd)
        if not isinstance(reports, dict):
            raise EmptyDataError("The request was returned empty.")

        def _row(code: str, period: dict[str, Any], named: bool) -> dict[str, Any]:
            """One PDF row for a report code and period."""
            stamp = f"{period['year']} Q{period['quarter']}"
            name = (reports.get(code) or {}).get("name") or code
            return {
                "rssd_id": rssd,
                "report_type": code,
                "year": int(period["year"]),
                "quarter": int(period["quarter"]),
                "label": f"{name} — {stamp}" if named else stamp,
                "url": _pdf_url(BASE_URL, code, rssd, period),
            }

        code = str(query.report_type or "").strip().upper()
        rows: list[dict[str, Any]] = []
        if code:
            rows = [
                _row(code, period, named=False)
                for period in (reports.get(code) or {}).get("periods", [])
            ]
        else:
            for candidate in READY_REPORTS:
                periods = (reports.get(candidate) or {}).get("periods", [])
                if periods:
                    rows.append(_row(candidate, periods[0], named=True))
        if not rows:
            raise EmptyDataError("The request was returned empty.")
        return rows

    @staticmethod
    def transform_data(
        query: FederalReserveFinancialReportPdfQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[FederalReserveFinancialReportPdfData]:
        """Sort newest-first and validate to the data model."""
        ordered = sorted(
            data, key=lambda row: (row["year"], row["quarter"]), reverse=True
        )
        return [
            FederalReserveFinancialReportPdfData.model_validate(row) for row in ordered
        ]

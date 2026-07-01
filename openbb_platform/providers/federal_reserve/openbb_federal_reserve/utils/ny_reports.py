"""New York Fed survey full-report (PDF) helpers.

The Business Leaders Survey publishes a full PDF report per monthly release. The
report links (with their Sitecore hash query strings) are listed on the survey
overview page; this module discovers them and serves a selected report as a
base64-encoded PDF suitable for an OpenBB Workspace PDF widget.
"""

from __future__ import annotations

from typing import Any

BASE_URL = "https://www.newyorkfed.org"
OVERVIEW_URL = f"{BASE_URL}/survey/business_leaders/bls_overview"
SUPPLEMENTAL_URL = f"{BASE_URL}/survey/business_leaders/supplemental_survey_report"


def list_business_leaders_reports() -> list[dict[str, str]]:
    """Return available Business Leaders Survey reports as period/url records."""
    import re

    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, str]]:
        """Scrape the survey overview page for report PDF links."""
        response = make_request(OVERVIEW_URL)
        response.raise_for_status()
        pattern = (
            r"(/medialibrary/media/survey/business_leaders/\d{4}/"
            r"[^\"']*blsreport\.pdf[^\"']*)"
        )
        reports: dict[str, str] = {}
        for match in re.finditer(pattern, response.text, re.IGNORECASE):
            href = match.group(1).replace("&amp;", "&")
            filename = href.rsplit("/", 1)[-1]
            period_match = re.match(r"(\d{4})[-_]?(\d{2})", filename)
            if period_match:
                period = period_match.group(1) + period_match.group(2)
                reports[period] = f"{BASE_URL}{href}"
        return [
            {"period": period, "url": url}
            for period, url in sorted(reports.items(), reverse=True)
        ]

    return cached(
        "ny_bls_reports", lambda: seconds_until_next_release("monthly"), _producer
    )


def fetch_business_leaders_report(period: str | None = None) -> dict[str, Any]:
    """Return a Business Leaders Survey report as a base64-encoded PDF payload."""
    import base64

    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    reports = list_business_leaders_reports()
    if not reports:
        raise OpenBBError("No Business Leaders Survey reports are available.")

    selected = reports[0]
    if period:
        selected = next((r for r in reports if r["period"] == period), None)  # type: ignore[assignment]
        if not selected:
            raise OpenBBError(
                f"No Business Leaders Survey report for period '{period}'."
            )

    def _producer() -> str:
        """Download and base64-encode the selected report PDF."""
        response = make_request(selected["url"])
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

    content = cached(
        ("ny_bls_report", selected["period"]),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    return {
        "content": content,
        "data_format": {
            "data_type": "pdf",
            "filename": f"NY_BLS_{selected['period']}.pdf",
        },
    }


def list_business_leaders_supplemental_reports() -> list[dict[str, str]]:
    """Return available Business Leaders Supplemental reports, newest first."""
    import re

    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, str]]:
        """Scrape the supplemental report page for the PDF links."""
        response = make_request(SUPPLEMENTAL_URL)
        response.raise_for_status()
        pattern = (
            r"(/medialibrary/media/[Ss]urvey/business_leaders/\d{4}/"
            r"[^\"']*supplemental\.pdf[^\"']*)"
        )
        reports: dict[str, str] = {}
        for match in re.finditer(pattern, response.text, re.IGNORECASE):
            href = match.group(1).replace("&amp;", "&")
            filename = href.split("?")[0].rsplit("/", 1)[-1]
            period_match = re.match(r"(\d{4})[-_]?(\d{2})", filename)
            if period_match:
                period = period_match.group(1) + period_match.group(2)
                reports[period] = f"{BASE_URL}{href}"
        return [
            {"period": period, "url": url}
            for period, url in sorted(reports.items(), reverse=True)
        ]

    return cached(
        "ny_bls_supplemental_reports",
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )


def fetch_business_leaders_supplemental_report(
    period: str | None = None,
) -> dict[str, Any]:
    """Return a Business Leaders Supplemental report as a base64 PDF payload."""
    import base64

    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    reports = list_business_leaders_supplemental_reports()
    if not reports:
        raise OpenBBError("No Business Leaders Supplemental reports are available.")

    selected = reports[0]
    if period:
        selected = next((r for r in reports if r["period"] == period), None)  # type: ignore[assignment]
        if not selected:
            raise OpenBBError(
                f"No Business Leaders Supplemental report for period '{period}'."
            )

    def _producer() -> str:
        """Download and base64-encode the selected supplemental report PDF."""
        response = make_request(selected["url"])
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

    content = cached(
        ("ny_bls_supplemental_report", selected["period"]),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    return {
        "content": content,
        "data_format": {
            "data_type": "pdf",
            "filename": f"NY_BLS_Supplemental_{selected['period']}.pdf",
        },
    }

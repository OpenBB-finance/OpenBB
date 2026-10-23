"""BLS Employment Situation news-release chart-data scrapers.

Source: https://www.bls.gov/charts/employment-situation/

Each chart page embeds its data as an HTML ``<table class="regular">`` (the
page's "Show table" content). The package mixes two shapes:

* ``ts`` — a monthly time series: a ``Month`` stub column plus one column per
  plotted series (unemployment rates, levels, hours, ...).
* ``industry`` — an industry cross-section for the latest release: an
  ``Industry`` stub column plus metric columns (net changes, confidence
  intervals, earnings, employment levels).
"""

from __future__ import annotations

import calendar
import re
from datetime import date as dateType
from functools import lru_cache
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_bls.utils.constants import BLS_USER_AGENT

_BASE = "https://www.bls.gov/charts/employment-situation"
_HEADERS = {
    "User-Agent": BLS_USER_AGENT,
    "Accept": "text/html,*/*",
}

_MONTH_LOOKUP: dict[str, int] = {}
for _m in range(1, 13):
    _MONTH_LOOKUP[calendar.month_abbr[_m].lower()] = _m
    _MONTH_LOOKUP[calendar.month_name[_m].lower()] = _m
_MONTH_LOOKUP["sept"] = 9

_MONTH_RE = re.compile(r"([A-Za-z]{3,9})\.?\s+(\d{4})")

_DEMOGRAPHICS = (
    ("total", "Total", "num"),
    ("men_20_over", "Men, 20 years and over", "num"),
    ("women_20_over", "Women, 20 years and over", "num"),
    ("age_16_19", "16 to 19 years old", "num"),
    ("white", "White", "num"),
    ("black", "Black or African American", "num"),
    ("asian", "Asian", "num"),
    ("hispanic", "Hispanic or Latino", "num"),
)

# Per-chart spec: slug, human label, kind (ts|industry), default chart type,
# and the ordered value columns as (field_name, BLS header, role). Role drives
# column formatting: num -> plain number, change -> greenRed number, pct ->
# greenRed percent.
CHART_SPECS: dict[str, dict[str, Any]] = {
    "civilian-unemployment-rate": {
        "slug": "civilian-unemployment-rate",
        "label": "Civilian Unemployment Rate",
        "kind": "ts",
        "chart_type": "line",
        "fields": _DEMOGRAPHICS,
    },
    "civilian-unemployment": {
        "slug": "civilian-unemployment",
        "label": "Civilian Unemployment (Level)",
        "kind": "ts",
        "chart_type": "line",
        "fields": _DEMOGRAPHICS,
    },
    "unemployment-by-education": {
        "slug": "unemployment-rates-for-persons-25-years-and-older-by-educational-attainment",
        "label": "Unemployment Rates by Educational Attainment (25+)",
        "kind": "ts",
        "chart_type": "line",
        "fields": (
            ("less_than_high_school", "Less than a high school diploma", "num"),
            ("high_school_no_college", "High school graduates, no college", "num"),
            ("some_college", "Some college or associate degree", "num"),
            ("bachelors_or_higher", "Bachelor's degree and higher", "num"),
        ),
    },
    "unemployment-by-veteran-status": {
        "slug": "unemployment-rates-for-persons-18-years-and-older-by-veteran-status",
        "label": "Unemployment Rates by Veteran Status (18+)",
        "kind": "ts",
        "chart_type": "line",
        "fields": (
            ("total_veterans", "Total veterans", "num"),
            ("veteran_men", "Veteran men", "num"),
            ("veteran_women", "Veteran women", "num"),
            ("gulf_war_era_1", "Gulf War-era I veterans", "num"),
            ("gulf_war_era_2", "Gulf War-era II veterans", "num"),
            (
                "wwii_korea_vietnam",
                "World War II, Korean War, and Vietnam-era veterans",
                "num",
            ),
            ("other_service_veterans", "Veterans of other service periods", "num"),
            ("total_nonveterans", "Total nonveterans", "num"),
            ("nonveteran_men", "Nonveteran men", "num"),
            ("nonveteran_women", "Nonveteran women", "num"),
        ),
    },
    "reasons-for-unemployment": {
        "slug": "reasons-for-unemployment",
        "label": "Reasons for Unemployment",
        "kind": "ts",
        "chart_type": "line",
        "fields": (
            (
                "job_losers_and_completed_temp",
                "Job losers and people who completed temporary jobs",
                "num",
            ),
            ("job_losers_not_on_layoff", "Job losers not on temporary layoff", "num"),
            ("job_losers_on_temp_layoff", "Job losers on temporary layoff", "num"),
            ("job_leavers", "Job leavers", "num"),
            ("reentrants", "Reentrants", "num"),
            ("new_entrants", "New entrants", "num"),
        ),
    },
    "duration-of-unemployment": {
        "slug": "duration-of-unemployment",
        "label": "Duration of Unemployment",
        "kind": "ts",
        "chart_type": "line",
        "fields": (
            ("less_than_5_weeks", "Less than 5 weeks", "num"),
            ("weeks_5_to_14", "5-14 weeks", "num"),
            ("weeks_15_to_26", "15-26 weeks", "num"),
            ("weeks_27_and_over", "27 weeks and over", "num"),
        ),
    },
    "long-term-unemployed-share": {
        "slug": "unemployed-27-weeks-or-longer-as-a-percent-of-total-unemployed",
        "label": "Unemployed 27 Weeks or Longer as a Percent of Total Unemployed",
        "kind": "ts",
        "chart_type": "line",
        "fields": (("percent", "Percent", "num"),),
    },
    "labor-underutilization": {
        "slug": "alternative-measures-of-labor-underutilization",
        "label": "Alternative Measures of Labor Underutilization (U-1 to U-6)",
        "kind": "ts",
        "chart_type": "line",
        "fields": (
            (
                "u_1",
                "U-1, people unemployed 15 weeks or longer, as a percent of the civilian labor force",
                "num",
            ),
            (
                "u_2",
                "U-2, job losers and people who completed temporary jobs, as a percent of the civilian labor force",
                "num",
            ),
            (
                "u_3",
                "U-3, total unemployed, as a percent of the civilian labor force (official unemployment rate)",
                "num",
            ),
            (
                "u_4",
                "U-4, total unemployed plus discouraged workers, as a percent of the civilian labor force plus discouraged workers",
                "num",
            ),
            (
                "u_5",
                "U-5, total unemployed, plus discouraged workers, plus all other marginally attached workers, as a percent of the civilian labor force plus all marginally attached workers",
                "num",
            ),
            (
                "u_6",
                "U-6, total unemployed, plus all marginally attached workers, plus total employed part time for economic reasons, as a percent of the civilian labor force plus all marginally attached workers",
                "num",
            ),
        ),
    },
    "labor-force-participation-rate": {
        "slug": "civilian-labor-force-participation-rate",
        "label": "Civilian Labor Force Participation Rate",
        "kind": "ts",
        "chart_type": "line",
        "fields": _DEMOGRAPHICS,
    },
    "employment-population-ratio": {
        "slug": "employment-population-ratio",
        "label": "Employment-Population Ratio",
        "kind": "ts",
        "chart_type": "line",
        "fields": _DEMOGRAPHICS,
    },
    "civilian-employment": {
        "slug": "civilian-employment",
        "label": "Civilian Employment (Level)",
        "kind": "ts",
        "chart_type": "line",
        "fields": (
            ("total", "Total", "num"),
            ("nonag_wage_and_salary", "Nonagricultural wage and salary", "num"),
            ("nonag_self_employment", "Nonagricultural self-employment", "num"),
            ("employed_part_time", "Employed part time", "num"),
        ),
    },
    "not-in-labor-force-want-a-job": {
        "slug": "persons-not-in-the-labor-force-who-want-a-job",
        "label": "People Not in the Labor Force Who Want a Job",
        "kind": "ts",
        "chart_type": "line",
        "fields": (("thousands", "Thousands", "num"),),
    },
    "not-in-labor-force-indicators": {
        "slug": "persons-not-in-the-labor-force-selected-indicators",
        "label": "People Not in the Labor Force, Selected Indicators",
        "kind": "ts",
        "chart_type": "line",
        "fields": (
            ("marginally_attached", "Marginally attached", "num"),
            ("discouraged", "Discouraged", "num"),
        ),
    },
    "employment-levels-by-industry": {
        "slug": "employment-levels-by-industry",
        "label": "Employment Levels by Industry",
        "kind": "ts",
        "chart_type": "line",
        "fields": (
            # Grand totals stay in the table but are excluded from the chart
            ("total_nonfarm", "Total nonfarm", "exclude"),
            ("total_private", "Total private", "exclude"),
            ("mining_and_logging", "Mining and logging", "num"),
            ("construction", "Construction", "num"),
            ("manufacturing", "Manufacturing", "num"),
            ("wholesale_trade", "Wholesale trade", "num"),
            ("retail_trade", "Retail trade", "num"),
            ("transportation_and_warehousing", "Transportation and warehousing", "num"),
            ("utilities", "Utilities", "num"),
            ("information", "Information", "num"),
            ("financial_activities", "Financial activities", "num"),
            (
                "professional_and_business_services",
                "Professional and business services",
                "num",
            ),
            (
                "private_education_and_health_services",
                "Private education and health services",
                "num",
            ),
            ("leisure_and_hospitality", "Leisure and hospitality", "num"),
            ("other_services", "Other services", "num"),
            ("government", "Government", "num"),
            ("federal_government", "Federal government", "num"),
            ("state_government", "State government", "num"),
            ("local_government", "Local government", "num"),
        ),
    },
    "average-weekly-hours-production": {
        "slug": "average-weekly-hours-of-production-employees",
        "label": "Average Weekly Hours of Production Employees in Manufacturing",
        "kind": "ts",
        "chart_type": "line",
        "fields": (
            ("manufacturing", "Manufacturing", "num"),
            ("durable_goods", "Durable goods", "num"),
            ("wood_product", "Wood product manufacturing", "num"),
            ("nonmetallic_mineral", "Nonmetallic mineral product manufacturing", "num"),
            ("primary_metal", "Primary metal manufacturing", "num"),
            ("fabricated_metal", "Fabricated metal product manufacturing", "num"),
            ("machinery", "Machinery manufacturing", "num"),
            (
                "computer_electronic",
                "Computer and electronic product manufacturing",
                "num",
            ),
            (
                "electrical_equipment",
                "Electrical equipment, appliance, and component manufacturing",
                "num",
            ),
            (
                "transportation_equipment",
                "Transportation equipment manufacturing",
                "num",
            ),
            ("furniture", "Furniture and related product manufacturing", "num"),
            ("miscellaneous", "Miscellaneous manufacturing", "num"),
            ("nondurable_goods", "Nondurable goods", "num"),
            ("food", "Food manufacturing", "num"),
            ("textile_mills", "Textile product mills", "num"),
            ("paper", "Paper manufacturing", "num"),
            ("printing", "Printing and related support activities", "num"),
            ("chemical", "Chemical manufacturing", "num"),
            (
                "plastics_and_rubber",
                "Plastics and rubber products manufacturing",
                "num",
            ),
        ),
    },
    "employment-change-by-industry-ci": {
        "slug": "otm-employment-change-by-industry-confidence-intervals",
        "label": "Employment Change by Industry With Confidence Intervals",
        "kind": "industry",
        "chart_type": "column",
        "fields": (
            ("net_change_1month", "1-month net change", "change"),
            ("ci_1month", "1-month 90-percent confidence interval", "num"),
            ("net_change_3month", "3-month net change", "change"),
            ("ci_3month", "3-month 90-percent confidence interval", "num"),
            ("net_change_6month", "6-month net change", "change"),
            ("ci_6month", "6-month 90-percent confidence interval", "num"),
            ("net_change_12month", "12-month net change", "change"),
            ("ci_12month", "12-month 90-percent confidence interval", "num"),
        ),
    },
    "employment-by-industry-monthly-changes": {
        "slug": "employment-by-industry-monthly-changes",
        "label": "Employment by Industry, Monthly Changes",
        "kind": "industry",
        "chart_type": "column",
        "fields": (
            ("employed", "Employed (thousands)", "num"),
            ("net_change_1month", "1-month net change (thousands)", "change"),
            ("pct_change_1month", "1-month percent change", "pct"),
            ("net_change_3month", "3-month net change (thousands)", "change"),
            ("pct_change_3month", "3-month percent change", "pct"),
            ("net_change_6month", "6-month net change (thousands)", "change"),
            ("pct_change_6month", "6-month percent change", "pct"),
            ("net_change_12month", "12-month net change (thousands)", "change"),
            ("pct_change_12month", "12-month percent change", "pct"),
        ),
    },
    "employment-and-hourly-earnings-by-industry": {
        "slug": "employment-and-average-hourly-earnings-by-industry-bubble",
        "label": "Employment and Average Hourly Earnings by Industry",
        "kind": "industry",
        "chart_type": "scatter",
        "fields": (
            (
                "otm_change_employment",
                "Over-the-month-change in employment (in thousands)",
                "change",
            ),
            ("average_hourly_earnings", "Average hourly earnings", "num"),
            ("employment_level", "Employment level (in thousands)", "num"),
        ),
    },
    "employment-and-weekly-earnings-by-industry": {
        "slug": "employment-and-average-weekly-earnings-by-industry-bubble",
        "label": "Employment and Average Weekly Earnings by Industry",
        "kind": "industry",
        "chart_type": "scatter",
        "fields": (
            (
                "otm_change_employment",
                "Over-the-month-change in employment (in thousands)",
                "change",
            ),
            ("average_weekly_earnings", "Average weekly earnings", "num"),
            ("employment_level", "Employment level (in thousands)", "num"),
        ),
    },
}


def _decode(content: bytes) -> str:
    """Decode HTML bytes, falling back to latin-1."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="replace")


@lru_cache(maxsize=len(CHART_SPECS))
def fetch_chart_html(slug: str) -> str:
    """Download one employment-situation chart page as decoded HTML."""
    import requests

    url = f"{_BASE}/{slug}.htm"
    resp = requests.get(url, headers=_HEADERS, timeout=30)
    if resp.status_code != 200:
        raise OpenBBError(f"BLS returned HTTP {resp.status_code} fetching {url}.")
    return _decode(resp.content)


def _parse_month(text: str) -> dateType | None:
    """Parse a ``Mon YYYY`` stub cell into a first-of-month date."""
    match = _MONTH_RE.search(text or "")
    if match is None:
        return None
    month = _MONTH_LOOKUP.get(match.group(1).strip().lower().rstrip("."))
    if month is None:
        return None
    return dateType(int(match.group(2)), month, 1)


def _to_num(text: Any) -> float | None:
    """Coerce a numeric cell (commas, optional %) into a float; blanks -> None."""
    if text is None:
        return None
    cleaned = (
        str(text).replace("\xa0", " ").strip().rstrip("%").replace(",", "").strip()
    )
    if cleaned in ("", "(NA)", "NA", "N/A", "-", "--"):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_chart_table(html: str, chart_key: str) -> dict[str, Any]:
    """Parse one chart page's data table into wide rows keyed by the chart's fields.

    Time-series charts key the stub column as ``date``; industry cross-sections
    key it as ``industry``. Either way each value column is named from the
    chart's ``CHART_SPECS`` entry so a typed model can declare and format it.
    """
    from bs4 import BeautifulSoup

    spec = CHART_SPECS[chart_key]
    is_ts = spec["kind"] == "ts"
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="regular")
    if table is None:
        raise OpenBBError(
            f"BLS employment-situation chart '{chart_key}' page has no data table."
        )
    caption = table.find("caption")
    chart_title = (
        " ".join(caption.get_text(" ", strip=True).split())
        if caption is not None
        else spec["label"]
    )
    fields = spec["fields"]
    body = table.find("tbody")
    rows = body.find_all("tr") if body is not None else []
    table_id = table.get("id") or f"empsit-chart-{chart_key}"

    out: list[dict[str, Any]] = []
    for tr in rows:
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        stub = cells[0].get_text(" ", strip=True)
        record: dict[str, Any] = {
            "chart": chart_key,
            "chart_title": chart_title,
            "table_id": table_id,
        }
        if is_ts:
            period = _parse_month(stub)
            if period is None:
                continue
            record["date"] = period
        else:
            industry = " ".join(stub.split())
            if not industry:
                continue
            record["industry"] = industry
        for col, (field, _label, _role) in enumerate(fields, start=1):
            record[field] = (
                _to_num(cells[col].get_text(" ", strip=True))
                if col < len(cells)
                else None
            )
        out.append(record)
    return {"rows": out, "table_id": table_id, "chart_title": chart_title}


def fetch_and_parse(chart_key: str) -> dict[str, Any]:
    """Resolve a chart key to its slug, download, and parse the data table."""
    slug = CHART_SPECS[chart_key]["slug"]
    return parse_chart_table(fetch_chart_html(slug), chart_key)

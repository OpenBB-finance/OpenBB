"""BLS Job Openings and Labor Turnover (JOLTS) news-release chart-data scrapers.

Source: https://www.bls.gov/charts/job-openings-and-labor-turnover/

Chart specs (slug / label / kind / value columns) are generated from the live
table headers and bundled in ``assets/charts/jolts.json``. Every chart is a
monthly time series.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openbb_bls.utils.charts_common import make_html_fetcher, parse_chart_table

_BASE = "https://www.bls.gov/charts/job-openings-and-labor-turnover"
_SPECS_FILE = Path(__file__).parent.parent / "assets" / "charts" / "jolts.json"

CHART_SPECS: dict[str, dict[str, Any]] = json.loads(
    _SPECS_FILE.read_text(encoding="utf-8")
)

fetch_chart_html = make_html_fetcher(_BASE, maxsize=len(CHART_SPECS))


def fetch_and_parse(chart_key: str) -> dict[str, Any]:
    """Resolve a chart key to its slug, download, and parse the data table."""
    slug = CHART_SPECS[chart_key]["slug"]
    return parse_chart_table(
        fetch_chart_html(slug),
        chart_key,
        CHART_SPECS,
        period="month",
        error_label="job-openings-and-labor-turnover",
        table_id_prefix="jolts-chart",
    )

"""BLS Job Openings and Labor Turnover (JOLTS) chart data (per-chart tables)."""

from __future__ import annotations

from openbb_core.provider.abstract.fetcher import Fetcher

from openbb_bls.models.charts_common import build_chart_pack
from openbb_bls.utils.jolts_charts import CHART_SPECS, fetch_and_parse


def jolts_chart_model_name(chart_key: str) -> str:
    """Stable widget/model name for one JOLTS chart key."""
    return "BlsJolts" + "".join(p.capitalize() for p in chart_key.split("-"))


JOLTS_CHART_FETCHERS: dict[str, type[Fetcher]] = build_chart_pack(
    specs=CHART_SPECS,
    fetch_and_parse=fetch_and_parse,
    model_name_fn=jolts_chart_model_name,
    model_id_prefix="BlsJoltsChart",
    widget_name_prefix="BLS Job Openings & Labor Turnover",
    subcategory="Job Openings & Labor Turnover",
    pack_label="Job Openings and Labor Turnover",
    period_header="Month",
)

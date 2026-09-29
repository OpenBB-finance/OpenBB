"""BLS Total Factor Productivity news-release chart data (per-chart tables)."""

from __future__ import annotations

from openbb_core.provider.abstract.fetcher import Fetcher

from openbb_bls.models.charts_common import build_chart_pack
from openbb_bls.utils.tfp_charts import CHART_SPECS, fetch_and_parse


def tfp_model_name(chart_key: str) -> str:
    """Stable widget/model name for one Total Factor Productivity chart key."""
    return "Bls" + "".join(p.capitalize() for p in chart_key.split("-"))


TFP_CHART_FETCHERS: dict[str, type[Fetcher]] = build_chart_pack(
    specs=CHART_SPECS,
    fetch_and_parse=fetch_and_parse,
    model_name_fn=tfp_model_name,
    model_id_prefix="BlsTfp",
    widget_name_prefix="BLS Total Factor Productivity",
    subcategory="Total Factor Productivity",
    pack_label="Total Factor Productivity",
    period_header="Year",
)

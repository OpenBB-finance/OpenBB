"""BLS Mining & Manufacturing Productivity chart data (per-chart tables)."""

from __future__ import annotations

from openbb_core.provider.abstract.fetcher import Fetcher

from openbb_bls.models.charts_common import build_chart_pack
from openbb_bls.utils.mining_manufacturing_charts import CHART_SPECS, fetch_and_parse


def mining_manufacturing_model_name(chart_key: str) -> str:
    """Stable widget/model name for one mining/manufacturing productivity chart key."""
    return "Bls" + "".join(p.capitalize() for p in chart_key.split("-"))


MINING_MANUFACTURING_CHART_FETCHERS: dict[str, type[Fetcher]] = build_chart_pack(
    specs=CHART_SPECS,
    fetch_and_parse=fetch_and_parse,
    model_name_fn=mining_manufacturing_model_name,
    model_id_prefix="BlsMm",
    widget_name_prefix="BLS Mining & Manufacturing Productivity",
    subcategory="Productivity by Industry",
    pack_label="Mining & Manufacturing Productivity",
    period_header="Year",
)

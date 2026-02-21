"""HTML report builder for standardized run artifacts."""

from __future__ import annotations

from typing import Any


def build_report_html(payload: dict[str, Any]) -> str:
    """Render a minimal static report page."""
    run_id = str(payload.get("run_id", "unknown"))
    run_uid = str(payload.get("run_uid", "unknown"))
    model = str(payload.get("model_name", "lgbm_ranker"))
    metrics = payload.get("metrics", {}) if isinstance(payload, dict) else {}
    sharpe = float(metrics.get("sharpe", 0.0) or 0.0) if isinstance(metrics, dict) else 0.0
    cagr = float(metrics.get("cagr", 0.0) or 0.0) if isinstance(metrics, dict) else 0.0
    max_dd = float(metrics.get("max_drawdown", 0.0) or 0.0) if isinstance(metrics, dict) else 0.0
    return (
        "<html><head><meta charset='utf-8'><title>Quant ML Report</title></head>"
        "<body>"
        f"<h1>Quant ML Run Report</h1>"
        f"<p><b>run_id</b>: {run_id}</p>"
        f"<p><b>run_uid</b>: {run_uid}</p>"
        f"<p><b>model</b>: {model}</p>"
        "<h2>Metrics</h2>"
        f"<p>Sharpe: {sharpe:.4f}</p>"
        f"<p>CAGR: {cagr:.4f}</p>"
        f"<p>Max Drawdown: {max_dd:.4f}</p>"
        "</body></html>"
    )


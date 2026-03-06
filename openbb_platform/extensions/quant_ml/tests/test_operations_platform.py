"""Operational platform service tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from openbb_quant_ml.service import data_lake, data_quality, notification_center, reporting
from openbb_quant_ml.service.registry import run_registry_db as registry_db


def _isolate_ops_storage(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        registry_db,
        "RUN_REGISTRY_DB_PATH",
        tmp_path / "run_registry.sqlite3",
    )
    monkeypatch.setattr(reporting, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(
        data_lake,
        "_LAYER_DIRS",
        {
            "bronze": tmp_path / "lake" / "bronze",
            "silver": tmp_path / "lake" / "silver",
            "gold": tmp_path / "lake" / "gold",
        },
    )


def test_quality_gate_persists_reports_and_blocks_critical(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _isolate_ops_storage(monkeypatch, tmp_path)
    run_id = "run-ops"
    previous = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2026-03-04", "2026-03-04", "2026-03-05", "2026-03-05"]
            ),
            "symbol": ["AAA", "BBB", "AAA", "BBB"],
            "close": [100.0, 101.0, 102.0, 103.0],
            "volume": [10_000, 8_000, 10_500, 8_100],
        }
    )
    previous_meta = data_lake.write_lake_dataset(
        layer="silver",
        dataset="equity_ohlcv",
        frame=previous,
        as_of_date="2026-03-05",
        run_id=run_id,
        metadata={"symbols": ["AAA", "BBB"], "expected_symbols": ["AAA", "BBB"]},
    )
    data_quality.register_dataset_snapshot(previous_meta)

    current = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-03-06", "2026-03-06"]),
            "symbol": ["AAA", "AAA"],
            "close": [103.5, 104.0],
        }
    )
    current_meta = data_lake.write_lake_dataset(
        layer="silver",
        dataset="equity_ohlcv",
        frame=current,
        as_of_date="2026-03-06",
        run_id=run_id,
        metadata={"symbols": ["AAA"], "expected_symbols": ["AAA", "BBB"]},
    )
    data_quality.register_dataset_snapshot(current_meta)

    result = data_quality.run_quality_gate(
        run_id=run_id,
        gate_name="silver_to_gold",
        dataset_name="equity_ohlcv",
        layer="silver",
        frame=current,
        as_of_date="2026-03-06",
        snapshot_meta=current_meta,
    )

    assert result.qc_status == "CRITICAL"
    assert result.report_path is not None
    assert Path(result.report_path).exists()
    assert data_quality.should_block_on_quality(result.qc_status) is True

    latest = data_quality.get_latest_data_quality_response(run_id=run_id)
    assert latest.run_id == run_id
    assert latest.qc_status == "CRITICAL"

    history = data_quality.get_data_quality_history_response(run_id=run_id, limit=10)
    assert len(history.items) == 1
    assert history.items[0].summary.get("dataset_name") == "equity_ohlcv"

    latest_report = reporting.get_reports_latest_response(
        run_id=run_id,
        report_type="data_quality",
    )
    assert latest_report.item is not None
    assert latest_report.item.report_type == "data_quality"


def test_notification_center_dedupes_and_persists_history(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _isolate_ops_storage(monkeypatch, tmp_path)
    sent_payloads: list[dict[str, object]] = []

    monkeypatch.setattr(
        notification_center,
        "_enabled_channels",
        lambda explicit=None: ["slack"],
    )
    monkeypatch.setitem(
        notification_center._CHANNEL_SENDERS,
        "slack",
        lambda payload: sent_payloads.append(payload),
    )

    first = notification_center.dispatch_notification(
        run_id="run-ops",
        event_type="risk.exceeded",
        title="Risk exceeded",
        body="Portfolio volatility crossed the configured limit.",
    )
    second = notification_center.dispatch_notification(
        run_id="run-ops",
        event_type="risk.exceeded",
        title="Risk exceeded",
        body="Portfolio volatility crossed the configured limit.",
    )

    assert first[0]["status"] == "sent"
    assert second[0]["status"] == "duplicate"
    assert len(sent_payloads) == 1

    history = notification_center.get_notifications_history_response(limit=10)
    statuses = {item.status for item in history.items}
    assert "sent" in statuses
    assert "duplicate" in statuses

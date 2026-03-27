"""Macro study and vintage service tests."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from openbb_quant_ml.macro_models import MacroStudyPayload
from openbb_quant_ml.service import macro_service as ms


def test_compare_release_and_feature_export(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    study = MacroStudyPayload(
        id="study-1",
        name="Labor and Inflation Monitor",
        objective="Track regime shifts.",
        series_specs=[
            {
                "key": "FRED:UNRATE",
                "alias": "Unemployment",
                "transform_chain": [],
                "freq": "M",
                "fill": "ffill",
                "axis": "left",
                "normalize_mode": "raw",
                "lag_mode": None,
                "display_style": "line",
            },
            {
                "key": "FRED:CPIAUCSL",
                "alias": "CPI",
                "transform_chain": ["yoy"],
                "freq": "M",
                "fill": "ffill",
                "axis": "right",
                "normalize_mode": "yoy",
                "lag_mode": None,
                "display_style": "line",
            },
        ],
        view_specs=[],
        notes="Draft note",
        conclusion={"summary": "Cooling labor", "thesis": "Growth is slowing"},
        linked_assets=["SPY", "TLT"],
    )

    idx = pd.date_range("2024-01-31", periods=12, freq="ME")
    monkeypatch.setattr(ms, "get_macro_study", lambda study_id: study.model_dump() if study_id == "study-1" else None)
    monkeypatch.setattr(ms, "MACRO_ROOT", tmp_path / "macro")

    def _series_loader(key: str, start=None, end=None, as_of_date=None):  # noqa: ANN001
        values = np.linspace(3.5, 4.6, len(idx)) if key == "FRED:UNRATE" else np.linspace(300.0, 315.0, len(idx))
        return (
            pd.Series(values, index=idx, dtype=float),
            {
                "key": key,
                "title": key,
                "units": "level",
                "frequency": "monthly",
                "source": "FRED",
                "lag_applied": "P1M",
            },
            None,
        )

    monkeypatch.setattr(ms, "_get_series_asof", _series_loader)

    compare = ms.get_compare_response("study-1", normalization="raw")
    assert compare.status == "ok"
    assert "FRED:UNRATE" in compare.series

    monkeypatch.setattr(ms, "list_catalog_items", lambda domain=None: [{"id": "FRED:UNRATE", "title": "Unemployment Rate", "domain": "labor", "frequency": "monthly", "publish_lag": 30, "source": "FRED", "series_id": "UNRATE"}])
    monkeypatch.setattr(
        ms,
        "get_obs_summaries",
        lambda pairs: {
            ("FRED", "UNRATE"): {
                "last_obs": "2026-02-28",
                "vintage_available": 1,
            }
        },
    )
    release = ms.get_release_calendar_response()
    assert release.status == "ok"
    assert release.items[0].estimated_next_release is not None

    report = ms.create_report_response("study-1")
    assert report.status == "ok"
    assert report.report_path is not None
    assert Path(report.report_path).exists()

    exported = ms.export_features_response("study-1")
    assert exported.status == "ok"
    assert exported.artifact_path is not None
    assert Path(exported.artifact_path).exists()


def test_leadlag_scatter_and_vintage(monkeypatch: pytest.MonkeyPatch) -> None:
    idx = pd.date_range("2024-01-05", periods=20, freq="W-FRI")

    def _series_loader(key: str, start=None, end=None):  # noqa: ANN001
        values = np.linspace(1.0, 2.0, len(idx)) if key == "A" else np.linspace(2.0, 3.5, len(idx))
        return (
            pd.Series(values, index=idx, dtype=float),
            {
                "key": key,
                "title": key,
                "units": "level",
                "frequency": "weekly",
                "source": "stub",
                "lag_applied": "P0D",
            },
            None,
        )

    monkeypatch.setattr(ms, "_get_series", _series_loader)
    leadlag = ms.get_leadlag_response("A", "B", freq="W")
    assert leadlag.status == "ok"
    assert len(leadlag.table) > 3

    scatter = ms.get_scatter_response("A", "B", freq="W")
    assert scatter.status == "ok"
    assert scatter.correlation is not None
    assert len(scatter.points) > 3

    monkeypatch.setattr(ms, "_normalize_key", lambda key: ("FRED", "UNRATE"))
    monkeypatch.setattr(ms, "load_observations", lambda source, series_id, start=None, end=None: [
        {"date": "2025-01-31", "value": 4.0},
        {"date": "2025-02-28", "value": 4.2},
    ])
    monkeypatch.setattr(ms, "load_observations_asof", lambda source, series_id, as_of_date, start=None, end=None: [
        {"date": "2025-01-31", "value": 4.0},
        {"date": "2025-02-28", "value": 4.1},
    ])
    monkeypatch.setattr(ms, "load_observation_vintages", lambda source, series_id, obs_date: [
        {"date": "2025-02-28", "value": 4.1, "realtime_start": "2025-03-01", "realtime_end": "2025-03-14"},
        {"date": "2025-02-28", "value": 4.2, "realtime_start": "2025-03-15", "realtime_end": "9999-12-31"},
    ])
    vintage = ms.get_vintage_response("FRED:UNRATE", as_of_date=date(2025, 3, 10))
    assert vintage.status == "ok"
    assert vintage.revision_delta == pytest.approx(0.1)
    assert len(vintage.revisions) == 2

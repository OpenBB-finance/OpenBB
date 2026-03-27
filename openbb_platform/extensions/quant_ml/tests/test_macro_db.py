"""Macro SQLite storage tests."""

from __future__ import annotations

from pathlib import Path

from openbb_quant_ml.service import macro_db


def _patch_db(monkeypatch, tmp_path: Path) -> None:
    macro_root = tmp_path / "macro"
    monkeypatch.setattr(macro_db, "MACRO_ROOT", macro_root)
    monkeypatch.setattr(macro_db, "MACRO_DB_PATH", macro_root / "macro.db")


def test_macro_db_upsert_and_load(monkeypatch, tmp_path: Path):
    _patch_db(monkeypatch, tmp_path)
    macro_db.init_macro_db()

    macro_db.upsert_catalog_item(
        {
            "id": "FRED:UNRATE",
            "source": "FRED",
            "series_id": "UNRATE",
            "title": "Unemployment Rate",
            "domain": "Labor",
            "default_transform": "yoy",
            "publish_lag": 30,
        }
    )
    rows = macro_db.list_catalog()
    assert any(item["id"] == "FRED:UNRATE" for item in rows)

    macro_db.upsert_observations(
        "FRED",
        "UNRATE",
        [
            {
                "date": "2025-01-31",
                "value": 4.0,
                "realtime_start": "2025-02-01",
                "realtime_end": "2025-02-01",
            },
            {
                "date": "2025-02-28",
                "value": 4.1,
                "realtime_start": "2025-03-01",
                "realtime_end": "2025-03-01",
            },
        ],
    )
    loaded = macro_db.load_observations("FRED", "UNRATE")
    assert len(loaded) == 2
    assert loaded[-1]["date"] == "2025-02-28"

    macro_db.upsert_observations(
        "FRED",
        "UNRATE",
        [
            {
                "date": "2025-02-28",
                "value": 4.3,
                "realtime_start": "2025-03-15",
                "realtime_end": "9999-12-31",
            },
        ],
    )
    asof = macro_db.load_observations_asof("FRED", "UNRATE", "2025-03-10")
    assert asof[-1]["value"] == 4.1
    vintages = macro_db.load_observation_vintages("FRED", "UNRATE", "2025-02-28")
    assert len(vintages) == 2

    summary = macro_db.get_obs_summary("FRED", "UNRATE")
    assert summary["last_obs"] == "2025-02-28"
    assert summary["vintage_available"] == 1

    batch = macro_db.get_obs_summaries([("FRED", "UNRATE"), ("FRED", "MISSING")])
    assert batch[("FRED", "UNRATE")]["last_obs"] == "2025-02-28"
    assert batch[("FRED", "UNRATE")]["vintage_available"] == 1
    assert batch[("FRED", "MISSING")]["total_rows"] == 0


def test_macro_db_derived_and_alerts(monkeypatch, tmp_path: Path):
    _patch_db(monkeypatch, tmp_path)
    macro_db.init_macro_db()

    macro_db.save_derived_expression(
        derived_id="DRV:gld_spy",
        expression="GLD/SPY",
        dependencies=["GLD", "SPY"],
        default_transform="zscore",
    )
    derived = macro_db.list_derived_expressions()
    assert len(derived) == 1
    assert derived[0]["derived_id"] == "DRV:gld_spy"

    macro_db.save_alert_events(
        [
            {
                "rule_id": "credit_stress_gt_80",
                "severity": "warning",
                "triggered_at": "2026-01-01T00:00:00+00:00",
                "message": "alert",
                "value": 81,
                "threshold": 80,
                "context": {"metric": "credit_stress_score"},
            }
        ]
    )
    alerts = macro_db.list_alert_events(limit=5)
    assert len(alerts) == 1
    assert alerts[0]["rule_id"] == "credit_stress_gt_80"


def test_macro_study_roundtrip(monkeypatch, tmp_path: Path):
    _patch_db(monkeypatch, tmp_path)
    macro_db.init_macro_db()

    saved = macro_db.save_macro_study(
        {
            "name": "Labor and Inflation Monitor",
            "objective": "Track macro regime.",
            "series_specs": [
                {
                    "key": "FRED:UNRATE",
                    "alias": "Unemployment",
                    "transform_chain": ["yoy"],
                    "freq": "M",
                    "fill": "ffill",
                    "axis": "left",
                    "normalize_mode": "yoy",
                    "lag_mode": None,
                    "display_style": "line",
                }
            ],
            "view_specs": [
                {
                    "view_id": "explorer",
                    "mode": "explorer",
                    "title": "Explorer",
                    "layout": {},
                }
            ],
            "notes": "Draft note",
            "conclusion": {"summary": "Softening labor market"},
            "linked_assets": ["SPY", "TLT"],
            "linked_feature_set_id": None,
        }
    )

    assert saved["id"]
    loaded = macro_db.get_macro_study(saved["id"])
    assert loaded is not None
    assert loaded["name"] == "Labor and Inflation Monitor"
    assert loaded["series_specs"][0]["alias"] == "Unemployment"
    assert loaded["notes"] == "Draft note"
    assert loaded["conclusion"]["summary"] == "Softening labor market"
    assert macro_db.list_macro_studies()[0]["id"] == saved["id"]

"""Tests for universe refresh utility script."""

from __future__ import annotations

from pathlib import Path

import pytest
from openbb_quant_ml.tools import refresh_universes as ru


def test_refresh_one_dry_run_does_not_write(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setattr(ru, "_fetch_us_from_wikipedia", lambda universe_id: ["AAPL", "MSFT"])
    monkeypatch.setattr(ru, "get_universe_minimum_required", lambda universe_id: 0)

    result = ru._refresh_one(
        "sp500",
        tmp_path,
        validate=False,
        max_workers=2,
        dry_run=True,
    )
    assert result.ok is True
    assert result.valid == 2
    assert (tmp_path / "sp500.csv").exists() is False


def test_atomic_write_preserves_existing_file_on_replace_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    target = tmp_path / "sp500.csv"
    original = "symbol\nOLD\n"
    target.write_text(original, encoding="utf-8")

    def _raise_replace(src: str, dst: str) -> None:  # noqa: ARG001
        raise OSError("replace failed")

    monkeypatch.setattr(ru.os, "replace", _raise_replace)
    with pytest.raises(OSError):
        ru._atomic_write_csv(target, ["NEW"])

    assert target.read_text(encoding="utf-8") == original


def test_refresh_one_writes_invalid_split(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setattr(ru, "_fetch_us_from_wikipedia", lambda universe_id: ["AAPL", "MSFT"])
    monkeypatch.setattr(ru, "get_universe_minimum_required", lambda universe_id: 0)
    monkeypatch.setattr(
        ru,
        "_validate_with_yfinance",
        lambda symbols, max_workers=6: (["AAPL"], ["MSFT"], "ok"),
    )

    result = ru._refresh_one(
        "sp500",
        tmp_path,
        validate=True,
        max_workers=2,
        dry_run=False,
    )
    assert result.ok is True
    assert result.valid == 1
    assert result.invalid == 1

    valid_text = (tmp_path / "sp500.csv").read_text(encoding="utf-8")
    invalid_text = (tmp_path / "_invalid_sp500.csv").read_text(encoding="utf-8")
    assert "AAPL" in valid_text
    assert "MSFT" in invalid_text


def test_fetch_sox_uses_html_list_fallback(monkeypatch: pytest.MonkeyPatch):
    html = "<ul><li>NVIDIA Corporation, NVDA</li><li>Broadcom Inc., AVGO</li></ul>"

    def _raise_no_table(_):  # noqa: ANN001
        raise ValueError("No tables found")

    monkeypatch.setattr(ru, "_fetch_html", lambda url, timeout_sec=20: html)
    monkeypatch.setattr(ru.pd, "read_html", _raise_no_table)

    symbols = ru._fetch_us_from_wikipedia("sox")
    assert symbols == ["AVGO", "NVDA"]


def test_refresh_one_undersized_preserves_existing_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    target = tmp_path / "sp500.csv"
    target.write_text("symbol\nOLD\n", encoding="utf-8")

    monkeypatch.setattr(ru, "_fetch_us_from_wikipedia", lambda universe_id: ["AAPL", "MSFT"])
    monkeypatch.setattr(ru, "get_universe_minimum_required", lambda universe_id: 3)

    result = ru._refresh_one(
        "sp500",
        tmp_path,
        validate=False,
        max_workers=2,
        dry_run=False,
    )

    assert result.ok is False
    assert "undersized_refresh_result" in result.message
    assert target.read_text(encoding="utf-8") == "symbol\nOLD\n"

"""Additional coverage tests for refresh_universes utility."""

from __future__ import annotations

import builtins
import types
from pathlib import Path

import pandas as pd
import pytest
from openbb_quant_ml.tools import refresh_universes as ru


def test_normalization_helpers_and_symbol_rows() -> None:
    assert ru._sanitize_token(" brk.b / ") == "BRK.B"
    assert ru._normalize_us_ticker("brk.b") == "BRK-B"
    assert ru._normalize_us_ticker("bfa") == "BF-A"
    assert ru._normalize_kr_code("005930", ".KS") == "005930.KS"
    assert ru._normalize_kr_code("abc", ".KS") == ""
    assert ru._dedupe_sort(["B", "A", "A"]) == ["A", "B"]
    rows = ru._symbol_only_rows(["aapl", "AAPL", "", "msft"])
    assert rows == [{"symbol": "AAPL"}, {"symbol": "MSFT"}]


def test_read_rows_dedupe_and_fieldnames(tmp_path: Path) -> None:
    csv_path = tmp_path / "u.csv"
    csv_path.write_text(
        "\n".join(
            [
                "symbol,name,market,category_l2",
                "AAPL,Apple,US,equity_stock",
                "AAPL,Apple Inc,US,equity_stock",
                "005930.KS,Samsung,KOSPI,semiconductor",
            ]
        ),
        encoding="utf-8",
    )
    rows = ru._read_rows_from_csv(csv_path)
    assert len(rows) == 2
    assert rows[0]["symbol"] == "005930.KS"
    assert ru._infer_market("005930.KS") == "KOSPI"
    assert ru._infer_market("005930.KQ") == "KOSDAQ"
    assert ru._infer_market("AAPL") == "US"
    fields = ru._universe_rows_fieldnames(rows)
    assert fields[0] == "symbol"
    assert "market" in fields


def test_allowed_etf_rows_and_source_path_resolution(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg = tmp_path / "universe.yaml"
    cfg.write_text(
        "\n".join(
            [
                "assets:",
                "  - symbol: TLT",
                "    category: bond_etf",
                "  - symbol: GLD",
                "    category: commodity_etf",
                "  - symbol: SPY",
                "    category: us_equity_etf",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(ru, "UNIVERSE_CONFIG_PATH", cfg)
    rows = ru._load_allowed_etf_rows()
    symbols = {row["symbol"] for row in rows}
    assert symbols == {"TLT", "GLD"}

    outdir = tmp_path / "out"
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "sp500.csv").write_text("symbol\nAAPL\n", encoding="utf-8")
    assert ru._resolve_source_universe_path("sp500", outdir) == outdir / "sp500.csv"


def test_build_all_in_one_raises_when_source_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(ru, "ALL_IN_ONE_SOURCE_UNIVERSES", ("sp500", "nasdaq100"))
    monkeypatch.setattr(ru, "_load_allowed_etf_rows", lambda: [])
    sp500_path = tmp_path / "sp500.csv"
    sp500_path.write_text("symbol\nAAPL\n", encoding="utf-8")
    monkeypatch.setattr(
        ru,
        "_resolve_source_universe_path",
        lambda universe_id, outdir: sp500_path if universe_id == "sp500" else None,
    )
    with pytest.raises(RuntimeError, match="missing source universe"):
        ru._build_all_in_one_rows(tmp_path)


def test_load_kr_taxonomy_defaults_and_classification(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    missing = tmp_path / "missing.yaml"
    monkeypatch.setattr(ru, "KR_TAXONOMY_PATH", missing)
    default_tax = ru._load_kr_taxonomy()
    assert default_tax["default_category_l2"] == "other"

    path = tmp_path / "taxonomy.yaml"
    path.write_text(
        "\n".join(
            [
                "symbol_overrides:",
                "  005930.KS: semiconductor",
                "name_keywords:",
                "  - keyword: 자동차",
                "    category_l2: automobile",
                "sector_defaults:",
                "  화학: chemical",
                "default_category_l2: other",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(ru, "KR_TAXONOMY_PATH", path)
    taxonomy = ru._load_kr_taxonomy()
    assert ru._classify_kr_category_l2("005930.KS", "삼성전자", "전기전자", taxonomy) == "semiconductor"
    assert ru._classify_kr_category_l2("005380.KS", "현대자동차", "운송장비", taxonomy) == "automobile"


def test_table_column_helpers_and_sox_fallback_parsing() -> None:
    t1 = pd.DataFrame({"A": [1]})
    t2 = pd.DataFrame({"Ticker": ["NVDA", "AVGO"]})
    table, col = ru._pick_table_with_column([t1, t2], ["Ticker", "Symbol"])
    assert col == "Ticker"
    assert ru._extract_col_values(table, "Ticker") == ["NVDA", "AVGO"]
    html = "<ul><li>NVIDIA Corporation, NVDA</li><li>Broadcom Inc., AVGO</li></ul>"
    assert ru._extract_sox_from_html_list(html) == ["AVGO", "NVDA"]
    with pytest.raises(ValueError, match="no SOX tickers"):
        ru._extract_sox_from_html_list("<ul><li>n/a</li></ul>")


def test_fetch_russell1000_parser(monkeypatch: pytest.MonkeyPatch) -> None:
    header = "Ticker,Name,Asset Class,Sector\n"
    few_rows = "\n".join([f"T{i},Name{i},Equity,Tech" for i in range(10)])
    monkeypatch.setattr(ru, "_fetch_html", lambda url, timeout_sec=30: header + few_rows)
    with pytest.raises(ValueError, match="expected >= 900"):
        ru._fetch_russell1000_from_ishares()

    many_rows = "\n".join([f"T{i},Name{i},Equity,Tech" for i in range(1000)])
    monkeypatch.setattr(ru, "_fetch_html", lambda url, timeout_sec=30: header + many_rows)
    rows = ru._fetch_russell1000_from_ishares()
    assert len(rows) >= 900
    assert rows[0]["market"] == "US"


def test_kr_snapshot_and_market_cap_fallback() -> None:
    class _Stock:
        @staticmethod
        def get_market_sector_classifications(day: str, market: str = "KOSPI"):  # noqa: ARG004
            return pd.DataFrame({"종목명": ["A"], "업종명": ["전기전자"]}, index=["005930"])

        @staticmethod
        def get_market_cap_by_ticker(day: str, market: str = "KOSPI"):  # noqa: ARG004
            frame = pd.DataFrame({"시가총액": [3, 2, 1]}, index=["005930", "000660", "005380"])
            return frame

    day, frame = ru._latest_kr_sector_snapshot(_Stock, market="KOSPI", max_lookback_days=3)
    assert day is not None
    assert not frame.empty
    caps = ru._fallback_kr_market_cap_tickers(_Stock, market="KOSPI", top_n=2, max_lookback_days=2)
    assert caps == ["005930", "000660"]


def test_validate_with_yfinance_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    # yfinance missing -> skipped validation
    original_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        if name == "yfinance":
            raise ImportError("missing")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    valid, invalid, msg = ru._validate_with_yfinance(["AAPL", "MSFT"], max_workers=2)
    assert valid == ["AAPL", "MSFT"]
    assert invalid == []
    assert "validation skipped" in msg
    monkeypatch.setattr(builtins, "__import__", original_import)

    class _YF:
        @staticmethod
        def download(symbol: str, **kwargs):  # noqa: ANN003
            if symbol == "AAPL":
                return pd.DataFrame({"Close": [1.0, 1.1]})
            return pd.DataFrame()

    monkeypatch.setitem(__import__("sys").modules, "yfinance", _YF)
    valid2, invalid2, msg2 = ru._validate_with_yfinance(["AAPL", "MSFT"], max_workers=2)
    assert valid2 == ["AAPL"]
    assert invalid2 == ["MSFT"]
    assert msg2 == "ok"


def test_main_argument_routing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # no targets -> exit 2
    args_none = types.SimpleNamespace(
        all=False,
        only=None,
        outdir=str(tmp_path),
        validate=False,
        no_validate=False,
        max_workers=2,
        dry_run=True,
    )
    monkeypatch.setattr(ru, "_parse_args", lambda: args_none)
    assert ru.main() == 2

    # target refresh with success then failure
    args_only = types.SimpleNamespace(
        all=False,
        only=["sp500", "nasdaq100"],
        outdir=str(tmp_path),
        validate=False,
        no_validate=False,
        max_workers=2,
        dry_run=True,
    )
    monkeypatch.setattr(ru, "_parse_args", lambda: args_only)
    monkeypatch.setattr(
        ru,
        "_refresh_one",
        lambda universe_id, outdir, validate, max_workers, dry_run: ru.RefreshResult(
            universe_id=universe_id,
            ok=(universe_id == "sp500"),
            fetched=1,
            normalized=1,
            valid=1,
            invalid=0,
            message="ok",
        ),
    )
    assert ru.main() == 1

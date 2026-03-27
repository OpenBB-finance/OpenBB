from types import SimpleNamespace

from openbb_quant_ml.service import finance_fundamentals


class _Row:
    def __init__(self, payload):
        self._payload = payload

    def model_dump(self):
        return dict(self._payload)


def _result(provider, rows):
    return SimpleNamespace(
        results=[_Row(row) for row in rows],
        provider=provider,
        extra=SimpleNamespace(metadata={"timestamp": "2026-03-28T00:00:00Z"}),
    )


def test_get_forecast_falls_back_to_yfinance_when_fmp_is_premium(monkeypatch):
    calls = []

    def fake_consensus(symbol, provider):
        calls.append((symbol, provider))
        if provider == "fmp":
            raise RuntimeError("402 Premium")
        if provider == "yfinance":
            return _result(
                "yfinance",
                [
                    {
                        "symbol": symbol,
                        "target_high": 390.0,
                        "target_low": 218.0,
                        "target_consensus": 313.39,
                        "target_median": 330.0,
                        "recommendation": "buy",
                        "recommendation_mean": 2.19,
                        "number_of_analysts": 19,
                        "current_price": 236.34,
                        "currency": "USD",
                    }
                ],
            )
        raise AssertionError(f"Unexpected provider {provider}")

    fake_obb = SimpleNamespace(
        equity=SimpleNamespace(
            estimates=SimpleNamespace(consensus=fake_consensus),
        ),
    )
    monkeypatch.setattr(finance_fundamentals, "obb", fake_obb)
    monkeypatch.setattr(
        "openbb_quant_ml.service.data_loader._ensure_ssl_bundle_path",
        lambda: None,
    )

    payload = finance_fundamentals.get_forecast("IBM")

    assert payload["provider"] == "yfinance"
    assert payload["results"][0]["target_consensus"] == 313.39
    assert calls == [("IBM", "fmp"), ("IBM", "yfinance")]


def test_get_forecast_returns_detail_when_all_providers_are_unusable(monkeypatch):
    def fake_consensus(symbol, provider):
        if provider == "fmp":
            raise RuntimeError("402 Premium")
        if provider == "yfinance":
            raise RuntimeError("ssl failure")
        if provider == "tmx":
            return _result(
                "tmx",
                [
                    {
                        "symbol": symbol,
                        "target_high": None,
                        "target_low": None,
                        "target_consensus": None,
                        "target_median": None,
                        "total_analysts": 0,
                        "buy_ratings": 0,
                        "hold_ratings": 0,
                        "sell_ratings": 0,
                    }
                ],
            )
        raise AssertionError(f"Unexpected provider {provider}")

    fake_obb = SimpleNamespace(
        equity=SimpleNamespace(
            estimates=SimpleNamespace(consensus=fake_consensus),
        ),
    )
    monkeypatch.setattr(finance_fundamentals, "obb", fake_obb)
    monkeypatch.setattr(
        "openbb_quant_ml.service.data_loader._ensure_ssl_bundle_path",
        lambda: None,
    )

    payload = finance_fundamentals.get_forecast("IBM")

    assert "detail" in payload
    assert "provider" not in payload

"""Unit tests for provider auto-selection strategy."""

from types import SimpleNamespace

from openbb_core.api.provider_strategy import (
    compute_confidence,
    resolve_provider_strategy,
    resolve_provider_candidates,
)


class _Credentials(SimpleNamespace):
    pass


def test_resolve_provider_candidates_prefers_quality_and_credentials():
    coverage = {"/equity/price/historical": ["wind", "tushare", "yfinance"]}
    provider_credentials = {
        "wind": [],
        "tushare": ["tushare_api_key"],
        "yfinance": [],
    }
    creds = _Credentials(tushare_api_key="token")

    result = resolve_provider_candidates(
        route="/equity/price/historical",
        requested_provider="auto",
        command_coverage=coverage,
        provider_credentials=provider_credentials,
        credentials_obj=creds,
    )

    assert result[0] == "wind"
    assert result[1] == "tushare"


def test_resolve_provider_candidates_explicit_provider():
    result = resolve_provider_candidates(
        route="/economy/gdp/real",
        requested_provider="oecd",
        command_coverage={"/economy/gdp/real": ["oecd", "imf"]},
        provider_credentials={},
        credentials_obj=_Credentials(),
    )
    assert result == ["oecd"]


def test_compute_confidence_penalizes_failures():
    no_failure = compute_confidence(
        "wind",
        [{"provider": "wind", "status": "success", "attempt": 1}],
    )
    with_failure = compute_confidence(
        "tushare",
        [
            {"provider": "wind", "status": "failed", "attempt": 1},
            {"provider": "tushare", "status": "success", "attempt": 2},
        ],
    )

    assert 0 <= with_failure <= 1
    assert 0 <= no_failure <= 1
    assert with_failure < no_failure


def test_resolve_provider_strategy_applies_route_policy_for_macro():
    strategy = resolve_provider_strategy(
        route="/economy/gdp/real",
        requested_provider="auto",
        command_coverage={"/economy/gdp/real": ["yfinance", "imf", "oecd"]},
        provider_credentials={},
        credentials_obj=_Credentials(),
        provider_health={},
        health_source="inline-test",
    )

    assert strategy["candidates"][0] == "imf"
    assert strategy["selection_reason"]["mode"] == "auto"
    assert strategy["selection_reason"]["route_policy_applied"] is True


def test_resolve_provider_strategy_health_can_deprioritize_provider():
    strategy = resolve_provider_strategy(
        route="/equity/price/historical",
        requested_provider="auto",
        command_coverage={"/equity/price/historical": ["wind", "yfinance"]},
        provider_credentials={},
        credentials_obj=_Credentials(),
        provider_health={
            "wind": {
                "success_rate": 0.1,
                "error_rate_24h": 0.8,
                "latency_ms": 2500,
            },
            "yfinance": {
                "success_rate": 0.99,
                "error_rate_24h": 0.01,
                "latency_ms": 120,
            },
        },
        health_source="inline-test",
    )

    assert strategy["candidates"][0] == "yfinance"
    scored = strategy["selection_reason"]["scored_providers"]
    assert scored[0]["provider"] == "yfinance"
    assert scored[0]["total_score"] >= scored[1]["total_score"]


def test_resolve_provider_strategy_includes_selection_reason_details():
    strategy = resolve_provider_strategy(
        route="/equity/price/historical",
        requested_provider="auto",
        command_coverage={"/equity/price/historical": ["wind", "tushare"]},
        provider_credentials={"tushare": ["tushare_api_key"]},
        credentials_obj=_Credentials(tushare_api_key="token"),
        provider_health={},
        health_source="inline-test",
    )

    reason = strategy["selection_reason"]
    assert reason["mode"] == "auto"
    assert reason["health_source"] == "inline-test"
    assert reason["requested_provider"] == "auto"
    assert isinstance(reason["scored_providers"], list)
    assert {"provider", "base_priority", "total_score"}.issubset(
        set(reason["scored_providers"][0].keys())
    )

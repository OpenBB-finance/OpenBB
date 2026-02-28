"""Unit tests for provider auto-selection strategy."""

from types import SimpleNamespace

from openbb_core.api.provider_strategy import (
    compute_confidence,
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

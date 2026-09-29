"""Tests for openbb_cli.codegen.provider_gen — provider __init__.py emission."""

from __future__ import annotations

from dataclasses import dataclass, field

from openbb_cli.codegen import provider_gen as pg


@dataclass
class _Fetcher:
    module_name: str
    fetcher_class: str
    model_name: str
    credentials_used: list[str] = field(default_factory=list)


def test_generate_provider_module_emits_provider_block_and_fetcher_imports():
    fetchers = [
        _Fetcher(
            module_name="equity_price_historical",
            fetcher_class="EquityPriceHistoricalFetcher",
            model_name="EquityPriceHistorical",
            credentials_used=["api_key"],
        ),
        _Fetcher(
            module_name="equity_quote",
            fetcher_class="EquityQuoteFetcher",
            model_name="EquityQuote",
            credentials_used=["api_key", "app_token"],
        ),
    ]
    out = pg.generate_provider_module(
        package_name="openbb_codegen",
        provider_name="fmp",
        description="FMP provider.",
        website="https://fmp.example",
        fetchers=fetchers,
    )

    assert isinstance(out, pg.GeneratedProvider)
    assert out.package_name == "openbb_codegen"
    assert out.provider_name == "fmp"
    # Credentials union deduped + sorted
    assert out.credential_keys == ["api_key", "app_token"]

    src = out.source
    assert (
        "from openbb_codegen.providers.fmp.models.equity_price_historical "
        "import EquityPriceHistoricalFetcher"
    ) in src
    assert (
        "from openbb_codegen.providers.fmp.models.equity_quote import EquityQuoteFetcher"
    ) in src
    assert "fmp_provider = Provider(" in src
    assert 'name="fmp"' in src
    assert "description='FMP provider.'" in src
    assert 'website="https://fmp.example"' in src
    assert '"EquityPriceHistorical": EquityPriceHistoricalFetcher,' in src
    assert '"EquityQuote": EquityQuoteFetcher,' in src
    # Credentials block present in sorted order
    assert "credentials=[" in src
    assert "'api_key'" in src
    assert "'app_token'" in src


def test_generate_provider_module_omits_credentials_when_none():
    fetchers = [
        _Fetcher(
            module_name="m",
            fetcher_class="MFetcher",
            model_name="M",
            credentials_used=[],
        )
    ]
    out = pg.generate_provider_module(
        package_name="openbb_x",
        provider_name="p",
        description="d",
        website="https://x",
        fetchers=fetchers,
    )

    assert out.credential_keys == []
    assert "credentials=" not in out.source
    assert "p_provider = Provider(" in out.source

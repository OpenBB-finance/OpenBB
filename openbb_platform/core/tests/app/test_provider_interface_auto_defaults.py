"""Lightweight tests for provider auto defaults without full registry setup."""

from typing import get_args

from openbb_core.app.provider_interface import ProviderInterface


def _new_provider_interface() -> ProviderInterface:
    """Create ProviderInterface instance without running heavy __init__."""
    return ProviderInterface.__new__(ProviderInterface)


def test_with_auto_choice_adds_auto_prefix():
    choices = ProviderInterface._with_auto_choice(["wind", "tushare"])
    assert choices[0] == "auto"
    assert "wind" in choices
    assert "tushare" in choices


def test_generate_model_providers_dc_defaults_to_auto():
    provider_interface = _new_provider_interface()
    map_ = {
        "EquityHistorical": {
            "openbb": {},
            "yfinance": {},
            "wind": {},
        }
    }

    providers = ProviderInterface._generate_model_providers_dc(provider_interface, map_)
    model_dc = providers["EquityHistorical"]
    instance = model_dc()

    assert instance.provider == "auto"
    annotation_choices = get_args(model_dc.__annotations__["provider"])
    assert "auto" in annotation_choices


def test_get_provider_choices_defaults_to_auto():
    provider_interface = _new_provider_interface()
    provider_choices_cls = ProviderInterface._get_provider_choices(
        provider_interface, ["yfinance", "wind"]
    )

    instance = provider_choices_cls()
    assert instance.provider == "auto"
    annotation_choices = get_args(provider_choices_cls.__annotations__["provider"])
    assert "auto" in annotation_choices

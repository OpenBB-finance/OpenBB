import openbb_ecb.assets  # noqa: F401
from openbb_ecb import _installed, ecb_provider


def test_provider_metadata():
    assert ecb_provider.name == "ECB"
    assert ecb_provider.website == "https://data.ecb.europa.eu"
    keys = set(ecb_provider.fetcher_dict)
    assert {"EcbMfiInterestRates", "EcbEligibleAssets"} <= keys
    assert len(ecb_provider.fetcher_dict) == 11


def test_key_helpers_both_branches(monkeypatch):
    for flag, helper in (
        ("ECONOMY_INSTALLED", _installed.economy_key),
        ("CURRENCY_INSTALLED", _installed.currency_key),
        ("FIXEDINCOME_INSTALLED", _installed.fixedincome_key),
    ):
        monkeypatch.setattr(_installed, flag, True)
        assert helper("Standard", "Alias") == "Standard"
        monkeypatch.setattr(_installed, flag, False)
        assert helper("Standard", "Alias") == "Alias"

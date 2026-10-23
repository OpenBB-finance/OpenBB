"""Integration tests for the usda REST API."""

from importlib.util import find_spec

import pytest
import requests
from openbb_core.provider.utils.helpers import get_querystring

BASE = "http://127.0.0.1:8000/api/v1/usda"


def _get(endpoint: str, params: dict, headers: dict) -> requests.Response:
    """GET an endpoint with None-stripped query params."""
    query = get_querystring({k: v for k, v in params.items() if v is not None}, [])
    return requests.get(f"{BASE}/{endpoint}?{query}", headers=headers, timeout=60)


def _post_urls(endpoint: str, urls: list, headers: dict) -> requests.Response:
    """POST a document-download endpoint with a list of URLs."""
    return requests.post(f"{BASE}/{endpoint}", headers=headers, json=urls, timeout=60)


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "usda"},
        {
            "provider": "usda",
            "commodity": "coffee",
            "attribute": "exports",
            "country": "brazil",
            "start_year": 2020,
            "end_year": 2025,
        },
    ],
)
@pytest.mark.skipif(
    find_spec("openbb_commodity") is not None,
    reason="commands live on the commodity extension",
)
@pytest.mark.integration
def test_usda_psd_data(params, headers):
    """GET /psd_data."""
    assert _get("psd_data", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "usda", "commodity": "sugar", "year": 2025, "month": 5}],
)
@pytest.mark.skipif(
    find_spec("openbb_commodity") is not None,
    reason="commands live on the commodity extension",
)
@pytest.mark.integration
def test_usda_psd_report(params, headers):
    """GET /psd_report."""
    assert _get("psd_report", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "usda", "year": 2024, "month": 12, "week": 2}],
)
@pytest.mark.skipif(
    find_spec("openbb_commodity") is not None,
    reason="commands live on the commodity extension",
)
@pytest.mark.integration
def test_usda_weather_bulletins(params, headers):
    """GET /weather_bulletins."""
    assert _get("weather_bulletins", params, headers).status_code == 200


@pytest.mark.parametrize(
    "urls",
    [
        [
            "https://esmis.nal.usda.gov/sites/default/release-files/cj82k728n/9w033w568/x059f4232/wwcb0125.pdf"
        ]
    ],
)
@pytest.mark.skipif(
    find_spec("openbb_commodity") is not None,
    reason="commands live on the commodity extension",
)
@pytest.mark.integration
def test_usda_weather_bulletins_download(urls, headers):
    """POST /weather_bulletins_download."""
    assert _post_urls("weather_bulletins_download", urls, headers).status_code == 200

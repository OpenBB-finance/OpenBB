"""HTTP API integration tests."""

import base64

import pytest
import requests
from openbb_core.env import Env

_BASE_URL = "http://127.0.0.1:8000/api/v1/news"
_headers: dict = {}


def get_headers() -> dict:
    if _headers:
        return _headers
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    base64_bytes = base64.b64encode(userpass.encode("ascii"))
    _headers["Authorization"] = f"Basic {base64_bytes.decode('ascii')}"
    return _headers


def _get(path: str, params: dict | None = None) -> requests.Response:
    return requests.get(
        f"{_BASE_URL}/{path}", headers=get_headers(), params=params, timeout=60
    )


@pytest.mark.integration
def test_rss_providers_lists_outlets():
    result = _get("rss_providers")
    assert result.status_code == 200
    payload = result.json()
    assert isinstance(payload, list)
    values = {entry["value"] for entry in payload}
    assert "bbc" in values
    assert "globenewswire" in values
    assert "pr_newswire" in values
    assert "drugs_com" in values
    assert "brutalist_tech" in values
    assert "brutalist_sports" in values


@pytest.mark.integration
def test_rss_feeds_filtered_by_outlet():
    result = _get("rss_feeds", params={"outlet": "bbc"})
    assert result.status_code == 200
    payload = result.json()
    assert isinstance(payload, list)
    values = {entry["value"] for entry in payload}
    assert "bbc_world" in values
    assert "bbc_business" in values


@pytest.mark.integration
def test_rss_fetches_articles_without_body():
    result = _get(
        "rss",
        params={"source": "bbc_world", "limit": 3, "fetch_body": "false"},
    )
    assert result.status_code == 200
    body = result.json()
    results = body["results"]
    assert 1 <= len(results) <= 3
    first = results[0]
    assert first["title"]
    assert first["date"]
    assert first["author"]
    assert "url" in first
    assert "excerpt" in first
    assert "body" in first


@pytest.mark.integration
def test_rss_feeds_filtered_by_drugs_com_outlet():
    result = _get("rss_feeds", params={"outlet": "drugs_com"})
    assert result.status_code == 200
    values = {entry["value"] for entry in result.json()}
    assert values == {
        "drugs_com_medical_news",
        "drugs_com_headline_news",
        "drugs_com_fda_alerts",
        "drugs_com_new_drug_approvals",
        "drugs_com_new_drug_applications",
        "drugs_com_clinical_trials",
    }


@pytest.mark.integration
def test_rss_drugs_com_fetches_full_body():
    result = _get(
        "rss",
        params={"source": "drugs_com_medical_news", "limit": 3, "fetch_body": "true"},
    )
    assert result.status_code == 200
    results = result.json()["results"]
    assert 1 <= len(results) <= 3
    for article in results:
        assert len(article["body"]) > len(article["excerpt"])
        assert "Whatever your topic of interest" not in article["body"]
        assert "Disclaimer: Statistical data" not in article["body"]
        assert "ddc-opengraph-logomark" not in article["body"]


@pytest.mark.integration
def test_rss_brutalist_gated_host_fetches_full_body():
    # ESPN, PBS, BleepingComputer, Heavy and Techmeme need pinned request
    # headers; a plain session gets 403/202/406. Exercise one of them live.
    result = _get(
        "rss",
        params={"source": "brutalist_tech_bleepingcomputer", "limit": 2},
    )
    assert result.status_code == 200
    results = result.json()["results"]
    assert 1 <= len(results) <= 2
    for article in results:
        assert article["title"]
        assert len(article["body"]) > len(article["excerpt"])


@pytest.mark.integration
def test_rss_returns_empty_when_no_source_and_no_outlet():
    result = _get("rss")
    assert result.status_code == 200
    assert result.json()["results"] == []


@pytest.mark.integration
def test_rss_auto_resolves_default_when_only_outlet_given():
    result = _get("rss", params={"outlet": "bbc", "limit": 1, "fetch_body": "false"})
    assert result.status_code == 200
    body = result.json()
    assert len(body["results"]) == 1


@pytest.mark.integration
def test_rss_unknown_source_returns_error():
    result = _get("rss", params={"source": "not_a_feed", "limit": 1})
    assert result.status_code >= 400

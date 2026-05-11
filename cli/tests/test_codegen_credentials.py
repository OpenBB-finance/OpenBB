"""Tests for openbb_cli.codegen.credentials — credential name detection."""

from __future__ import annotations

import pytest

from openbb_cli.codegen import credentials as cr

# --- normalize_credential_key ---


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("api_key", "api_key"),
        ("API-KEY", "api_key"),
        ("X-API-Key", "x_api_key"),
        ("apikey", "apikey"),
        ("App-Token", "app_token"),
        ("Authorization", "authorization"),
        ("__leading__trailing__", "leading__trailing"),
    ],
)
def test_normalize_credential_key_canonicalizes_separators_and_case(raw, expected):
    assert cr.normalize_credential_key(raw) == expected


# --- is_credential_name ---


@pytest.mark.parametrize(
    "name",
    [
        "api_key",
        "apikey",
        "API_KEY",
        "X-API-Key",
        "x-api-key",
        "app_token",
        "client_id",
        "client_secret",
        "Authorization",
        "subscription_key",
        "Ocp-Apim-Subscription-Key",
        "bearer_token",
        "session_token",
        "private_key",
    ],
)
def test_is_credential_name_recognizes_canonical_credentials(name):
    assert cr.is_credential_name(name) is True


@pytest.mark.parametrize(
    "name",
    [
        "symbol",
        "limit",
        "from_date",
        "x_columns",
        "interval",
        "format",
        "page_size",
    ],
)
def test_is_credential_name_rejects_regular_params(name):
    assert cr.is_credential_name(name) is False


# --- classify_parameter ---


def test_classify_parameter_returns_query_for_query_credential():
    p = {"name": "api_key", "in": "query"}
    assert cr.classify_parameter(p) == "query"


def test_classify_parameter_returns_header_for_header_credential():
    p = {"name": "Authorization", "in": "header"}
    assert cr.classify_parameter(p) == "header"


def test_classify_parameter_defaults_to_query_when_in_unset():
    """A credential without an ``in`` location is treated as query (most common)."""
    p = {"name": "api_key"}
    assert cr.classify_parameter(p) == "query"


def test_classify_parameter_returns_none_for_regular_param():
    p = {"name": "symbol", "in": "query"}
    assert cr.classify_parameter(p) is None


def test_classify_parameter_returns_none_for_unnamed_param():
    """A malformed param entry without ``name`` is gracefully skipped."""
    assert cr.classify_parameter({}) is None
    assert cr.classify_parameter({"name": 42, "in": "query"}) is None  # type: ignore[arg-type]


def test_classify_parameter_returns_none_for_non_dict_input():
    """Defensive: a stray non-dict in the parameters list doesn't crash."""
    assert cr.classify_parameter("not-a-dict") is None  # type: ignore[arg-type]


# --- credentials_from_command ---


def test_credentials_from_command_extracts_query_and_header_entries():
    cmd = {
        "parameters": [
            {"name": "symbol", "in": "query"},
            {"name": "api_key", "in": "query"},
            {"name": "Authorization", "in": "header"},
        ]
    }
    out = cr.credentials_from_command(cmd)
    assert out == {
        "api_key": {"name": "api_key", "in": "query"},
        "authorization": {"name": "Authorization", "in": "header"},
    }


def test_credentials_from_command_returns_empty_when_no_creds():
    assert cr.credentials_from_command({"parameters": [{"name": "limit"}]}) == {}


def test_credentials_from_command_handles_missing_parameters_key():
    assert cr.credentials_from_command({}) == {}


# --- credentials_from_spec ---


def test_credentials_from_spec_aggregates_across_commands():
    spec = {
        "commands": {
            "a": {"parameters": [{"name": "api_key", "in": "query"}]},
            "b": {"parameters": [{"name": "Authorization", "in": "header"}]},
            "c": {"parameters": [{"name": "symbol", "in": "query"}]},
        }
    }
    out = cr.credentials_from_spec(spec)
    assert set(out) == {"api_key", "authorization"}
    assert out["api_key"]["name"] == "api_key"
    assert out["authorization"]["in"] == "header"


def test_credentials_from_spec_first_occurrence_wins_on_collision():
    """If two commands declare the same canonical key with different spellings,
    the first one encountered keeps its on-the-wire spelling."""
    spec = {
        "commands": {
            "a": {"parameters": [{"name": "API-KEY", "in": "query"}]},
            "b": {"parameters": [{"name": "api_key", "in": "header"}]},
        }
    }
    out = cr.credentials_from_spec(spec)
    assert out["api_key"]["name"] == "API-KEY"
    assert out["api_key"]["in"] == "query"


def test_credentials_from_spec_returns_empty_when_no_commands():
    assert cr.credentials_from_spec({}) == {}


# --- filter_user_params ---


def test_filter_user_params_strips_credential_entries():
    params = [
        {"name": "symbol", "in": "query"},
        {"name": "api_key", "in": "query"},
        {"name": "limit", "in": "query"},
        {"name": "Authorization", "in": "header"},
    ]
    out = cr.filter_user_params(params)
    names = [p["name"] for p in out]
    assert names == ["symbol", "limit"]


def test_filter_user_params_returns_empty_for_none_or_empty():
    assert cr.filter_user_params(None) == []  # type: ignore[arg-type]
    assert cr.filter_user_params([]) == []


def test_filter_user_params_does_not_mutate_input():
    """Defensive: the input list is unchanged after filtering."""
    params = [
        {"name": "api_key", "in": "query"},
        {"name": "symbol", "in": "query"},
    ]
    original = list(params)
    cr.filter_user_params(params)
    assert params == original

"""Tests for openbb_cli.codegen.test_gen — per-provider unit-test emission."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field

from openbb_cli.codegen import test_gen as tg


@dataclass
class _Fetcher:
    module_name: str
    fetcher_class: str
    model_name: str = ""
    credentials_used: dict[str, dict[str, str]] = field(default_factory=dict)


def _spec_with_choices_and_default():
    return {
        "equity.search": {
            "parameters": [
                {
                    "name": "scope",
                    "type": "string",
                    "required": True,
                    "choices": ["all", "active"],
                },
                {
                    "name": "format",
                    "type": "string",
                    "required": True,
                    "default": "json",
                    "choices": ["json", "xml"],
                },
            ],
        },
    }


# --- _spec_supplied_value ---


def test_spec_supplied_value_prefers_example_over_everything():
    assert (
        tg._spec_supplied_value(
            {
                "example": "AAPL",
                "default": "MSFT",
                "choices": ["GOOG", "AMZN"],
            }
        )
        == "AAPL"
    )


def test_spec_supplied_value_prefers_default_over_choices():
    assert (
        tg._spec_supplied_value({"default": "json", "choices": ["xml", "json"]})
        == "json"
    )


def test_spec_supplied_value_falls_back_to_first_choice():
    assert tg._spec_supplied_value({"choices": ["all", "active"]}) == "all"


def test_spec_supplied_value_returns_none_when_no_default_or_choices():
    assert tg._spec_supplied_value({"type": "string"}) is None
    assert tg._spec_supplied_value({}) is None


def test_spec_supplied_value_treats_empty_choices_as_no_choices():
    assert tg._spec_supplied_value({"choices": []}) is None


def test_normalize_to_module_matches_fetcher_module_naming_with_spaces():
    """Dotted names with spaces collapse the same way fetcher module names do."""
    assert tg._normalize_to_module("soma.agency.wam.agency debts.asof") == (
        "soma_agency_wam_agency_debts_asof"
    )


def test_normalize_to_module_handles_leading_digit_and_empty():
    assert tg._normalize_to_module("3legged.path") == "_3legged_path"
    assert tg._normalize_to_module("___") == "command"


# --- _derive_test_params ---


def test_derive_test_params_returns_empty_when_no_required_params():
    cmd = {"parameters": [{"name": "x", "type": "string"}]}
    assert tg._derive_test_params(cmd, "fmp") == {}


def test_derive_test_params_includes_only_required_with_known_value():
    cmd = {
        "parameters": [
            {
                "name": "scope",
                "type": "string",
                "required": True,
                "choices": ["all"],
            },
            {"name": "limit", "type": "integer", "default": 10},
        ]
    }
    out = tg._derive_test_params(cmd, "fmp")
    assert out == {"scope": "all"}


def test_derive_test_params_returns_none_when_required_param_has_no_supplied_value():
    cmd = {
        "parameters": [
            {"name": "cusip", "type": "string", "required": True},
        ]
    }
    assert tg._derive_test_params(cmd, "fmp") is None


def test_derive_test_params_skips_provider_discriminator():
    cmd = {
        "parameters": [
            {"name": "provider", "type": "string", "required": True},
            {
                "name": "scope",
                "type": "string",
                "required": True,
                "choices": ["all"],
            },
        ]
    }
    assert tg._derive_test_params(cmd, "fmp") == {"scope": "all"}


def test_derive_test_params_skips_unnamed_or_non_dict_entries():
    cmd = {
        "parameters": [
            "not a dict",
            {"type": "string", "required": True},
            {
                "name": "scope",
                "type": "string",
                "required": True,
                "choices": ["all"],
            },
        ]
    }
    assert tg._derive_test_params(cmd, "fmp") == {"scope": "all"}


def test_derive_test_params_skips_param_outside_provider_whitelist():
    cmd = {
        "parameters": [
            {
                "name": "use_cache",
                "type": "boolean",
                "required": True,
                "providers": ["cboe"],
            },
        ]
    }
    # ``use_cache`` is cboe-only — fmp's QueryParams class doesn't have it,
    # so it's skipped instead of failing the whole test.
    assert tg._derive_test_params(cmd, "fmp") == {}


def test_derive_test_params_skips_optional_choices_to_avoid_over_constraining():
    """Optional ``choices`` over-constrain queries (rp_results_search empty
    when method=multiple+term=overnight added). Better to omit and let the
    upstream choose its own defaults."""
    cmd = {
        "parameters": [
            {
                "name": "scope",
                "type": "string",
                "required": True,
                "choices": ["all"],
            },
            {
                "name": "operationTypes",
                "type": "string",
                "required": False,
                "choices": ["Repo", "Reverse Repo"],
            },
        ]
    }
    out = tg._derive_test_params(cmd, "fmp")
    assert out == {"scope": "all"}
    assert "operationTypes" not in out


def test_derive_test_params_includes_optional_date_params_with_current_date():
    """Search endpoints typically need a date range to return data."""
    cmd = {
        "parameters": [
            {
                "name": "scope",
                "type": "string",
                "required": True,
                "choices": ["all"],
            },
            {"name": "startDate", "type": "string", "required": False},
            {"name": "endDate", "type": "string", "required": False},
        ]
    }
    out = tg._derive_test_params(cmd, "fmp")
    from datetime import date, timedelta

    assert out["scope"] == "all"
    assert out["startDate"] == str(date.today() - timedelta(days=30))
    assert out["endDate"] == str(date.today())


def test_derive_test_params_skips_optional_param_without_date_shape_or_required():
    cmd = {
        "parameters": [
            {
                "name": "scope",
                "type": "string",
                "required": True,
                "choices": ["all"],
            },
            {"name": "extra", "type": "string", "required": False},
            {
                "name": "cusip",
                "type": "string",
                "required": False,
                "example": "01234ABCD",
            },
        ]
    }
    out = tg._derive_test_params(cmd, "fmp")
    assert out == {"scope": "all"}


def test_is_date_param_recognizes_canonical_names():
    assert tg._is_date_param("startDate")
    assert tg._is_date_param("endDate")
    assert tg._is_date_param("date")
    assert tg._is_date_param("fromDate")
    assert tg._is_date_param("toDate")
    assert tg._is_date_param("from")
    assert tg._is_date_param("to")
    assert tg._is_date_param("operationDate")  # contains "date"
    assert not tg._is_date_param("symbol")
    assert not tg._is_date_param("limit")


# --- _refresh_date_shape ---


def test_refresh_date_shape_replaces_yyyy_mm_dd_example_with_today():
    out = tg._refresh_date_shape("endDate", "2021-01-01")
    from datetime import date

    assert out == str(date.today())


def test_refresh_date_shape_uses_thirty_days_ago_for_start_date():
    out = tg._refresh_date_shape("startDate", "2021-01-01")
    from datetime import date, timedelta

    assert out == str(date.today() - timedelta(days=30))


def test_refresh_date_shape_treats_from_as_start_alias():
    out = tg._refresh_date_shape("from", "2021-01-01")
    from datetime import date, timedelta

    assert out == str(date.today() - timedelta(days=30))


def test_refresh_date_shape_handles_iso_timestamps():
    """ISO-8601 timestamps refresh to today's UTC timestamp."""
    out = tg._refresh_date_shape("toDateTime", "2021-01-01T00:00:00Z")
    assert out.endswith("Z")
    assert "T" in out
    # It's an actual parseable iso datetime
    from datetime import datetime

    parsed = datetime.fromisoformat(out.replace("Z", "+00:00"))
    assert parsed.year >= 2024


def test_refresh_date_shape_passes_through_non_date_strings():
    assert tg._refresh_date_shape("symbol", "AAPL") == "AAPL"


def test_refresh_date_shape_passes_through_non_strings():
    assert tg._refresh_date_shape("limit", 5) == 5
    assert tg._refresh_date_shape("flag", True) is True


def test_spec_supplied_value_returns_none_for_open_ended_param():
    """Param with no example, default, or choices yields None — caller skips test."""
    assert tg._spec_supplied_value({"name": "cusip", "type": "string"}) is None


# --- generate_provider_tests ---


def test_generate_provider_tests_returns_none_when_no_fetchers():
    out = tg.generate_provider_tests(
        package_name="openbb_x",
        provider_name="x",
        fetchers=[],
        commands_by_dotted={},
    )
    assert out is None


def test_generate_provider_tests_emits_runnable_module():
    fetchers = [
        _Fetcher(module_name="equity_search", fetcher_class="EquitySearchFetcher"),
    ]
    out = tg.generate_provider_tests(
        package_name="openbb_x",
        provider_name="x",
        fetchers=fetchers,
        commands_by_dotted=_spec_with_choices_and_default(),
    )
    assert out is not None
    assert out.module_name == "test_x_fetchers"
    src = out.source
    ast.parse(src)
    assert "import pytest" in src
    assert (
        "from openbb_x.providers.x.models.equity_search import EquitySearchFetcher"
    ) in src
    assert "test_credentials = UserService()" in src
    assert "@pytest.fixture" in src
    assert "def vcr_config():" in src
    assert "@pytest.mark.record_http" in src
    assert "def test_equity_search_fetcher(credentials=test_credentials):" in src
    assert "fetcher = EquitySearchFetcher()" in src
    assert "result = fetcher.test(params, credentials)" in src
    assert "assert result is None" in src
    # Required params: scope (choices[0]='all') + format (default='json').
    assert "'scope': 'all'" in src
    assert "'format': 'json'" in src


def test_generate_provider_tests_skips_fetchers_with_unsuppliable_required_params():
    fetchers = [
        _Fetcher(module_name="equity_search", fetcher_class="EquitySearchFetcher"),
        _Fetcher(module_name="x_y", fetcher_class="XYFetcher"),
    ]
    cmds = {
        "equity.search": _spec_with_choices_and_default()["equity.search"],
        # XY requires a free-form ``cusip`` -- can't derive a valid value
        "x.y": {
            "parameters": [
                {"name": "cusip", "type": "string", "required": True},
            ]
        },
    }
    out = tg.generate_provider_tests(
        package_name="openbb_x",
        provider_name="x",
        fetchers=fetchers,
        commands_by_dotted=cmds,
    )
    assert out is not None
    assert "EquitySearchFetcher()" in out.source
    assert "XYFetcher" not in out.source


def test_generate_provider_tests_returns_none_when_every_fetcher_unconfident():
    fetchers = [
        _Fetcher(module_name="x_y", fetcher_class="XYFetcher"),
        _Fetcher(module_name="a_b", fetcher_class="ABFetcher"),
    ]
    cmds = {
        "x.y": {"parameters": [{"name": "cusip", "type": "string", "required": True}]},
        "a.b": {"parameters": [{"name": "raw_id", "type": "string", "required": True}]},
    }
    assert (
        tg.generate_provider_tests(
            package_name="openbb_x",
            provider_name="x",
            fetchers=fetchers,
            commands_by_dotted=cmds,
        )
        is None
    )


def test_generate_provider_tests_handles_unknown_command_dotted_path():
    """Fetcher whose module name doesn't match any dotted command -> empty params."""
    fetchers = [_Fetcher(module_name="orphan", fetcher_class="OrphanFetcher")]
    out = tg.generate_provider_tests(
        package_name="openbb_x",
        provider_name="x",
        fetchers=fetchers,
        commands_by_dotted={"some.other.thing": {"parameters": []}},
    )
    assert out is not None
    assert "params = {}" in out.source


# --- vcr_config redactions ---


def test_generate_provider_tests_emits_query_credential_with_mock_value():
    fetchers = [
        _Fetcher(
            module_name="equity_search",
            fetcher_class="EquitySearchFetcher",
            credentials_used={"api_key": {"name": "apikey", "in": "query"}},
        ),
    ]
    out = tg.generate_provider_tests(
        package_name="openbb_x",
        provider_name="x",
        fetchers=fetchers,
        commands_by_dotted=_spec_with_choices_and_default(),
    )
    assert out is not None
    assert "filter_query_parameters" in out.source
    assert "('apikey', 'MOCK_API_KEY')" in out.source


def test_generate_provider_tests_emits_header_credential_with_bearer_mock():
    fetchers = [
        _Fetcher(
            module_name="equity_search",
            fetcher_class="EquitySearchFetcher",
            credentials_used={
                "authorization": {"name": "Authorization", "in": "header"}
            },
        ),
    ]
    out = tg.generate_provider_tests(
        package_name="openbb_x",
        provider_name="x",
        fetchers=fetchers,
        commands_by_dotted=_spec_with_choices_and_default(),
    )
    assert out is not None
    assert "('Authorization', 'Bearer MOCK_TOKEN')" in out.source


def test_generate_provider_tests_includes_standard_redaction_baseline():
    """Even without provider-declared credentials, the baseline redactions ship."""
    fetchers = [
        _Fetcher(module_name="equity_search", fetcher_class="EquitySearchFetcher")
    ]
    out = tg.generate_provider_tests(
        package_name="openbb_x",
        provider_name="x",
        fetchers=fetchers,
        commands_by_dotted=_spec_with_choices_and_default(),
    )
    assert out is not None
    assert "('User-Agent', None)" in out.source
    for entry in (
        "('api_key', 'MOCK_API_KEY')",
        "('client_secret', 'MOCK_CLIENT_SECRET')",
        "('access_token', 'MOCK_TOKEN')",
        "('private_key', 'MOCK_SECRET')",
    ):
        assert entry in out.source


# --- _mock_value_for branches ---


def test_mock_value_for_picks_secret_when_name_contains_secret():
    assert tg._mock_value_for("client_secret") == "MOCK_SECRET"
    assert tg._mock_value_for("private_key_secret") == "MOCK_SECRET"


def test_mock_value_for_picks_token_when_name_contains_token():
    assert tg._mock_value_for("auth_token") == "MOCK_TOKEN"
    assert tg._mock_value_for("X-Auth-Token") == "MOCK_TOKEN"


def test_mock_value_for_picks_client_id_for_id_shaped_names():
    assert tg._mock_value_for("client_id") == "MOCK_CLIENT_ID"
    assert tg._mock_value_for("appid") == "MOCK_CLIENT_ID"
    assert tg._mock_value_for("app_id") == "MOCK_CLIENT_ID"


def test_mock_value_for_default_falls_back_to_api_key():
    assert tg._mock_value_for("apikey") == "MOCK_API_KEY"
    assert tg._mock_value_for("subscription_key") == "MOCK_API_KEY"


# --- _merge_redactions edge cases ---


def test_merge_redactions_skips_credentials_without_wire_name():
    fetchers = [
        _Fetcher(
            module_name="x",
            fetcher_class="XFetcher",
            credentials_used={"weird": {"in": "query"}},
        ),
    ]
    headers, queries = tg._merge_redactions(fetchers)
    assert all(name for name, _ in headers)
    assert all(name for name, _ in queries)


def test_merge_redactions_picks_up_provider_credential_outside_baseline():
    fetchers = [
        _Fetcher(
            module_name="x",
            fetcher_class="XFetcher",
            credentials_used={"weird_creds": {"name": "X-Weird-Creds", "in": "header"}},
        ),
    ]
    headers, _ = tg._merge_redactions(fetchers)
    assert ("X-Weird-Creds", "MOCK_API_KEY") in headers


# --- _snake ---


def test_snake_handles_multi_word_camelcase():
    assert (
        tg._snake("EquityPriceHistoricalFetcher") == "equity_price_historical_fetcher"
    )
    assert tg._snake("XYZFetcher") == "xyzfetcher"
    assert tg._snake("simple") == "simple"

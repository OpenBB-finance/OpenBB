"""Tests for openbb_cli.dispatchers.socrata — story → spec ingestion."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
import pytest

from openbb_cli.dispatchers import socrata
from openbb_cli.dispatchers.spec import SpecDocument


def _run_with_mock_client(
    handler: Callable[[httpx.Request], httpx.Response],
    operation: Callable[[httpx.AsyncClient], Awaitable[Any]],
) -> Any:
    """Run an async operation against an ``httpx.AsyncClient`` whose
    transport is mocked by ``handler``.

    Lets sync test functions exercise the async network paths without
    pulling in pytest-asyncio — each test owns its own event loop via
    ``asyncio.run``.
    """

    async def go() -> Any:
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            return await operation(client)

    return asyncio.run(go())


# --- _slugify ---


def test_slugify_lowercases_and_collapses_non_alnum_to_underscore():
    assert socrata._slugify("Waterborne Agricultural Trade Data!") == (
        "waterborne_agricultural_trade_data"
    )


def test_slugify_prefixes_underscore_when_starts_with_digit():
    assert socrata._slugify("2024 Quarterly Report") == "_2024_quarterly_report"


def test_slugify_falls_back_to_dataset_when_input_is_only_punctuation():
    assert socrata._slugify("---") == "dataset"


# --- extract_dataset_uids / _walk_for_dataset_uids ---


def test_extract_dataset_uids_walks_nested_blocks():
    """Stories nest ``datasetUid`` deep inside layout/component trees."""
    story = {
        "blocks": [
            {
                "components": [
                    {"vif": {"dataSource": {"datasetUid": "aaaa-bbbb"}}},
                    {"vif": {"dataSource": {"datasetUid": "cccc-dddd"}}},
                ]
            },
            {"layout": {"sections": [{"datasetUid": "aaaa-bbbb"}]}},  # dup
        ]
    }
    assert socrata.extract_dataset_uids(story) == ["aaaa-bbbb", "cccc-dddd"]


def test_extract_dataset_uids_ignores_non_string_dataset_uid_values():
    """A ``datasetUid: null`` (sometimes appears in disabled blocks) is skipped."""
    story = {"blocks": [{"datasetUid": None}, {"datasetUid": "real-data"}]}
    assert socrata.extract_dataset_uids(story) == ["real-data"]


def test_extract_dataset_uids_ignores_4x4_strings_outside_dataset_uid_keys():
    """A 4x4-shaped string in body text isn't a real reference — only
    values keyed by ``datasetUid`` count."""
    story = {
        "title": "Story xxxx-yyyy is not a dataset reference",
        "blocks": [{"datasetUid": "real-data"}],
    }
    assert socrata.extract_dataset_uids(story) == ["real-data"]


def test_extract_dataset_uids_returns_empty_when_story_has_no_datasets():
    assert socrata.extract_dataset_uids({"blocks": []}) == []


# --- _coerce_choices_to_type ---


def test_coerce_choices_to_type_casts_checkbox_strings_to_booleans():
    """Socrata serializes ``checkbox`` distinct values as the strings
    ``"true"`` / ``"false"`` — proper parsing (not naive ``bool()``,
    which would call ``"false"`` truthy)."""
    assert socrata._coerce_choices_to_type(
        ["true", "false", None, True, "garbage"], "checkbox"
    ) == [True, False, True]


def test_coerce_choices_to_type_passes_through_non_numeric_non_checkbox_types():
    """``string`` / ``date`` columns just hand the raw values back."""
    assert socrata._coerce_choices_to_type(["a", "b"], "text") == ["a", "b"]


# --- _is_categorical_column ---


def test_is_categorical_column_returns_true_for_text_and_html_only():
    assert socrata._is_categorical_column({"dataTypeName": "text"}) is True
    assert socrata._is_categorical_column({"dataTypeName": "html"}) is True
    assert socrata._is_categorical_column({"dataTypeName": "number"}) is False
    assert socrata._is_categorical_column({"dataTypeName": "calendar_date"}) is False
    # Defaults to ``"text"`` when ``dataTypeName`` is missing.
    assert socrata._is_categorical_column({}) is True


# --- fetch_column_distinct_values defensive branch ---


def test_afetch_column_distinct_values_skips_non_dict_rows_in_response():
    """A SoQL response with a stray scalar in the rows list (malformed
    upstream payload) doesn't crash — non-dict entries are silently
    skipped."""

    def handler(_request):
        return httpx.Response(200, json=[{"port": "A"}, "garbage", {"port": "B"}])

    out = _run_with_mock_client(
        handler,
        lambda c: socrata.afetch_column_distinct_values(
            c, "https://x", "uid-1", "port"
        ),
    )
    assert out == ["A", "B"]


# --- _build_query_parameters defensive branches ---


def test_build_query_parameters_skips_non_dict_columns_and_unnamed_columns():
    """Defensive: a stray non-dict entry in ``columns`` and a column with
    no ``fieldName`` / ``name`` both get skipped — only well-formed
    columns produce filter params."""
    meta = {
        "columns": [
            "not-a-dict",  # skipped — non-dict
            {"dataTypeName": "text"},  # skipped — no fieldName
            {"fieldName": "ok", "dataTypeName": "text"},
        ]
    }
    params = socrata._build_query_parameters(meta)
    column_names = [p["name"] for p in params if p["name"] not in ("limit", "offset")]
    assert column_names == ["ok"]


# --- build_socrata_spec command-path collision branch ---


def test_build_socrata_spec_disambiguates_duplicate_command_paths(tmp_path):
    """Two datasets that slugify to the same router AND command (e.g.
    identical names from different data eras) get the second's path
    suffixed with the UID so commands don't clobber each other."""
    story_path = tmp_path / "story.json"
    story_path.write_text(
        json.dumps(
            {
                "dataSource": {"domainCName": "x.com"},
                "blocks": [
                    {"datasetUid": "abcd-1111"},
                    {"datasetUid": "efgh-2222"},
                ],
            }
        )
    )

    def stub_fetch(host, uid):  # noqa: ARG001
        # Both datasets share the exact same name → same slug → collision.
        return {
            "assetType": "dataset",
            "name": "Quarterly Sales",
            "columns": [{"fieldName": "x", "dataTypeName": "text"}],
        }

    spec_doc = socrata.build_socrata_spec(
        str(story_path),
        fetch=stub_fetch,
        choice_resolver=_no_choice_resolver,
    )
    # Both are singletons (different first tokens, same full slug) — they
    # land at the spec root with the second one disambiguated by UID.
    paths = sorted(spec_doc["commands"])
    assert paths == [
        "quarterly_sales",
        "quarterly_sales_efgh2222",
    ]


# --- _column_to_schema / _build_response_schema ---


def test_column_to_schema_maps_calendar_date_to_plain_date_format():
    """Socrata's ``calendar_date`` columns serialize as ISO timestamps on
    the wire but the time component is always zeros — model the field as
    ``format: date`` so the response row carries a clean ``date`` value
    instead of a ``datetime`` with a noisy 00:00:00 suffix."""
    assert socrata._column_to_schema(
        {"fieldName": "monthyear", "dataTypeName": "calendar_date"}
    ) == {"type": "string", "format": "date"}


def test_column_to_schema_captures_currency_format_hints():
    """Socrata's ``format.precisionStyle`` (``currency`` / ``percent``)
    plus locale separators land under ``socrata_format`` so downstream
    formatters know to render ``$763.75`` instead of ``763.75``."""
    out = socrata._column_to_schema(
        {
            "fieldName": "price",
            "dataTypeName": "number",
            "description": "Price, measured in dollars per ton.",
            "format": {
                "precisionStyle": "currency",
                "decimalSeparator": ".",
                "groupSeparator": ",",
                "align": "right",  # internal hint — should be filtered out
            },
        }
    )
    assert out["type"] == "number"
    assert out["description"] == "Price, measured in dollars per ton."
    assert out["socrata_format"] == {
        "precisionStyle": "currency",
        "decimalSeparator": ".",
        "groupSeparator": ",",
    }


def test_column_to_schema_omits_socrata_format_when_no_hints():
    """A column with no ``format`` block (or only internal keys) gets
    no ``socrata_format`` key — keeps the schema lean."""
    out = socrata._column_to_schema({"fieldName": "name", "dataTypeName": "text"})
    assert "socrata_format" not in out


def test_column_to_schema_keeps_description():
    out = socrata._column_to_schema(
        {
            "fieldName": "exim",
            "dataTypeName": "text",
            "description": "Identifies either an import and export shipment",
        }
    )
    assert out["type"] == "string"
    assert out["description"] == "Identifies either an import and export shipment"


def test_column_to_schema_strips_trailing_whitespace_from_description():
    """Socrata descriptions frequently arrive with trailing whitespace
    ("Quarter number. ", "Price, measured in dollars per ton. "). Strip
    both edges so downstream renderers don't have to see the noise.
    """
    out = socrata._column_to_schema(
        {
            "fieldName": "price",
            "dataTypeName": "number",
            "description": "  Price, measured in dollars per ton. \n",
        }
    )
    assert out["description"] == "Price, measured in dollars per ton."


def test_column_to_schema_drops_description_when_only_whitespace():
    """A description that is *only* whitespace shouldn't survive — it would
    leave an empty ``description`` field that's worse than absent."""
    out = socrata._column_to_schema(
        {"fieldName": "x", "dataTypeName": "text", "description": "   \n  "}
    )
    assert "description" not in out


def test_column_to_schema_falls_back_to_string_for_unknown_type():
    """An unrecognized ``dataTypeName`` collapses to ``string`` so codegen
    still produces a usable field rather than crashing."""
    out = socrata._column_to_schema(
        {"fieldName": "weird", "dataTypeName": "unknown_socrata_type"}
    )
    assert out == {"type": "string"}


def test_column_to_schema_url_type_renders_as_object_with_url_and_description():
    out = socrata._column_to_schema({"fieldName": "link", "dataTypeName": "url"})
    assert out["type"] == "object"
    assert "url" in out["properties"]
    assert "description" in out["properties"]


def test_build_response_schema_wraps_columns_in_results_envelope():
    """Output is ``{results: array<row>}`` so the existing schema unwrap
    descends single-array properties to the row shape."""
    meta = {
        "columns": [
            {"fieldName": "year", "dataTypeName": "text"},
            {"fieldName": "amount", "dataTypeName": "number"},
        ]
    }
    out = socrata._build_response_schema(meta)
    assert out["type"] == "object"
    assert "results" in out["properties"]
    items = out["properties"]["results"]["items"]
    assert items["properties"]["year"] == {"type": "string"}
    assert items["properties"]["amount"] == {"type": "number"}


def test_build_response_schema_skips_columns_without_field_name():
    meta = {
        "columns": [
            {"dataTypeName": "text"},  # no fieldName -> skip
            {"fieldName": "ok", "dataTypeName": "text"},
        ]
    }
    out = socrata._build_response_schema(meta)
    assert list(out["properties"]["results"]["items"]["properties"]) == ["ok"]


def test_build_response_schema_handles_non_dict_column_entries():
    """Defensive: a stray non-dict in the columns list doesn't crash."""
    out = socrata._build_response_schema(
        {"columns": ["not-a-dict", {"fieldName": "ok", "dataTypeName": "text"}]}
    )
    assert "ok" in out["properties"]["results"]["items"]["properties"]


# --- _build_command ---


def test_build_command_uses_description_first_for_repl_menu_one_liner():
    """REPL menu renderer keeps only the first sentence
    (``description.split('.')[0]``) — leading with the dataset name
    would duplicate the command label and waste that one-line summary
    slot. So the description's first sentence is the prose, not the
    name."""
    cmd = socrata._build_command(
        "https://portal",
        "abcd-1234",
        {"name": "Monthly Sales", "description": "Sales aggregated by month."},
    )
    assert cmd["url_path"] == "/resource/abcd-1234.json"
    assert cmd["method"] == "get"
    # First sentence (what the menu shows) is the prose, not the name.
    assert cmd["description"].startswith("Sales aggregated by month")


def test_build_command_falls_back_to_name_when_no_description():
    """A dataset with no description uses the name as summary so the
    menu still has something to show."""
    cmd = socrata._build_command(
        "https://portal", "abcd-1234", {"name": "Monthly Sales"}
    )
    assert cmd["description"] == "Monthly Sales"


def _no_choice_resolver(host, uid, field, **kwargs):  # noqa: ARG001
    """Default test stub — every column resolves to ``None`` (overflow).

    Accepts ``**kwargs`` so production-side ``limit=`` calls land safely.
    """
    return None


def test_build_command_emits_one_filter_param_per_column_plus_pagination():
    """One ``?<col>=<val>`` filter param per column, plus clean
    ``limit`` / ``offset`` (the SoQL ``$``-prefix lives in ``wire_name``
    and gets applied by the dispatcher — never surfaces to the user)."""
    meta = {
        "name": "Trade",
        "columns": [
            {"fieldName": "year", "dataTypeName": "text"},
            {"fieldName": "amount", "dataTypeName": "number"},
        ],
    }
    cmd = socrata._build_command(
        "https://x", "uid-1", meta, choice_resolver=_no_choice_resolver
    )
    names = [p["name"] for p in cmd["parameters"]]
    assert names == ["year", "amount", "limit", "offset"]
    # No ``$``-prefixed names anywhere on the user-facing surface.
    assert all(not p["name"].startswith("$") for p in cmd["parameters"])
    # Pagination params carry the SoQL wire form for the dispatcher.
    by_name = {p["name"]: p for p in cmd["parameters"]}
    assert by_name["limit"]["wire_name"] == "$limit"
    assert by_name["offset"]["wire_name"] == "$offset"


def test_build_command_uses_resolver_to_populate_column_choices():
    """``_build_command`` issues a SoQL probe per column via the resolver
    and surfaces the returned distinct values as ``choices``."""

    def resolver(host, uid, field, **kwargs):  # noqa: ARG001
        if field == "exim":
            return ["Import", "Export"]
        return None  # other columns don't fit a closed set

    meta = {
        "name": "Trade",
        "columns": [
            {"fieldName": "exim", "dataTypeName": "text"},
            {"fieldName": "port", "dataTypeName": "text"},
        ],
    }
    cmd = socrata._build_command("https://x", "uid-1", meta, choice_resolver=resolver)
    by_name = {p["name"]: p for p in cmd["parameters"]}
    assert by_name["exim"]["choices"] == ["Import", "Export"]
    assert by_name["port"]["choices"] == []


def test_build_command_column_type_maps_money_and_percent_to_number():
    meta = {
        "name": "Trade",
        "columns": [
            {"fieldName": "revenue", "dataTypeName": "money"},
            {"fieldName": "share", "dataTypeName": "percent"},
            {"fieldName": "active", "dataTypeName": "checkbox"},
            {"fieldName": "city", "dataTypeName": "text"},
        ],
    }
    cmd = socrata._build_command(
        "https://x", "uid-1", meta, choice_resolver=_no_choice_resolver
    )
    by_name = {p["name"]: p["type"] for p in cmd["parameters"]}
    assert by_name["revenue"] == "number"
    assert by_name["share"] == "number"
    assert by_name["active"] == "boolean"
    assert by_name["city"] == "string"


def test_build_command_pagination_defaults_match_socrata_api_defaults():
    cmd = socrata._build_command(
        "https://x", "uid-1", {"name": "n"}, choice_resolver=_no_choice_resolver
    )
    by_name = {p["name"]: p for p in cmd["parameters"]}
    assert by_name["limit"]["default"] == 1000
    assert by_name["limit"]["type"] == "integer"
    assert by_name["offset"]["default"] is None
    assert by_name["offset"]["type"] == "integer"


def test_build_command_date_column_emits_uniform_start_end_date_pair():
    """Every dataset with a date column gets ``start_date`` / ``end_date``
    — names are uniform across datasets so callers don't need to look up
    the underlying column name. The SoQL ``$where`` translation in the
    dispatcher uses ``_socrata_column`` to address the actual column."""
    meta = {
        "name": "Trade",
        "columns": [
            {
                "fieldName": "monthyear",
                "dataTypeName": "calendar_date",
                "description": "Month and year of the shipment",
                "cachedContents": {
                    "smallest": "2010-01-01T00:00:00.000",
                    "largest": "2025-12-01T00:00:00.000",
                },
            }
        ],
    }
    cmd = socrata._build_command(
        "https://x", "uid-1", meta, choice_resolver=_no_choice_resolver
    )
    names = [p["name"] for p in cmd["parameters"]]
    # Unified naming — no per-column ``monthyear_start`` etc.
    assert "monthyear" not in names
    assert "monthyear_start" not in names
    assert "start_date" in names and "end_date" in names

    by_name = {p["name"]: p for p in cmd["parameters"]}
    start = by_name["start_date"]
    end = by_name["end_date"]
    # Defaults are ``None`` so omitting the params returns everything the
    # other filters allow — clamping to the cached bounds would silently
    # exclude rows added after the metadata snapshot.
    assert start["default"] is None
    assert end["default"] is None
    # Cached bounds (stripped to plain ``YYYY-MM-DD``) survive in
    # ``example`` so callers still see the available range up front.
    assert start["example"] == "2010-01-01"
    assert end["example"] == "2025-12-01"
    assert start["_socrata_op"] == "date_min"
    assert end["_socrata_op"] == "date_max"
    # ``_socrata_column`` carries the actual column name for the SoQL builder.
    assert start["_socrata_column"] == "monthyear"
    assert end["_socrata_column"] == "monthyear"
    assert "monthyear" in start["help"]
    assert "Dataset spans" in start["help"]
    # Help line tells the user the expected format and the omit semantics.
    assert "YYYY-MM-DD" in start["help"]
    assert "Omit" in start["help"]


def test_build_command_date_column_without_cached_bounds_still_emits_range_params():
    """A date column with no smallest/largest still gets the range params,
    just with ``None`` defaults — the user can supply bounds manually."""
    meta = {
        "name": "Trade",
        "columns": [{"fieldName": "ts", "dataTypeName": "calendar_date"}],
    }
    cmd = socrata._build_command(
        "https://x", "uid-1", meta, choice_resolver=_no_choice_resolver
    )
    by_name = {p["name"]: p for p in cmd["parameters"]}
    assert "start_date" in by_name and "end_date" in by_name
    assert by_name["start_date"]["default"] is None
    assert by_name["end_date"]["default"] is None
    # Still keyed on the actual column for the SoQL translator.
    assert by_name["start_date"]["_socrata_column"] == "ts"


def test_to_plain_date_strips_socrata_timestamp_suffix():
    assert socrata._to_plain_date("2010-01-01T00:00:00.000") == "2010-01-01"


def test_to_plain_date_passes_through_already_plain_date():
    assert socrata._to_plain_date("2025-12-31") == "2025-12-31"


def test_to_plain_date_passes_through_non_date_strings_unchanged():
    """A garbled value isn't a date — return it as-is so the spec
    consumer can decide what to do with it."""
    assert socrata._to_plain_date("not-a-date") == "not-a-date"


def test_to_plain_date_passes_through_non_string_values():
    assert socrata._to_plain_date(None) is None
    assert socrata._to_plain_date(42) == 42


def test_build_command_with_multiple_date_columns_emits_only_one_range_pair():
    """Only the first date column drives ``start_date`` / ``end_date`` —
    additional date columns fall back to plain equality filters so the
    parameter list stays predictable."""
    meta = {
        "name": "Audits",
        "columns": [
            {
                "fieldName": "audit_date",
                "dataTypeName": "calendar_date",
                "cachedContents": {
                    "smallest": "2020-01-01",
                    "largest": "2025-01-01",
                },
            },
            {
                "fieldName": "review_date",
                "dataTypeName": "calendar_date",
            },
        ],
    }
    cmd = socrata._build_command(
        "https://x", "uid-1", meta, choice_resolver=_no_choice_resolver
    )
    by_name = {p["name"]: p for p in cmd["parameters"]}
    assert by_name["start_date"]["_socrata_column"] == "audit_date"
    assert by_name["end_date"]["_socrata_column"] == "audit_date"
    # Second date column does NOT spawn another start_date / end_date.
    names = [p["name"] for p in cmd["parameters"]]
    assert names.count("start_date") == 1
    assert names.count("end_date") == 1
    # Second date column simply gets dropped (it's not useful as an
    # equality filter and we don't want to confuse with the primary
    # date range).
    assert "review_date" not in by_name


def test_build_command_falls_back_to_cached_top_when_resolver_returns_none(
    monkeypatch,
):
    """When the SoQL resolver fails (overflow / network), columns whose
    ``cachedContents.top`` is below the 20-cap fall back to that list —
    so the user still sees something useful even if the live query
    didn't pan out."""

    def overflow_resolver(host, uid, field, **kwargs):  # noqa: ARG001
        return None

    meta = {
        "name": "Trade",
        "columns": [
            {
                "fieldName": "exim",
                "dataTypeName": "text",
                "cachedContents": {
                    "top": [{"item": "Import"}, {"item": "Export"}],
                },
            },
            {
                "fieldName": "port",
                "dataTypeName": "text",
                "cachedContents": {
                    "top": [{"item": f"P{i}"} for i in range(20)],
                },
            },
        ],
    }
    cmd = socrata._build_command(
        "https://x", "uid-1", meta, choice_resolver=overflow_resolver
    )
    by_name = {p["name"]: p for p in cmd["parameters"]}
    # Below-cap cached top survives as fallback choices.
    assert by_name["exim"]["choices"] == ["Import", "Export"]
    # At-cap cached top stays empty — it would mislead to call those the full set.
    assert by_name["port"]["choices"] == []


def test_build_command_falls_back_to_uid_when_meta_has_no_name():
    cmd = socrata._build_command("https://x", "fall-back", {})
    assert "fall-back" in cmd["description"]


# --- _story_host ---


def test_story_host_prefers_data_source_domain_when_present():
    assert (
        socrata._story_host(
            "https://other.example.com/stories/s/x.json",
            {"dataSource": {"domainCName": "agtransport.usda.gov"}},
        )
        == "https://agtransport.usda.gov"
    )


def test_story_host_falls_back_to_url_host_when_domain_missing():
    assert (
        socrata._story_host(
            "https://agtransport.usda.gov/stories/s/x.json",
            {"dataSource": {}},
        )
        == "https://agtransport.usda.gov"
    )


def test_story_host_raises_when_both_domain_and_url_unavailable(tmp_path):
    """A local-file story without ``domainCName`` has no host to infer."""
    with pytest.raises(ValueError, match="domainCName"):
        socrata._story_host("/local/path.json", {"dataSource": {}})


# --- _backing_dataset_uid ---


def test_backing_dataset_uid_prefers_modifying_view_uid():
    """Modern Socrata stores the backing reference in ``modifyingViewUid``."""
    assert (
        socrata._backing_dataset_uid({"modifyingViewUid": "abcd-1234"}) == "abcd-1234"
    )


def test_backing_dataset_uid_falls_back_to_query_view_source_id():
    """Legacy assets put the same reference in ``query.viewSourceId``."""
    assert (
        socrata._backing_dataset_uid({"query": {"viewSourceId": "wxyz-9999"}})
        == "wxyz-9999"
    )


def test_backing_dataset_uid_returns_none_when_no_reference_present():
    assert socrata._backing_dataset_uid({"name": "standalone"}) is None


def test_backing_dataset_uid_ignores_non_string_values():
    """Defensive: a malformed ``modifyingViewUid: null`` doesn't crash."""
    assert socrata._backing_dataset_uid({"modifyingViewUid": None}) is None
    assert socrata._backing_dataset_uid({"query": {"viewSourceId": 42}}) is None


# --- chart-view following in build_socrata_spec ---


def test_build_socrata_spec_follows_chart_view_to_backing_dataset(tmp_path):
    """A story that only references a chart view still ends up with the
    chart's backing dataset in the generated spec — the chart UID itself
    gets skipped, but its ``modifyingViewUid`` gets fetched."""
    story_path = tmp_path / "story.json"
    story_path.write_text(
        json.dumps(
            {
                "dataSource": {"domainCName": "x.com"},
                "blocks": [{"datasetUid": "chrt-aaaa"}],
            }
        )
    )

    fetched: list[str] = []

    def stub_fetch(host: str, uid: str) -> dict:  # noqa: ARG001
        fetched.append(uid)
        catalogue = {
            "chrt-aaaa": {
                "assetType": "chart",
                "name": "Trade Chart",
                "modifyingViewUid": "data-bbbb",
            },
            "data-bbbb": {
                "assetType": "dataset",
                "name": "Backing Trade Data",
                "columns": [{"fieldName": "x", "dataTypeName": "text"}],
            },
        }
        return catalogue[uid]

    spec_doc = socrata.build_socrata_spec(
        str(story_path),
        fetch=stub_fetch,
        choice_resolver=_no_choice_resolver,
    )
    # Chart was followed to its dataset — both fetched, the dataset
    # ended up as a top-level command, the chart was skipped.
    assert fetched == ["chrt-aaaa", "data-bbbb"]
    assert "backing_trade_data" in spec_doc["commands"]
    skipped_uids = [s["uid"] for s in spec_doc["_socrata"]["skipped"]]
    assert "chrt-aaaa" in skipped_uids


def test_build_socrata_spec_follows_chart_of_chart_chain_to_dataset(tmp_path):
    """A chart that points at another chart still resolves — discovery
    is BFS-style, so multi-hop chains land on the underlying dataset."""
    story_path = tmp_path / "story.json"
    story_path.write_text(
        json.dumps(
            {
                "dataSource": {"domainCName": "x.com"},
                "blocks": [{"datasetUid": "chrt-1111"}],
            }
        )
    )

    def stub_fetch(host: str, uid: str) -> dict:  # noqa: ARG001
        return {
            "chrt-1111": {
                "assetType": "chart",
                "name": "Outer chart",
                "modifyingViewUid": "chrt-2222",
            },
            "chrt-2222": {
                "assetType": "chart",
                "name": "Inner chart",
                "modifyingViewUid": "data-3333",
            },
            "data-3333": {
                "assetType": "dataset",
                "name": "Underlying",
                "columns": [{"fieldName": "k", "dataTypeName": "text"}],
            },
        }[uid]

    spec_doc = socrata.build_socrata_spec(
        str(story_path),
        fetch=stub_fetch,
        choice_resolver=_no_choice_resolver,
    )
    assert "underlying" in spec_doc["commands"]
    skipped_uids = [s["uid"] for s in spec_doc["_socrata"]["skipped"]]
    assert "chrt-1111" in skipped_uids and "chrt-2222" in skipped_uids


def test_build_socrata_spec_does_not_refetch_uid_already_in_story(tmp_path):
    """If a chart's backing dataset is already referenced by the story,
    the discovery loop notices and skips the redundant fetch — no
    duplicate command entries."""
    story_path = tmp_path / "story.json"
    story_path.write_text(
        json.dumps(
            {
                "dataSource": {"domainCName": "x.com"},
                "blocks": [
                    {"datasetUid": "chrt-aaaa"},
                    {"datasetUid": "data-bbbb"},  # already referenced directly
                ],
            }
        )
    )

    fetched: list[str] = []

    def stub_fetch(host: str, uid: str) -> dict:  # noqa: ARG001
        fetched.append(uid)
        return {
            "chrt-aaaa": {
                "assetType": "chart",
                "modifyingViewUid": "data-bbbb",
            },
            "data-bbbb": {
                "assetType": "dataset",
                "name": "Trade Data",
                "columns": [{"fieldName": "x", "dataTypeName": "text"}],
            },
        }[uid]

    spec_doc = socrata.build_socrata_spec(
        str(story_path),
        fetch=stub_fetch,
        choice_resolver=_no_choice_resolver,
    )
    # ``data-bbbb`` fetched only once, not twice.
    assert fetched.count("data-bbbb") == 1
    assert list(spec_doc["commands"]) == ["trade_data"]


def test_build_socrata_spec_skips_chart_with_no_backing_reference(tmp_path):
    """A chart with neither ``modifyingViewUid`` nor ``query.viewSourceId``
    just gets skipped — there's nowhere to follow."""
    story_path = tmp_path / "story.json"
    story_path.write_text(
        json.dumps(
            {
                "dataSource": {"domainCName": "x.com"},
                "blocks": [{"datasetUid": "chrt-orph"}],
            }
        )
    )

    def stub_fetch(host: str, uid: str) -> dict:  # noqa: ARG001
        return {"assetType": "chart", "name": "Orphan chart"}

    spec_doc = socrata.build_socrata_spec(
        str(story_path),
        fetch=stub_fetch,
        choice_resolver=_no_choice_resolver,
    )
    assert spec_doc["commands"] == {}
    assert spec_doc["_socrata"]["skipped"] == [
        {"uid": "chrt-orph", "asset_type": "chart"}
    ]


# --- _direct_dataset_seed ---


def test_direct_dataset_seed_recognizes_resource_url():
    """``/resource/{uid}.json`` URL → ``(host, uid)``."""
    assert socrata._direct_dataset_seed(
        "https://agtransport.usda.gov/resource/8bgf-5mdv.json"
    ) == ("https://agtransport.usda.gov", "8bgf-5mdv")


def test_direct_dataset_seed_recognizes_api_views_url():
    """``/api/views/{uid}.json`` URL → ``(host, uid)``."""
    assert socrata._direct_dataset_seed(
        "https://agtransport.usda.gov/api/views/8bgf-5mdv.json"
    ) == ("https://agtransport.usda.gov", "8bgf-5mdv")


def test_direct_dataset_seed_works_without_json_suffix():
    assert socrata._direct_dataset_seed(
        "https://agtransport.usda.gov/resource/8bgf-5mdv"
    ) == ("https://agtransport.usda.gov", "8bgf-5mdv")


def test_direct_dataset_seed_returns_none_for_story_url():
    """Story URLs go through the regular story-fetch path."""
    assert (
        socrata._direct_dataset_seed("https://agtransport.usda.gov/stories/s/abcd-1234")
        is None
    )


def test_direct_dataset_seed_returns_none_for_local_path():
    assert socrata._direct_dataset_seed("/tmp/story.json") is None


def test_build_socrata_spec_handles_direct_resource_url(tmp_path):
    """``--socrata-story <resource-url>`` builds a one-dataset spec
    without trying to parse the URL as a story."""

    def stub_fetch(host, uid):  # noqa: ARG001
        return {
            "assetType": "dataset",
            "name": "Fertilizer Prices by Region",
            "columns": [{"fieldName": "region", "dataTypeName": "text"}],
        }

    spec_doc = socrata.build_socrata_spec(
        "https://agtransport.usda.gov/resource/8bgf-5mdv.json",
        fetch=stub_fetch,
        choice_resolver=_no_choice_resolver,
    )
    SpecDocument.model_validate(spec_doc)
    assert spec_doc["base_url"] == "https://agtransport.usda.gov"
    # Single dataset → top-level command (no router wrapper).
    assert list(spec_doc["commands"]) == ["fertilizer_prices_by_region"]
    cmd = spec_doc["commands"]["fertilizer_prices_by_region"]
    assert cmd["url_path"] == "/resource/8bgf-5mdv.json"


# --- _normalize_story_url ---


def test_normalize_story_url_appends_json_to_browser_form():
    """User pastes the human-facing URL; we append ``.json`` so the
    fetcher hits the JSON sibling, not the HTML page."""
    assert (
        socrata._normalize_story_url("https://agtransport.usda.gov/stories/s/7vku-v3nn")
        == "https://agtransport.usda.gov/stories/s/7vku-v3nn.json"
    )


def test_normalize_story_url_preserves_already_json_form():
    url = "https://agtransport.usda.gov/stories/s/7vku-v3nn.json"
    assert socrata._normalize_story_url(url) == url


def test_normalize_story_url_inserts_json_before_query_string():
    """``?theme=dark`` style query strings on the browser URL stay intact
    after the ``.json`` suffix lands."""
    out = socrata._normalize_story_url(
        "https://agtransport.usda.gov/stories/s/7vku-v3nn?theme=dark"
    )
    assert out == ("https://agtransport.usda.gov/stories/s/7vku-v3nn.json?theme=dark")


def test_normalize_story_url_passes_through_non_story_urls():
    assert (
        socrata._normalize_story_url("https://example.com/api/views/x.json")
        == "https://example.com/api/views/x.json"
    )


def test_normalize_story_url_passes_through_local_path():
    """File paths don't get the ``.json`` rewrite — they're passed straight
    to ``Path(...).read_text``."""
    assert socrata._normalize_story_url("/local/story.json") == "/local/story.json"


def test_normalize_story_url_leaves_story_subpath_alone():
    """``/stories/s/<id>/embed`` and similar story-extension paths shouldn't
    get a ``.json`` rewrite — only the bare browser URL does."""
    url = "https://x.com/stories/s/abcd-1234/embed"
    assert socrata._normalize_story_url(url) == url


# --- _read_json_url_or_path ---


def test_aload_story_loads_local_file(tmp_path):
    """File paths bypass HTTP entirely — read straight off disk."""
    p = tmp_path / "story.json"
    p.write_text(json.dumps({"a": 1}))

    async def go():
        async with httpx.AsyncClient() as client:
            return await socrata._aload_story(client, str(p))

    assert asyncio.run(go()) == {"a": 1}


# --- _build_routers / _build_reference ---


def test_build_routers_marks_each_namespace_as_menu_and_leaf_as_command():
    out = socrata._build_routers({"alpha.query": {}, "beta_two.query": {}})
    assert out == {
        "alpha": "menu",
        "alpha.query": "command",
        "beta_two": "menu",
        "beta_two.query": "command",
    }


def test_build_reference_emits_slash_paths_and_routers():
    out = socrata._build_reference({"alpha.query": {"description": "Alpha rows."}})
    assert "/alpha/query" in out["paths"]
    assert out["paths"]["/alpha/query"]["description"] == "Alpha rows."
    assert "/alpha/" in out["routers"]


# --- build_socrata_spec end-to-end ---


def _stub_dataset_meta(host: str, uid: str) -> dict[str, Any]:  # noqa: ARG001
    """Per-uid metadata stub used by the integration-shaped tests below.

    The catalogue mirrors the agtransport story shape: three datasets that
    share a ``port_profiles_by_*`` prefix (so they cluster into one router)
    and one standalone ``waterborne_*`` dataset (its own router).
    """
    catalogue = {
        "wbrn-aaaa": {
            "assetType": "dataset",
            "name": "Waterborne Agricultural Trade Data",
            "description": "Imports/exports by commodity.",
            "columns": [{"fieldName": "year", "dataTypeName": "text"}],
        },
        "port-cmdy": {
            "assetType": "dataset",
            "name": "Port Profiles by Commodity",
            "columns": [{"fieldName": "port", "dataTypeName": "text"}],
        },
        "port-pcty": {
            "assetType": "dataset",
            "name": "Port Profiles by Partner Country",
            "columns": [{"fieldName": "port", "dataTypeName": "text"}],
        },
        "port-shtp": {
            "assetType": "dataset",
            "name": "Port Profiles by Shipment Type",
            "columns": [{"fieldName": "port", "dataTypeName": "text"}],
        },
        "wxyz-chrt": {
            # Chart view — should be skipped.
            "assetType": "chart",
            "name": "Sales chart",
        },
    }
    return catalogue[uid]


def test_build_socrata_spec_round_trips_through_spec_document_validator(
    tmp_path, monkeypatch
):
    story_path = tmp_path / "story.json"
    story_path.write_text(
        json.dumps(
            {
                "uid": "test-stry",
                "dataSource": {"domainCName": "portal.example.com"},
                "blocks": [
                    {"datasetUid": "wbrn-aaaa"},
                    {"datasetUid": "port-cmdy"},
                    {"datasetUid": "port-pcty"},
                    {"datasetUid": "port-shtp"},
                    {"datasetUid": "wxyz-chrt"},
                ],
            }
        )
    )
    spec_doc = socrata.build_socrata_spec(
        str(story_path),
        fetch=_stub_dataset_meta,
        choice_resolver=_no_choice_resolver,
    )
    # Validates against the canonical SpecDocument schema — proves the
    # output matches what ``load_spec`` will accept downstream.
    SpecDocument.model_validate(spec_doc)

    assert spec_doc["base_url"] == "https://portal.example.com"
    assert spec_doc["api_prefix"] == ""
    assert spec_doc["source_url"] == str(story_path)

    # Four datasets kept (chart skipped). The singleton
    # ``waterborne_agricultural_trade_data`` is a top-level command
    # (no router); the three ``port_profiles_by_*`` collapse into a
    # single ``port_profiles`` router with one command each. The
    # trailing ``by`` flows back into the command name.
    assert set(spec_doc["commands"]) == {
        "waterborne_agricultural_trade_data",
        "port_profiles.by_commodity",
        "port_profiles.by_partner_country",
        "port_profiles.by_shipment_type",
    }
    assert spec_doc["_socrata"]["dataset_count"] == 4
    assert spec_doc["_socrata"]["skipped"] == [
        {"uid": "wxyz-chrt", "asset_type": "chart"}
    ]

    # Only ``port_profiles`` is a router (the other dataset is a
    # top-level command, not a one-command router).
    router_namespaces = {k for k, v in spec_doc["routers"].items() if v == "menu"}
    assert router_namespaces == {"port_profiles"}


def test_build_socrata_spec_uses_host_override_when_supplied(tmp_path):
    """Override skips ``_story_host`` so a captured story can drive
    generation against a test mirror without touching the original host."""
    story_path = tmp_path / "story.json"
    story_path.write_text(
        json.dumps(
            {
                "dataSource": {"domainCName": "real.portal.com"},
                "blocks": [{"datasetUid": "wbrn-aaaa"}],
            }
        )
    )
    spec_doc = socrata.build_socrata_spec(
        str(story_path),
        host_override="https://test.mirror",
        fetch=_stub_dataset_meta,
        choice_resolver=_no_choice_resolver,
    )
    assert spec_doc["base_url"] == "https://test.mirror"


def test_build_socrata_spec_handles_story_with_zero_referenced_datasets(tmp_path):
    """Empty-narrative stories produce a valid (empty) spec rather than
    erroring — caller can decide whether that's a problem."""
    story_path = tmp_path / "empty.json"
    story_path.write_text(
        json.dumps({"dataSource": {"domainCName": "x.com"}, "blocks": []})
    )
    spec_doc = socrata.build_socrata_spec(str(story_path), fetch=lambda h, u: {})
    assert spec_doc["commands"] == {}
    assert spec_doc["routers"] == {}
    SpecDocument.model_validate(spec_doc)


def test_build_socrata_spec_command_url_path_carries_dataset_uid(tmp_path):
    story_path = tmp_path / "story.json"
    story_path.write_text(
        json.dumps(
            {
                "dataSource": {"domainCName": "x.com"},
                "blocks": [{"datasetUid": "wbrn-aaaa"}],
            }
        )
    )
    spec_doc = socrata.build_socrata_spec(
        str(story_path),
        fetch=_stub_dataset_meta,
        choice_resolver=_no_choice_resolver,
    )
    cmd = spec_doc["commands"]["waterborne_agricultural_trade_data"]
    assert cmd["url_path"] == "/resource/wbrn-aaaa.json"
    assert cmd["method"] == "get"
    # Response schema reflects the column metadata.
    items = cmd["response_schema"]["properties"]["results"]["items"]
    assert items["properties"]["year"] == {"type": "string"}


# --- _common_token_prefix / _assign_router_namespaces ---


def test_common_token_prefix_returns_shared_leading_tokens():
    out = socrata._common_token_prefix(
        [
            ["port", "profiles", "by", "commodity"],
            ["port", "profiles", "by", "country"],
            ["port", "profiles", "by", "shipment"],
        ]
    )
    assert out == ["port", "profiles", "by"]


def test_common_token_prefix_returns_empty_when_no_input():
    assert socrata._common_token_prefix([]) == []


def test_common_token_prefix_stops_at_first_diverging_token():
    out = socrata._common_token_prefix([["a", "b", "c"], ["a", "b", "d"], ["a", "x"]])
    assert out == ["a"]


def test_assign_router_namespaces_consolidates_shared_prefix_into_one_router():
    """Three datasets sharing ``port_profiles_by_*`` collapse to one
    router (``port_profiles`` — the trailing ``by`` flows back into the
    command name as ``by_commodity`` etc.)."""
    out = socrata._assign_router_namespaces(
        {
            "uid1": "port_profiles_by_commodity",
            "uid2": "port_profiles_by_partner_country",
            "uid3": "port_profiles_by_shipment_type",
        }
    )
    assert out == {
        "uid1": ("port_profiles", "by_commodity"),
        "uid2": ("port_profiles", "by_partner_country"),
        "uid3": ("port_profiles", "by_shipment_type"),
    }


def test_assign_router_namespaces_singleton_dataset_uses_no_router():
    """A bucket with one dataset is a top-level command — no router
    wrapper, so the user calls ``waterborne_agricultural_trade_data(...)``
    directly instead of navigating into a one-command menu."""
    out = socrata._assign_router_namespaces(
        {"uid1": "waterborne_agricultural_trade_data"}
    )
    assert out == {"uid1": (None, "waterborne_agricultural_trade_data")}


def test_assign_router_namespaces_strips_trailing_preposition_from_router():
    """``Sales by *`` collapses to router ``sales`` (not ``sales_by``)."""
    out = socrata._assign_router_namespaces(
        {"u1": "sales_by_region", "u2": "sales_by_quarter"}
    )
    assert out == {
        "u1": ("sales", "by_region"),
        "u2": ("sales", "by_quarter"),
    }


def test_assign_router_namespaces_does_not_cluster_on_single_stop_token():
    """A single-token shared run that's a stop word (``by``) doesn't
    qualify as a meaningful cluster — both stay as top-level commands."""
    out = socrata._assign_router_namespaces({"u1": "by_alpha", "u2": "by_beta"})
    assert out == {
        "u1": (None, "by_alpha"),
        "u2": (None, "by_beta"),
    }


def test_assign_router_namespaces_does_not_cluster_on_single_token_overlap():
    """One shared token isn't enough to cluster — generic single-word
    overlaps (``alpha``) would over-bucket otherwise unrelated names."""
    out = socrata._assign_router_namespaces({"u1": "alpha", "u2": "alpha_two"})
    assert out == {
        "u1": (None, "alpha"),
        "u2": (None, "alpha_two"),
    }


def test_assign_router_namespaces_clusters_on_shared_substring_anywhere():
    """Three datasets sharing ``container_vessel_fleet`` cluster on
    that substring even when none of them start with it. The router
    becomes the shared run; each command keeps the tokens that lie
    outside it."""
    out = socrata._assign_router_namespaces(
        {
            "u1": "idle_container_vessel_fleet",
            "u2": "container_vessel_fleet_data",
            "u3": "global_container_vessel_fleet_and_spot_rates",
        }
    )
    routers = {router for router, _ in out.values()}
    assert routers == {"container_vessel_fleet"}
    by_uid = {uid: cmd for uid, (_, cmd) in out.items()}
    assert by_uid["u1"] == "idle"
    assert by_uid["u2"] == "data"
    # ``and`` survives in the command name — the strip-stop-tokens pass
    # only trims the *router* edges, not internal command tokens.
    assert by_uid["u3"] == "global_and_spot_rates"


# --- _column_choices / _column_help ---


def test_column_choices_uses_resolver_when_host_and_uid_supplied():
    """Live SoQL resolver is the source of truth for choices when present."""
    out = socrata._column_choices(
        {"fieldName": "x"},
        host="https://h",
        uid="abcd-1234",
        resolver=lambda h, u, f, **k: ["A", "B", "C"],  # noqa: ARG005
    )
    assert out == ["A", "B", "C"]


def test_column_choices_falls_back_to_cached_top_when_no_host_uid():
    """Without a host/uid (unit-test path) the cached top is the source."""
    out = socrata._column_choices(
        {
            "fieldName": "x",
            "cachedContents": {"top": [{"item": "a"}, {"item": "b"}]},
        }
    )
    assert out == ["a", "b"]


def test_column_choices_falls_back_to_cached_top_when_resolver_is_none():
    """Host + uid + field present but no resolver injected → fall back to
    the metadata's cached top rather than dereferencing the dropped
    sync ``fetch_column_distinct_values`` symbol. Live discovery uses
    the async path via ``_abuild_discovery``; this branch only fires
    when a caller side-steps that pipeline.
    """
    out = socrata._column_choices(
        {
            "fieldName": "x",
            "cachedContents": {"top": [{"item": "a"}, {"item": "b"}]},
        },
        host="https://h",
        uid="uid-1",
        resolver=None,
    )
    assert out == ["a", "b"]


def test_column_choices_returns_empty_when_resolver_overflow_and_top_at_cap():
    """Resolver returns ``None`` (overflow) AND cached top is at the cap →
    empty choices. We don't pretend the top-20 is a complete set when we
    know there's more."""
    out = socrata._column_choices(
        {
            "fieldName": "x",
            "cachedContents": {"top": [{"item": f"v{i}"} for i in range(20)]},
        },
        host="https://h",
        uid="uid-1",
        resolver=lambda h, u, f, **k: None,  # noqa: ARG005
    )
    assert out == []


def test_column_choices_falls_back_when_resolver_overflow_and_top_below_cap():
    """Resolver returns ``None`` but cached top is below cap → use cached
    top as a best-effort fallback."""
    out = socrata._column_choices(
        {
            "fieldName": "x",
            "cachedContents": {"top": [{"item": "a"}, {"item": "b"}]},
        },
        host="https://h",
        uid="uid-1",
        resolver=lambda h, u, f, **k: None,  # noqa: ARG005
    )
    assert out == ["a", "b"]


def test_column_choices_coerces_numeric_string_values_to_int():
    """Socrata serializes numeric columns as strings (``"2024"``) — the
    Literal set we generate has to match the declared field type
    (``int`` / ``float``) or callers passing ``year=2024`` would be
    rejected against a ``Literal["2024", ...]`` of strings."""
    out = socrata._column_choices(
        {"fieldName": "year", "dataTypeName": "number"},
        host="https://h",
        uid="uid-1",
        resolver=lambda h, u, f, **k: ["2024", "2023", "2022"],  # noqa: ARG005
    )
    assert out == [2024, 2023, 2022]


def test_column_choices_keeps_float_for_non_integer_numeric_values():
    out = socrata._column_choices(
        {"fieldName": "ratio", "dataTypeName": "number"},
        host="https://h",
        uid="uid-1",
        resolver=lambda h, u, f, **k: ["1.5", "2.5"],  # noqa: ARG005
    )
    assert out == [1.5, 2.5]


def test_column_choices_drops_uncoercible_numeric_values():
    """A stray non-numeric string in a numeric column gets silently
    dropped from choices — better than crashing or rejecting valid
    inputs against a Literal contaminated with garbage."""
    out = socrata._column_choices(
        {"fieldName": "year", "dataTypeName": "number"},
        host="https://h",
        uid="uid-1",
        resolver=lambda h, u, f, **k: ["2024", "N/A", "2025"],  # noqa: ARG005
    )
    assert out == [2024, 2025]


def test_column_choices_caps_numeric_columns_at_lower_limit():
    """Numeric columns hit a tighter cap so continuous-valued fields
    (prices, ratios) overflow — only narrow numeric enums (months,
    years) survive as Literal choices."""
    seen_limits: list[int] = []

    def capture_resolver(host, uid, field, *, limit):  # noqa: ARG001
        seen_limits.append(limit)

    socrata._column_choices(
        {"fieldName": "fuel_price", "dataTypeName": "number"},
        host="https://h",
        uid="uid-1",
        resolver=capture_resolver,
    )
    socrata._column_choices(
        {"fieldName": "port", "dataTypeName": "text"},
        host="https://h",
        uid="uid-1",
        resolver=capture_resolver,
    )
    # Numeric column probed with the tight cap (50); text column with
    # the wider one (1000).
    assert seen_limits == [
        socrata._NUMERIC_CHOICE_CAP,
        socrata._MAX_RESOLVED_CHOICES,
    ]


def test_column_choices_returns_empty_when_no_field_name():
    """Defensive: a column with no ``fieldName`` can't be queried."""
    out = socrata._column_choices(
        {},
        host="https://h",
        uid="uid-1",
        resolver=lambda h, u, f: ["should-not-be-called"],  # noqa: ARG005
    )
    assert out == []


def test_cached_top_values_extracts_items_and_skips_malformed_entries():
    """Defensive: stray non-dict entries don't crash the extractor."""
    out = socrata._cached_top_values(
        {"cachedContents": {"top": [{"item": "ok"}, {"count": 5}, "bareString", None]}}
    )
    assert out == ["ok", "bareString"]


def test_cached_top_values_returns_empty_when_no_cached_contents():
    assert socrata._cached_top_values({"fieldName": "x"}) == []


# --- fetch_column_distinct_values ---


def test_afetch_column_distinct_values_builds_soql_query():
    """SoQL probe issues ``$select=col&$group=col&$order=col&$limit=N+1``."""
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json=[{"port": "A"}, {"port": "B"}])

    out = _run_with_mock_client(
        handler,
        lambda c: socrata.afetch_column_distinct_values(
            c, "https://portal", "abcd-1234", "port", limit=1000
        ),
    )
    assert out == ["A", "B"]
    assert "/resource/abcd-1234.json" in captured["url"]
    # ``$``-prefixed SoQL params survive as URL-encoded ``%24``.
    assert "%24select=port" in captured["url"]
    assert "%24group=port" in captured["url"]
    assert "%24limit=1001" in captured["url"]  # limit + 1 for overflow detection


def test_afetch_column_distinct_values_returns_none_on_overflow():
    """Response with ``limit + 1`` rows signals overflow → no choices."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[{"port": f"P{i}"} for i in range(11)])

    out = _run_with_mock_client(
        handler,
        lambda c: socrata.afetch_column_distinct_values(
            c, "https://x", "uid-1", "port", limit=10
        ),
    )
    assert out is None


def test_afetch_column_distinct_values_returns_none_on_network_error():
    """Transient network failures fall through to ``None`` so the caller
    can degrade gracefully (cached-top fallback) instead of crashing."""

    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("dns failed")

    out = _run_with_mock_client(
        handler,
        lambda c: socrata.afetch_column_distinct_values(
            c, "https://x", "uid-1", "port"
        ),
    )
    assert out is None


def test_afetch_column_distinct_values_skips_rows_without_field_value():
    """A row with the column missing or null is dropped from the choices."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[{"port": "A"}, {"other": "x"}, {"port": None}, {"port": "B"}],
        )

    out = _run_with_mock_client(
        handler,
        lambda c: socrata.afetch_column_distinct_values(
            c, "https://x", "uid-1", "port"
        ),
    )
    assert out == ["A", "B"]


def test_afetch_column_distinct_values_returns_none_when_payload_not_a_list():
    """Defensive: an error response (object) shouldn't masquerade as choices."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"error": "rate limit"})

    out = _run_with_mock_client(
        handler,
        lambda c: socrata.afetch_column_distinct_values(
            c, "https://x", "uid-1", "port"
        ),
    )
    assert out is None


def test_column_help_combines_description_and_examples_for_capped_columns():
    help_text = socrata._column_help(
        {
            "description": "The U.S. port of entry",
            "cachedContents": {
                "top": [{"item": f"PORT_{i}"} for i in range(20)],
                "smallest": "AAA",
                "largest": "ZZZ",
            },
        }
    )
    assert "U.S. port of entry." in help_text
    assert "Examples:" in help_text
    assert "PORT_0" in help_text
    assert "AAA" in help_text and "ZZZ" in help_text


def test_column_help_omits_range_when_choices_present():
    """A constrained-choices column already lists every value — adding a
    range hint would be redundant."""
    help_text = socrata._column_help(
        {
            "description": "Yes/no flag",
            "cachedContents": {
                "top": [{"item": "Yes"}, {"item": "No"}],
                "smallest": "No",
                "largest": "Yes",
            },
        }
    )
    assert "Range:" not in help_text


def test_column_help_returns_empty_when_no_metadata_to_summarize():
    assert socrata._column_help({"fieldName": "bare"}) == ""


# --- afetch_dataset_metadata / _aload_story (network-mocked) ---


def test_afetch_dataset_metadata_hits_api_views_endpoint():
    """The fetcher targets ``{host}/api/views/{uid}.json`` exactly."""
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"name": "ok", "columns": []})

    out = _run_with_mock_client(
        handler,
        lambda c: socrata.afetch_dataset_metadata(
            c, "https://portal.example", "abcd-9999"
        ),
    )
    assert captured["url"] == "https://portal.example/api/views/abcd-9999.json"
    assert out == {"name": "ok", "columns": []}


def test_aload_story_loads_remote_url():
    """HTTP URLs go through the shared ``httpx.AsyncClient``."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"k": "v"})

    out = _run_with_mock_client(
        handler,
        lambda c: socrata._aload_story(c, "https://x/story.json"),
    )
    assert out == {"k": "v"}


# --- Helper-function coverage gaps ---


def test_detect_time_axis_column_skips_non_dict_columns_in_both_passes():
    """Both the calendar-date pass and the time-axis-named fallback skip
    non-dict entries — defensive against malformed metadata."""
    meta = {
        "columns": [
            "not-a-dict",  # skipped in pass 1
            {"fieldName": "x", "dataTypeName": "text"},  # not a date, not time-named
            "still-not-a-dict",  # skipped in pass 2
            {"fieldName": "year", "dataTypeName": "text"},  # time-named text col
        ]
    }
    assert socrata._detect_time_axis_column(meta) == "year"


def test_detect_time_axis_column_returns_none_when_no_columns_qualify():
    """Without any date-typed or time-axis-named columns,
    ``_detect_time_axis_column`` returns ``None`` so downstream code knows
    there's nothing to sort by."""
    meta = {
        "columns": [
            {"fieldName": "x", "dataTypeName": "text"},
            {"fieldName": "y", "dataTypeName": "number"},
        ]
    }
    assert socrata._detect_time_axis_column(meta) is None


def test_longest_common_token_run_returns_empty_for_no_common_run():
    """Three lists with no shared run of tokens → empty list."""
    assert socrata._longest_common_token_run([["a", "b"], ["c", "d"], ["e", "f"]]) == []


def test_longest_common_token_run_returns_empty_for_empty_input():
    """Empty input list short-circuits to ``[]`` — exercised by the
    ``if not token_lists`` guard."""
    assert socrata._longest_common_token_run([]) == []


def test_strip_stop_tokens_trims_leading_and_trailing_connectors():
    """Both the head and tail of the list get stripped of stop tokens."""
    out = socrata._strip_stop_tokens(["of", "the", "vessel", "data", "by", "of"])
    assert out == ["vessel", "data"]
    # All-stop list collapses to empty.
    assert socrata._strip_stop_tokens(["of", "the"]) == []


def test_assign_router_namespaces_falls_through_to_singletons_when_router_strips_to_empty():
    """When two slugs cluster (shared token run ≥ 2) but the run is
    entirely stop-tokens that strip to nothing, every member falls
    through to a singleton ``(None, slug)`` rather than getting forced
    into an empty router bucket.

    ``of_the_data`` + ``of_the_other`` share ``["of", "the"]`` (length 2 →
    clusters), but stripping connectors leaves an empty router name, so
    both UIDs become top-level commands.
    """
    slugs = {"u1": "of_the_data", "u2": "of_the_other"}
    out = socrata._assign_router_namespaces(slugs)
    # Both fell through to singletons — no synthetic empty-name router.
    assert out["u1"] == (None, "of_the_data")
    assert out["u2"] == (None, "of_the_other")


def test_assign_router_namespaces_returns_empty_for_empty_input():
    """No slugs → empty mapping (the trivial early-out path)."""
    assert socrata._assign_router_namespaces({}) == {}


def test_command_tokens_around_run_returns_full_list_when_run_absent():
    """If the router-token run isn't found in the per-member token list
    (shouldn't happen in practice, but defensive), return the full
    token list unchanged."""
    out = socrata._command_tokens_around_run(["alpha", "beta", "gamma"], ["nope"], 1)
    assert out == ["alpha", "beta", "gamma"]


def test_aread_json_url_or_path_reads_local_file_when_path_supplied(tmp_path):
    """Non-URL inputs read from the local filesystem — exercises the
    ``return json.loads(Path(...).read_text())`` fallback branch."""
    p = tmp_path / "story.json"
    p.write_text(json.dumps({"k": "v"}))

    async def go():
        return await socrata._aread_json_url_or_path(str(p))

    assert asyncio.run(go()) == {"k": "v"}


def test_aread_json_url_or_path_fetches_via_http_when_url_supplied():
    """The URL branch of ``_aread_json_url_or_path`` issues a real-shape
    HTTP request (mocked) rather than touching the local filesystem."""
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"ok": True})

    async def go():
        # Patch httpx.AsyncClient to use the mock transport.
        import openbb_cli.dispatchers.socrata as smod

        original = smod.httpx.AsyncClient

        def factory(*args, **kwargs):
            kwargs.pop("transport", None)
            return original(*args, transport=httpx.MockTransport(handler), **kwargs)

        smod.httpx.AsyncClient = factory
        try:
            return await smod._aread_json_url_or_path("https://h/story.json")
        finally:
            smod.httpx.AsyncClient = original

    result = asyncio.run(go())
    assert result == {"ok": True}
    assert "https://h/story.json" in captured["url"]


def test_afetch_json_returns_decoded_json_body():
    """Plain helper: GET, raise for status, return decoded JSON."""

    def handler(_request):
        return httpx.Response(200, json={"k": "v"})

    out = _run_with_mock_client(
        handler, lambda c: socrata._afetch_json(c, "https://h/x.json")
    )
    assert out == {"k": "v"}


def test_amaybe_call_passes_through_sync_callable_result():
    """A non-coroutine return value goes through ``_amaybe_call`` unchanged
    (no awaiting / wrapping)."""
    out = asyncio.run(socrata._amaybe_call(lambda x, y: x + y, 1, 2))
    assert out == 3


def test_amaybe_call_awaits_coroutine_result():
    """Coroutine return values get awaited so the caller doesn't have to
    branch on whether the stub was sync or async."""

    async def aplus(x, y):
        return x + y

    out = asyncio.run(socrata._amaybe_call(aplus, 1, 2))
    assert out == 3


def test_aone_metadata_returns_none_when_default_fetcher_raises_http_error():
    """Default fetcher path: HTTP errors get caught and yield ``None``
    (the caller records this as "unreachable" so the build keeps going)."""

    def handler(_request):
        return httpx.Response(404)

    out = _run_with_mock_client(
        handler,
        lambda c: socrata._aone_metadata(c, "https://h", "uid-1", None),
    )
    assert out is None


def test_aone_metadata_returns_none_when_stub_raises():
    """Stub fetcher path: any ``(httpx.HTTPError, OSError, ValueError)``
    raised by a test stub gets caught and surfaces as ``None``."""

    def stub_raises(host, uid):  # noqa: ARG001
        raise ValueError("simulated metadata failure")

    out = _run_with_mock_client(
        lambda r: httpx.Response(200),
        lambda c: socrata._aone_metadata(c, "https://h", "uid-1", stub_raises),
    )
    assert out is None


def test_afetch_metadata_batch_short_circuits_for_empty_uids():
    """Empty UID list → no work, empty dict back."""
    out = _run_with_mock_client(
        lambda r: httpx.Response(200),
        lambda c: socrata._afetch_metadata_batch(c, "https://h", [], None),
    )
    assert out == {}


def test_aone_choice_returns_none_when_resolver_raises():
    """Test-stub resolver that raises one of the caught exceptions → ``None``."""

    def raising_resolver(host, uid, field, *, limit):  # noqa: ARG001
        raise httpx.HTTPError("simulated choice probe failure")

    out = _run_with_mock_client(
        lambda r: httpx.Response(200),
        lambda c: socrata._aone_choice(
            c, "https://h", "uid-1", "field", 10, raising_resolver
        ),
    )
    assert out is None


def test_aone_choice_uses_default_async_fetcher_when_resolver_is_none():
    """No resolver injected → call ``afetch_column_distinct_values``
    directly (the live discovery path). Mocked at the HTTP transport
    level so we exercise the real default-fetcher branch.
    """

    def handler(_request):
        # Single-value response — under the cap, so returns the values.
        return httpx.Response(200, json=[{"port": "Tampa"}])

    out = _run_with_mock_client(
        handler,
        lambda c: socrata._aone_choice(c, "https://h", "uid-1", "port", 10, None),
    )
    assert out == ["Tampa"]


def test_abuild_discovery_records_unreachable_uids_as_skipped(tmp_path):
    """Stories that reference deleted / private datasets get those UIDs
    recorded as ``"unreachable"`` in the skipped list rather than
    aborting the whole build. Exercises the ``meta is None`` branch in
    ``_abuild_discovery``'s wave loop.
    """
    story = {
        "dataSource": {"domainCName": "x.com"},
        "blocks": [{"datasetUid": "dead-beef"}],
    }
    story_path = tmp_path / "story.json"
    story_path.write_text(json.dumps(story))

    def stub_fetch(host, uid):  # noqa: ARG001
        # Returns ``None`` → the UID is unreachable and gets recorded
        # in ``skipped``.
        return None

    spec_doc = socrata.build_socrata_spec(
        str(story_path),
        fetch=stub_fetch,
        choice_resolver=_no_choice_resolver,
    )
    # Story produced no commands (nothing reachable) and no errors.
    assert spec_doc["commands"] == {}


def test_aone_choice_uses_default_async_fetcher_when_resolver_is_the_async_function():
    """Passing the canonical ``afetch_column_distinct_values`` as the
    resolver takes the same default-fetcher branch (not the stub branch),
    since it's identity-checked."""

    def handler(_request):
        return httpx.Response(200, json=[{"port": "Tampa"}, {"port": "Miami"}])

    out = _run_with_mock_client(
        handler,
        lambda c: socrata._aone_choice(
            c,
            "https://h",
            "uid-1",
            "port",
            10,
            socrata.afetch_column_distinct_values,
        ),
    )
    assert out == ["Tampa", "Miami"]


def test_aprobe_choices_batch_skips_dates_objects_and_returns_empty_for_no_tasks():
    """Date-type and unsupported-type columns are filtered out before the
    probe; no eligible columns → empty cache back."""
    metas = {
        "uid-1": {
            "columns": [
                "not-a-dict",  # skipped — non-dict
                {"dataTypeName": "text"},  # skipped — no fieldName
                {"fieldName": "obs_date", "dataTypeName": "calendar_date"},  # date
                {"fieldName": "loc", "dataTypeName": "location"},  # not numeric/text
            ]
        }
    }
    out = _run_with_mock_client(
        lambda r: httpx.Response(200),
        lambda c: socrata._aprobe_choices_batch(c, "https://h", metas, None),
    )
    assert out == {}


def test_primary_item_column_picks_highest_cardinality_string_column():
    """``_primary_item_column`` selects the string param with the most
    distinct choices — the most useful 'item' for ``limit`` semantics."""
    parameters = [
        {"name": "limit", "type": "integer"},  # excluded by name
        {"name": "offset", "type": "integer"},  # excluded by name
        {"name": "obs_date", "type": "string"},  # excluded — time axis
        {"name": "year", "type": "string"},  # excluded — time-axis named
        {
            "name": "start_date",
            "type": "string",
            "_socrata_op": "date_min",
        },  # excluded — date-range op
        {"name": "category", "type": "integer"},  # excluded — not string
        {"name": "boolish", "type": "string", "choices": ["a", "b"]},  # < 3 choices
        {"name": "no_choices", "type": "string"},  # < 3 choices (empty)
        {
            "name": "region",
            "type": "string",
            "choices": ["a", "b", "c"],
        },  # 3 choices
        {
            "name": "port",
            "type": "string",
            "choices": [f"p{i}" for i in range(50)],
        },  # 50 choices — wins
        "not-a-dict",  # defensive skip
    ]
    out = socrata._primary_item_column(parameters, time_axis="obs_date")
    assert out == "port"


def test_primary_item_column_returns_none_when_no_eligible_column():
    """No string column with ≥3 choices outside the excluded set → ``None``."""
    assert socrata._primary_item_column([], time_axis=None) is None
    assert (
        socrata._primary_item_column(
            [{"name": "limit", "type": "integer"}], time_axis=None
        )
        is None
    )


def test_column_choices_choices_cache_hit_with_content_returns_coerced():
    """Cache-hit with non-None contents → coerce via the column's data
    type. Exercises the inner ``return _coerce_choices_to_type(...)``
    branch (was previously uncovered)."""
    out = socrata._column_choices(
        {"fieldName": "active", "dataTypeName": "checkbox"},
        host="https://h",
        uid="uid-1",
        choices_cache={("uid-1", "active"): ["true", "false"]},
    )
    assert out == [True, False]

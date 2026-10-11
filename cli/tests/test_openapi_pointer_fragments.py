"""URI-fragment references share local and external pointer semantics."""

import json
from contextlib import contextmanager

import httpx
import pytest

from openbb_cli.dispatchers.openapi_schema import (
    _bundle_external_refs,
    _resolve_json_pointer,
    build_parser_from_operation,
    resolve_ref,
)


@pytest.mark.parametrize(
    "fragment", ["/defs/limit%20param", "/parameters/0", "/defs/a~1b~0c"]
)
def test_local_reference_preserves_typed_parameters(fragment):
    parameter = {"name": "limit", "in": "query", "schema": {"type": "integer"}}
    spec = {
        "defs": {"limit param": parameter, "a/b~c": parameter},
        "parameters": [parameter],
    }
    assert resolve_ref(spec, "#" + fragment) == parameter
    parser = build_parser_from_operation(
        {"parameters": [{"$ref": "#" + fragment}]}, spec
    )
    assert parser.parse_args(["--limit", "7"]).limit == 7


@pytest.mark.parametrize("index", ["-1", "01", "+0", " 0", "١", "1", "nope"])
def test_noncanonical_or_missing_list_reference_is_rejected(index):
    spec = {"parameters": [{"type": "integer"}]}
    assert resolve_ref(spec, "#/parameters/" + index) == {}
    with pytest.raises((ValueError, IndexError)):
        _resolve_json_pointer(spec, "/parameters/" + index)


@pytest.mark.parametrize(
    "fragment", ["/defs/limit%20param", "/parameters/0", "/defs/a~1b~0c"]
)
def test_external_reference_has_local_pointer_parity(monkeypatch, fragment):
    parameter = {"name": "limit", "in": "query", "schema": {"type": "integer"}}
    doc = {
        "defs": {"limit param": parameter, "a/b~c": parameter},
        "parameters": [parameter],
    }

    @contextmanager
    def stream(_method, url, **_kwargs):
        yield httpx.Response(
            200, content=json.dumps(doc), request=httpx.Request("GET", url)
        )

    monkeypatch.setattr(httpx, "stream", stream)
    result = _bundle_external_refs(
        {"parameter": {"$ref": "defs.json#" + fragment}},
        "https://api.example/root.json",
        timeout=1,
        headers={},
    )
    assert result["parameter"] == resolve_ref(doc, "#" + fragment)


def test_dictionary_numeric_keys_and_missing_targets_keep_existing_semantics():
    spec = {"defs": {"01": {"type": "integer"}}}
    assert resolve_ref(spec, "#/defs/01") == {"type": "integer"}
    assert resolve_ref(spec, "#/missing") == {}
    assert resolve_ref(spec, "https://elsewhere.example/spec.json#/defs/01") == {}
    assert resolve_ref(spec, "#anchor") == {}

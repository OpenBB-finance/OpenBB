"""Tests for openbb_cli.dispatchers.runtime — argv parsing, run_argv, run_batch."""

from __future__ import annotations

import io
import json
from typing import Any

import pytest

from openbb_cli.dispatchers.protocol import Request, Response, ResponseError
from openbb_cli.dispatchers.runtime import (
    DEFAULT_BATCH_CONCURRENCY,
    build_parser,
    parse_argv,
    run_argv,
    run_batch,
)


def test_parse_argv_basic():
    req = parse_argv(["economy.gdp"])
    assert req.command == "economy.gdp"
    assert req.params == {}


def test_parse_argv_empty_raises():
    with pytest.raises(SystemExit):
        parse_argv([])


def test_parse_argv_kv_equals_form():
    req = parse_argv(["x", "--symbol=AAPL", "--limit=10"])
    assert req.params == {"symbol": "AAPL", "limit": 10}


def test_parse_argv_kv_space_form():
    req = parse_argv(["x", "--symbol", "AAPL"])
    assert req.params == {"symbol": "AAPL"}


def test_parse_argv_bool_flag_no_value():
    req = parse_argv(["x", "--verbose"])
    assert req.params == {"verbose": True}


def test_parse_argv_kv_dash_normalized_to_underscore():
    req = parse_argv(["x", "--start-date=2024-01-01"])
    assert req.params == {"start_date": "2024-01-01"}


def test_parse_argv_literal_eval_for_lists_and_dicts():
    req = parse_argv(["x", "--items=[1, 2, 3]", "--map={'a': 1}", "--flag=true"])
    assert req.params == {"items": [1, 2, 3], "map": {"a": 1}, "flag": True}


def test_parse_argv_unexpected_positional():
    with pytest.raises(SystemExit):
        parse_argv(["cmd", "stray"])


class _FakeDispatcher:
    """Records the request and returns a configurable Response."""

    def __init__(self, response: Response | None = None) -> None:
        self.response = response or Response(ok=True, result={"k": 1})
        self.requests: list[Request] = []
        self.closed = False

    async def dispatch(self, request: Request) -> Response:  # noqa: D401
        self.requests.append(request)
        return Response(
            id=request.id,
            ok=self.response.ok,
            result=self.response.result,
            error=self.response.error,
        )

    async def aclose(self) -> None:
        self.closed = True


def test_run_argv_success_writes_json_and_returns_zero(capsys):
    d = _FakeDispatcher()
    rc = run_argv(d, ["economy.gdp", "--provider=oecd"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    payload = json.loads(out)
    assert payload["ok"] is True
    assert d.requests[0].command == "economy.gdp"
    assert d.requests[0].params == {"provider": "oecd"}


def test_run_argv_failure_returns_one(capsys):
    d = _FakeDispatcher(
        Response(ok=False, error=ResponseError(type="X", message="nope"))
    )
    rc = run_argv(d, ["economy.gdp"])
    out = capsys.readouterr().out.strip()
    assert rc == 1
    payload = json.loads(out)
    assert payload["ok"] is False
    assert payload["error"]["type"] == "X"


def test_run_argv_serializes_non_json_values_via_default_str(capsys):
    """Non-JSON-serializable nested values (figures, datetimes, custom objs) coerce to repr.

    Regression: ``openbb equity.price.historical --provider yfinance`` exploded with
    ``PydanticSerializationError: Unable to serialize unknown type: OpenBBFigure``
    because the chart field carried a non-serializable object. The runtime now
    routes through ``json.dumps(..., default=str)``.
    """

    class NonSerializable:
        def __repr__(self):
            return "<figure-stand-in>"

    d = _FakeDispatcher(
        Response(ok=True, result={"chart": NonSerializable(), "results": [{"a": 1}]})
    )
    rc = run_argv(d, ["foo"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    payload = json.loads(out)
    assert payload["ok"] is True
    assert payload["result"]["chart"] == "<figure-stand-in>"
    assert payload["result"]["results"] == [{"a": 1}]


def test_run_batch_serializes_non_json_values_via_default_str():
    """Same default=str fallback for the batch loop's NDJSON writer."""

    class NonSerializable:
        def __repr__(self):
            return "<fig>"

    d = _FakeDispatcher(Response(ok=True, result={"chart": NonSerializable()}))
    reader = io.StringIO(_ndjson({"id": "a", "command": "x"}))
    writer = io.StringIO()
    rc = run_batch(d, reader=reader, writer=writer, concurrency=1)
    assert rc == 0
    line = json.loads(writer.getvalue().strip())
    assert line["result"]["chart"] == "<fig>"


def _ndjson(*requests: dict[str, Any]) -> str:
    return "\n".join(json.dumps(r) for r in requests) + "\n"


def test_run_batch_dispatches_each_line_and_writes_responses():
    d = _FakeDispatcher()
    reader = io.StringIO(
        _ndjson(
            {"id": "a", "command": "x", "params": {"k": 1}},
            {"id": "b", "command": "y"},
        )
    )
    writer = io.StringIO()
    rc = run_batch(d, reader=reader, writer=writer, concurrency=2)
    assert rc == 0
    lines = [ln for ln in writer.getvalue().splitlines() if ln]
    payloads = [json.loads(ln) for ln in lines]
    ids = sorted(p["id"] for p in payloads)
    assert ids == ["a", "b"]
    assert d.closed is True


def test_run_batch_skips_blank_lines():
    d = _FakeDispatcher()
    reader = io.StringIO(
        "\n"
        + _ndjson({"id": "1", "command": "ping"})
        + "\n"
        + _ndjson({"id": "2", "command": "ping"})
    )
    writer = io.StringIO()
    rc = run_batch(d, reader=reader, writer=writer, concurrency=1)
    lines = [ln for ln in writer.getvalue().splitlines() if ln]
    assert rc == 0
    assert len(lines) == 2


def test_run_batch_reports_request_parse_errors():
    d = _FakeDispatcher()
    reader = io.StringIO("not-json\n" + _ndjson({"id": "ok", "command": "ping"}))
    writer = io.StringIO()
    rc = run_batch(d, reader=reader, writer=writer, concurrency=1)
    assert rc == 1
    lines = [json.loads(ln) for ln in writer.getvalue().splitlines() if ln]
    types = {ln.get("error", {}).get("type") for ln in lines if not ln["ok"]}
    assert "RequestParseError" in types


def test_run_batch_handles_dispatcher_error_responses():
    """Dispatcher returns Response(ok=False) — runtime counts that as a failure."""
    d = _FakeDispatcher(
        Response(ok=False, error=ResponseError(type="Boom", message="bad"))
    )
    reader = io.StringIO(_ndjson({"id": "1", "command": "x"}))
    writer = io.StringIO()
    rc = run_batch(d, reader=reader, writer=writer, concurrency=1)
    assert rc == 1


def test_run_batch_default_concurrency_from_env(monkeypatch):
    monkeypatch.setenv("OPENBB_CLI_BATCH_CONCURRENCY", "3")
    d = _FakeDispatcher()
    reader = io.StringIO(_ndjson({"id": "1", "command": "x"}))
    writer = io.StringIO()
    rc = run_batch(d, reader=reader, writer=writer, concurrency=None)
    assert rc == 0


def test_default_batch_concurrency_constant():
    assert DEFAULT_BATCH_CONCURRENCY > 0


def test_parser_interactive_flag():
    p = build_parser()
    ns = p.parse_args(["-i"])
    assert ns.interactive is True
    assert ns.batch is False


def test_parser_batch_and_interactive_are_mutex():
    p = build_parser()
    with pytest.raises(SystemExit):
        p.parse_args(["-i", "--batch"])


def test_parser_command_capture():
    p = build_parser()
    ns = p.parse_args(["economy.gdp", "--provider=oecd"])
    assert ns.command == ["economy.gdp", "--provider=oecd"]


def test_parser_server_from_env(monkeypatch):
    monkeypatch.setenv("OPENBB_SERVER_URL", "http://api.local")
    p = build_parser()
    ns = p.parse_args([])
    assert ns.server == "http://api.local"


def test_parser_server_explicit_overrides_env(monkeypatch):
    monkeypatch.setenv("OPENBB_SERVER_URL", "http://from-env")
    p = build_parser()
    ns = p.parse_args(["--server", "http://explicit"])
    assert ns.server == "http://explicit"


def test_parser_include_and_exclude_are_repeatable():
    """Both ``--include`` and ``--exclude`` accept repeated values, each
    appended to a list — supports ``--include 'a.*' --include 'b.*'`` for
    multi-pattern selection."""
    p = build_parser()
    ns = p.parse_args(
        [
            "--generate-extension",
            "--spec",
            "x.spec",
            "--include",
            "equity.*",
            "--include",
            "shipping.*",
            "--exclude",
            "equity.fundamentals.*",
        ]
    )
    assert ns.include == ["equity.*", "shipping.*"]
    assert ns.exclude == ["equity.fundamentals.*"]


def test_parser_include_exclude_default_to_none_when_omitted():
    """Both flags default to ``None`` (not ``[]``) so callers can
    distinguish "not supplied" from "supplied but empty"."""
    p = build_parser()
    ns = p.parse_args(["x.foo"])
    assert ns.include is None
    assert ns.exclude is None

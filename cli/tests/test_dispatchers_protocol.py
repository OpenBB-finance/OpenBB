"""Tests for openbb_cli.dispatchers.protocol — Request/Response wire models."""

import pytest
from pydantic import ValidationError

from openbb_cli.dispatchers.protocol import Request, Response, ResponseError


def test_request_defaults():
    req = Request(command="economy.gdp")
    assert req.command == "economy.gdp"
    assert req.params == {}
    assert req.id is None


def test_request_with_id_and_params():
    req = Request(
        id="abc", command="equity.price.historical", params={"symbol": "AAPL"}
    )
    assert req.id == "abc"
    assert req.params == {"symbol": "AAPL"}


def test_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        Request(command="x", unknown_field=True)


def test_request_requires_command():
    with pytest.raises(ValidationError):
        Request()


def test_response_ok():
    resp = Response(ok=True, result={"a": 1})
    assert resp.ok is True
    assert resp.error is None


def test_response_error_round_trip():
    err = ResponseError(type="ValueError", message="bad")
    resp = Response(id="42", ok=False, error=err)
    assert resp.ok is False
    assert resp.error is not None
    assert resp.error.type == "ValueError"
    assert resp.error.message == "bad"


def test_response_serialization():
    resp = Response(id="1", ok=True, result=[1, 2, 3])
    payload = resp.model_dump_json()
    assert '"ok":true' in payload
    assert '"id":"1"' in payload

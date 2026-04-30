"""Tests for openbb_core.app.static.utils.decorators."""

import pytest
from pydantic import BaseModel, ValidationError

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError


def test_validate_no_args_decorator():
    @validate
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3
    with pytest.raises(ValidationError):
        add("a", 2)  # type: ignore[arg-type]


def test_validate_with_kwargs_decorator():
    class M(BaseModel):
        x: int

    @validate(config={"arbitrary_types_allowed": True})
    def f(m: M) -> int:
        return m.x

    assert f(M(x=5)) == 5


def test_exception_handler_passthrough():
    @exception_handler
    def f(x):
        return x * 2

    assert f(3) == 6


def test_exception_handler_validation_error_wrapped(monkeypatch):
    monkeypatch.delenv("OPENBB_DEBUG_MODE", raising=False)

    @exception_handler
    @validate
    def f(x: int) -> int:
        return x

    with pytest.raises(OpenBBError) as ei:
        f("not-an-int")  # type: ignore[arg-type]
    assert "[Error]" in str(ei.value)
    assert "[Arg]" in str(ei.value)


def test_exception_handler_unauthorized():
    @exception_handler
    def f():
        raise UnauthorizedError("nope")

    with pytest.raises(UnauthorizedError) as ei:
        f()
    assert "[Error]" in str(ei.value)


def test_exception_handler_empty_data():
    @exception_handler
    def f():
        raise EmptyDataError("none")

    with pytest.raises(EmptyDataError) as ei:
        f()
    assert "[Empty]" in str(ei.value)


def test_exception_handler_openbb_error():
    @exception_handler
    def f():
        raise OpenBBError("bad")

    with pytest.raises(OpenBBError) as ei:
        f()
    assert "[Error]" in str(ei.value)


def test_exception_handler_generic_exception_wrapped():
    @exception_handler
    def f():
        raise RuntimeError("boom")

    with pytest.raises(OpenBBError) as ei:
        f()
    assert "[Unexpected Error]" in str(ei.value)
    assert "RuntimeError" in str(ei.value)


def test_exception_handler_debug_mode_reraises(monkeypatch):
    from openbb_core.env import Env

    env = Env()
    monkeypatch.setitem(env._environ, "OPENBB_DEBUG_MODE", "True")

    @exception_handler
    def f():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        f()

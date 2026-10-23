"""Tests for openbb_core.app.model.field.OpenBBField."""

from openbb_core.app.model.field import OpenBBField


def test_openbbfield_repr_without_choices():
    f = OpenBBField(description="hello")
    r = repr(f)
    assert "OpenBBField" in r
    assert "hello" in r
    assert "choices" not in r


def test_openbbfield_repr_with_choices():
    f = OpenBBField(description="hello", choices=["a", "b"])
    r = repr(f)
    assert "choices" in r
    assert "a" in r and "b" in r


def test_openbbfield_choices_property_returns_list():
    f = OpenBBField(description="x", choices=[1, 2])
    assert f.choices == [1, 2]


def test_openbbfield_choices_property_returns_none_when_unset():
    f = OpenBBField(description="x")
    assert f.choices is None

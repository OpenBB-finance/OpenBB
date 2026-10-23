"""Tests for the {{ cookiecutter.obbject_name }} OBBject extensions."""

import json

from openbb_core.app.model.obbject import OBBject

import {{ cookiecutter.package_name }}.obbject.{{ cookiecutter.obbject_name }}  # noqa: F401


class TestToString:
    """``obbject.to_string`` serializes the results."""

    def test_value(self):
        obbject = OBBject(results=[{"a": 1}])
        assert json.loads(obbject.to_string) == {"results": [{"a": 1}]}


class TestNamespace:
    """``obbject.{{ cookiecutter.obbject_name }}`` exposes the extension methods."""

    def test_hello_world(self):
        obbject = OBBject(results=[{"a": 1}], provider="demo")
        assert obbject.{{ cookiecutter.obbject_name }}.hello_world() == (
            "Hello from the OBBject returned by demo!"
        )

"""Test python settings model."""

from openbb_core.app.model.python_settings import PythonSettings


def test_python_settings_repr_contains_fields():
    settings = PythonSettings(docstring_max_length=120, http={"timeout": 5})

    rep = repr(settings)
    assert rep.startswith("PythonSettings")
    assert "docstring_max_length: 120" in rep
    assert "http: {'timeout': 5}" in rep


def test_python_settings_allows_extra_fields():
    settings = PythonSettings(custom_option=True)

    assert settings.custom_option is True

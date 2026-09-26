"""Tests for openbb_core.app.utils_optional."""

import pytest

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.utils_optional import (
    _format_error,
    _install_hint,
    is_installed,
    require_optional,
)


def test_is_installed_true_for_stdlib():
    assert is_installed("json") is True


def test_is_installed_false_for_missing():
    assert is_installed("definitely_not_a_module_xyz") is False


def test_is_installed_false_when_find_spec_raises_value_error(monkeypatch):
    monkeypatch.setattr(
        "openbb_core.app.utils_optional.find_spec",
        lambda _name: (_ for _ in ()).throw(ValueError("boom")),
    )
    assert is_installed("json") is False


def test_is_installed_false_when_find_spec_raises_import_error(monkeypatch):
    monkeypatch.setattr(
        "openbb_core.app.utils_optional.find_spec",
        lambda _name: (_ for _ in ()).throw(ImportError("boom")),
    )
    assert is_installed("json") is False


def test_require_optional_returns_module_for_single_arg():
    import json as json_mod

    assert require_optional("json") is json_mod


def test_require_optional_returns_tuple_for_multi_args():
    import json as json_mod
    import os as os_mod

    result = require_optional("json", "os")
    assert isinstance(result, tuple)
    assert result == (json_mod, os_mod)


def test_require_optional_raises_openbberror_for_missing():
    with pytest.raises(OpenBBError) as excinfo:
        require_optional("definitely_not_a_module_xyz")
    msg = str(excinfo.value)
    assert "definitely_not_a_module_xyz" in msg
    assert "pip install" in msg


def test_require_optional_aggregates_multiple_missing():
    with pytest.raises(OpenBBError) as excinfo:
        require_optional("nope_one_xyz", "nope_two_xyz")
    msg = str(excinfo.value)
    assert "nope_one_xyz" in msg
    assert "nope_two_xyz" in msg


def test_require_optional_no_args_raises_value_error():
    with pytest.raises(ValueError):
        require_optional()


def test_install_hint_uses_curated_for_known():
    assert _install_hint("pandas") == "pip install 'openbb-core[pandas]'"
    assert _install_hint("polars") == "pip install polars pyarrow"


def test_install_hint_falls_back_to_generic():
    assert _install_hint("some_random_pkg") == "pip install some_random_pkg"


def test_install_hint_uses_top_level_package():
    assert _install_hint("pandas.core") == "pip install 'openbb-core[pandas]'"


def test_format_error_single():
    msg = _format_error(["polars"])
    assert "'polars'" in msg
    assert "pip install polars pyarrow" in msg


def test_format_error_multiple():
    msg = _format_error(["pandas", "polars"])
    assert "'pandas'" in msg and "'polars'" in msg
    assert "openbb-core[pandas]" in msg
    assert "polars pyarrow" in msg

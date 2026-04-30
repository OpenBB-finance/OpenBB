"""Tests for openbb_core.app.model.example."""

import pytest

from openbb_core.app.model.example import (
    APIEx,
    PythonEx,
    filter_list,
)


def test_apiex_basic_to_python():
    eg = APIEx(parameters={"symbol": "AAPL"})
    out = eg.to_python(func_path=".equity.profile")
    assert out == "obb.equity.profile(symbol='AAPL')\n"


def test_apiex_provider_kept_in_parameters_and_exposed():
    eg = APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})
    assert eg.parameters["provider"] == "fmp"
    assert eg.provider == "fmp"


def test_apiex_provider_rendered_in_to_python():
    eg = APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})
    out = eg.to_python(func_path=".equity.profile")
    assert "symbol='AAPL'" in out
    assert "provider='fmp'" in out


def test_apiex_no_provider_means_none():
    eg = APIEx(parameters={"symbol": "AAPL"})
    assert eg.provider is None


def test_apiex_provider_must_be_string():
    with pytest.raises(ValueError, match="Provider must be a string"):
        APIEx(parameters={"provider": 123})


def test_apiex_description_required_when_many_real_params():
    with pytest.raises(ValueError, match="Description is required"):
        APIEx(parameters={"a": 1, "b": 2, "c": 3, "d": 4})


def test_apiex_description_threshold_ignores_provider():
    eg = APIEx(parameters={"a": 1, "b": 2, "c": 3, "provider": "fmp"})
    assert eg.provider == "fmp"


def test_apiex_to_python_renders_description_and_param_types():
    from datetime import date

    eg = APIEx(
        description="Fetch a quote.",
        parameters={"symbol": "AAPL", "limit": 5, "as_of": "2023-01-01"},
    )
    out = eg.to_python(
        func_path=".equity.quote",
        param_types={"symbol": str, "limit": int, "as_of": date},
        indentation="    ",
        prompt=">>> ",
    )
    assert "    >>> # Fetch a quote.\n" in out
    assert "symbol='AAPL'" in out
    assert "limit=5" in out
    assert "as_of='2023-01-01'" in out
    assert out.endswith(")\n")


def test_apiex_to_python_quotes_unknown_string_param():
    eg = APIEx(parameters={"foo": "bar"})
    out = eg.to_python(func_path=".x")
    assert "foo='bar'" in out


def test_apiex_to_python_non_string_param_without_type_map():
    eg = APIEx(parameters={"limit": 5})
    out = eg.to_python(func_path=".x")
    assert "limit=5" in out


def test_apiex_unpack_type_handles_unions_and_generics():
    assert int in APIEx._unpack_type(int)
    assert str in APIEx._unpack_type(str | int)
    assert str in APIEx._unpack_type(list[str])


def test_apiex_mock_data_timeseries_default():
    rows = APIEx.mock_data("timeseries", size=3)
    assert len(rows) == 3
    assert {"date", "open", "high", "low", "close", "volume"} <= set(rows[0].keys())


def test_apiex_mock_data_timeseries_custom_sample():
    rows = APIEx.mock_data(
        "timeseries", size=2, sample={"date": "2024-01-01", "value": 100.0}
    )
    assert len(rows) == 2
    assert "value" in rows[0]
    assert rows[0]["date"] != rows[1]["date"]


def test_apiex_mock_data_panel_default():
    rows = APIEx.mock_data("panel", size=2)
    assert all("portfolio_value" in r for r in rows)
    assert any(r.get("is_multiindex") for r in rows)


def test_apiex_mock_data_panel_custom_string_sample():
    rows = APIEx.mock_data("panel", size=1, sample={"label": "L"})
    assert len(rows) == 2
    assert rows[0]["label"] == "L_0"
    assert rows[1]["label"] == "L_1"


def test_apiex_mock_data_invalid_dataset():
    with pytest.raises(ValueError, match="not found"):
        APIEx.mock_data("nope")  # type: ignore[arg-type]


def test_pythonex_to_python_renders_lines():
    eg = PythonEx(
        description="Compute returns.",
        code=["import pandas as pd", "df = pd.DataFrame()"],
    )
    out = eg.to_python(indentation="  ", prompt=">>> ")
    assert "  >>> # Compute returns.\n" in out
    assert "  >>> import pandas as pd\n" in out
    assert "  >>> df = pd.DataFrame()\n" in out


def test_filter_list_keeps_matching_provider_and_drops_others():
    e_fmp = APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})
    e_polygon = APIEx(parameters={"symbol": "MSFT", "provider": "polygon"})
    e_no_provider = APIEx(parameters={"symbol": "GOOG"})
    py = PythonEx(description="d", code=["x = 1"])

    out = filter_list([e_fmp, e_polygon, e_no_provider, py], providers=["fmp"])

    assert e_fmp in out
    assert e_polygon not in out
    assert e_no_provider in out
    assert py in out


def test_filter_list_empty_providers_drops_provider_specific():
    e_fmp = APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})
    e_no_provider = APIEx(parameters={"symbol": "GOOG"})
    out = filter_list([e_fmp, e_no_provider], providers=[])
    assert e_fmp not in out
    assert e_no_provider in out

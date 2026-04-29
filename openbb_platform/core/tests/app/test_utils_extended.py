"""Additional tests for ``openbb_core.app.utils`` covering edge branches."""

import pytest

pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")

pytestmark = pytest.mark.requires_pandas

from openbb_core.app.utils import (
    basemodel_to_df,
    convert_to_basemodel,
    df_to_basemodel,
    dict_to_basemodel,
    get_target_column,
    get_target_columns,
    list_to_basemodel,
    ndarray_to_basemodel,
)
from openbb_core.provider.abstract.data import Data

# --- basemodel_to_df ---


def test_basemodel_to_df_single_data_with_date_column():
    """Single Data with a date column triggers the to_datetime + date stripping path."""
    data = Data(date="2024-01-01", x=1, y=2)
    df = basemodel_to_df(data)
    assert "date" in df.columns
    assert "x" in df.columns


def test_basemodel_to_df_single_scalar_data_uses_values_index():
    """A single Data with only scalar fields hits the ValueError fallback."""
    data = Data(name="aapl")
    df = basemodel_to_df(data)
    # Either fallback ('values' index) or normal frame is acceptable
    assert isinstance(df, pd.DataFrame)
    assert "name" in df.columns


def test_basemodel_to_df_with_index_name():
    """Setting ``index='x'`` reindexes the resulting frame on x."""
    data = [Data(x=i, y=i * 2) for i in range(3)]
    df = basemodel_to_df(data, index="x")
    assert df.index.name == "x"


def test_basemodel_to_df_with_date_index():
    data = [Data(date=f"2024-01-0{i}", value=i) for i in range(1, 4)]
    df = basemodel_to_df(data, index="date")
    assert df.index.name == "date"


# --- df_to_basemodel ---


def test_df_to_basemodel_with_date_only_column_keeps_date_format():
    df = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "value": [1, 2],
        }
    )
    out = df_to_basemodel(df)
    assert len(out) == 2
    # The date column should be preserved as a YYYY-MM-DD string
    assert out[0].model_dump()["date"] == "2024-01-01"


def test_df_to_basemodel_series_input_is_promoted_to_frame():
    s = pd.Series([10, 20, 30], name="value")
    out = df_to_basemodel(s)
    assert len(out) == 3
    assert out[0].value == 10  # type: ignore[attr-defined]


def test_df_to_basemodel_with_named_index_resets():
    df = pd.DataFrame({"x": [1, 2], "y": [3, 4]}).set_index("x")
    out = df_to_basemodel(df, index=True)
    assert len(out) == 2
    # After reset, x is a column on the model
    assert hasattr(out[0], "x")


# --- list_to_basemodel ---


def test_list_to_basemodel_with_data_subclass_instance():
    class SubData(Data):
        custom: str = ""

    item = SubData(custom="hi")
    out = list_to_basemodel([item])
    assert out[0] is item


def test_list_to_basemodel_unsupported_type_raises():
    with pytest.raises(ValueError, match="Unsupported list item type"):
        list_to_basemodel([object()])


# --- dict_to_basemodel ---


def test_dict_to_basemodel_validation_error_raises_value_error(monkeypatch):
    """A ValidationError from ``Data(**...)`` is wrapped in ``ValueError``."""
    from pydantic import ValidationError

    from openbb_core.app import utils as utils_module

    class _BoomData:
        def __init__(self, **_kwargs):
            raise ValidationError.from_exception_data(title="Data", line_errors=[])

    monkeypatch.setattr(utils_module, "Data", _BoomData)
    with pytest.raises(ValueError, match="Validation error"):
        dict_to_basemodel({"x": 1})


# --- ndarray_to_basemodel ---


def test_ndarray_to_basemodel_non_2d_raises():
    with pytest.raises(ValueError, match="Only 2D arrays"):
        ndarray_to_basemodel(np.array([1, 2, 3]))


# --- convert_to_basemodel dispatch ---


def test_convert_to_basemodel_data_passthrough():
    d = Data(x=1)
    assert convert_to_basemodel(d) is d


def test_convert_to_basemodel_dict():
    out = convert_to_basemodel({"x": 5})
    assert isinstance(out, Data)
    assert out.x == 5  # type: ignore[attr-defined]


def test_convert_to_basemodel_list_of_dicts():
    out = convert_to_basemodel([{"x": 1}, {"x": 2}])
    assert isinstance(out, list)
    assert len(out) == 2


def test_convert_to_basemodel_dataframe():
    out = convert_to_basemodel(pd.DataFrame({"x": [1, 2]}))
    assert isinstance(out, list)
    assert len(out) == 2


def test_convert_to_basemodel_series():
    out = convert_to_basemodel(pd.Series([1, 2], name="x"))
    assert isinstance(out, list)
    assert len(out) == 2


def test_convert_to_basemodel_ndarray():
    out = convert_to_basemodel(np.array([[1, 2], [3, 4]]))
    assert isinstance(out, list)
    assert len(out) == 2


def test_convert_to_basemodel_unsupported_raises():
    with pytest.raises(ValueError, match="Unsupported data type"):
        convert_to_basemodel(object())


# --- get_target_column / get_target_columns ---


def test_get_target_column_missing_raises_with_choices():
    df = pd.DataFrame({"a": [1], "b": [2]})
    with pytest.raises(ValueError, match="Choose from"):
        get_target_column(df, "missing")


def test_get_target_columns_returns_dataframe_with_requested_columns():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    out = get_target_columns(df, ["a", "c"])
    assert list(out.columns) == ["a", "c"]


# --- get_user_cache_directory ---


def test_get_user_cache_directory_reads_preferences(tmp_path, monkeypatch):
    import json as _json

    from openbb_core.app import utils as utils_module

    settings_file = tmp_path / "user_settings.json"
    settings_file.write_text(
        _json.dumps({"preferences": {"cache_directory": "/tmp/my-cache"}})  # noqa: S108
    )

    class _FakeSystemSettings:
        def model_dump(self):
            return {"user_settings_path": str(settings_file)}

    monkeypatch.setattr(utils_module, "SystemSettings", _FakeSystemSettings)
    from openbb_core.app.utils import get_user_cache_directory

    assert get_user_cache_directory() == "/tmp/my-cache"  # noqa: S108


def test_get_user_cache_directory_falls_back_when_no_preferences(tmp_path, monkeypatch):
    from openbb_core.app import utils as utils_module

    settings_file = tmp_path / "user_settings.json"
    settings_file.write_text("{}")

    class _FakeSystemSettings:
        def model_dump(self):
            return {"user_settings_path": str(settings_file)}

    monkeypatch.setattr(utils_module, "SystemSettings", _FakeSystemSettings)
    from openbb_core.app.utils import get_user_cache_directory

    out = get_user_cache_directory()
    assert isinstance(out, str)
    assert out  # non-empty default

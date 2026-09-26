"""Targeted tests for ``OBBject`` conversion edge branches."""

import pytest

pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")

pytestmark = pytest.mark.requires_pandas

from pydantic import BaseModel

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.obbject import OBBject


class _ScalarModel(BaseModel):
    name: str = "x"
    value: int = 1


def test_to_dataframe_basemodel_scalar_uses_series_fallback():
    """A BaseModel whose dict is not list-of-list goes through Series.to_frame."""
    obb = OBBject(results=_ScalarModel())
    df = obb.to_dataframe(index=None)
    assert isinstance(df, pd.DataFrame)


def test_to_dataframe_dict_of_dicts_uses_from_dict_T():
    obb = OBBject(results={"a": {"x": 1, "y": 2}, "b": {"x": 3, "y": 4}})
    df = obb.to_dataframe(index=None)
    assert isinstance(df, pd.DataFrame)


def test_to_dataframe_dict_of_scalars_falls_back_to_series():
    """Dict of scalars triggers two ValueError fallbacks ending in Series."""
    obb = OBBject(results={"a": 1, "b": 2, "c": 3})
    df = obb.to_dataframe(index=None)
    assert isinstance(df, pd.DataFrame)


def test_to_dataframe_results_is_dataframe_returns_passthrough():
    src = pd.DataFrame({"x": [1, 2]})
    obb = OBBject(results=src)
    out = obb.to_dataframe()
    assert out is src


def test_to_dataframe_none_results_raises():
    obb = OBBject(results=None)
    with pytest.raises(OpenBBError, match="Results not found"):
        obb.to_dataframe(index=None)


def test_to_dataframe_empty_results_raises():
    obb = OBBject(results=[])
    with pytest.raises(OpenBBError, match="Results not found"):
        obb.to_dataframe(index=None)


def test_to_dataframe_str_results():
    obb = OBBject(results="hello")
    df = obb.to_dataframe(index=None)
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0, 0] == "hello"


def test_to_dataframe_list_of_lists():
    obb = OBBject(results=[[1, 2], [3, 4]])
    df = obb.to_dataframe(index=None)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)


def test_to_dataframe_list_of_one_dict_with_list_values():
    obb = OBBject(results=[{"a": [1, 2, 3], "b": [4, 5, 6]}])
    df = obb.to_dataframe(index=None)
    assert isinstance(df, pd.DataFrame)


def test_to_dataframe_value_error_wraps_to_openbb_error():
    """A list of mixed dicts with conflicting keys triggers ValueError → wrapped."""
    obb = OBBject(results=[1, "two", 3.0])
    df = obb.to_dataframe(index=None)
    assert isinstance(df, pd.DataFrame)


def test_to_dataframe_typeerror_wraps_to_openbb_error():
    obb = OBBject(results=object())
    with pytest.raises(OpenBBError):
        obb.to_dataframe(index=None)


def test_to_polars_uses_pandas_dataframe():
    polars = pytest.importorskip("polars")
    obb = OBBject(results=[{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    out = obb.to_polars()
    assert isinstance(out, polars.DataFrame)


def test_to_numpy_returns_ndarray():
    obb = OBBject(results=[{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    arr = obb.to_numpy()
    assert isinstance(arr, np.ndarray)


def test_to_dict_orient_list_with_dict_of_dicts_transposes():
    """Dict-of-dict + orient='list' goes through the .T branch and removes 'index'."""
    obb = OBBject(results={"a": {"x": 1, "y": 2}, "b": {"x": 3, "y": 4}})
    out = obb.to_dict(orient="list")
    assert isinstance(out, dict)
    assert "index" not in out


def test_to_dict_orient_records():
    obb = OBBject(results=[{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    out = obb.to_dict(orient="records")
    assert isinstance(out, list)


def test_repr_includes_class_name():
    obb = OBBject(results=[{"a": 1}])
    r = repr(obb)
    assert "OBBject" in r


class _ListFieldModel(BaseModel):
    """A model whose serialized dict has all list values."""

    xs: list = [1, 2, 3]
    ys: list = [4, 5, 6]


def test_to_dataframe_basemodel_with_dict_of_lists():
    obb = OBBject(results=_ListFieldModel(xs=[1, 2, 3], ys=[4, 5, 6]))
    df = obb.to_dataframe(index=None)
    assert isinstance(df, pd.DataFrame)
    assert set(df.columns) == {"xs", "ys"}


def test_to_dataframe_dict_with_index_orient_fallback():
    """Force the from_dict(...).T to fail and fall through to orient='index'."""
    obb = OBBject(results={"row1": [1, 2], "row2": [3, 4, 5]})
    df = obb.to_dataframe(index=None)
    assert isinstance(df, pd.DataFrame)


def test_to_dataframe_list_of_basemodels_all_array_properties():
    """A single Data with all array-typed fields uses model_dump directly."""
    from openbb_core.provider.abstract.data import Data

    obb = OBBject(results=[Data(arr=[1, 2, 3], other=[4, 5, 6])])
    df = obb.to_dataframe(index=None)
    assert isinstance(df, pd.DataFrame)


def test_to_dataframe_with_sort_by():
    """``sort_by`` triggers the inplace ``sort_values`` branch."""
    obb = OBBject(results=[{"a": 3}, {"a": 1}, {"a": 2}])
    df = obb.to_dataframe(index=None, sort_by="a", ascending=True)
    assert list(df["a"]) == [1, 2, 3]


def test_to_dataframe_with_sort_by_descending():
    obb = OBBject(results=[{"a": 1}, {"a": 3}, {"a": 2}])
    df = obb.to_dataframe(index=None, sort_by="a", ascending=False)
    assert list(df["a"]) == [3, 2, 1]


def test_to_dataframe_unexpected_exception_wrapped(monkeypatch):
    """A non-ValueError/non-TypeError exception is wrapped as 'unexpected error'."""
    from openbb_core.app import utils as utils_module
    from openbb_core.provider.abstract.data import Data

    def boom(*_a, **_kw):
        raise RuntimeError("boom")

    monkeypatch.setattr(utils_module, "basemodel_to_df", boom)

    obb = OBBject(results=[Data(a=1), Data(a=2)])
    with pytest.raises(OpenBBError, match="unexpected error"):
        obb.to_dataframe(index=None)


def test_to_dataframe_index_set_to_existing_column():
    obb = OBBject(results=[{"a": 1, "b": 10}, {"a": 2, "b": 20}])
    df = obb.to_dataframe(index="a")
    assert df.index.name == "a"


def test_to_polars_uses_pandas_then_converts():
    """Force the polars import path via require_optional."""
    pytest.importorskip("polars")
    obb = OBBject(results=[{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    out = obb.to_polars()
    assert hasattr(out, "to_pandas")


def test_to_llm_returns_json_string():
    obb = OBBject(results=[{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    out = obb.to_llm()
    assert isinstance(out, str)
    assert '"a"' in out


def test_show_without_chart_raises():
    obb = OBBject(results=[{"a": 1}])
    with pytest.raises(OpenBBError, match="Chart not found"):
        obb.show()


def test_show_with_chart_calls_show():
    from unittest.mock import MagicMock

    fake_fig = MagicMock()
    obb = OBBject(results=[{"a": 1}])
    obb.chart = MagicMock()
    obb.chart.fig = fake_fig
    obb.show()
    fake_fig.show.assert_called_once()


def test_from_query_returns_obbject_with_results():
    import asyncio
    from unittest.mock import AsyncMock, MagicMock

    fake_query = MagicMock()
    fake_query.execute = AsyncMock(return_value=[{"a": 1}])
    out = asyncio.run(OBBject.from_query(fake_query))
    assert isinstance(out, OBBject)
    assert out.results == [{"a": 1}]


def test_from_query_with_annotated_result():
    import asyncio
    from unittest.mock import AsyncMock, MagicMock

    from openbb_core.provider.abstract.annotated_result import AnnotatedResult

    fake_query = MagicMock()
    fake_query.execute = AsyncMock(
        return_value=AnnotatedResult(result=[{"a": 1}], metadata={"src": "test"})
    )
    out = asyncio.run(OBBject.from_query(fake_query))
    assert out.results == [{"a": 1}]
    assert out.extra["results_metadata"] == {"src": "test"}


def test_to_polars_raises_when_polars_missing(monkeypatch):
    """When polars is not installed, ``require_optional`` raises ImportError/ModuleNotFoundError."""

    from openbb_core.app import utils_optional

    real_require = utils_optional.require_optional

    def fake_require(pkg):
        if pkg == "polars":
            raise ModuleNotFoundError("polars not installed")
        return real_require(pkg)

    monkeypatch.setattr(utils_optional, "require_optional", fake_require)
    obb = OBBject(results=[{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    with pytest.raises(ModuleNotFoundError):
        obb.to_polars()

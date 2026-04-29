"""Extra branch coverage for openbb_core.app.model.obbject."""

from unittest.mock import AsyncMock, MagicMock

import pytest

pd = pytest.importorskip("pandas")

from openbb_core.app.model.charts.chart import Chart  # noqa: E402
from openbb_core.app.model.obbject import OBBject, OpenBBError  # noqa: E402
from openbb_core.provider.abstract.annotated_result import AnnotatedResult  # noqa: E402
from openbb_core.provider.abstract.data import Data  # noqa: E402

pytestmark = pytest.mark.requires_pandas


class _Row(Data):
    x: int
    y: int


def test_repr_contains_class_name_and_fields():
    co: OBBject = OBBject(results=[_Row(x=1, y=2)], provider="fmp")
    s = repr(co)
    assert s.startswith("OBBject")
    assert "results" in s
    assert "provider" in s


def test_to_df_alias_works():
    co: OBBject = OBBject(results=[{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    df = co.to_df(index=None)
    assert set(df.columns) == {"a", "b"}
    assert len(df) == 2


def test_to_dataframe_basemodel_with_list_values():
    co: OBBject = OBBject(results={"a": [1, 2, 3], "b": [4, 5, 6]})
    df = co.to_dataframe(index=None)
    assert df.size == 6


def test_to_dataframe_basemodel_scalar_values_uses_series():
    class M(Data):
        a: int
        b: int

    co: OBBject = OBBject(results=M(a=1, b=2))
    df = co.to_dataframe(index=None)
    assert df.shape[0] == 2


def test_to_dataframe_string_results():
    co: OBBject = OBBject(results="hello")
    df = co.to_dataframe(index=None)
    assert df.iloc[0, 0] == "hello"


def test_to_dataframe_sort_by():
    co: OBBject = OBBject(results=[{"v": 3}, {"v": 1}, {"v": 2}])
    df = co.to_dataframe(index=None, sort_by="v", ascending=True)
    assert list(df["v"]) == [1, 2, 3]


def test_to_dataframe_sort_by_descending():
    co: OBBject = OBBject(results=[{"v": 3}, {"v": 1}, {"v": 2}])
    df = co.to_dataframe(index=None, sort_by="v", ascending=False)
    assert list(df["v"]) == [3, 2, 1]


def test_to_dataframe_passthrough_dataframe():
    src = pd.DataFrame({"a": [1, 2]})
    co: OBBject = OBBject(results=[{"a": 1}, {"a": 2}])
    co.results = src  # type: ignore[assignment]
    out = co.to_dataframe()
    assert out is src


def test_to_dataframe_no_results_raises():
    co: OBBject = OBBject()
    with pytest.raises(OpenBBError):
        co.to_dataframe()


def test_to_dataframe_unsupported_format_raises():
    co: OBBject = OBBject(results=42)  # int
    with pytest.raises(OpenBBError):
        co.to_dataframe()


def test_to_polars():
    polars = pytest.importorskip("polars")
    co: OBBject = OBBject(results=[{"a": 1}, {"a": 2}])
    out = co.to_polars()
    assert isinstance(out, polars.DataFrame)


def test_to_numpy():
    co: OBBject = OBBject(results=[{"a": 1}, {"a": 2}])
    arr = co.to_numpy()
    assert arr.shape == (2, 1)


def test_to_dict_records():
    co: OBBject = OBBject(results=[{"a": 1}, {"a": 2}])
    out = co.to_dict(orient="records")
    assert out == [{"a": 1}, {"a": 2}]


def test_to_dict_list_with_dict_of_dict_transposes():
    co: OBBject = OBBject(results={"r1": {"a": 1, "b": 2}, "r2": {"a": 3, "b": 4}})
    out = co.to_dict(orient="list")
    assert isinstance(out, dict)
    assert set(out) == {"r1", "r2"}


def test_to_llm_returns_json_records():
    co: OBBject = OBBject(results=[{"a": 1}, {"a": 2}])
    out = co.to_llm()
    assert out.startswith("[") and '"a"' in out


def test_to_llm_empty_returns_empty_array():
    co: OBBject = OBBject(results=[{"a": None}])
    out = co.to_llm()
    assert out.startswith("[")


def test_show_no_chart_raises():
    co: OBBject = OBBject(results=[{"a": 1}])
    with pytest.raises(OpenBBError):
        co.show()


def test_show_invokes_chart_show():
    fig = MagicMock()
    chart = Chart(content={}, fig=fig)
    co: OBBject = OBBject(results=[{"a": 1}], chart=chart)
    co._route = "/eq/x"
    co.show(extra="kw")
    fig.show.assert_called_once()
    assert fig.show.call_args.kwargs["command_location"] == "/eq/x"


@pytest.mark.asyncio
async def test_from_query_annotated_result():
    q = MagicMock()
    q.execute = AsyncMock(
        return_value=AnnotatedResult(result=[{"a": 1}], metadata={"k": "v"})
    )
    out = await OBBject.from_query(q)
    assert out.results == [{"a": 1}]
    assert out.extra["results_metadata"] == {"k": "v"}


@pytest.mark.asyncio
async def test_from_query_plain_result():
    q = MagicMock()
    q.execute = AsyncMock(return_value=[{"a": 1}])
    out = await OBBject.from_query(q)
    assert out.results == [{"a": 1}]


def test_to_dataframe_dict_double_valueerror_falls_back_to_series():
    from unittest.mock import patch as _patch

    co: OBBject = OBBject(results={"a": 1, "b": 2})

    def _boom(*_args, **_kwargs):
        raise ValueError("bad")

    with _patch("pandas.DataFrame.from_dict", side_effect=_boom):
        df = co.to_dataframe(index=None)

    assert df is not None
    assert df.shape[0] > 0


def test_to_dataframe_raises_valueerror_non_dict_res():
    from unittest.mock import patch as _patch

    co: OBBject = OBBject(results=[{"v": 1}])

    def _boom(*_args, **_kwargs):
        raise ValueError("bad")

    with (
        _patch("pandas.DataFrame.sort_values", side_effect=_boom),
        pytest.raises(OpenBBError, match="ValueError"),
    ):
        co.to_dataframe(index=None, sort_by="v")


def test_to_dataframe_raises_typeerror_wraps_openbb():
    """Lines 281-283: TypeError inside conversion raises OpenBBError wrapping TypeError."""

    # Use an object type that triggers TypeError inside pandas conversion path
    class _Bad:
        def __iter__(self):
            raise TypeError("type bad")

        def __len__(self):
            return 1

    co: OBBject = OBBject(results=_Bad())
    with pytest.raises(OpenBBError, match="TypeError"):
        co.to_dataframe(index=None)


def test_to_dict_list_orient_removes_index_key():
    co: OBBject = OBBject(results=[{"a": 1}])

    with pytest.MonkeyPatch.context() as m:
        m.setattr(
            OBBject,
            "to_dataframe",
            lambda self, index=None: pd.DataFrame({"index": [1], "a": [2]}),
        )
        out = co.to_dict(orient="list")

    assert "index" not in out

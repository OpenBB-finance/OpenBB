"""Tests for the OBBject class."""

from unittest.mock import MagicMock

import pytest

pd = pytest.importorskip("pandas")
from pandas.testing import assert_frame_equal  # noqa: E402

from openbb_core.app.model.obbject import Chart, OBBject, OpenBBError  # noqa: E402
from openbb_core.app.utils import basemodel_to_df  # noqa: E402
from openbb_core.provider.abstract.data import Data  # noqa: E402

pytestmark = pytest.mark.requires_pandas


def test_OBBject():
    """Smoke test."""
    co: OBBject = OBBject()
    assert isinstance(co, OBBject)


def test_fields():
    """Smoke test."""
    fields = OBBject.model_fields.keys()

    assert "results" in fields
    assert "provider" in fields
    assert "warnings" in fields
    assert "chart" in fields
    assert "extra" in fields


def test_to_dataframe_no_results():
    """Test helper."""
    co: OBBject = OBBject()
    with pytest.raises(Exception):
        co.to_dataframe()


class MockData(Data):
    """Test helper."""

    x: int
    y: int


class MockMultiData(Data):
    """Test helper."""

    date: str
    another_date: str
    value: float


class MockDataFrame(Data):
    """Test helper."""

    date: str
    value: float


@pytest.mark.parametrize(
    "results, expected_df",
    [
        # Test case 1: Normal results with "date" column
        (
            [{"date": "2023-07-30", "value": 10}, {"date": "2023-07-31", "value": 20}],
            pd.DataFrame(
                [
                    {"date": "2023-07-30", "value": 10},
                    {"date": "2023-07-31", "value": 20},
                ],
            ),
        ),
        # Test case 2: Normal results without "date" column
        (
            [{"value": 10}, {"value": 20}],
            pd.DataFrame({"value": [10, 20]}, index=pd.RangeIndex(start=0, stop=2)),
        ),
        # Test case 3: List of Data
        (
            [
                MockData(x=0, y=2),
                MockData(x=1, y=3),
                MockData(x=2, y=0),
                MockData(x=3, y=1),
                MockData(x=4, y=6),
            ],
            pd.DataFrame(
                {"x": [0, 1, 2, 3, 4], "y": [2, 3, 0, 1, 6]}, columns=["x", "y"]
            ),
        ),
        # Test case 4: List of dict
        (
            [
                {"a": 1, "y": 2},
                {"a": 1, "y": 3},
                {"a": 2, "y": 0},
                {"a": 3, "y": 1},
                {"a": 4, "y": 6},
            ],
            pd.DataFrame(
                {"a": [1, 1, 2, 3, 4], "y": [2, 3, 0, 1, 6]}, columns=["a", "y"]
            ),
        ),
        # Test case 5: List of Lists
        (
            [[0, 1], [1, 3], [2, 0], [3, 1], [4, 6]],
            pd.DataFrame([[0, 1], [1, 3], [2, 0], [3, 1], [4, 6]]),
        ),
        # Test case 6: List of Tuples
        (
            [(3, 2), (1, 3), (2, 0), (3, 1), (4, 6)],
            pd.DataFrame([(3, 2), (1, 3), (2, 0), (3, 1), (4, 6)]),
        ),
        # Test case 7: List of Strings
        (
            ["YOLO2", "YOLO3", "YOLO0", "YOLO1", "YOLO6"],
            pd.DataFrame(["YOLO2", "YOLO3", "YOLO0", "YOLO1", "YOLO6"]),
        ),
        # Test case 7: List of Numbers
        (
            [1, 0.42, 12321298, 129387129387192837, 0.000000123],
            pd.DataFrame([1, 0.42, 12321298, 129387129387192837, 0.000000123]),
        ),
        # Test case 7: Dict of Dicts
        (
            {
                "0": {"x": 0, "y": 2},
                "1": {"x": 1, "y": 3},
                "2": {"x": 2, "y": 0},
                "3": {"x": 3, "y": 1},
                "4": {"x": 4, "y": 6},
            },
            pd.DataFrame.from_dict(
                {
                    "0": {"x": 0, "y": 2},
                    "1": {"x": 1, "y": 3},
                    "2": {"x": 2, "y": 0},
                    "3": {"x": 3, "y": 1},
                    "4": {"x": 4, "y": 6},
                },
                orient="index",
            ),
        ),
        # Test case 8: Dict of Lists
        (
            {"0": [0, 2], "1": [1, 3], "2": [2, 0], "3": [3, 1], "4": [4, 6]},
            pd.DataFrame.from_dict(
                {"0": [0, 2], "1": [1, 3], "2": [2, 0], "3": [3, 1], "4": [4, 6]},
                orient="index",
            ),
        ),
        # Test case 9: List of dict of data
        (
            [
                {
                    "df1": [
                        MockMultiData(
                            date="1956-01-01", another_date="2023-09-01", value=0.0
                        ),
                        MockMultiData(
                            date="1956-02-01", another_date="2023-09-01", value=0.0
                        ),
                        MockMultiData(
                            date="1956-03-01", another_date="2023-09-01", value=0.0
                        ),
                    ],
                    "df2": [
                        MockMultiData(
                            date="1955-03-01", another_date="2023-09-01", value=0.0
                        ),
                        MockMultiData(
                            date="1955-04-01", another_date="2023-09-01", value=0.0
                        ),
                        MockMultiData(
                            date="1955-05-01", another_date="2023-09-01", value=0.0
                        ),
                    ],
                }
            ],
            pd.concat(
                {
                    "df1": pd.DataFrame(
                        {
                            "date": [
                                pd.to_datetime("1956-01-01").date(),
                                pd.to_datetime("1956-02-01").date(),
                                pd.to_datetime("1956-03-01").date(),
                            ],
                            "another_date": ["2023-09-01", "2023-09-01", "2023-09-01"],
                            "value": [0.0, 0.0, 0.0],
                        },
                        columns=["date", "another_date", "value"],
                    ),
                    "df2": pd.DataFrame(
                        {
                            "date": [
                                pd.to_datetime("1955-03-01").date(),
                                pd.to_datetime("1955-04-01").date(),
                                pd.to_datetime("1955-05-01").date(),
                            ],
                            "another_date": ["2023-09-01", "2023-09-01", "2023-09-01"],
                            "value": [0.0, 0.0, 0.0],
                        },
                        columns=["date", "another_date", "value"],
                    ),
                },
                axis=1,
                sort=True,
            ),
        ),
        # Test case 10: Empty results
        ([], OpenBBError("Results not found.")),
        # Test case 11: Results as None, should raise OpenBBError
        (None, OpenBBError("Results not found.")),
    ],
)
def test_to_dataframe(results, expected_df):
    """Test helper."""
    # Arrange
    co: OBBject = OBBject(results=results)

    # Act and Assert
    if isinstance(expected_df, pd.DataFrame):
        result = co.to_dataframe(index=None)
        assert_frame_equal(result, expected_df)
    else:
        with pytest.raises(expected_df.__class__) as exc_info:
            co.to_dataframe(index=None)

        assert str(exc_info.value) == str(expected_df)


@pytest.mark.parametrize(
    "results, index, sort_by",
    [
        # Test case 1: Normal results with "date" column
        (
            [{"date": "2023-07-30", "value": 10}, {"date": "2023-07-31", "value": 20}],
            "date",
            "value",
        ),
        # Test case 2: List of Data
        (
            [
                MockData(x=0, y=2),
                MockData(x=1, y=3),
                MockData(x=2, y=0),
                MockData(x=3, y=1),
                MockData(x=4, y=6),
            ],
            "x",
            "y",
        ),
    ],
)
def test_to_dataframe_w_args(results, index, sort_by):
    """Test helper."""
    # Arrange
    co: OBBject = OBBject(results=results)

    # Act and Assert
    result = co.to_dataframe(index=index, sort_by=sort_by)
    assert isinstance(result, pd.DataFrame)
    assert result.index.name == index

    # check if dataframe is properly sorted
    assert result[sort_by].is_monotonic_increasing


@pytest.mark.parametrize(
    "results",
    # Test case 1: List of models with daylight savings crossover.
    (
        [
            MockDataFrame(date="2023-11-03 00:00:00-04:00", value=10),
            MockDataFrame(date="2023-11-03 08:00:00-04:00", value=9),
            MockDataFrame(date="2023-11-03 16:00:00-04:00", value=8),
            MockDataFrame(date="2023-11-06 00:00:00-05:00", value=11),
            MockDataFrame(date="2023-11-06 08:00:00-05:00", value=7),
            MockDataFrame(date="2023-11-06 16:00:00-05:00", value=12),
        ],
    ),
)
def test_to_df_daylight_savings(results):
    """Test helper."""
    # Arrange
    co: OBBject = OBBject(results=results)

    # Act and Assert
    expected_df = basemodel_to_df(results, index="date")
    result = co.to_dataframe(index="date")
    assert isinstance(result, pd.DataFrame)
    assert_frame_equal(expected_df, result)


@pytest.mark.parametrize(
    "results, expected_dict",
    [  # Case 1: Normal results with "date" column
        (
            [{"date": "2023-07-30", "value": 10}, {"date": "2023-07-31", "value": 20}],
            {"date": ["2023-07-30", "2023-07-31"], "value": [10, 20]},
        ),
        # Case 2: Normal results without "date" column
        (
            [{"value": 10}, {"value": 20}],
            {"value": [10, 20]},
        ),
        # Test case 3: Dict of lists
        (
            {"0": [0, 2], "1": [1, 3], "2": [2, 0], "3": [3, 1], "4": [4, 6]},
            {0: [0, 1, 2, 3, 4], 1: [2, 3, 0, 1, 6]},
        ),
        # Test case 4: No results
        ([], OpenBBError("Results not found.")),
        # Test case 5: Results as None, should raise OpenBBError
        (None, OpenBBError("Results not found.")),
        # Test case 6: List of tuples
        (
            [(3, 2), (1, 3), (2, 0), (3, 1), (4, 6)],
            {0: [3, 1, 2, 3, 4], 1: [2, 3, 0, 1, 6]},
        ),
        # Test case 7: List of Strings
        (
            ["YOLO2", "YOLO3", "YOLO0", "YOLO1", "YOLO6"],
            {0: ["YOLO2", "YOLO3", "YOLO0", "YOLO1", "YOLO6"]},
        ),
        # Test case 8: List of Numbers
        (
            [1, 0.42, 12321, 1293, 0.00123],
            {0: [1, 0.42, 12321, 1293, 0.00123]},
        ),
        # Test case 9: Dict of Dicts
        (
            {
                "0": {"x": 0, "y": 2},
                "1": {"x": 1, "y": 3},
                "2": {"x": 2, "y": 0},
                "3": {"x": 3, "y": 1},
                "4": {"x": 4, "y": 6},
            },
            {"0": [0, 2], "1": [1, 3], "2": [2, 0], "3": [3, 1], "4": [4, 6]},
        ),
    ],
)
def test_to_dict(results, expected_dict):
    """Test helper."""
    # Arrange
    co: OBBject = OBBject(results=results)

    # Act and Assert
    if isinstance(expected_dict, (list, dict)):
        result = co.to_dict()
        assert result == expected_dict
    else:
        with pytest.raises(expected_dict.__class__) as exc_info:
            co.to_dict()

        assert str(exc_info.value) == str(expected_dict)


def test_show_chart_exists():
    """Test helper."""
    mock_instance: OBBject = OBBject()
    # Arrange
    mock_instance.chart = MagicMock(spec=Chart)
    mock_instance.chart.fig = MagicMock()
    mock_instance.chart.fig.show.return_value = MagicMock()

    # Act
    mock_instance.show()

    # Assert
    mock_instance.chart.fig.show.assert_called_once()


def test_show_chart_no_chart():
    """Test helper."""
    mock_instance: OBBject = OBBject()

    # Act and Assert
    with pytest.raises(OpenBBError, match="Chart not found."):
        mock_instance.show()


def test_show_chart_no_fig():
    """Test helper."""
    mock_instance: OBBject = OBBject()
    # Arrange
    mock_instance.chart = Chart()

    # Act and Assert
    with pytest.raises(OpenBBError, match="Chart not found."):
        mock_instance.show()

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


def test_to_df_alias_calls_to_dataframe():
    co: OBBject = OBBject(results=[{"a": [1]}])
    out = co.to_df(index=None)
    assert isinstance(out, pd.DataFrame)


def test_to_dataframe_dict_double_valueerror_falls_back_to_series(monkeypatch):
    calls = {"n": 0}
    original = pd.DataFrame.from_dict

    def _boom(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] <= 2:
            raise ValueError("fail")
        return original(*args, **kwargs)

    with pytest.MonkeyPatch.context() as m:
        m.setattr(pd.DataFrame, "from_dict", _boom)
        co: OBBject = OBBject(results={"a": 1})
        out = co.to_dataframe(index=None)
        assert list(out.columns) == ["index", "values"]


def test_to_dataframe_wraps_valueerror_in_openbb_error(monkeypatch):
    def _raise_value_error(*args, **kwargs):
        raise ValueError("boom")

    with pytest.MonkeyPatch.context() as m:
        m.setattr(pd.DataFrame, "sort_index", _raise_value_error)
        co: OBBject = OBBject(results=[{"a": [1]}])
        with pytest.raises(OpenBBError, match="ValueError: boom"):
            co.to_dataframe(index=None)


def test_to_polars_uses_polars_from_pandas(monkeypatch):
    class _P:
        @staticmethod
        def from_pandas(df):
            return {"rows": len(df)}

    with pytest.MonkeyPatch.context() as m:
        m.setattr("openbb_core.app.utils_optional.require_optional", lambda name: _P)
        m.setattr(
            OBBject,
            "to_dataframe",
            lambda self, index=None: pd.DataFrame({"a": [1], "b": [2]}),
        )
        co: OBBject = OBBject(results=[{"a": [1], "b": [2]}])
        out = co.to_polars()
        assert out == {"rows": 1}

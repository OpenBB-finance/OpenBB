from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from openbb_core.app.model.obbject import Chart, OBBject, OpenBBError
from openbb_provider.abstract.data import Data


def test_OBBject():
    co = OBBject()
    assert isinstance(co, OBBject)


def test_fields():
    fields = OBBject.__fields__.keys()

    assert "results" in fields
    assert "provider" in fields
    assert "warnings" in fields
    assert "chart" in fields


def test_to_dataframe_no_results():
    co = OBBject()
    with pytest.raises(Exception):
        co.to_dataframe()


@pytest.mark.parametrize(
    "results, expected_df",
    [
        # Test case 1: Normal results with "date" column
        (
            [{"date": "2023-07-30", "value": 10}, {"date": "2023-07-31", "value": 20}],
            pd.DataFrame(
                {"value": [10, 20]},
                index=pd.to_datetime(["2023-07-30", "2023-07-31"]),
            ),
        ),
        # Test case 2: Normal results without "date" column
        (
            [{"value": 10}, {"value": 20}],
            pd.DataFrame({"value": [10, 20]}, index=pd.RangeIndex(start=0, stop=2)),
        ),
        # Test case 3: Empty results
        ([], OpenBBError("Results not found.")),
        # Test case 4: Results as None, should raise OpenBBError
        (None, OpenBBError("Results not found.")),
    ],
)
def test_to_dataframe(results, expected_df):
    # Arrange
    if results:
        results = [Data(**d) for d in results]
    co = OBBject(results=results)

    # Act and Assert
    if isinstance(expected_df, pd.DataFrame):
        result = co.to_dataframe()
        assert result.equals(expected_df)
    else:
        with pytest.raises(expected_df.__class__) as exc_info:
            co.to_dataframe()

        assert str(exc_info.value) == str(expected_df)


@pytest.mark.parametrize(
    "results, expected",
    [
        # Test case 1: Normal results with "date" column
        (
            [{"date": "2023-07-30", "value": 10}, {"date": "2023-07-31", "value": 20}],
            {
                "date": [pd.to_datetime("2023-07-30"), pd.to_datetime("2023-07-31")],
                "value": [10, 20],
            },
        ),
        # Test case 2: Normal results without "date" column
        (
            [{"value": 10}, {"value": 20}],
            {
                "value": [10, 20],
            },
        ),
        # Test case 3: Empty results
        ([], OpenBBError("Results not found.")),
    ],
)
def test_to_dict(results, expected):
    # Arrange
    if results:
        results = [Data(**d) for d in results]
    co = OBBject(results=results)

    # Act and Assert
    if isinstance(expected, Exception):
        with pytest.raises(expected.__class__) as exc_info:
            co.to_dict()

        assert str(exc_info.value) == str(expected)
    else:
        result = co.to_dict()
        result.pop("index", None)

        assert result == expected


@patch("openbb_core.app.charting_manager.ChartingManager.to_chart")
@patch("openbb_core.app.model.obbject.OBBject.to_dataframe")
def test_to_chart_with_existing_chart(mock_to_dataframe, mock_to_chart):
    # Arrange
    mock_instance = OBBject()
    mock_instance.chart = Chart(content={"existing_chart_data": "some_data"})

    # mock the return value of ChartingManager.to_chart()
    mock_to_chart.return_value = Chart(
        content={"content": "some_new_content"}, fig={"fig": "some_mock_fig"}
    )

    # Act
    result = mock_instance.to_chart()

    # Assert
    assert result == {"fig": "some_mock_fig"}
    assert mock_instance.chart.content == {"content": "some_new_content"}

    mock_to_dataframe.assert_called_once()


@patch("openbb_core.app.model.obbject.OBBject.to_dataframe")
@patch("openbb_core.app.model.obbject.ChartingManager")
def test_to_chart_with_new_chart(
    mock_charting_manager,
    mock_to_dataframe,
):
    def get_mock_dataframe():
        data = {
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"],
            "col3": [True, False, True],
        }

        return pd.DataFrame(data)

    # Arrange
    mock_instance = OBBject()
    mock_charting_manager_instance = mock_charting_manager.return_value
    mock_charting_manager_instance.to_chart.return_value = Chart(
        content={"content": "some_new_content"}, fig={"fig": "some_mock_fig"}
    )
    mock_to_dataframe.return_value = get_mock_dataframe()

    # Act
    result = mock_instance.to_chart()

    # Assert
    assert result == {"fig": "some_mock_fig"}
    assert mock_instance.chart.content == {"content": "some_new_content"}

    # Ensure self.to_dataframe() was called
    mock_to_dataframe.assert_called_once()

    # Ensure ChartingManager was called with the correct parameters
    mock_charting_manager_instance.to_chart.assert_called_once()


def test_show_chart_exists():
    mock_instance = OBBject()
    # Arrange
    mock_instance.chart = MagicMock(spec=Chart)
    mock_instance.chart.fig = MagicMock()
    mock_instance.chart.fig.show.return_value = MagicMock()

    # Act
    mock_instance.show()

    # Assert
    mock_instance.chart.fig.show.assert_called_once()


def test_show_chart_no_chart():
    mock_instance = OBBject()

    # Act and Assert
    with pytest.raises(OpenBBError, match="Chart not found."):
        mock_instance.show()


def test_show_chart_no_fig():
    mock_instance = OBBject()
    # Arrange
    mock_instance.chart = Chart()

    # Act and Assert
    with pytest.raises(OpenBBError, match="Chart not found."):
        mock_instance.show()

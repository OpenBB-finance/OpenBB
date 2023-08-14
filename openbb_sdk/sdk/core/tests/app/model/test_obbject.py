from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from openbb_core.app.model.command_output import Chart, OBBject, OpenBBError


def test_command_output():
    co = OBBject()
    assert isinstance(co, OBBject)


def test_fields():
    fields = OBBject.__fields__.keys()

    assert "results" in fields
    assert "provider" in fields
    assert "warnings" in fields
    assert "error" in fields
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
        ([], pd.DataFrame()),
        # Test case 4: Results as None, should raise OpenBBError
        (None, OpenBBError("Results not found.")),
    ],
)
def test_to_dataframe(results, expected_df):
    # Arrange
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
        ([], {}),
    ],
)
def test_to_dict(results, expected):
    # Arrange
    co = OBBject(results=results)

    # Act
    result = co.to_dict()
    result.pop("index", None)

    # Assert
    assert result == expected


@patch("openbb_core.app.model.command_output.ChartingManager")
@patch("openbb_core.app.model.command_output.Chart")
def test_to_plotly_json_with_existing_chart(mock_chart, mock_charting_manager):
    # Arrange
    mock_instance = OBBject()
    mock_instance.chart = Chart(content={"existing_chart_data": "some_data"})

    # Act
    result = mock_instance.to_plotly_json()

    # Assert
    assert result == {"existing_chart_data": "some_data"}

    # Ensure ChartingManager and Chart constructors were not called
    mock_charting_manager.assert_not_called()
    mock_chart.assert_not_called()


@patch("openbb_core.app.model.command_outputobbject.to_dataframe")
@patch("openbb_core.app.model.command_output.ChartingManager")
@patch("openbb_core.app.model.command_output.Chart")
def test_to_plotly_json_with_new_chart(
    mock_chart,
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
    mock_charting_manager_instance.to_plotly_json.return_value = {
        "new_chart_data": "some_data"
    }
    mock_to_dataframe.return_value = get_mock_dataframe()

    # Act
    result = mock_instance.to_plotly_json(
        create_chart=True, chart_option="option_value"
    )

    # Assert
    assert result == {"new_chart_data": "some_data"}

    # Ensure self.to_dataframe() was called
    mock_to_dataframe.assert_called_once()

    # Ensure ChartingManager was called with the correct parameters
    mock_charting_manager_instance.to_plotly_json.assert_called_once()

    # Ensure Chart constructor was called with the correct parameters
    mock_chart.assert_called_once_with(
        content={"new_chart_data": "some_data"}, format="plotly"
    )


def test_show_chart_exists():
    mock_instance = OBBject()
    # Arrange
    mock_instance.chart = MagicMock(spec=Chart)

    # Act
    mock_instance.show()

    # Assert
    mock_instance.chart.show.assert_called_once()


def test_show_chart_not_found():
    mock_instance = OBBject()
    # Arrange
    mock_instance.chart = None

    # Act and Assert
    with pytest.raises(OpenBBError, match="Chart not found."):
        mock_instance.show()

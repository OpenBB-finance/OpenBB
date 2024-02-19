from unittest.mock import MagicMock, patch

import pytest
from openbb_charting import Charting
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from pydantic import BaseModel


@pytest.fixture()
def obbject():
    class MockStdParams(BaseModel):
        param1: str
        param2: str

    class MockOOBject:
        def __init__(self):
            self._user_settings = UserSettings()
            self._system_settings = SystemSettings()
            self._route = "mock/route"
            self._standard_params = MockStdParams(
                param1="mock_param1", param2="mock_param2"
            )
            self.results = "mock_results"

        def to_dataframe(self):
            return "mock_dataframe"

    return MockOOBject()


def test_charting_settings(obbject):
    cm = Charting(obbject)
    assert isinstance(cm, Charting)


@patch("openbb_charting.ChartIndicators.get_available_indicators")
def test_indicators(mock_get_available_indicators, obbject):
    # Arrange
    mock_get_available_indicators.return_value = [
        "indicator1",
        "indicator2",
        "indicator3",
    ]
    obj = Charting(obbject)

    # Act
    result = obj.indicators()

    # Assert
    assert result == ["indicator1", "indicator2", "indicator3"]
    mock_get_available_indicators.assert_called_once()


@patch("openbb_charting.get_charting_functions")
def test_functions(mock_get_charting_functions):
    # Arrange
    mock_get_charting_functions.return_value = ["function1", "function2", "function3"]

    # Act
    result = Charting.functions()

    # Assert
    assert result == ["function1", "function2", "function3"]
    mock_get_charting_functions.assert_called_once()


@patch("openbb_charting.core.backend.get_backend")
@patch("openbb_charting.core.backend.create_backend")
def test_handle_backend(mock_create_backend, mock_get_backend, obbject):
    # Act -> _handle backend is called in the constructor
    obj = Charting(obbject)

    # Assert
    mock_create_backend.assert_called_once_with(obj._charting_settings)
    mock_get_backend.assert_called_once()


@patch("openbb_charting.charting_router")
def test_get_chart_function(mock_charting_router):
    # Arrange
    mock_function = MagicMock()
    mock_charting_router.some_function = mock_function
    route = "/some/function"

    # Act
    result = Charting._get_chart_function(route)

    # Assert
    assert result == mock_function


@patch("openbb_charting.Charting._get_chart_function")
def test_show(mock_get_chart_function, obbject):
    # Arrange
    mock_function = MagicMock()
    mock_get_chart_function.return_value = mock_function
    mock_fig = MagicMock()
    mock_function.return_value = (mock_fig, {"content": "mock_content"})
    obj = Charting(obbject)

    # Act
    obj.show()

    # Assert
    mock_get_chart_function.assert_called_once()
    mock_function.assert_called_once()
    mock_fig.show.assert_called_once()


@patch("openbb_charting.to_chart")
def test_to_chart(mock_to_chart, obbject):
    # Arrange
    mock_fig = MagicMock()
    mock_to_chart.return_value = (mock_fig, {"content": "mock_content"})
    obj = Charting(obbject)

    # Act
    obj.to_chart()

    # Assert
    assert obj._obbject.chart.fig == mock_fig
    mock_to_chart.assert_called_once_with(
        "mock_dataframe",
        indicators=None,
        symbol="",
        candles=True,
        volume=True,
        prepost=False,
        volume_ticks_x=7,
    )

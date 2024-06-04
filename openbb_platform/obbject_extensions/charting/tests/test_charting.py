"""Test Charting class."""

from unittest.mock import MagicMock, patch

import pytest
from openbb_charting import Charting
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from pydantic import BaseModel

# pylint: disable=redefined-outer-name, protected-access


class MockDataframe:
    """Mock Dataframe."""

    def __init__(self):
        """Mock Dataframe."""
        self.columns = ["column1", "column2"]


mock_dataframe = MockDataframe()


@pytest.fixture()
def obbject():
    """Mock OOBject."""

    class MockStdParams(BaseModel):
        """Mock Standard Parameters."""

        param1: str
        param2: str

    class MockOOBject:
        """Mock OOBject."""

        def __init__(self):
            """Mock OOBject."""
            self._user_settings = UserSettings()
            self._system_settings = SystemSettings()
            self._route = "mock/route"
            self._standard_params = MockStdParams(
                param1="mock_param1", param2="mock_param2"
            )
            self.results = "mock_results"

            self.provider = "mock_provider"
            self.extra = "mock_extra"
            self.warnings = "mock_warnings"
            self.chart = MagicMock()

        def to_dataframe(self):
            """Mock to_dataframe."""
            return mock_dataframe

    return MockOOBject()


def test_charting_settings(obbject):
    """Test charting_settings."""
    cm = Charting(obbject)
    assert isinstance(cm, Charting)


def test_indicators(obbject):
    """Test indicators method."""
    obj = Charting(obbject)
    indicators = list(obj.indicators().model_dump().keys())

    assert indicators == [
        "sma",
        "ema",
        "hma",
        "wma",
        "zlma",
        "ad",
        "adoscillator",
        "adx",
        "aroon",
        "atr",
        "cci",
        "clenow",
        "demark",
        "donchian",
        "fib",
        "fisher",
        "ichimoku",
        "kc",
        "macd",
        "obv",
        "rsi",
        "srlines",
        "stoch",
    ]


@patch("openbb_charting.get_charting_functions")
def test_functions(mock_get_charting_functions):
    """Test functions method."""
    # Arrange
    mock_get_charting_functions.return_value = ["function1", "function2", "function3"]

    # Act
    result = Charting.functions()

    # Assert
    assert result == ["function1", "function2", "function3"]
    mock_get_charting_functions.assert_called_once()


@patch("openbb_charting.get_backend")
@patch("openbb_charting.create_backend")
def test_handle_backend(mock_create_backend, mock_get_backend, obbject):
    """Test _handle_backend method."""
    # Act -> _handle backend is called in the constructor
    obj = Charting(obbject)

    # Assert
    mock_create_backend.assert_called_once_with(obj._charting_settings)
    mock_get_backend.assert_called_once()


def test_get_chart_function(obbject):
    """Test _get_chart_function method."""
    # Arrange
    mock_function = MagicMock()
    charting = Charting(obbject)
    charting._functions = {"some_function": mock_function}
    route = "/some/function"

    # Act
    result = charting._get_chart_function(route)

    # Assert
    assert result == mock_function


@patch("openbb_charting.Charting._get_chart_function")
@patch("openbb_charting.Chart")
def test_show(_, mock_get_chart_function, obbject):
    """Test show method."""
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


@patch("openbb_charting.Charting._prepare_data_as_df")
@patch("openbb_charting.Charting._get_chart_function")
@patch("openbb_charting.Chart")
def test_to_chart(_, mock_get_chart_function, mock_prepare_data_as_df, obbject):
    """Test to_chart method."""
    # Arrange
    mock_prepare_data_as_df.return_value = (mock_dataframe, True)
    mock_function = MagicMock()
    mock_get_chart_function.return_value = mock_function
    mock_fig = MagicMock()
    mock_function.return_value = (mock_fig, {"content": "mock_content"})
    obj = Charting(obbject)

    # Act
    obj.to_chart()

    # Assert
    mock_get_chart_function.assert_called_once()
    mock_function.assert_called_once()

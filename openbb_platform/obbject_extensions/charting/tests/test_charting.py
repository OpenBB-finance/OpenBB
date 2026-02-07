"""Test Charting class."""

from unittest.mock import MagicMock, patch

import pytest
from openbb_charting.charting import Charting
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
    """Mock OBBject."""

    class MockStdParams(BaseModel):
        """Mock Standard Parameters."""

        param1: str
        param2: str

    class MockOBBject:
        """Mock OBBject."""

        def __init__(self):
            """Mock OBBject."""
            self._user_settings = UserSettings()
            self._system_settings = SystemSettings()
            self._route = "mock/route"
            self._standard_params = MockStdParams(
                param1="mock_param1", param2="mock_param2"
            )
            self._extra_params = {}
            self.results = "mock_results"

            self.provider = "mock_provider"
            self.extra = {}
            self.warnings = "mock_warnings"
            self.chart = MagicMock()

        def to_dataframe(self):
            """Mock to_dataframe."""
            return mock_dataframe

    return MockOBBject()


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


@patch("openbb_charting.charting.get_charting_functions_list")
def test_functions(get_charting_functions_list):
    """Test functions method."""
    # Arrange
    get_charting_functions_list.return_value = ["function1", "function2", "function3"]

    # Act
    result = Charting.functions()

    # Assert
    assert set(result) == {"function1", "function2", "function3"}
    assert get_charting_functions_list.call_count >= 1


@patch("openbb_charting.charting.Charting._handle_backend")
def test_handle_backend(mock_handle_backend, obbject):
    """Test _handle_backend method."""
    # Act -> _handle backend is called in the constructor
    _ = Charting(obbject)

    # Assert
    mock_handle_backend.assert_called_once()


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


@patch("openbb_charting.charting.Charting._get_chart_function")
def test_show(mock_get_chart_function, obbject):
    """Test show method."""
    # Arrange
    mock_function = MagicMock()
    mock_get_chart_function.return_value = mock_function
    mock_fig = MagicMock()
    mock_fig.show = MagicMock(
        return_value=MagicMock(to_plotly_json=MagicMock(return_value={}))
    )
    mock_function.return_value = (mock_fig, {"content": "mock_content"})
    obj = Charting(obbject)

    # Act
    obj.show(render=False)

    # Assert
    mock_get_chart_function.assert_called_once()
    mock_function.assert_called_once()


@patch("openbb_charting.charting.Charting._prepare_data_as_df")
@patch("openbb_charting.charting.Charting._get_chart_function")
def test_to_chart(mock_get_chart_function, mock_prepare_data_as_df, obbject):
    """Test to_chart method."""
    # Arrange
    mock_prepare_data_as_df.return_value = (mock_dataframe, True)
    mock_function = MagicMock()
    mock_get_chart_function.return_value = mock_function
    mock_fig = MagicMock()
    mock_fig.show = MagicMock(
        return_value=MagicMock(to_plotly_json=MagicMock(return_value={}))
    )
    mock_function.return_value = (mock_fig, {"content": "mock_content"})
    obj = Charting(obbject)

    # Act
    obj.to_chart(render=False)

    # Assert
    mock_get_chart_function.assert_called_once()
    mock_function.assert_called_once()

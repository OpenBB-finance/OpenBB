"""Test the chart model."""

import pytest
from openbb_core.app.model.charts.chart import Chart


def test_charting_default_values():
    """Test the charting default values."""
    # Arrange & Act
    chart = Chart()

    # Assert
    assert chart.content is None
    assert chart.format is None


def test_charting_custom_values():
    """Test the charting custom values."""
    # Arrange
    content = {"data": [1, 2, 3]}
    chart_format = "plotly"

    # Act
    chart = Chart(content=content, format=chart_format)

    # Assert
    assert chart.content == content
    assert chart.format == chart_format


def test_charting_assignment_validation():
    """Test the charting assignment validation."""
    # Arrange
    chart = Chart()

    # Act & Assert
    with pytest.raises(ValueError):
        chart.invalid_field = "Invalid Value"


def test_charting_config_validation():
    """Test the charting config validation."""
    # Arrange
    content = {"data": [1, 2, 3]}
    chart_format = "plotly"

    chart = Chart(content=content, format=chart_format)

    with pytest.raises(ValueError):
        chart.content = "Invalid Content"  # type: ignore[assignment]

    assert chart.content == content
    assert chart.format == chart_format


def test_show():
    """Test the show method."""
    # TODO : add test after the function is properly refactored

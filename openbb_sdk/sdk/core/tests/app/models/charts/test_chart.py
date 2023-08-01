from openbb_core.app.model.charts.chart import Chart, ChartFormat, Error

import pytest


def test_chart_default_values():
    # Arrange & Act
    chart = Chart()

    # Assert
    assert chart.content is None
    assert chart.format == ChartFormat.plotly
    assert chart.error is None


def test_chart_custom_values():
    # Arrange
    content = {"data": [1, 2, 3]}
    chart_format = ChartFormat.plotly
    error = Error(message="Test Error")

    # Act
    chart = Chart(content=content, format=chart_format, error=error)

    # Assert
    assert chart.content == content
    assert chart.format == chart_format
    assert chart.error == error


def test_chart_assignment_validation():
    # Arrange
    chart = Chart()

    # Act & Assert
    with pytest.raises(ValueError):
        chart.invalid_field = "Invalid Value"


def test_chart_config_validation():
    # Arrange
    content = {"data": [1, 2, 3]}
    chart_format = ChartFormat.plotly

    chart = Chart(content=content, format=chart_format)

    with pytest.raises(ValueError):
        chart.content = "Invalid Content"

    assert chart.content == content
    assert chart.format == chart_format

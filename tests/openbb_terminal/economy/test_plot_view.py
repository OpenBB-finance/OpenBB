"""Test the plot view."""
import pandas as pd
import pytest

from openbb_terminal.economy import plot_view


@pytest.mark.parametrize(
    "dataset_yaxis_1, dataset_yaxis_2, kwargs",
    [
        (
            pd.DataFrame(
                {
                    "yaxis_1": [1, 2, 3, 4, 5],
                    "yaxis_2": [1, 2, 3, 4, 5],
                },
                index=pd.date_range("2020-01-01", "2020-01-05"),
            ),
            pd.DataFrame(
                {
                    "yaxis_1": [1, 2, 3, 4, 5],
                    "yaxis_2": [1, 2, 3, 4, 5],
                },
                index=pd.date_range("2020-01-01", "2020-01-05"),
            ),
            {},
        )
    ],
)
def test_show_plot(dataset_yaxis_1, dataset_yaxis_2, kwargs):
    """Test show_plot."""
    plot = plot_view.show_plot(dataset_yaxis_1, dataset_yaxis_2, **kwargs)
    assert plot is not None


@pytest.mark.parametrize(
    "dataset_yaxis_1, dataset_yaxis_2, kwargs",
    [
        (
            pd.DataFrame(
                {
                    "yaxis_1": [1, 2, 3, 4, 5],
                    "yaxis_2": [1, 2, 3, 4, 5],
                },
                index=pd.date_range("2020-01-01", "2020-01-05"),
            ),
            pd.DataFrame(
                {
                    "yaxis_1": [1, 2, 3, 4, 5],
                    "yaxis_2": [1, 2, 3, 4, 5],
                },
                index=pd.date_range("2020-01-01", "2020-01-05"),
            ),
            {},
        )
    ],
)
def test_show_options(dataset_yaxis_1, dataset_yaxis_2, kwargs):
    """Test show_options."""
    datasets = {"yaxis_1": dataset_yaxis_1, "yaxis_2": dataset_yaxis_2}
    plot_view.show_options(datasets, **kwargs)

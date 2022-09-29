# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.common.behavioural_analysis import google_view

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111
# pylint: disable=W0621
# pylint: disable=W0613


@pytest.fixture
def get_queries_response():
    """
    mock response from get_queries function in google_model
    """
    top_list = [
        ["stock aapl", 100],
        ["aapl price", 29],
        ["stock price aapl", 24],
        ["amzn", 19],
        ["tsla", 19],
        ["msft", 15],
        ["tsla stock", 12],
        ["amzn stock", 11],
        ["fb stock", 10],
        ["msft stock", 9],
        ["nvda", 7],
        ["dow", 6],
        ["tesla", 6],
        ["amd", 5],
        ["goog", 5],
        ["baba", 5],
        ["aapl premarket", 5],
        ["nvda stock", 5],
        ["tesla stock", 5],
        ["amd stock", 4],
        ["aapl stock price today", 4],
        ["nflx", 4],
        ["nio", 4],
        ["baba stock", 4],
        ["nio stock", 4],
    ]

    resp = {
        "AAPL": {
            "top": pd.DataFrame(top_list, columns=["query", "value"]),
            "rising": pd.DataFrame(top_list, columns=["query", "value"]),
        }
    }

    return pd.DataFrame(resp)


@pytest.mark.default_cassette("test_google_view")
@pytest.mark.vcr
@pytest.mark.parametrize(
    "symbol, limit, export",
    [
        (
            # standard run without export
            "AAPL",
            25,
            "",
        ),
        (
            # standard run WITH export
            "AAPL",
            25,
            "csv",
        ),
    ],
)
def test_display_queries(mocker, symbol, limit, export, get_queries_response):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    # MOCK GOOGLE_MODEL
    mocker.patch(
        target="openbb_terminal.common.behavioural_analysis.google_model.get_queries",
        return_value=get_queries_response,
    )

    # MOCK EXPORT_DATA
    export_mock = mocker.Mock()
    mocker.patch(
        target="openbb_terminal.common.behavioural_analysis.google_view.export_data",
        new=export_mock,
    )

    google_view.display_queries(symbol, limit, export)

    if export:
        pd.testing.assert_frame_equal(
            export_mock.call_args[0][3],  # fourth positional arg is the df
            pd.DataFrame(get_queries_response),  # expected DF
        )

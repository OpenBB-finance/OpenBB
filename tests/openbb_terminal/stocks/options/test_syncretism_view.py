# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pytest
import pandas as pd

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import syncretism_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
        ],
    }


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "preset",
    ["high_IV", ""],
)
def test_view_available_presets(preset):
    presets_path = os.path.join(os.path.dirname(syncretism_view.__file__), "presets/")
    syncretism_view.view_available_presets(
        preset=preset,
        presets_path=presets_path,
    )


@pytest.mark.default_cassette("test_view_screener_output")
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_view_screener_output(mocker):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")
    presets_path = os.path.join(os.path.dirname(syncretism_view.__file__), "presets/")
    syncretism_view.view_screener_output(
        preset="high_IV",
        presets_path=presets_path,
        n_show=5,
        export="",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_view_screener_output_error(mocker):
    mocker.patch(
        target="openbb_terminal.stocks.options.syncretism_view.syncretism_model.get_screener_output",
        return_value=(pd.DataFrame(), "MOCK_ERROR_MESSAGE"),
    )
    presets_path = os.path.join(os.path.dirname(syncretism_view.__file__), "presets/")
    syncretism_view.view_screener_output(
        preset="high_IV",
        presets_path=presets_path,
        n_show=5,
        export="",
    )


@pytest.mark.vcr
def test_view_historical_greeks(mocker):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    syncretism_view.view_historical_greeks(
        ticker="PM",
        expiry="2022-01-07",
        chain_id="PM220107P00090000",
        strike=90,
        greek="theta",
        put=True,
        raw=True,
        n_show=5,
        export="",
    )

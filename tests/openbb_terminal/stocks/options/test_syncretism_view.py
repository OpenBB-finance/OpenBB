# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
from pathlib import Path

import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options.screen import syncretism_view


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


@pytest.mark.default_cassette("test_view_screener_output")
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_view_screener_output():
    syncretism_view.view_screener_output(
        preset="high_iv.ini",
        limit=5,
        export="",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_view_screener_output_error(mocker):
    mocker.patch(
        target="openbb_terminal.stocks.options.screen.syncretism_view.syncretism_model.get_screener_output",
        return_value=(pd.DataFrame(), "MOCK_ERROR_MESSAGE"),
    )
    syncretism_view.view_screener_output(
        preset="high_iv.ini",
        limit=5,
        export="",
    )


@pytest.mark.vcr
def test_view_historical_greeks():
    syncretism_view.view_historical_greeks(
        symbol="PM",
        expiry="",
        chain_id="PM220107P00090000",
        strike=90,
        greek="theta",
        put=True,
        raw=True,
        limit=5,
        export="",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "preset",
    ["template.ini", "spy_30_delta.ini"],
)
def test_view_available_presets(mocker, preset):
    mock_preset_path = Path(__file__).resolve().parent / "ini"
    preset_choices = {
        filepath.name: filepath
        for filepath in mock_preset_path.iterdir()
        if filepath.suffix == ".ini"
    }
    mocker.patch(
        target="openbb_terminal.stocks.options.screen.syncretism_model.get_preset_choices",
        return_value=preset_choices,
    )
    syncretism_view.view_available_presets(
        preset=preset,
    )

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.economy import alphavantage_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [("apikey", "MOCK_API_KEY")],
    }


@pytest.mark.default_cassette("test_realtime_performance_sector")
@pytest.mark.vcr
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
@pytest.mark.record_stdout
def test_realtime_performance_sector(mocker, raw):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.alphavantage_view.export_data")

    alphavantage_view.realtime_performance_sector(raw=raw)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
@pytest.mark.record_stdout
def test_display_real_gdp(mocker, raw):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.alphavantage_view.export_data")

    alphavantage_view.display_real_gdp(raw=raw)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
@pytest.mark.record_stdout
def test_display_gdp_capita(mocker, raw):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.alphavantage_view.export_data")

    alphavantage_view.display_gdp_capita(raw=raw)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
@pytest.mark.record_stdout
def test_display_inflation(mocker, raw):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.alphavantage_view.export_data")

    alphavantage_view.display_inflation(raw=raw)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
@pytest.mark.record_stdout
def test_display_cpi(mocker, raw):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.alphavantage_view.export_data")

    alphavantage_view.display_cpi(raw=raw)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
@pytest.mark.record_stdout
def test_display_treasury_yield(mocker, raw):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.alphavantage_view.export_data")

    alphavantage_view.display_treasury_yield(raw=raw)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
@pytest.mark.record_stdout
def test_display_unemployment(mocker, raw):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.alphavantage_view.export_data")

    alphavantage_view.display_unemployment(raw=raw)

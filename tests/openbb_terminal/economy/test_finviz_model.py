# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.economy import finviz_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr(record_mode="none")
def test_get_performance_map(mocker):
    # MOCK EXPORT_DATA
    mock_open = mocker.Mock()
    mocker.patch(
        target="openbb_terminal.economy.finviz_model.webbrowser.open", new=mock_open
    )

    finviz_model.get_performance_map(period="1w", map_filter="sp500")

    mock_open.assert_called_once()


@pytest.mark.vcr
def test_get_valuation_data(recorder):
    result_df = finviz_model.get_valuation_data(group="sector")

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_performance_data(recorder):
    result_df = finviz_model.get_performance_data(group="sector")

    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="none")
def test_get_spectrum_data(mocker):
    # MOCK screener_view
    mock_spectrum = mocker.Mock()
    mocker.patch(
        target="openbb_terminal.economy.finviz_model.spectrum",
        new=mock_spectrum,
    )
    finviz_model.get_spectrum_data(group="sector")

    mock_spectrum.Spectrum().screener_view.assert_called_with(group="Sector")


@pytest.mark.vcr
def test_get_futures(recorder):
    result_dict = finviz_model.get_futures()

    recorder.capture(result_dict)

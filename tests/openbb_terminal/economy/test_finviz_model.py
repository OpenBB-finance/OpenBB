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


@pytest.mark.vcr
@pytest.mark.parametrize(
    "data_type",
    [
        "valuation",
        "performance",
    ],
)
def test_get_valuation_performance_data(data_type, recorder):
    result_df = finviz_model.get_valuation_performance_data(
        group="Sector", data_type=data_type
    )

    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="none")
def test_get_spectrum_data(mocker):
    # MOCK screener_view
    mock_spectrum = mocker.Mock()
    mocker.patch(
        target="openbb_terminal.economy.finviz_model.spectrum",
        new=mock_spectrum,
    )
    finviz_model.get_spectrum_data(group="Sector")

    mock_spectrum.Spectrum().screener_view.assert_called_with(group="Sector")


@pytest.mark.vcr
def test_get_futures(recorder):
    result_dict = finviz_model.get_futures()

    recorder.capture(result_dict)

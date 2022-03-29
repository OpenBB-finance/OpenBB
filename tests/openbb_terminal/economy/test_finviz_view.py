# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.economy import finviz_view
from openbb_terminal import helper_funcs


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr(record_mode="none")
def test_map_sp500_view(mocker):
    # MOCK EXPORT_DATA
    mock_open = mocker.Mock()
    mocker.patch(
        target="openbb_terminal.economy.finviz_view.webbrowser.open", new=mock_open
    )

    finviz_view.map_sp500_view(period="1w", map_type="sp500")

    mock_open.assert_called_once()


@pytest.mark.default_cassette("test_display_performance")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "tab",
    [
        True,
        False,
    ],
)
def test_display_performance(mocker, tab):
    # MOCK GTFF
    mocker.patch.object(target=helper_funcs.obbff, attribute="USE_TABULATE_DF", new=tab)
    mocker.patch.object(target=helper_funcs.obbff, attribute="USE_ION", new=True)

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.finviz_view.export_data")

    finviz_view.display_performance(
        s_group="Sector",
        sort_col="Name",
        ascending=True,
        export="",
    )


@pytest.mark.default_cassette("test_display_valuation")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "tab",
    [
        True,
        False,
    ],
)
def test_display_valuation(mocker, tab):
    # MOCK GTFF
    mocker.patch.object(target=helper_funcs.obbff, attribute="USE_TABULATE_DF", new=tab)
    mocker.patch.object(target=helper_funcs.obbff, attribute="USE_ION", new=True)

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.finviz_view.export_data")

    finviz_view.display_valuation(
        s_group="Sector",
        sort_col="Name",
        ascending=True,
        export="",
    )


@pytest.mark.vcr(record_mode="none")
def test_display_spectrum(mocker):
    # MOCK GET_SPECTRUM_DATA
    mocker.patch(
        target="openbb_terminal.economy.finviz_view.finviz_model.get_spectrum_data"
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.finviz_view.export_data")

    # MOCK OPEN
    mock_image = mocker.Mock()
    mocker.patch(
        target="openbb_terminal.economy.finviz_view.Image",
        new=mock_image,
    )

    finviz_view.display_spectrum(
        s_group="Sector",
        export="",
    )

    mock_image.open().show.assert_called_once()


@pytest.mark.default_cassette("test_display_future")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "tab",
    [
        True,
        False,
    ],
)
def test_display_future(mocker, tab):
    # MOCK GTFF
    mocker.patch.object(target=helper_funcs.obbff, attribute="USE_TABULATE_DF", new=tab)
    mocker.patch.object(target=helper_funcs.obbff, attribute="USE_ION", new=True)

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.finviz_view.export_data")

    finviz_view.display_future(
        future_type="Indices",
        sort_col="ticker",
        ascending=False,
        export="",
    )

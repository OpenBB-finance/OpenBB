# IMPORTATION STANDARD
import dataclasses

# IMPORTATION THIRDPARTY
import pytest

from openbb_terminal import helper_funcs

# IMPORTATION INTERNAL
from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.economy import finviz_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


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
    # MOCK OBBFF
    current_user = get_current_user()
    preference = PreferencesModel(
        USE_TABULATE_DF=tab,
        USE_ION=True,
    )
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.finviz_view.export_data")

    finviz_view.display_valuation(
        group="sector",
        sortby="Name",
        ascend=True,
        export="",
    )


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
    # MOCK OBBFF
    current_user = get_current_user()
    preference = PreferencesModel(
        USE_TABULATE_DF=tab,
        USE_ION=True,
    )
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.finviz_view.export_data")

    finviz_view.display_performance(
        group="sector",
        sortby="Name",
        ascend=True,
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
        group="sector",
        export="jpg",
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
    # MOCK OBBFF
    current_user = get_current_user()
    preference = PreferencesModel(
        USE_TABULATE_DF=tab,
        USE_ION=True,
    )
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.finviz_view.export_data")

    finviz_view.display_future(
        future_type="Indices",
        sortby="ticker",
        ascend=False,
        export="",
    )

# IMPORTATION STANDARD
import dataclasses

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.stocks.screener import ark_view

# pytest.skip("skipping tests, ark views seems broken", allow_module_level=True)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.default_cassette("test_display_ark_trades_INVALID_TICKER")
@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_display_ark_trades_invalid_ticker():
    ark_view.display_ark_trades(symbol="INVALID_TICKER")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_ark_trades_default():
    ark_view.display_ark_trades(symbol="TSLA")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_ark_trades_no_tab(mocker):
    current_user = get_current_user()
    preference = PreferencesModel(USE_TABULATE_DF=False)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )

    ark_view.display_ark_trades(symbol="TSLA")


@pytest.mark.vcr
def test_display_ark_trades_export(capsys, mocker):
    ark_view.export_data = mocker.Mock()

    ark_view.display_ark_trades(symbol="TSLA", export="csv")

    capsys.readouterr()

    ark_view.export_data.assert_called_once()

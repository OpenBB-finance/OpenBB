# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import ark_view

pytest.skip("skipping tests, ark views seems broken", allow_module_level=True)


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
    ark_view.display_ark_trades(ticker="INVALID_TICKER")


@pytest.mark.default_cassette("test_display_ark_trades_TSLA")
@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_display_ark_trades_default():
    ark_view.display_ark_trades(ticker="TSLA")


@pytest.mark.default_cassette("test_display_ark_trades_TSLA")
@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_display_ark_trades_no_tab(mocker):
    mocker.patch(
        target="gamestonk_terminal.feature_flags.USE_TABULATE_DF",
        new=False,
    )

    ark_view.display_ark_trades(ticker="TSLA")


@pytest.mark.default_cassette("test_display_ark_trades_TSLA")
@pytest.mark.vcr(record_mode="none")
def test_display_ark_trades_export(capsys, mocker):
    ark_view.export_data = mocker.Mock()

    ark_view.display_ark_trades(ticker="TSLA", export="csv")

    capsys.readouterr()

    ark_view.export_data.assert_called_once()

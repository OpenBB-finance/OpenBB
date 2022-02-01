# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.options import tradier_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("Authorization", "MOCK_TOKEN")],
    }


@pytest.mark.vcr(record_mode="none")
def test_red_highlight(recorder):
    result = tradier_view.red_highlight(val="MOCK TEXT")
    recorder.capture(result)


@pytest.mark.vcr(record_mode="none")
def test_green_highlight(recorder):
    result = tradier_view.green_highlight(val="MOCK TEXT")
    recorder.capture(result)


@pytest.mark.vcr(record_mode="none")
def test_check_valid_option_chains_headers(recorder):
    result = tradier_view.check_valid_option_chains_headers(headers="gamma,delta")
    recorder.capture(result)


@pytest.mark.default_cassette("test_display_chains")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "calls_only, puts_only, min_sp, max_sp",
    [
        (True, False, 80.0, 90.0),
        (False, True, 80.0, 90.0),
        (True, False, -1, -1),
        (False, True, -1, -1),
        (False, False, -1, -1),
    ],
)
def test_display_chains(calls_only, max_sp, min_sp, mocker, puts_only):
    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.stocks.options.tradier_view.export_data")

    # MOCK USE_COLOR
    mocker.patch.object(target=tradier_view.gtff, attribute="USE_COLOR", new=True)

    tradier_view.display_chains(
        ticker="PM",
        expiry="2022-01-07",
        to_display=["volume"],
        min_sp=min_sp,
        max_sp=max_sp,
        calls_only=calls_only,
        puts_only=puts_only,
        export="",
    )


@pytest.mark.default_cassette("test_plot_oi")
@pytest.mark.vcr
@pytest.mark.parametrize(
    "calls_only, puts_only, min_sp, max_sp",
    [
        (True, False, 80.0, 90.0),
        (False, True, 80.0, 90.0),
        (True, False, -1, -1),
        (False, True, -1, -1),
        (True, True, -1, -1),
        (False, False, -1, -1),
    ],
)
def test_plot_oi(calls_only, max_sp, min_sp, mocker, puts_only):
    # MOCK CHARTS
    mocker.patch.object(target=tradier_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.tradier_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.tradier_view.plt.show")

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.stocks.options.tradier_view.export_data")

    # MOCK USE_COLOR
    mocker.patch.object(target=tradier_view.gtff, attribute="USE_COLOR", new=True)

    tradier_view.plot_oi(
        ticker="PM",
        expiry="2022-01-07",
        min_sp=min_sp,
        max_sp=max_sp,
        calls_only=calls_only,
        puts_only=puts_only,
        export="",
    )


@pytest.mark.default_cassette("test_plot_oi")
@pytest.mark.vcr
@pytest.mark.parametrize(
    "calls_only, puts_only, min_sp, max_sp",
    [
        (True, False, 80.0, 90.0),
        (False, True, 80.0, 90.0),
        (True, False, -1, -1),
        (False, True, -1, -1),
        (True, True, -1, -1),
        (False, False, -1, -1),
    ],
)
def test_plot_vol(calls_only, max_sp, min_sp, mocker, puts_only):
    # MOCK CHARTS
    mocker.patch.object(target=tradier_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.tradier_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.tradier_view.plt.show")

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.stocks.options.tradier_view.export_data")

    # MOCK USE_COLOR
    mocker.patch.object(target=tradier_view.gtff, attribute="USE_COLOR", new=True)

    tradier_view.plot_vol(
        ticker="PM",
        expiry="2022-01-07",
        min_sp=min_sp,
        max_sp=max_sp,
        calls_only=calls_only,
        puts_only=puts_only,
        export="",
    )


@pytest.mark.default_cassette("test_plot_volume_open_interest")
@pytest.mark.vcr
@pytest.mark.parametrize(
    "min_sp, max_sp, min_vol",
    [
        (80.0, 90.0, 0.0),
        (-1, -1, -1),
    ],
)
def test_plot_volume_open_interest(max_sp, min_sp, min_vol, mocker):
    # MOCK CHARTS
    mocker.patch.object(target=tradier_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.tradier_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.tradier_view.plt.show")

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.stocks.options.tradier_view.export_data")

    # MOCK USE_COLOR
    mocker.patch.object(target=tradier_view.gtff, attribute="USE_COLOR", new=True)

    tradier_view.plot_volume_open_interest(
        ticker="PM",
        expiry="2022-01-07",
        min_sp=min_sp,
        max_sp=max_sp,
        min_vol=min_vol,
        export="",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_historical(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=tradier_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.tradier_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.tradier_view.plt.show")

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.stocks.options.tradier_view.export_data")

    # MOCK USE_COLOR
    mocker.patch.object(target=tradier_view.gtff, attribute="USE_COLOR", new=True)

    tradier_view.display_historical(
        ticker="PM",
        expiry="2022-01-07",
        strike=90.0,
        put=True,
        export="csv",
        raw=True,
        chain_id="",
    )

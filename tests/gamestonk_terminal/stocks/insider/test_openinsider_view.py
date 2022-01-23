# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.insider import openinsider_view

# pylint: disable=E1101


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, text_list",
    [
        ("red_highlight", ["MOCK_TEXT_1", "MOCK_TEXT_2"]),
        ("yellow_highlight", ["MOCK_TEXT_1", "MOCK_TEXT_2"]),
        ("magenta_highlight", ["MOCK_TEXT_1", "MOCK_TEXT_2"]),
        ("green_highlight", ["MOCK_TEXT_1", "MOCK_TEXT_2"]),
    ],
)
def test_format_list_func(func, recorder, text_list):
    text_list_formatted = getattr(openinsider_view, func)(values=text_list)

    recorder.capture(text_list_formatted)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_print_insider_filter(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.stocks.insider.openinsider_view.export_data"
    )

    openinsider_view.print_insider_filter(
        preset_loaded="whales",
        ticker="PM",
        limit=5,
        links=False,
        export="csv",
    )


@pytest.mark.vcr(record_mode="none")
def test_print_insider_filter_no_table(mocker):
    # MOCK SOUP
    mocker.patch(
        target="gamestonk_terminal.stocks.insider.openinsider_view.get_open_insider_link",
        return_value=None,
    )

    openinsider_view.print_insider_filter(
        preset_loaded="whales",
        ticker="",
        limit=10,
        links=False,
        export="",
    )


@pytest.mark.default_cassette("test_print_insider_data")
@pytest.mark.vcr
@pytest.mark.parametrize(
    "color",
    [True, False],
)
def test_print_insider_data(color, mocker):
    # MOCK GTFF
    mocker.patch.object(target=openinsider_view.gtff, attribute="USE_COLOR", new=color)

    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.stocks.insider.openinsider_view.export_data"
    )

    openinsider_view.print_insider_data(
        type_insider="lip",
        limit=10,
        export="",
    )


@pytest.mark.vcr(record_mode="none")
def test_print_insider_data_no_table(mocker):
    # MOCK GET
    mocker.patch(target="requests.get")

    # MOCK BEAUTIFULSOUP
    mock_soup = mocker.Mock()
    mocker.patch.object(target=mock_soup, attribute="find", return_value=None)
    mocker.patch(
        target="gamestonk_terminal.stocks.insider.openinsider_view.BeautifulSoup",
        return_value=mock_soup,
    )

    openinsider_view.print_insider_data(
        type_insider="lip",
        limit=10,
        export="",
    )

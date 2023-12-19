# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.insider import openinsider_view

# pylint: disable=E1101


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, text_list",
    [
        ("lambda_red_highlight", ["MOCK_TEXT_1", "MOCK_TEXT_2"]),
        ("lambda_yellow_highlight", ["MOCK_TEXT_1", "MOCK_TEXT_2"]),
        ("lambda_magenta_highlight", ["MOCK_TEXT_1", "MOCK_TEXT_2"]),
        ("lambda_green_highlight", ["MOCK_TEXT_1", "MOCK_TEXT_2"]),
    ],
)
def test_format_list_func(func, recorder, text_list):
    text_list_formatted = getattr(openinsider_view, func)(values=text_list)

    recorder.capture(text_list_formatted)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_print_insider_filter(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.stocks.insider.openinsider_view.export_data")

    openinsider_view.print_insider_filter(
        preset="whales",
        symbol="PM",
        limit=5,
        links=False,
        export="csv",
        sheet_name=None,
    )


@pytest.mark.vcr(record_mode="none")
def test_print_insider_filter_no_table(mocker):
    # MOCK SOUP
    mocker.patch(
        target="openbb_terminal.stocks.insider.openinsider_view.get_open_insider_link",
        return_value=None,
    )

    openinsider_view.print_insider_filter(
        preset="whales",
        symbol="",
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
    # MOCK OBBFF
    mocker.patch.object(
        target=openinsider_view.rich_config, attribute="USE_COLOR", new=color
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.stocks.insider.openinsider_view.export_data")

    openinsider_view.print_insider_data(
        type_insider="lip",
        limit=10,
        export="",
    )


@pytest.mark.vcr(record_mode="none")
def test_print_insider_data_no_table(mocker):
    # MOCK GET
    attrs = {"status_code": 200, "text": ""}
    mock_response = mocker.Mock(**attrs)
    mocker.patch(
        "openbb_terminal.helper_funcs.requests.get", return_value=mock_response
    )
    mocker.patch(
        target="openbb_terminal.stocks.insider.openinsider_model.pd.read_html",
        return_value=[pd.DataFrame(columns=["1d", "1w", "1m", "6m"]) for _ in range(5)],
    )

    openinsider_view.print_insider_data(
        type_insider="lip",
        limit=10,
        export="",
    )

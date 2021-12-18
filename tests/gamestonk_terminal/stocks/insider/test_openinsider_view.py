# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.insider import openinsider_view

# pylint: disable=E1101

pytest.skip(allow_module_level=True)


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


@pytest.mark.skip
@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        (
            "print_insider_data",
            dict(other_args=list(), type_insider="topt"),
        ),
        (
            "print_insider_filter",
            dict(preset_loaded="whales", ticker=""),
        ),
    ],
)
def test_call_func_no_parser(func, kwargs_dict, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.insider.openinsider_view.parse_known_args_and_warn",
        return_value=None,
    )

    func_result = getattr(openinsider_view, func)(**kwargs_dict)
    assert func_result is None
    getattr(openinsider_view, "parse_known_args_and_warn").assert_called_once()


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_print_insider_filter():
    openinsider_view.print_insider_filter(
        preset_loaded="whales",
        ticker="",
        limit=5,
    )

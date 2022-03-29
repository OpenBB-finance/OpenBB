# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.economy import wsj_view
from openbb_terminal import helper_funcs


@pytest.mark.vcr
@pytest.mark.parametrize(
    "tab",
    [True, False],
)
@pytest.mark.parametrize(
    "func",
    [
        "display_overview",
        "display_indices",
        "display_futures",
        "display_usbonds",
        "display_glbonds",
        "display_currencies",
    ],
)
@pytest.mark.record_stdout
def test_call_func(func, mocker, tab):
    # MOCK OBBFF
    mocker.patch.object(target=helper_funcs.obbff, attribute="USE_TABULATE_DF", new=tab)

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.wsj_view.export_data")

    getattr(wsj_view, func)(export="")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, mocked_func",
    [
        ("display_overview", "market_overview"),
        ("display_indices", "us_indices"),
        ("display_futures", "top_commodities"),
        ("display_usbonds", "us_bonds"),
        ("display_glbonds", "global_bonds"),
        ("display_currencies", "global_currencies"),
    ],
)
def test_call_func_empty_df(func, mocked_func, mocker):
    # MOCK MOCKED_FUNC
    attrs = {"empty": True}
    mock_empty_df = mocker.Mock(**attrs)
    mocker.patch(
        target=f"openbb_terminal.economy.wsj_view.wsj_model.{mocked_func}",
        return_value=mock_empty_df,
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.economy.wsj_view.export_data")

    getattr(wsj_view, func)(export="")

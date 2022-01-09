# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.options import fdscanner_view


# pylint: disable=E1101


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.default_cassette("test_display_options")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "toggle",
    [True, False],
)
def test_display_options(mocker, toggle):
    # MOCK CHARTS
    mocker.patch.object(
        target=fdscanner_view.gtff,
        attribute="USE_TABULATE_DF",
        new=toggle,
    )

    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.stocks.options.fdscanner_view.export_data",
    )

    fdscanner_view.display_options(
        num=5,
        sort_column=["Vol"],
        export="csv",
        ascending=True,
        calls_only=toggle,
        puts_only=not toggle,
    )

    fdscanner_view.export_data.assert_called_once()

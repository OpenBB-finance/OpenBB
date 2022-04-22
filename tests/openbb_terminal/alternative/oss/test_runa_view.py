# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.alternative.oss import runa_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
        ],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_rossindex(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.alternative.oss.runa_view.export_data")

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    runa_view.display_rossindex(
        sortby="",
        descend=False,
        top=10,
        show_chart=True,
        show_growth=False,
        chart_type="stars",
    )
